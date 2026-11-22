"""Is there an n-channel sorting network of depth d whose first layer has only k comparators?
(SS(n, d, k, 1); any first layer of k comparators is (0,1),(2,3),... up to relabeling.)
netsat CEGAR. usage: N D K [--solver S]"""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, '..', '..', 'd18-search')]
import netsat
n, d, k = map(int, sys.argv[1:4])
solver = sys.argv[sys.argv.index('--solver') + 1] if '--solver' in sys.argv else 'cadical195'
prefix = [[(2 * i, 2 * i + 1) for i in range(k)]]
t0 = time.time()
res = netsat.search(n, prefix, d - 1, solver=solver, log=lambda s: None)
v = 'UNSAT (lemma true)' if res is None else ('network found (lemma false)' if isinstance(res, list) else str(res))
print(f'RESULT SS({n},{d},{k},1): {v} {time.time() - t0:.1f}s', flush=True)
if isinstance(res, list):
    print('NETWORK', res, flush=True)
