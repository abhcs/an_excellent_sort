#!/usr/bin/env python3
"""Cheap repair of all606 pure models to nonempty/nonrepeat profiles."""
from collections import Counter
import gzip
from itertools import combinations
import json
from pathlib import Path
import time
import networkx as nx
from d17_feedback_round9_check import states_of,apply,legal

ROOT=Path(__file__).parent


def repair(states,M,second):
    # Repeated prefix gates are idempotent and retain zero gates here.
    M=[tuple(e) for e in M if tuple(e) not in set(map(tuple,second))]
    after=[apply(s,M) for s in states]
    counts=[sum(s[a]==s[b]==0 for a,b in M) for s in states]
    if min(counts)==0:return None
    bad=[i for i,c in enumerate(counts) if c<4]
    sig=[sum(1<<i for i,s in enumerate(after) if s[v]==0) for v in range(17)]+[0]
    mask=sum(1<<i for i in bad);big=9*len(states)+1
    graph=nx.Graph();graph.add_nodes_from(range(18))
    for a,b in combinations(range(18),2):
        if (a,b) in M:continue
        diff=sig[a]^sig[b]
        graph.add_edge(a,b,weight=big*(diff&mask).bit_count()+diff.bit_count())
    allpairs=nx.min_weight_matching(graph);assert len(allpairs)==9
    N=sorted(tuple(sorted(e)) for e in allpairs if 17 not in e)
    profiles=[[a,sum(s[u]==s[v]==0 for u,v in N)] for a,s in zip(counts,after)]
    if all(min(p)>=1 and max(p)==4 for p in profiles):return M,N,profiles
    return None


def main():
    start=time.monotonic();cover=[json.loads(s) for s in (ROOT/'prefixes/complete17.jsonl').read_text().splitlines()]
    old=json.loads(gzip.decompress((ROOT/'results/d17-feedback-round9-all606-covers.json.gz').read_bytes()))['cases']
    models=[];fail=[];methods=Counter()
    for i,record in enumerate(old):
        states=states_of(cover[i]);result=repair(states,record['M'],cover[i]['layers'][1]);method='matching_repair'
        if result is None and i in (587,600,604,605):
            source=json.loads((ROOT/f'results/d17-feedback-round9-case{i}/result.json').read_text())
            M,N=source['next_layers'];profiles=[[sum(s[a]==s[b]==0 for a,b in M),
                                               sum(apply(s,M)[a]==apply(s,M)[b]==0 for a,b in N)] for s in states]
            result=M,N,profiles;method='existing_SAT_control'
        if result is None:fail.append(i);continue
        M,N,profiles=result
        assert legal(M) and legal(N) and not(set(map(tuple,M))&set(map(tuple,N)))
        assert not(set(map(tuple,M))&set(map(tuple,cover[i]['layers'][1])))
        assert all(min(p)>=1 and max(p)==4 for p in profiles)
        models.append(dict(case=i,M=M,N=N,profiles=profiles,method=method));methods[method]+=1
    report=dict(status='COMPLETED',sat_used_in_this_run=False,cases_repaired=len(models),unrepaired=fail,
                methods=dict(methods),records=models,seconds=round(time.monotonic()-start,4),
                scope='Existing nonempty, noL2/L3repeat, noL3/L4repeat, and onepeak4 conditions; not sorting images')
    (ROOT/'results/d17-feedback-round10-repair.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2))


if __name__=='__main__':main()
