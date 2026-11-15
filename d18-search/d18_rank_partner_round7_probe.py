#!/usr/bin/env python3
"""Bounded fixed-bank support analysis; no SAT or matching enumeration."""
import itertools
import json
import time
from pathlib import Path

ROOT=Path(__file__).parent


def run(prefix,values):
    out=list(values)
    for layer in prefix:
        for a,b in layer:
            if out[a]>out[b]:out[a],out[b]=out[b],out[a]
    return out


def interval(values):return min(values),max(values)


def parity_bad(a,b,c=8):
    return a[1]-a[0]==b[1]-b[0]==c-1 and max(0,min(a[1],b[1])-max(a[0],b[0])+1)%2==1


def pair_ok(x,y,c=8):
    lo=interval([min(a,b) for a,b in zip(x,y)]);hi=interval([max(a,b) for a,b in zip(x,y)])
    return lo[1]-lo[0]<c and hi[1]-hi[0]<c and not parity_bad(lo,hi,c)


def main():
    start=time.monotonic();data=json.loads((ROOT/'results/rank-layer-round6-hand-certificate.json').read_text());report=[]
    for record in data['records']:
        name=record['name'];prefix=record['prefix'];bank=record['rank_inputs'];n=len(bank[0])
        before=[run(prefix[:-1],x) for x in bank];after=[run(prefix,x) for x in bank]
        choices=[tuple(e) for e in prefix[-1]];used={v for e in choices for v in e}
        choices += [(v,) for v in range(n) if v not in used]
        vectors={}
        for v in range(n):
            vectors[v,None]=[x[v] for x in before]
            for u in range(n):
                if u==v:continue
                vectors[v,u]=[(min if v<u else max)(x[v],x[u]) for x in before]
        pivots=[12] if name=='beam00' else [6] if name=='beam16' else [5,12]
        fixed_vectors={p:[x[p] for x in after] for p in pivots}
        allowed={p:{v:{u for u in [None]+[j for j in range(n) if j!=v]
                       if pair_ok(fixed_vectors[p],vectors[v,u])}
                    for v in range(n) if v!=p} for p in pivots}
        required_choices={j for j,e in enumerate(choices) if any(p in e for p in pivots)}
        if name=='beam32':required_choices|={j for j,e in enumerate(choices) if 2 in e or 8 in e}
        def evaluate(selected):
            fixed={v:(None if len(choices[j])==1 else next(u for u in choices[j] if u!=v)) for j in selected for v in choices[j]}
            free=set(range(n))-set(fixed);neighbors={}
            for p in pivots:
                neighbors[p]=[v for v in range(n) if v!=p and
                              (fixed[v] in allowed[p][v] if v in fixed else bool(allowed[p][v]&({None}|(free-{v}))))]
            if any(not neighbors[p] for p in pivots):return True,neighbors
            if name=='beam32' and neighbors[12]==[8] and set(neighbors[5])<={2,8}:
                a=interval([min(x[8],x[12]) for x in after]);b=interval([max(x[2],x[5]) for x in after])
                if parity_bad(a,b):return True,neighbors
            return False,neighbors
        witnesses=[]
        for size in range(len(required_choices),len(choices)+1):
            for extra in itertools.combinations(sorted(set(range(len(choices)))-required_choices),size-len(required_choices)):
                selected=required_choices|set(extra);closed,neighbors=evaluate(selected)
                if closed:witnesses.append(dict(fixed=[choices[j] for j in sorted(selected)],neighbors=neighbors))
            if witnesses:break
            assert time.monotonic()-start<20
        full=evaluate(set(range(len(choices))))
        print(name,'minimum fixed activities',size,'witnesses',len(witnesses),'examples',witnesses[:3],'full',full,flush=True)
        report.append(dict(name=name,total_activities=len(choices),minimum_fixed_activities=size,witnesses=witnesses,full=full))
    out=dict(status='DISCOVERY_ONLY',records=report,elapsed_seconds=time.monotonic()-start)
    (ROOT/'results/d18-rank-partner-round7-probe.json').write_text(json.dumps(out,indent=2)+'\n')
    print('DONE',out['elapsed_seconds'])


if __name__=='__main__':main()
