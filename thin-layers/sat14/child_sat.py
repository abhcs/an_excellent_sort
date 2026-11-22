"""SAT for one S14 root child: does the prefix (L1, L2, L3) of case CASE, child K (the run's
canonical-layer index), extend to a 14-channel network of depth 9?  netsat's CEGAR model (end-game
constraints, window encoding). Prints netsat's log and a final RESULT line.
usage: CASE K [--solver S] [--cosat] [--init N] [--batch N] [--dump CNF]"""
import argparse, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, '..'), os.path.join(HERE, '..', '..', 'd18-search')]
import ss_cases
import sentinel_prover as sp
import netsat

ap = argparse.ArgumentParser()
ap.add_argument('case', type=int); ap.add_argument('k', type=int)
ap.add_argument('--solver', default='cadical195'); ap.add_argument('--cosat', action='store_true')
ap.add_argument('--init', type=int, default=300); ap.add_argument('--batch', type=int, default=30)
ap.add_argument('--depth', type=int, default=9); ap.add_argument('--full', action='store_true')
ap.add_argument('--n', type=int, default=14); ap.add_argument('--a', type=int, default=5)
a = ap.parse_args()
n = a.n
L1, cs = ss_cases.cases(n, a.a)
L2, X = cs[a.case]
nonred = sp._fc.nonredundant(n, X)
auts = [g for g in sp._fc.automorphisms(X, n, maxg=500)[0] if g != (tuple(range(n)), False)]
allL = sp._fc.canonical_layers(n, nonred, a.a, auts)
L3 = allL[a.k]
prefix = [list(L1), list(L2), list(L3)]
log = lambda s: print(time.strftime('%H:%M:%S'), s, flush=True)
log(f'SS({n},{a.depth},{a.a},3) case {a.case} child {a.k}: L3 = {list(L3)}')
t0 = time.time()
res = netsat.search(n, prefix, a.depth - 3, init=a.init, batch=a.batch, solver=a.solver, cosat=a.cosat, full=a.full, log=log)
verdict = 'UNSAT' if res is None else ('SAT' if isinstance(res, list) else str(res))
print(f'RESULT n {n} a {a.a} case {a.case} child {a.k} {verdict} {time.time() - t0:.1f}s solver {a.solver} cosat {a.cosat} full {a.full} init {a.init}', flush=True)
