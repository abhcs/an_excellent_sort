"""Shapes of optimal strategies, from tokwin_v's optimal (L4, best L5) pairs.  For each comparator: top
units (window ranks removed at its min end) and bottom units (at its max end); layer-5 inputs typed as
m (min end of an L4 comparator), M (max end) or i (idle in L4).  usage: EXC.json KEY [MAXPREFIXES]"""
import json, sys, os, subprocess, collections
sys.path[:0] = ['.']
from ranks import states, rank_sets, states_step
d = json.load(open(sys.argv[1])); P = d[sys.argv[2]]
if len(sys.argv) > 3:
    P = P[:int(sys.argv[3])]
n = d['n']; W = set(range(n // 2 - 1, n // 2 + 2)); Wmask = sum(1 << k for k in W)


def ivs(X):
    return [(min(r), max(r)) for r in rank_sets(n, X)]


def units(ivb, iva, u, v):
    both = W & set(range(ivb[u][0], ivb[u][1] + 1)) & set(range(ivb[v][0], ivb[v][1] + 1))
    return sum(1 for k in both if k > iva[u][1]), sum(1 for k in both if k < iva[v][0])


def parse(tok):
    return [tuple(map(int, c.split('-'))) for c in tok]


env = dict(os.environ, TOKWIN_VERBOSE='1')
shape = collections.Counter(); kinds5 = collections.Counter(); per_layer = collections.Counter()
for pre in P:
    inp = f'{n} 7 1\n3\n' + '\n'.join(' '.join([str(len(L))] + [f'{i} {j}' for i, j in L]) for L in pre) + '\n'
    out = subprocess.run(['./tokwin_v', format(Wmask, 'x')], input=inp, capture_output=True, text=True, env=env).stdout
    rows = [l for l in out.split('\n') if l.startswith('A')]
    best = min(int(l.split('S5min ')[1].split()[0]) for l in rows)
    X3 = states(n, pre); iv3 = ivs(X3)
    for l in rows:
        if int(l.split('S5min ')[1].split()[0]) != best:
            continue
        A = parse(l.split('|')[0].split()[1:]); B = parse(l.split('| B')[1].split()) if '| B' in l else []
        X4 = states_step(n, X3, A); iv4 = ivs(X4); X5 = states_step(n, X4, B); iv5 = ivs(X5)
        kind = {c: 'i' for c in range(n)}
        for p, q in A:
            kind[p], kind[q] = 'm', 'M'
        u4 = sorted(units(iv3, iv4, p, q) for p, q in A)
        u5 = sorted((''.join(sorted(kind[u] + kind[v])), units(iv4, iv5, u, v)) for u, v in B)
        shape[(tuple(u4), tuple(u5))] += 1
        per_layer[(sum(a + b for a, b in u4), sum(a + b for _, (a, b) in u5))] += 1
        for k, uv in u5:
            kinds5[(k, uv)] += 1
print('removal (layer 4, layer 5) over optimal pairs:', sorted(per_layer.items()))
print('layer-5 comparator kinds -> (top, bottom) units:', sorted(kinds5.items(), key=lambda kv: -kv[1])[:16])
for (u4, u5), c in shape.most_common(8):
    print(f'{c:3d}x  L4 {list(u4)}  L5 {list(u5)}')
