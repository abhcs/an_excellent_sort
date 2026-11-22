"""Prove one S14 case with the compiled core, logging each closed child of the case's root split."""
import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import sprove, ss_cases
import sentinel_prover as sp
path, i = sys.argv[1], int(sys.argv[2])
L1, cs = ss_cases.cases(14, 5)
log = lambda s: print(time.strftime('%H:%M:%S'), s[:300], flush=True)
S = sprove.Store(path, compact=True, x_cap=40000)
P = sprove.Prover(S, oracle=True, guide=True, wide_sub=True, qcover_max_n=int(os.environ.get("QMAX", "99")), oracle_max_n=12,
                  guide_big_n=12, guide_big_seconds=2.0, log=log)
L2, Y = cs[i]
P.trace = (14, (L1, L2))
log(f'case {i}: |X|={len(Y)} layer {list(L2)}; store {S.loaded} facts')
t0 = time.time()
res, fid = P.ext(14, (L1, L2), 7, Y, sp.norm_caps(14, 7, (5,)))
log(f'case {i}: {res} ({time.time() - t0:.0f}s) fact {fid} {P.stats}')
