#!/usr/bin/env python3
"""No SAT: exact full-row cores plus free-endpoint forcing feedback."""
import collections
from itertools import combinations
import json
from pathlib import Path
import time
from d17_feedback_round4_verify import matchings,step,edge,G,SIGN

ROOT=Path(__file__).parent
STATES=json.loads((ROOT/'results/d17-feedback-fourteen-hand606-states.json').read_text())['states']


def compatible(C):
    partner={}
    for a,b in C:
        if a in partner and partner[a]!=b or b in partner and partner[b]!=a:return False
        partner[a]=b;partner[b]=a
    return True


def row_cores(family):
    T=set.intersection(*family);assert len(T)==3
    q,=family[0]&family[1]-T;e,=family[1]&family[2]-T
    b,=family[0]-T-{q};r,=family[2]-T-{e}
    return [frozenset((edge(e,r),)+P) for P in matchings(sorted(T|{q}),True)]+[
            frozenset((edge(q,b),)+P) for P in matchings(sorted(T|{e}),True)]


def propagate(core,sets):
    core=set(core)
    while True:
        if not compatible(core):return None
        used={v for e in core for v in e};add=set()
        for S in sets:
            need=2-sum(a in S and b in S for a,b in core)
            if need<=0:continue
            free=S-used
            if len(free)<2*need:return None
            if len(free)==2 and need==1:add.add(tuple(sorted(free)))
        if add<=core:return frozenset(core)
        core.update(add)


def main():
    started=time.monotonic();counts=collections.Counter();examples={};records=[]
    for tail in matchings([v for v in range(14) if v not in (7,10)],True):
        M=((7,10),)+tail
        cross=sum(a in SIGN and b>=7 for a,b in M)
        if cross<3:continue
        allsets=[];full=[]
        for row in range(4):
            sets=[]
            for s in STATES[5*row+1:5*row+4]:
                if sum(s[a]==s[b]==0 for a,b in M)<4:
                    sets.append({v for v,x in enumerate(step(s,M)) if x})
            allsets+=sets
            if len(sets)==3:full.append((row,row_cores(sets)))
        assert full
        possible={frozenset()}
        for unused,cores in full:
            nxt=set()
            for C in possible:
                for D in cores:
                    propagated=propagate(C|D,allsets)
                    if propagated is not None:nxt.add(propagated)
            possible=nxt
            if not possible:break
        counts[(cross,len(full),bool(possible))]+=1
        if possible:
            key=str((cross,len(full)))
            examples.setdefault(key,dict(M=M,full_rows=[r for r,c in full],cores=[sorted(C) for C in possible],
                                         required_sets=[sorted(S) for S in allsets]))
            records.append(dict(M=M,cross=cross,full_rows=[r for r,c in full],cores=[sorted(C) for C in possible]))
    result=dict(status='COMPLETED',sat_used=False,seconds=round(time.monotonic()-started,4),
                counts=[dict(cross=c,full=f,survives=p,count=v) for (c,f,p),v in sorted(counts.items())],
                examples=examples,survivors=records,
                scope='Incomplete full-row-core and forced-edge screen; survivors are not peak covers')
    (ROOT/'results/d17-feedback-round5-core-screen.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('examples','survivors')},indent=2))
    print(json.dumps(examples,indent=2))


if __name__=='__main__':main()
