"""Try every S14 case root with a time limit: which cases close without a root split?
Worker w of W takes cases w, w + W, ...; facts are shared through the store. usage: STORE W w LIMIT"""
import os, signal, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import sprove, ss_cases
import sentinel_prover as sp
from sprove import inv_hash
path, W, w, LIMIT = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
L1, cs = ss_cases.cases(14, 5)
n, t = 14, 7
caps = sp.norm_caps(n, t, (5,))
log = lambda s: print(time.strftime('%H:%M:%S'), s[:300], flush=True)
S = sprove.Store(path, compact=True, x_cap=40000)
log(f'worker {w}/{W}: store {S.loaded} facts')


class Out(Exception):
    pass


def alarm(*a):
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
                      guide_big_n=12, guide_big_seconds=2.0, absorb_max_n=12)
    t0 = time.time()
    signal.alarm(LIMIT)
    try:
        res, fid = P.ext(n, (L1, L2), t, Y, caps)
        rule = S.facts[fid].get('step', {}).get('rule') if fid in S.facts else None
    except Out:
        res, rule = 'OPEN', None
    signal.alarm(0)
    log(f'case {i}: {res} by {rule} ({time.time() - t0:.1f}s) |L2|={len(L2)} |X|={len(Y)} nodes {P.stats["nodes"]}')
log('worker done')
