#!/usr/bin/env python3
"""SAT-free six-core certificates for critical mixed two-idle normal forms."""
import hashlib
from itertools import combinations,permutations
import json
from pathlib import Path
import time
from d17_feedback_round5_certificate import step,edge,comparable,row_cores,refute

ROOT=Path(__file__).parent
SOURCE=ROOT/'results/d17-feedback-fourteen-hand606-states.json'


def cases(base):
    A=set(range(5));B={6,7,9,10,11};critical=(5,8)
    selected=[base[5*r+c] for r in range(4) for c in (1,2,3)]
    for ia in sorted(A):
        for ib in sorted(B):
            if comparable(ia,ib,selected):continue
            usedA=A-{ia};usedB=B-{ib}
            for c in (2,3,4):
                for xa in combinations(sorted(usedA),c):
                    for xb in combinations(sorted(usedB),c):
                        for targets in permutations(xb):
                            cross=tuple(edge(a,b) for a,b in zip(xa,targets))
                            ra=sorted(usedA-set(xa));rb=sorted(usedB-set(xb))
                            if c==2:
                                yield 12,c,(ia,ib),tuple(sorted((critical,edge(*ra),edge(*rb))+cross))
                                if not comparable(*ra,base):
                                    yield 14,c,(ia,ib),tuple(sorted((critical,edge(*rb),(ra[0],12),(ra[1],13))+cross))
                            elif c==3:
                                a,=ra;b,=rb
                                # Full-family comparability is essential: later traces may use qab.
                                if not comparable(a,b,base):
                                    yield 14,c,(ia,ib),tuple(sorted((critical,(a,12),(b,13))+cross))
                            else:yield 12,c,(ia,ib),tuple(sorted((critical,)+cross))


def main():
    started=time.monotonic();base=[s[2:] for s in json.loads(SOURCE.read_text())['states']]
    records=[];hist={};total_forced=max_forced=0
    for n,c,idles,M in cases(base):
        states=[s+[0]*(n-12) for s in base];peak=n//2-3
        required=[(i,{v for v,x in enumerate(step(s,M)) if x}) for i,s in enumerate(states)
                  if sum(s[a]==s[b]==0 for a,b in M)<peak]
        lookup=dict(required);choices=[];full=[]
        for row in range(4):
            ids=[5*row+col for col in (1,2,3)]
            if not all(i in lookup for i in ids):continue
            full.append(row);S=[lookup[i] for i in ids]
            try:traces=[refute(C,required) for C in row_cores(S)]
            except AssertionError:continue
            choices.append((max(len(t['forced']) for t in traces),sum(len(t['forced']) for t in traces),row,traces))
        assert len(full)>=2 and choices,(n,c,idles,M)
        maximum,total,row,traces=min(choices,key=lambda x:x[:3])
        records.append(dict(n=n,cross=c,idles=idles,M=M,full_row=row,branches=traces))
        hist[str((n,c))]=hist.get(str((n,c)),0)+1
        max_forced=max(max_forced,maximum);total_forced+=total
    assert len(records)==1584
    report=dict(status='CERTIFICATE_GENERATED',sat_used=False,
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                input_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                full_family_contraction=True,cases=records,case_counts=hist,
                branches=6*len(records),forced_steps=total_forced,max_forced_per_branch=max_forced,
                seconds=round(time.monotonic()-started,4),
                scope='Critical mixed two-idle >=2cross cases, finite-assisted, all twenty states available')
    (ROOT/'results/d17-feedback-round6-core-certificate.json').write_text(json.dumps(report,separators=(',',':'))+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='cases'},indent=2))


if __name__=='__main__':main()
