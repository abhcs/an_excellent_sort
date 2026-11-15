#!/usr/bin/env python3
"""Check small D17 weighted matching certificates without SAT."""
from collections import Counter
from functools import lru_cache
from itertools import combinations
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).parent


def step(state,M):
    state=list(state)
    for a,b in M:state[a],state[b]=min(state[a],state[b]),max(state[a],state[b])
    return state


def check_prices(sets,prices):
    # Prices are twice their mathematical values.
    n=len(prices)
    weights={(a,b):sum(a in S and b in S for S in sets) for a,b in combinations(range(n),2)}
    assert all(2*w<=prices[a]+prices[b] for (a,b),w in weights.items())
    tight={e for e,w in weights.items() if 2*w==sum(prices[c] for c in e)}
    return weights,tight


def maximum_matching(sets,n=17):
    active=sorted(set.union(*sets))
    weights={(a,b):sum(a in S and b in S for S in sets) for a,b in combinations(active,2)}
    @lru_cache(None)
    def rec(V):
        if not V:return 0,()
        a,*rest=V;best=rec(tuple(rest))
        for j,b in enumerate(rest):
            val,M=rec(tuple(rest[:j]+rest[j+1:]));val+=weights[a,b]
            if val>best[0]:best=val,((a,b),)+M
        return best
    return rec(tuple(active))


def main():
    initial=json.loads((ROOT/'results/d17-feedback-peaks/result.json').read_text())['states']
    allsets=[{c for c,v in enumerate(s) if v==0} for s in initial]
    A=[{4,7,8},{4,5,8},{4,5,6},{5,7,8}]
    B=[{10,12,15,16},{10,12,13,16},{10,12,13,14},{10,13,15,16},{9,13,15,16}]
    assert all(allsets[5*i+j]=={1,2}|A[i]|B[j] for i in range(4) for j in range(5))
    columns=[];rows=[]
    for j in range(5):
        C={1,2}|B[j];sets=[allsets[5*i+j] for i in range(4)]
        p=[4 if c in C else 2 if c in {4,5,7,8} else 0 for c in range(17)]
        _,tight=check_prices(sets,p)
        assert sum(p)==32
        assert {e for e in tight if 7 in e}=={(7,8)}
        core=C|{4,5}
        M=[(7,8)]+list(zip(sorted(core)[::2],sorted(core)[1::2]))
        assert all(sum(set(e)<=S for e in M)==4 for S in sets)
        columns.append(dict(column=j,common=sorted(C),double_prices=p,total_price=16,positive_matching=M))
    for i in range(4):
        C={1,2}|A[i];sets=allsets[5*i:5*i+5]
        p=[5 if c in C else 3 if c in {10,12,13,15,16} else 0 for c in range(17)]
        _,tight=check_prices(sets,p)
        assert sum(p)==40
        assert {e for e in tight if 12 in e}=={(10,12)}
        assert {e for e in tight if 15 in e}=={(15,16)}
        hub=min(C);rest=sorted(C-{hub})
        M=[(10,12),(15,16),(hub,13)]+list(zip(rest[::2],rest[1::2]))
        assert all(sum(set(e)<=S for e in M)==4 for S in sets)
        rows.append(dict(row=i,common=sorted(C),double_prices=p,total_price=20,positive_matching=M))
    prior=json.loads((ROOT/'results/d17-feedback-peaks/second-matching.json').read_text())
    M=prior['first_matching'];transported=[step(s,M) for s in initial]
    assert transported==prior['states']
    indices=[2,5,15,18]
    sets=[{c for c,v in enumerate(transported[i]) if v==0} for i in indices]
    C={1,2,4,7,10,13};a,b,c,x,y,z=8,12,15,14,16,5
    assert sets==[C|{a,b,x},C|{b,c,y},C|{a,b,c},C|{a,c,z}]
    counts=[sum(initial[i][a]==initial[i][b]==0 for a,b in M) for i in indices]
    assert counts==[3,3,3,3]
    p=[4 if v in C else 2 if v in {a,b,c} else 0 for v in range(17)]
    check_prices(sets,p);assert sum(p)==30
    positive=[]
    for omit in range(4):
        retained=[S for j,S in enumerate(sets) if j!=omit]
        val,N=maximum_matching(retained)
        ns=[sum(set(e)<=S for e in N) for S in retained]
        assert ns==[4,4,4]
        positive.append(dict(omitted_index=indices[omit],matching=N,retained_counts=ns))
    val,N=maximum_matching(sets)
    assert val==15
    certificate=dict(status='VERIFIED',scope='One fixed first matching in case608, not all first matchings',first_matching=M,indices=indices,first_retained_counts=counts,transported_sets=[sorted(S) for S in sets],common=sorted(C),symbols=dict(a=a,b=b,c=c,x=x,y=y,z=z),double_prices=p,total_price=15,required_total=16,deletion_controls=positive,maximum_total=val,maximum_matching=N)
    (ROOT/'results/d17-hand-defects-four-set.json').write_text(json.dumps(certificate,indent=2)+'\n')
    result=dict(status='VERIFIED',sat_used=False,columns=columns,rows=rows,four_set_certificate='d17-hand-defects-four-set.json',weighted_edge_inequalities_checked=(5+4+1)*136,scope='Hand classifications of static peak rows/columns and one conditional transported obstruction; no complete case closure',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (ROOT/'results/d17-hand-defects-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('columns','rows')},indent=2))
    print(json.dumps(certificate,indent=2))

if __name__=='__main__':main()
