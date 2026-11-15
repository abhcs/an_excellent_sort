#!/usr/bin/env python3
"""Compress partial-row price feedback into unsigned small hypergraphs."""
from itertools import combinations,permutations
import gzip
import json
from pathlib import Path
import time
from d17_feedback_round8_patterns import prices
from d17_feedback_round7_screen import transport

ROOT=Path(__file__).parent
CACHE={}


def canonical(sets):
    vertices=sorted(set.union(*sets));m=len(sets)
    columns=tuple(sorted(sum((1<<i) for i,S in enumerate(sets) if v in S) for v in vertices))
    cachekey=(m,columns)
    if cachekey in CACHE:return CACHE[cachekey]
    best=None
    for p in permutations(range(m)):
        image=tuple(sorted(sum(1<<j for j,i in enumerate(p) if bit>>i&1) for bit in columns))
        if best is None or image<best:best=image
    CACHE[cachekey]=best
    return best


def main():
    start=time.monotonic();base=[s[2:] for s in json.loads((ROOT/'results/d17-feedback-fourteen-hand606-states.json').read_text())['states']]
    cert=json.loads(gzip.decompress((ROOT/'results/d17-feedback-round7-core-certificate.json.gz').read_bytes()))
    sizes={};patterns={};equality=[];total=0
    for record in cert['cases']:
        if record['r']:continue
        code=record['m'];n=len(code);M=[(i,int(x,16)) for i,x in enumerate(code) if i<int(x,16)]
        family=[s+[0]*(n-12) for s in base]
        required={i:transport(s,M) for i,s in enumerate(family) if sum(s[a]==s[b]==0 for a,b in M)<n//2-3}
        core=dict(required);q,cost,target=prices(list(core.values()))
        if cost>=target:
            found=None
            for k in range(3,len(core)):
                for ids in combinations(core,k):
                    trial={i:core[i] for i in ids};pq,pc,pt=prices(list(trial.values()))
                    if pc<pt:found=trial;break
                if found:break
            if found:core=found
            else:
                equality.append(dict(code=code,required={i:sorted(S) for i,S in core.items()},prices=q));continue
        for i in tuple(core):
            trial={j:S for j,S in core.items() if i!=j}
            pq,pc,pt=prices(list(trial.values()))
            if pc<pt:core=trial
        sets=list(core.values());key=(len(sets),canonical(sets))
        q,cost,target=prices(sets);assert cost<target
        if key not in patterns:
            patterns[key]=dict(size=len(sets),columns=key[1],count=0,example=code,
                               state_ids=list(core),sets=[sorted(S) for S in sets],
                               doubled_prices=q,cost=cost,target=target)
        patterns[key]['count']+=1;sizes[len(sets)]=sizes.get(len(sets),0)+1;total+=1
    report=dict(status='COMPLETED_FEEDBACK',sat_used=False,strict_cases=total,core_size_counts=sizes,
                template_count=len(patterns),canonical_cache_size=len(CACHE),
                templates=sorted(patterns.values(),key=lambda p:(p['size'],p['columns'])),
                equality_cases=equality,seconds=round(time.monotonic()-start,4))
    (ROOT/'results/d17-feedback-round8-templates.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='templates'},indent=2))


if __name__=='__main__':main()
