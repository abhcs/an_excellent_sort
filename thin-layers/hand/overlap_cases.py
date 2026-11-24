"""For a prefix: the layers 4 where exact intervals after layer 4 + overlap-free calculus for layer 5 accept
a layer 5 (window sum <= 12), and for that layer 5, which comparators the calculus over-narrows compared
with the exact intervals, with the prefix channels each L5 input depends on (through layer 4).
usage: EXC.json KEY IDX [COUNT]"""
import json, sys, itertools
sys.path[:0] = ['.']
from ranks import states, rank_sets, states_step

d = json.load(open(sys.argv[1])); pre = d[sys.argv[2]][int(sys.argv[3])]
cnt = int(sys.argv[4]) if len(sys.argv) > 4 else 3
n = d['n']; W = set(range(n // 2 - 1, n // 2 + 2))


def intervals(X):
    return [(min(r), max(r)) for r in rank_sets(n, X)]


def relax_pair(iu, iv):
    (lu, hu), (lv, hv) = iu, iv
    lo_min = min(lu, lv); hi_min = max(lo_min, hu + hv - n)
    hi_max = max(hu, hv); lo_max = min(hi_max, lu + lv + 1)
    return (lo_min, hi_min), (lo_max, hi_max)


def w(iv):
    return len(set(range(iv[0], iv[1] + 1)) & W)


def matchings(chs):
    if not chs:
        yield []
        return
    c, rest = chs[0], chs[1:]
    yield from matchings(rest)
    for i, j in enumerate(rest):
        for m in matchings(rest[:i] + rest[i + 1:]):
            yield [(c, j)] + m


X3 = states(n, pre)
ALL = list(matchings(list(range(n))))
shown = 0
for L4 in ALL:
    if not L4 or not all(any((x >> i) & 1 and not (x >> j) & 1 for x in X3) for i, j in L4):
        continue
    X4 = states_step(n, X3, L4); iv4 = intervals(X4)
    # sources: which prefix channels feed each L4 output, and as min/max/idle
    src = {c: f'{c}' for c in range(n)}
    for p, q in L4:
        src[p] = f'min({p},{q})'; src[q] = f'max({p},{q})'
    for L5 in ALL:
        ivr = list(iv4)
        for u, v in L5:
            ivr[u], ivr[v] = relax_pair(iv4[u], iv4[v])
        if sum(w(x) for x in ivr) > 12:
            continue
        X5 = states_step(n, X4, L5); iv5 = intervals(X5)
        print(f'L4 {L4}  L5 {L5}: calculus S5={sum(w(x) for x in ivr)}, exact S5={sum(w(x) for x in iv5)}')
        for u, v in L5:
            if (ivr[u], ivr[v]) != (iv5[u], iv5[v]):
                print(f'    over-narrowed: ({u},{v}) = ({src[u]} {iv4[u]}, {src[v]} {iv4[v]}) -> calculus {ivr[u]},{ivr[v]}  exact {iv5[u]},{iv5[v]}')
        shown += 1
        break
    if shown >= cnt:
        break
