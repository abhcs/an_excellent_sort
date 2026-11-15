#!/usr/bin/env python3
"""Check two additional six-layer D18 prefix exclusions by explicit values."""
import hashlib
from itertools import combinations,permutations
import json
from pathlib import Path

ROOT=Path(__file__).parent


def check(layers,entry):
    initial=entry['initial'];real=[v for v,x in enumerate(initial) if x==0]
    pairs=entry['compressed_oriented_pairs'];labels=entry['final_labels']
    used=[v for e in pairs for v in e]
    assert len(used)==len(set(used)) and set(used)<=set(real)
    state=initial.copy();track=[v if x==0 else -1 for v,x in enumerate(state)]
    trace=[]
    for layer in layers:
        row=[]
        for a,b in layer:
            if state[a]==state[b]==0:row.append([track[a],track[b]])
            elif state[a]>state[b]:state[a],state[b]=state[b],state[a];track[a],track[b]=track[b],track[a]
        trace.append(row)
    assert track==labels
    assert sum(1<<v for v,t in enumerate(state) if t==0)==entry['real_mask']
    runs=0
    for values in permutations(range(1,len(real)+1)):
        original=[-100 if x<0 else 100 if x>0 else 0 for x in initial]
        for v,x in zip(real,values):original[v]=x
        output=original.copy()
        for layer in layers:
            for a,b in layer:output[a],output[b]=sorted((output[a],output[b]))
        compressed={v:original[v] for v in real}
        for a,b in pairs:compressed[a],compressed[b]=sorted((compressed[a],compressed[b]))
        predicted=[compressed[v] if v>=0 else -100 if t<0 else 100 for v,t in zip(labels,state)]
        assert predicted==output;runs+=1
    return dict(**entry,retained_track_trace=trace,direct_value_runs=runs)


def main():
    budget_file=ROOT/'results/commuting-prefix-six-budget-counterexample18-r5.json'
    cube_file=ROOT/'results/commuting-prefix-six-cube-free-prefix-probe18-r5.json'
    budget=json.loads(budget_file.read_text());cube=json.loads(cube_file.read_text())
    blind=next(s for s in budget['states'] if not s['compressed_oriented_pairs'])
    blind=check(budget['layers'],blind)
    assert all(not row for row in blind['retained_track_trace'])
    witnesses=[check(cube['layers'],cube['states'][i]) for i in cube['classification']['core_indices']]
    assert len(witnesses)==4 and all(len(s['compressed_oriented_pairs'])==1 for s in witnesses)
    prices={v:3 if v in {7,11,12} else 1 if v in {5,8,10,13,15} else 0 for v in range(18)}
    for a,b in combinations(range(18),2):
        weight=sum(bool(s['real_mask']>>a&1) and bool(s['real_mask']>>b&1) for s in witnesses)
        assert 2*weight<=prices[a]+prices[b]
    assert sum(prices.values())==14<2*8
    report=dict(status='VERIFIED',scope='Two specified six-layer prefixes cannot extend to depth10; no complete two-layer cover case is closed',
                sat_used=False,exhaustive_search_is_proof_premise=False,
                direct_real_permutation_runs=blind['direct_value_runs']+sum(s['direct_value_runs'] for s in witnesses),
                direct_blinding=dict(prefix=budget['layers'],restriction=blind,remaining_layers=4,required_depth_D5=5),
                four_restriction_prices=dict(prefix=cube['layers'],restrictions=witnesses,twice_prices=prices,twice_bound=14,required_sum=8),
                sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in (budget_file,cube_file,Path(__file__))})
    (ROOT/'results/commuting-prefix18-additional-hand-proofs.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('direct_blinding','four_restriction_prices','sha256')},indent=2))


if __name__=='__main__':main()
