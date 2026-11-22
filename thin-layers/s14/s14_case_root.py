"""Assemble the root fact of one S14 case after s14_case_run.py proved its children (README §8.12).

The root split also needs the child with an empty third layer (the root's output set with 6 layers
left); it is proved first, with the runner's prover. The root is then split without trying sentinel
residuals at the root itself (max_rec=0, no guide): the survey showed the root dives into a costly
residual, while every child of the split is already a store hit. usage: STORE CASE"""
import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import sprove, ss_cases
import sentinel_prover as sp

path, i = sys.argv[1], int(sys.argv[2])
n, t = 14, 7
L1, cs = ss_cases.cases(n, 5)
L2, X = cs[i]
caps = sp.norm_caps(n, t, (5,))
log = lambda s: print(time.strftime('%m-%d %H:%M:%S'), s[:400], flush=True)
S = sprove.Store(path, compact=True, x_cap=40000)
log(f'case {i}: |L2|={len(L2)} |X|={len(X)}; store {S.loaded} facts')
# every canonical child must already be proved: the root split below tries no sentinels
nonred = sp._fc.nonredundant(n, X)
auts = [g for g in sp._fc.automorphisms(X, n, maxg=500)[0] if g != (tuple(range(n)), False)]
missing = []
for L3 in sp._fc.canonical_layers(n, nonred, 5, auts):
    Y = sp._fc.apply_layer(n, X, L3)
    cls = S.find_class(n, Y, sprove.inv_hash(Y, n))
    hit = S.lookup(cls, n, t - 1, sp.norm_caps(n, t - 1, ())) if cls is not None else None
    if not (hit and hit[0] == 'NO'):
        missing.append(L3)
log(f'children not yet proved: {len(missing)} {[list(L) for L in missing[:5]]}')
if missing:
    sys.exit(1)
P = sprove.Prover(S, oracle=True, guide=True, wide_sub=True, oracle_max_n=12, guide_big_n=12,
                  guide_big_seconds=2.0, absorb_max_n=12)
t0 = time.time()
res, fid = P.ext(n, (L1, L2), t - 1, X, ())
log(f'empty third layer: {res} fact {fid} ({time.time() - t0:.0f}s) nodes {P.stats["nodes"]}')
if res != 'NO':
    sys.exit(1)
R = sprove.Prover(S, oracle=False, guide=False, wide_sub=True, max_rec=0, absorb_max_n=12)
t0 = time.time()
res, fid = R.ext(n, (L1, L2), t, X, caps)
step = S.facts[fid].get('step', {}) if fid in S.facts else {}
log(f'case {i} root: {res} fact {fid} ({time.time() - t0:.0f}s) rule {step.get("rule")} '
    f'children {len(step.get("children", []))} qcovers {len(step.get("qcovers", []))} '
    f'automorphisms {len(step.get("aut", []))} {R.stats}')
sys.exit(0 if res == 'NO' else 1)
