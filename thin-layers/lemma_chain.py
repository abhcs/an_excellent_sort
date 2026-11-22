#!/usr/bin/env python3
"""lemma_chain.py OUT_PREFIX STATEMENT...: prove, in one memo, D(3..10) and then each statement in
order, every proved sparse-start statement becoming a lemma for the later ones.
A statement is 'SS:n,d,a,m' or 'D:n' (no n-channel sorter of depth DUP[n]-1).
Writes OUT_PREFIX.jsonl (proof DAG of everything) and OUT_PREFIX.dlow.json."""
import json, sys, time
import sentinel_prover as sp


def main():
    out = sys.argv[1]
    log = lambda s: print(time.strftime('%H:%M:%S'), s, flush=True)
    P = sp.Prover(kmax=4, log=log)
    roots = []
    for r in range(3, 11):
        L1 = (sp.first_layer(r),)
        if not P.ext(r, L1, sp.DUP[r] - 2):
            sp.DLOW[r] = sp.DUP[r]
            roots.append(P.key(r, sp.outputs(r, L1), sp.DUP[r] - 2, ()))
    log(f'D(r) proved for r <= 10')
    for st in sys.argv[2:]:
        kind, args = st.split(':')
        t0 = time.time()
        if kind == 'SS':
            n, d, a, m = map(int, args.split(','))
            L1 = (tuple((2 * k, 2 * k + 1) for k in range(a)),)
            caps = (a,) * (m - 1)
        else:
            n = int(args)
            d, L1, caps = sp.DUP[n] - 1, (sp.first_layer(n),), ()
        root = P.key(n, sp.outputs(n, L1), d - 1, sp.norm_caps(n, d - 1, caps))
        P.trace = root
        ok = P.ext(n, L1, d - 1, caps=caps)
        if ok:
            log(f'{st}: a sorter EXISTS ({time.time() - t0:.0f}s)')
            continue
        roots.append(root)
        if kind == 'SS':
            P.lemmas.setdefault(n, []).append((d, a, m, root))
        else:
            sp.DLOW[n] = sp.DUP[n]
        nodes, kinds = P.proof_dag(root)
        log(f'{st}: PROVED ({time.time() - t0:.0f}s), proof DAG {len(nodes)} nodes {kinds}; stats {P.stats}')
        P.export(roots, out + '.jsonl')
        json.dump({str(k): v for k, v in sp.DLOW.items()}, open(out + '.dlow.json', 'w'))


if __name__ == '__main__':
    main()
