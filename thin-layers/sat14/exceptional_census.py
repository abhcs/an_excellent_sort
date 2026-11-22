"""Census of exceptional root children over all cases of SS(n, 9, a, 3): per case, the canonical
children and how many are exceptional (no good sentinel track through layers 2-3).
usage: N A OUT.jsonl"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import ss_cases
import sentinel_prover as sp
from exceptional_children import tracks_good

n, a, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
L1, cs = ss_cases.cases(n, a)
t0 = time.time()
tot = exc_tot = 0
with open(out, 'w') as f:
    for case, (L2, X) in enumerate(cs):
        nonred = sp._fc.nonredundant(n, X)
        auts = [g for g in sp._fc.automorphisms(X, n, maxg=500)[0] if g != (tuple(range(n)), False)]
        allL = sp._fc.canonical_layers(n, nonred, a, auts)
        exc = [k for k, L3 in enumerate(allL) if not tracks_good(n, a, L1, L2, L3)]
        tot += len(allL)
        exc_tot += len(exc)
        f.write(json.dumps({'case': case, 'L2': [list(c) for c in L2], 'X': len(X), 'children': len(allL),
                            'exceptional': exc}) + '\n')
print(f'SS({n},9,{a},3): {len(cs)} cases, {tot} canonical children, {exc_tot} exceptional '
      f'({time.time() - t0:.0f}s)', flush=True)
