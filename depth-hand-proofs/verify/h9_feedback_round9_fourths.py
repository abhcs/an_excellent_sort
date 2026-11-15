#!/usr/bin/env python3
"""Single-class finite feedback for six third-layer representatives."""
import itertools
import json
import time
from pathlib import Path
from netlib import placements,matchings,run
from h9_feedback_round9_probe import FIRST,SECOND
from h9_feedback_round4_proof import normalized as norm
from h9_feedback_reschedule_extend import prefix_state
from h9_feedback_round4_proof import propagated_order
from h9_feedback_round4_rank_witnesses import lift


def canonical(m):
    pi=(4,3,5,1,0,2,7,6,8)
    return min(norm(m),norm((pi[a],pi[b])for a,b in m))


def main():
    start=time.monotonic();root=Path(__file__).parents[1]
    source=next(e for e in json.loads((root/'results/h9-feedback-next-fourths-combined.json').read_text()) if e['label']=='(0,3)(1,4)(6,7)')
    thirds=sorted({canonical(row['third']) for row in source['rows']});layers=matchings(9)
    seeds=sorted({lift(x) for x in itertools.product((0,1),repeat=9)});report=[]
    for number,m in enumerate(thirds,1):
        prefix=(FIRST,SECOND,m);forbid=propagated_order(prefix);rows={}
        states=[run(prefix,x) for x in itertools.product((0,1),repeat=9)]
        extra={(a,b) for a,b in itertools.combinations(range(9),2) if all(x[a]<=x[b] for x in states)}-forbid
        for p in placements(9,4):
            r=prefix_state(prefix,p);t=len(r['gates'])
            if t in (1,2):
                real=tuple(i for i,s in enumerate(r['state']) if not s);rows.setdefault((real,3-t),dict(real=real,demand=3-t,placement=p))
        selected=list(rows.values());candidates=[n for n in layers if not set(n)&forbid]
        def permitted(n,rs):return all(sum(a in r['real'] and b in r['real'] for a,b in n)>=r['demand'] for r in rs)
        passing={n for n in candidates if permitted(n,selected)}
        for row in list(selected):
            rest=[r for r in selected if r is not row]
            if {n for n in candidates if permitted(n,rest)}==passing:selected.remove(row)
        endings=[]
        for n in sorted(passing):
            out=[run(prefix+(n,),x) for x in seeds];bad=set();required=set()
            for p in range(9):
                vals=[x[p] for x in out]
                if max(vals)-min(vals)>=4:required.add(p)
                for q in range(p+1,9):
                    for op in (min,max):
                        vals=[op(x[p],x[q]) for x in out]
                        if max(vals)-min(vals)>=4:bad.add((p,q));break
            iso=[p for p in required if all(tuple(sorted((p,q))) in bad for q in range(9) if q!=p)]
            endings.append(dict(fourth=n,isolated=iso))
        record=dict(case=number,third=m,forbidden=sorted(forbid),extra_order=sorted(extra),rows=selected,fourths=endings)
        report.append(record);print('CASE',number,m,'rows',len(selected),'N',len(endings),'nonisolated',sum(not r['isolated'] for r in endings),'extra order',extra,flush=True)
        for r in selected:print(' ',r)
        assert time.monotonic()-start<30
    out=dict(status='DISCOVERY_ONLY',cases=report,elapsed_seconds=time.monotonic()-start)
    (root/'results/h9-feedback-round9-fourths.json').write_text(json.dumps(out,indent=2)+'\n');print('DONE',out['elapsed_seconds'])


if __name__=='__main__':main()
