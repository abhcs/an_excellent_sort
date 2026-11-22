"""Sample children of an S14 case root (nodes after a random canonical third layer) and try each with
a time limit: how many close at once, how many within the limit, and at what cost."""
import collections, os, random, signal, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import sprove, ss_cases
import sentinel_prover as sp
path, i, K, LIMIT = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
L1, cs = ss_cases.cases(14, 5)
L2, X = cs[i]
n = 14
nonred = sp._fc.nonredundant(n, X)
auts = [g for g in sp._fc.automorphisms(X, n, maxg=500)[0] if g != (tuple(range(n)), False)]
allL = sp._fc.canonical_layers(n, nonred, 5, auts)
log = lambda s: print(time.strftime('%H:%M:%S'), s[:300], flush=True)
S = sprove.Store(path, compact=True, x_cap=40000)
log(f'case {i}: {len(allL)} canonical third layers; store {S.loaded} facts; {K} samples, {LIMIT}s each')


class Out(Exception):
    pass


def alarm(*a):
    raise Out()


signal.signal(signal.SIGALRM, alarm)
rng = random.Random(1000 + i)
tally = collections.Counter()
for k in range(K):
    L3 = rng.choice(allL)
    Y = sp._fc.apply_layer(n, X, L3)
    P = sprove.Prover(S, oracle=True, guide=True, wide_sub=True, oracle_max_n=12, guide_big_n=12,
                      guide_big_seconds=2.0, absorb_max_n=12)
    f0, t0 = len(S.facts), time.time()
    signal.alarm(LIMIT)
    try:
        res, fid = P.ext(n, (L1, L2, L3), 6, Y, ())
        rule = S.facts[fid].get('step', {}).get('rule') if fid in S.facts else None
    except Out:
        res, rule = 'OPEN', None
    signal.alarm(0)
    secs = time.time() - t0
    kind = res if res != 'NO' else ('NO at once' if P.stats['nodes'] <= 1 else 'NO')
    tally[kind] += 1
    log(f'{k}: {kind} by {rule} {secs:.1f}s nodes {P.stats["nodes"]} new facts {len(S.facts) - f0} '
        f'|X|={len(Y)} layer {list(L3)}')
log(f'case {i}: {dict(tally)}')
