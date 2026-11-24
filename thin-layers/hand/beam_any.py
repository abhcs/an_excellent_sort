"""Run tokbeam.c (beam search for continuations that pass the token cone at layer D-2) on prefixes from a
JSON file, in parallel chunks.  usage: beam_any.py FILE.json KEY N D B C TEMP SEED FIRST:LAST JOBS OUT.log"""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
f, key, n, D, B, C, T, seed, rng, jobs, outp = sys.argv[1:12]
P = json.load(open(f))[key]
lo, hi = map(int, rng.split(':')); idxs = list(range(lo, min(hi, len(P))))
J = int(jobs); chunks = [idxs[i::J] for i in range(J)]


def run(chunk):
    lines = [f'{n} {D} {len(chunk)}']
    for i in chunk:
        pre = P[i]; lines.append(str(len(pre)))
        for L in pre:
            lines.append(' '.join([str(len(L))] + [f'{a} {b}' for a, b in L]))
    r = subprocess.run([os.path.join(HERE, 'tokbeam'), B, C, T, seed], input='\n'.join(lines) + '\n', capture_output=True, text=True)
    out = r.stdout.splitlines(); res = []
    k = 0
    for line in out:
        if line.startswith('  layers:'):
            res[-1] = (res[-1][0], res[-1][1] + ' |' + line[9:])
        else:
            parts = line.split(' ', 1); res.append((chunk[int(parts[0])], parts[1]))
    return res


with ThreadPoolExecutor(J) as ex:
    allres = [r for rs in ex.map(run, chunks) for r in rs]
allres.sort()
with open(outp, 'w') as fo:
    for i, s in allres:
        fo.write(f'{i} {s}\n')
npass = sum(1 for _, s in allres if 'PASSES' in s)
print(f'{len(allres)} prefixes, {npass} pass the cone at layer {int(D) - 2}')
