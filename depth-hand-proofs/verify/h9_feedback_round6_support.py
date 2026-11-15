#!/usr/bin/env python3
"""Bounded activity-support propagation; no SAT or full suffix enumeration."""
import itertools
import json
import time
from pathlib import Path
from netlib import run
from h9_feedback_round6_probe import FIRST,SECOND
from h9_feedback_round4_rank_witnesses import lift


def compatible(a,b):return a==b or not set(a)&set(b)
def odd(a,b):return a[1]-a[0]==b[1]-b[0]==3 and max(0,min(a[1],b[1])-max(a[0],b[0])+1)%2


def main():
    start=time.monotonic();root=Path(__file__).parents[1]
    cases=json.loads((root/'results/h9-feedback-round6-fourths.json').read_text())['cases']
    inputs=sorted({lift(x) for x in itertools.product((0,1),repeat=9)});report=[]
    for case in cases:
        out=[run((FIRST,SECOND,case['third']),x) for x in inputs]
        forbid=set(map(tuple,case['forbidden']));activities=[(i,) for i in range(9)]+[e for e in itertools.combinations(range(9),2) if e not in forbid]
        vectors={};mandatory={};supports={}
        for i,a in enumerate(activities):
            for p in a:
                v=[x[p] if len(a)==1 else (min if p==a[0] else max)(x[a[0]],x[a[1]]) for x in out]
                vectors[i,p]=v;mandatory[i,p]=max(v)-min(v)>=4
        for (i,p),v in vectors.items():
            if not mandatory[i,p]:continue
            support=[]
            for (j,q),w in vectors.items():
                if p==q or not compatible(activities[i],activities[j]):continue
                lo=[min(a,b) for a,b in zip(v,w)];hi=[max(a,b) for a,b in zip(v,w)];a=(min(lo),max(lo));b=(min(hi),max(hi))
                if a[1]-a[0]<4 and b[1]-b[0]<4 and not odd(a,b):support.append((j,q))
            supports[i,p]=support
        active=set(range(len(activities)));steps=[]
        while True:
            removed=[]
            for i in sorted(active):
                a=activities[i];reason=None
                for p in a:
                    if mandatory[i,p] and not any(j in active for j,q in supports[i,p]):reason=dict(kind='rank',pivot=p);break
                if reason is None:
                    for index,row in enumerate(case['rows']):
                        real=set(row['real']);need=row['demand']
                        possibles=[j for j in active if len(activities[j])==2 and set(activities[j])<=real and compatible(a,activities[j])]
                        if not possibles or need==2 and not any(compatible(activities[j],activities[k]) and j!=k for j,k in itertools.combinations(possibles,2)):
                            reason=dict(kind='demand',row=index);break
                if reason is not None:removed.append((i,reason))
            if removed:
                for i,reason in removed:active.remove(i);steps.append(dict(activity=activities[i],**reason))
                continue
            forced=[next(i for i in active if p in activities[i]) for p in range(9) if sum(p in activities[i] for i in active)==1]
            conflict=[i for i in active if any(not compatible(activities[i],activities[j]) for j in forced)]
            if conflict:
                for i in sorted(conflict):active.remove(i);steps.append(dict(activity=activities[i],kind='forced',forced=[activities[j] for j in forced if not compatible(activities[i],activities[j])]))
                continue
            break
        empty=[p for p in range(9) if not any(p in activities[i] for i in active)]
        item=dict(case=case['case'],initial=len(activities),remaining=[activities[i] for i in sorted(active)],empty_wires=empty,steps=steps)
        report.append(item);print(case['case'],'activities',len(activities),'->',len(active),'empty',empty,'reasons',{k:sum(s['kind']==k for s in steps) for k in ('rank','demand','forced')},flush=True)
        assert time.monotonic()-start<30
    (root/'results/h9-feedback-round6-support.json').write_text(json.dumps(dict(status='DISCOVERY_ONLY',records=report,elapsed_seconds=time.monotonic()-start),indent=2)+'\n')
    print('DONE',time.monotonic()-start)


if __name__=='__main__':main()
