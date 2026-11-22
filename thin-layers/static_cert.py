#!/usr/bin/env python3
"""static_cert.py -- the fixed-point (poset) certificate rule.

Inputs on which no prefix comparator swaps are exactly the linear extensions of the poset Q generated
by the prefix comparisons (i < j for each comparator (i, j)); the prefix fixes them, so the f free
layers alone must sort all of them.  Split the channels into a down-set D (values -inf), an up-set U
(+inf) and the rest A; every linear extension of Q|A then occurs, and the free layers restricted to A
must sort all linear extensions of Q|A.  When Q|A is a disjoint union of chains of sizes c_1..c_t,
the free layers form a merging network for those chains, and these hand bounds apply:
  * all chains of size 1 (an antichain of r elements): depth >= D(r);
  * any chains: an element in place i of a chain of size c can be the k-th smallest exactly for
    i <= k <= i + (N - c), N = sum c_i (choose how many elements of the other chains lie below it).
    So output k depends on that many elements, and its backward cone forces
    depth >= ceil(log2 max_k #{elements that can be the k-th smallest});
  * chain sizes (4,4,1), (4,3,2), (3,3,3): depth >= 5 (hand proofs h9_feedback_round2_merge432.md,
    h9_feedback_round3_merge333.md, d13_feedback_round3_merger441.md).
"""
import itertools, math

D = {1: 0, 2: 1, 3: 3, 4: 3, 5: 5, 6: 5, 7: 6, 8: 6, 9: 7, 10: 7}
MERGE5 = {(4, 4, 1), (4, 3, 2), (3, 3, 3)}


def closure(n, rels):
    less = [[False] * n for _ in range(n)]
    for i, j in rels:
        less[i][j] = True
    for k in range(n):
        for i in range(n):
            if less[i][k]:
                for j in range(n):
                    if less[k][j]:
                        less[i][j] = True
    return less


def merge_bound(chains):
    cs = tuple(sorted(chains, reverse=True))
    N = sum(cs)
    width = max(sum(1 for c in cs for i in range(1, c + 1) if i <= k <= i + N - c) for k in range(1, N + 1))
    b = math.ceil(math.log2(width)) if width > 1 else 0
    if all(c == 1 for c in cs):
        b = max(b, D.get(len(cs), 0))
    if cs in MERGE5:
        b = max(b, 5)
    return b


def chain_sizes(A, less):
    """If Q|A is a disjoint union of chains, return their sizes, else None."""
    A = list(A)
    comp = {a: a for a in A}

    def find(x):
        while comp[x] != x:
            comp[x] = comp[comp[x]]
            x = comp[x]
        return x
    for a, b in itertools.combinations(A, 2):
        if less[a][b] or less[b][a]:
            comp[find(a)] = find(b)
    groups = {}
    for a in A:
        groups.setdefault(find(a), []).append(a)
    sizes = []
    for g in groups.values():
        for a, b in itertools.combinations(g, 2):        # a chain: every pair comparable
            if not (less[a][b] or less[b][a]):
                return None
        sizes.append(len(g))
    return sizes


def static_certify(n, layers, f):
    rels = [c for L in layers for c in L]
    less = closure(n, rels)
    best = None
    for labels in itertools.product((0, 1, 2), repeat=n):      # 0 = D (-inf), 1 = A, 2 = U (+inf)
        ok = True
        for i in range(n):
            for j in range(n):
                if less[i][j] and labels[i] > labels[j] and not (labels[i] == 1 and labels[j] == 1):
                    ok = False
                    break
            if not ok:
                break
        if not ok:
            continue
        A = [i for i in range(n) if labels[i] == 1]
        if len(A) < 2:
            continue
        cs = chain_sizes(A, less)
        if cs is None:
            continue
        if merge_bound(cs) > f:
            return {'D': [i for i in range(n) if labels[i] == 0], 'A': A,
                    'U': [i for i in range(n) if labels[i] == 2], 'chains': sorted(cs, reverse=True),
                    'bound': merge_bound(cs)}
    return None


if __name__ == '__main__':
    import json, sys
    path, n, f = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    data = json.load(open(path))
    pref = data.get('uncertified_all') or data.get('uncertified_examples')
    stats = {}
    for P in pref:
        c = static_certify(n, P, f)
        key = 'none' if c is None else 'chains ' + ','.join(map(str, c['chains']))
        stats[key] = stats.get(key, 0) + 1
    print(json.dumps({'file': path, 'prefixes': len(pref), 'static_rule': stats}))
