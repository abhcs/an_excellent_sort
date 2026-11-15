#!/usr/bin/env python3
"""Independent small-network checks of interval endpoint constraints."""
import hashlib
import json
from pathlib import Path
import random

from interval_frontier import endpoints, add_state_bounds, actual_intervals
from probe_frontier import ProbeModel
from netsat import apply_layers, prefix_images


def random_layer(n,rng):
    wires=list(range(n))
    rng.shuffle(wires)
    return [tuple(sorted(wires[i:i+2])) for i in range(0,n-1,2) if rng.random()<0.8]


def main():
    rng=random.Random(20261115)
    records=[]
    for n in range(4,9):
        for trial in range(12):
            net=[random_layer(n,rng) for _ in range(3+trial%4)]
            prefix,free=net[:2],net[2:]
            images=[apply_layers(net,x) for x in range(1<<n)]
            possible=[set() for _ in range(n)]
            for x in range(1<<n):
                for i in range(n):
                    if not x&(1<<i):
                        y=x|(1<<i)
                        diff=images[x]^images[y]
                        assert diff.bit_count()==1
                        possible[diff.bit_length()-1].add(n-y.bit_count())
            intervals,_,_=actual_intervals(n,prefix,free)
            assert all(possible[c]==set(range(a,b+1)) for c,(a,b) in enumerate(intervals))
            expected=(max(map(len,possible))<=4 and max(sum(k in s for s in possible) for k in range(n))<=4)
            universe=prefix_images(n,prefix)
            model=ProbeModel(n,len(free)+2,universe,phi=False,nored0=False)
            lower,upper,_=endpoints(model,4)
            for t,layer in enumerate(free):
                chosen=set(layer)
                for edge,v in model.g[t].items():
                    model.add([v if edge in chosen else -v])
            for x in universe:
                state=model.simulate_to_cut(x,len(free))
                add_state_bounds(model,x,state,lower,upper)
            try:
                actual=model.S.solve()
                assert actual==expected,(n,trial,net,intervals,actual,expected)
            finally:
                model.S.delete()
            records.append(dict(n=n,trial=trial,cut=len(net),passes=actual,network=net,intervals=intervals))
    result=dict(status='VERIFIED',cases=len(records),positive=sum(r['passes'] for r in records),
                negative=sum(not r['passes'] for r in records),seed=20261115,
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                encoder_sha256=hashlib.sha256(Path(__file__).with_name('interval_frontier.py').read_bytes()).hexdigest(),records=records)
    out=Path(__file__).parent/'results/interval-frontier-checks.json'
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='records'}))


if __name__=='__main__':
    main()
