"""All 3-layer prefixes of a sparse-start statement T3(n, a) at depth d (not only the exceptional ones):
L1 = a middle pairs, L2 over its symmetry classes, L3 every non-redundant layer of at most a comparators.
usage: N A DEPTH OUT.json"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, '..'), os.path.join(HERE, '..', 'sat14')]
import l2classes
import sentinel_prover as sp
from exceptional_children import tracks_good

n, a, d = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
L1, reps = l2classes.classes(n, a)
L1 = tuple(tuple(p) for p in L1)
X1 = sp.outputs(n, (L1,))
out, exc = [], []
for L2, _ in reps:
    L2 = tuple(tuple(p) for p in L2)
    X2 = frozenset(sp.apply_layer(L2, x) for x in X1)
    nonred = [(i, j) for i in range(n) for j in range(i + 1, n) if any((x >> i) & 1 and not (x >> j) & 1 for x in X2)]
    allL = [()]

    def gen(start, used, cur):
        if len(cur) == a:
            return
        for idx in range(start, len(nonred)):
            i, j = nonred[idx]
            if used >> i & 1 or used >> j & 1:
                continue
            cur.append((i, j))
            allL.append(tuple(cur))
            gen(idx + 1, used | (1 << i) | (1 << j), cur)
            cur.pop()
    gen(0, 0, [])
    for L3 in allL:
        P = [list(map(list, L1)), list(map(list, L2)), list(map(list, L3))]
        out.append(P)
        exc.append(not tracks_good(n, a, L1, L2, L3))
json.dump({'n': n, 'a': a, 'depth': d, 'all': out, 'is_exceptional': exc}, open(sys.argv[4], 'w'))
print(f'T3({n},{a}) depth {d}: {len(reps)} L2 classes, {len(out)} prefixes, {sum(exc)} exceptional')
