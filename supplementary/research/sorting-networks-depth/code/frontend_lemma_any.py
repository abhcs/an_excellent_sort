"""Lemma F for odd n: every near-perfect matching M and every partition of [n]
into >= 2 intervals admits a state with no (1,0) on M that is non-constant on
two distinct blocks of size >= 2."""
import sys
import numpy as np

def perfect_matchings(items):
    if not items:
        yield (); return
    a = items[0]
    for k in range(1, len(items)):
        b = items[k]
        for m in perfect_matchings(tuple(x for x in items[1:] if x != b)):
            yield ((a, b),) + m

def run(n):
    parts = []
    for mask in range(1, 1 << (n - 1)):
        blocks, lo = [], 0
        for i in range(n - 1):
            if mask >> i & 1: blocks.append((lo, i)); lo = i + 1
        blocks.append((lo, n - 1))
        if len(blocks) >= 2: parts.append(tuple(blocks))
    ivs = [(a, b) for a in range(n) for b in range(a + 1, n)]
    idx = {v: i for i, v in enumerate(ivs)}
    allst = np.array([[(v >> i) & 1 for i in range(n)] for v in range(1 << n)], dtype=np.int8)
    bad = 0; cnt = 0
    for z in range(n):
        for M in perfect_matchings(tuple(x for x in range(n) if x != z)):
            cnt += 1
            ok = np.ones(1 << n, dtype=bool)
            for (a, b) in M: ok &= ~((allst[:, a] == 1) & (allst[:, b] == 0))
            U = allst[ok]
            mixed = np.zeros((U.shape[0], len(ivs)), dtype=np.int8)
            for j, (a, b) in enumerate(ivs):
                seg = U[:, a:b+1]; mixed[:, j] = (seg.min(axis=1) != seg.max(axis=1))
            A = (mixed.T.astype(np.int16) @ mixed.astype(np.int16)) > 0
            for P in parts:
                bl = [t for t in P if t[1] > t[0]]
                if len(bl) < 2: continue
                if not any(A[idx[bl[x]], idx[bl[y]]] for x in range(len(bl)) for y in range(x+1, len(bl))):
                    bad += 1; break
            if bad: break
        if bad: break
    print(f"n={n}: matchings {cnt}, partitions {len(parts)}, violations {bad}")

for n in (3, 5, 7, 9):
    run(n)
