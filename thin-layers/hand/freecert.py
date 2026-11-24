"""Certificates that cover overlap-free gain bounds (computed from the sizes a, b of the two outputs only)
instead of exact gains, except on a chosen set of pairs.  Mode 'free': every pair uses the overlap-free bound.
usage: EXC.json KEY IDX"""
import json, sys, itertools, math
from fractions import Fraction as F
sys.path[:0] = ['.']
import blockcert_fast as bc
import fastlp
from lp import simplex
N = 9; K = 3
def ab(t):
    lo, hi = bc.interval(t); return N - hi, lo + 1
def cap(v): return max(0, min(3, v))
def free_gain(ax, bx, ay, by):
    return (cap(ax + ay - 4) - cap(max(ax, ay) - 4)) + (cap(bx + by - 4) - cap(max(bx, by) - 4))
d = json.load(open(sys.argv[1])); pre = d[sys.argv[2]][int(sys.argv[3])]
tabs, blocks = bc.build(pre)
outs = []
for bi, (chs, ol) in enumerate(blocks):
    for name, t in ol:
        outs.append((bi, name, t, bc.w_of(t)))
abv = [ab(o[2]) for o in outs]
cover = []
for x, y in itertools.combinations(range(len(outs)), 2):
    if set(blocks[outs[x][0]][0]) & set(blocks[outs[y][0]][0]): continue
    if bc.leq(outs[x][2], outs[y][2]) or bc.leq(outs[y][2], outs[x][2]): continue
    g = free_gain(*abv[x], *abv[y])
    if g > 0: cover.append((x, y, g))
no = len(outs); nv = N + no; A, b = [], []
for i, j, g in cover:
    row = [0] * nv; row[N + i] += 1; row[N + j] += 1; A.append(row); b.append(6 - g)
for i in range(no):
    row = [0] * nv; row[N + i] = 1; A.append(row); b.append(3)
for bi, (chs, ol) in enumerate(blocks):
    idx = [k for k, o in enumerate(outs) if o[0] == bi]
    row = [0] * nv; r = sum(outs[k][3] for k in idx) + K * len(chs) - 3 * len(idx)
    for p in chs: row[p] += 1
    for k in idx: row[N + k] -= 1
    A.append(row); b.append(r)
val, x = fastlp.simplex([1] * N + [0] * no, A, b)
print(f'{len(cover)} pairs with positive overlap-free gain; best sum of potentials (float LP) {val - 9 * K:.3f}  (> 12 needed)')
