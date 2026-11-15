#!/usr/bin/env python3
"""Remove common fixed sentinels while preserving two-layer RR counts.

Only the first layer's transported types and the two retained counts are
preserved after normalization. No claim about final type positions is made.
"""
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'depth-hand-proofs/verify'))
from netlib import matchings


def project(n,layers,fixed):
    assert len(layers)==2 and all(v in (-1,1) for v in fixed.values())
    remaining=[i for i in range(n) if i not in fixed]
    labels={physical:i for i,physical in enumerate(remaining)}
    tracks=[('f',fixed[i]) if i in fixed else ('v',labels[i]) for i in range(n)]
    projected=[]
    for t,layer in enumerate(layers):
        row=[]
        for a,b in layer:
            x,y=tracks[a],tracks[b]
            if x[0]==y[0]=='v':
                if t==0:
                    assert x[1]<y[1]
                # Second-layer orientation changes no RR count.
                row.append(tuple(sorted((x[1],y[1]))))
            elif x[0]==y[0]=='f':
                tracks[a],tracks[b]=sorted((x,y),key=lambda q:q[1])
            else:
                constant=x if x[0]=='f' else y
                variable=y if x[0]=='f' else x
                tracks[a],tracks[b]=(constant,variable) if constant[1]==-1 else (variable,constant)
        used=[v for edge in row for v in edge]
        assert len(used)==len(set(used))
        projected.append(row)
    return remaining,projected


def counts(layers,state):
    state=list(state)
    result=[]
    for layer in layers:
        result.append(sum(state[a]==state[b]==0 for a,b in layer))
        for a,b in layer:
            state[a],state[b]=min(state[a],state[b]),max(state[a],state[b])
    return result


def random_matching(n,rng):
    order=list(range(n))
    rng.shuffle(order)
    return [tuple(sorted(order[i:i+2])) for i in range(0,n-1,2) if rng.random()<0.8]


def main():
    small=0
    for n in range(2,6):
        all_layers=matchings(n)
        for first,second in itertools.product(all_layers,repeat=2):
            for c in range(n):
                for sign in (-1,1):
                    remaining,projected=project(n,[first,second],{c:sign})
                    for values in itertools.product((-1,0,1),repeat=n-1):
                        state=[sign]*n
                        for k,v in zip(remaining,values):
                            state[k]=v
                        assert counts([first,second],state)==counts(projected,values)
                        small+=1
    data=json.loads((ROOT/'d18-search/results/d17-feedback-peaks/result.json').read_text())
    states=data['states']
    fixed={c:states[0][c] for c in range(17) if states[0][c] in (-1,1)
           and all(state[c]==states[0][c] for state in states)}
    assert fixed=={0:-1,3:-1,11:-1}
    keep=[c for c in range(17) if c not in fixed]
    template=[[s[c] for c in keep] for s in states]
    assert len(keep)==14 and all(s.count(0)==9 for s in template)
    rng=random.Random(20261115)
    large=0
    for n in (14,17,18,20,24):
        for _ in range(100):
            positions=sorted(rng.sample(range(n),14))
            constants={c:rng.choice((-1,1)) for c in range(n) if c not in positions}
            layers=[random_matching(n,rng),random_matching(n,rng)]
            remaining,projected=project(n,layers,constants)
            assert remaining==positions
            for state in template:
                expanded=[constants.get(c,0) for c in range(n)]
                for c,value in zip(positions,state):
                    expanded[c]=value
                assert counts(layers,expanded)==counts(projected,state)
                large+=1
    result=dict(status='VERIFIED',small_all_assignment_checks=small,
                template_embedding_checks=large,widths=[14,17,18,20,24],
                original_kept_wires=keep,removed_common_sentinels=fixed,template=template,
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    path=ROOT/'d18-search/results/fixed-sentinel-pruning.json'
    path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='template'}))


if __name__=='__main__':
    main()
