"""Exceptional prefixes at the D(11) level, normalized: no comparator of layers 2-3 that never fires.
For (n, a) in {(8, 2), (9, 3)} at depth 7: L1 = a middle pairs, L2 over its symmetry classes, L3 every
non-redundant layer of at most a comparators; keep the exceptional ones (no first-layer sentinel has
a good track, README §4.1) and try the hand certificates (prefix_cert.certify, static_cert).
usage: N A [OUT.json]"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, '..'), os.path.join(HERE, '..', 'sat14')]
import l2classes
import sentinel_prover as sp
from exceptional_children import tracks_good
from prefix_cert import certify
from static_cert import static_certify

n, a = int(sys.argv[1]), int(sys.argv[2])
d = 7
L1, reps = l2classes.classes(n, a)
L1 = tuple(tuple(p) for p in L1)
X1 = sp.outputs(n, (L1,))
t0 = time.time()
exc, cert = [], {}
for L2, _ in reps:
    L2 = tuple(tuple(p) for p in L2)
    X2 = frozenset(sp.apply_layer(L2, x) for x in X1)
    nonred = [(i, j) for i in range(n) for j in range(i + 1, n) if any((x >> i) & 1 and not (x >> j) & 1 for x in X2)]
    allL = []

    def gen(start, used, cur):
        if cur:
            allL.append(tuple(cur))
        if len(cur) == a:
            return
        for idx in range(start, len(nonred)):
            i, j = nonred[idx]
            if used >> i & 1 or used >> j & 1:
                continue
            cur.append((i, j))
            gen(idx + 1, used | (1 << i) | (1 << j), cur)
            cur.pop()
    gen(0, 0, [])
    for L3 in allL:
        if tracks_good(n, a, L1, L2, L3):
            continue
        P = (L1, L2, L3)
        exc.append(P)
        c = certify(n, d, a, 3, [list(L) for L in P])
        if c is None:
            c = static_certify(n, [list(L) for L in P], d - 3)
        cert[P] = c
left = [P for P in exc if cert[P] is None]
from collections import Counter
rules = Counter((c[0] if isinstance(c, tuple) else str(c)[:30]) if c else 'none' for c in cert.values())
print(f'E3({n},{a}) depth {d}: {len(reps)} L2 classes; {len(exc)} non-redundant exceptional prefixes; '
      f'certified {len(exc) - len(left)} {dict(rules)}; left {len(left)} ({time.time() - t0:.0f}s)')
for P in left[:12]:
    print('  ', [list(map(list, L)) for L in P])
if len(sys.argv) > 3:
    json.dump({'n': n, 'a': a, 'depth': d, 'exceptional': [[list(map(list, L)) for L in P] for P in exc],
               'left': [[list(map(list, L)) for L in P] for P in left]}, open(sys.argv[3], 'w'))
