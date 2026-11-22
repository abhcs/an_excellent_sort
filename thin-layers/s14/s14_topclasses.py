"""Prove the residual classes that cover most open S14 root children (greedy order from s14_classes.json).
Worker w of W takes classes w, w + W, ... among the first TOP; each is SAT-checked, then proved with a time limit.
Based on: Residual classes of S14 root children: for sampled children (nodes after a canonical third layer)
list the prover's first K sentinel candidates (its own order: residual height, then more sentinels),
key each residual by (channels, invariant hash), and look each key up in the store.
usage: s14_classes.py STORE CASES(comma) SAMPLE K OUT.json"""
import collections, itertools, json, os, random, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import sprove, ss_cases
import sentinel_prover as sp
from sprove import sentinel_state, inv_hash

path, W, w, TOP, LIMIT = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
log = lambda s: print(time.strftime('%H:%M:%S'), s, flush=True)
L1, cs = ss_cases.cases(14, 5)
St = sprove.Store(path, compact=True, x_cap=40000)
P = sprove.Prover(St, oracle=True, guide=True, wide_sub=True, oracle_max_n=12, guide_big_n=12,
                  guide_big_seconds=2.0, absorb_max_n=12)
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



import signal
d = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 's14_classes.json')))
keys = d['keys']
open_rows = []
for case, rows in d['cases'].items():
    for row in rows:
        if row['leaf'] or any(keys[k][1] == 'NO' for k in row['keys']):
            continue
        open_rows.append((int(case), row))
cand = [[k for k in row['keys'] if keys[k][1] != 'YES'] for _, row in open_rows]
unc = set(range(len(cand)))
inv = collections.defaultdict(set)
for i, ks in enumerate(cand):
    for k in ks:
        inv[k].add(i)
chosen = []
while unc and len(chosen) < TOP:
    best = max(inv, key=lambda k: len(inv[k] & unc))
    g = inv[best] & unc
    if not g:
        break
    chosen.append((best, len(g), min(g)))
    unc -= g


class Out(Exception):
    pass


def alarm(*a):
    raise Out()


signal.signal(signal.SIGALRM, alarm)
for j, (key, gain, row_i) in enumerate(chosen):
    if j % W != w:
        continue
    case, row = open_rows[row_i]
    L2, X = cs[case]
    L3 = tuple(tuple(c) for c in row['L3'])
    layers = (L1, L2, L3)
    leaf, cands_ = candidates(layers)
    rep = None
    for h, k, S in cands_[:300]:
        r = n - k
        R = sp.residual2(n, layers, S)[1]
        XR = sp.outputs(r, R)
        if f'{r}:{inv_hash(XR, r)}' == key:
            rep = (r, R, XR, S, h)
            break
    if rep is None:
        log(f'class {j} {key}: representative not found')
        continue
    r, R, XR, S, h = rep
    t0 = time.time()
    v = sp.sat_oracle(r, R, t, (), seconds=120)
    sat = 'YES' if isinstance(v, list) else ('NO' if v is None else 'UNKNOWN')
    log(f'class {j} {key} (covers {gain} open children): r={r} h={h} sentinels {S} |X|={len(XR)} '
        f'prefix {[list(L) for L in R]}; SAT {sat} ({time.time() - t0:.0f}s)')
    if sat == 'YES':
        continue
    f0, t0 = len(St.facts), time.time()
    P.stats = collections.Counter(P.stats) if not isinstance(P.stats, collections.Counter) else P.stats
    n0 = P.stats['nodes']
    signal.alarm(LIMIT)
    try:
        res, fid = P.ext(r, tuple(tuple(map(tuple, L)) for L in R), t, XR, ())
    except Out:
        res, fid = 'OPEN', None
    signal.alarm(0)
    log(f'class {j}: {res} ({time.time() - t0:.0f}s) fact {fid} new facts {len(St.facts) - f0} '
        f'nodes {P.stats["nodes"] - n0}')
log('worker done')
