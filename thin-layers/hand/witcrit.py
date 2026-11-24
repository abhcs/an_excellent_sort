"""For a prefix the 'ovl' rule does not settle: fewest layer-5 pairs (x, y) whose union sizes must come from
explicit witness unions ('pairw' bounds) while all other pairs use the 'ovl' rule.  Greedy relaxation keeping
sum(pi) > 12.  usage: EXC.json KEY IDX..."""
import json, sys, os, itertools, random
os.environ.setdefault('KEEPRED', '1')
sys.path[:0] = ['.']
import gainrules as gr
import fastlp
N = gr.N


def lp_mixed(pre, special):
    """Like gainrules.lp_value, with the 'pairw' rule on the pairs in `special` and 'ovl' elsewhere."""
    tabs = gr.channel_tables(pre)
    top = gr.Side(tabs); bot = gr.Side([gr.dual(t) for t in tabs])
    blocks, outs = gr.outputs(tabs)
    A_ = [min(top.bound(S, 'ovl') for S in o[3]) for o in outs]
    B_ = [min(bot.bound(S, 'ovl') for S in o[4]) for o in outs]
    w = [gr.wcount(A_[i], B_[i]) for i in range(len(outs))]
    pairs, cover = [], []
    for i, j in itertools.combinations(range(len(outs)), 2):
        oi, oj = outs[i], outs[j]
        if set(blocks[oi[0]]) & set(blocks[oj[0]]):
            continue
        g = {}
        for rule in ('ovl', 'pairw'):
            aj = min(top.bound(S + T, rule) for S in oi[3] for T in oj[3])
            bj = min(bot.bound(S + T, rule) for S in oi[4] for T in oj[4])
            g[rule] = w[i] + w[j] - gr.wcount(aj, min(B_[i], B_[j])) - gr.wcount(min(A_[i], A_[j]), bj)
        pairs.append((i, j, g['ovl'], g['pairw']))
    return blocks, outs, w, pairs


def solve(blocks, outs, w, pairs, special):
    K = 3; no = len(outs); nv = N + no; A, b = [], []
    for k, (i, j, go, gw) in enumerate(pairs):
        g = gw if k in special else go
        if g <= 0:
            continue
        row = [0] * nv; row[N + i] += 1; row[N + j] += 1; A.append(row); b.append(6 - g)
    for i in range(no):
        row = [0] * nv; row[N + i] = 1; A.append(row); b.append(3)
    for bi, chs in enumerate(blocks):
        idx = [k for k, o in enumerate(outs) if o[0] == bi]
        row = [0] * nv; r = sum(w[k] for k in idx) + K * len(chs) - 3 * len(idx)
        for p in chs:
            row[p] += 1
        for k in idx:
            row[N + k] -= 1
        A.append(row); b.append(r)
    val, _ = fastlp.simplex([1] * N + [0] * no, A, b)
    return val - 9 * K


d = json.load(open(sys.argv[1])); P = d[sys.argv[2]]
for idx in map(int, sys.argv[3:]):
    blocks, outs, w, pairs = lp_mixed(P[idx], None)
    cand = [k for k, p in enumerate(pairs) if p[3] < p[2]]
    E = set(cand)
    v_all = solve(blocks, outs, w, pairs, E); v_none = solve(blocks, outs, w, pairs, set())
    random.seed(idx); order = cand[:]; random.shuffle(order)
    for k in order:
        if solve(blocks, outs, w, pairs, E - {k}) > 12 + 1e-6:
            E.discard(k)
    names = [f'{outs[pairs[k][0]][1]}|{outs[pairs[k][1]][1]}' for k in sorted(E)]
    print(idx, f'ovl={v_none:.3f} all-pairw={v_all:.3f}; {len(cand)} pairs where witness unions help; needed {len(E)}:', ' '.join(names), flush=True)
