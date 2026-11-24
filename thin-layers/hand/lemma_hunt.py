"""Which small statements would close the leftover exceptional prefixes of a level (hand/exc_*.json)?

For every leftover prefix (3 layers, f = depth - 3 free layers) and every set of up to KMAX
infinities, the residual on r reals has a schedule of its real comparisons: in its own layers
(as-is, 3 layers), as early or as late as possible (height h).  A statement "no r-channel sorter of
depth D(r) whose first layers have at most (c1, c2, ...) comparators" (caps; later layers free)
closes the prefix if some schedule s with len(s) + f <= D(r) fits the caps.  Counts, for every cap
vector, how many prefixes it would close; prints the best ones (to test by SAT next).
usage: EXC.json KMAX [TOP]"""
import collections, itertools, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, '..')]
import sentinel_prover as sp
from sprove import asis_sizes

D = {3: 3, 4: 3, 5: 5, 6: 5, 7: 6, 8: 6}
d = json.load(open(sys.argv[1]))
KMAX = int(sys.argv[2])
TOP = int(sys.argv[3]) if len(sys.argv) > 3 else 25
n, f = d['n'], d['depth'] - 3
print(f'{len(d["left"])} leftover prefixes of E3({n},{d["a"]}) at depth {d["depth"]}')
# aggregate: for each candidate (r, caps), the number of prefixes with some profile <= caps
cands = collections.defaultdict(set)
for idx, P in enumerate(d['left']):
    layers = tuple(tuple(tuple(c) for c in L) for L in P)
    profs = set()
    for k in range(1, KMAX + 1):
        r = n - k
        if r not in D:
            continue
        for ch in itertools.combinations(range(n), k):
            for sg in itertools.product('+-', repeat=k):
                S = dict(zip(ch, sg))
                _, R, h, asap, alap = sp.residual2(n, layers, S)
                for s in {tuple(asap), tuple(alap), tuple(asis_sizes(n, layers, S))}:
                    if len(s) + f <= D[r]:
                        profs.add((r, tuple(list(s) + [r // 2] * (D[r] - len(s)))))
    for r, prof in profs:
        for m in (1, 2, 3):
            # every cap vector at least prof[:m], capped at r // 2 - 1 (a full first layer is no restriction)
            ranges = [range(prof[i], r // 2) for i in range(m)]
            for caps in itertools.product(*ranges):
                cands[(r, caps)].add(idx)
best = sorted(cands.items(), key=lambda kv: (-len(kv[1]), sum(kv[0][1]), kv[0]))
seen = set()
shown = 0
for (r, caps), idxs in best:
    key = frozenset(idxs)
    print(f'  r={r} depth {D[r]} caps {caps}: closes {len(idxs)}')
    shown += 1
    if shown >= TOP:
        break
