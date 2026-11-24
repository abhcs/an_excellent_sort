"""Run tokfull (unpruned cross-check) on all prefixes of an exc file; prints a summary line.
usage: EXC.json KEY"""
import json, subprocess, collections, sys, time, os
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(sys.argv[1])); P = d[sys.argv[2]]
lines = [f"{d['n']} {d['depth']} {len(P)}"]
for pre in P:
    lines.append(str(len(pre)))
    for L in pre:
        lines.append(' '.join([str(len(L))] + [f'{i} {j}' for i, j in L]))
t = time.time()
out = subprocess.run([os.path.join(HERE, 'tokfull')], input='\n'.join(lines) + '\n', capture_output=True, text=True).stdout
rows = [list(map(int, l.split())) for l in out.split('\n') if l.strip()]
print(sys.argv[1], len(rows), 'prefixes; pairs checked', sum(r[2] for r in rows), '; least max_k |T_5(k)| histogram',
      dict(collections.Counter(r[3] for r in rows)), f'({time.time() - t:.0f}s)')
