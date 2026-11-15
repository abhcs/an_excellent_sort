#!/usr/bin/env python3
"""Tiny static-matching cores and independently checkable wire prices."""
from itertools import combinations
import json
from pathlib import Path
from pysat.card import CardEnc,EncType
from pysat.formula import IDPool
from pysat.solvers import Solver

ROOT=Path(__file__).parent
STATES=json.loads((ROOT/'results/d17-feedback-fourteen-hand606-states.json').read_text())['states']


def step(s,M):
    s=list(s)
    for a,b in M:s[a],s[b]=sorted((s[a],s[b]))
    return s


def requirements(M):
    groups={}
    for i,s in enumerate(STATES):
        if sum(s[a]==s[b]==0 for a,b in M)>=4:continue
        S=tuple(j for j,x in enumerate(step(s,M)) if x)
        groups.setdefault(S,[]).append(i)
    return [(S,indices) for S,indices in groups.items()]


def matching_core(rows):
    pool=IDPool();edge={p:pool.id(('e',p)) for p in combinations(range(14),2)}
    clauses=[]
    for v in range(14):
        clauses+=CardEnc.atmost([x for p,x in edge.items() if v in p],1,vpool=pool,encoding=EncType.pairwise).clauses
    selectors=[]
    for S,indices in rows:
        selector=pool.id();selectors.append(selector)
        for c in CardEnc.atleast([x for p,x in edge.items() if set(p)<=set(S)],2,vpool=pool,encoding=EncType.seqcounter).clauses:
            clauses.append([-selector]+c)
    with Solver(name='glucose3',bootstrap_with=clauses) as solver:
        if solver.solve(assumptions=selectors):
            model=set(solver.get_model())
            return dict(sat=True,N=[p for p,x in edge.items() if x in model])
        active=set(solver.get_core())
        for x in list(active):
            trial=active-{x}
            if not solver.solve(assumptions=sorted(trial)):
                active=trial
        core=[row for selector,row in zip(selectors,rows) if selector in active]
        return dict(sat=False,core=core)


def prices(rows,equality=False):
    t=len(rows);cap=2*t;pool=IDPool();q={(v,i):pool.id((v,i)) for v in range(14) for i in range(1,cap+1)}
    clauses=[]
    for v in range(14):
        clauses += [[-q[v,i],q[v,i-1]] for i in range(2,cap+1)]
    weights={e:sum(set(e)<=set(S) for S,unused in rows) for e in combinations(range(14),2)}
    for (a,b),w in weights.items():
        for i in range(2*w):clauses.append([q[a,i+1],q[b,2*w-i]])
    bound=4*t if equality else 4*t-1
    clauses+=CardEnc.atmost(list(q.values()),bound,vpool=pool,encoding=EncType.seqcounter).clauses
    with Solver(name='cadical195',bootstrap_with=clauses) as solver:
        if not solver.solve():return None
        model=set(solver.get_model());p=[sum(q[v,i] in model for i in range(1,cap+1)) for v in range(14)]
    assert all(2*w<=p[a]+p[b] for (a,b),w in weights.items())
    assert sum(p)<=bound
    return dict(twice_prices=p,total=sum(p),required=4*t,
                tight=[e for e,w in weights.items() if 2*w==p[e[0]]+p[e[1]]])


def main():
    M=((0,1),(2,3),(4,8),(5,6),(7,10),(9,11),(12,13))
    rows=requirements(M);result=matching_core(rows)
    assert not result['sat']
    result.update(M=M,required_sets=len(rows))
    result['strict_price']=prices(result['core'])
    if result['strict_price'] is None:result['equality_price']=prices(result['core'],True)
    out=ROOT/'results/d17-feedback-round3-probe.json'
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
