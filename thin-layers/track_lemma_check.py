#!/usr/bin/env python3
"""track_lemma_check.py -- brute-force check of the three-layer track lemma.

Setting: n channels, first layer L1 = exactly a comparators (lo_j, hi_j), k = n - 2a idle channels.
A +inf sentinel on an input of comparator j sits on hi_j after L1, -inf on lo_j.  In every later
layer it moves to the max end (+inf) or min end (-inf) of the comparator it meets, if any.
A track is GOOD for (L2, L3) if it meets a comparator of L2 whenever |L2| = a, and a comparator of
L3 whenever |L3| = a.  The lemma claims a good track exists for EVERY pair (L2, L3) of matchings
with at most a comparators each, provided
    ceil((2a - k)/2) > k   and   2*ceil(a/2) > k.
For a fixed L2 the worst L3 at the cap leaves an arbitrary k-set W idle (any 2a channels can be
perfectly matched), so: a good track exists for all L3 at the cap  <=>  the set S of positions
after L2 of the tracks that pass L2 has more than k elements; for all L3 below the cap  <=>  S is
nonempty.  We enumerate every matching L2 (no symmetry reduction) and test both.
"""
import itertools
import json
import math
import sys

sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from thinsat import middle_layer  # noqa: E402


def matchings(n, cap):
    """All matchings on range(n) with at most cap edges (as dict partner)."""
    def rec(free, cur):
        yield dict(cur)
        if len(cur) // 2 >= cap or not free:
            return
        # choose the smallest vertex that will be matched next among free ones, to avoid repeats:
        # standard: iterate over first free vertex v either skipped (handled by ordering) or matched
    # simple generator: edges chosen in increasing order
    edges = list(itertools.combinations(range(n), 2))
    out = []

    def go(start, used, cur):
        out.append(dict(cur))
        if len(cur) // 2 == cap:
            return
        for idx in range(start, len(edges)):
            u, v = edges[idx]
            if u in used or v in used:
                continue
            cur[u], cur[v] = v, u
            used.add(u); used.add(v)
            go(idx + 1, used, cur)
            used.discard(u); used.discard(v)
            del cur[u]; del cur[v]
    go(0, set(), {})
    return out


def check(n, a):
    k = n - 2 * a
    L1 = middle_layer(n, a)
    claim = math.ceil((2 * a - k) / 2) > k and 2 * math.ceil(a / 2) > k
    bad_atcap, bad_below = 0, 0
    worst = None
    count = 0
    for M in matchings(n, a):
        count += 1
        at_cap = (len(M) // 2 == a)
        S = set()
        for lo, hi in L1:
            for start, sign in ((hi, +1), (lo, -1)):
                if start in M:
                    p = M[start]
                    pos = max(start, p) if sign > 0 else min(start, p)
                else:
                    if at_cap:
                        continue          # fails to meet L2, which must be met
                    pos = start
                S.add(pos)
        if len(S) <= k:
            bad_atcap += 1
            if worst is None or len(S) < worst[0]:
                worst = (len(S), sorted((u, v) for u, v in M.items() if u < v))
        if not S:
            bad_below += 1
    return {'n': n, 'a': a, 'k': k, 'L1': L1, 'second_layers': count, 'lemma_condition': claim,
            'L2_with_no_good_track_vs_some_L3_at_cap': bad_atcap,
            'L2_with_no_good_track_vs_L3_below_cap': bad_below, 'example_bad_L2': worst,
            'consistent': (bad_atcap == 0 and bad_below == 0) if claim else True}


if __name__ == '__main__':
    res = []
    for n, a in [(7, 3), (6, 2), (9, 4), (8, 3), (11, 5), (10, 4), (9, 3), (13, 6), (12, 5), (11, 4),
                 (15, 7), (14, 6), (13, 5), (12, 4)]:
        r = check(n, a)
        res.append(r)
        print(json.dumps({x: r[x] for x in r if x != 'L1'}), flush=True)
    if len(sys.argv) > 1:
        json.dump(res, open(sys.argv[1], 'w'), indent=1)
