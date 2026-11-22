"""Close every root child of one S14 case that one sentinel step onto a stored residual closes, with
no other proving (README §8.13). The child's sentinel candidates are all looked up in the store
(store_first over every candidate); the guided search, which would start proving, is replaced by
an exception. Children closed this way get their fact; the others are listed, one index per line,
in OUT. Worker w of W takes children w, w + W, ... usage: STORE CASE W w OUT"""
import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import sprove, ss_cases
import sentinel_prover as sp

path, i, W, w, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
n = 14
L1, cs = ss_cases.cases(n, 5)
L2, X = cs[i]
nonred = sp._fc.nonredundant(n, X)
auts = [g for g in sp._fc.automorphisms(X, n, maxg=500)[0] if g != (tuple(range(n)), False)]
allL = sp._fc.canonical_layers(n, nonred, 5, auts)
S = sprove.Store(path, compact=True, x_cap=40000)


class NotAtOnce(Exception):
    pass


def stop(*a, **k):
    raise NotAtOnce()


tally = {'stored': 0, 'closed': 0, 'open': 0}
t0 = time.time()
with open(out, 'w') as f:
    for k in range(w, len(allL), W):
        Y = sp._fc.apply_layer(n, X, allL[k])
        P = sprove.Prover(S, oracle=False, guide=True, wide_sub=False, store_first_n=13, store_first_big=10 ** 6)
        P._guided = stop
        try:
            P.ext(n, (L1, L2, allL[k]), 6, Y, ())
            tally['stored' if P.stats['nodes'] == 0 else 'closed'] += 1
        except NotAtOnce:
            tally['open'] += 1
            f.write(f'{k}\n')
print(time.strftime('%m-%d %H:%M:%S'), f'case {i} worker {w}/{W}: {tally} ({time.time() - t0:.0f}s)', flush=True)
