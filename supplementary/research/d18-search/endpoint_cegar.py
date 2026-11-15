#!/usr/bin/env python3
"""Incremental wire-interval necessary conditions before a sorting suffix.

For cap=2**remaining, width <= cap is equivalent to f(x)>=f(y) whenever
weight(x)-weight(y)>=cap-1. The oracle enumerates the entire prefix image;
only violated two-run witnesses are added to the synthesis formula.
UNSAT excludes the whole fixed prefix. SURVIVOR is only a necessary-condition
witness, never a claim that a sorting network exists.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

from netsat import apply_layers, neg, prefix_images, verify_all
from probe_frontier import ProbeModel
from interval_frontier import add_state_bounds


class IntervalOracle:
    """Bit-parallel exact extrema, independent of the SAT state simulation."""
    def __init__(self, n, universe):
        self.n = n
        self.universe = list(universe)
        self.full = (1 << len(universe)) - 1
        self.initial = [0] * n
        self.weights = [0] * (n + 1)
        for pos, x in enumerate(universe):
            flag = 1 << pos
            self.weights[x.bit_count()] |= flag
            for c in range(n):
                if (x >> c) & 1:
                    self.initial[c] |= flag

    def evaluate(self, layers):
        truth = self.initial[:]
        for layer in layers:
            seen = set()
            for i, j in layer:
                assert 0 <= i < j < self.n and i not in seen and j not in seen
                seen.update((i, j))
                truth[i], truth[j] = truth[i] & truth[j], truth[i] | truth[j]
        answer = []
        for c, bits in enumerate(truth):
            ones = next(w for w in range(self.n + 1) if bits & self.weights[w])
            zeros = next(w for w in range(self.n, -1, -1)
                         if (self.full ^ bits) & self.weights[w])
            yflags = bits & self.weights[ones]
            xflags = (self.full ^ bits) & self.weights[zeros]
            x = self.universe[(xflags & -xflags).bit_length() - 1]
            y = self.universe[(yflags & -yflags).bit_length() - 1]
            lo, hi = self.n - zeros - 1, self.n - ones
            assert lo <= c <= hi
            answer.append(dict(wire=c, lo=lo, hi=hi, width=hi-lo+1,
                               zero_witness=x, one_witness=y))
        return answer


def wire_endpoints(model, wires, cap):
    n = model.n
    lower = [[True] + [model.new_var() for _ in range(n - 1)] + [False]
             for _ in range(n)]
    upper = [[False] + [model.new_var() for _ in range(n - 1)] + [True]
             for _ in range(n)]
    for c in range(n):
        L, U = lower[c], upper[c]
        for k in range(n):
            model.add([neg(L[k+1]), L[k]])
            model.add([neg(U[k]), U[k+1]])
            model.add([neg(L[k]), neg(U[k])])
        model.add([neg(L[c+1])])
        model.add([neg(U[c])])
        if c in wires:
            for k in range(n - cap):
                model.add([L[k+1], U[k+cap]])
    return lower, upper


def run(args):
    started = time.monotonic()
    seed = json.loads(args.seed.read_text())
    n = seed.get('n', len(seed.get('output_permutation', [])))
    assert n > 0
    prefix = seed['prefix']
    depth = args.depth or seed['depth']
    cut = args.cut or depth - 2
    free = cut - len(prefix)
    assert 0 < free < depth - len(prefix)
    cap = 2 ** (depth - cut)
    wires = list(range(n)) if args.wires == 'all' else [int(x) for x in args.wires.split(',')]
    assert wires and len(wires) == len(set(wires)) and all(0 <= c < n for c in wires)
    universe = sorted(prefix_images(n, prefix))
    oracle = IntervalOracle(n, universe)
    if args.proof:
        import netsat
        from prefix_drat import RecordingSolver
        netsat.Solver = RecordingSolver
    # Unused final layers ensure every cut layer permits all comparator spans.
    # Only function-preserving redundant comparators are excluded before the cut.
    model = ProbeModel(n, depth-len(prefix), universe, phi=False, solver=args.solver)
    if args.mode == 'endpoints':
        lower, upper = wire_endpoints(model, wires, cap)
    if args.witness:
        network = json.loads(args.witness.read_text())['network']
        assert len(network) == depth and network[:len(prefix)] == prefix
        assert verify_all(n, network)
        for t, layer in enumerate(network[len(prefix):]):
            chosen = set(map(tuple, layer))
            assert chosen <= set(model.g[t])
            for edge, var in model.g[t].items():
                model.add([var if edge in chosen else -var])
    states, obligations, log = {}, set(), []
    def add_input(x):
        if x not in states:
            states[x] = model.simulate_to_cut(x, free)
            if args.mode == 'endpoints':
                add_state_bounds(model, x, states[x], lower, upper)
        return states[x]
    result = dict(case_id=seed.get('case_id', 'custom'), n=n, depth=depth, cut=cut,
                  prefix=prefix, wires=wires, cap=cap, mode=args.mode,
                  scope='All continuations of fixed prefix; selected wire intervals only',
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  status='BUILT', independently_proof_checked=False,
                  universe_size=len(universe), iterations=log)
    def save():
        result.update(seconds=time.monotonic()-started, variables=model.nv,
                      clauses=model.ncl, input_count=len(states), pair_count=len(obligations),
                      selected_inputs=sorted(states))
        args.out.write_text(json.dumps(result, indent=2)+'\n')
    try:
        while True:
            if time.monotonic()-started > args.seconds:
                result['status'] = 'TIME_LIMIT_BETWEEN_SOLVES'
                save()
                break
            result['status'] = 'SOLVING'
            save()
            solve_start = time.monotonic()
            ok = model.S.solve()
            solve_seconds = time.monotonic()-solve_start
            if not ok:
                log.append(dict(iteration=len(log), status='UNSAT', solve_seconds=solve_seconds))
                result['status'] = 'UNSAT'
                if args.proof:
                    directory = args.out.with_suffix('')
                    directory.mkdir(parents=True, exist_ok=True)
                    cnf, proof = directory/'problem.cnf', directory/'proof.drat'
                    cnf.write_text(f'p cnf {model.nv} {len(model.S.clauses)}\n' +
                                   ''.join(' '.join(map(str,c))+' 0\n' for c in model.S.clauses))
                    proof.write_text('\n'.join(model.S.get_proof())+'\n')
                    result.update(certificate_directory=str(directory),
                                  cnf_sha256=hashlib.sha256(cnf.read_bytes()).hexdigest(),
                                  proof_sha256=hashlib.sha256(proof.read_bytes()).hexdigest())
                save()
                break
            layers = model.network(model.S.get_model())[:free]
            oracle_start = time.monotonic()
            intervals = oracle.evaluate(layers)
            bad = sorted((intervals[c] for c in wires if intervals[c]['width'] > cap),
                         key=lambda row: (-row['width'], row['wire']))
            row = dict(iteration=len(log), solve_seconds=solve_seconds,
                       oracle_seconds=time.monotonic()-oracle_start,
                       violated_wires=len(bad), input_count=len(states),
                       maximum_width=max(intervals[c]['width'] for c in wires))
            log.append(row)
            if not bad:
                result.update(status='SURVIVOR', free_layers=layers, intervals=intervals,
                              full_cut_sorts=verify_all(n, prefix+layers))
                save()
                break
            selected = bad if args.batch == 0 else bad[:args.batch]
            for violation in selected:
                c, x, y = (violation[k] for k in ('wire', 'zero_witness', 'one_witness'))
                assert x.bit_count()-y.bit_count() >= cap-1
                assert not (apply_layers(layers,x) >> c)&1 and (apply_layers(layers,y) >> c)&1
                assert (c,x,y) not in obligations
                obligations.add((c,x,y))
                sx, sy = add_input(x), add_input(y)
                if args.mode == 'pairs':
                    model.add([sx[c], neg(sy[c])])
            row['added_witnesses'] = selected
        print(json.dumps({k:v for k,v in result.items()
                          if k not in ('prefix','selected_inputs','iterations','free_layers','intervals')}), flush=True)
    finally:
        model.S.delete()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--depth', type=int)
    parser.add_argument('--cut', type=int)
    parser.add_argument('--mode', choices=('endpoints','pairs'), default='endpoints')
    parser.add_argument('--wires', default='all')
    parser.add_argument('--batch', type=int, default=0, help='0 adds witnesses for all bad wires')
    parser.add_argument('--seconds', type=float, default=55)
    parser.add_argument('--solver', default='cadical195')
    parser.add_argument('--proof', action='store_true')
    parser.add_argument('--witness', type=Path)
    run(parser.parse_args())


if __name__ == '__main__':
    main()
