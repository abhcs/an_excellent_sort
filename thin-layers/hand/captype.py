"""Capacities kappa(p) = 3 - pi(p) of block-separable certificates (efficient-prefixes.md section 7.7).
Does a certificate exist whose potentials depend only on a TYPE of the prefix channel?  Per prefix: the LP of
blockcert.py with pi_p = alpha[type(p)] (exact gains).  Types: 'ab' = (a, b); 'abn' = (a, b, number of
shortest terms, number of shortest clauses); 'free' = no restriction.
usage: EXC.json KEY FIRST:LAST TYPE[,TYPE...]"""
import json, sys, itertools, collections
sys.path[:0] = ['.']
import gainrules as gr
import fastlp
N = gr.N; K = 3


def system(pre):
    tabs = gr.channel_tables(pre)
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
    return tabs, blocks, outs, [w(t) for _, t in outs], cover


def chtype(tabs, kind):
    top = gr.Side(tabs); bot = gr.Side([gr.dual(t) for t in tabs])
    if kind == 'free':
        return list(range(N))
    if kind == 'ab':
        return [(top.a[p], bot.a[p]) for p in range(N)]
    if kind == 'abn':
        return [(top.a[p], bot.a[p], len(top.mins((p,))), len(bot.mins((p,)))) for p in range(N)]
    raise ValueError(kind)


def best(pre, kind, sysd=None):
    tabs, blocks, outs, w, cover = sysd or system(pre)
    ty = chtype(tabs, kind); types = sorted(set(ty), key=str); ti = {t: i for i, t in enumerate(types)}
    nt = len(types); no = len(outs); nv = nt + no; A, b = [], []
    for i, j, g in cover:
        row = [0] * nv; row[nt + i] += 1; row[nt + j] += 1; A.append(row); b.append(6 - g)
    for i in range(no):
        row = [0] * nv; row[nt + i] = 1; A.append(row); b.append(3)
    for bi, chs in enumerate(blocks):
        idx = [k for k, o in enumerate(outs) if o[0] == bi]
        row = [0] * nv; r = sum(w[k] for k in idx) + K * len(chs) - 3 * len(idx)
        for p in chs:
            row[ti[ty[p]]] += 1
        for k in idx:
            row[nt + k] -= 1
        A.append(row); b.append(r)
    obj = [0] * nv
    for p in range(N):
        obj[ti[ty[p]]] += 1
    val, x = fastlp.simplex(obj, A, b)
    alpha = {t: x[ti[t]] - K for t in types}
    return val - 9 * K, alpha


if __name__ == '__main__':
    d = json.load(open(sys.argv[1])); P = d[sys.argv[2]]
    lo, hi = map(int, sys.argv[3].split(':')); kinds = sys.argv[4].split(',')
    fails = collections.Counter(); least = {k: 99 for k in kinds}
    for idx in range(lo, min(hi, len(P))):
        sd = system(P[idx]); out = []
        for k in kinds:
            v, al = best(P[idx], k, sd)
            least[k] = min(least[k], v); fails[k] += v <= 12 + 1e-6
            out.append(f'{k}={v:.3f}')
        print(idx, ' '.join(out), flush=True)
    for k in kinds:
        print(f'{k}: prefixes with sum(pi) <= 12: {fails[k]}; least {least[k]:.3f}')
