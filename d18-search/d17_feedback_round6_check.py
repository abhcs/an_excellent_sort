#!/usr/bin/env python3
"""Independent, SAT-free check of all critical mixed two-idle core traces."""
import hashlib
import json
from pathlib import Path
import time

ROOT=Path(__file__).parent
SOURCE=ROOT/'results/d17-feedback-fourteen-hand606-states.json'
CERT=ROOT/'results/d17-feedback-round6-core-certificate.json'


def perfect(xs):
    if not xs:
        yield ();return
    a,*rest=xs
    for j,b in enumerate(rest):
        for tail in perfect(rest[:j]+rest[j+1:]):yield ((a,b),)+tail


def matching(M):
    vs=[v for e in M for v in e]
    return len(vs)==len(set(vs)) and all(a<b for a,b in M)


def step(s,M):
    out=list(s)
    for a,b in M:out[a],out[b]=min(out[a],out[b]),max(out[a],out[b])
    return out


def incomparable(a,b,S):return any(s[a]<s[b] for s in S) and any(s[a]>s[b] for s in S)


def expected_cases(base):
    A=set(range(5));B={6,7,9,10,11};selected=[s for i,s in enumerate(base) if i%5 in (1,2,3)]
    expected=set()
    for ia in A:
        for ib in B:
            if not incomparable(ia,ib,selected):continue
            for n in (12,14):
                for tail in perfect([v for v in range(n) if v not in (5,8,ia,ib)]):
                    M=tuple(sorted(((5,8),)+tail));c=sum(a in A and b in B for a,b in M)
                    if c<2:continue
                    if n==12:
                        assert c in (2,4);expected.add((n,(ia,ib),M));continue
                    p={v:w for a,b in M for v,w in ((a,b),(b,a))};a,b=p[12],p[13]
                    if c==2 and a in A and b in A and a<b and incomparable(a,b,base):
                        expected.add((n,(ia,ib),M))
                    if c==3 and a in A and b in B and incomparable(a,b,base):
                        expected.add((n,(ia,ib),M))
    return expected


def main():
    start=time.monotonic();base=[s[2:] for s in json.loads(SOURCE.read_text())['states']]
    data=json.loads(CERT.read_text());assert data['input_sha256']==hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    expected=expected_cases(base);assert len(expected)==1584
    seen=set();hist={};branches=forces=maxforce=0;exceptional_column_uses=0
    for record in data['cases']:
        n=record['n'];I=tuple(record['idles']);M=tuple(tuple(e) for e in record['M']);key=(n,I,M)
        assert key in expected and key not in seen;seen.add(key)
        assert matching(M) and len(M)==n//2-1
        assert set(range(n))-{v for e in M for v in e}==set(I)
        states=[s+[0]*(n-12) for s in base];peak=n//2-3
        required={i:{v for v,x in enumerate(step(s,M)) if x} for i,s in enumerate(states)
                  if sum(s[a]==s[b]==0 for a,b in M)<peak}
        row=record['full_row'];ids=[5*row+c for c in (1,2,3)];assert all(i in required for i in ids)
        S=[required[i] for i in ids];T=set.intersection(*S);assert len(T)==3
        q,=(S[0]&S[1])-T;e,=(S[1]&S[2])-T
        b,=S[0]-T-{q};r,=S[2]-T-{e}
        cores={frozenset((tuple(sorted((e,r))),)+P) for P in perfect(sorted(T|{q}))}
        cores|={frozenset((tuple(sorted((q,b))),)+P) for P in perfect(sorted(T|{e}))}
        assert len(cores)==6 and len(record['branches'])==6
        assert {frozenset(tuple(e) for e in t['initial_core']) for t in record['branches']}==cores
        for trace in record['branches']:
            K=set(tuple(e) for e in trace['initial_core']);assert matching(K)
            for operation in trace['forced']:
                i=operation['state'];assert i in required;S=required[i]
                free=S-{v for e in K for v in e}
                assert sum(a in S and b in S for a,b in K)==1 and len(free)==2
                new=tuple(operation['edge']);assert new==tuple(sorted(free));K.add(new);assert matching(K)
                forces+=1;exceptional_column_uses+=i%5==0
            i=trace['contradiction'];assert i in required;S=required[i]
            free=S-{v for e in K for v in e}
            assert sum(a in S and b in S for a,b in K)+len(free)//2<2
            exceptional_column_uses+=i%5==0;branches+=1;maxforce=max(maxforce,len(trace['forced']))
        hist[str((n,record['cross']))]=hist.get(str((n,record['cross'])),0)+1
    assert seen==expected and branches==9504
    report=dict(status='VERIFIED',sat_used=False,certificate_sha256=hashlib.sha256(CERT.read_bytes()).hexdigest(),
                checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                input_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),case_counts=hist,
                canonical_cases=len(seen),branches=branches,forced_steps=forces,max_forced_per_branch=maxforce,
                qab_column_inference_uses=exceptional_column_uses,seconds=round(time.monotonic()-start,4),
                finite_verification_is_a_premise=True,complete_pure_hand_classification=False)
    (ROOT/'results/d17-feedback-round6-core-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
