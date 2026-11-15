#!/usr/bin/env python3
"""Local audits for hand531/522 merger obstructions, no SAT."""
import hashlib
import itertools
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def main():
    singleton_cases=[]
    for p,q in ((3,5),(4,4),(5,3)):
        triples=[set(range(i,i+3)) for i in range(q-2)]
        common=set.intersection(*triples)
        assert len(common)==6-q<p-1
        singleton_cases.append(dict(partner_block=p,other_block=q,intersection=sorted(common),demand=p-1))
    path=[set((i,i+1)) for i in range(4)]
    covers=[list(S) for k in range(3) for S in itertools.combinations(range(5),k)
            if all(set(S)&e for e in path)]
    assert covers==[[1,3]]
    bblock=(5,6);cblock=(7,8);restrictions=[]
    for b,c in itertools.product(bblock,cblock):
        bout=next(v for v in bblock if v!=b);cout=next(v for v in cblock if v!=c)
        for x,z in ((bout,cout),(cout,bout)):
            y=c if x==bout else b
            first=[(b,c),tuple(sorted((1,z))),tuple(sorted((3,x)))]
            real={0,1,2,x,y}
            assert all(not(set(e)<=real) for e in first)
            initial=[0]*9
            initial[3]=initial[4]=1
            for pair in (bblock,cblock):
                keep=next(v for v in pair if v in real)
                for v in pair:
                    if v!=keep:initial[v]=-1 if v<keep else 1
            assert initial[:5]==sorted(initial[:5])
            assert initial[5:7]==sorted(initial[5:7]) and initial[7:9]==sorted(initial[7:9])
            assert {v for v,x in enumerate(initial) if x==0}==real
            restrictions.append(dict(first=first,real=sorted(real),initial=initial))
    assert len(restrictions)==8
    witnesses={}
    for aranks in itertools.combinations(range(9),5):
        branks=tuple(v for v in range(9) if v not in aranks)
        values=aranks+branks
        witnesses.setdefault(values.index(4),values)
    assert set(witnesses)==set(range(9))
    report=dict(status='VERIFIED',singleton_intersection_cases=singleton_cases,
                path_covers=covers,blind_311_restrictions=restrictions,
                median_positions_54=witnesses,uses_sat=False,enumerates_all_matchings=False,
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                proof_sha256=hashlib.sha256((HERE/'d13_feedback_round4_mergers.md').read_bytes()).hexdigest())
    out=HERE/'results/d13_feedback_round4-mergers-verification.json'
    out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('blind_311_restrictions','median_positions_54')},indent=2))


if __name__=='__main__':main()
