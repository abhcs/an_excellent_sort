"""Cascade of gain rules over a range of prefixes: 'pair' first; where it does not reach sum(pi) > 12,
'pairw'; where that fails too, 'exact'.  One line per prefix.  usage: EXC.json KEY FIRST:LAST"""
import json, sys, os
os.environ.setdefault('KEEPRED', '1')
sys.path[:0] = ['.']
import gainrules as gr
d = json.load(open(sys.argv[1])); P = d[sys.argv[2]]
lo, hi = map(int, sys.argv[3].split(':'))
RULES = sys.argv[4].split(',') if len(sys.argv) > 4 else ['pair', 'pairw', 'exact']
for idx in range(lo, min(hi, len(P))):
    out = []
    for rule in RULES:
        v, _ = gr.lp_value(P[idx], rule)
        out.append(f'{rule}={v:.3f}')
        if v > 12 + 1e-6:
            break
    print(idx, ' '.join(out), flush=True)
