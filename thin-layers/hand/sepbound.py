"""Separation bound: S_5 >= S_3 - R_4 - nu_5, where R_4 = window incidences removed by layer 4 and nu_5 =
largest matching of separation weights after layer 4 (sum over window ranks k on both channels of
[k always the larger] + [k always the smaller]).  Checks how close S_3 - R_4 - nu_5 comes to the true
least S_5 over all layers 5, for every non-redundant layer 4 of a prefix.  usage: EXC.json KEY IDX"""
import json, sys, itertools, functools, collections
sys.path[:0] = ['.']
from ranks import states, rank_sets, states_step

d = json.load(open(sys.argv[1])); pre = d[sys.argv[2]][int(sys.argv[3])]
n = d['n']; W = set(range(n // 2 - 1, n // 2 + 2))
POP = [bin(s).count('1') for s in range(1 << n)]


def intervals(X):
    return [(min(r), max(r)) for r in rank_sets(n, X)]


def wsum(iv):
    return sum(len(set(range(a, b + 1)) & W) for a, b in iv)


def sep_weights(X, iv):
    wt = {}
    for u, v in itertools.combinations(range(n), 2):
        c = 0
        for k in W:
            if not (iv[u][0] <= k <= iv[u][1] and iv[v][0] <= k <= iv[v][1]):
                continue
            if not any(POP[s] == n - k and (s >> u) & 1 and (s >> v) & 1 for s in X):
                c += 1
            if not any(POP[s] == n - 1 - k and not (s >> u) & 1 and not (s >> v) & 1 for s in X):
                c += 1
        if c:
            wt[(u, v)] = c
    return wt


def max_matching(wt):
    @functools.lru_cache(None)
    def f(mask):
        if not mask:
            return 0
        i = (mask & -mask).bit_length() - 1
        rest = mask & ~(1 << i)
        best = f(rest)
        for j in range(n):
            if rest >> j & 1 and (i, j) in wt:
                best = max(best, wt[(i, j)] + f(rest & ~(1 << j)))
        return best
    return f((1 << n) - 1)


def matchings(chs):
    if not chs:
        yield []
        return
    c, rest = chs[0], chs[1:]
    yield from matchings(rest)
    for i, j in enumerate(rest):
        for m in matchings(rest[:i] + rest[i + 1:]):
            yield [(c, j)] + m


X3 = states(n, pre); iv3 = intervals(X3); S3 = wsum(iv3)
ALL = list(matchings(list(range(n))))
rows = []
for L4 in ALL:
    if not all(any((x >> i) & 1 and not (x >> j) & 1 for x in X3) for i, j in L4):
        continue
    X4 = states_step(n, X3, L4); iv4 = intervals(X4); S4 = wsum(iv4)
    nu5 = max_matching(sep_weights(X4, iv4))
    rows.append((S4 - nu5, S4, nu5, L4))
print(f'prefix {sys.argv[3]}: S3 = {S3}; {len(rows)} layers 4; separation bound S4 - nu5 ranges',
      min(r[0] for r in rows), '..', max(r[0] for r in rows))
print('   histogram of S4 - nu5:', sorted(collections.Counter(r[0] for r in rows).items()))
for r in sorted(rows)[:6]:
    print('   ', r)
