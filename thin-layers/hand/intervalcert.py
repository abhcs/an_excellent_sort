"""Within one prefix: is there a block-separable certificate whose cover value depends only on the output's
interval (and on whether it is an idle channel)?  LP over the table c[interval, idle?] and potentials pi.
usage: EXC.json KEY IDX"""
import json, sys, itertools
from fractions import Fraction as F
sys.path[:0] = ['.']
import blockcert_fast as bc
import fastlp
from lp import simplex
import math

d = json.load(open(sys.argv[1])); pre = d[sys.argv[2]][int(sys.argv[3])]
cert = bc.certify(pre); outs = cert['outs']; blocks = cert['blocks']; cover = cert['cover']
feat = []
for (bi, name, t, w) in outs:
    feat.append((bc.interval(t), len(blocks[bi][0]) == 1))
keys = sorted(set(feat)); ki = {k: i for i, k in enumerate(keys)}
nk = len(keys); N = 9; K = 3
# variables: sigma_p (9), d_k = 3 - c_k (nk); cover: d_i + d_j <= 6 - g (merge duplicates by feature)
best = {}
for i, j, g in cover:
    a, b = sorted((ki[feat[i]], ki[feat[j]]))
    best[(a, b)] = max(best.get((a, b), 0), g)
A, rhs = [], []
for (a, b), g in best.items():
    row = [0] * (N + nk); row[N + a] += 1; row[N + b] += 1; A.append(row); rhs.append(6 - g)
for k in range(nk):
    row = [0] * (N + nk); row[N + k] = 1; A.append(row); rhs.append(3)
for bi, (chs, ol) in enumerate(blocks):
    idx = [k for k, o in enumerate(outs) if o[0] == bi]
    row = [0] * (N + nk); r = sum(outs[k][3] for k in idx) + K * len(chs) - 3 * len(idx)
    for p in chs: row[p] += 1
    for k in idx: row[N + ki[feat[k]]] -= 1
    A.append(row); rhs.append(r)
val, x = fastlp.simplex([1] * N + [0] * nk, A, rhs)
c = {k: min(F(3), max(F(0), F(math.ceil((3 - x[N + ki[k]]) * 12 - 1e-7), 12))) for k in keys}
ok_cover = all(c[feat[i]] + c[feat[j]] >= g for i, j, g in cover)
A2, b2 = [], []
for bi, (chs, ol) in enumerate(blocks):
    idx = [k for k, o in enumerate(outs) if o[0] == bi]
    row = [0] * N
    for p in chs: row[p] += 1
    A2.append(row); b2.append(sum(outs[k][3] - c[feat[k]] for k in idx) + K * len(chs))
v2, s2, _ = simplex([1] * N, A2, b2)
pi = [s2[p] - K for p in range(N)]
print(f'{len(keys)} (interval, idle) classes; cover holds: {ok_cover}; sum of potentials {sum(pi)} = {float(sum(pi)):.3f} (> 12 needed)')
print('table c[interval, idle]:', {f'{k[0]}{"i" if k[1] else ""}': str(v) for k, v in c.items()})
print('potentials:', [str(v) for v in pi])
