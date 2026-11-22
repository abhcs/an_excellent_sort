"""Prove the root children of one S14 case in parallel: worker w of W takes canonical children
w, w + W, ... in the root split's order (smallest output set first) and shares facts through the
store (refresh every 60 s). Logs one line per child. usage: STORE CASE W w"""
import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import sprove, ss_cases
import sentinel_prover as sp
path, i, W, w = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
L1, cs = ss_cases.cases(14, 5)
L2, X = cs[i]
n = 14
nonred = sp._fc.nonredundant(n, X)
auts = [g for g in sp._fc.automorphisms(X, n, maxg=500)[0] if g != (tuple(range(n)), False)]
allL = sp._fc.canonical_layers(n, nonred, 5, auts)
kids = sorted(((L, sp._fc.apply_layer(n, X, L)) for L in allL), key=lambda c: len(c[1]))
log = lambda s: print(time.strftime('%H:%M:%S'), s[:300], flush=True)
S = sprove.Store(path, compact=True, x_cap=40000)
P = sprove.Prover(S, oracle=True, guide=True, wide_sub=True, share_seconds=60, oracle_max_n=12,
                  guide_big_n=12, guide_big_seconds=2.0, absorb_max_n=12)
log(f'case {i} worker {w}/{W}: {len(kids)} children; store {S.loaded} facts')
T0 = time.time()
for k in range(w, len(kids), W):
    L3, Y = kids[k]
    t0, n0, f0 = time.time(), P.stats['nodes'], len(S.facts)
    res, fid = P.ext(n, (L1, L2, L3), 6, Y, ())
    rule = S.facts[fid].get('step', {}).get('rule') if fid in S.facts else None
    log(f'child {k}: {res} by {rule} {time.time() - t0:.1f}s nodes {P.stats["nodes"] - n0} '
        f'new facts {len(S.facts) - f0} |X|={len(Y)} layer {list(L3)}')
log(f'worker {w} done ({time.time() - T0:.0f}s) {P.stats}')
