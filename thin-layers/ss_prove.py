#!/usr/bin/env python3
"""ss_prove.py n d a m [--kmax K] [--show]: decide SS(n,d,a,m) with the sentinel prover.

SS(n,d,a,m): no n-channel sorter of depth d has <= a comparators in each of its first m layers.
WLOG the first layer has exactly a comparators (adding comparators to layer 1 keeps a sorter) in
normal form (Fact A); layers 2..m are capped at a.  D(r) for r <= 10 is first proved by the same
procedure (bottom-up), so the quick sentinel rule only uses bounds proved here.
"""
import sys, time
import sentinel_prover as sp


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    n, d, a, m = map(int, args[:4])
    kmax = int(sys.argv[sys.argv.index('--kmax') + 1]) if '--kmax' in sys.argv else 3
    log = lambda s: print(time.strftime('%H:%M:%S'), s, flush=True)
    P = sp.Prover(kmax=kmax, log=log, oracle='--oracle' in sys.argv)
    for r in range(3, min(n, 10) + 1):
        if not P.ext(r, (sp.first_layer(r),), sp.DUP[r] - 2):
            sp.DLOW[r] = sp.DUP[r]
    log(f'D(r) proved for r <= {min(n, 10)}: {sp.DLOW}')
    L1 = (tuple((2 * k, 2 * k + 1) for k in range(a)),)
    caps = (a,) * (m - 1)
    t0 = time.time()
    before = dict(P.stats)
    P.trace = P.key(n, sp.outputs(n, L1), d - 1, sp.norm_caps(n, d - 1, caps))
    ok = P.ext(n, L1, d - 1, caps=caps)
    dt = time.time() - t0
    delta = {k: P.stats[k] - before[k] for k in P.stats}
    if ok:
        log(f'SS({n},{d},{a},{m}) is FALSE: a sorter exists ({dt:.1f}s) {delta}')
    else:
        root = P.key(n, sp.outputs(n, L1), d - 1, sp.norm_caps(n, d - 1, caps))
        P.lemmas.setdefault(n, []).append((d, a, m, root))
        nodes, kinds = P.proof_dag(root)
        log(f'SS({n},{d},{a},{m}) is TRUE ({dt:.1f}s): proof DAG {len(nodes)} nodes {kinds}; search {delta}')
        if '--show' in sys.argv:
            print(P.describe(root, limit=400))


if __name__ == '__main__':
    main()
