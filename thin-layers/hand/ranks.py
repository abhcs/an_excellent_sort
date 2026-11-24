"""Rank sets R_t(c) = {k : channel c holds a token of output k after layer t} (the transpose of the token
sets).  Checks whether they are intervals and prints (lo, hi) per channel along a network.
usage: ranks.py N 'NETWORK_JSON' [FROM]"""
import json, sys


def states(n, layers):
    X = set(range(1 << n))
    for L in layers:
        Y = set()
        for x in X:
            for i, j in L:
                if (x >> i) & 1 and not (x >> j) & 1:
                    x ^= (1 << i) | (1 << j)
            Y.add(x)
        X = Y
    return X


def rank_sets(n, X):
    R = [set() for _ in range(n)]
    for s in X:
        k = n - 1 - bin(s).count('1')
        for j in range(n):
            if not (s >> j) & 1 and (s | (1 << j)) in X:
                R[j].add(k)
    return R


def profile(n, net, start=0):
    out = []
    X = states(n, net[:start])
    for t in range(start, len(net) + 1):
        if t > start:
            X = states_step(n, X, net[t - 1])
        R = rank_sets(n, X)
        holes = sum((max(r) - min(r) + 1 - len(r)) if r else 0 for r in R)
        out.append((t, [(min(r), max(r)) if r else None for r in R], holes))
    return out


def states_step(n, X, L):
    Y = set()
    for x in X:
        for i, j in L:
            if (x >> i) & 1 and not (x >> j) & 1:
                x ^= (1 << i) | (1 << j)
        Y.add(x)
    return Y


if __name__ == '__main__':
    n = int(sys.argv[1])
    net = json.loads(sys.argv[2])
    start = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    for t, iv, holes in profile(n, net, start):
        print(f'after layer {t}: holes {holes}; (lo,hi) per channel', iv)
