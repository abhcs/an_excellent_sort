"""Exhaustive sanity checks of the small-width facts the six-real exchange rule uses:
  (T5) README Lemma 3: no depth-5 sorter on 5 wires has <=1 gate in BOTH of its first two layers
  (the stronger 'at least two in each' is false: 34 | 13 24 | 02 34 | 01 23 | 12 34 sorts);
  (S6) a depth-5 sorter on 6 wires has >=2 gates first, and if exactly 2 first then 3 second.
Search over images of binary vectors with memoisation; layers are arbitrary matchings."""
import itertools
import sys
from functools import lru_cache

sys.setrecursionlimit(10000)


def matchings(n):
    out = []

    def rec(i, used, cur):
        if i == n:
            out.append(tuple(cur)); return
        if i in used:
            rec(i + 1, used, cur); return
        rec(i + 1, used, cur)
        for j in range(i + 1, n):
            if j not in used:
                rec(i + 1, used | {i, j}, cur + [(i, j)])
    rec(0, frozenset(), [])
    return out


def make(n):
    MS = matchings(n)
    vecs = list(range(1 << n))  # bit i = wire i

    def apply_vec(v, layer):
        for a, b in layer:
            ba, bb = (v >> a) & 1, (v >> b) & 1
            if ba > bb:  # min to a
                v ^= (1 << a) | (1 << b)
        return v
    table = [[apply_vec(v, L) for v in vecs] for L in MS]
    sorted_mask = 0
    for k in range(n + 1):
        v = sum(1 << i for i in range(n - k, n))  # zeros low, ones high
        sorted_mask |= 1 << v

    def apply(state, li):
        t = table[li]; out = 0; s = state
        while s:
            low = s & -s; v = low.bit_length() - 1; s ^= low
            out |= 1 << t[v]
        return out

    @lru_cache(maxsize=None)
    def can(state, k):
        if state & ~sorted_mask == 0:
            return True
        if k == 0:
            return False
        for li in range(len(MS)):
            if can(apply(state, li), k - 1):
                return True
        return False
    full = (1 << (1 << n)) - 1
    return MS, apply, can, full


# T5
MS5, ap5, can5, full5 = make(5)
bad = []
for i1, L in enumerate(MS5):
    s1 = ap5(full5, i1)
    for i2, L2 in enumerate(MS5):
        if len(L) <= 1 and len(L2) <= 1:
            if can5(ap5(s1, i2), 3):
                bad.append((L, L2))
print('T5 counterexamples (first AND second layer <=1 gate, depth 5):', bad[:3], len(bad))
assert not bad
# sanity: some depth-5 5-wire sorter exists, none of depth 4
assert can5(full5, 5) and not can5(full5, 4)

# S6
MS6, ap6, can6, full6 = make(6)
assert can6(full6, 5) and not can6(full6, 4)
bad = []
for i1, L in enumerate(MS6):
    if len(L) > 2:
        continue
    s1 = ap6(full6, i1)
    for i2, L2 in enumerate(MS6):
        if len(L) <= 1 or len(L2) <= 2:
            if can6(ap6(s1, i2), 3):
                bad.append((L, L2))
print('S6 counterexamples:', bad[:3], len(bad))
assert not bad
print('SMALL OK')
