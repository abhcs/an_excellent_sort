"""Try every case root of SS(n, d, a, 3) with a time limit: which cases close without a root split?
Worker w of W takes cases w, w + W, ...; facts are shared through the store.
usage: STORE N D A W w LIMIT"""
import os, signal, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
import sprove, ss_cases
import sentinel_prover as sp
from sprove import inv_hash
path, n, d, a, W, w, LIMIT = sys.argv[1], *map(int, sys.argv[2:8])
L1, cs = ss_cases.cases(n, a)
t = d - 2
caps = sp.norm_caps(n, t, (a,))
log = lambda s: print(time.strftime('%H:%M:%S'), s[:300], flush=True)
S = sprove.Store(path, compact=True, x_cap=40000)
log(f'SS({n},{d},{a},3) worker {w}/{W}: {len(cs)} cases; store {S.loaded} facts')


class Out(BaseException):
    pass


def alarm(*_):
    raise Out()


signal.signal(signal.SIGALRM, alarm)
for i in range(w, len(cs), W):
    L2, Y = cs[i]
    S.refresh()
    cls = S.find_class(n, Y, inv_hash(Y, n))
    hit = S.lookup(cls, n, t, caps) if cls is not None else None
    if hit and hit[0] == 'NO':
        log(f'case {i}: NO already stored |L2|={len(L2)}')
        continue
    P = sprove.Prover(S, oracle=True, guide=True, wide_sub=True, share_seconds=60, oracle_max_n=12,
                      guide_big_n=12, guide_big_seconds=2.0, absorb_max_n=12, store_first_n=13,
                      store_first_big=10 ** 6, guide_skip_n=13, guide_conflicts=10000)
    t0 = time.time()
    res = rule = None
    try:
        signal.alarm(LIMIT)
        try:
            res, fid = P.ext(n, (L1, L2), t, Y, caps)
            rule = S.facts[fid].get('step', {}).get('rule') if fid in S.facts else None
        finally:
            signal.alarm(0)
    except Out:
        res = 'OPEN'
    log(f'case {i}: {res} by {rule} ({time.time() - t0:.1f}s) |L2|={len(L2)} |X|={len(Y)} nodes {P.stats["nodes"]}')
log('worker done')
