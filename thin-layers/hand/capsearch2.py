"""Uniform capacities WITH PAIRWISE TERMS (efficient-prefixes.md section 7.7).

kappa(p) = k0[type p] + sum over the other prefix channels q of k1[type p, rel(p, q)], one global table,
the cover values still free per prefix.  rel(p, q) = (order: lt / gt / inc, overlap of shortest terms capped
at 2, overlap of shortest clauses capped at 2, shared inputs?).  Cutting planes exactly as capsearch.py.
usage: [RELMODE=full|coarse|coarse+] [PAIRDEP=1|0] capsearch2.py EXC.json KEY TYPE [reps|all] [rounds]
TYPE in ab, abs, abn, abns.  PAIRDEP=0: the pair term depends on the relation only, not on the type."""
import json, sys, time
from multiprocessing import Pool
sys.path[:0] = ['.']
import gainrules as gr
import capsearch as cs
import lp2
N = gr.N


def supp(t):
    s = 0
    for v in range(N):
        for x in range(1 << N):
            if not (x >> v) & 1 and ((t >> x) & 1) != ((t >> (x | 1 << v)) & 1):
                s |= 1 << v; break
    return s


def features(pre, kind):
    """per channel p: dict param -> coefficient of kappa(p)"""
    tabs = gr.channel_tables(pre)
    top = gr.Side(tabs); bot = gr.Side([gr.dual(t) for t in tabs])
    sp = [supp(t) for t in tabs]
    ab = [(top.a[p], bot.a[p]) for p in range(N)]
    nn = [(len(top.mins((p,))), len(bot.mins((p,)))) for p in range(N)]
    sym = kind.endswith('s')

    def ty(p):
        if kind.startswith('abn'):
            t, tc = (ab[p][0], ab[p][1], nn[p][0], nn[p][1]), (ab[p][1], ab[p][0], nn[p][1], nn[p][0])
        else:
            t, tc = ab[p], (ab[p][1], ab[p][0])
        return (min(t, tc), t > tc) if sym else (t, False)

    def rel(p, q):
        if gr.leq(tabs[p], tabs[q]):
            o = 'lt'
        elif gr.leq(tabs[q], tabs[p]):
            o = 'gt'
        else:
            o = 'inc'
        oT = min(2, max(gr.POP[T & U] for T in top.mins((p,)) for U in top.mins((q,))))
        oC = min(2, max(gr.POP[T & U] for T in bot.mins((p,)) for U in bot.mins((q,))))
        sh = int(bool(sp[p] & sp[q]))
        return (o, oT, oC, sh)

    out = []
    for p in range(N):
        t, flip = ty(p)
        f = {('k0', t): 1.0}
        for q in range(N):
            if q == p:
                continue
            r = rel(p, q)
            if flip:                       # complement: order reverses, terms <-> clauses
                r = ({'lt': 'gt', 'gt': 'lt', 'inc': 'inc'}[r[0]], r[2], r[1], r[3])
            if RELMODE == 'coarse':        # 7 kinds: none / shared inputs only / terms meet / clauses meet / both / lt / gt
                o, oT, oC, sh = r
                r = o if o != 'inc' else ('both' if oT and oC else 'T' if oT else 'C' if oC else 'share' if sh else 'none')
            if RELMODE == 'coarse+':       # coarse, overlap 2 kept apart
                o, oT, oC, sh = r
                r = o if o != 'inc' else (oT, oC) if (oT or oC) else ('share' if sh else 'none')
            if r == 'none' and NONEZERO:   # unrelated partners carry no term (baseline)
                continue
            k = ('k1', t, r) if PAIRDEP else ('k1', r)
            f[k] = f.get(k, 0.0) + 1.0
        out.append(f)
    return out


