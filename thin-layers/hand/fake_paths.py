"""Pairs of layers 4, 5 that the overlap-free interval calculus accepts (window sum <= 12) for a prefix,
compared with the exact intervals: which comparator ends does the calculus over-narrow, and are
those comparators redundant?  usage: EXC.json KEY IDX [COUNT]"""
import json, sys, itertools, collections
sys.path[:0] = ['.']
from ranks import states, rank_sets, states_step

d = json.load(open(sys.argv[1])); pre = d[sys.argv[2]][int(sys.argv[3])]
cnt = int(sys.argv[4]) if len(sys.argv) > 4 else 5
n = d['n']; W = set(range(n // 2 - 1, n // 2 + 2))


def matchings(chs):
    if not chs:
        yield []
        return
    c, rest = chs[0], chs[1:]
    yield from matchings(rest)
    for i, j in enumerate(rest):
        for m in matchings(rest[:i] + rest[i + 1:]):
            yield [(c, j)] + m


def intervals(X):
    R = rank_sets(n, X)
    return [(min(r), max(r)) for r in R]


def relax(iv, L):
    iv = list(iv)
    for i, j in L:
        (li, hi_), (lj, hj) = iv[i], iv[j]
        iv[i] = (min(li, lj), max(min(li, lj), hi_ + hj - n))
        iv[j] = (min(li + lj + 1, max(hi_, hj)), max(hi_, hj))
    return iv


def wsum(iv):
    return sum(len(set(range(a, b + 1)) & W) for a, b in iv)


X3 = states(n, pre)
iv3 = intervals(X3)
ALL = list(matchings(list(range(n))))
shown = 0
stats = collections.Counter()
for L4 in ALL:
    iv4r = relax(iv3, L4)
    X4 = states_step(n, X3, L4)
    iv4 = intervals(X4)
    for L5 in ALL:
        iv5r = relax(iv4r, L5)
        if wsum(iv5r) > 12:
            continue
        X5 = states_step(n, X4, L5)
        iv5 = intervals(X5)
        # where does the calculus over-narrow? compare layer-4 intervals (relaxed from exact layer 3)
        bad4 = [(i, j) for i, j in L4 if iv4r[i] != iv4[i] or iv4r[j] != iv4[j]]
        red4 = [(i, j) for i, j in L4 if not any((x >> i) & 1 and not (x >> j) & 1 for x in X3)]
        stats['fake pairs'] += 1
        stats['layer 4 over-narrowed'] += bool(bad4)
        stats['layer 4 has a redundant comparator'] += bool(red4)
        if shown < cnt:
            shown += 1
            print('L4', L4, 'L5', L5, f'calculus S5={wsum(iv5r)}, exact S5={wsum(iv5)}')
            print('   exact after 3:', iv3)
            print('   calc  after 4:', iv4r)
            print('   exact after 4:', iv4, ' over-narrowed comparators:', bad4, ' redundant:', red4)
print(dict(stats))
