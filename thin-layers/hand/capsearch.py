"""Search for a UNIFORM capacity table (efficient-prefixes.md section 7.7).

A block-separable certificate is the same as capacities kappa(p) = 3 - pi(p) on the prefix channels: every
block's layer-4 removal plus the cover values of its outputs fits in the capacities of its channels, and
R4 + R5 <= sum kappa.  (W) needs sum kappa < 15.  Is there ONE table kappa[type] (type = (a, b) of the prefix
channel, or coarser/finer) that works for every prefix, the cover values c still chosen per prefix?

Cutting planes: the master LP chooses kappa[type] maximising eps with sum_p kappa[t(p)] + eps <= 15 for every
prefix, subject to the cuts found so far.  For each prefix, a separation LP over fractional fourth layers y and
fifth layers z (Farkas dual of the certificate LP with pi fixed) finds a violated inequality
  sum_B y_B pi(B) <= sum_B y_B W_B - sum z g,
if any.  Exact gains from truth tables.  usage: capsearch.py EXC.json KEY TYPE [reps|all] [rounds]"""
import json, sys, itertools, collections, time
from multiprocessing import Pool
import numpy as np
sys.path[:0] = ['.']
import gainrules as gr
import fastlp, lp2
N = gr.N
D = None; SYS = {}


def system(idx):
    if idx in SYS:
        return SYS[idx]
    pre = D[idx]; tabs = gr.channel_tables(pre)
    W = {}

    def w(t):
        if t not in W:
            W[t] = 3 - gr.cap(gr.least(t) - 4) - gr.cap(gr.least(gr.dual(t)) - 4)
        return W[t]
    blocks = [(p,) for p in range(N)]
    outs = [(p, tabs[p]) for p in range(N)]
    for p, q in itertools.combinations(range(N), 2):
        if gr.leq(tabs[p], tabs[q]) or gr.leq(tabs[q], tabs[p]):
            continue
        blocks.append((p, q))
        outs += [(len(blocks) - 1, tabs[p] & tabs[q]), (len(blocks) - 1, tabs[p] | tabs[q])]
    cover = []
    for i, j in itertools.combinations(range(len(outs)), 2):
        (bi, ti), (bj, tj) = outs[i], outs[j]
        if set(blocks[bi]) & set(blocks[bj]) or gr.leq(ti, tj) or gr.leq(tj, ti):
            continue
        g = w(ti) + w(tj) - w(ti & tj) - w(ti | tj)
        if g > 0:
            cover.append((i, j, g))
    WB = [0] * len(blocks)
    for bi, t in outs:
        WB[bi] += w(t)
    top = gr.Side(tabs); bot = gr.Side([gr.dual(t) for t in tabs])
    info = {'ab': [(top.a[p], bot.a[p]) for p in range(N)],
            'abn': [(top.a[p], bot.a[p], len(top.mins((p,))), len(bot.mins((p,)))) for p in range(N)]}
    SYS[idx] = (blocks, outs, WB, cover, info)
    return SYS[idx]


def tkey(info, kind, p):
    if kind == 'ab':
        return info['ab'][p]
    if kind == 'abs':                        # complement-symmetric: kappa(a, b) = kappa(b, a)
        return tuple(sorted(info['ab'][p]))
    if kind == 'abn':
        return info['abn'][p]
    if kind == 'abns':
        a, b, nt, nc = info['abn'][p]
        return min((a, b, nt, nc), (b, a, nc, nt))
    raise ValueError(kind)


