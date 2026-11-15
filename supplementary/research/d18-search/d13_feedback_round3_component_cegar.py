#!/usr/bin/env python3
"""Common D13 L3,L4 satisfying old profiles and the nine-real component lemma.

Lazy cuts fix only L3, then require L4 to cross a forbidden track partition.
Use an external60-second worker cap. A survivor is not a sorting network.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import time

from mixed_profile_frontier import Master, add_state, blind_states, simulate
from d13_feedback_round3_components import placements, scan
from pysat.solvers import Solver

HERE=Path(__file__).resolve().parent


def partition_at_cut3(prefix2,third,fourth,initial):
    types=initial[:];labels=[v if x==0 else -1 for v,x in enumerate(types)]
    parent=list(range(13));sizes=[1]*13
    def find(v):
        while parent[v]!=v:
            parent[v]=parent[parent[v]];v=parent[v]
        return v
    def join(a,b):
        a,b=find(a),find(b)
        if a!=b:
            if sizes[a]<sizes[b]:a,b=b,a
            parent[b]=a;sizes[a]+=sizes[b]
        return sizes[a]<5
    for layer in prefix2+[third]:
        for a,b in layer:
            if types[a]==types[b]==0:
                if not join(labels[a],labels[b]):return None
            elif types[a]>types[b]:
                types[a],types[b]=types[b],types[a]
                labels[a],labels[b]=labels[b],labels[a]
    # L4 is a matching: all its RR decisions use this same cut3 state.
    for a,b in fourth:
        if types[a]==types[b]==0 and not join(labels[a],labels[b]):return None
    groups={}
    for v,label in enumerate(labels):
        if label>=0:groups.setdefault(find(label),[]).append(v)
    result=sorted(groups.values(),key=lambda g:(-len(g),g))
    assert sum(map(len,result))==9 and max(map(len,result))<=4
    return result


def guarded_cut(model,third,groups):
    selected=set(map(tuple,third));used={v for e in selected for v in e}
    idle=[v for v in range(13) if v not in used]
    guard=[-model.g[1,a,b] for a,b in sorted(selected)]
    guard += [model.g[1,a,b] for a,b in itertools.combinations(idle,2)]
    owner={v:i for i,group in enumerate(groups) for v in group}
    crosses=[model.g[2,a,b] for a,b in model.pairs if a in owner and b in owner and owner[a]!=owner[b]]
    return sorted(set(guard+crosses),key=lambda x:(abs(x),x))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--case',type=int,default=116)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--seconds',type=float,default=55)
    args=ap.parse_args();started=time.monotonic()
    cover=HERE/'prefixes/complete13.jsonl'
    case=[json.loads(line) for line in cover.read_text().splitlines()][args.case]
    families={r:blind_states(case,r) for r in (5,7)}
    all9=list(placements())
    model=Master(13,3,first=0,adjacent=False,no_repeat=True)
    for a,b in case['layers'][1]:model.add(-model.g[1,a,b])
    for state in families[7]:add_state(model,state)
    included5=set();cuts=set();cut_records=[];iterations=[]
    result=dict(status='RUNNING',case_id=case['case_id'],prefix=case['layers'],
                scope='All common L3,L4; seven-real profiles, five-real blind condition, nine-real component condition',
                cover_sha256=hashlib.sha256(cover.read_bytes()).hexdigest(),
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                family_sizes={r:len(f) for r,f in families.items()},nine_real_placements=len(all9),
                independently_proof_checked=False)
    def save():
        result.update(seconds=time.monotonic()-started,variables=model.pool.top,clauses=len(model.clauses),
                      iterations=iterations,component_cut_count=len(cuts),included_five_states=sorted(included5),
                      component_cuts=cut_records)
        args.out.write_text(json.dumps(result,indent=2)+'\n')
    with Solver(name='cadical195',bootstrap_with=model.clauses,with_proof=True) as solver:
        while True:
            save()
            if time.monotonic()-started>args.seconds:
                result['status']='TIME_LIMIT_BETWEEN_SOLVES';save();break
            solve_start=time.monotonic()
            if not solver.solve():
                result['status']='UNSAT_UNCHECKED'
                directory=args.out.with_suffix('');directory.mkdir(parents=True,exist_ok=True)
                (directory/'problem.cnf').write_text(f'p cnf {model.pool.top} {len(model.clauses)}\n'+''.join(' '.join(map(str,c))+' 0\n' for c in model.clauses))
                (directory/'proof.drat').write_text('\n'.join(solver.get_proof())+'\n')
                result['certificate_directory']=str(directory);save();break
            layers=model.network(solver.get_model())[1:]
            assert all(min(simulate(layers,s))>=2 and max(simulate(layers,s))==3 for s in families[7])
            bad5=[s for s in families[5] if not any(simulate(layers,s))]
            new_cuts=[];bad9=0
            for initial in all9:
                groups=partition_at_cut3(case['layers'],layers[0],layers[1],initial)
                if groups is None:continue
                bad9+=1;clause=guarded_cut(model,layers[0],groups);key=tuple(clause)
                assert key not in cuts, 'An existing cut must reject the current candidate'
                if key in {x[0] for x in new_cuts}:continue
                new_cuts.append((key,dict(initial=initial,third_layer=layers[0],cut3_track_groups=groups,clause=clause)))
            iterations.append(dict(iteration=len(iterations),solve_seconds=time.monotonic()-solve_start,
                                   five_violations=len(bad5),nine_violations=bad9,new_component_cuts=len(new_cuts)))
            if not bad5 and not bad9:
                independent=scan(case['case_id'],case['layers']+layers,all9)
                assert independent['obstructed_placements']==0
                result.update(status='SURVIVOR',next_layers=layers,independent_component_replay=independent)
                save();break
            begin=len(model.clauses)
            for state in bad5[:16]:
                assert state not in included5;included5.add(state);add_state(model,state)
            for key,record in new_cuts:
                model.add(*key);cuts.add(key);cut_records.append(record)
            solver.append_formula(model.clauses[begin:])
            if len(iterations)%10==0:print(json.dumps(iterations[-1]),flush=True)
    print(json.dumps({k:v for k,v in result.items() if k not in ('prefix','component_cuts','included_five_states','iterations','independent_component_replay')}),flush=True)


if __name__=='__main__':main()
