#!/usr/bin/env python3
"""Extract/check a finite rank-separation table; no SAT premises."""
import json
from itertools import combinations
from pathlib import Path
from d13_hand_matching import analyze


def apply(layers,x):
    for L in layers:
        for a,b in L:
            if x>>a&1 and not x>>b&1:x^=(1<<a)|(1<<b)
    return x


def table_candidates(n,layers,k,S):
    universe={('wire',c) for c in S}|{(a,b,d) for a,b in combinations(S,2) for d in (0,1)}
    rows=[]
    seen=set()
    for ones in combinations(range(n),n-1-k):
        x=sum(1<<c for c in ones)
        a=apply(layers,x)
        for p in range(n):
            if x>>p&1:continue
            b=apply(layers,x|(1<<p))
            c=(a^b).bit_length()-1
            assert a^b==1<<c
            if c not in S or (a,c) in seen:continue
            seen.add((a,c))
            cover={('wire',c)}
            for q in S:
                if q!=c:cover.add((min(c,q),max(c,q),a>>q&1))
            rows.append((cover,dict(input_zero=x,input_star=p,output_zero=a,output_star=c)))
    return universe,rows


def greedy_table(n,layers,k,S):
    universe,rows=table_candidates(n,layers,k,S)
    remaining=set(universe);chosen=[]
    while remaining:
        row=max(rows,key=lambda r:len(r[0]&remaining))
        assert row[0]&remaining
        chosen.append(row);remaining-=row[0]
    changed=True
    while changed:
        changed=False
        for i in range(len(chosen)-1,-1,-1):
            if set().union(*(r[0] for j,r in enumerate(chosen) if i!=j))==universe:
                chosen.pop(i);changed=True
    return [r[1] for r in chosen]


def probe_string(x,p,n):
    return ''.join('*' if c==p else str(x>>c&1) for c in range(n))


def check_table(n,layers,k,S,rows):
    covered=set()
    for row in rows:
        x,p=row['input_zero'],row['input_star']
        assert x.bit_count()==n-1-k and not x>>p&1
        a,b=apply(layers,x),apply(layers,x|(1<<p))
        c=(a^b).bit_length()-1
        assert a^b==1<<c and a&b==a
        assert row['output_zero']==a and row['output_star']==c
        assert c in S
        covered.add(('wire',c))
        for q in S:
            if q!=c:covered.add((min(c,q),max(c,q),a>>q&1))
    want={('wire',c) for c in S}|{(a,b,d) for a,b in combinations(S,2) for d in (0,1)}
    assert covered==want
    return len(want)


def main():
    root=Path(__file__).parent
    source=json.loads((root/'results/d13-hand-five-passes.json').read_text())
    n=13;k=8
    choices=[]
    for S in combinations([3,6,7,8,9,10],5):
        rows=greedy_table(n,source['layers'],k,S)
        choices.append((len(rows),S,rows))
    _,S,rows=min(choices)
    checks=check_table(n,source['layers'],k,S,rows)
    result=dict(status='VERIFIED',scope='A named five-layer prefix, not an entire two-layer cover case',n=n,rank=k,positions=S,layers=source['layers'],probe_rows=rows,covered_obligations=checks)
    (root/'results/d13-hand-rank-separation-certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print('S',S,'rows',len(rows),'obligations',checks)
    for row in rows:
        print(probe_string(row['input_zero'],row['input_star'],n),probe_string(row['output_zero'],row['output_star'],n))

if __name__=='__main__':main()
