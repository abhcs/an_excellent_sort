#!/usr/bin/env python3
"""d13_networks.py -- the networks behind h9.md section 9, checked on all binary inputs.

1. (H11) is false.  An 8-layer sorting network on 11 channels whose first two layers have four
   comparators each (found by h11_sat.py).  So the two-sentinel route of README Lemma 4 / h9.md
   Corollary 8 cannot give D(13) >= 9.
2. (P7) is as far as three-layer blinding on 13 channels can go.  Seven reals that meet more than once
   in layers 1-3 meet in one layer at least twice, or in two layers.  The first case leaves a 7-channel
   network of six layers whose first has two comparators, the second one of seven layers whose first
   two have one comparator each.  Both shapes contain sorting networks (found by h11_sat.py), so no
   statement about these shapes can do better than (P7).

Needs only python3.  Exit status 0 iff every network is a matching per layer, has the stated shape,
and sorts.  usage: python3 d13_networks.py
"""
import sys

H11 = [[(0, 1), (2, 3), (4, 5), (6, 7)],
       [(0, 8), (1, 7), (4, 6), (9, 10)],
       [(0, 4), (1, 5), (2, 9), (3, 10), (6, 8)],
       [(1, 2), (3, 6), (4, 9), (5, 7), (8, 10)],
       [(0, 1), (2, 8), (3, 4), (5, 9), (6, 7)],
       [(1, 3), (2, 4), (5, 6), (7, 10), (8, 9)],
       [(0, 1), (2, 3), (4, 5), (6, 8), (7, 9)],
       [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]]
SIX_LAYERS_L1_TWO = [[(1, 2), (3, 5)],
                     [(0, 3), (1, 4), (5, 6)],
                     [(0, 1), (2, 3), (4, 5)],
                     [(1, 2), (3, 4), (5, 6)],
                     [(1, 3), (2, 5), (4, 6)],
                     [(0, 1), (2, 3), (4, 5)]]
SEVEN_LAYERS_ONE_ONE = [[(3, 5)],
                        [(1, 5)],
                        [(0, 1), (2, 3), (4, 5)],
                        [(0, 2), (1, 3), (4, 6)],
                        [(1, 6), (2, 4), (3, 5)],
                        [(0, 2), (1, 4), (3, 6)],
                        [(1, 2), (3, 4), (5, 6)]]


def check(name, net, n, sizes):
    ok = all(a < b for L in net for a, b in L)
    ok &= all(len({x for e in L for x in e}) == 2 * len(L) for L in net)
    ok &= [len(L) for L in net] == sizes
    for x in range(1 << n):
        v = [x >> i & 1 for i in range(n)]
        for L in net:
            for a, b in L:
                if v[a] > v[b]:
                    v[a], v[b] = v[b], v[a]
        if v != sorted(v):
            ok = False
            break
    print('  %-62s %s' % (name, 'sorts all %d binary inputs' % (1 << n) if ok else 'FAILS'))
    return ok


print('the networks of h9.md section 9')
results = [
    check('(H11) is false: 11 channels, 8 layers, sizes 4,4,5,5,5,5,5,5', H11, 11, [4, 4, 5, 5, 5, 5, 5, 5]),
    check('7 channels, 6 layers, first layer with two comparators', SIX_LAYERS_L1_TWO, 7, [2, 3, 3, 3, 3, 3]),
    check('7 channels, 7 layers, first two layers with one comparator each', SEVEN_LAYERS_ONE_ONE, 7, [1, 1, 3, 3, 3, 3, 3]),
]
print('all networks check out' if all(results) else 'SOME NETWORK FAILS')
sys.exit(0 if all(results) else 1)
