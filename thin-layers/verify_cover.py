#!/usr/bin/env python3
"""verify_cover.py CLASSES.json: independent check that the second-layer classes cover every case.

Recounts, by a memoized recursion over vertex sets (not by listing), the matchings with at most a
edges on n channels that avoid the L1 pairs; recomputes each representative's orbit by breadth-first
search under GENERATORS of the symmetry group (adjacent swaps of L1 pairs, min end with min end and
max end with max end; adjacent swaps of idle channels; duality i -> n-1-i if L1 is self-dual), and
checks: the orbits are pairwise disjoint, every representative is a legal second layer, and the
orbit sizes add up to the recount.  Then every legal second layer lies in exactly one class."""
import functools, json, sys

d = json.load(open(sys.argv[1]))
n, a, L1, reps = d['n'], d['a'], [tuple(p) for p in d['L1']], [[tuple(e) for e in r] for r in d['reps']]
banned = set(L1)
idle = [c for c in range(n) if all(c not in p for p in L1)]


@functools.lru_cache(maxsize=None)
def count(mask, k):
    """Matchings with exactly k edges using only channels in mask, avoiding banned pairs."""
    if k == 0:
        return 1
    if bin(mask).count('1') < 2 * k:
        return 0
    v = (mask & -mask).bit_length() - 1
    rest = mask & ~(1 << v)
    total = count(rest, k)                       # v unmatched
    m = rest
    while m:
        u = (m & -m).bit_length() - 1
        m &= m - 1
        if (v, u) not in banned:
            total += count(rest & ~(1 << u), k - 1)
    return total


full = (1 << n) - 1
recount = sum(count(full, k) for k in range(a + 1))

gens = []
for i in range(len(L1) - 1):
    g = list(range(n))
    (p, q), (r, s) = L1[i], L1[i + 1]
    g[p], g[r], g[q], g[s] = r, p, s, q
    gens.append(g)
for i in range(len(idle) - 1):
    g = list(range(n)); g[idle[i]], g[idle[i + 1]] = idle[i + 1], idle[i]; gens.append(g)
selfdual = {(n - 1 - j, n - 1 - i) for (i, j) in L1} == banned
if selfdual:
    gens.append([n - 1 - c for c in range(n)])


def canon(M):
    return tuple(sorted(tuple(sorted(e)) for e in M))


def orbit(M):
    start = canon(M)
    seen, frontier = {start}, [start]
    while frontier:
        nxt = []
        for X in frontier:
            for g in gens:
                Y = canon([(g[x], g[y]) for x, y in X])
                if Y not in seen:
                    seen.add(Y); nxt.append(Y)
        frontier = nxt
    return seen


union, total, ok = set(), 0, True
for r in reps:
    used = [c for e in r for c in e]
    legal = len(set(used)) == len(used) and len(r) <= a and not (set(map(tuple, map(sorted, r))) & banned)
    o = orbit(r)
    if not legal or (o & union):
        ok = False
    union |= o
    total += len(o)
res = {'n': n, 'a': a, 'L1': L1, 'self_dual_L1': selfdual, 'classes': len(reps),
       'second_layers_recounted': recount, 'orbit_sizes_sum': total, 'orbits_disjoint_and_legal': ok,
       'cover_complete': ok and total == recount}
print(json.dumps(res))
