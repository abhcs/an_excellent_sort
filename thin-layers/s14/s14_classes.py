"""Residual classes of S14 root children: for sampled children (nodes after a canonical third layer)
list the prover's first K sentinel candidates (its own order: residual height, then more sentinels),
key each residual by (channels, invariant hash), and look each key up in the store.
usage: s14_classes.py STORE CASES(comma) SAMPLE K OUT.json"""
import collections, itertools, json, os, random, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import sprove, ss_cases
import sentinel_prover as sp
from sprove import sentinel_state, inv_hash

path, which, SAMPLE, K, out = sys.argv[1], [int(v) for v in sys.argv[2].split(',')], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
log = lambda s: print(time.strftime('%H:%M:%S'), s, flush=True)
L1, cs = ss_cases.cases(14, 5)
St = sprove.Store(path, compact=True, x_cap=40000)
P = sprove.Prover(St)
n, t = 14, 6
log(f'store {St.loaded} facts')


def candidates(layers):
    """The prover's leaf test and candidate list for EXT(14, layers, 6) (as in sprove.Prover._ext)."""
    Lp, total = len(layers), sum(len(L) for L in layers)
    single = []
    for c in range(n):
        for sg in '+-':
            pos, hit = c, 0
            for L in layers:
                for i, j in L:
                    if pos == i or pos == j:
                        hit += 1
                        pos = j if sg == '+' else i
                        break
            single.append((hit, c, sg))
    pool = [(c, sg) for hit, c, sg in single if hit == Lp]
    if len({c for c, _ in pool}) < P.kmax:
        pool = [(c, sg) for hit, c, sg in single if hit >= Lp - 1]
    cands = []
    for k in range(1, min(P.kmax, n - 2) + 1):
        r = n - k
        capsr = sp.norm_caps(r, t, ())
        rec_ok = bool(capsr) or t < sp.DUP.get(r, 99)
        hmax = P.dlow[r] - t - 1 if r in P.dlow else -1
        quick_ok = hmax >= 0 and total - k * Lp <= hmax * (r // 2)
        lems = [lm for lm in P.lemmas.get(r, ()) if lm[0] - t >= 1]
        full = quick_ok or bool(lems)
        if not (rec_ok or full):
            continue
        combos = ((tuple(zip(ch, sg)) for ch in itertools.combinations(range(n), k)
                   for sg in itertools.product('+-', repeat=k)) if full else itertools.combinations(pool, k))
        for combo in combos:
            if len({c for c, _ in combo}) < k:
                continue
            S = dict(combo)
            content, chlvl, asap, h = sentinel_state(n, layers, S)
            if quick_ok and h <= hmax:
                return 'quick', []
            alap = None
            for d2, a2, m2, lfid in lems:
                if h + t > d2:
                    continue
                for name in ('asap', 'alap'):
                    if name == 'alap' and alap is None:
                        alap = sp.residual2(n, layers, S)[4]
                    prof = asap if name == 'asap' else alap
                    sizes = [prof[i] if i < h else (capsr[i - h] if i - h < len(capsr) else r // 2) for i in range(m2)]
                    if all(x <= a2 for x in sizes):
                        return 'lemma', []
            if rec_ok:
                cands.append((h, k, S))
    cands.sort(key=lambda c: (c[0], -c[1]))
    return None, cands


keys = {}              # key -> [r, X (sorted list), status]
result = {}
for i in which:
    L2, X = cs[i]
    nonred = sp._fc.nonredundant(n, X)
    auts = [g for g in sp._fc.automorphisms(X, n, maxg=500)[0] if g != (tuple(range(n)), False)]
    allL = sp._fc.canonical_layers(n, nonred, 5, auts)
    rng = random.Random(7 + i)
    sample = allL if SAMPLE >= len(allL) else rng.sample(allL, SAMPLE)
    rows = []
    t0 = time.time()
    for idx, L3 in enumerate(sample):
        layers = (L1, L2, L3)
        leaf, cands = candidates(layers)
        if leaf:
            rows.append({'L3': L3, 'leaf': leaf, 'keys': [], 'hk': []})
            continue
        ks, hk = [], []
        for h, k, S in cands[:K]:
            r = n - k
            R = sp.residual2(n, layers, S)[1]
            XR = sp.outputs(r, R)
            if all(sp.is_sorted(x, r) for x in XR):
                continue
            key = f'{r}:{inv_hash(XR, r)}'
            if key not in keys:
                keys[key] = [r, XR, None]
            if key not in ks:
                ks.append(key)
                hk.append((h, k))
        rows.append({'L3': L3, 'leaf': None, 'keys': ks, 'hk': hk})
        if idx % 250 == 0:
            log(f'case {i}: {idx}/{len(sample)} children, {len(keys)} keys so far ({time.time() - t0:.0f}s)')
    result[i] = rows
    log(f'case {i}: {len(sample)} of {len(allL)} children done, {len(keys)} keys ({time.time() - t0:.0f}s)')
# store status of each key (the prover's store-first test: an equivalent class with a NO fact, t' >= 6)
t0 = time.time()
for key, v in keys.items():
    r, XR, _ = v
    ih = key.split(':')[1]
    cls = St.find_class(r, XR, ih)
    hit = St.lookup(cls, r, t, sp.norm_caps(r, t, ())) if cls is not None else None
    v[2] = hit[0] if hit else ('known class' if cls is not None else None)
log(f'store lookups for {len(keys)} keys ({time.time() - t0:.0f}s)')
json.dump({'cases': {str(i): [{'L3': [list(c) for c in row['L3']], 'leaf': row['leaf'], 'keys': row['keys'],
                               'hk': row['hk']} for row in rows] for i, rows in result.items()},
           'keys': {k: [v[0], v[2]] for k, v in keys.items()}}, open(out, 'w'))
for i, rows in result.items():
    st = collections.Counter()
    for row in rows:
        if row['leaf']:
            st['leaf (' + row['leaf'] + ')'] += 1
        elif any(keys[k][2] == 'NO' for k in row['keys']):
            st['a stored NO residual'] += 1
        elif not row['keys']:
            st['no candidates'] += 1
        else:
            st['none known'] += 1
    log(f'case {i}: {dict(st)}; min (h, k) of first candidate: '
        f'{collections.Counter(tuple(row["hk"][0]) for row in rows if row["hk"]).most_common(5)}')
log(f'key status: {collections.Counter(v[2] for v in keys.values())}')
