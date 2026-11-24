"""Gain lemmas for block-separable certificates (efficient-prefixes.md section 7.6).

Every quantity in a certificate is a least term size a or least clause size b of an AND or OR of prefix
channels.  Window counts only grow when a and b shrink, so UPPER bounds on these sizes give valid lower
bounds on S_5 (section 7.4).  This script replaces the exact sizes of sets of prefix channels by rule-based
upper bounds and asks whether block-separable certificates still reach sum(pi) > 12.

J(S) = least term size of AND_{p in S} f_p, K(S) = least clause size of OR_{p in S} f_p.
Rules for J (K is the dual, computed on dual functions):
  free   J(S) <= sum_{p in S} a_p                                  (overlap-free)
  abs    first drop every p in S above another member of S (f_q <= f_p), then 'free'
  core   abs, then each kept channel contributes a_p - |core_p| plus the union of the cores
         (core_p = inputs common to all minimum-size terms of p)
  pair   abs, then the best split of the kept channels into singletons and pairs, pairs at exact J
  pairc  as pair, but pairs at their 'core' bound instead of exact
  pairna as pair, without the absorption step (no order relations needed)
  trip   abs, then the best split into parts of size <= 3, parts at exact J
  meet   as pair, with J(p, q) = a_p + a_q - 1 when some minimum-size terms of p and q meet, else the sum
  ovl    as pair, with J(p, q) = a_p + a_q - (largest intersection of minimum-size terms of p and q)
  pairw  abs, then a split into singletons and pairs with one minimum-size term per part; size of the union
  exact  J(S) itself
usage: gainrules.py EXC.json KEY FIRST:LAST RULE[,RULE...]"""
import json, sys, itertools, functools
sys.path[:0] = ['.']
import fastlp, os
KEEPRED = os.environ.get('KEEPRED') == '1'   # keep redundant blocks and pairs (no redundancy proofs needed)

N = 9; FULL = (1 << N) - 1; ALL = (1 << (1 << N)) - 1
POP = [bin(x).count('1') for x in range(1 << N)]
WM = [sum(1 << x for x in range(1 << N) if POP[x] == k) for k in range(N + 1)]


def channel_tables(pre):
    tabs = [0] * N
    for x in range(1 << N):
        t = x
        for L in pre:
            for i, j in L:
                if (t >> i) & 1 and not (t >> j) & 1:
                    t ^= (1 << i) | (1 << j)
        for c in range(N):
            if (t >> c) & 1:
                tabs[c] |= 1 << x
    return tabs


def dual(t):                               # f^d(x) = not f(not x); clauses of f = terms of f^d
    d = 0
    for x in range(1 << N):
        if not (t >> (FULL ^ x)) & 1:
            d |= 1 << x
    return d


def least(t):                              # least term size (N + 1 if f = 0)
    for k in range(N + 1):
        if t & WM[k]:
            return k
    return N + 1


def core(t):
    a = least(t); c = FULL
    m = t & WM[a]
    x = 0
    while m:
        if m & 1:
            c &= x
        m >>= 1; x += 1
    return c


def leq(tx, ty):
    return tx & ~ty == 0


def cap(v):
    return max(0, min(3, v))


class Side:
    """Term sizes of ANDs of prefix channels for one side (tables = f for J, duals for K)."""

    def __init__(self, tabs):
        self.override = {}
        self.t = tabs
        self.a = [least(t) for t in tabs]
        self.core = [core(t) for t in tabs]

    @functools.lru_cache(maxsize=None)
    def exact(self, S):
        t = ALL
        for p in S:
            t &= self.t[p]
        return least(t)

    def reduce(self, S):                   # drop members above another member (keep one of equal ones)
        S = sorted(set(S)); keep = []
        for i, p in enumerate(S):
            if any(leq(self.t[q], self.t[p]) and (not leq(self.t[p], self.t[q]) or q < p) for q in S if q != p):
                continue
            keep.append(p)
        return tuple(keep)

    @functools.lru_cache(maxsize=None)
    def mins(self, S):                     # all minimum-size terms of AND of S
        t = ALL
        for p in S:
            t &= self.t[p]
        k = least(t); m = t & WM[k]; out = []; x = 0
        while m:
            if m & 1:
                out.append(x)
            m >>= 1; x += 1
        return tuple(out)

    def witbound(self, R):
        # choose a split of R into singletons and pairs, one minimum term per part; least size of the union
        best = [10 ** 9]

        def rec(rest, acc):
            if POP[acc] >= best[0]:
                return
            if not rest:
                best[0] = POP[acc]; return
            p = rest[0]
            for T in self.mins((p,)):
                rec(rest[1:], acc | T)
            for i in range(1, len(rest)):
                for T in self.mins((p, rest[i])):
                    rec(rest[1:i] + rest[i + 1:], acc | T)
        rec(R, 0)
        return best[0]

    def meetbound(self, P):                # a_p + a_q - 1 if some minimum terms of p and q meet, else the sum
        p, q = P
        meet = any(T & U for T in self.mins((p,)) for U in self.mins((q,)))
        return self.a[p] + self.a[q] - (1 if meet else 0)

    def ovlbound(self, P):                 # a_p + a_q - (largest intersection of minimum-size terms of p and q)
        p, q = P
        return self.a[p] + self.a[q] - max(POP[T & U] for T in self.mins((p,)) for U in self.mins((q,)))

    def corebound(self, S):
        u = 0
        for p in S:
            u |= self.core[p]
        return sum(self.a[p] - POP[self.core[p]] for p in S) + POP[u]

    @functools.lru_cache(maxsize=None)
    def bound(self, S, rule):
        S = tuple(sorted(set(S)))
        if rule == 'exact' or len(S) == 1:
            return self.exact(S)
        if rule == 'free':
            return sum(self.a[p] for p in S)
        R = self.reduce(S) if rule != 'pairna' else S
        if rule == 'abs':
            return sum(self.a[p] for p in R)
        if rule == 'core':
            return self.corebound(R)
        if rule == 'trip':                 # best split into parts of size <= 3, parts at exact values
            best = [10 ** 9]

            def rec3(rest, acc):
                if acc >= best[0]:
                    return
                if not rest:
                    best[0] = acc; return
                p = rest[0]; others = rest[1:]
                for k in range(0, 3):
                    for C in itertools.combinations(others, k):
                        rem = tuple(o for o in others if o not in C)
                        rec3(rem, acc + self.exact((p,) + C))
            rec3(R, 0)
            return best[0]
        if rule == 'pairw':                # unions of minimum common terms of pairs and of single channels
            return self.witbound(R)
        if rule in ('pair', 'pairc', 'pairna', 'meet', 'ovl'):
            if rule == 'meet':
                pv = lambda P: self.meetbound(P)
            elif rule == 'ovl':
                pv = lambda P: self.ovlbound(P)
            elif rule == 'pairc':
                pv = lambda P: self.corebound(P)
            else:
                pv = lambda P: self.override.get(P, self.exact(P))
            best = [10 ** 9]

            def rec(rest, acc):
                if acc >= best[0]:
                    return
                if not rest:
                    best[0] = acc; return
                p = rest[0]
                rec(rest[1:], acc + self.a[p])
                for i in range(1, len(rest)):
                    rec(rest[1:i] + rest[i + 1:], acc + pv((p, rest[i])))
            rec(R, 0)
            return best[0]
        raise ValueError(rule)


