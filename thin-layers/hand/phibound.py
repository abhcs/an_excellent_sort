"""Additive bound for (W): S_5 >= sum_x phi(I_4(x)), phi([lo,hi]) = |[lo,hi] cap W| - (A-hi)^+ - (lo-B)^+,
because a layer-5 comparator (x, y) removes at most (a_x - 2)^+ + (a_y - 2)^+ ranks at its min end and
(b_x - 2)^+ + (b_y - 2)^+ at its max end (a = n - hi, b = lo + 1; overlap-free bounds).  For n = 9,
W = {3,4,5}: A = 7, B = 1.  Each layer-4 comparator then contributes phi(min end) + phi(max end), so the
least value over layers 4 is a least-cost matching on the prefix's pair table.
usage: EXC.json KEY [FIRST:LAST]"""
import json, sys, itertools, functools, collections
sys.path[:0] = ['.']
from ranks import states, rank_sets, states_step

d = json.load(open(sys.argv[1])); P = d[sys.argv[2]]
if len(sys.argv) > 3:
    a, b = map(int, sys.argv[3].split(':')); P = P[a:b]
n = d['n']; W = set(range(n // 2 - 1, n // 2 + 2)); A = n - 2; B = 1


def phi(iv):
    lo, hi = iv
    return len(set(range(lo, hi + 1)) & W) - max(0, A - hi) - max(0, lo - B)


def pair_out(X, p, q):
    """exact intervals of min and max of channels p < q after one comparator on X."""
    Y = states_step(n, X, [(p, q)])
    R = rank_sets(n, Y)
    return (min(R[p]), max(R[p])), (min(R[q]), max(R[q]))


res = collections.Counter()
for pre in P:
    X = states(n, pre)
    R = rank_sets(n, X)
    iv = [(min(r), max(r)) for r in R]
    idle = [phi(iv[c]) for c in range(n)]
    cost = {}
    for p, q in itertools.combinations(range(n), 2):
        if not any((x >> p) & 1 and not (x >> q) & 1 for x in X):
            continue                                   # redundant comparator
        mn, mx = pair_out(X, p, q)
        cost[(p, q)] = phi(mn) + phi(mx)

    @functools.lru_cache(None)
    def best(mask):
        if not mask:
            return 0
        i = (mask & -mask).bit_length() - 1
        rest = mask & ~(1 << i)
        v = idle[i] + best(rest)
        for j in range(n):
            if rest >> j & 1 and (i, j) in cost:
                v = min(v, cost[(i, j)] + best(rest & ~(1 << j)))
        return v
    res[best((1 << n) - 1)] += 1
print(f'{sum(res.values())} prefixes: least additive bound over layers 4:', sorted(res.items()),
      ' (13 or more settles the prefix)')
