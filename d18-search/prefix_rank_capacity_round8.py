#!/usr/bin/env python3
"""Exact adjacent-ending rank reachability through local block capacities.

Optionally joins previously verified one-next-layer rescheduling/component
constraints. Run each worker under an external wall cap; SAT is only a
necessary-condition survivor. No data sorting is enforced after the cut.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import time

import netsat
from netsat import neg, prefix_images, verify_all
from endpoint_cegar import wire_endpoints, IntervalOracle
from interval_frontier import add_state_bounds
from probe_frontier import ProbeModel
from prefix_drat import RecordingSolver
from rank_block_capacity_cnf import add_block_capacity
from adjacent_rank_ending import ending

HERE=Path(__file__).resolve().parent


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--seed',type=Path,required=True)
    ap.add_argument('--depth',type=int,required=True)
    ap.add_argument('--cut',type=int,required=True)
    ap.add_argument('--combined',type=Path)
    ap.add_argument('--witness',type=Path)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();start=time.monotonic()
    seed=json.loads(args.seed.read_text());n=seed['n'];prefix=seed['prefix']
    free=args.cut-len(prefix);remaining=args.depth-args.cut;cap=2**remaining
    assert 0<free<args.depth-len(prefix) and remaining>=1
    universe=sorted(prefix_images(n,prefix))
    netsat.Solver=RecordingSolver
    model=ProbeModel(n,args.depth-len(prefix),universe,phi=False,nored0=False)
    lower,upper=wire_endpoints(model,list(range(n)),cap)
    assert cap==4
    capacity_stats=add_block_capacity(model,lower,upper)
    combined_count=0
    if args.combined:
        from d18_hand_next_reschedule import build, PAIRS
        data=json.loads(args.combined.read_text())
        assert n==18 and data['prefix']==prefix and args.depth==len(prefix)+5
        clauses,variables,_=build(data['rescheduling_items'],assumptions=False)
        mapping={i+1:model.g[0][e] for i,e in enumerate(PAIRS)}
        for v in range(154,variables+1):mapping[v]=model.new_var()
        clauses += [r['clause'] for r in data['component_cuts']]
        for clause in clauses:
            model.add([mapping[abs(v)] if v>0 else -mapping[abs(v)] for v in clause])
        combined_count=len(clauses)
    if args.witness:
        network=json.loads(args.witness.read_text())['layers']
        assert len(network)==args.depth and network[:len(prefix)]==prefix and verify_all(n,network)
        for t,layer in enumerate(network[len(prefix):]):
            chosen=set(map(tuple,layer));assert chosen<=set(model.g[t])
            for e,v in model.g[t].items():model.add([v if e in chosen else -v])
    for x in universe:add_state_bounds(model,x,model.simulate_to_cut(x,free),lower,upper)
    directory=args.out.with_suffix('');directory.mkdir(exist_ok=True,parents=True)
    cnf=directory/'problem.cnf';proof=directory/'proof.drat'
    cnf.write_text(f'p cnf {model.nv} {len(model.S.clauses)}\n'+''.join(' '.join(map(str,c))+' 0\n' for c in model.S.clauses))
    result=dict(status='BUILT',n=n,depth=args.depth,cut=args.cut,cap=cap,prefix=prefix,
        inputs=len(universe),variables=model.nv,clauses=model.ncl,block_capacity=capacity_stats,combined_clauses=combined_count,source_sha256=sha(Path(__file__)),seed_sha256=sha(args.seed),
        cnf_sha256=sha(cnf),certificate_directory=str(directory),
        scope='All continuations of the fixed prefix; exact rank-set reachability with adjacent final matching (necessary normal form for sorting)',
        dependencies_sha256={name:sha(HERE/name) for name in ('netsat.py','endpoint_cegar.py','interval_frontier.py','probe_frontier.py','prefix_drat.py','rank_block_capacity_cnf.py','adjacent_rank_ending.py')})
    if args.combined:
        result['combined_input_sha256']=sha(args.combined)
        result['combined_encoder_sha256']=sha(HERE/'d18_hand_next_reschedule.py')
    def save():
        result['seconds']=time.monotonic()-start;args.out.write_text(json.dumps(result,indent=2)+'\n')
    save();print(json.dumps({k:v for k,v in result.items() if k not in ('prefix','dependencies_sha256')}),flush=True)
    try:
        sat=model.S.solve()
        if sat:
            assignment=model.S.get_model()
            all_layers=model.network(assignment)
            layers=all_layers[:free]
            selected_last=all_layers[-1]
            intervals=IntervalOracle(n,universe).evaluate(layers)
            assert all(r['width']<=cap for r in intervals)
            full=[r for r in intervals if r['width']==cap]
            assert all(max(0,min(a['hi'],b['hi'])-max(a['lo'],b['lo'])+1)%2==0
                       for a,b in itertools.combinations(full,2))
            for row in intervals:
                inside=sum(row['lo']<=i<j<=row['hi'] for i,j in selected_last)
                assert row['width']-inside<=2
            route,route_stats=ending([(r['lo'],r['hi']) for r in intervals])
            assert route is not None
            result.update(status='SURVIVOR',free_layers=layers,intervals=intervals,last_pairing_projection=selected_last,independent_rank_routing=route,rank_dp_stats=route_stats)
        else:
            proof.write_text('\n'.join(model.S.get_proof())+'\n')
            result.update(status='UNSAT_UNCHECKED',proof_sha256=sha(proof))
        save();print(json.dumps(dict(status=result['status'],seconds=result['seconds'])),flush=True)
    finally:model.S.delete()


if __name__=='__main__':main()
