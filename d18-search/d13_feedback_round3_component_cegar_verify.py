#!/usr/bin/env python3
"""Raw-placement replay and guarded-cut translation audit, no SAT solver."""
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'depth-hand-proofs/verify'))
from sentinel_cegar import Master
from d13_feedback_round3_components import placements, scan


def step(types,layer):
    count=sum(types[a]==types[b]==0 for a,b in layer)
    for a,b in layer:types[a],types[b]=min(types[a],types[b]),max(types[a],types[b])
    return count


def main():
    start=time.monotonic()
    source=HERE/'results/d13_feedback_round3-component-cegar-r0116.json'
    result=json.loads(source.read_text());assert result['status']=='SURVIVOR'
    cover=HERE/'prefixes/complete13.jsonl'
    assert hashlib.sha256(cover.read_bytes()).hexdigest()==result['cover_sha256']
    case=next(json.loads(line) for line in cover.read_text().splitlines()
              if json.loads(line)['case_id']==result['case_id'])
    assert case['layers']==result['prefix']
    prefix=result['prefix'];layers=result['next_layers'];records=[]
    for r in (5,7):
        checked=blind=0
        for sentinel in itertools.combinations(range(13),13-r):
            for signs in itertools.product((-1,1),repeat=13-r):
                checked+=1;types=[0]*13
                for v,s in zip(sentinel,signs):types[v]=s
                retained=[step(types,layer) for layer in prefix]
                if any(retained):continue
                blind+=1;profile=[step(types,layer) for layer in layers]
                assert (any(profile) if r==5 else min(profile)>=2 and max(profile)==3)
        records.append(dict(reals=r,raw_signed_placements=checked,blind_two_placements=blind,violations=0))
    nine=scan(result['case_id'],prefix+layers,list(placements()))
    assert nine['obstructed_placements']==0
    # A stored cut is sound if its nine-real blocks are unions of cut3
    # interaction components, with each block of size at most4.
    skeleton=Master(13,3,first=0,adjacent=False,no_repeat=True)
    cut_count=0
    for record in result['component_cuts']:
        types=record['initial'][:];labels=[v if x==0 else -1 for v,x in enumerate(types)]
        history=[]
        for layer in prefix+[record['third_layer']]:
            for a,b in layer:
                if types[a]==types[b]==0:history.append((labels[a],labels[b]))
                elif types[a]>types[b]:
                    types[a],types[b]=types[b],types[a];labels[a],labels[b]=labels[b],labels[a]
        groups=record['cut3_track_groups']
        owner={v:i for i,g in enumerate(groups) for v in g}
        assert sum(map(len,groups))==len(owner)==9 and max(map(len,groups))<=4
        assert set(owner)=={v for v,x in enumerate(types) if x==0}
        original_owner={labels[v]:i for v,i in owner.items()}
        assert all(original_owner[a]==original_owner[b] for a,b in history)
        chosen=set(map(tuple,record['third_layer']));used={v for e in chosen for v in e}
        idle=[v for v in range(13) if v not in used]
        clause=[-skeleton.g[1,a,b] for a,b in chosen]
        clause += [skeleton.g[1,a,b] for a,b in itertools.combinations(idle,2)]
        clause += [skeleton.g[2,a,b] for a,b in skeleton.pairs if a in owner and b in owner and owner[a]!=owner[b]]
        assert set(clause)==set(record['clause'])
        cut_count+=1
    report=dict(status='VERIFIED',case_id=result['case_id'],next_layers=layers,
                profile_replays=records,nine_real_replay=nine,guarded_cuts_checked=cut_count,
                seconds=time.monotonic()-start,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                input_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    output=HERE/'results/d13_feedback_round3-component-cegar-r0116-verification.json'
    output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='nine_real_replay'},indent=2))


if __name__=='__main__':main()
