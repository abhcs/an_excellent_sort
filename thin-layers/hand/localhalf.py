"""Potentials on the state after layer 4 (efficient-prefixes.md section 7.7).  For a fourth layer L4 with outputs
x and layer-5 gains g(x, y):
  nu  = best fifth-layer removal (max-weight matching),
  tau = least fractional vertex cover of g  (LP),
  H   = sum_x max_y g(x, y) / 2   (each output pays half its best gain among the outputs present),
  Q   = g*_(2) + g*_(4) + g*_(6) + g*_(8), the best gains g*(x) = max_y g(x, y) sorted decreasingly
        (a fifth-layer comparator gains at most the smaller best gain of its two inputs).
All bound R5, and nu <= tau <= H, nu <= Q <= H.  (W) is R4 + nu <= 14.  Reports, per prefix, the largest R4 + H and
R4 + tau over fourth layers, and counts fourth layers with R4 + H >= 15.  usage: EXC.json KEY FIRST:LAST [tau]"""
import json, sys, itertools, functools, collections
sys.path[:0] = ['.']
from gainrules import channel_tables, least, dual, leq, cap, N
import fastlp


def matchings(items):
    if not items:
        yield []; return
    a = items[0]
    for m in matchings(items[1:]):
        yield [(a,)] + m
    for i in range(1, len(items)):
        for m in matchings(items[1:i] + items[i + 1:]):
            yield [(a, items[i])] + m


def run(pre, want_tau):
    tabs = channel_tables(pre); W = {}

    def w(t):
        if t not in W:
            W[t] = 3 - cap(least(t) - 4) - cap(least(dual(t)) - 4)
        return W[t]
    S3 = sum(w(t) for t in tabs); out = {'H': -1, 'tau': -1, 'nu': -1, 'badH': 0, 'n': 0}
    for L4 in matchings(list(range(N))):
        if any(len(B) == 2 and (leq(tabs[B[0]], tabs[B[1]]) or leq(tabs[B[1]], tabs[B[0]])) for B in L4):
            continue
        outs = []; blk = []
        for bi, B in enumerate(L4):
            ts = [tabs[B[0]]] if len(B) == 1 else [tabs[B[0]] & tabs[B[1]], tabs[B[0]] | tabs[B[1]]]
            outs += ts; blk += [bi] * len(ts)
        ws = [w(t) for t in outs]; R4 = S3 - sum(ws); n = len(outs)
        g = [[0] * n for _ in range(n)]
        for i, j in itertools.combinations(range(n), 2):
            if blk[i] != blk[j] and not (leq(outs[i], outs[j]) or leq(outs[j], outs[i])):
                g[i][j] = g[j][i] = ws[i] + ws[j] - w(outs[i] & outs[j]) - w(outs[i] | outs[j])
        gs = [max(g[i]) for i in range(n)]
        H = sum(gs) / 2
        Hm = H - min(gs) / 2 if n % 2 else H          # an odd number of outputs leaves one unmatched
        sg = sorted(gs, reverse=True)
        Q = sum(sg[1::2])                             # every L5 pair gains <= min of the two best gains

        @functools.lru_cache(maxsize=None)
        def mm(mask):
            if mask == 0:
                return 0
            i = (mask & -mask).bit_length() - 1; rest = mask & ~(1 << i); bv = mm(rest)
            for j in range(n):
                if rest >> j & 1 and g[i][j] > 0:
                    bv = max(bv, g[i][j] + mm(rest & ~(1 << j)))
            return bv
        nu = mm((1 << n) - 1)
        out['n'] += 1
        out['H'] = max(out['H'], R4 + H); out['nu'] = max(out['nu'], R4 + nu)
        out['Hm'] = max(out.get('Hm', -1), R4 + Hm)
        out['Q'] = max(out.get('Q', -1), R4 + Q)
        if R4 + Q >= 15:
            out['badQ'] = out.get('badQ', 0) + 1
            out.setdefault('exQ', []).append((L4, R4, gs, nu))
        if R4 + Hm >= 15:
            out['badHm'] = out.get('badHm', 0) + 1
            out.setdefault('exHm', []).append((L4, R4, gs, nu))
        if R4 + H >= 15:
            out['badH'] += 1
            if want_tau:
                pairs = [(i, j, g[i][j]) for i, j in itertools.combinations(range(n), 2) if g[i][j] > 0]
                # tau = min sum c, c_i + c_j >= g_ij, 0 <= c <= 3  ->  max sum d, d = 3 - c: d_i + d_j <= 6 - g
                A = []; b = []
                for i, j, gg in pairs:
                    r = [0] * n; r[i] = 1; r[j] = 1; A.append(r); b.append(6 - gg)
                for i in range(n):
                    r = [0] * n; r[i] = 1; A.append(r); b.append(3)
                v, _ = fastlp.simplex([1] * n, A, b)
                out['tau'] = max(out['tau'], R4 + 3 * n - v)
    return S3, out


if __name__ == '__main__':
    d = json.load(open(sys.argv[1])); P = d[sys.argv[2]]
    lo, hi = map(int, sys.argv[3].split(':')); want_tau = len(sys.argv) > 4
    agg = collections.Counter(); worstH = 0; prefH = 0; worstHm = 0; worstQ = 0
    for idx in range(lo, min(hi, len(P))):
        S3, o = run(P[idx], want_tau)
        worstH = max(worstH, o['H']); prefH += o['badH'] > 0; agg['L4'] += o['n']; agg['badL4'] += o['badH']
        agg['badHm'] += o.get('badHm', 0); worstHm = max(worstHm, o.get('Hm', -1))
        agg['badQ'] += o.get('badQ', 0); worstQ = max(worstQ, o.get('Q', -1))
        for ex in o.get('exQ', []):
            print('   R4+Q >= 15:', idx, ex, flush=True)
        for ex in o.get('exHm', []):
            print('   R4+Hm >= 15:', idx, ex, flush=True)
        print(idx, f"max R4+nu {o['nu']}  max R4+H {o['H']}  max R4+Hm {o.get('Hm')}  L4 with R4+H>=15: {o['badH']}/{o['n']}"
              + (f"  max R4+tau over those {o['tau']:.2f}" if want_tau and o['badH'] else ''), flush=True)
    print(f'prefixes with some fourth layer R4 + H >= 15: {prefH}; fourth layers: {agg["badL4"]} of {agg["L4"]}; largest R4 + H {worstH}')
    print(f'with one output unmatched (Hm): fourth layers with R4 + Hm >= 15: {agg["badHm"]}; largest R4 + Hm {worstHm}')
    print(f'pairing best gains (Q): fourth layers with R4 + Q >= 15: {agg["badQ"]}; largest R4 + Q {worstQ}')
