"""All sentinel sets of a hard S14 root child, not only the prover's pool: for k = 1..KMAX sentinels,
the distinct residuals (up to equal output sets), their real comparisons and heights; then a SAT
verdict (netsat CEGAR via sentinel_prover.sat_oracle, glucose) for the sparsest residuals of each k.
usage: CASE K [KMAX] [PER_K] [SECONDS]"""
import collections, itertools, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, '..')]
import ss_cases
import sentinel_prover as sp

case, kc = int(sys.argv[1]), int(sys.argv[2])
KMAX = int(sys.argv[3]) if len(sys.argv) > 3 else 5
PER = int(sys.argv[4]) if len(sys.argv) > 4 else 6
SECS = float(sys.argv[5]) if len(sys.argv) > 5 else 30.0
n, t = 14, 6
L1, cs = ss_cases.cases(n, 5)
L2, X = cs[case]
nonred = sp._fc.nonredundant(n, X)
auts = [g for g in sp._fc.automorphisms(X, n, maxg=500)[0] if g != (tuple(range(n)), False)]
allL = sp._fc.canonical_layers(n, nonred, 5, auts)
L3 = allL[kc]
layers = (L1, L2, L3)
print(f'case {case} child {kc}: L3={list(L3)}', flush=True)
t0 = time.time()
for k in range(1, KMAX + 1):
    r = n - k
    seen = {}
    for ch in itertools.combinations(range(n), k):
        for sg in itertools.product('+-', repeat=k):
            S = dict(zip(ch, sg))
            rr, R, h, asap, alap = sp.residual2(n, layers, S)
            real = sum(len(L) for L in R)
            XR = sp._fc.outputs(r, R)
            key = (len(XR), hash(XR))
            if key not in seen or real < seen[key][0]:
                seen[key] = (real, h, S, R)
    hist = collections.Counter(v[0] for v in seen.values())
    best = sorted(seen.values(), key=lambda v: (v[0], v[1]))
    print(f'k={k} r={r}: {len(seen)} distinct residuals; real comparisons histogram {sorted(hist.items())[:8]} '
          f'({time.time() - t0:.0f}s)', flush=True)
    for real, h, S, R in best[:PER]:
        t1 = time.time()
        w = sp.sat_oracle(r, R, t, (), seconds=SECS, conflicts=20000)
        v = 'YES' if isinstance(w, list) else ('NO' if w is None else 'UNKNOWN')
        print(f'   real {real} h {h} sizes {[len(L) for L in R]} S {S}: {v} ({time.time() - t1:.1f}s)', flush=True)
