#!/usr/bin/env python3
"""Independent all-signed-placement replay of the D13 rescheduling survivors."""
from itertools import combinations,product
from pathlib import Path
import hashlib,json,time

ROOT=Path(__file__).parent


def retained_dag(layers,placement):
    types=list(placement);tracks=list(range(13));depth={v:0 for v in range(13) if types[v]==0};edges=[]
    for layer in layers:
        for a,b in layer:
            if types[a]==types[b]==0:
                u,v=tracks[a],tracks[b];depth[u]=depth[v]=1+max(depth[u],depth[v]);edges.append((u,v))
            elif types[a]>types[b]:
                types[a],types[b]=types[b],types[a];tracks[a],tracks[b]=tracks[b],tracks[a]
    return max(depth.values(),default=0),len(edges)


def main():
    result=[];start=time.monotonic()
    for case in (0,116):
        source=ROOT/f'results/d13-hand-next-reschedule-two-{case:04d}.json';data=json.loads(source.read_text());assert data['status']=='SURVIVOR'
        layers=data['prefix']+data['next_layers'];checked={};eligible={}
        for r in (7,8):
            count=depth_two=0
            for sentinel_positions in combinations(range(13),13-r):
                for signs in product((-1,1),repeat=13-r):
                    p=[0]*13
                    for c,s in zip(sentinel_positions,signs):p[c]=s
                    d,g=retained_dag(layers,p);count+=1
                    if d<=2:
                        depth_two+=1;assert g>={7:5,8:7}[r],(case,p,d,g)
            checked[r]=count;eligible[r]=depth_two
        rec=dict(case_id=data['case_id'],status='VERIFIED_SURVIVOR',scope='Necessary rescheduling condition only; not a sorting network or a closed cover case',prefix=data['prefix'],next_layers=data['next_layers'],signed_placements_checked=checked,restrictions_reschedulable_into_two_layers=eligible,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
        result.append(rec);print(json.dumps(rec),flush=True)
    out=dict(status='VERIFIED',seconds=time.monotonic()-start,sat_used=False,cases=result,verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (ROOT/'results/d13-hand-next-reschedule-verification.json').write_text(json.dumps(out,indent=2)+'\n')

if __name__=='__main__':main()
