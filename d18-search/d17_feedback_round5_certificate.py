#!/usr/bin/env python3
"""Generate short arithmetic certificates for 1080 normalized first matchings.

No SAT. Each final matching is split into six exact full-row cores, and
then only forced edges and free-endpoint capacity contradictions are used.
"""
import hashlib
from itertools import combinations,permutations
import json
from pathlib import Path
import time

ROOT=Path(__file__).parent
SOURCE=ROOT/'results/d17-feedback-fourteen-hand606-states.json'


def step(s,M):
    out=list(s)
    for a,b in M:out[a],out[b]=sorted((out[a],out[b]))
    return out


def edge(a,b):return tuple(sorted((a,b)))


def pairings(four):
    a,*rest=sorted(four)
    for i,b in enumerate(rest):
        c,d=rest[:i]+rest[i+1:]
        yield (edge(a,b),edge(c,d))


def comparable(a,b,states):
    return all(s[a]<=s[b] for s in states) or all(s[a]>=s[b] for s in states)


def canonical_cases(base):
    A=set(range(5));B={6,7,9,10,11};critical=(5,8)
    selected=[base[5*r+c] for r in range(4) for c in (1,2,3)]
    for c in (3,4,5):
        for crossedA in combinations(sorted(A),c):
            for crossedB in combinations(sorted(B),c):
                for targets in permutations(crossedB):
                    cross=tuple(edge(a,b) for a,b in zip(crossedA,targets))
                    restA=sorted(A-set(crossedA));restB=sorted(B-set(crossedB))
                    if c==3:
                        yield 12,c,tuple(sorted((critical,edge(*restA),edge(*restB))+cross))
                        if not comparable(*restA,selected):
                            yield 14,c,tuple(sorted((critical,edge(*restB),(restA[0],12),(restA[1],13))+cross))
                    elif c==4:
                        a,=restA;b,=restB
                        if not comparable(a,b,selected):
                            yield 14,c,tuple(sorted((critical,(a,12),(b,13))+cross))
                    else:yield 12,c,tuple(sorted((critical,)+cross))


def row_cores(S):
    T=set.intersection(*S);assert len(T)==3
    q,=(S[0]&S[1])-T;e,=(S[1]&S[2])-T
    b,=S[0]-T-{q};r,=S[2]-T-{e}
    return [tuple(sorted((edge(e,r),)+P)) for P in pairings(T|{q})]+[
            tuple(sorted((edge(q,b),)+P)) for P in pairings(T|{e})]


def refute(core,required):
    current=set(core);forced=[]
    while True:
        used={v for e in current for v in e}
        changed=False
        for i,S in required:
            inside=sum(a in S and b in S for a,b in current);free=S-used
            if inside+len(free)//2<2:
                return dict(initial_core=core,forced=forced,contradiction=i)
            if inside==1 and len(free)==2:
                new=tuple(sorted(free));current.add(new)
                forced.append(dict(state=i,edge=new));changed=True;break
        assert changed,('unresolved',core,required,current)


def main():
    started=time.monotonic();base=[s[2:] for s in json.loads(SOURCE.read_text())['states']]
    records=[];hist={};branches=forces=0
    for n,c,M in canonical_cases(base):
        states=[s+[0]*(n-12) for s in base];peak=n//2-3;required=[];full=[]
        for row in range(4):
            S=[]
            for col in (1,2,3):
                i=5*row+col;s=states[i]
                if sum(s[a]==s[b]==0 for a,b in M)<peak:
                    positions={v for v,x in enumerate(step(s,M)) if x};required.append((i,positions));S.append(positions)
            if len(S)==3:full.append((row,S))
        assert full
        row,S=full[0]
        traces=[refute(core,required) for core in row_cores(S)]
        records.append(dict(n=n,cross=c,M=M,full_row=row,branches=traces))
        hist[str((n,c))]=hist.get(str((n,c)),0)+1
        branches+=len(traces);forces+=sum(len(t['forced']) for t in traces)
    assert len(records)==1080 and branches==6480
    report=dict(status='CERTIFICATE_GENERATED',sat_used=False,
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                input_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                base_map_to_original=json.loads(SOURCE.read_text())['compact_to_original'][2:],
                selected_B_columns=[1,2,3],cases=records,case_counts=hist,branches=branches,
                forced_steps=forces,seconds=round(time.monotonic()-started,4),
                scope='Finite-assisted critical-perfect >=3cross obstruction; not a complete hand classification')
    out=ROOT/'results/d17-feedback-round5-core-certificate.json'
    out.write_text(json.dumps(report,separators=(',',':'))+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='cases'},indent=2))


if __name__=='__main__':main()
