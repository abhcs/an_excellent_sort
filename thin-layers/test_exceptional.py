#!/usr/bin/env python3
"""test_exceptional.py n a m trials: compare the SAT encoding of 'no good track through layers 1..m'
(exceptional.py) with a direct computation, on random layers 2..m (fixed by unit clauses)."""
import random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'd18-search'))
from netsat import Model
from thinsat import middle_layer
from exceptional import add_exceptional
from descent import track

n, a, m, trials = map(int, sys.argv[1:5])
rng = random.Random(1)
L1 = middle_layer(n, a)
lo_hi = {c for p in L1 for c in p}


def rand_layer(size):
    while True:
        ch = list(range(n)); rng.shuffle(ch)
        L = [tuple(sorted(ch[2 * i:2 * i + 2])) for i in range(size)]
        if not (set(L) & set(L1)):
            return sorted(L)


def direct_exceptional(layers):
    full = [len(layers[t]) == a for t in range(m)]
    for lo, hi in L1:
        for start, sign in ((hi, 1), (lo, -1)):
            _, meets = track(layers, start, sign, upto=m)
            if all(meets[t] or not full[t] for t in range(1, m)):
                return False
    return True


agree = disagree = exc = 0
for k in range(trials):
    sizes = [rng.choice([a, a, a, a - 1]) for _ in range(m - 1)]
    layers = [L1] + [rand_layer(s) for s in sizes]
    want = direct_exceptional(layers)
    M = Model(n, 6, [], nored0=False, phi=False)
    add_exceptional(M, n, a, L1, m)
    for t in range(m - 1):
        S = set(layers[t + 1])
        for p, v in M.g[t].items():
            M.add([v] if p in S else [-v])
    got = M.S.solve()
    exc += want
    if got == want:
        agree += 1
    else:
        disagree += 1
        print('DISAGREE', layers, 'direct', want, 'sat', got)
print(f'n={n} a={a} m={m}: {trials} random layer stacks, {exc} exceptional, agree={agree} disagree={disagree}')


def mutate(layer, size_cap):
    """Random local change of a matching: re-pair two comparators, or move one endpoint."""
    L = [list(p) for p in layer]
    used = {c for p in L for c in p}
    free = [c for c in range(n) if c not in used]
    r = rng.random()
    if r < 0.4 and len(L) >= 2:
        i, j = rng.sample(range(len(L)), 2)
        (a1, b1), (a2, b2) = L[i], L[j]
        L[i], L[j] = [a1, a2], [b1, b2]
    elif r < 0.8 and free:
        i = rng.randrange(len(L)); k = rng.randrange(2)
        L[i][k] = rng.choice(free)
    elif len(L) > 1 and r < 0.9:
        L.pop(rng.randrange(len(L)))
    elif len(free) >= 2 and len(L) < size_cap:
        x, y = rng.sample(free, 2); L.append([x, y])
    L = sorted(tuple(sorted(p)) for p in L)
    if set(L) & set(L1) or any(p[0] == p[1] for p in L):
        return list(layer)
    return L


if n == 12 and a == 5 and m == 4:
    base = [L1, [(1, 3), (2, 4), (5, 7), (6, 8), (0, 11)], [(1, 5), (4, 8), (0, 2), (3, 6), (7, 9)],
            [(0, 2), (3, 4), (5, 6), (7, 9), (10, 11)]]
    print('hand-built example exceptional (direct):', direct_exceptional(base))
    agree2 = dis2 = exc2 = 0
    for k in range(600):
        layers = [L1] + [mutate(base[t], a) if rng.random() < 0.5 else list(base[t]) for t in range(1, m)]
        want = direct_exceptional(layers)
        M = Model(n, 6, [], nored0=False, phi=False)
        add_exceptional(M, n, a, L1, m)
        for t in range(m - 1):
            S = set(layers[t + 1])
            for p, v in M.g[t].items():
                M.add([v] if p in S else [-v])
            for p in S:
                if p not in M.g[t]:
                    M.add([])
        got = M.S.solve()
        exc2 += want
        if got == want:
            agree2 += 1
        else:
            dis2 += 1
            print('DISAGREE', layers, want, got)
    print(f'mutations of the hand-built example: 600 stacks, {exc2} exceptional, agree={agree2} disagree={dis2}')
