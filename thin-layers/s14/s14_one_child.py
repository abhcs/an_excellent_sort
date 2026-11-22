"""Prove one given child of an S14 case root (third layer given as JSON) with a time limit."""
import json, os, signal, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import sprove, ss_cases
import sentinel_prover as sp
path, i, layer, LIMIT = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
L1, cs = ss_cases.cases(14, 5)
L2, X = cs[i]
n = 14
L3 = tuple(tuple(c) for c in json.loads(layer.replace('(', '[').replace(')', ']')))
Y = sp._fc.apply_layer(n, X, L3)
log = lambda s: print(time.strftime('%H:%M:%S'), s[:300], flush=True)
S = sprove.Store(path, compact=True, x_cap=40000)
P = sprove.Prover(S, oracle=True, guide=True, wide_sub=True, oracle_max_n=12, guide_big_n=12,
                  guide_big_seconds=2.0, absorb_max_n=12, log=log)
P.trace = (n, (L1, L2, L3))


class Out(Exception):
    pass


def alarm(*a):
    raise Out()


signal.signal(signal.SIGALRM, alarm)
f0, t0 = len(S.facts), time.time()
signal.alarm(LIMIT)
try:
    res, fid = P.ext(n, (L1, L2, L3), 6, Y, ())
    rule = S.facts[fid].get('step', {}).get('rule') if fid in S.facts else None
except Out:
    res, fid, rule = 'OPEN', None, None
signal.alarm(0)
log(f'case {i} layer {list(L3)} |X|={len(Y)}: {res} by {rule} ({time.time() - t0:.0f}s) fact {fid} '
    f'new facts {len(S.facts) - f0} {P.stats}')
