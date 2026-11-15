#!/usr/bin/env python3
"""Fixed-prefix CEGAR with semantic cores of entire sentinel restrictions.

Only hand depth bounds through nine wires and the proved 5/7 early profiles
are used. A SURVIVOR passes all signed placements for the selected retained
sizes but need not sort. Each restriction has an activation variable, so an
UNSAT core names mathematical restrictions rather than anonymous clauses.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'depth-hand-proofs/verify'))
import sentinel_cegar as base
from two_layer_cover import half_blind_family
from pysat.solvers import Solver


def profile_condition(cnf,leaks,r,depth,strong=True,h9=False,sizes=False):
    assert not h9 and not sizes
    active=[cnf.disj(row) for row in leaks]
    conditions=[cnf.ge(active,depth[r])]
    if r in (5,7):
        d,minimum,peak={5:(5,1,2),7:(6,2,3)}[r]
        slack=cnf.ge(active,d+1)
        for t,row in enumerate(leaks):
            conditions.append(cnf.disj([slack,base.neg(active[t]),cnf.ge(active[:t],2),cnf.ge(row,minimum)]))
        conditions.append(cnf.disj([slack,*[cnf.conj([cnf.ge(row,peak),base.neg(cnf.ge(active[:t],2))])
                                             for t,row in enumerate(leaks)]]))
    return cnf.conj(conditions)


def passes(profile,r,depth,strong=True,h9=False,sizes=False):
    assert not h9 and not sizes
    p=[x for x in profile if x]
    if len(p)<depth[r]:
        return False
    if r==5 and len(p)==5 and max(p[:2])<2:
        return False
    if r==7 and len(p)==6 and (min(p[:2])<2 or max(p[:2])<3):
        return False
    return True


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cover',type=Path,required=True)
    ap.add_argument('--case',type=int,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    payload=args.cover.read_bytes()
    case=[json.loads(line) for line in payload.splitlines()][args.case]
    assert case['n']==13
    base.profile_condition=profile_condition
    base.passes=passes
    cnf=base.Master(13,8,first=0,adjacent=True,no_repeat=False)
    cnf.prefix=[tuple(e) for e in case['layers'][0]]
    second=set(map(tuple,case['layers'][1]))
    for a,b in cnf.pairs:
        cnf.add(cnf.g[1,a,b] if (a,b) in second else -cnf.g[1,a,b])
    for t in range(2,8):
        for a,b in cnf.pairs:
            cnf.add(-cnf.g[t-1,a,b],-cnf.g[t,a,b])
    restrictions=[]
    activations=[]
    started=time.monotonic()
    result=dict(case_id=case['case_id'],status='RUNNING',retained_sizes=[5,7,9],
                scope=__doc__,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                cover_sha256=hashlib.sha256(payload).hexdigest(),independently_proof_checked=False)
    def save():
        result.update(seconds=round(time.monotonic()-started,3),restrictions=restrictions,
                      variables=cnf.pool.top,clauses=len(cnf.clauses))
        args.out.write_text(json.dumps(result,indent=2)+'\n')
    with Solver(name='cadical195',bootstrap_with=cnf.clauses) as solver:
        def add(placement):
            assert placement not in restrictions
            start=len(cnf.clauses)
            selector=cnf.var()
            cnf.restriction(placement,base.HAND_DEPTH,True,False)
            # Gate/matching definitions precede every restriction. All fresh
            # auxiliary variables here belong to this restriction only.
            solver.append_formula([[-selector,*c] for c in cnf.clauses[start:]])
            activations.append(selector)
            restrictions.append(list(placement))
        for placement in half_blind_family(13,case['layers']).values():
            add(placement)
        while True:
            save()
            if not solver.solve(assumptions=activations):
                core=set(solver.get_core())
                result.update(status='UNSAT',core_indices=[i for i,s in enumerate(activations) if s in core])
                save()
                print('UNSAT',len(result['core_indices']),result['seconds'],flush=True)
                break
            net=cnf.network(solver.get_model())
            bad=[]
            for r in (5,7,9):
                placement=base.adversary(net,13,r,base.HAND_DEPTH,True,False,'cadical195')
                if placement is not None:
                    assert not passes(base.simulate(net,placement),r,base.HAND_DEPTH)
                    bad.append(placement)
            if not bad:
                result.update(status='SURVIVOR',network=net)
                save()
                print('SURVIVOR',len(restrictions),result['seconds'],flush=True)
                break
            for placement in bad:
                add(placement)
            print('restrictions',len(restrictions),'seconds',round(time.monotonic()-started,2),flush=True)


if __name__=='__main__':
    main()
