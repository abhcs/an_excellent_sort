"""The paired best-gain potential with PREFIX-LEVEL best gains (efficient-prefixes.md section 7.7).

For every possible fourth-layer output x (idle channel, or min / max end of a non-redundant comparator) let
G(x) = its largest fifth-layer gain with any output of any block disjoint from x's block (exact gains).  For a
fourth layer L4 with outputs x_1..x_9, a fifth layer removes at most  Q_G = G_(2) + G_(4) + G_(6) + G_(8)
(sorted decreasingly).  Checks R4 + Q_G <= 14 for every fourth layer; the per-block data (r4, G of the outputs)
is all a proof needs.  usage: EXC.json KEY FIRST:LAST"""
import json, sys, itertools, collections
sys.path[:0] = ['.']
from gainrules import channel_tables, least, dual, leq, cap, N


def matchings(items):
    if not items:
        yield []; return
    a = items[0]
    for m in matchings(items[1:]):
        yield [(a,)] + m
    for i in range(1, len(items)):
        for m in matchings(items[1:i] + items[i + 1:]):
            yield [(a, items[i])] + m


def block_table(pre):
    tabs = channel_tables(pre); W = {}

    def w(t):
        if t not in W:
            W[t] = 3 - cap(least(t) - 4) - cap(least(dual(t)) - 4)
        return W[t]
    blocks = {(p,): [tabs[p]] for p in range(N)}
    for p, q in itertools.combinations(range(N), 2):
        if not (leq(tabs[p], tabs[q]) or leq(tabs[q], tabs[p])):
            blocks[(p, q)] = [tabs[p] & tabs[q], tabs[p] | tabs[q]]
    outs = [(B, k, t) for B, ts in blocks.items() for k, t in enumerate(ts)]
    G = collections.defaultdict(int)
    for (B1, k1, t1), (B2, k2, t2) in itertools.combinations(outs, 2):
        if set(B1) & set(B2) or leq(t1, t2) or leq(t2, t1):
            continue
        g = w(t1) + w(t2) - w(t1 & t2) - w(t1 | t2)
        G[(B1, k1)] = max(G[(B1, k1)], g); G[(B2, k2)] = max(G[(B2, k2)], g)
    S3 = sum(w(t) for t in tabs)
    tab = {B: (sum(w(tabs[p]) for p in B) - sum(w(t) for t in ts), [G[(B, k)] for k in range(len(ts))]) for B, ts in blocks.items()}
    return S3, tab


def check(pre):
    S3, tab = block_table(pre)
    worst = -1; bad = []
    for L4 in matchings(list(range(N))):
        if any(B not in tab for B in L4):
            continue
        R4 = sum(tab[B][0] for B in L4); gs = sorted((g for B in L4 for g in tab[B][1]), reverse=True)
        Q = sum(gs[1::2]); v = R4 + Q - (S3 - 13)
        worst = max(worst, v)
        if v > 0:
            bad.append((L4, R4, gs))
    return worst, bad


if __name__ == '__main__':
    d = json.load(open(sys.argv[1])); P = d[sys.argv[2]]
    lo, hi = map(int, sys.argv[3].split(':'))
    hist = collections.Counter(); nb = 0
    for idx in range(lo, min(hi, len(P))):
        worst, bad = check(P[idx]); hist[worst] += 1; nb += len(bad)
        print(idx, 'max R4 + Q_G - (S3 - 13) =', worst, 'violating fourth layers:', len(bad), (bad[:1] if bad else ''), flush=True)
    print('histogram of max(R4 + Q_G) - (S3 - 13):', sorted(hist.items()), ' violating fourth layers:', nb)
