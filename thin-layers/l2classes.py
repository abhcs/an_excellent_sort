#!/usr/bin/env python3
"""l2classes.py n a: second layers (<= a comparators, none equal to an L1 pair) for the thin prefix
L1 = a middle pairs, up to the symmetries that fix L1: permuting the L1 pairs (min end to min end),
permuting the n-2a idle channels, and duality (i -> n-1-i, which swaps min and max ends)."""
import itertools, json, sys


def classes(n, a, cap=None):
    cap = a if cap is None else cap
    sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
    from thinsat import middle_layer
    pairs = middle_layer(n, a)
    idle = [k for k in range(n) if not any(k in p for p in pairs)]
    perms = []
    for pp in itertools.permutations(range(a)):
        for ip in itertools.permutations(idle):
            m = {}
            for i, j in enumerate(pp):
                m[pairs[i][0]] = pairs[j][0]
                m[pairs[i][1]] = pairs[j][1]
            for u, v in zip(idle, ip):
                m[u] = v
            perms.append(m)
    dual = {k: n - 1 - k for k in range(n)}
    selfdual = {(n - 1 - j, n - 1 - i) for (i, j) in pairs} == set(pairs)
    group = perms + ([{k: dual[m[k]] for k in range(n)} for m in perms] if selfdual else [])
    l1 = set(pairs)
    cand = [p for p in itertools.combinations(range(n), 2) if p not in l1]
    seen, reps = set(), []
    for k in range(cap + 1):
        for M in itertools.combinations(cand, k):
            used = [v for p in M for v in p]
            if len(set(used)) != len(used):
                continue
            key = tuple(sorted(M))
            if key in seen:
                continue
            orbit = set()
            for g in group:
                orbit.add(tuple(sorted(tuple(sorted((g[x], g[y]))) for x, y in M)))
            seen |= orbit
            reps.append((list(key), len(orbit)))
    return pairs, reps


if __name__ == '__main__':
    n, a = int(sys.argv[1]), int(sys.argv[2])
    pairs, reps = classes(n, a)
    from collections import Counter
    print(json.dumps({'n': n, 'a': a, 'L1': pairs, 'self_dual_L1': {(n - 1 - j, n - 1 - i) for (i, j) in pairs} == set(pairs), 'classes': len(reps),
                      'by_size': dict(Counter(len(r) for r, _ in reps)),
                      'matchings_covered': sum(o for _, o in reps)}))
    if len(sys.argv) > 3:
        with open(sys.argv[3], 'w') as f:
            json.dump({'n': n, 'a': a, 'L1': pairs, 'reps': [r for r, _ in reps], 'orbit_sizes': [o for _, o in reps]}, f)
