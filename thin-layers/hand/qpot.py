"""The paired best-gain potential Q (efficient-prefixes.md section 7.7), exact integers from truth tables.

After a fourth layer L4 (9 outputs), let g*(x) be the largest fifth-layer gain of output x with any other output
present, and N_t the number of outputs with g*(x) >= t.  A fifth-layer comparator with gain >= t joins two such
outputs, so a fifth layer removes at most  Q = floor(N_1/2) + floor(N_2/2) + floor(N_3/2)  window incidences
(= the 2nd + 4th + 6th + 8th largest g*).  (W) follows if  R4 + Q <= S3 - 13  for every fourth layer.
Prints per prefix the largest R4 + Q - (S3 - 13) (must be <= 0).
usage: qpot.py ALL.json KEY (FIRST:LAST | @FILE_OF_INDICES)"""
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


L4S = list(matchings(list(range(N))))


def worst(pre):
    tabs = channel_tables(pre); W = {}

    def w(t):
        if t not in W:
            W[t] = 3 - cap(least(t) - 4) - cap(least(dual(t)) - 4)
        return W[t]
    S3 = sum(w(t) for t in tabs); best = -99; arg = None
    for L4 in L4S:
        if any(len(B) == 2 and (leq(tabs[B[0]], tabs[B[1]]) or leq(tabs[B[1]], tabs[B[0]])) for B in L4):
            continue
        outs = []; blk = []
        for bi, B in enumerate(L4):
            ts = [tabs[B[0]]] if len(B) == 1 else [tabs[B[0]] & tabs[B[1]], tabs[B[0]] | tabs[B[1]]]
            outs += ts; blk += [bi] * len(ts)
        ws = [w(t) for t in outs]; R4 = S3 - sum(ws); n = len(outs)
        gs = [0] * n
        for i, j in itertools.combinations(range(n), 2):
            if blk[i] != blk[j] and not (leq(outs[i], outs[j]) or leq(outs[j], outs[i])):
                g = ws[i] + ws[j] - w(outs[i] & outs[j]) - w(outs[i] | outs[j])
                if g > gs[i]: gs[i] = g
                if g > gs[j]: gs[j] = g
        Q = sum(sum(1 for v in gs if v >= t) // 2 for t in (1, 2, 3))
        v = R4 + Q - (S3 - 13)
        if v > best:
            best, arg = v, (L4, R4, gs)
    return S3, best, arg


if __name__ == '__main__':
    d = json.load(open(sys.argv[1])); P = d[sys.argv[2]]
    spec = sys.argv[3]
    idxs = [int(x) for x in open(spec[1:]).read().split()] if spec.startswith('@') else range(*map(int, spec.split(':')))
    hist = collections.Counter()
    for idx in idxs:
        if idx >= len(P):
            continue
        S3, b, arg = worst(P[idx]); hist[b] += 1
        print(idx, S3, b, (arg if b > 0 else ''), flush=True)
    print('histogram of max(R4 + Q) - (S3 - 13):', sorted(hist.items()))
