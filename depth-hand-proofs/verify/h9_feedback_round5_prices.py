#!/usr/bin/env python3
"""Two bounded integer-price probes; results are discovery only."""
import itertools
import json
import time
from pathlib import Path
import z3


def main():
    start=time.monotonic();root=Path(__file__).parents[1]
    cases=json.loads((root/'results/h9-feedback-round5-fourths.json').read_text())['cases']
    report=[]
    for case in cases:
        if case['case'] not in (7,9):continue
        rows=case['rows'];p=[z3.Int(f'p{i}') for i in range(9)]
        w=[z3.Int(f'w{i}') for i in range(len(rows))];g=z3.Int('g')
        solver=z3.Solver();solver.set(timeout=1500)
        solver.add([v>=0 for v in p+w+[g]])
        solver.add([v<=20 for v in p+w+[g]])
        solver.add(z3.Sum(w)<=20)
        for a,b in itertools.combinations(range(9),2):
            if [a,b] in case['forbidden']:continue
            weight=z3.Sum([v for v,r in zip(w,rows) if a in r['real'] and b in r['real']])
            solver.add(weight<=p[a]+p[b]+g)
        demand=z3.Sum([v*r['demand'] for v,r in zip(w,rows)])
        solver.add(z3.Sum(p)+4*g<demand)
        answer=solver.check();record=dict(case=case['case'],status=str(answer),timeout_ms=1500)
        if answer==z3.sat:
            m=solver.model();record.update(prices=[m.eval(v).as_long() for v in p],weights=[m.eval(v).as_long() for v in w],gate=m.eval(g).as_long())
        report.append(record);print(record,flush=True)
    (root/'results/h9-feedback-round5-prices.json').write_text(json.dumps(dict(status='DISCOVERY_ONLY',records=report,elapsed_seconds=time.monotonic()-start),indent=2)+'\n')


if __name__=='__main__':main()
