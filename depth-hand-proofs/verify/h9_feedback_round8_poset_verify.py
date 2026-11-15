#!/usr/bin/env python3
"""Check the poset extraction and bounded D18 component-recognition census.

Standard library only. No solver or general signed-image search is used.
"""
from collections import Counter
import hashlib
import itertools
import json
import time
from pathlib import Path

ROOT=Path(__file__).parents[1]
SOURCE=ROOT.parent/'d18-search/results/rank-layer-round6-hand-certificate.json'
FIRST=((0,1),(2,3),(4,5))
SECONDS=(((0,3),(1,6),(4,7)),((0,3),(1,6),(5,7)))
ACCEPTED={'h9-feedback-round6-certificate.json':'c258d102a019b789a5a01edfae1b410629d1e61f8a2ba3f1976e09c6eabf05ae',
          'h9-feedback-round7-certificate.json':'d9237f438467d95088717b2016cc8734453ea62f4540f3ecbe48994a9cc6ca60'}


def run(layers,values):
    out=list(values)
    for layer in layers:
        for a,b in layer:
            out[a],out[b]=min(out[a],out[b]),max(out[a],out[b])
    return tuple(out)


def component_image(vertices,gates):
    index={v:i for i,v in enumerate(vertices)}
    word=[(index[a],index[b])for a,b in gates if a in index]
    assert all(b in index for a,b in gates if a in index)
    return {run((word,),x)for x in itertools.permutations(range(len(vertices)))}


def restricted(prefix,signs):
    # Compact real labels here differ from the discovery script's original
    # eighteen-wire labels. Only deterministic sentinel routes move them.
    original=[i for i,x in enumerate(signs)if x==0]
    owner=[original.index(i)if i in original else None for i in range(len(signs))]
    state=list(signs);gates=[]
    for layer in prefix:
        for a,b in layer:
            if state[a]==state[b]==0:
                gates.append((owner[a],owner[b]))
            elif state[a]>state[b]:
                state[a],state[b]=state[b],state[a]
                owner[a],owner[b]=owner[b],owner[a]
    adjacency=[1<<i for i in range(len(original))]
    for a,b in gates:
        adjacency[a]|=1<<b;adjacency[b]|=1<<a
    remaining=(1<<len(original))-1;parts=[]
    while remaining:
        frontier=remaining&-remaining;mask=0
        while frontier:
            v=frontier.bit_length()-1;frontier &= ~(1<<v)
            mask |= 1<<v
            frontier |= adjacency[v]&~mask
        remaining &= ~mask
        parts.append(tuple(i for i in range(len(original))if mask>>i&1))
    parts.sort(key=lambda p:(-len(p),p))
    positions={label:i for i,label in enumerate(owner)if label is not None}
    return dict(original=original,gates=gates,parts=parts,positions=positions,state=state)


def normalized_patterns(k):
    if k==0:
        for bits in range(512):
            yield tuple(v for pair in range(9)for v in ((0,1)if bits>>pair&1 else(-1,0)))
    else:
        assert k==1
        for real in range(9):
            for sent in range(9):
                if sent==real:continue
                singles=[i for i in range(9)if i not in(real,sent)]
                for signs in((-1,-1),(-1,1),(1,1)):
                    for bits in range(128):
                        result=[0]*18;result[2*sent:2*sent+2]=signs
                        for j,pair in enumerate(singles):
                            result[2*pair:2*pair+2]=(0,1)if bits>>j&1 else(-1,0)
                        yield tuple(result)


def packing(sizes,capacities=(5,3,1)):
    if not sizes:return True
    size,*tail=sizes
    for i,capacity in enumerate(capacities):
        if capacity>=size:
            changed=list(capacities);changed[i]-=size
            if packing(tail,tuple(changed)):return True
    return False


