"""Lemma 4, the counting step, exhaustively: first layer (0,1),(2,3),(4,5) with channel 6 idle
(lo_i = 2i, hi_i = 2i+1).  For EVERY matching L2 on 7 channels (any size) some i != j has the property
that, with +inf on hi_i and -inf on lo_j, at most one comparator of L2 meets two reals.
(Layer 1 then has exactly one such comparator, the pair k not in {i, j}.)"""
from netlib import matchings

bad = []
L2s = matchings(7)
for L2 in L2s:
    ok = any(sum(1 for (a, b) in L2 if a not in {2 * i + 1, 2 * j} and b not in {2 * i + 1, 2 * j}) <= 1
             for i in range(3) for j in range(3) if i != j)
    if not ok:
        bad.append(L2)
print(f'Lemma 4: {len(L2s)} second layers, {len(bad)} without a good (i, j)')
assert not bad
