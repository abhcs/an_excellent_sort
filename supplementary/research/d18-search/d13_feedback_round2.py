#!/usr/bin/env python3
"""Named complete-cover D13 cases, cut6 interval bounds, optional ending cones.

Run under an external hard wall cap; this worker never treats timeout as UNSAT.
It performs no data comparisons in the last two layers.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

from pysat.card import CardEnc, EncType
from cover_solve import relabel_prefix
from interval_frontier import actual_intervals, add_state_bounds, common_ending
import netsat
from netsat import neg, prefix_images
from prefix_drat import RecordingSolver
from probe_frontier import ProbeModel
from relabel import relabel_vec

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--case', type=int, required=True)
    ap.add_argument('--mode', choices=('wire', 'both', 'route'), default='wire')
    ap.add_argument('--wires', default='all')
    ap.add_argument('--ranks', default='all')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--proof', action='store_true')
    args = ap.parse_args()
    started = time.monotonic()
    cover = HERE / 'prefixes/complete13.jsonl'
    case = [json.loads(line) for line in cover.read_text().splitlines()][args.case]
    n = case['n']
    original = prefix_images(n, case['layers'])
    prefix, lab, mapping, before, after = relabel_prefix(n, case['layers'], original, 200)
    universe = sorted(prefix_images(n, prefix))
    assert {relabel_vec(x, mapping, n) for x in original} == set(universe)
    wires = list(range(n)) if args.wires == 'all' else [int(x) for x in args.wires.split(',') if x]
    ranks = ([] if args.mode == 'wire' else list(range(n)) if args.ranks == 'all'
             else [int(x) for x in args.ranks.split(',') if x])
    if args.proof:
        netsat.Solver = RecordingSolver
    m = ProbeModel(n, 6, universe, phi=args.mode == 'route')
    lower = [[True] + [m.new_var() for _ in range(n - 1)] + [False] for _ in range(n)]
    upper = [[False] + [m.new_var() for _ in range(n - 1)] + [True] for _ in range(n)]
    for c in range(n):
        L, U = lower[c], upper[c]
        for k in range(n):
            m.add([neg(L[k + 1]), L[k]])
            m.add([neg(U[k]), U[k + 1]])
            m.add([neg(L[k]), neg(U[k])])
        m.add([neg(L[c + 1])])
        m.add([neg(U[c])])
    groups = []
    assumptions = []
    for c in wires:
        a = m.new_var()
        assumptions.append(a)
        groups.append(dict(kind='wire', index=c, selector=a, clause_start=m.ncl))
        for k in range(n - 4):
            m.add([-a, lower[c][k + 1], upper[c][k + 4]])
        groups[-1]['clause_stop'] = m.ncl
    support = []
    if args.mode != 'wire':
        for k in range(n):
            row = []
            for c in range(n):
                s = m.new_var()
                row.append(s)
                m.add([-s, neg(lower[c][k + 1])])
                m.add([-s, neg(upper[c][k])])
                m.add([s, lower[c][k + 1], upper[c][k]])
            support.append(row)
        for k in ranks:
            a = m.new_var()
            assumptions.append(a)
            groups.append(dict(kind='rank', index=k, selector=a, clause_start=m.ncl))
            enc = CardEnc.atmost(support[k], 4, top_id=m.nv, encoding=EncType.seqcounter)
            m.nv = max(m.nv, enc.nv)
            for clause in enc.clauses:
                m.add([-a, *clause])
            groups[-1]['clause_stop'] = m.ncl
    if args.mode == 'route':
        common_ending(m, support)
    for x in universe:
        add_state_bounds(m, x, m.simulate_to_cut(x, 4), lower, upper)
    directory = args.out.with_suffix('')
    if args.proof:
        for a in assumptions:
            m.add([a])
        directory.mkdir(parents=True, exist_ok=True)
        cnf = directory / 'problem.cnf'
        cnf.write_text(f'p cnf {m.nv} {len(m.S.clauses)}\n' +
                       ''.join(' '.join(map(str, cl)) + ' 0\n' for cl in m.S.clauses))
        (directory / 'groups.json').write_text(json.dumps(groups, indent=2) + '\n')
    result = dict(case_id=case['case_id'], depth=8, cut=6, mode=args.mode,
                  prefix=prefix, source_case=case, input_permutation=lab, output_permutation=mapping,
                  inputs=len(universe), wires=wires, ranks=ranks, variables=m.nv, clauses=m.ncl,
                  original_window_cost=before, window_cost=after,
                  scope='All four-layer continuations of this complete-cover prefix; cut6 interval bounds, optional common ending routing',
                  source_sha256=sha(Path(__file__)), cover_sha256=sha(cover),
                  dependencies_sha256={name: sha(HERE / name) for name in
                                      ('netsat.py', 'probe_frontier.py', 'interval_frontier.py',
                                       'cover_solve.py', 'relabel.py', 'prefix_drat.py')},
                  status='BUILT', independently_proof_checked=False,
                  build_seconds=time.monotonic() - started)
    def save():
        args.out.write_text(json.dumps(result, indent=2) + '\n')
    save()
    print(json.dumps({k: v for k, v in result.items() if k not in
                      ('prefix', 'source_case', 'dependencies_sha256', 'input_permutation', 'output_permutation')}), flush=True)
    try:
        sat = m.S.solve(assumptions=[] if args.proof else assumptions)
        result['status'] = 'SURVIVOR' if sat else 'UNSAT'
        if sat:
            layers = m.network(m.S.get_model())
            intervals, low, high = actual_intervals(n, prefix, layers[:4])
            assert all(intervals[c][1] - intervals[c][0] + 1 <= 4 for c in wires)
            assert all(sum(a <= k <= b for a, b in intervals) <= 4 for k in ranks)
            if args.mode == 'route':
                for k in range(n):
                    positions = {c for c, (a, b) in enumerate(intervals) if a <= k <= b}
                    cone = {k}
                    for layer in reversed(layers[-2:]):
                        cone |= {v for a, b in layer if a in cone or b in cone for v in (a, b)}
                    assert positions <= cone
            result.update(free_layers=layers, intervals=intervals, low_witnesses=low, high_witnesses=high)
        elif args.proof:
            proof = directory / 'proof.drat'
            proof.write_text('\n'.join(m.S.get_proof()) + '\n')
            result.update(certificate_directory=str(directory), cnf_sha256=sha(cnf), proof_sha256=sha(proof))
        else:
            core = set(m.S.get_core())
            result['semantic_assumption_core'] = [g for g in groups if g['selector'] in core]
        result['seconds'] = time.monotonic() - started
        save()
        print(result['status'], result['seconds'], flush=True)
    finally:
        m.S.delete()


if __name__ == '__main__':
    main()
