"""h11_sat.py -- the SAT searches behind h9.md section 9 (needs python-sat; about 70 s in all).

1. (H11): is there a sorting network on 11 channels with at most 8 layers whose first two layers have at
   most four comparators each?  D(13) >= 9 would follow from "no" by the two-sentinel argument.  Layer 1
   is (0,1)(2,3)(4,5)(6,7) (fill it to four comparators by Tool B, then relabel and untangle), layer 2
   any matching with at most four comparators, layers 3-8 any matchings, layer 8 adjacent pairs only
   (h9.md Lemma 6).  The answer is yes: (H11) is false.
2. The two 7-channel shapes just beyond (P7): six layers with two comparators in the first, and seven
   layers with one comparator in each of the first two.  Both contain sorting networks.
The networks found are checked by brute force here and listed in d13_networks.py.

usage: .venv/bin/python h11_sat.py [solver]   (default cadical195)
"""
import sys
import time

from satnet import Encoding, adjacent_pairs, solve, sorts


def search(name, n, d, caps, prefix=()):
    enc = Encoding(n, d, caps=caps, prefix=prefix, allowed=[None] * (d - 1) + [adjacent_pairs(n)])
    t = time.time()
    ok, model = solve(enc, sys.argv[1] if len(sys.argv) > 1 else 'cadical195')
    dt = time.time() - t
    if not ok:
        print(f'{name}: no network ({dt:.0f} s)', flush=True)
        return None
    net = [list(L) for L in prefix] + enc.network(model)
    assert sorts(net, n)
    print(f'{name}: a sorting network ({dt:.0f} s), layer sizes {[len(L) for L in net]}:', flush=True)
    print('   ', ' | '.join(''.join(f'({a},{b})' for a, b in L) for L in net), flush=True)
    return net


search('(H11), 11 channels, 8 layers, |L1| = 4, |L2| <= 4', 11, 7, [4, None, None, None, None, None, None],
       prefix=[[(0, 1), (2, 3), (4, 5), (6, 7)]])
search('7 channels, 6 layers, |L1| <= 2', 7, 6, [2, None, None, None, None, None])
search('7 channels, 7 layers, |L1| <= 1, |L2| <= 1', 7, 7, [1, 1, None, None, None, None, None])
