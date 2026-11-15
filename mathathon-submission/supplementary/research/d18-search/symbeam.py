#!/usr/bin/env python3
"""symbeam.py -- greedy beam search for reflection-symmetric prefixes with few outputs.

Following C. Wang, "Depth-13 sorting networks for 28 channels" (arXiv 2511.04107), section 3.2:
grow a reflection-symmetric prefix one comparator (plus its mirror image) at a time, keeping the
B prefixes with the smallest output sets; finish a layer, then start the next.  Output sets that
look isomorphic under reflection-symmetric channel permutations and negation (same invariants)
are merged, a cheap stand-in for the subsumption test of that paper.

Writes JSON lines {"n":..,"outputs":..,"layers":..} for the best prefixes of the final depth.
"""
import argparse
import json
import sys

sys.path.insert(0, __import__('os').path.dirname(__file__))
from netsat import is_self_dual, mirror  # noqa: E402


def apply_pair(S, cs):
    out = set()
    for x in S:
        for (i, j) in cs:
            if (x >> i) & 1 and not (x >> j) & 1:
                x ^= (1 << i) | (1 << j)
        out.add(x)
    return frozenset(out)


def invariant(S, n):
    """Cheap isomorphism invariant under reflection-symmetric permutations (and negation+reflection)."""
    col = [0] * n
    rows = [0] * (n + 1)
    for x in S:
        rows[bin(x).count('1')] += 1
        for k in range(n):
            if (x >> k) & 1:
                col[k] += 1
    m = len(S)
    pairs = sorted(tuple(sorted((col[k], m - col[n - 1 - k]))) for k in range(n // 2))
    # negation+reflection maps weight w to n-w and column k to column n-1-k complemented
    rows_t = tuple(rows)
    return (m, tuple(pairs), min(rows_t, rows_t[::-1]))


def beam(n, first_layer, depth, B, log=print):
    full = frozenset(range(1 << n))
    S1 = apply_pair(full, first_layer)
    states = [([list(first_layer)], S1)]                     # (layers, output set)
    for layer_idx in range(1, depth):
        cur = [(layers + [[]], S) for (layers, S) in states]
        for step in range(n // 2):
            cand = {}
            for (layers, S) in cur:
                key = invariant(S, n)
                if key not in cand or len(cand[key][1]) > len(S):
                    cand[key] = (layers, S)
                used = {k for c in layers[-1] for k in c}
                for i in range(n):
                    if i in used:
                        continue
                    for j in range(i + 1, n):
                        if j in used:
                            continue
                        c = (i, j)
                        m = mirror(n, c)
                        cs = [c] if m == c else [c, m]
                        if m != c and (m[0] in used or m[1] in used or m[0] in c or m[1] in c):
                            continue
                        T = apply_pair(S, cs)
                        if len(T) == len(S) and T == S:
                            continue                         # redundant
                        nl = layers[:-1] + [sorted(layers[-1] + cs)]
                        key = invariant(T, n)
                        if key not in cand or len(cand[key][1]) > len(T):
                            cand[key] = (nl, T)
            cur = sorted(cand.values(), key=lambda t: len(t[1]))[:B]
            log(f'layer {layer_idx + 1} step {step + 1}: best {len(cur[0][1])} worst kept {len(cur[-1][1])} '
                f'({len(cand)} candidates)')
        states = cur
    return states


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=18)
    ap.add_argument('--depth', type=int, default=4)
    ap.add_argument('--beam', type=int, default=64)
    ap.add_argument('--first', default='pb', help='pb: (2i,2i+1); bz: (i,n-1-i)')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    n = args.n
    if args.first == 'pb':
        L1 = [(2 * i, 2 * i + 1) for i in range(n // 2)]
    else:
        L1 = [(i, n - 1 - i) for i in range(n // 2)]
    states = beam(n, L1, args.depth, args.beam, log=lambda s: print(s, flush=True))
    with open(args.out, 'w') as f:
        for layers, S in states:
            layers = [sorted(map(list, L)) for L in layers if L]
            assert is_self_dual(n, [[tuple(c) for c in L] for L in layers])
            f.write(json.dumps({'n': n, 'outputs': len(S), 'layers': layers}) + '\n')
    print('best output sizes:', [len(S) for _, S in states[:10]])


if __name__ == '__main__':
    main()
