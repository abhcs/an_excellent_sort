"""Time the compiled sentinel covers on S14 nodes: a case root (next cap 5) and a node after layer 3."""
import os, shutil, sys, tempfile, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import sprove, ss_cases
import sentinel_prover as sp
tmp = tempfile.mkdtemp()
shutil.copy('facts_s14/statements.jsonl', tmp)
P = sprove.Prover(sprove.Store(tmp))
print('dlow', P.dlow, 'lemmas', {r: [(d, a, m) for d, a, m, _ in v] for r, v in P.lemmas.items()})
L1, cs = ss_cases.cases(14, 5)
for i in (0, 340):
    L2, X = cs[i]
    n = 14
    nonred = sp._fc.nonredundant(n, X)
    auts = [g for g in sp._fc.automorphisms(X, n, maxg=500)[0] if g != (tuple(range(n)), False)]
    allL = sp._fc.canonical_layers(n, nonred, 5, auts)
    t0 = time.time()
    qc, open_ = P._qcover(n, (L1, L2), 7, (5,), allL)
    print(f'case {i} root: {len(allL)} canonical layers ({len(auts)} automorphisms); covers {len(qc)} close '
          f'{len(allL) - len(open_)}, {len(open_)} open ({time.time() - t0:.1f}s)', flush=True)
    L3 = allL[len(allL) // 2]
    Y = sp._fc.apply_layer(n, X, L3)
    nonred = sp._fc.nonredundant(n, Y)
    auts = [g for g in sp._fc.automorphisms(Y, n, maxg=500)[0] if g != (tuple(range(n)), False)]
    allL = sp._fc.canonical_layers(n, nonred, 7, auts)
    t0 = time.time()
    qc, open_ = P._qcover(n, (L1, L2, L3), 6, (), allL)
    print(f'  after layer 3 {list(L3)}: |X|={len(Y)} {len(allL)} canonical layers ({len(auts)} automorphisms); '
          f'covers {len(qc)} close {len(allL) - len(open_)}, {len(open_)} open ({time.time() - t0:.1f}s)', flush=True)
shutil.rmtree(tmp)