def outputs(tabs):
    """Blocks and their outputs.  Each output: (block index, name, table, DNF, CNF) where DNF / CNF list the
    sets of prefix channels whose AND (resp. OR) the output is an OR (resp. AND) of."""
    blocks, outs = [], []
    for p in range(N):
        blocks.append((p,))
        outs.append((len(blocks) - 1, f'{p}', tabs[p], [(p,)], [(p,)]))
    for p, q in itertools.combinations(range(N), 2):
        if not KEEPRED and leq(tabs[p], tabs[q]):
            continue
        blocks.append((p, q)); bi = len(blocks) - 1
        outs.append((bi, f'min{p}{q}', tabs[p] & tabs[q], [(p, q)], [(p,), (q,)]))
        outs.append((bi, f'max{p}{q}', tabs[p] | tabs[q], [(p,), (q,)], [(p, q)]))
    return blocks, outs


def wcount(a, b):
    return 3 - cap(a - 4) - cap(b - 4)


def lp_value(pre, rule, want_pairs=False, sides=None):
    tabs = channel_tables(pre)
    top, bot = sides if sides else (Side(tabs), Side([dual(t) for t in tabs]))
    blocks, outs = outputs(tabs)
    A_ = [min(top.bound(S, rule) for S in o[3]) for o in outs]
    B_ = [min(bot.bound(S, rule) for S in o[4]) for o in outs]
    w = [wcount(A_[i], B_[i]) for i in range(len(outs))]
    cover = []
    for i, j in itertools.combinations(range(len(outs)), 2):
        oi, oj = outs[i], outs[j]
        if set(blocks[oi[0]]) & set(blocks[oj[0]]):
            continue
        if not KEEPRED and (leq(oi[2], oj[2]) or leq(oj[2], oi[2])):
            continue
        aj = min(top.bound(S + T, rule) for S in oi[3] for T in oj[3])
        bj = min(bot.bound(S + T, rule) for S in oi[4] for T in oj[4])
        g = w[i] + w[j] - wcount(aj, min(B_[i], B_[j])) - wcount(min(A_[i], A_[j]), bj)
        if g > 0:
            cover.append((i, j, g))
    K = 3; no = len(outs); nv = N + no; A, b = [], []
    for i, j, g in cover:
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
    if min(b) < 0:
        return float('-inf'), cover
    val, _ = fastlp.simplex([1] * N + [0] * no, A, b)
    return val - 9 * K, cover


if __name__ == '__main__':
    d = json.load(open(sys.argv[1])); P = d[sys.argv[2]]
    lo, hi = map(int, sys.argv[3].split(':'))
    rules = sys.argv[4].split(',')
    import collections, time
    worst = {r: [] for r in rules}; fails = collections.Counter(); t0 = time.time()
    for idx in range(lo, min(hi, len(P))):
        vals = [lp_value(P[idx], r)[0] for r in rules]
        for r, v in zip(rules, vals):
            worst[r].append(v)
            if v <= 12 + 1e-6:
                fails[r] += 1
        print(idx, ' '.join(f'{r}={v:.3f}' for r, v in zip(rules, vals)), flush=True)
    n = hi - lo
    for r in rules:
        print(f'rule {r:6s}: prefixes with sum(pi) <= 12: {fails[r]} of {len(worst[r])}; least {min(worst[r]):.3f}')
    print(f'{time.time() - t0:.0f}s')
