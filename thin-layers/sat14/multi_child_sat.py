"""One SAT instance for several root children of an S14 case: the case prefix (L1, L2), seven free
layers, the first of them (layer 3) forced by selector variables to be one of the children's third
layers; every output of the case prefix is encoded (netsat's model, full).  UNSAT refutes all those
children at once, and what the solver learns about layers 4-9 serves every child.
usage: CASE K1 K2 ... [--solver S] [--dump CNF]"""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, '..'), os.path.join(HERE, '..', '..', 'd18-search')]
import ss_cases
import sentinel_prover as sp
import netsat
from thinsat import RecModel

args = sys.argv[1:]
solver = 'cadical195'
dump = None
if '--solver' in args:
    i = args.index('--solver'); solver = args[i + 1]; del args[i:i + 2]
if '--dump' in args:
    i = args.index('--dump'); dump = args[i + 1]; del args[i:i + 2]
case, ks = int(args[0]), [int(k) for k in args[1:]]
n = 14
L1, cs = ss_cases.cases(n, 5)
L2, X = cs[case]
nonred = sp._fc.nonredundant(n, X)
auts = [g for g in sp._fc.automorphisms(X, n, maxg=500)[0] if g != (tuple(range(n)), False)]
allL = sp._fc.canonical_layers(n, nonred, 5, auts)
t0 = time.time()
U = sorted(x for x in X if not netsat.is_sorted(x, n))
M = (RecModel if dump else netsat.Model)(n, 7, U, solver=solver)
sels = []
for k in ks:
    L3 = set(allL[k])
    s = M.new_var()
    sels.append(s)
    for p, v in M.g[0].items():
        M.add([-s, v] if p in L3 else [-s, -v])
    if any(p not in M.g[0] for p in L3):
        M.add([-s])
M.add(sels)
for x in U:
    M.add_input(x)
t1 = time.time()
ok = M.S.solve()
verdict = 'UNSAT' if not ok else 'SAT'
extra = ''
if ok:
    net = M.network(M.S.get_model())
    k3 = next(k for k, s in zip(ks, sels) if s in set(M.S.get_model()))
    full = [list(L1), list(L2)] + net
    extra = f' child {k3} completes: verified {netsat.verify_all(n, full)}'
if dump and not ok:
    M.dump(dump, [f'multi_child case {case} children {ks}'])
print(f'RESULT case {case} {len(ks)} children {verdict} {time.time() - t0:.1f}s (build {t1 - t0:.1f}s, '
      f'vars {M.nv}, clauses {M.ncl}, solver {solver}){extra}', flush=True)
