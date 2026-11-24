"""Fractional vertex cover bound for every (prefix, non-redundant layer 4): S4 - tau* >= 13 ?
Writes per-case (idx, layer-4 index, S4, nu, tau*) for cases with S4 - tau* <= 14, and a summary.
usage: EXC.json KEY OUT.jsonl"""
import json, subprocess, sys, time, collections, itertools
from lp import fractional_cover
d = json.load(open(sys.argv[1])); P = d[sys.argv[2]]
lines = [f"9 7 {len(P)}"] + sum((['3'] + [' '.join([str(len(L))] + [f'{i} {j}' for i, j in L]) for L in pre] for pre in P), [])
t = time.time()
proc = subprocess.Popen(['./coverdump'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, env={'LIMIT': '99'})
proc.stdin.write('\n'.join(lines) + '\n'); proc.stdin.close()
pairs = list(itertools.combinations(range(9), 2))
summ = collections.Counter(); worst = collections.defaultdict(lambda: 99); n = 0
with open(sys.argv[3], 'w') as fo:
    for line in proc.stdout:
        if not line.startswith('C '):
            continue
        r = line.split(); idx, ai, S4, nu = map(int, r[1:5]); ws = list(map(int, r[5:]))
        w = {p: x for p, x in zip(pairs, ws) if x}
        tau, _ = fractional_cover(9, w)
        n += 1
        summ[(S4 - nu, float(tau - nu))] += 1
        worst[idx] = min(worst[idx], float(S4 - tau))
        if S4 - tau <= 14:
            fo.write(json.dumps([idx, ai, S4, nu, float(tau)]) + '\n')
print(f'{n} cases ({time.time()-t:.0f}s); (S4 - nu, gap) counts:', sorted(summ.items()))
print('least S4 - tau* per prefix:', sorted(collections.Counter(worst.values()).items()))
