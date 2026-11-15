#!/usr/bin/env python3
"""Small explicit cut-budget witnesses for the common four-gate spine."""
from itertools import combinations
import json
from pathlib import Path
import time
from d17_feedback_round8_patterns import prices
from d17_feedback_round7_screen import transport

ROOT=Path(__file__).parent
SPINE=((1,7),(2,9),(3,4),(8,10))
RESIDUAL=(0,5,6,11)


def variants():
    for tail in (((0,5),(6,11)),((0,6),(5,11)),((0,11),(5,6))):
        yield 'internal',12,SPINE+tail,()
    for P in combinations((0,5,11),2):
        left=tuple(v for v in RESIDUAL if v not in P)
        yield 'external',14,SPINE+((P[0],12),(P[1],13),(left[0],left[1])),()
    for I in combinations((0,5,11),2):
        left=tuple(v for v in RESIDUAL if v not in I)
        yield 'idle',12,SPINE+((left[0],left[1]),),I


def main():
    start=time.monotonic();base=[s[2:] for s in json.loads((ROOT/'results/d17-feedback-fourteen-hand606-states.json').read_text())['states']]
    reports=[]
    for kind,n,M,I in variants():
        family=[s+[0]*(n-12) for s in base]
        required={i:transport(s,M) for i,s in enumerate(family) if sum(s[a]==s[b]==0 for a,b in M)<n//2-3}
        witness=None
        for k in (3,4,5,6):
            for ids in combinations(required,k):
                sets=[required[i] for i in ids];q,cost,target=prices(sets)
                if cost<target:
                    radii={v:sum(v in S for S in sets)-price for v,price in q.items()}
                    if min(radii.values())<0:continue
                    witness=(ids,sets,radii);break
            if witness:break
        assert witness
        ids,sets,radii=witness
        # Lowering a radius preserves every distance inequality.
        for v in sorted(radii):
            while radii[v] and sum(radii.values())>len(sets)+1:radii[v]-=1
        radii={v:r for v,r in radii.items() if r}
        incidence={v:sum(1<<j for j,S in enumerate(sets) if v in S) for v in range(n)}
        assert sum(radii.values())==len(sets)+1
        assert all(radii.get(v,0)<=incidence[v].bit_count() for v in range(n))
        assert all(radii.get(u,0)+radii.get(v,0)<=(incidence[u]^incidence[v]).bit_count()
                   for u,v in combinations(range(n),2))
        reports.append(dict(kind=kind,n=n,M=sorted(M),idles=I,states=ids,
                            sentinel_sets=[sorted(S) for S in sets],radii=radii,
                            incidence={v:format(incidence[v],f'0{len(sets)}b') for v in range(n) if incidence[v]},
                            first_counts=[sum(family[i][a]==family[i][b]==0 for a,b in M) for i in ids]))
    report=dict(status='WITNESSES_GENERATED',sat_used=False,scope='Nine normalized four-gate-spine forms',
                records=reports,seconds=round(time.monotonic()-start,4))
    (ROOT/'results/d17-feedback-round8-spine-witnesses.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
