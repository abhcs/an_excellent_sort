#!/usr/bin/env python3
"""exc_pairs.py: which three-layer prefixes of an S11 network have NO good pair of sentinel tracks?

Two sentinels (+inf or -inf) whose tracks absorb two distinct comparators in every layer t <= m
that has more than a-2 comparators (one in a layer with exactly a-1) leave a residual sorter on
n-2 channels whose first m layers have <= a-2 comparators each (Fact B).  For S11 (n=11, a=4,
m=3) the residual violates SS(9,8,2,3).  A prefix (L1, L2, L3) is *pair-exceptional* if no pair
of tracks does this.  L1 is the fixed normal form; both sentinels must start in L1 comparators
(L1 has a comparators), on different ones.  L2 runs over the class reps, L3 over every matching
with <= a comparators none of which is redundant after L1;L2.

usage: exc_pairs.py CLASSES.json [OUT.json]
"""
import itertools, json, sys
import numpy as np


def apply(layer, x):
    for i, j in layer:
        if (x >> i) & 1 and not (x >> j) & 1:
            x ^= (1 << i) | (1 << j)
    return x


def matchings(n, kmax):
    out = []
    def rec(start, used, cur):
        out.append(list(cur))
        if len(cur) == kmax:
            return
        for i in range(start, n):
            if used >> i & 1:
                continue
            for j in range(i + 1, n):
                if used >> j & 1:
                    continue
                cur.append((i, j))
                rec(i + 1, used | (1 << i) | (1 << j), cur)
                cur.pop()
    rec(0, 0, [])
    return out


def step_pair(layer, tracks):
    """tracks: [(pos, sign), (pos, sign)] -> (new tracks, #distinct comparators absorbed)."""
    where = {}
    for c in layer:
        where[c[0]] = c
        where[c[1]] = c
    (u, s), (v, t) = tracks
    cu, cv = where.get(u), where.get(v)
    if cu is not None and cu == cv:              # both sentinels in one comparator
        i, j = cu
        if s == t:
            return [(u, s), (v, t)], 1               # two equal sentinels: positions unchanged as a set
        return ([(j, s), (i, t)] if s > 0 else [(i, s), (j, t)]), 1
    new, k = [], 0
    for (p, sg), c in ((tracks[0], cu), (tracks[1], cv)):
        if c is None:
            new.append((p, sg))
        else:
            k += 1
            new.append((c[1] if sg > 0 else c[0], sg))
    return new, k


def main():
    d = json.load(open(sys.argv[1]))
    n, a, L1, reps = d['n'], d['a'], [tuple(p) for p in d['L1']], d['reps']
    need = lambda c: max(0, c - (a - 2))         # absorptions needed in a layer with c comparators
    starts = [(hi, +1) for lo, hi in L1] + [(lo, -1) for lo, hi in L1]
    owner = {}
    for k, (lo, hi) in enumerate(L1):
        owner[lo] = owner[hi] = k
    pairs = [(x, y) for x, y in itertools.combinations(starts, 2) if owner[x[0]] != owner[y[0]]]
    M3 = matchings(n, a)
    cps = list(itertools.combinations(range(n), 2))
    cpi = {c: k for k, c in enumerate(cps)}
    U3 = np.array([sum((1 << i) | (1 << j) for i, j in L) for L in M3], dtype=np.int64)
    C3 = np.array([len(L) for L in M3])
    P3 = np.array([sum(1 << cpi[c] for c in L) for L in M3], dtype=np.uint64)
    partner = np.full((len(M3), n), -1, dtype=np.int64)
    for k, L in enumerate(M3):
        for i, j in L:
            partner[k, i], partner[k, j] = j, i
    results, total = [], 0
    for r, L2 in enumerate(reps):
        L2 = [tuple(p) for p in L2]
        X = {apply(L2, apply(L1, x)) for x in range(1 << n)}
        red = 0
        for (i, j) in cps:
            if not any((x >> i) & 1 and not (x >> j) & 1 for x in X):
                red |= 1 << cpi[(i, j)]
        keep = (P3 & np.uint64(red)) == 0
        alive = []                                # pairs that pass layers 1 and 2: positions after L2
        for pr in pairs:
            tr = [pr[0], pr[1]]
            tr, k1 = step_pair(L1, tr)
            assert k1 == 2
            tr, k2 = step_pair(L2, tr)
            if k2 >= need(len(L2)):
                alive.append((tr[0][0], tr[1][0]))
        exc = keep.copy()
        n3 = np.array([need(c) for c in C3])
        for u, v in alive:
            iu = (U3 >> u) & 1
            iv = (U3 >> v) & 1
            same = (partner[:, u] == v).astype(np.int64)
            got = iu + iv - same
            exc &= got < n3
        idx = np.nonzero(exc)[0]
        total += len(idx)
        results.append({'class': r, 'l2': L2, 'alive_pairs': len(alive), 'kept_L3': int(keep.sum()),
                        'exceptional_L3': [M3[k] for k in idx]})
    print(f'total exceptional (L2 rep, L3) prefixes: {total}')
    print('L2 classes with exceptional L3:', sum(1 for r in results if r['exceptional_L3']), 'of', len(reps))
    from collections import Counter
    print('by |L2|:', dict(sorted(Counter(len(r['l2']) for r in results if r['exceptional_L3']).items())))
    print('by |L3|:', dict(sorted(Counter(len(L) for r in results for L in r['exceptional_L3']).items())))
    if len(sys.argv) > 2:
        json.dump({'n': n, 'a': a, 'L1': L1, 'classes': results}, open(sys.argv[2], 'w'))


if __name__ == '__main__':
    main()
