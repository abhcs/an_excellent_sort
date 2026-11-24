"""A random sample of the 3-layer prefixes of T3(n, a) (efficient-prefixes.md section 9): L1 = a middle
pairs, L2 over its symmetry classes, L3 a random non-redundant layer of at most a comparators.
Per L2 class: K layers with exactly a comparators and K2 with fewer.  Also counts all prefixes.
usage: N A DEPTH K K2 SEED OUT.json"""
import json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, '..'), os.path.join(HERE, '..', 'sat14')]
import l2classes
import sentinel_prover as sp
from exceptional_children import tracks_good

n, a, d, K, K2, seed = map(int, sys.argv[1:7])
rng = random.Random(seed)
L1, reps = l2classes.classes(n, a)
L1 = tuple(tuple(p) for p in L1)
X1 = sp.outputs(n, (L1,))
out, exc, total, total_full = [], [], 0, 0
for ci, (L2, _) in enumerate(reps):
    L2 = tuple(tuple(p) for p in L2)
    X2 = frozenset(sp.apply_layer(L2, x) for x in X1)
    nonred = [(i, j) for i in range(n) for j in range(i + 1, n) if any((x >> i) & 1 and not (x >> j) & 1 for x in X2)]
    full, small = [], [()]

    def gen(start, used, cur):
        if len(cur) == a:
            return
        for idx in range(start, len(nonred)):
            i, j = nonred[idx]
            if used >> i & 1 or used >> j & 1:
                continue
            cur.append((i, j))
            (full if len(cur) == a else small).append(tuple(cur))
            gen(idx + 1, used | (1 << i) | (1 << j), cur)
            cur.pop()
    gen(0, 0, [])
    total += len(full) + len(small); total_full += len(full)
    pick = rng.sample(full, min(K, len(full))) + rng.sample(small, min(K2, len(small)))
    for L3 in pick:
        out.append([list(map(list, L1)), list(map(list, L2)), list(map(list, L3))])
        exc.append(not tracks_good(n, a, L1, L2, L3))
    print(ci, len(full), len(small), flush=True) if ci % 20 == 0 else None
json.dump({'n': n, 'a': a, 'depth': d, 'all': out, 'is_exceptional': exc, 'total_prefixes': total,
           'total_full_L3': total_full}, open(sys.argv[7], 'w'))
print(f'T3({n},{a}) depth {d}: {len(reps)} L2 classes, {total} prefixes in all ({total_full} with a full L3); '
      f'sample {len(out)}, {sum(exc)} exceptional')