def separate(args):
    idx, pi = args
    blocks, outs, WB, cover, info = system(idx)
    nb = len(blocks); nz = len(cover); no = len(outs)
    # variables: y_B (nb), z_k (nz).  maximize sum g z - sum y_B (W_B - pi(B))
    c = [-(WB[b] - sum(pi[p] for p in blocks[b])) for b in range(nb)] + [g for _, _, g in cover]
    A = []; bb = []
    rows = [[0.0] * (nb + nz) for _ in range(no)]
    for k, (i, j, g) in enumerate(cover):
        rows[i][nb + k] += 1; rows[j][nb + k] += 1
    for x, (bi, _) in enumerate(outs):
        rows[x][bi] -= 1
    A += rows; bb += [0.0] * no
    for b in range(nb):
        r = [0.0] * (nb + nz); r[b] = 1; A.append(r); bb.append(1.0)
    val, x = fastlp.simplex(c, A, bb)
    if val <= 1e-7:
        return idx, None
    y = x[:nb]; z = x[nb:]
    # cut: sum_B y_B pi(B) <= sum_B y_B W_B - sum z g ;  returned as (per-channel weight of pi_p, rhs)
    wp = [0.0] * N
    for b in range(nb):
        for p in blocks[b]:
            wp[p] += y[b]
    rhs = sum(y[b] * WB[b] for b in range(nb)) - sum(z[k] * cover[k][2] for k in range(nz))
    return idx, (wp, rhs, val)


def init(d):
    global D
    D = d


if __name__ == '__main__':
    d = json.load(open(sys.argv[1])); P = d[sys.argv[2]]; kind = sys.argv[3]
    which = sys.argv[4] if len(sys.argv) > 4 else 'reps'; rounds = int(sys.argv[5]) if len(sys.argv) > 5 else 40
    D = P
    if which == 'reps':
        prof = json.load(open('meetprofiles_left_9_3.json'))['profiles']
        idxs = sorted(p['rep'] for p in prof)
    else:
        idxs = list(range(len(P)))
    t0 = time.time()
    with Pool(9, initializer=init, initargs=(P,)) as pool:
        tys = {}
        for i in idxs:
            tys[i] = [tkey(system(i)[4], kind, p) for p in range(N)]
        types = sorted({t for i in idxs for t in tys[i]}); ti = {t: k for k, t in enumerate(types)}
        nt = len(types)
        print(f'{len(idxs)} prefixes, {nt} types: {types}', flush=True)
        cuts = []                                  # (coef over types for kappa, rhs): coef . kappa >= rhs
        for rnd in range(rounds):
            # master: variables kappa_t (nt), eps = e1 - e2 (free) ; maximize eps
            A = []; b = []
            for i in idxs:
                row = [0.0] * (nt + 2)
                for t in tys[i]:
                    row[ti[t]] += 1
                row[nt] = 1; row[nt + 1] = -1; A.append(row); b.append(15.0)
            for coef, rhs in cuts:
                A.append([-v for v in coef] + [0.0, 0.0]); b.append(-rhs)
            for k in range(nt):
                r = [0.0] * (nt + 2); r[k] = 1; A.append(r); b.append(6.0)
            r = [0.0] * (nt + 2); r[nt + 1] = 1; A.append(r); b.append(30.0)
            st, val, x = lp2.solve([0.0] * nt + [1.0, -1.0], A, b)
            if st != 'optimal':
                print('master', st); break
            kap = x[:nt]; eps = x[nt] - x[nt + 1]
            print(f'round {rnd}: eps = {eps:.4f} (best max sum kappa {15 - eps:.4f})  kappa = '
                  + ', '.join(f'{types[k]}:{kap[k]:.3f}' for k in range(nt)), flush=True)
            jobs = [(i, [3 - kap[ti[t]] for t in tys[i]]) for i in idxs]
            res = pool.map(separate, jobs)
            new = 0; worst = 0
            for i, r in res:
                if r is None:
                    continue
                wp, rhs, v = r
                coef = [0.0] * nt
                for p in range(N):
                    coef[ti[tys[i][p]]] += wp[p]
                # sum_p wp_p (3 - kappa_p) <= rhs  <=>  coef . kappa >= 3 sum wp - rhs
                cuts.append((coef, 3 * sum(wp) - rhs)); new += 1; worst = max(worst, v)
            print(f'   {new} violated prefixes (largest violation {worst:.3f}), {len(cuts)} cuts, {time.time()-t0:.0f}s', flush=True)
            if new == 0:
                print('converged:', 'a uniform table WORKS (float; verify exactly)' if eps > 1e-7 else
                      f'NO uniform table of this kind: best max over prefixes of sum kappa = {15 - eps:.4f} >= 15')
                json.dump({'kind': kind, 'types': [list(t) for t in types], 'kappa': list(map(float, kap)), 'eps': eps},
                          open(f'capsearch_{kind}.json', 'w'))
                break
