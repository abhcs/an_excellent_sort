"""Split a leftover prefix on its fourth layer and try the hand certificates of prefix_cert.py (infinities
+ D / P7 / SS7 rules) on each 4-layer prefix (3 free layers left at depth 7).  Counts how many fourth
layers get a hand certificate.  usage: EXC.json KEY IDX [KMAX]"""
import json, sys, time, collections, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, '..'), HERE]
from prefix_cert import certify
from ranks import states

d = json.load(open(sys.argv[1])); pre = d[sys.argv[2]][int(sys.argv[3])]
kmax = int(sys.argv[4]) if len(sys.argv) > 4 else 3
n = d['n']


def matchings(chs):
    if not chs:
        yield []
        return
    c, rest = chs[0], chs[1:]
    yield from matchings(rest)
    for i, j in enumerate(rest):
        for m in matchings(rest[:i] + rest[i + 1:]):
            yield [(c, j)] + m


X = states(n, pre)
t = time.time()
stat = collections.Counter()
for L4 in matchings(list(range(n))):
    if not L4 or not all(any((x >> i) & 1 and not (x >> j) & 1 for x in X) for i, j in L4):
        continue
    c = certify(n, d['depth'], 4, 4, [list(map(tuple, L)) for L in pre] + [L4], kmax=kmax)
    stat[c[0] if c else 'none'] += 1
print(f'prefix {sys.argv[3]}: fourth layers by certificate {dict(stat)} ({time.time() - t:.0f}s)')
