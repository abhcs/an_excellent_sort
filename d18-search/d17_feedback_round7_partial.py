#!/usr/bin/env python3
"""Tiny matching-core feedback for forms with no fully required A row."""
from itertools import combinations
import json
from pathlib import Path
import time
from d17_feedback_round7_screen import ROOT,SOURCE,transport


def pairings(xs):
    if not xs:yield ();return
    a,*rest=xs
    for j,b in enumerate(rest):
        for tail in pairings(rest[:j]+rest[j+1:]):yield ((a,b),)+tail


def options(S,K):
    used={v for e in K for v in e};inside=sum(a in S and b in S for a,b in K)
    need=2-inside;free=sorted(S-used)
    if need<=0:return [()]
    if len(free)<2*need:return []
    return [P for chosen in combinations(free,2*need) for P in pairings(list(chosen))]


def solve(required,K=(),depth=0):
    # Monotone matching-core recursion; counts internal SS edges only.
    node={'nodes':1,'branch_nodes':0,'leaves':0,'max_depth':depth,'max_choice':0}
    while True:
        demands=[(len(o),i,o) for i,S in required.items() if (o:=options(S,K))!=[()]]
        if not demands:return K,node
        size,i,choices=min(demands,key=lambda x:x[:2])
        if size==0:node['leaves']+=1;return None,node
        if size==1:K=tuple(sorted(K+choices[0]));continue
        node['branch_nodes']+=1;node['max_choice']=max(node['max_choice'],size)
        for addition in choices:
            model,child=solve(required,tuple(sorted(K+addition)),depth+1)
            for key in ('nodes','branch_nodes','leaves'):node[key]+=child[key]
            for key in ('max_depth','max_choice'):node[key]=max(node[key],child[key])
            if model is not None:return model,node
        return None,node


def main():
    start=time.monotonic();base=[s[2:] for s in json.loads(SOURCE.read_text())['states']]
    reports=[];models=[];totals={};hist={}
    for d in (0,1):
        path=ROOT/f'results/d17-feedback-round7-screen-d{d}-survivors.jsonl'
        count=0
        for line in path.read_text().splitlines():
            record=json.loads(line);n=record['n'];M=record['M'];states=[s+[0]*(n-12) for s in base]
            required={i:transport(s,M) for i,s in enumerate(states)
                      if sum(s[a]==s[b]==0 for a,b in M)<n//2-3}
            model,stats=solve(required);count+=1
            for key in ('nodes','branch_nodes','leaves'):totals[key]=totals.get(key,0)+stats[key]
            for key in ('max_depth','max_choice'):totals[key]=max(totals.get(key,0),stats[key])
            hist[str((d,stats['max_depth'],model is not None))]=hist.get(str((d,stats['max_depth'],model is not None)),0)+1
            if model is not None:models.append(dict(deficit=d,**record,N=model))
        reports.append(dict(deficit=d,cases=count))
    report=dict(status='COMPLETED_FEEDBACK',sat_used=False,scope='Exploratory recursion; no independent certificate yet',
                batches=reports,stats=totals,histogram=hist,models=models,seconds=round(time.monotonic()-start,4))
    (ROOT/'results/d17-feedback-round7-partial.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
