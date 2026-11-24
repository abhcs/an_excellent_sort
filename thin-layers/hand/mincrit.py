"""Fewest layer-5 pairs whose gain must be computed exactly (from witness unions); all other pairs use the
overlap-free bound from the sizes (a, b) of the two outputs.  Greedy batch relaxation keeping the block-
separable certificate's sum of potentials > 12.  usage: EXC.json KEY IDX"""
import json, sys, itertools, random
sys.path[:0] = ['.']
import blockcert_fast as bc
import fastlp
N = 9; K = 3
def ab(t):
    lo, hi = bc.interval(t); return N - hi, lo + 1
def cap(v): return max(0, min(3, v))
def free_gain(ax, bx, ay, by):
    return (cap(ax + ay - 4) - cap(max(ax, ay) - 4)) + (cap(bx + by - 4) - cap(max(bx, by) - 4))
d = json.load(open(sys.argv[1])); pre = d[sys.argv[2]][int(sys.argv[3])]
tabs, blocks = bc.build(pre)
outs = [(bi, name, t, bc.w_of(t)) for bi, (chs, ol) in enumerate(blocks) for name, t in ol]
abv = [ab(o[2]) for o in outs]
pairs = []
for x, y in itertools.combinations(range(len(outs)), 2):
    if set(blocks[outs[x][0]][0]) & set(blocks[outs[y][0]][0]): continue
    if bc.leq(outs[x][2], outs[y][2]) or bc.leq(outs[y][2], outs[x][2]): continue
    ex = outs[x][3] + outs[y][3] - bc.w_of(outs[x][2] & outs[y][2]) - bc.w_of(outs[x][2] | outs[y][2])
    fr = free_gain(*abv[x], *abv[y])
    pairs.append((x, y, ex, fr))
cand = [k for k, p in enumerate(pairs) if p[3] > p[2]]


def solve(exact_set):
    no = len(outs); nv = N + no; A, b = [], []
    for k, (x, y, ex, fr) in enumerate(pairs):
        g = ex if k in exact_set else fr
        if g <= 0: continue
        row = [0] * nv; row[N + x] += 1; row[N + y] += 1; A.append(row); b.append(6 - g)
    for i in range(no):
        row = [0] * nv; row[N + i] = 1; A.append(row); b.append(3)
    for bi, (chs, ol) in enumerate(blocks):
        idx = [k for k, o in enumerate(outs) if o[0] == bi]
        row = [0] * nv; r = sum(outs[k][3] for k in idx) + K * len(chs) - 3 * len(idx)
        for p in chs: row[p] += 1
        for k in idx: row[N + k] -= 1
        A.append(row); b.append(r)
    val, _ = fastlp.simplex([1] * N + [0] * no, A, b)
    return val - 9 * K


E = set(cand)
print(f'{len(pairs)} layer-5 pairs; {len(cand)} where the exact gain is below the overlap-free bound; LP with all exact: {solve(E):.3f}')
random.seed(0)
order = cand[:]; random.shuffle(order)
batch = 64
while batch >= 1:
    i = 0
    while i < len(order):
        chunk = [k for k in order[i:i + batch] if k in E]
        if chunk:
            trial = E - set(chunk)
            if solve(trial) > 12 + 1e-6:
                E = trial
        i += batch
    batch //= 2
print(f'pairs still needing exact unions after greedy relaxation: {len(E)}  (LP value {solve(E):.3f})')
