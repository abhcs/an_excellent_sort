"""For each prefix: the layers 4 (non-redundant) for which exact intervals after layer 4 plus the
overlap-free calculus for layer 5 do NOT refute it at layer 5 (tokrelax.c, mode 0, on prefix+L4).
usage: EXC.json KEY"""
import json, subprocess, sys, collections
sys.path[:0] = ['.']
from ranks import states
d = json.load(open(sys.argv[1])); P = d[sys.argv[2]]; n = d['n']


def matchings(chs):
    if not chs:
        yield []
        return
    c, rest = chs[0], chs[1:]
    yield from matchings(rest)
    for i, j in enumerate(rest):
        for m in matchings(rest[:i] + rest[i + 1:]):
            yield [(c, j)] + m


ALL = list(matchings(list(range(n))))
lines, owner = [], []
for pi, pre in enumerate(P):
    X = states(n, pre)
    for L4 in ALL:
        if L4 and all(any((x >> i) & 1 and not (x >> j) & 1 for x in X) for i, j in L4):
            owner.append(pi)
            Q = pre + [L4]
            lines.append(str(len(Q)))
            for L in Q:
                lines.append(' '.join([str(len(L))] + [f'{i} {j}' for i, j in L]))
out = subprocess.run(['./tokrelax', '0', 'ffff'], input=f'{n} {d["depth"]} {len(owner)}\n' + '\n'.join(lines) + '\n',
                     capture_output=True, text=True).stdout
rows = [list(map(int, l.split())) for l in out.split('\n') if l.strip()]
fail = collections.Counter(owner[r[0]] for r in rows if r[1] > 0)
print(f'{len(P)} prefixes, {len(rows)} (prefix, layer 4) pairs; hybrid bound fails for {sum(fail.values())} pairs '
      f'({100 * sum(fail.values()) / len(rows):.2f}%), in {len(fail)} prefixes')
print('failing layers 4 per affected prefix:', sorted(collections.Counter(fail.values()).items()))
