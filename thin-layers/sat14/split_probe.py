"""Split hard S14 root children on their fourth layer: canonical next layers, how many the compiled
sentinel covers close, and how many distinct grandchildren (up to equivalence) stay open.
usage: CASE K [K ...]"""
import os, shutil, sys, tempfile, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, '..')]
import sprove, ss_cases
import sentinel_prover as sp
case, ks = int(sys.argv[1]), [int(k) for k in sys.argv[2:]]
n = 14
L1, cs = ss_cases.cases(n, 5)
L2, X = cs[case]
nonred = sp._fc.nonredundant(n, X)
auts = [g for g in sp._fc.automorphisms(X, n, maxg=500)[0] if g != (tuple(range(n)), False)]
allL = sp._fc.canonical_layers(n, nonred, 5, auts)
tmp = tempfile.mkdtemp()
shutil.copy(os.path.join(HERE, '..', 'facts_s14', 'statements.jsonl'), tmp)
P = sprove.Prover(sprove.Store(tmp))
for k in ks:
    L3 = allL[k]
    Y = sp._fc.apply_layer(n, X, L3)
    t0 = time.time()
    nr = sp._fc.nonredundant(n, Y)
    au = [g for g in sp._fc.automorphisms(Y, n, maxg=500)[0] if g != (tuple(range(n)), False)]
    L4s = sp._fc.canonical_layers(n, nr, 7, au)
    t1 = time.time()
    qc, open_ = P._qcover(n, (L1, L2, L3), 6, (), L4s)
    t2 = time.time()
    keys = sp._fc.child_keys(n, Y, open_) if open_ else []
    groups = {}
    for L, kk in zip(open_, keys):
        groups.setdefault((kk[0], kk[3]), []).append(L)
    reps = 0
    for g in groups.values():
        seen = []
        for L in g:
            Z = sp._fc.apply_layer(n, Y, L)
            if not any(len(Z) == len(W) and sp._fc.equivalent(Z, W, n) is not None for W in seen):
                seen.append(Z)
        reps += len(seen)
    print(f'child {k} L3={list(L3)} |Y|={len(Y)} auts={len(au)}: {len(L4s)} canonical 4th layers ({t1 - t0:.1f}s); '
          f'covers {len(qc)} close {len(L4s) - len(open_)}, open {len(open_)} ({t2 - t1:.1f}s), '
          f'open classes {reps} ({time.time() - t2:.1f}s)', flush=True)
shutil.rmtree(tmp)
