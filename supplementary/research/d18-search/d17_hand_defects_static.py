#!/usr/bin/env python3
"""Small static subfamily classifications, with no SAT."""
import json
from pathlib import Path
from collections import Counter


def matchings(V):
    if not V:
        yield ()
        return
    a=V[0];rest=V[1:]
    for M in matchings(rest):yield M
    for i,b in enumerate(rest):
        for M in matchings(rest[:i]+rest[i+1:]):yield ((a,b),)+M


def classify(sets):
    V=sorted(set.union(*sets));count=0;types=Counter();examples={}
    for M in matchings(V):
        edges=[{e for e in M if set(e)<=S} for S in sets]
        if any(len(E)!=4 for E in edges):continue
        count+=1
        common=set.intersection(*edges);union=set.union(*edges)
        kind=('star' if len(common)>=3 else 'top' if len(union)<=5 else 'other')
        key=(kind,len(common),len(union),len(set(frozenset(x) for x in edges)))
        types[str(key)]+=1;examples.setdefault(str(key),M)
    return dict(count=count,types=dict(types),examples=examples)


def main():
    root=Path(__file__).parent
    states=json.loads((root/'results/d17-feedback-peaks/result.json').read_text())['states']
    sets=[{i for i,v in enumerate(s) if v==0} for s in states]
    result={}
    for j in range(5):
        result[f'column{j}']=classify([sets[5*i+j] for i in range(4)])
        print('column',j,result[f'column{j}'],flush=True)
    # Every row has union12; 140152 matchings each, still a small static check.
    for i in range(4):
        result[f'row{i}']=classify(sets[5*i:5*i+5])
        print('row',i,result[f'row{i}'],flush=True)
    (root/'results/d17-hand-defects-static.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
