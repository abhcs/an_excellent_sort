#!/usr/bin/env python3
"""Replace all2728 partial-row trees by short cut-radius witnesses."""
from itertools import combinations
import gzip
import hashlib
import json
from pathlib import Path
import time
from d17_feedback_round8_patterns import prices
from d17_feedback_round7_screen import transport

ROOT=Path(__file__).parent


def main():
    start=time.monotonic();source=ROOT/'results/d17-feedback-fourteen-hand606-states.json'
    old=ROOT/'results/d17-feedback-round7-core-certificate.json.gz'
    base=[s[2:] for s in json.loads(source.read_text())['states']]
    records=[];sizes={};radii_hist={}
    for record in json.loads(gzip.decompress(old.read_bytes()))['cases']:
        if record['r']:continue
        code=record['m'];n=len(code);M=[(i,int(x,16)) for i,x in enumerate(code) if i<int(x,16)]
        family=[s+[0]*(n-12) for s in base]
        core={i:transport(s,M) for i,s in enumerate(family) if sum(s[a]==s[b]==0 for a,b in M)<n//2-3}
        _,cost,target=prices(list(core.values()))
        if cost>=target:
            found=None
            for k in range(3,len(core)):
                for ids in combinations(core,k):
                    trial={i:core[i] for i in ids};_,c,t=prices(list(trial.values()))
                    if c<t:found=trial;break
                if found:break
            assert found;core=found
        for i in tuple(core):
            trial={j:S for j,S in core.items() if j!=i};_,c,t=prices(list(trial.values()))
            if c<t:core=trial
        q,c,t=prices(list(core.values()));assert c<t
        radii={v:sum(v in S for S in core.values())-price for v,price in q.items()}
        assert min(radii.values())>=0 and max(radii.values())<=2
        for v in sorted(radii):
            while radii[v] and sum(radii.values())>len(core)+1:radii[v]-=1
        radii={v:r for v,r in radii.items() if r}
        incidence={v:sum(1<<j for j,S in enumerate(core.values()) if v in S) for v in range(n)}
        unique=[v for v,bits in incidence.items() if bits and list(incidence.values()).count(bits)==1]
        for chosen in combinations(unique,len(core)+1):
            if all((incidence[u]^incidence[v]).bit_count()>=2 for u,v in combinations(chosen,2)):
                radii={v:1 for v in chosen};break
        records.append(dict(m=code,s=list(core),r=sorted(radii.items())))
        sizes[len(core)]=sizes.get(len(core),0)+1
        key=str(tuple(sorted(radii.values())));radii_hist[key]=radii_hist.get(key,0)+1
    assert len(records)==2728
    certificate=dict(version=1,input_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                     round7_certificate_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),cases=records)
    raw=(json.dumps(certificate,separators=(',',':'))+'\n').encode()
    target=ROOT/'results/d17-feedback-round8-cut-certificate.json.gz'
    target.write_bytes(gzip.compress(raw,compresslevel=9,mtime=0))
    report=dict(status='CERTIFICATE_GENERATED',sat_used=False,cases=len(records),core_size_counts=sizes,
                radius_patterns=radii_hist,compressed_bytes=target.stat().st_size,
                certificate_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                seconds=round(time.monotonic()-start,4),
                scope='Finite selection of cut-radius witnesses; each local contradiction has one uniform hand proof')
    (ROOT/'results/d17-feedback-round8-cut-generation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
