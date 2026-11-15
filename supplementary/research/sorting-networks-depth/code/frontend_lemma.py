"""Check the front-end combinatorial lemma used to prove D(11) >= 8.

For n=11, a near-perfect matching M (5 disjoint comparators, one idle channel),
image(M) = {u in {0,1}^11 : u has no (1,0) on any edge of M}, |image| = 486.

Lemma to test: for EVERY near-perfect matching M and EVERY partition of [11]
into b >= 2 intervals ("blocks"), there is a state u in image(M) that is
non-constant ("mixed") on two distinct blocks of size >= 2.
"""
import itertools, sys
import numpy as np

n = 11
ch = list(range(n))

def perfect_matchings(items):
    if not items:
        yield ()
        return
    a = items[0]
    for k in range(1, len(items)):
        b = items[k]
        rest = tuple(x for x in items[1:] if x != b)
        for m in perfect_matchings(rest):
            yield ((a, b),) + m

def near_perfect():
    for z in ch:
        rest = tuple(x for x in ch if x != z)
        for m in perfect_matchings(rest):
            yield m

def partitions_of(n):
    """all interval partitions into >= 2 blocks, as tuples of (lo,hi) inclusive"""
    for mask in range(1, 1 << (n - 1)):
        blocks, lo = [], 0
        for i in range(n - 1):
            if mask >> i & 1:
                blocks.append((lo, i)); lo = i + 1
        blocks.append((lo, n - 1))
        if len(blocks) >= 2:
            yield tuple(blocks)

PARTS = list(partitions_of(n))
INTERVALS = [(a, b) for a in range(n) for b in range(a + 1, n)]  # size >= 2
IDX = {iv: i for i, iv in enumerate(INTERVALS)}

allstates = np.array([[ (v >> i) & 1 for i in range(n)] for v in range(1 << n)], dtype=np.int8)

bad = []
count = 0
for M in near_perfect():
    count += 1
    # valid states: no 10 on any edge
    ok = np.ones(1 << n, dtype=bool)
    for (a, b) in M:
        ok &= ~((allstates[:, a] == 1) & (allstates[:, b] == 0))
    U = allstates[ok]
    mixed = np.zeros((U.shape[0], len(INTERVALS)), dtype=np.int8)
    for j, (a, b) in enumerate(INTERVALS):
        seg = U[:, a:b+1]
        mixed[:, j] = (seg.min(axis=1) != seg.max(axis=1))
    A = mixed.T.astype(np.int16) @ mixed.astype(np.int16)   # A[i,j] > 0 iff some u mixed on both
    pairs_ok = A > 0
    for P in PARTS:
        bl = [iv for iv in P if iv[1] > iv[0]]
        if len(bl) < 2:
            continue
        good = False
        for x in range(len(bl)):
            for y in range(x + 1, len(bl)):
                if pairs_ok[IDX[bl[x]], IDX[bl[y]]]:
                    good = True; break
            if good: break
        if not good:
            bad.append((M, P))
            break
    if bad:
        break
print("matchings checked:", count, " violations:", len(bad))
if bad:
    print(bad[0])
