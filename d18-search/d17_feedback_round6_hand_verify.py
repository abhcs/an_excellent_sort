#!/usr/bin/env python3
"""Small SAT-free corroboration of the round-six hand reductions/controls."""
import hashlib
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


def step(s,M):
    t=list(s)
    for a,b in M:t[a],t[b]=min(t[a],t[b]),max(t[a],t[b])
    return t


def rr(s,M):return sum(s[a]==s[b]==0 for a,b in M)


def signature(S,R):
    T=set.intersection(*S);U=set.intersection(*R)
    assert len(T)==len(U)==3 and len(T&U)==2
    x,=T-U;w,=U-T
    P=[s-T for s in S];Q=[s-U for s in R]
    assert all(len(p)==2 for p in P+Q)
    if P==Q:return 'ordinary'
    candidates=set.union(*P)
    assert any(Q==[(p-{y})|({x} if y in p else set()) for p in P] for y in candidates)
    return 'single_transfer'


def main():
    started=time.monotonic();base=[s[2:] for s in json.loads(SOURCE.read_text())['states']]
    aa=0;signatures={}
    for n in (12,14):
        states=[s+[0]*(n-12) for s in base];peak=n//2-3
        for I in ((0,3),(0,4)):
            for tail in perfect([v for v in range(n) if v not in (*I,5,8)]):
                M=((5,8),)+tail
                assert all(rr(s,M)<peak for i,s in enumerate(states) if i%5 in (1,2,3))
                # BC and BD are rows 1 and 3; D is idle in either AA pattern.
                S=[{v for v,x in enumerate(step(states[5+c],M)) if x} for c in (1,2,3)]
                R=[{v for v,x in enumerate(step(states[15+c],M)) if x} for c in (1,2,3)]
                sig=signature(S,R);signatures[sig]=signatures.get(sig,0)+1;aa+=1
    assert aa==2100
    cert=json.loads((ROOT/'results/d17-feedback-round6-core-certificate.json').read_text())
    mixed=0
    for record in cert['cases']:
        n=record['n'];M=record['M'];I=set(record['idles'])
        states=[s+[0]*(n-12) for s in base];peak=n//2-3
        first=[i for i,s in enumerate(states) if i%5 in (1,2,3) and rr(s,M)>=peak]
        assert len(first)<=2
        assert len({i//5 for i in first})==len(first)==len({i%5 for i in first})
        assert all(I<={v for v,x in enumerate(states[i]) if x} for i in first)
        assert len([r for r in range(4) if all(5*r+c not in first for c in (1,2,3))])>=2
        mixed+=1
    controls=json.loads((ROOT/'results/d17-feedback-round6-three-column-controls.json').read_text())
    controls_checked=0
    for example in controls['examples']:
        M=example['M']
        for control in example['selected_three_column_covers']:
            N=control['N'];profiles=[[rr(s,M),rr(step(s,M),N)] for s in base]
            assert profiles==control['profiles']
            failing=[i for i,p in enumerate(profiles) if max(p)<3]
            assert failing==control['failing_full'] and failing
            assert all(i%5==0 for i in failing)
            controls_checked+=1
    report=dict(status='VERIFIED',sat_used=False,aa_idle_cases=aa,aa_row_signatures=signatures,
                mixed_canonical_full_row_checks=mixed,three_column_covers_checked=controls_checked,
                input_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                seconds=round(time.monotonic()-started,4),
                scope='Corroboration only; does not replace the hand normalization proof or finite core premise')
    (ROOT/'results/d17-feedback-round6-hand-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
