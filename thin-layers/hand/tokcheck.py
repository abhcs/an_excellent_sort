"""Independent check of tokcore.c on sample prefixes: enumerate every non-redundant layer 4 and every
layer 5 (no pruning), compute the reachable set and the token sets directly, and confirm that some
output has more than 4 token channels after layer 5.  numpy; usage: EXC.json KEY FIRST:LAST"""
import json, sys
import numpy as np

d = json.load(open(sys.argv[1])); key = sys.argv[2]
a, b = map(int, sys.argv[3].split(':'))
n = d['n']; N = 1 << n
pop = np.array([bin(s).count('1') for s in range(N)])


def matchings(chs):
    if not chs:
        yield []
        return
    c, rest = chs[0], chs[1:]
    yield from matchings(rest)
    for i, j in enumerate(rest):
        for m in matchings(rest[:i] + rest[i + 1:]):
            yield [(c, j)] + m


def layer_map(L):
    s = np.arange(N)
    for i, j in L:
        sw = ((s >> i) & 1 == 1) & ((s >> j) & 1 == 0)
        s = np.where(sw, s ^ ((1 << i) | (1 << j)), s)
    return s


ALL = list(matchings(list(range(n))))
MAPS = np.array([layer_map(L) for L in ALL])


def tok_max(X):
    """largest |T(k)| over outputs k for reachable set X (boolean array)."""
    inX = X
    S = np.nonzero(X)[0]
    best = 0
    T = np.zeros(n, dtype=np.int64)          # bitmask per output
    for j in range(n):
        free = ((S >> j) & 1) == 0
        sj = S[free]
        hit = inX[sj | (1 << j)]
        ks = n - 1 - pop[sj[hit]]
        for k in np.unique(ks):
            T[k] |= 1 << j
    return max(bin(int(t)).count('1') for t in T)


def nonred(X, L):
    S = np.nonzero(X)[0]
    return all(np.any(((S >> i) & 1 == 1) & ((S >> j) & 1 == 0)) for i, j in L)


for idx, pre in enumerate(d[key][a:b], start=a):
    X = np.ones(N, dtype=bool)
    for L in pre:
        Y = np.zeros(N, dtype=bool); Y[layer_map(L)[X]] = True; X = Y
    n4 = n45 = 0; worst = 99
    for m4, L4 in zip(MAPS, ALL):
        if not nonred(X, L4):
            continue
        X4 = np.zeros(N, dtype=bool); X4[m4[X]] = True
        n4 += 1
        for m5 in MAPS:
            X5 = np.zeros(N, dtype=bool); X5[m5[X4]] = True
            n45 += 1
            v = tok_max(X5)
            worst = min(worst, v)
    print(f'prefix {idx}: {n4} non-redundant layers 4, {n45} pairs (L4, L5); least max_k |T_5(k)| = {worst} '
          f'({"refuted" if worst > 4 else "NOT refuted"})', flush=True)
