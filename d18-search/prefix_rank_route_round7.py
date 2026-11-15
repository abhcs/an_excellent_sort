#!/usr/bin/env python3
"""Common two-layer reachability for exact rank intervals of a fixed prefix.

Default: both ending matchings have arbitrary spans. --normal uses the
existing last-two-layer nonredundancy normal form. This extends the earlier
interval_frontier routing experiment to round-six prefixes and DRAT records.
No data sorting constraints are imposed in the ending. Use an external cap.
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

HERE=Path(__file__).resolve().parent


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def add_common_ending(model, lower, upper, normal):
    """Every interval rank must have a path through the same two matchings."""
    n = model.n
    pen, last = model.g[-2], dict(model.g[-1])
    if not normal:
        # Model always has adjacent-only last-layer variables, even phi=False.
        # Extend them to ALL pairs; reimpose matching across the full edge set.
        for edge in itertools.combinations(range(n), 2):
            if edge not in last:
                last[edge] = model.new_var()
        for c in range(n):
            incident = [v for edge, v in last.items() if c in edge]
            for a, b in itertools.combinations(incident, 2):
                model.add([-a, -b])
    start = model.ncl
    def gate(layer, a, b):
        return layer.get((min(a,b), max(a,b)), False)
    for c in range(n):
        for rank in range(n):
            if c == rank:
                continue
            paths = [gate(pen,c,rank), gate(last,c,rank)]
            for middle in range(n):
                if middle in (c,rank):
                    continue
                a,b = gate(pen,c,middle),gate(last,middle,rank)
                if a is False or b is False:
                    continue
                v=model.new_var()
                model.add([-v,a]);model.add([-v,b])
                model.add([v,neg(a),neg(b)])
                paths.append(v)
            # L[k+1] or U[k] says rank k is outside the chosen interval.
            model.add([lower[c][rank+1],upper[c][rank],*paths])
    return last, model.ncl-start


def verify_routing(intervals, pen, last):
    for row in intervals:
        cone={row['wire']}
        for layer in (pen,last):
            cone |= {v for a,b in layer if a in cone or b in cone for v in (a,b)}
        assert set(range(row['lo'],row['hi']+1)) <= cone, (row,pen,last)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--seed',type=Path,required=True)
    ap.add_argument('--depth',type=int,required=True)
    ap.add_argument('--cut',type=int,required=True)
    ap.add_argument('--normal',action='store_true')
    ap.add_argument('--combined',type=Path)
    ap.add_argument('--witness',type=Path)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();start=time.monotonic()
    seed=json.loads(args.seed.read_text());n=seed['n'];prefix=seed['prefix']
    free=args.cut-len(prefix);remaining=args.depth-args.cut;cap=2**remaining
    assert 0<free<args.depth-len(prefix) and remaining==2
    universe=sorted(prefix_images(n,prefix))
    netsat.Solver=RecordingSolver
    model=ProbeModel(n,args.depth-len(prefix),universe,phi=args.normal,nored0=False)
    lower,upper=wire_endpoints(model,list(range(n)),cap)
    parity=0
    if cap<=n:
        for c,d in itertools.combinations(range(n),2):
            for a in range(max(0,c-cap+1),min(c,n-cap)+1):
                for b in range(max(0,d-cap+1),min(d,n-cap)+1):
                    if abs(a-b)<cap and abs(a-b)%2:
                        model.add([lower[c][a+1],upper[c][a+cap-1],lower[d][b+1],upper[d][b+cap-1]])
                        parity+=1
    last, route_count=add_common_ending(model,lower,upper,args.normal)
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
            chosen=set(map(tuple,layer))
            gates=last if t==model.r-1 else model.g[t]
            assert chosen<=set(gates)
            for e,v in gates.items():model.add([v if e in chosen else -v])
    for x in universe:add_state_bounds(model,x,model.simulate_to_cut(x,free),lower,upper)
    directory=args.out.with_suffix('');directory.mkdir(exist_ok=True,parents=True)
    cnf=directory/'problem.cnf';proof=directory/'proof.drat'
    cnf.write_text(f'p cnf {model.nv} {len(model.S.clauses)}\n'+''.join(' '.join(map(str,c))+' 0\n' for c in model.S.clauses))
    result=dict(status='BUILT',n=n,depth=args.depth,cut=args.cut,cap=cap,prefix=prefix,
        inputs=len(universe),variables=model.nv,clauses=model.ncl,parity_clauses=parity,
        combined_clauses=combined_count,route_clauses=route_count,
        ending_normal_form=args.normal,source_sha256=sha(Path(__file__)),seed_sha256=sha(args.seed),
        cnf_sha256=sha(cnf),certificate_directory=str(directory),
        scope='All continuations of the fixed prefix; cut intervals route through common two-layer ending',
        dependencies_sha256={name:sha(HERE/name) for name in ('netsat.py','endpoint_cegar.py','interval_frontier.py','probe_frontier.py','prefix_drat.py')})
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
            pos=set(v for v in assignment if v>0)
            ending=[all_layers[-2],sorted(e for e,v in last.items() if v in pos)]
            intervals=IntervalOracle(n,universe).evaluate(layers)
            assert all(r['width']<=cap for r in intervals)
            full=[r for r in intervals if r['width']==cap]
            assert all(max(0,min(a['hi'],b['hi'])-max(a['lo'],b['lo'])+1)%2==0
                       for a,b in itertools.combinations(full,2))
            verify_routing(intervals,*ending)
            result.update(status='SURVIVOR',free_layers=layers,intervals=intervals,ending_matchings=ending)
        else:
            proof.write_text('\n'.join(model.S.get_proof())+'\n')
            result.update(status='UNSAT_UNCHECKED',proof_sha256=sha(proof))
        save();print(json.dumps(dict(status=result['status'],seconds=result['seconds'])),flush=True)
    finally:model.S.delete()


if __name__=='__main__':main()
