#!/usr/bin/env python3
"""Exact search for T(r,a): first TWO layers have at most a comparators.

The first layer may be filled to a comparators and relabelled to adjacent
pairs. All later layers are arbitrary matchings; the final adjacency normal
form is justified by h9.md Lemma 6. Uses the independent exact satnet encoder.
"""
import argparse
import json
from pathlib import Path
import sys
import subprocess
import time

from pysat.card import CardEnc, EncType
from pysat.solvers import Solver
from satnet import Encoding, adjacent_pairs, sorts


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('n', type=int)
    ap.add_argument('cap', type=int)
    ap.add_argument('depth', type=int)
    ap.add_argument('--seconds', type=float, default=300)
    ap.add_argument('--solver', default='cadical195')
    ap.add_argument('--encoder', choices=['exact', 'windows'], default='exact')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--one-shot', action='store_true', help=argparse.SUPPRESS)
    args = ap.parse_args()
    if not (args.n >= 2 and 0 <= args.cap <= args.n // 2 and args.depth >= 2):
        ap.error('need n >= 2, 0 <= cap <= floor(n/2), depth >= 2')
    n, a, d = args.n, args.cap, args.depth
    # This is a batch problem. A single solve in a child process gives every
    # backend a hard wall-clock bound, including time spent preprocessing.
    # It also avoids unsupported resume calls in Kissat.
    if not args.one_shot:
        started = time.monotonic()
        try:
            child = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                                    *sys.argv[1:], '--one-shot'], timeout=args.seconds)
            if child.returncode == 0:
                return
            status = 'ERROR'
        except subprocess.TimeoutExpired:
            status = 'TIME_LIMIT'
        except KeyboardInterrupt:
            status = 'INTERRUPTED'
        result = dict(n=n, cap=a, depth=d, status=status, solver=args.solver,
                      encoder=args.encoder, seconds=round(time.monotonic() - started, 3))
        if status == 'ERROR':
            result['returncode'] = child.returncode
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result), flush=True)
        return
    prefix = [[(2 * i, 2 * i + 1) for i in range(a)]]
    start = time.monotonic()
    result = dict(n=n, cap=a, depth=d, status='TIME_LIMIT', solver=args.solver, encoder=args.encoder)
    if args.encoder == 'exact':
        enc = Encoding(n, d - 1, prefix=prefix, caps=[a] + [None] * (d - 2),
                       allowed=[None] * (d - 2) + [adjacent_pairs(n)])
        print(f'built {enc.nvars} variables, {len(enc.clauses)} clauses', flush=True)
        solver = Solver(name=args.solver, bootstrap_with=enc.clauses)
    else:
        sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'd18-search'))
        from netsat import Model, is_sorted, prefix_images
        inputs = sorted(x for x in prefix_images(n, prefix) if not is_sorted(x, n))
        enc = Model(n, d - 1, inputs, solver=args.solver)
        # The first free layer is original L2. Caps are preserved when
        # deleting redundant comparators, as required by Model's end rules.
        card = CardEnc.atmost(list(enc.g[0].values()), bound=a, top_id=enc.nv,
                             encoding=EncType.seqcounter)
        enc.nv = card.nv
        for clause in card.clauses:
            enc.add(clause)
        for x in inputs:
            enc.add_input(x)
        print(f'built {enc.nv} variables, {enc.ncl} clauses', flush=True)
        solver = enc.S
    with solver as s:
        ok = s.solve()
        if ok is not None:
            result['status'] = 'SAT' if ok else 'UNSAT'
        if ok:
            result['network'] = prefix + enc.network(s.get_model())
            assert sorts(result['network'], n)
            result['verified_binary_inputs'] = 1 << n
    result['seconds'] = round(time.monotonic() - start, 3)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
