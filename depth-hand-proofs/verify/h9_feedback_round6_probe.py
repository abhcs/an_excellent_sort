#!/usr/bin/env python3
"""Bounded single-class rank-partner discovery for 03 16 47."""
import itertools
import json
import time
from pathlib import Path
from netlib import matchings,run
from h9_feedback_round4_rank_witnesses import lift

FIRST=((0,1),(2,3),(4,5));SECOND=((0,3),(1,6),(4,7))


def norm(m):return tuple(sorted(tuple(sorted(e)) for e in m))
def swap(i):return 7 if i==5 else 5 if i==7 else i
def canonical(m):return min(norm(m),norm((swap(a),swap(b)) for a,b in m))
def bounds(values):return min(values),max(values)
def odd(a,b):return a[1]-a[0]==b[1]-b[0]==3 and max(0,min(a[1],b[1])-max(a[0],b[0])+1)%2


def main():
    start=time.monotonic();root=Path(__file__).parents[1]
    source=next(e for e in json.loads((root/'results/h9-feedback-next-fourths-combined.json').read_text()) if e['label']=='(0,3)(1,6)(4,7)')
    seeds=sorted({lift(x) for x in itertools.product((0,1),repeat=9)});layers=matchings(9);cases=[]
    for row in source['rows']:
        m=norm(row['third'])
        if canonical(m)!=m:continue
        case=dict(case=len(cases)+1,third=m,fourths=[])
        for number,n in enumerate(row['fourths'],1):
            out=[run((FIRST,SECOND,m,n),x) for x in seeds]
            idle={p:bounds([x[p] for x in out]) for p in range(9)}
            intervals={e:(bounds([min(x[e[0]],x[e[1]]) for x in out]),bounds([max(x[e[0]],x[e[1]]) for x in out])) for e in itertools.combinations(range(9),2)}
            mandatory={p for p,(lo,hi) in idle.items() if hi-lo>=4}
            forbidden={e for e,ab in intervals.items() if any(hi-lo>=4 for lo,hi in ab)}
            iso=[p for p in mandatory if all(tuple(sorted((p,q))) in forbidden for q in range(9) if q!=p)]
            qwidth=[q for q in layers if not set(q)&forbidden and mandatory<={v for e in q for v in e}]
            qparity=[]
            for q in qwidth:
                occupied={v for e in q for v in e};all_intervals=[idle[p] for p in range(9) if p not in occupied]+[ab for e in q for ab in intervals[e]]
                if not any(odd(a,b) for a,b in itertools.combinations(all_intervals,2)):qparity.append(q)
            case['fourths'].append(dict(number=number,fourth=n,mandatory=sorted(mandatory),isolated=iso,width_survivors=qwidth,parity_survivors=qparity))
            print(case['case'],m,number,n,'isolated',iso,'Qwidth',len(qwidth),'Qparity',len(qparity),flush=True)
            assert time.monotonic()-start<30
        cases.append(case)
    data=dict(status='DISCOVERY_ONLY',second=SECOND,cases=cases,elapsed_seconds=time.monotonic()-start)
    (root/'results/h9-feedback-round6-probe.json').write_text(json.dumps(data,indent=2)+'\n');print('DONE',data['elapsed_seconds'])


if __name__=='__main__':main()
