"""Prove every root child of one S14 case in passes with growing time caps (README §8.12).

Workers go through the canonical children (third layers) in a fixed random order and claim each
child with a file, so faster cores take more children. Facts are shared through the store (refresh
every 60 s). Pass p gives each child CAP seconds; a child still open is tried again in the next pass,
when the store holds more facts, and children proved earlier are store hits. A random order makes
the progress of a pass an unbiased sample of the case.

Logs one line per child: HIT (already proved), NO (proved now), OPEN (cap reached) or YES.
usage: STORE CASE PASS CAP w [OPTS]   (CAP 0: no time limit; OPTS: JSON of extra prover options,
e.g. {"store_first_n": 13, "store_first_big": 100000, "guide_skip_n": 13, "guide_conflicts": 10000})"""
import json, os, random, signal, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import sprove, ss_cases
import sentinel_prover as sp

path, i, p, CAP, w = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
opts = json.loads(sys.argv[6]) if len(sys.argv) > 6 else {}
n = 14
L1, cs = ss_cases.cases(n, 5)
L2, X = cs[i]
nonred = sp._fc.nonredundant(n, X)
auts = [g for g in sp._fc.automorphisms(X, n, maxg=500)[0] if g != (tuple(range(n)), False)]
allL = sp._fc.canonical_layers(n, nonred, 5, auts)
order = list(range(len(allL)))
random.Random(i).shuffle(order)
claims = os.path.join(path, 'claims', f'case{i}-pass{p}')
os.makedirs(claims, exist_ok=True)
log = lambda s: print(time.strftime('%m-%d %H:%M:%S'), s[:300], flush=True)
S = sprove.Store(path, compact=True, x_cap=40000)
P = sprove.Prover(S, oracle=True, guide=True, wide_sub=True, share_seconds=60, oracle_max_n=12,
                  guide_big_n=12, guide_big_seconds=2.0, absorb_max_n=12, **opts)


class Out(BaseException):          # not an Exception: no handler inside the prover may swallow it
    pass


def alarm(*a):
    raise Out()


signal.signal(signal.SIGALRM, alarm)
log(f'case {i} pass {p} worker {w}: {len(allL)} children, cap {CAP}s; store {S.loaded} facts; options {opts}')
T0 = time.time()
for k in order:
    try:
        os.close(os.open(os.path.join(claims, str(k)), os.O_CREAT | os.O_EXCL | os.O_WRONLY))
    except FileExistsError:
        continue
    L3 = allL[k]
    Y = sp._fc.apply_layer(n, X, L3)
    t0, n0, f0 = time.time(), P.stats['nodes'], len(S.facts)
    res = rule = None
    try:
        if CAP:
            signal.alarm(CAP)
        try:
            res, fid = P.ext(n, (L1, L2, L3), 6, Y, ())
            rule = S.facts[fid].get('step', {}).get('rule') if fid in S.facts else None
        finally:
            signal.alarm(0)
    except Out:
        pass
    nodes = P.stats['nodes'] - n0
    kind = 'OPEN' if res is None else ('HIT' if res == 'NO' and nodes == 0 else res)
    log(f'child {k}: {kind} by {rule} {time.time() - t0:.1f}s nodes {nodes} new facts {len(S.facts) - f0} '
        f'|X|={len(Y)} layer {list(L3)}')
    if kind == 'YES':
        log(f'!!! child {k} has a completion')
log(f'worker {w} pass {p} done ({time.time() - T0:.0f}s) {P.stats}')
