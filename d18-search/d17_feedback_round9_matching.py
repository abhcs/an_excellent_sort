#!/usr/bin/env python3
"""Exact static frontier via minimum Hamming-cost perfect matchings.

A maximum RR matching on each odd nine-set crosses each set once. Thus its
total signature-distance cost is exactly the number of states. We add one
never-real dummy to width17 and use maximum-cardinality perfect matchings.
Positive results are replayable witnesses; negative optimum values are
discovery unless separately supported by an explicit price bound.
"""
from collections import Counter
import hashlib
from itertools import combinations
import json
from pathlib import Path
import time
import networkx as nx
from two_layer_cover import half_blind_family,type_step

ROOT=Path(__file__).parent


def main():
    start=time.monotonic();source=ROOT/'prefixes/complete17.jsonl'
    cases=[json.loads(s) for s in source.read_text().splitlines()];records=[];hist=Counter()
    for case in cases:
        states=[type_step(s,case['layers'][1]) for s in half_blind_family(17,case['layers']).values()]
        signatures=[sum(1<<j for j,s in enumerate(states) if s[v]==0) for v in range(17)]+[0]
        graph=nx.Graph();graph.add_nodes_from(range(18))
        graph.add_weighted_edges_from((a,b,(signatures[a]^signatures[b]).bit_count()) for a,b in combinations(range(18),2))
        matching=sorted(tuple(sorted(e)) for e in nx.min_weight_matching(graph))
        assert len(matching)==9 and len({v for e in matching for v in e})==18
        cost=sum((signatures[a]^signatures[b]).bit_count() for a,b in matching)
        M=[e for e in matching if 17 not in e]
        profiles=[sum(s[a]==s[b]==0 for a,b in M) for s in states]
        assert cost>=len(states) and (cost==len(states))==all(p==4 for p in profiles)
        kind='STATIC_COVER' if cost==len(states) else 'NO_STATIC_COVER_DISCOVERY'
        hist[kind]+=1
        records.append(dict(case_id=case['case_id'],family_size=len(states),status=kind,
                            minimum_hamming_cost=cost,state_boundary_budget=len(states),matching=M,profiles=profiles))
    report=dict(status='COMPLETED_EXACT_MATCHING_SCREEN',sat_used=False,networkx_version=nx.__version__,
                classifications=dict(hist),records=records,seconds=round(time.monotonic()-start,4),
                cover_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                scope='All positive static covers directly replayed; negative optima require separate proof premises')
    (ROOT/'results/d17-feedback-round9-matching.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2))
    print('NO_STATIC',[r['case_id'] for r in records if r['status']!='STATIC_COVER'])


if __name__=='__main__':main()
