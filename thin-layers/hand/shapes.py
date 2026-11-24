"""Shapes of optimal strategies: for each prefix, all pairs (L4, L5) reaching the least window sum; for
each comparator its 'top' units (window ranks removed at the min end) and 'bottom' units (at the max end),
and for layer-5 comparators the types of their inputs (min/max end of a layer-4 comparator, or idle).
usage: EXC.json KEY COUNT"""
import json, sys, itertools, collections
sys.path[:0] = ['.']
from ranks import states, rank_sets, states_step

d = json.load(open(sys.argv[1])); P = d[sys.argv[2]][:int(sys.argv[3])]
n = d['n']; W = set(range(n // 2 - 1, n // 2 + 2))


def ivs(X):
    return [(min(r), max(r)) for r in rank_sets(n, X)]


def units(iv_before, iv_after, u, v):
    """top units: window ranks in both inputs that the min end u lost; bottom: that the max end v lost."""
    both = W & set(range(iv_before[u][0], iv_before[u][1] + 1)) & set(range(iv_before[v][0], iv_before[v][1] + 1))
    top = sum(1 for k in both if k > iv_after[u][1])
    bot = sum(1 for k in both if k < iv_after[v][0])
    return top, bot


def matchings(chs):
    if not chs:
        yield []
        return
    c, rest = chs[0], chs[1:]
    yield from matchings(rest)
    for i, j in enumerate(rest):
        for m in matchings(rest[:i] + rest[i + 1:]):
            yield [(c, j)] + m


ALL = list(matchings(list(range(n))))
shape_count = collections.Counter()
for pre in P:
    X3 = states(n, pre); iv3 = ivs(X3)
    best, sols = 99, []
    for L4 in ALL:
        if not all(any((x >> i) & 1 and not (x >> j) & 1 for x in X3) for i, j in L4):
            continue
        X4 = states_step(n, X3, L4); iv4 = ivs(X4)
        for L5 in ALL:
            X5 = states_step(n, X4, L5); iv5 = ivs(X5)
            S = sum(len(set(range(a, b + 1)) & W) for a, b in iv5)
            if S < best:
                best, sols = S, []
            if S == best:
                sols.append((L4, L5, iv3, iv4, iv5))
    for L4, L5, iv3, iv4, iv5 in sols:
        kind = {c: 'i' for c in range(n)}
        for p, q in L4:
            kind[p], kind[q] = 'm', 'M'
        u4 = [units(iv3, iv4, p, q) for p, q in L4]
        u5 = [(kind[u] + kind[v], units(iv4, iv5, u, v)) for u, v in L5]
        key = (tuple(sorted(u4)), tuple(sorted(u5)))
        shape_count[key] += 1
for (u4, u5), c in shape_count.most_common(12):
    t4 = sum(a for a, b in u4); b4 = sum(b for a, b in u4)
    t5 = sum(a for _, (a, b) in u5); b5 = sum(b for _, (a, b) in u5)
    print(f'{c:3d}x  L4 (top,bottom) {list(u4)}  L5 {list(u5)}   totals top {t4}+{t5}, bottom {b4}+{b5}')