def canonical_and_controls():
    core=(0,1,2,3,6);fork=(4,5,7)
    u={x for x in itertools.permutations(range(5))if x[0]<x[3]and x[0]<x[4]and x[1]<x[4]and x[2]<x[3]}
    assert len(u)==16
    controls=[]
    for polarity,second in zip(('minimum','maximum'),SECONDS):
        prefix=(FIRST,second)
        gates=[e for layer in prefix for e in layer]
        assert component_image(core,gates)==u
        fork_expected={(0,1,2),(0,2,1)}if polarity=='minimum'else{(0,1,2),(1,0,2)}
        assert component_image(fork,gates)==fork_expected
        # The three extra layers route real tracks past fixed sentinels.
        ambient=prefix+(((0,17),),((1,16),),((4,15),))
        signs=[0]*9+[-1]*9
        reduction=restricted(ambient,signs)
        assert reduction['parts']==[(0,1,2,3,6),(4,5,7),(8,)]
        assert component_image(reduction['parts'][0],reduction['gates'])==u
        assert component_image(reduction['parts'][1],reduction['gates'])==fork_expected
        assert reduction['positions']=={0:17,1:16,2:2,3:3,4:15,5:5,6:6,7:7,8:8}
        assert sorted(i for i,s in enumerate(reduction['state'])if s==0)==[2,3,5,6,7,8,15,16,17]
        for real_values in itertools.product((0,1),repeat=9):
            values=real_values+(-1,)*9
            direct=run(ambient,values)
            reduced=run((reduction['gates'],),real_values)
            assert all(direct[reduction['positions'][i]]==reduced[i]for i in range(9))
            assert all(direct[i]==-1 for i,s in enumerate(reduction['state'])if s)
        controls.append(dict(polarity=polarity,ambient_width=18,fixed_layers=5,real_tracks=9,
                             component_orders=[16,2,1],routed_real_positions=[2,3,5,6,7,8,15,16,17],binary_replays=512))
    return dict(U5_orders=16,fork_orders=2,product_order_types=16128,controls=controls)


def census(start):
    source=json.loads(SOURCE.read_text())
    probe_file=ROOT/'results/h9-feedback-round8-poset-probe.json'
    probe=json.loads(probe_file.read_text())
    assert probe['source_sha256']==hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    expected_counts={'beam00':(64,4,2),'beam16':(128,5,1),'beam32':(64,3,2)}
    outputs=[]
    for record,saved in zip(source['records'],probe['records']):
        name=record['name'];assert name==saved['name']
        prefix=record['prefix'][:5]
        assert prefix[0]==[[2*i,2*i+1]for i in range(9)]
        hist=Counter();images=Counter();recognized=[];counts={};candidate_signs=set();image_runs=0
        for k in(0,1):
            count=0
            for signs in normalized_patterns(k):
                reduction=restricted(prefix,signs)
                sizes=tuple(map(len,reduction['parts']))
                assert sum(sizes)==9
                hist[k,sizes]+=1;count+=1
                if not packing(sizes):continue
                assert sizes==(5,3,1)
                candidate_signs.add(signs)
                first=component_image(reduction['parts'][0],reduction['gates'])
                second=component_image(reduction['parts'][1],reduction['gates'])
                image_runs+=126
                images[len(first),len(second)]+=1
                # Too few five-component outputs for any relabelled U image.
                assert len(first)<16
            counts[k]=count
            assert time.monotonic()-start<30
        assert counts=={0:512,1:27648}
        assert candidate_signs=={tuple(c['initial'])for c in saved['candidates']}
        assert hist==Counter({(r['first_rr'],tuple(r['sizes'])):r['count']for r in saved['histogram']})
        number,u,f=expected_counts[name]
        assert images=={(u,f):number}
        outputs.append(dict(name=name,patterns=28160,first_rr_counts=counts,packing_survivors=number,
                            component_image_sizes=[u,f,1],component_order_replays=image_runs,recognized=0))
    return dict(records=outputs,total_patterns=84480,component_order_replays=sum(x['component_order_replays']for x in outputs),
                discovery_report_sha256=hashlib.sha256(probe_file.read_bytes()).hexdigest())


def main():
    start=time.monotonic()
    for name,expected in ACCEPTED.items():
        assert hashlib.sha256((ROOT/'results'/name).read_bytes()).hexdigest()==expected
    controls=canonical_and_controls()
    scanned=census(start)
    note=ROOT/'h9_feedback_round8_poset.md'
    report=dict(status='VERIFIED',solver_free=True,ambient_width_theorem=True,
                exactly_nine_real_tracks_required=True,complete_signed_image_search=False,
                additional_H9_classes=0,additional_D18_prefixes=0,
                canonical=controls,census=scanned,accepted_certificate_sha256=ACCEPTED,
                source_prefix_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                note_sha256=hashlib.sha256(note.read_bytes()).hexdigest(),
                checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                elapsed_seconds=time.monotonic()-start)
    (ROOT/'results/h9-feedback-round8-poset-proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
