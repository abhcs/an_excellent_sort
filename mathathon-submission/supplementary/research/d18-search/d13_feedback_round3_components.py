#!/usr/bin/env python3
"""Independent scalar nine-real component scan of saved D13 four-layer witnesses.

Rejecting a saved L3,L4 witness is not closing its complete two-layer case.
No SAT is run. All C(13,4)*16 signed placements are checked per prefix.
"""
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import time

from netsat import verify_all

HERE=Path(__file__).resolve().parent


def placements():
    for sentinel in itertools.combinations(range(13),4):
        for signs in itertools.product((-1,1),repeat=4):
            initial=[0]*13
            for v,s in zip(sentinel,signs):initial[v]=s
            yield initial


def evaluate(prefix,initial):
    types=initial[:]
    labels=[v if x==0 else -1 for v,x in enumerate(types)]
    parent=list(range(13));sizes=[1]*13
    def find(v):
        while parent[v]!=v:
            parent[v]=parent[parent[v]];v=parent[v]
        return v
    for a,b in prefix:
        if types[a]==types[b]==0:
            x,y=find(labels[a]),find(labels[b])
            if x!=y:
                if sizes[x]<sizes[y]:x,y=y,x
                parent[y]=x;sizes[x]+=sizes[y]
                if sizes[x]>=5:return None
        elif types[a]>types[b]:
            types[a],types[b]=types[b],types[a]
            labels[a],labels[b]=labels[b],labels[a]
    components={}
    for wire,label in enumerate(labels):
        if label>=0:components.setdefault(find(label),[]).append(wire)
    return sorted(components.values(),key=lambda group:(-len(group),group))


def scan(name,prefix,all_placements):
    start=time.monotonic();counter=Counter();example=None
    flat=[tuple(e) for layer in prefix for e in layer]
    for p in all_placements:
        components=evaluate(flat,p)
        if components is None:continue
        shape=tuple(map(len,components));counter[shape]+=1
        if example is None:example=dict(initial=p,components=components,component_sizes=shape)
    return dict(name=name,prefix=prefix,placements_checked=len(all_placements),
                obstructed_placements=sum(counter.values()),
                component_shapes={','.join(map(str,k)):v for k,v in sorted(counter.items())},
                example=example,seconds=time.monotonic()-start)


def audit_component_chains(prefix,example):
    """Construct every binary sorted-chain output on the recorded components."""
    initial=example['initial'];components=example['components']
    def run(values):
        values=values[:]
        for layer in prefix:
            for a,b in layer:values[a],values[b]=min(values[a],values[b]),max(values[a],values[b])
        return values
    reference=run([-100 if x<0 else 100 if x>0 else v+1 for v,x in enumerate(initial)])
    output_orders=[sorted(group,key=lambda v:reference[v]) for group in components]
    input_orders=[sorted(reference[v]-1 for v in group) for group in components]
    checked=0
    for zeros in itertools.product(*(range(len(group)+1) for group in components)):
        values=[-100 if x<0 else 100 if x>0 else None for x in initial]
        expected={}
        for ins,outs,z in zip(input_orders,output_orders,zeros):
            for j,v in enumerate(ins):values[v]=int(j>=z)
            for j,v in enumerate(outs):expected[v]=int(j>=z)
        actual=run(values)
        assert all(actual[v]==x for v,x in expected.items())
        checked+=1
    return checked


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cases',default='all');args=ap.parse_args()
    cover=HERE/'prefixes/complete13.jsonl'
    cases=[json.loads(line) for line in cover.read_text().splitlines()]
    chosen=list(range(117)) if args.cases=='all' else [int(x) for x in args.cases.split(',')]
    all_placements=list(placements());assert len(all_placements)==11440
    rows=[];start=time.monotonic()
    for i in chosen:
        source=HERE/f'results/profile-frontier13/n13-r{i:04d}.json'
        saved=json.loads(source.read_text())
        assert saved['status']=='SURVIVOR'
        row=scan(cases[i]['case_id'],cases[i]['layers']+saved['next_layers'],all_placements)
        if row['example']:
            row['direct_component_chain_replays']=audit_component_chains(row['prefix'],row['example'])
        row['saved_witness_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
        rows.append(row)
        if len(rows)%20==0:print('scanned',len(rows),'witnesses',flush=True)
    # Positive control at the cut with four remaining layers of a known sorter.
    positive_source=HERE/'results/complete13-d9-control/n13-r0116/result.json'
    positive_net=json.loads(positive_source.read_text())['network']
    assert verify_all(13,positive_net)
    positive=scan('known13-depth9-cut5',positive_net[:5],all_placements)
    assert positive['obstructed_placements']==0
    report=dict(status='VERIFIED',scope='Saved four-layer relaxation witnesses, not entire cover cases',
                cases_scanned=len(rows),witnesses_rejected=sum(bool(r['obstructed_placements']) for r in rows),
                witnesses_surviving=sum(not r['obstructed_placements'] for r in rows),rows=rows,
                direct_component_chain_replays=sum(r.get('direct_component_chain_replays',0) for r in rows),
                positive_sorter_binary_inputs=8192,
                positive_control=positive,seconds=time.monotonic()-start,
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                cover_sha256=hashlib.sha256(cover.read_bytes()).hexdigest())
    name='all' if args.cases=='all' else 'selected'
    path=HERE/f'results/d13_feedback_round3-components-{name}.json'
    path.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('rows','positive_control')},indent=2))


if __name__=='__main__':main()
