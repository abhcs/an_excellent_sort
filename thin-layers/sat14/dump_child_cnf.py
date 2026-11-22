"""Write the full netsat CNF for one S14 root child (every unsorted output encoded) without solving.
usage: CASE K OUT.cnf"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, '..'), os.path.join(HERE, '..', '..', 'd18-search')]
import ss_cases
import sentinel_prover as sp
import netsat
from thinsat import RecModel
case, k, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
n = 14
L1, cs = ss_cases.cases(n, 5)
L2, X = cs[case]
nonred = sp._fc.nonredundant(n, X)
auts = [g for g in sp._fc.automorphisms(X, n, maxg=500)[0] if g != (tuple(range(n)), False)]
allL = sp._fc.canonical_layers(n, nonred, 5, auts)
prefix = [list(L1), list(L2), list(allL[k])]
U = sorted(x for x in netsat.prefix_images(n, prefix) if not netsat.is_sorted(x, n))
M = RecModel(n, 6, U, solver='minisat22')
for x in U:
    M.add_input(x)
M.dump(out, [f'S14 case {case} child {k} prefix {prefix} full netsat encoding, 6 free layers'])
print(f'wrote {out}: {M.nv} vars, {len(M.rec)} clauses, {len(U)} inputs')
