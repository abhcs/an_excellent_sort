"""Beam search (tokbeam.c) for token-passing continuations at 14 channels, depth 9.
usage: tokbeam_run.py WHICH B C TEMP SEED [COUNT]   WHICH = feasible | sparse | feasible-own"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, '..')]
from tokpot_run import feasible14, run
from phi import residual_network
import itertools

which, B, C, T, seed = sys.argv[1:6]
cnt = int(sys.argv[6]) if len(sys.argv) > 6 else 10
if which == 'sparse':
    c0 = json.load(open(os.path.join(HERE, 'case0_exceptional.json')))
    P = [[c0['L1'], c0['L2'], L3] for L3 in c0['L3s']][:cnt]
else:
    P = feasible14()[:cnt]
lines = [f'14 9 {len(P)}']
for pre in P:
    lines.append(str(len(pre)))
    for L in pre:
        lines.append(' '.join([str(len(L))] + [f'{i} {j}' for i, j in L]))
r = subprocess.run([os.path.join(HERE, 'tokbeam'), B, C, T, seed] + sys.argv[7:], input='\n'.join(lines) + '\n', capture_output=True, text=True)
print(r.stdout)
