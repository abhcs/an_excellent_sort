#!/usr/bin/env python3
"""Find four-sentinel nine-real restrictions with a commuting two-layer prefix."""
import json
from itertools import combinations,product
from pathlib import Path


def prune(prefix,state):
    types=list(state);tracks=[i if v==0 else None for i,v in enumerate(state)];out=[]
    for layer in prefix:
        rr=[]
        for a,b in layer:
            if types[a]==types[b]==0:rr.append(tuple(sorted((tracks[a],tracks[b]))))
            elif types[a]>types[b]:
                types[a],types[b]=types[b],types[a]
                tracks[a],tracks[b]=tracks[b],tracks[a]
        out.append(rr)
    return types,tracks,out


def collect(case):
    families={};counts={}
    for S in combinations(range(13),4):
        for signs in product((-1,1),repeat=4):
            state=[0]*13
            for c,s in zip(S,signs):state[c]=s
            after,tracks,rr=prune(case['layers'],state)
            gates=rr[0]+rr[1]
            vertices=[v for e in gates for v in e]
            if len(gates)>3 or len(vertices)!=len(set(vertices)):continue
            key=tuple(after)
            families.setdefault(key,dict(initial=state,after=after,retained=rr))
            counts[str(tuple(map(len,rr)))]=counts.get(str(tuple(map(len,rr))),0)+1
    return dict(case_id=case['case_id'],prefix=case['layers'],family_size=len(families),profile_counts=counts,restrictions=list(families.values()))


def main():
    root=Path(__file__).parent
    cases=[json.loads(s) for s in (root/'prefixes/complete13.jsonl').read_text().splitlines()]
    result=[]
    for index in (0,116):
        data=collect(cases[index]);result.append(data)
        print(data['case_id'],data['family_size'],data['profile_counts'])
    (root/'results/d13-hand-next-commuting9.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
