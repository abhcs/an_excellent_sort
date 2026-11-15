#!/usr/bin/env python3
"""Replayable pure-peak witnesses: minimum-cut M, then a matching on failures."""
from collections import Counter
import json
from itertools import combinations
from pathlib import Path
import time
import networkx as nx
from two_layer_cover import half_blind_family,type_step

ROOT=Path(__file__).parent


def final_matching(states):
    if not states:return [],0
    sig=[sum(1<<i for i,s in enumerate(states) if s[v]==0) for v in range(17)]+[0]
    graph=nx.Graph();graph.add_nodes_from(range(18))
    graph.add_weighted_edges_from((a,b,(sig[a]^sig[b]).bit_count()) for a,b in combinations(range(18),2))
    matching=[tuple(sorted(e)) for e in nx.min_weight_matching(graph)]
    assert len(matching)==9
    cost=sum((sig[a]^sig[b]).bit_count() for a,b in matching)
    return sorted(e for e in matching if 17 not in e),cost


def main():
    start=time.monotonic();cover=[json.loads(s) for s in (ROOT/'prefixes/complete17.jsonl').read_text().splitlines()]
    first=json.loads((ROOT/'results/d17-feedback-round9-matching.json').read_text())['records']
    results=[];hist=Counter()
    for case,rec in zip(cover,first):
        assert case['case_id']==rec['case_id'];M=rec['matching']
        states=[type_step(s,case['layers'][1]) for s in half_blind_family(17,case['layers']).values()]
        after=[type_step(s,M) for s in states]
        failed=[i for i,p in enumerate(rec['profiles']) if p<4]
        N,cost=final_matching([after[i] for i in failed])
        profiles=[[sum(s[a]==s[b]==0 for a,b in M),sum(t[a]==t[b]==0 for a,b in N)]
                  for s,t in zip(states,after)]
        ok=all(max(p)==4 for p in profiles);assert ok==(cost==len(failed))
        status='PURE_PEAK_COVER' if ok else 'THIS_FIRST_MATCHING_FAILS'
        hist[status]+=1
        results.append(dict(case_id=case['case_id'],status=status,M=M,N=N,profiles=profiles,
                            first_failures=failed,second_hamming_cost=cost))
    report=dict(status='COMPLETED',sat_used=False,classifications=dict(hist),records=results,
                seconds=round(time.monotonic()-start,4),
                scope='Constructive pure two-layer peak covers only, not sorter completions or full H9 profiles')
    (ROOT/'results/d17-feedback-round9-two-stage.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2))
    print('UNRESOLVED',[r['case_id'] for r in results if r['status']!='PURE_PEAK_COVER'])


if __name__=='__main__':main()
