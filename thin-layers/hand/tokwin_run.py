"""Window sums (tokwin.c) over a prefix file: least sum over the window after one and after two more
layers, per prefix.  usage: FILE.json KEY WMASK OUT.json"""
import json, os, subprocess, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(sys.argv[1])); P = d[sys.argv[2]]; W = sys.argv[3]
lines = [f"{d['n']} {d['depth']} {len(P)}"]
for pre in P:
    lines.append(str(len(pre)))
    for L in pre:
        lines.append(' '.join([str(len(L))] + [f'{i} {j}' for i, j in L]))
out = subprocess.run([os.path.join(HERE, 'tokwin'), W], input='\n'.join(lines) + '\n', capture_output=True, text=True).stdout
rows = [list(map(int, l.split())) for l in out.split('\n') if l.strip()]
json.dump(rows, open(sys.argv[4], 'w'))
print(len(rows), 'prefixes; least window sum after the next layer:', sorted(collections.Counter(r[2] for r in rows).items()))
print('   least window sum after two layers:', sorted(collections.Counter(r[4] for r in rows).items()))
print('   least max over the window after two layers:', sorted(collections.Counter(r[5] for r in rows).items()))
