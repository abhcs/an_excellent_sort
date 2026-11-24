"""Exact token search (tokcore.c) on many prefixes in parallel, one process per prefix, with timing.
Env: TOKBIN (default tokcore; tokcore2 adds TOK_MATCH=1, the merge-matching filter), RESUME=1 (append to OUT
and skip indices already in it), ORDER=size (largest classes first, using the file's 'size' list).
usage: tokcore_par.py FILE.json KEY N D MAXNODES JOBS OUT.jsonl [IDX...|FIRST:LAST]"""
import json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
f, key, n, D, maxn, jobs, outp = sys.argv[1:8]
DATA = json.load(open(f)); P = DATA[key]
sel = sys.argv[8:]
if len(sel) == 1 and ':' in sel[0]:
    a, b = map(int, sel[0].split(':')); idxs = list(range(a, min(b, len(P))))
elif sel:
    idxs = list(map(int, sel))
else:
    idxs = list(range(len(P)))


if os.environ.get('ORDER') == 'size' and 'size' in DATA:
    idxs.sort(key=lambda i: -DATA['size'][i])
done = set()
if os.environ.get('RESUME') == '1' and os.path.exists(outp):
    done = {json.loads(l)['idx'] for l in open(outp) if l.strip()}
idxs = [i for i in idxs if i not in done]
BIN = os.path.join(HERE, os.environ.get('TOKBIN', 'tokcore'))


def run(i):
    pre = P[i]
    lines = [f'{n} {D} 1', str(len(pre))] + [' '.join([str(len(L))] + [f'{a} {b}' for a, b in L]) for L in pre]
    t = time.time()
    r = subprocess.run([BIN, maxn], input='\n'.join(lines) + '\n', capture_output=True, text=True)
    row = r.stdout.split()
    k = row.index('pruned') if 'pruned' in row else len(row)
    return {'idx': i, 'nodes': list(map(int, row[1:k - 1])), 'outcome': row[k - 1], 'seconds': round(time.time() - t, 2)}


with ThreadPoolExecutor(int(jobs)) as ex, open(outp, 'a' if done or os.environ.get('RESUME') == '1' else 'w') as fo:
    for res in ex.map(run, idxs):
        fo.write(json.dumps(res) + '\n'); fo.flush()
