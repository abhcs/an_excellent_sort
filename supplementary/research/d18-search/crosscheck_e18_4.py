"""Independent check of 'e18_4 has no depth-10 completion' with depth-hand-proofs/verify/satnet.py
(exact encoding, full equivalences, no windows or end-game constraints except: last layer adjacent)."""
import sys, time
sys.path.insert(0, '/Users/abhishek/Documents/an_excellent_sort/depth-hand-proofs/verify')
sys.path.insert(0, '/Users/abhishek/Documents/an_excellent_sort/d18-search')
from satnet import Encoding, adjacent_pairs
from netsat import named_prefix
from pysat.solvers import Solver
n, P = named_prefix('e18_4')
d = 10 - len(P)
t = time.time()
enc = Encoding(n, d, prefix=P, allowed=[None] * (d - 1) + [adjacent_pairs(n)])
print(f'inputs={len(enc.inputs)} vars={enc.nvars} clauses={len(enc.clauses)} built in {time.time()-t:.0f}s', flush=True)
with Solver(name=sys.argv[1] if len(sys.argv) > 1 else 'kissat404', bootstrap_with=enc.clauses) as s:
    ok = s.solve()
    print('SAT' if ok else 'UNSAT', f'after {time.time()-t:.0f}s', flush=True)
    if ok:
        print(enc.network(s.get_model()))
