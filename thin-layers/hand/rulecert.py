"""Exact block-separable certificates under a gain rule (efficient-prefixes.md section 7.6).

For each prefix: solve the certificate LP with rule-based sizes (gainrules.py), round every cover value c UP
onto a grid, solve an exact LP for the potentials pi, and re-check every inequality in exact arithmetic.
All sizes used are rule-based upper bounds on least term / clause sizes, so a certificate with sum(pi) > 12
proves S_5 >= 13 after every fourth and fifth layer.  Tries the rules in the given order, keeps the first
that certifies.  Writes one JSON line per prefix.
usage: rulecert.py EXC.json KEY FIRST:LAST RULE[,RULE...] OUT.jsonl"""
import json, sys, os, itertools, math
from fractions import Fraction
os.environ.setdefault('KEEPRED', '1')
sys.path[:0] = ['.']
import gainrules as gr
import fastlp
from lp import simplex
N = gr.N; K = 3


def system(pre, rule):
    tabs = gr.channel_tables(pre)
    top = gr.Side(tabs); bot = gr.Side([gr.dual(t) for t in tabs])
    blocks, outs = gr.outputs(tabs)
    A_ = [min(top.bound(S, rule) for S in o[3]) for o in outs]
    B_ = [min(bot.bound(S, rule) for S in o[4]) for o in outs]
    w = [gr.wcount(A_[i], B_[i]) for i in range(len(outs))]
    cover = []
    for i, j in itertools.combinations(range(len(outs)), 2):
        oi, oj = outs[i], outs[j]
        if set(blocks[oi[0]]) & set(blocks[oj[0]]):
            continue
        aj = min(top.bound(S + T, rule) for S in oi[3] for T in oj[3])
        bj = min(bot.bound(S + T, rule) for S in oi[4] for T in oj[4])
        g = w[i] + w[j] - gr.wcount(aj, min(B_[i], B_[j])) - gr.wcount(min(A_[i], A_[j]), bj)
        if g > 0:
            cover.append((i, j, g))
    return blocks, outs, w, cover


def certify(pre, rule):
    blocks, outs, w, cover = system(pre, rule)
    no = len(outs); nv = N + no; A, b = [], []
    for i, j, g in cover:
        row = [0] * nv; row[N + i] += 1; row[N + j] += 1; A.append(row); b.append(6 - g)
    for i in range(no):
        row = [0] * nv; row[N + i] = 1; A.append(row); b.append(3)
    idxs = [[k for k, o in enumerate(outs) if o[0] == bi] for bi in range(len(blocks))]
    for bi, chs in enumerate(blocks):
        row = [0] * nv; r = sum(w[k] for k in idxs[bi]) + K * len(chs) - 3 * len(idxs[bi])
        for p in chs:
            row[p] += 1
        for k in idxs[bi]:
            row[N + k] -= 1
        A.append(row); b.append(r)
    if min(b) < 0:
        return None
    val, x = fastlp.simplex([1] * N + [0] * no, A, b)
    best = None
    for den in (2, 3, 4, 6, 8, 9, 12, 18, 24, 36, 72):
        c = [min(Fraction(3), max(Fraction(0), Fraction(math.ceil((3 - x[N + k]) * den - 1e-7), den))) for k in range(no)]
        if any(c[i] + c[j] < g for i, j, g in cover):
            continue
        A2, b2 = [], []
        for bi, chs in enumerate(blocks):
            row = [0] * N
            for p in chs:
                row[p] += 1
            A2.append(row); b2.append(sum(w[k] - c[k] for k in idxs[bi]) + K * len(chs))
        if min(b2) < 0:
            continue
        v2, s2, _ = simplex([1] * N, A2, b2)
        pi = [s2[p] - K for p in range(N)]
        if best is None or sum(pi) > sum(best[0]):
            best = (pi, c)
    if best is None:
        return None
    pi, c = best
    # exact re-check, recomputing the rule-based system from scratch
    blocks2, outs2, w2, cover2 = system(pre, rule)
    ok = all(c[i] + c[j] >= g for i, j, g in cover2) and min(c) >= 0
    ok = ok and all(sum(pi[p] for p in chs) <= sum(w2[k] - c[k] for k in idxs[bi]) for bi, chs in enumerate(blocks2))
    return {'ok': ok, 'sum_pi': sum(pi), 'pi': pi, 'c': {outs[k][1]: c[k] for k in range(no)}, 'cover_pairs': len(cover)}


if __name__ == '__main__':
    d = json.load(open(sys.argv[1])); P = d[sys.argv[2]]
    lo, hi = map(int, sys.argv[3].split(':')); rules = sys.argv[4].split(',')
    with open(sys.argv[5], 'w') as fo:
        for idx in range(lo, min(hi, len(P))):
            res = None
            for rule in rules:
                cert = certify(P[idx], rule)
                if cert and cert['ok'] and cert['sum_pi'] > 12:
                    res = (rule, cert); break
            if res is None:
                fo.write(json.dumps({'idx': idx, 'rule': None}) + '\n'); print(idx, 'NOT CERTIFIED', flush=True); continue
            rule, cert = res
            fo.write(json.dumps({'idx': idx, 'rule': rule, 'sum_pi': str(cert['sum_pi']), 'pi': [str(v) for v in cert['pi']],
                                 'c': {k: str(v) for k, v in cert['c'].items()}, 'cover_pairs': cert['cover_pairs']}) + '\n')
            print(idx, rule, cert['sum_pi'], flush=True)
