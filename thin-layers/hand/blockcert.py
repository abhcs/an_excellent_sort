"""Block-separable certificates for the window lemma (W) on one prefix (efficient-prefixes.md section 7.5).

Blocks are the possible layer-4 comparators (p, q) (non-redundant after the prefix) and idle channels.
Every block output x gets a value c(x) >= 0; every prefix channel p a potential pi(p).  Conditions:
  (cover)  c(x) + c(y) >= gain(x, y) for outputs x, y of disjoint blocks, whenever the layer-5
           comparator (x, y) is non-redundant;  gain = window incidences removed by that comparator;
  (block)  pi(p) + pi(q) <= w(min end) + w(max end) - c(min end) - c(max end)  for each block (p, q);
  (idle)   pi(p) <= w(p) - c(p).
Then for any layers 4, 5:  S_5 = S_4 - sum of layer-5 gains >= S_4 - sum c >= sum pi.  So sum pi >= 13
proves the prefix.  Everything is exact: channel functions are truth tables over the 2^9 inputs, and
a function's rank interval is [n-1-(greatest weight with f = 0), n-(least weight with f = 1)].
usage: blockcert.py EXC.json KEY IDX [OUT.json]"""
import json, sys, itertools
from fractions import Fraction as F
from lp import simplex

N = 9; W = (3, 4, 5); FULL = (1 << N) - 1
POP = [bin(x).count('1') for x in range(1 << N)]


def channel_tables(pre):
    tabs = [0] * N                       # tabs[c] = bitmask over inputs x (bit x set iff channel c is 1)
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


def interval(tab):
    ones = [POP[x] for x in range(1 << N) if (tab >> x) & 1]
    zeros = [POP[x] for x in range(1 << N) if not (tab >> x) & 1]
    return N - 1 - max(zeros), N - min(ones)


def w_of(tab):
    lo, hi = interval(tab)
    return max(0, min(hi, W[-1]) - max(lo, W[0]) + 1)


def leq(tx, ty):                         # f_x <= f_y everywhere: comparator (x, y) never swaps
    return tx & ~ty == 0


def build(pre):
    tabs = channel_tables(pre)
    blocks = []                          # (channels, [(name, table)])
    for p in range(N):
        blocks.append(((p,), [(f'{p}', tabs[p])]))
    for p, q in itertools.combinations(range(N), 2):
        if leq(tabs[p], tabs[q]):        # redundant after the prefix (p <= q always)
            continue
        blocks.append(((p, q), [(f'min{p}{q}', tabs[p] & tabs[q]), (f'max{p}{q}', tabs[p] | tabs[q])]))
    return tabs, blocks


def certify(pre):
    tabs, blocks = build(pre)
    outs = []                            # (block index, name, table, w)
    for bi, (chs, ol) in enumerate(blocks):
        for name, t in ol:
            outs.append((bi, name, t, w_of(t)))
    cover = []                           # (i, j, gain) over outputs of disjoint blocks
    for i, j in itertools.combinations(range(len(outs)), 2):
        bi, _, ti, wi = outs[i]; bj, _, tj, wj = outs[j]
        if set(blocks[bi][0]) & set(blocks[bj][0]):
            continue
        if leq(ti, tj) or leq(tj, ti):  # the layer-5 comparator would never swap
            continue
        g = wi + wj - w_of(ti & tj) - w_of(ti | tj)
        if g > 0:
            cover.append((i, j, g))
    # LP in standard form: variables sigma_p = pi_p + K (9), d_x = 3 - c_x (one per output); all >= 0
    K = 3; no = len(outs); nv = N + no
    A, b = [], []
    for i, j, g in cover:                # c_i + c_j >= g  <=>  d_i + d_j <= 6 - g
        row = [0] * nv; row[N + i] += 1; row[N + j] += 1; A.append(row); b.append(6 - g)
    for i in range(no):                  # c_i >= 0  <=>  d_i <= 3
        row = [0] * nv; row[N + i] = 1; A.append(row); b.append(3)
    for bi, (chs, ol) in enumerate(blocks):
        idx = [k for k, o in enumerate(outs) if o[0] == bi]
        row = [0] * nv
        for p in chs:
            row[p] += 1
        rhs = sum(outs[k][3] for k in idx) + K * len(chs)
        for k in idx:                    # - c_k = d_k - 3
            row[N + k] -= 1
            rhs -= 3
        A.append(row); b.append(rhs)
    assert min(b) >= 0
    obj = [1] * N + [0] * no
    val, x, _ = simplex(obj, A, b)
    pi = [x[p] - K for p in range(N)]
    c = [3 - x[N + k] for k in range(no)]
    return {'pi': pi, 'c': c, 'outs': outs, 'blocks': blocks, 'cover': cover, 'tabs': tabs, 'value': sum(pi)}


def check(cert):
    """Exact re-check of every inequality of a certificate (independent of the LP)."""
    outs, blocks, c, pi = cert['outs'], cert['blocks'], cert['c'], cert['pi']
    for i, j in itertools.combinations(range(len(outs)), 2):
        bi, _, ti, wi = outs[i]; bj, _, tj, wj = outs[j]
        if set(blocks[bi][0]) & set(blocks[bj][0]) or leq(ti, tj) or leq(tj, ti):
            continue
        g = wi + wj - w_of(ti & tj) - w_of(ti | tj)
        if c[i] + c[j] < g:
            return False, ('cover', outs[i][1], outs[j][1])
    if min(c) < 0:
        return False, 'negative c'
    for bi, (chs, ol) in enumerate(blocks):
        idx = [k for k, o in enumerate(outs) if o[0] == bi]
        if sum(pi[p] for p in chs) > sum(outs[k][3] - c[k] for k in idx):
            return False, ('block', chs)
    return True, sum(pi)


if __name__ == '__main__':
    d = json.load(open(sys.argv[1])); pre = d[sys.argv[2]][int(sys.argv[3])]
    cert = certify(pre)
    ok, val = check(cert)
    print(f'prefix {pre}: {len(cert["blocks"])} blocks, {len(cert["outs"])} outputs, {len(cert["cover"])} cover pairs with positive gain')
    print(f'best sum of potentials: {cert["value"]} (13 needed); exact re-check: {ok}, {val}')
    print('potentials pi:', [str(v) for v in cert['pi']])
    nz = [(o[1], str(v)) for o, v in zip(cert['outs'], cert['c']) if v]
    print(f'nonzero cover values ({len(nz)} of {len(cert["outs"])}):', nz)
    if len(sys.argv) > 4:
        json.dump({'prefix': pre, 'pi': [str(v) for v in cert['pi']],
                   'c': {o[1]: str(v) for o, v in zip(cert['outs'], cert['c'])}}, open(sys.argv[4], 'w'), indent=1)
