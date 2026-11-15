#!/usr/bin/env python3
"""Replay short conditional hand certificates and their positive controls.

No SAT solver is used. Input rank-k probes have n-1-k fixed ones.
A token and a 0/1 at its partner witness rank-k below/above that partner.
"""
import hashlib
import json
from itertools import combinations
from pathlib import Path
from d13_hand_probe_table import apply, check_table
from d13_hand_matching import analyze

ROOT=Path(__file__).parent


def read(name):
    return json.loads((ROOT/'results'/name).read_text())


def check_rows(n,layers,k,S,rows):
    coverage=set()
    for r in rows:
        x,p=r['input_zero'],r['input_star']
        assert x.bit_count()==n-1-k and not x>>p&1
        a,b=apply(layers,x),apply(layers,x|(1<<p))
        assert a==r['output_zero'] and a^b==1<<r['output_star'] and a&b==a
        c=r['output_star'];assert c in S
        coverage.add(('wire',c))
        for q in S:
            if q!=c:coverage.add((min(c,q),max(c,q),a>>q&1))
    return coverage


def main():
    single=read('d13-hand-case116-rank-separation-certificate.json')
    n=single['n'];layers=single['layers'];k=single['rank'];S=single['positions']
    obligations=check_table(n,layers,k,S,single['probe_rows'])
    assert len(S)==5
    double=read('d13-hand-case116-two-rank-certificate.json')
    assert double['n']==n and double['layers']==layers
    T=set(double['potential_vertices']);sets=[]
    for item in double['ranks']:
        k=item['rank'];S=set(item['positions']);sets.append(S)
        outside=sorted(S-T)
        assert outside==item['separated_positions']
        coverage=check_rows(n,layers,k,S,item['probe_rows'])
        wanted={('wire',c) for c in S}|{(a,b,v) for a,b in combinations(outside,2) for v in (0,1)}
        assert wanted<=coverage
    assert sets[0]&sets[1]<=T
    assert sum(map(len,sets))-len(T)>8
    # Strong separate-rank controls: these are actual feasible matchings,
    # not merely fractional or cardinality relaxation solutions.
    separate={3:[(0,1),(2,6),(3,9),(4,5)],9:[(2,4),(6,8),(7,9),(10,11)]}
    separate_sizes={}
    for rank,M in separate.items():
        nxt=analyze(n,layers+[M])
        size=len(nxt['supports'][rank]);assert size==4
        separate_sizes[rank]=size
    cut5=analyze(n,layers)
    assert max(map(len,cut5['supports']))<=8
    assert max(hi-lo+1 for lo,hi in cut5['intervals'])<=8
    # A depth-nine sorter extending exactly the same two-layer prefix.
    pos=read('probe-frontier13-d9-positive.json')
    fullnet=pos['prefix']+pos['free_layers']+pos['ending_matchings']
    assert fullnet[:2]==layers[:2] and len(fullnet)==9
    for x in range(1<<n):
        w=x.bit_count();target=((1<<w)-1)<<(n-w)
        assert apply(fullnet,x)==target
    at6=analyze(n,fullnet[:6]);at7=analyze(n,fullnet[:7])
    assert max(map(len,at7['supports']))<=4
    assert max(hi-lo+1 for lo,hi in at7['intervals'])<=4
    # The same separator search must reject this extendible positive control:
    # a five-vertex set with no reducing edge cannot exist before its layer7.
    for rank,support in enumerate(at6['supports']):
        edges={tuple(map(int,e.split(','))) for e,rs in at6['edge_ranks'].items() if rank in rs}
        for S in combinations(support,5):
            assert any(e in edges for e in combinations(S,2))
    paths=[ROOT/'d13_hand_verify.py',ROOT/'d13_hand_probe_table.py',ROOT/'d13_hand_matching.py',ROOT/'results/d13-hand-case116-rank-separation-certificate.json',ROOT/'results/d13-hand-case116-two-rank-certificate.json']
    result=dict(status='VERIFIED',sat_used_by_verifier=False,scope='One specified five-layer continuation of case116 only; not a refutation of all continuations',single_rank=dict(rank=single['rank'],positions=single['positions'],probe_rows=len(single['probe_rows']),covered_obligations=obligations,next_layer_support_lower_bound=5),two_rank=dict(ranks=[3,9],initial_total=16,potential_vertices=sorted(T),maximum_total_reductions=6,next_layer_total_lower_bound=10,probe_rows=sum(len(x['probe_rows']) for x in double['ranks']),separate_rank_matchings={str(k):v for k,v in separate.items()},separate_rank_final_sizes=separate_sizes),cut5_max_rank_degree=max(map(len,cut5['supports'])),cut5_max_wire_degree=max(hi-lo+1 for lo,hi in cut5['intervals']),positive_control=dict(binary_inputs_checked=1<<n,depth=9,cut=7,max_rank_degree=max(map(len,at7['supports'])),max_wire_degree=max(hi-lo+1 for lo,hi in at7['intervals']),no_five_position_separator_at_cut6=True),sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    (ROOT/'results/d13-hand-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
