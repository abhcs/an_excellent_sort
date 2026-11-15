#!/usr/bin/env python3
"""Independent checker of normalized-case coverage and forced-edge traces.

Does not import the certificate generator, discovery scripts, or a solver.
"""
import hashlib
from itertools import combinations
import json
from pathlib import Path
import time

ROOT=Path(__file__).parent
SOURCE=ROOT/'results/d17-feedback-fourteen-hand606-states.json'
CERT=ROOT/'results/d17-feedback-round5-core-certificate.json'


def perfect(xs):
    if not xs:
        yield ();return
    a,*rest=xs
    for j,b in enumerate(rest):
        for tail in perfect(rest[:j]+rest[j+1:]):yield ((a,b),)+tail


def matching(M):
    used=[v for e in M for v in e]
    return len(used)==len(set(used)) and all(a<b for a,b in M)


def transport(s,M):
    out=list(s)
    for a,b in M:
        lo=min(out[a],out[b]);hi=max(out[a],out[b]);out[a]=lo;out[b]=hi
    return out


def incomparable(a,b,states):
    return any(s[a]<s[b] for s in states) and any(s[a]>s[b] for s in states)


def expected_cases(base):
    A=set(range(5));B={6,7,9,10,11};selected=[base[i] for i in range(20) if i%5 in (1,2,3)]
    result=set()
    for n in (12,14):
        for tail in perfect([v for v in range(n) if v not in (5,8)]):
            M=tuple(sorted(((5,8),)+tail));cross=[(a,b) for a,b in M if a in A and b in B]
            c=len(cross)
            if c<3:continue
            if n==12:
                assert c in (3,5);result.add((n,M));continue
            partner={v:w for a,b in M for v,w in ((a,b),(b,a))}
            if c==3:
                a,b=partner[12],partner[13]
                if a in A and b in A and a<b and incomparable(a,b,selected):result.add((n,M))
            if c==4:
                a,b=partner[12],partner[13]
                if a in A and b in B and incomparable(a,b,selected):result.add((n,M))
    return result


def main():
    started=time.monotonic();source=json.loads(SOURCE.read_text());base=[s[2:] for s in source['states']]
    data=json.loads(CERT.read_text());assert data['input_sha256']==hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    expected=expected_cases(base);assert len(expected)==1080
    seen=set();branches=forced=0;max_forced=0;hist={}
    for record in data['cases']:
        n=record['n'];M=tuple(tuple(e) for e in record['M']);key=(n,M)
        assert key in expected and key not in seen;seen.add(key)
        assert matching(M) and len(M)==n//2
        states=[s+[0]*(n-12) for s in base];peak=n//2-3
        required={i:{v for v,x in enumerate(transport(s,M)) if x} for i,s in enumerate(states)
                  if i%5 in (1,2,3) and sum(s[a]==s[b]==0 for a,b in M)<peak}
        row=record['full_row'];ids=[5*row+c for c in (1,2,3)];assert all(i in required for i in ids)
        S=[required[i] for i in ids];T=set.intersection(*S);assert len(T)==3
        q,=(S[0]&S[1])-T;e,=(S[1]&S[2])-T
        b,=S[0]-T-{q};r,=S[2]-T-{e}
        exact={frozenset((tuple(sorted((e,r))),)+P) for P in perfect(sorted(T|{q}))}
        exact|={frozenset((tuple(sorted((q,b))),)+P) for P in perfect(sorted(T|{e}))}
        assert len(exact)==6
        assert {frozenset(tuple(e) for e in t['initial_core']) for t in record['branches']}==exact
        assert len(record['branches'])==6
        for trace in record['branches']:
            core=set(tuple(e) for e in trace['initial_core']);assert matching(core)
            for operation in trace['forced']:
                i=operation['state'];assert i in required;S=required[i]
                used={v for e in core for v in e};free=S-used
                assert sum(a in S and b in S for a,b in core)==1 and len(free)==2
                e=tuple(operation['edge']);assert e==tuple(sorted(free));core.add(e);assert matching(core)
                forced+=1
            S=required[trace['contradiction']];used={v for e in core for v in e}
            assert sum(a in S and b in S for a,b in core)+len(S-used)//2<2
            branches+=1;max_forced=max(max_forced,len(trace['forced']))
        hist[str((n,record['cross']))]=hist.get(str((n,record['cross'])),0)+1
    assert seen==expected and branches==6480
    # Local RR loss in contracting two external common-real partners.
    for a in (-1,0,1):
        for b in (-1,0,1):
            old=(a==0)+(b==0);new=int(a==b==0)
            assert old-new in (0,1)
    report=dict(status='VERIFIED',sat_used=False,certificate_sha256=hashlib.sha256(CERT.read_bytes()).hexdigest(),
                checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                input_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),case_counts=hist,
                canonical_cases=len(seen),branches=branches,forced_steps=forced,max_forced_per_branch=max_forced,
                seconds=round(time.monotonic()-started,4),
                finite_verification_is_a_premise=True,complete_pure_hand_classification=False,
                conclusion='Critical perfect first matching, >=3crosses, arbitrary even active width: excluded by hand normalization plus finite core certificate')
    (ROOT/'results/d17-feedback-round5-core-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
