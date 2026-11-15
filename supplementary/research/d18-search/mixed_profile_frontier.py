#!/usr/bin/env python3
"""Joint five- and seven-real restrictions on layers 3 and 4 for D(13).

Every seven-real restriction blind in layers 1 and 2 needs first-two counts
(2,3), (3,2), or (3,3). Every five-real restriction blind in those layers
must be nonempty in layer 3 or 4, since D(5)>=5. CEGAR ranges over ALL
normalized placements blind in the first two layers, not sampled placements.
SAT remains only a relaxation witness. UNSAT excludes a whole prefix case.
"""
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'depth-hand-proofs/verify'))
from sentinel_cegar import Master, neg, simulate
from two_layer_cover import type_step
from pysat.solvers import Solver


def blind_states(case,r):
    n=case['n']
    first,second=case['layers']
    idle=[v for v in range(n) if all(v not in e for e in first)]
    assert len(idle)==1
    # Sorting types inside L1 changes no later state. RR is forbidden by
    # the blind-L1 premise; the other five normalized pair types are exhaustive.
    options=((-1,-1),(-1,0),(-1,1),(0,1),(1,1))
    states={}
    for values in itertools.product(options,repeat=len(first)):
        for z in (-1,0,1):
            if sum(p.count(0) for p in values)+(z==0)!=r:
                continue
            placement=[z]*n
            for (a,b),v in zip(first,values):
                placement[a],placement[b]=v
            if any(placement[a]==placement[b]==0 for a,b in second):
                continue
            state=tuple(type_step(placement,second))
            states[state]=placement
    return states


def add_state(cnf,state):
    r=state.count(0)
    assert r in (5,7)
    cur=[(v>=0,v>=1) for v in state]
    rows=[]
    for t in (1,2):
        real=[cnf.conj([lo,neg(hi)]) for lo,hi in cur]
        row=[cnf.disj(cnf.conj([cnf.g[t,a,b],real[a],real[b]])
                       for b in range(a+1,cnf.n)) for a in range(cnf.n-1)]
        rows.append(row)
        if t==1:
            nxt=[(cnf.var(),cnf.var()) for _ in range(cnf.n)]
            for a,b in cnf.pairs:
                for q in (0,1):
                    cnf.gate(cur[a][q],cur[b][q],nxt[a][q],nxt[b][q],cnf.g[t,a,b])
            for a in range(cnf.n):
                for q in (0,1):
                    cnf.eq(cur[a][q],nxt[a][q],neg(cnf.used[t,a]))
            cur=nxt
    if r==5:
        cnf.add(cnf.disj(x for row in rows for x in row))
    else:
        for row in rows:
            cnf.add(cnf.ge(row,2))
        cnf.add(cnf.disj(cnf.ge(row,3) for row in rows))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cover',type=Path,required=True)
    ap.add_argument('--case',type=int,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--solver',default='cadical195')
    args=ap.parse_args()
    payload=args.cover.read_bytes()
    case=[json.loads(line) for line in payload.splitlines()][args.case]
    assert case['n']==13
    families={r:blind_states(case,r) for r in (5,7)}
    cnf=Master(13,3,first=0,adjacent=False,no_repeat=True)
    for a,b in case['layers'][1]:
        cnf.add(-cnf.g[1,a,b])
    included=[]
    for state in families[7]:
        add_state(cnf,state)
        included.append(state)
    started=time.monotonic()
    records=[]
    result=dict(case_id=case['case_id'],cover_sha256=hashlib.sha256(payload).hexdigest(),
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                family_sizes={r:len(f) for r,f in families.items()},status='RUNNING',
                scope='All five- and seven-real blind-two restrictions on L3,L4',
                independently_proof_checked=False)
    def save():
        result.update(seconds=round(time.monotonic()-started,3),iterations=records,
                      included_states=[list(s) for s in included],variables=cnf.pool.top,clauses=len(cnf.clauses))
        args.out.write_text(json.dumps(result,indent=2)+'\n')
    with Solver(name=args.solver,bootstrap_with=cnf.clauses) as solver:
        while True:
            save()
            if not solver.solve():
                result['status']='UNSAT'
                save()
                print('UNSAT',result['seconds'],flush=True)
                break
            layers=cnf.network(solver.get_model())[1:]
            assert all(min(p)>=2 and max(p)==3 for p in (simulate(layers,s) for s in families[7]))
            bad=[s for s in families[5] if not any(simulate(layers,s))]
            records.append(dict(iteration=len(records),violations=len(bad)))
            print(json.dumps(records[-1]),flush=True)
            if not bad:
                result.update(status='SURVIVOR',next_layers=layers,
                              profile_histogram={r:dict(Counter(str(simulate(layers,s)) for s in family))
                                                 for r,family in families.items()})
                save()
                break
            begin=len(cnf.clauses)
            for state in bad[:16]:
                assert state not in included
                add_state(cnf,state)
                included.append(state)
            solver.append_formula(cnf.clauses[begin:])


if __name__=='__main__':
    main()
