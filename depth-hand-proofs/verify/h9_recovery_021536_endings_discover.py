#!/usr/bin/env python3
"""Bounded discovery only; exported finite witnesses are checked separately."""
import itertools
import json
import time
from pathlib import Path
from netlib import placements,matchings,run
from h9_feedback_reschedule_extend import prefix_state
from h9_feedback_round4_proof import propagated_order
from h9_feedback_round4_rank_witnesses import lift

ROOT=Path(__file__).parents[1]
FIRST=((0,1),(2,3),(4,5))
SECOND=((0,2),(1,5),(3,6))
TEXT=['12 34 56 78','12 34 78','12 37 48','12 37 48 56',
      '13 24 56 78','13 24 78','13 27 48','13 27 48 56',
      '14 23 56 78','14 23 78','14 27 38','14 27 38 56',
      '17 23 48','17 23 48 56','17 24 38','17 24 38 56',
      '17 28 34','17 28 34 56']
THIRDS=[tuple(sorted(tuple(map(int,e)) for e in s.split())) for s in TEXT]

def main():
    start=time.monotonic();layers=matchings(9)
    seeds=sorted({lift(x) for x in itertools.product((0,1),repeat=9)})
    report=[]
    for number,m in enumerate(THIRDS,1):
        prefix=(FIRST,SECOND,m);forbid=propagated_order(prefix);rows={}
        for p in placements(9,4):
            r=prefix_state(prefix,p);t=len(r['gates'])
            if t in (1,2):
                real=tuple(i for i,s in enumerate(r['state']) if not s)
                rows.setdefault((real,3-t),dict(real=real,demand=3-t,placement=p))
        selected=list(rows.values());candidates=[n for n in layers if not set(n)&forbid]
        def permitted(n,rs):
            return all(sum(a in r['real'] and b in r['real'] for a,b in n)>=r['demand'] for r in rs)
        passing={n for n in candidates if permitted(n,selected)}
        for row in list(selected):
            rest=[r for r in selected if r is not row]
            if {n for n in candidates if permitted(n,rest)}==passing:selected.remove(row)
        endings=[]
        for n in sorted(passing):
            out=[run(prefix+(n,),x) for x in seeds];bad={};required=[]
            for p in range(9):
                vals=[x[p] for x in out]
                if max(vals)-min(vals)>=4:required.append(p)
                for q in range(p+1,9):
                    for opname,op in (('min',min),('max',max)):
                        vals=[op(x[p],x[q]) for x in out]
                        if max(vals)-min(vals)>=4:
                            bad[(p,q)]=opname;break
            allowed=[e for e in itertools.combinations(range(9),2) if e not in bad]
            isolated=[p for p in required if all(p not in e for e in allowed)]
            endings.append(dict(fourth=n,mandatory=required,allowed=allowed,isolated=isolated))
        report.append(dict(case=number,third=m,forbidden=sorted(forbid),all_rows=list(rows.values()),rows=selected,fourths=endings))
        print(number,'demands',len(rows),'selected',len(selected),'N',len(endings),'nonisolated',sum(not r['isolated'] for r in endings),flush=True)
        assert time.monotonic()-start<28
    data=dict(status='DISCOVERY_ONLY',first=FIRST,second=SECOND,cases=report,seconds=time.monotonic()-start)
    dest=ROOT/'results/h9-recovery-021536-endings-discovery.json'
    dest.write_text(json.dumps(data,indent=2)+'\n')
    print('DONE',data['seconds'],flush=True)

if __name__=='__main__':main()
