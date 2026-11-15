#!/usr/bin/env python3
"""SAT-free feedback for canonical critical two-idle mixed cases."""
import collections
from itertools import combinations,permutations
import json
from pathlib import Path
import time
from d17_feedback_round5_certificate import step,edge,comparable,row_cores,refute

ROOT=Path(__file__).parent
SOURCE=ROOT/'results/d17-feedback-fourteen-hand606-states.json'


def canonical_cases(base):
    A=set(range(5));B={6,7,9,10,11};critical=(5,8)
    selected=[base[5*r+c] for r in range(4) for c in (1,2,3)]
    for idleA in sorted(A):
        for idleB in sorted(B):
            if comparable(idleA,idleB,selected):continue
            usedA=A-{idleA};usedB=B-{idleB}
            for c in (2,3,4):
                for crossedA in combinations(sorted(usedA),c):
                    for crossedB in combinations(sorted(usedB),c):
                        for targets in permutations(crossedB):
                            cross=tuple(edge(a,b) for a,b in zip(crossedA,targets))
                            restA=sorted(usedA-set(crossedA));restB=sorted(usedB-set(crossedB))
                            if c==2:
                                yield 12,c,(idleA,idleB),tuple(sorted((critical,edge(*restA),edge(*restB))+cross))
                                if not comparable(*restA,selected):
                                    yield 14,c,(idleA,idleB),tuple(sorted((critical,edge(*restB),(restA[0],12),(restA[1],13))+cross))
                            elif c==3:
                                a,=restA;b,=restB
                                if not comparable(a,b,selected):
                                    yield 14,c,(idleA,idleB),tuple(sorted((critical,(a,12),(b,13))+cross))
                            else:yield 12,c,(idleA,idleB),tuple(sorted((critical,)+cross))


def main():
    started=time.monotonic();base=[s[2:] for s in json.loads(SOURCE.read_text())['states']]
    counts=collections.Counter();failures=[];max_forced=0;closed=0
    for n,c,idles,M in canonical_cases(base):
        states=[s+[0]*(n-12) for s in base];peak=n//2-3;required=[];full=[]
        for row in range(4):
            S=[]
            for col in (1,2,3):
                i=5*row+col;s=states[i]
                if sum(s[a]==s[b]==0 for a,b in M)<peak:
                    pos={v for v,x in enumerate(step(s,M)) if x};required.append((i,pos));S.append(pos)
            if len(S)==3:full.append((row,S))
        assert len(full)>=2
        success=False;left=[]
        for row,S in full:
            traces=[];survive=[]
            for core in row_cores(S):
                try:traces.append(refute(core,required))
                except AssertionError:survive.append(core)
            if not survive:
                success=True;max_forced=max(max_forced,max(len(t['forced']) for t in traces));break
            left.append(dict(row=row,cores=survive))
        if success:closed+=1
        else:failures.append(dict(n=n,cross=c,idles=idles,M=M,full_rows=[r for r,S in full],unresolved=left))
        counts[(n,c,success)]+=1
    assert sum(counts.values())==1488
    result=dict(status='COMPLETED',sat_used=False,cases=1488,closed=closed,max_forced=max_forced,
                counts=[dict(n=n,cross=c,closed=p,count=v) for (n,c,p),v in sorted(counts.items())],
                failures=failures,seconds=round(time.monotonic()-started,4),
                scope='Discovery only; unresolved cores are not peak covers')
    (ROOT/'results/d17-feedback-round6-discovery.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='failures'},indent=2))
    if failures:print(json.dumps(failures[:3],indent=2))


if __name__=='__main__':main()
