#!/usr/bin/env python3
"""All seven-real early profiles plus all five-real blind-four exclusions.

With four layers left in a hypothetical D(13)<=8 network, every seven-real
restriction has >=2 active layers so far. If it has exactly two, their sizes
are (2,3), (3,2), or (3,3). This includes restrictions that did NOT blind the
first two layers. The five-real condition is as in mixed_profile_frontier.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import time

from mixed_profile_frontier import Master, neg, simulate, type_step, Solver, blind_states


def seven_states(case):
    first,second=case['layers']
    idle=next(v for v in range(13) if all(v not in e for e in first))
    options=((-1,-1),(-1,0),(-1,1),(0,0),(0,1),(1,1))
    states={}
    for values in itertools.product(options,repeat=6):
        for z in (-1,0,1):
            if sum(p.count(0) for p in values)+(z==0)!=7:
                continue
            placement=[z]*13
            for (a,b),v in zip(first,values):
                placement[a],placement[b]=v
            early=(sum(a==b==0 for a,b in values),sum(placement[a]==placement[b]==0 for a,b in second))
            active=[x for x in early if x]
            if len(active)==2 and min(active)>=2 and max(active)==3:
                continue  # Already passes for every continuation.
            states[(tuple(type_step(placement,second)),early)]=placement
    return states


def valid(early,later):
    p=[x for x in early+tuple(later) if x]
    return len(p)>2 or len(p)==2 and min(p)>=2 and max(p)==3


def add_condition(cnf,state,early):
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
    if state.count(0)==5:
        cnf.add(cnf.disj(x for row in rows for x in row))
        return
    p=[x for x in early if x]
    if not p:
        for row in rows:
            cnf.add(cnf.ge(row,2))
        cnf.add(cnf.disj(cnf.ge(row,3) for row in rows))
    elif len(p)==1:
        alternatives=[cnf.conj(cnf.disj(row) for row in rows)]
        if p[0]>=2:
            target=2 if p[0]==3 else 3
            alternatives.extend(cnf.ge(row,target) for row in rows)
        cnf.add(cnf.disj(alternatives))
    elif min(p)<2 or max(p)<3:
        cnf.add(cnf.disj(x for row in rows for x in row))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cover',type=Path,required=True)
    ap.add_argument('--case',type=int,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    payload=args.cover.read_bytes()
    case=[json.loads(line) for line in payload.splitlines()][args.case]
    families={5:{(s,(0,0)):p for s,p in blind_states(case,5).items()},7:seven_states(case)}
    cnf=Master(13,3,first=0,adjacent=False,no_repeat=True)
    for a,b in case['layers'][1]:
        cnf.add(-cnf.g[1,a,b])
    included=[]
    for state,early in families[7]:
        if early==(0,0):
            add_condition(cnf,state,early)
            included.append((state,early))
    started=time.monotonic()
    records=[]
    result=dict(case_id=case['case_id'],cover_sha256=hashlib.sha256(payload).hexdigest(),
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                family_sizes={r:len(f) for r,f in families.items()},status='RUNNING',
                scope=__doc__,independently_proof_checked=False)
    def save():
        result.update(seconds=round(time.monotonic()-started,3),iterations=records,
                      included_states=included,variables=cnf.pool.top,clauses=len(cnf.clauses))
        args.out.write_text(json.dumps(result,indent=2)+'\n')
    with Solver(name='cadical195',bootstrap_with=cnf.clauses) as solver:
        while True:
            save()
            if not solver.solve():
                result['status']='UNSAT'
                save()
                print('UNSAT',result['seconds'],flush=True)
                break
            layers=cnf.network(solver.get_model())[1:]
            bad=[]
            for r,family in families.items():
                for state,early in family:
                    later=simulate(layers,state)
                    if not (any(later) if r==5 else valid(early,later)):
                        bad.append((state,early))
            records.append(dict(iteration=len(records),violations=len(bad)))
            print(json.dumps(records[-1]),flush=True)
            if not bad:
                result.update(status='SURVIVOR',next_layers=layers)
                save()
                break
            begin=len(cnf.clauses)
            # Spread additions across the sorted family instead of adding many
            # near-identical failures from a single sentinel configuration.
            batch=bad if len(bad)<=24 else [bad[i*len(bad)//24] for i in range(24)]
            for state,early in batch:
                assert (state,early) not in included
                add_condition(cnf,state,early)
                included.append((state,early))
            solver.append_formula(cnf.clauses[begin:])


if __name__=='__main__':
    main()
