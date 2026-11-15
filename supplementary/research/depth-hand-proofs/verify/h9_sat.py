"""h9_sat.py -- (H9) by SAT, as one instance.

(H9): no sorting network on 9 channels with at most 7 layers has at most three comparators in each of
its first two layers.

Reduction (h9.md section 2).  Fill layer 1 up to exactly three comparators (Tool B), relabel and
untangle so that L1 = (0,1)(2,3)(4,5); untangling keeps every layer's size.  Then L2 is any matching
with at most 3 comparators and L3..L7 are ANY matchings.  Variant 'adjacent' also deletes the
comparators of L7 that never fire, after which L7 uses only pairs (i, i+1) (h9.md, Lemma 6); variant
'free' does not use that lemma.  Both must be UNSAT for (H9) to hold.

usage: .venv/bin/python h9_sat.py [--variant adjacent|free|both] [--dimacs PREFIX] [solver ...]
       solvers: names from pysat (default cadical195); e.g. glucose4 kissat404 minisat22
"""
import argparse
import time

from satnet import Encoding, adjacent_pairs, solve, sorts

L1 = [(0, 1), (2, 3), (4, 5)]


def instance(variant):
    last = adjacent_pairs(9) if variant == 'adjacent' else None
    return Encoding(9, 6, caps=[3, None, None, None, None, None], prefix=[L1],
                    allowed=[None, None, None, None, None, last])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--variant', default='both', choices=['adjacent', 'free', 'both'])
    ap.add_argument('--dimacs', default=None, help='also write the CNF to PREFIX-<variant>.cnf')
    ap.add_argument('solvers', nargs='*', default=['cadical195'])
    a = ap.parse_args()
    variants = ['adjacent', 'free'] if a.variant == 'both' else [a.variant]
    for v in variants:
        enc = instance(v)
        print(f'(H9) variant {v}: {len(enc.inputs)} inputs, {enc.nvars} variables, '
              f'{len(enc.clauses)} clauses', flush=True)
        if a.dimacs:
            enc.write_dimacs(f'{a.dimacs}-{v}.cnf')
        for s in a.solvers:
            t = time.time()
            ok, model = solve(enc, s)
            dt = time.time() - t
            if ok:
                net = [L1] + enc.network(model)
                print(f'  {s}: SAT in {dt:.1f}s -- a counterexample to (H9):', net, flush=True)
                assert sorts(net, 9) and len(net[0]) <= 3 and len(net[1]) <= 3
            else:
                print(f'  {s}: UNSAT in {dt:.1f}s', flush=True)


if __name__ == '__main__':
    main()
