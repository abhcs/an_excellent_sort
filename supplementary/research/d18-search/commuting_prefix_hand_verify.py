#!/usr/bin/env python3
"""Independent direct-value and hand-price check of one D18 prefix exclusion."""
import hashlib
from itertools import combinations, permutations
import json
from pathlib import Path

ROOT=Path(__file__).parent


def main():
    source=ROOT/'results/combined-prefix-probe18.json'
    core_file=ROOT/'results/commuting-prefix-combined-prefix-probe18-r7-core.json'
    layers=json.loads(source.read_text())['layers'][:5]
    core=json.loads(core_file.read_text())
    C={7,10,12,13}
    expected=[C|{8,9,11},C|{4,11,16},C|{9,11,16},C|{9,14,16}]
    direct_runs=0
    placements=[]
    for entry,R in zip(core['states'],expected):
        assert entry['real_mask']==sum(1<<v for v in R)
        initial=entry['initial']
        reals=[v for v,x in enumerate(initial) if x==0]
        assert len(reals)==7
        pairs=entry['compressed_oriented_pairs']
        assert len(pairs)==2
        used=[v for pair in pairs for v in pair]
        assert len(set(used))==4 and set(used)<=set(reals)
        labels=entry['final_labels']
        assert {v for v in labels if v>=0}==set(reals)
        assert {i for i,v in enumerate(labels) if v>=0}==R
        types=list(initial)
        for layer in layers:
            for a,b in layer:types[a],types[b]=min(types[a],types[b]),max(types[a],types[b])
        assert {i for i,x in enumerate(types) if x==0}==R
        # All distinct-real assignments, not just ternary or binary replay.
        for values in permutations(range(1,8)):
            original=[-100 if x<0 else 100 if x>0 else 0 for x in initial]
            for v,x in zip(reals,values):original[v]=x
            actual=original.copy()
            for layer in layers:
                for a,b in layer:actual[a],actual[b]=min(actual[a],actual[b]),max(actual[a],actual[b])
            compressed={v:original[v] for v in reals}
            for lo,hi in pairs:
                compressed[lo],compressed[hi]=min(compressed[lo],compressed[hi]),max(compressed[lo],compressed[hi])
            predicted=[compressed[label] if label>=0 else -100 if t<0 else 100
                       for label,t in zip(labels,types)]
            assert actual==predicted
            direct_runs+=1
        placements.append(dict(initial=initial,cut_real_positions=sorted(R),
                               compressed_oriented_pairs=pairs,final_labels=labels))
    assert len(placements)==4 and direct_runs==20160
    prices={v:2 if v in C else 1 if v in {9,11,16} else 0 for v in range(18)}
    checked=0
    for a,b in combinations(range(18),2):
        weight=sum(a in R and b in R for R in expected)
        assert weight<=prices[a]+prices[b]
        checked+=1
    assert sum(prices.values())==11<4*3
    report=dict(status='VERIFIED',n=18,prefix_depth=5,excluded_completion_depth=10,
                proof_uses_sat=False,proof_uses_exhaustive_search=False,
                scope='Every depth-ten completion of this specified five-layer prefix is excluded; not a complete two-layer cover case',
                prefix=layers,placements=placements,common_reals=sorted(C),
                nonzero_vertex_prices={v:p for v,p in prices.items() if p},
                bound_on_sum_of_four_retained_counts=11,required_sum=12,
                direct_real_permutation_runs=direct_runs,pair_price_checks=checked,
                sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in (source,core_file,Path(__file__))})
    (ROOT/'results/commuting-prefix18-hand-proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('placements','prefix','sha256')},indent=2))


if __name__=='__main__':main()
