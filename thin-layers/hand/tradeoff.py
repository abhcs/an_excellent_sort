"""Trade-off between the window removal R4 of layer 4 and the best removal R5 of layer 5 (efficient-prefixes.md
section 7.6).  For each prefix and each value of R4: the largest R5 over fourth layers removing R4 (exact
truth tables, best fifth layer by a matching DP).  (W) says R4 + R5 <= S3 - 13.
usage: tradeoff.py EXC.json KEY FIRST:LAST"""
import json, sys, itertools, functools, collections
sys.path[:0] = ['.']
from gainrules import channel_tables, least, dual, leq, cap, N
DU = {}


def w(t):
    if t not in DU:
        DU[t] = 3 - cap(least(t) - 4) - cap(least(dual(t)) - 4)
    return DU[t]


def matchings(items):
    if not items:
        yield []; return
    a = items[0]
    for m in matchings(items[1:]):
        yield [(a,)] + m
    for i in range(1, len(items)):
        for m in matchings(items[1:i] + items[i + 1:]):
            yield [(a, items[i])] + m


def curve(pre):
    tabs = channel_tables(pre); S3 = sum(w(t) for t in tabs); best = {}
    for L4 in matchings(list(range(N))):
        if any(len(B) == 2 and (leq(tabs[B[0]], tabs[B[1]]) or leq(tabs[B[1]], tabs[B[0]])) for B in L4):
            continue
        outs = []
        for B in L4:
            outs += [tabs[B[0]]] if len(B) == 1 else [tabs[B[0]] & tabs[B[1]], tabs[B[0]] | tabs[B[1]]]
        ws = [w(t) for t in outs]; R4 = S3 - sum(ws); n = len(outs)
        g = [[0] * n for _ in range(n)]
        for i, j in itertools.combinations(range(n), 2):
            if not (leq(outs[i], outs[j]) or leq(outs[j], outs[i])):
                g[i][j] = g[j][i] = ws[i] + ws[j] - w(outs[i] & outs[j]) - w(outs[i] | outs[j])

        @functools.lru_cache(maxsize=None)
        def mm(mask):
            if mask == 0:
                return 0
            i = (mask & -mask).bit_length() - 1; rest = mask & ~(1 << i); bv = mm(rest)
            for j in range(n):
                if rest >> j & 1 and g[i][j] > 0:
                    bv = max(bv, g[i][j] + mm(rest & ~(1 << j)))
            return bv
        R5 = mm((1 << n) - 1)
        best[R4] = max(best.get(R4, -1), R5)
    return S3, best


if __name__ == '__main__':
    d = json.load(open(sys.argv[1])); P = d[sys.argv[2]]
    lo, hi = map(int, sys.argv[3].split(':'))
    tot = collections.defaultdict(lambda: [99, -1]); s3s = collections.Counter(); worst = collections.Counter()
    for idx in range(lo, min(hi, len(P))):
        S3, best = curve(P[idx]); s3s[S3] += 1
        worst[max(r4 + r5 for r4, r5 in best.items()) - (S3 - 13)] += 1
        for r4, r5 in best.items():
            t = tot[r4]; t[0] = min(t[0], r4 + r5); t[1] = max(t[1], r4 + r5)
        print(idx, S3, ' '.join(f'{r4}:{r5}' for r4, r5 in sorted(best.items())), flush=True)
    print('S3 values:', dict(s3s))
    print('max over R4 of (R4 + best R5) minus (S3 - 13), i.e. slack used (0 = tight):', dict(sorted(worst.items())))
    print('per R4: least and largest R4 + best R5 over prefixes:', {r4: tuple(v) for r4, v in sorted(tot.items())})
