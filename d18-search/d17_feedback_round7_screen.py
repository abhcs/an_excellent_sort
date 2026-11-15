#!/usr/bin/env python3
"""Bounded SAT-free feedback: noncritical common-real antichain forms."""
from itertools import combinations
import json
from pathlib import Path
import time

ROOT=Path(__file__).parent
SOURCE=ROOT/'results/d17-feedback-fourteen-hand606-states.json'


def perfect(xs):
    if not xs:
        yield ();return
    a,*rest=xs
    for j,b in enumerate(rest):
        for tail in perfect(rest[:j]+rest[j+1:]):yield ((a,b),)+tail


def incomparable(a,b,states):
    return any(s[a]<s[b] for s in states) and any(s[a]>s[b] for s in states)


def cases(base,deficit,include_zero=False):
    vertices=set(range(12))
    inc={tuple(p) for p in combinations(range(12),2) if incomparable(*p,base)}
    antis=[()]+sorted(inc)+[p for p in combinations(range(12),4)
                            if all(q in inc for q in combinations(p,2))]
    idles=[()] if deficit==0 else sorted(inc)
    for I in idles:
        for E in antis:
            if set(I)&set(E):continue
            ext=tuple((v,12+j) for j,v in enumerate(E));n=12+len(E)
            for P in perfect(sorted(vertices-set(I)-set(E))):
                if (5,8) in P:continue
                M=tuple(sorted(P+ext));c=sum(a<5<=b<12 for a,b in M)
                if not c and not include_zero:continue
                yield n,I,E,c,M


def transport(s,M):
    out=s[:]
    for a,b in M:out[a],out[b]=min(out[a],out[b]),max(out[a],out[b])
    return {v for v,x in enumerate(out) if x}


def add(K,e):
    if e in K:return True
    if set(e)&{v for f in K for v in f}:return False
    K.add(e);return True


def propagate(K,required):
    forced=0
    while True:
        used={v for e in K for v in e};change=False
        for i,S in required.items():
            inside=sum(a in S and b in S for a,b in K);free=S-used
            if inside+len(free)//2<2:return True,forced
            if inside==1 and len(free)==2:
                K.add(tuple(sorted(free)));forced+=1;change=True;break
        if not change:return False,forced


def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--deficit',type=int,choices=(0,1),default=0)
    parser.add_argument('--include-zero',action='store_true')
    args=parser.parse_args();start=time.monotonic();base=[s[2:] for s in json.loads(SOURCE.read_text())['states']]
    hist={};survivors=[];count=0
    for n,I,E,c,M in cases(base,args.deficit,args.include_zero):
        states=[s+[0]*(n-12) for s in base];peak=n//2-3
        required={i:transport(s,M) for i,s in enumerate(states)
                  if sum(s[a]==s[b]==0 for a,b in M)<peak}
        full=[r for r in range(4) if all(5*r+j in required for j in range(5))]
        K=set();closed=False
        for r in full:
            S=[required[5*r+j] for j in range(5)];T=set.intersection(*S);assert len(T)==2
            core=[T,(S[0]&S[1])-T,(S[2]&S[3])-T];assert all(len(e)==2 for e in core)
            if not all(add(K,tuple(sorted(e))) for e in core):closed=True;break
        if not closed:closed,_=propagate(K,required)
        key=str((n,c,len(full),closed));hist[key]=hist.get(key,0)+1;count+=1
        if not closed:survivors.append(dict(n=n,idles=I,external=E,cross=c,M=M,full_rows=full,core=sorted(K),
                                           required=[i for i in required]))
    report=dict(status='COMPLETED_SCREEN',sat_used=False,deficit=args.deficit,canonical_cases=count,
                closed_by_full_row_core=count-len(survivors),survivors=len(survivors),histogram=hist,
                seconds=round(time.monotonic()-start,4),
                scope='Exploratory full-row screen; survivors are not feasible covers')
    name=f'd17-feedback-round7-screen-d{args.deficit}'+('-all' if args.include_zero else '')
    (ROOT/'results'/f'{name}.json').write_text(json.dumps(report,indent=2)+'\n')
    with (ROOT/'results'/f'{name}-survivors.jsonl').open('w') as f:
        for record in survivors:f.write(json.dumps(record,separators=(',',':'))+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
