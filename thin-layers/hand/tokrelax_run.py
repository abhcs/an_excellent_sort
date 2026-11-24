"""Run tokrelax on hand/exc_*.json prefixes.  usage: EXC.json KEY MODE [OUTMASK] [FIRST:LAST]"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(sys.argv[1])); key = sys.argv[2]; mode = sys.argv[3]
mask = sys.argv[4] if len(sys.argv) > 4 else 'ffff'
P = d[key]
if len(sys.argv) > 5:
    a, b = map(int, sys.argv[5].split(':')); P = P[a:b]
lines = [f"{d['n']} {d['depth']} {len(P)}"]
for pre in P:
    lines.append(str(len(pre)))
    for L in pre:
        lines.append(' '.join([str(len(L))] + [f'{i} {j}' for i, j in L]))
out = subprocess.run([os.path.join(HERE, 'tokrelax'), mode, mask], input='\n'.join(lines) + '\n', capture_output=True, text=True).stdout
rows = [list(map(int, l.split())) for l in out.split('\n') if l.strip()]
p = len(P[0])
for t in range(p + 1, d['depth'] + 1):
    col = [r[1 + t - p - 1] for r in rows]
    print(f'  after layer {t}: prefixes with no surviving node {sum(1 for c in col if c == 0)}/{len(rows)}; nodes total {sum(col)}')