if __name__ == '__main__':
    d = json.load(open(sys.argv[1])); P = d[sys.argv[2]]; kind = sys.argv[3]
    import os
    RELMODE = os.environ.get('RELMODE', 'full'); PAIRDEP = os.environ.get('PAIRDEP', '1') == '1'
    NONEZERO = os.environ.get('NONEZERO', '1') == '1'
    MASTER = os.environ.get('MASTER', 'minmax'); MARGIN = float(os.environ.get('MARGIN', '0.01'))
    globals().update(RELMODE=RELMODE, PAIRDEP=PAIRDEP, NONEZERO=NONEZERO)
    which = sys.argv[4] if len(sys.argv) > 4 else 'reps'; rounds = int(sys.argv[5]) if len(sys.argv) > 5 else 80
    cs.D = P
    if which == 'reps':
        prof = json.load(open('meetprofiles_left_9_3.json'))['profiles']
        idxs = sorted(p['rep'] for p in prof)
    else:
        idxs = list(range(len(P)))
    t0 = time.time()
    F = {i: features(P[i], kind) for i in idxs}
    params = sorted({k for i in idxs for f in F[i] for k in f}, key=str); pi_ = {k: j for j, k in enumerate(params)}
    npar = len(params)
    print(f'{len(idxs)} prefixes, {npar} parameters ({sum(1 for k in params if k[0] == "k0")} types)', flush=True)
    SH = 20.0                                       # theta = phi - SH, phi in [0, 2 SH]

    def kvec(i, p):                                # coefficient vector of kappa(p) over params
        v = [0.0] * npar
        for k, c in F[i][p].items():
            v[pi_[k]] += c
        return v
    KV = {i: [kvec(i, p) for p in range(N)] for i in idxs}
    cuts = []
    with Pool(9, initializer=cs.init, initargs=(P,)) as pool:
        for rnd in range(rounds):
            if MASTER == 'l1':
                # variables phi (npar), s_i >= 0 per prefix; minimize sum s_i  s.t.  sum kappa_i - s_i <= 15 - margin
                ni = len(idxs); A = []; b = []
                for k, i in enumerate(idxs):
                    tot = [sum(KV[i][p][j] for p in range(N)) for j in range(npar)]
                    row = tot + [0.0] * ni; row[npar + k] = -1.0
                    A.append(row); b.append(15.0 - MARGIN + SH * sum(tot))
                for coef, rhs in cuts:
                    A.append([-c for c in coef] + [0.0] * ni); b.append(-(rhs + SH * sum(coef)))
                for j in range(npar):
                    r = [0.0] * (npar + ni); r[j] = 1; A.append(r); b.append(2 * SH)
                st, val, x = lp2.solve([0.0] * npar + [-1.0] * ni, A, b)
                if st != 'optimal':
                    print('master', st); break
                th = [x[j] - SH for j in range(npar)]; sl = x[npar:]
                bad = [idxs[k] for k in range(ni) if sl[k] > 1e-7]
                eps = -max(sl) if bad else MARGIN
                print(f'round {rnd}: total excess {sum(sl):.4f}; prefixes over 15 - {MARGIN}: {len(bad)}', flush=True)
            else:
                # variables phi (npar) in [0, 2 SH], eps = e1 - e2; maximize eps
                A = []; b = []
                for i in idxs:
                    tot = [sum(KV[i][p][j] for p in range(N)) for j in range(npar)]
                    const = -SH * sum(tot)              # sum kappa = tot.phi - SH sum(tot)
                    A.append(tot + [1.0, -1.0]); b.append(15.0 - const)
                for coef, rhs in cuts:                  # coef . theta >= rhs  -> coef . phi >= rhs + SH sum(coef)
                    A.append([-c for c in coef] + [0.0, 0.0]); b.append(-(rhs + SH * sum(coef)))
                for j in range(npar):
                    r = [0.0] * (npar + 2); r[j] = 1; A.append(r); b.append(2 * SH)
                r = [0.0] * (npar + 2); r[npar + 1] = 1; A.append(r); b.append(30.0)
                st, val, x = lp2.solve([0.0] * npar + [1.0, -1.0], A, b)
                if st != 'optimal':
                    print('master', st); break
                th = [x[j] - SH for j in range(npar)]; eps = x[npar] - x[npar + 1]
                print(f'round {rnd}: eps = {eps:.4f} (best max sum kappa {15 - eps:.4f})', flush=True)
            jobs = [(i, [3 - sum(KV[i][p][j] * th[j] for j in range(npar)) for p in range(N)]) for i in idxs]
            res = pool.map(cs.separate, jobs)
            new = 0; worst = 0
            for i, r in res:
                if r is None:
                    continue
                wp, rhs, v = r
                # sum_p wp_p (3 - kappa_p) <= rhs  <=>  sum_p wp_p kappa_p >= 3 sum wp - rhs
                coef = [sum(wp[p] * KV[i][p][j] for p in range(N)) for j in range(npar)]
                cuts.append((coef, 3 * sum(wp) - rhs)); new += 1; worst = max(worst, v)
            print(f'   {new} violated (largest {worst:.3f}), {len(cuts)} cuts, {time.time()-t0:.0f}s', flush=True)
            if new == 0 and MASTER == 'l1':
                print(f'converged (l1): {len(bad)} of {len(idxs)} prefixes need sum kappa > 15 - {MARGIN}:', bad)
                json.dump({'kind': kind, 'relmode': RELMODE, 'pairdep': PAIRDEP, 'params': [str(k) for k in params],
                           'theta': th, 'bad': bad}, open(f'capsearch2_{kind}_{RELMODE}_{int(PAIRDEP)}_l1.json', 'w'))
                break
            if new == 0:
                print('converged:', 'a uniform pairwise table WORKS (float; verify exactly)' if eps > 1e-7 else
                      f'NO uniform pairwise table of this kind: best max sum kappa = {15 - eps:.4f}')
                json.dump({'kind': kind, 'relmode': RELMODE, 'pairdep': PAIRDEP, 'params': [str(k) for k in params],
                           'theta': th, 'eps': eps}, open(f'capsearch2_{kind}_{RELMODE}_{int(PAIRDEP)}.json', 'w'))
                break
