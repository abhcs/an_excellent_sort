#!/usr/bin/env python3
"""Single-class discovery of short fourth-layer demand families."""
import itertools
import json
import time
from pathlib import Path
from netlib import placements, matchings, run
from h9_feedback_round5_probe import FIRST, SECOND, norm
from h9_feedback_reschedule_extend import prefix_state
from h9_feedback_round4_proof import propagated_order


def main():
    start=time.monotonic();root=Path(__file__).parents[1]
    cases=json.loads((root/'results/h9-feedback-round5-probe.json').read_text())['cases']
    layers=matchings(9);report=[]
    for case in cases:
        M=norm(case['third']);prefix=(FIRST,SECOND,M)
        ordered=propagated_order(prefix)
        image={tuple(run(prefix,x)) for x in itertools.product((0,1),repeat=9)}
        exact={(a,b) for a,b in itertools.combinations(range(9),2) if all(x[a]<=x[b] for x in image)}
        unique={}
        for p in placements(9,4):
            r=prefix_state(prefix,p);total=len(r['gates'])
            if total in (1,2):
                real=tuple(i for i,s in enumerate(r['state']) if not s)
                key=(real,3-total)
                unique.setdefault(key,dict(placement=p,real=real,demand=3-total))
        rows=list(unique.values())
        passed=[n for n in layers if not set(n)&ordered and all(sum(a in row['real'] and b in row['real'] for a,b in n)>=row['demand'] for row in rows)]
        desired={norm(r['fourth']) for r in case['fourths']}
        print('CASE',case['case'],'M',M,'order extra',sorted(exact-ordered),'rows',len(rows),'five-only',len(passed),'old',len(desired))
        # Greedy deletion gives a small sufficient subset for these exact five-real constraints.
        selected=rows[:]
        candidates=[n for n in layers if not set(n)&ordered]
        for row in rows:
            rest=[r for r in selected if r is not row]
            if {n for n in candidates if all(sum(a in r['real'] and b in r['real'] for a,b in n)>=r['demand'] for r in rest)}==set(passed):
                selected.remove(row)
        for row in selected:print(' ',row)
        print(' N',passed)
        report.append(dict(case=case['case'],third=M,forbidden=sorted(ordered),extra_order=sorted(exact-ordered),rows=selected,fourths=passed,old_fourths=sorted(desired)))
    out=dict(status='DISCOVERY_ONLY',cases=report,elapsed_seconds=time.monotonic()-start)
    (root/'results/h9-feedback-round5-fourths.json').write_text(json.dumps(out,indent=2)+'\n')
    print('DONE',out['elapsed_seconds'])


if __name__=='__main__':main()
