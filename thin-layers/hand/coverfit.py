"""Search for a uniform cover formula (efficient-prefixes.md section 7.3).  Variables g(f) per feature
f; cover value of a channel = w(f) - g(f).  Constraints: g(f) + g(f') <= w(f) + w(f') - Wmax(f, f') for
every realized feature pair (cover condition), and sum of g over the 9 channels >= t for every realized
pattern.  Maximize t.  Numeric simplex with constraint generation, then an exact check in Fractions.
usage: featagg_MODE.txt MODE"""
import sys, collections
import numpy as np
from fractions import Fraction as F

lines = open(sys.argv[1]).read().split('\n'); mode = int(sys.argv[2])
Wmax = {}; pats = []
for l in lines:
    p = l.split()
    if not p:
        continue
    if p[0] == 'W':
        a, b, w = map(int, p[1:]); Wmax[(a, b)] = w
    elif p[0] == 'M':
        cnt, S4 = int(p[1]), int(p[2]); fs = tuple(map(int, p[3:])); pats.append((S4, fs))
feats = sorted({a for k in Wmax for a in k})
fi = {f: i for i, f in enumerate(feats)}


def interval(f):
    if mode == 1:
        f //= 3
    return divmod(f, 9)


def wint(f):
    lo, hi = interval(f)
    return max(0, min(hi, 5) - max(lo, 3) + 1)


nf = len(feats); M = 20.0
# variables: h_0..h_{nf-1}, t'   (g = h - M, t = t' - 9M)
pair_rows = []
for (a, b), w in Wmax.items():
    row = np.zeros(nf + 1); row[fi[a]] += 1; row[fi[b]] += 1
    pair_rows.append((row, wint(a) + wint(b) - w + 2 * M))
for i in range(nf):                       # keep bounded
    row = np.zeros(nf + 1); row[i] = 1
    pair_rows.append((row, 3 + 2 * M))


def pat_row(fs):
    row = np.zeros(nf + 1); row[nf] = 1
    for f in fs:
        row[fi[f]] -= 1
    return row


def simplex(c, A, b, tol=1e-9):
    m, n = A.shape
    T = np.hstack([A, np.eye(m), b.reshape(-1, 1)]).astype(float)
    z = np.concatenate([-c, np.zeros(m + 1)]).astype(float)
    basis = list(range(n, n + m))
    for _ in range(20000):
        cols = np.where(z[:-1] < -tol)[0]
        if len(cols) == 0:
            break
        col = cols[0]
        colv = T[:, col]
        mask = colv > tol
        if not mask.any():
            raise ValueError('unbounded')
        ratios = np.full(m, np.inf); ratios[mask] = T[mask, -1] / colv[mask]
        rmin = ratios.min()
        cand = np.where(np.abs(ratios - rmin) <= 1e-12)[0]
        row = min(cand, key=lambda i: basis[i])
        T[row] /= T[row, col]
        others = np.arange(m) != row
        T[others] -= np.outer(T[others, col], T[row])
        z -= z[col] * T[row]
        basis[row] = col
    x = np.zeros(n)
    for i, bv in enumerate(basis):
        if bv < n:
            x[bv] = T[i, -1]
    return z[-1], x


c = np.zeros(nf + 1); c[nf] = 1
active = sorted(range(len(pats)), key=lambda k: pats[k][0])[:50]
for it in range(60):
    rows = [r for r, _ in pair_rows] + [pat_row(pats[k][1]) for k in active]
    rhs = [v for _, v in pair_rows] + [0.0] * len(active)
    val, x = simplex(c, np.array(rows), np.array(rhs))
    g = x[:nf] - M; t = val - 9 * M
    sums = np.array([sum(g[fi[f]] for f in fs) for _, fs in pats])
    viol = np.where(sums < t - 1e-7)[0]
    print(f'iteration {it}: t = {t:.4f}, active patterns {len(active)}, violated {len(viol)}', flush=True)
    if len(viol) == 0:
        break
    worst = viol[np.argsort(sums[viol])][:100]
    active = sorted(set(active) | set(int(k) for k in worst))
# exact check with rounded values
g_exact = {f: F(round(g[fi[f]] * 4), 4) for f in feats}
ok_pairs = all(g_exact[a] + g_exact[b] <= wint(a) + wint(b) - w for (a, b), w in Wmax.items())
tmin = min(sum(g_exact[f] for f in fs) for _, fs in pats)
print('rounded to quarters: cover condition holds:', ok_pairs, '; least margin over all patterns:', tmin, '(13 needed)')
print('table (feature: interval, role, w, g):')
for f in feats:
    lo, hi = interval(f)
    role = 'mMi'[f % 3] if mode == 1 else ''
    print(f'   [{lo},{hi}]{role}: w={wint(f)} g={g_exact[f]}')
