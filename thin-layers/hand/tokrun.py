"""Feed prefixes from a hand/exc_*.json file (key 'left' or 'exceptional') to tokcore and summarise.
usage: EXC.json KEY [MAXNODES] [FIRST:LAST]"""
import json, subprocess, sys, os, collections
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(sys.argv[1]))
key = sys.argv[2]
maxn = sys.argv[3] if len(sys.argv) > 3 else '0'
P = d[key]
if len(sys.argv) > 4:
    a, b = map(int, sys.argv[4].split(':'))
    P = P[a:b]
lines = [f"{d['n']} {d['depth']} {len(P)}"]
for pre in P:
    lines.append(str(len(pre)))
    for L in pre:
        lines.append(' '.join([str(len(L))] + [f'{i} {j}' for i, j in L]))
out = subprocess.run([os.path.join(HERE, 'tokcore'), maxn] + sys.argv[5:], input='\n'.join(lines) + '\n',
                     capture_output=True, text=True).stdout.split('\n')
rows = [l.split() for l in out if l.strip()]
p = len(P[0])
depth = d['depth']
print(f"{len(rows)} prefixes of E3({d['n']},{d['a']}) at depth {depth} ({key})")
for t in range(p + 1, depth + 1):
    col = [int(r[1 + t - p - 1]) for r in rows]
    z = sum(1 for c in col if c == 0)
    print(f'  after layer {t}: prefixes with no surviving node {z}/{len(rows)}; nodes total {sum(col)}, max {max(col)}')
print('  outcomes:', dict(collections.Counter(r[-1] for r in rows)))
json.dump(rows, open(os.path.splitext(sys.argv[1])[0] + f'_tok_{key}.json', 'w'))
