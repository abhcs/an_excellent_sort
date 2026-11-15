#!/usr/bin/env python3
"""One common next matching constrained by exact rank ranges and cone parity.

No future data comparisons are encoded. UNSAT excludes every next matching
for this fixed prefix; SAT is only a necessary-condition survivor. Run a
worker under an external wall limit. Matching variables include all pairs,
without adjacency or redundancy normal forms.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import time

from endpoint_cegar import IntervalOracle
from netsat import prefix_images
from pysat.solvers import Solver

HERE=Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(n,prefix,cap):
    universe=sorted(prefix_images(n,prefix))
    oracle=IntervalOracle(n,universe)
    initial=oracle.evaluate([])
    pairs=list(itertools.combinations(range(n),2))
    gates={e:i+1 for i,e in enumerate(pairs)}
    idles={c:len(pairs)+c+1 for c in range(n)}
    clauses=[]
    for c in range(n):
        incident=[gates[e] for e in pairs if c in e]
        clauses.extend([-a,-b] for a,b in itertools.combinations(incident,2))
        clauses.extend([-idles[c],-a] for a in incident)
        clauses.append([idles[c],*incident])
    actions=[]
    for c in range(n):
        actions.append(dict(variable=idles[c],edge=None,idle=c,intervals=[initial[c]]))
    for a,b in pairs:
        changed=oracle.evaluate([[(a,b)]])
        actions.append(dict(variable=gates[a,b],edge=[a,b],idle=None,intervals=[changed[a],changed[b]]))
    forbidden=[];full=[]
    for action in actions:
        if any(row['width']>cap for row in action['intervals']):
            clauses.append([-action['variable']]);forbidden.append(action['variable'])
        else:
            full.extend((action['variable'],r) for r in action['intervals'] if r['width']==cap)
    parity=set()
    for (a,x),(b,y) in itertools.combinations(full,2):
        overlap=max(0,min(x['hi'],y['hi'])-max(x['lo'],y['lo'])+1)
        if overlap%2:
            parity.add(tuple(sorted({-a,-b})))
    clauses.extend(map(list,sorted(parity)))
    return clauses,actions,dict(universe_size=len(universe),variables=len(pairs)+n,
        clauses=len(clauses),width_forbidden_actions=len(forbidden),parity_clauses=len(parity),
        initial_intervals=initial,cap=cap)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--seed',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--remaining',type=int,required=True,help='Layers remaining after the proposed next matching')
    parser.add_argument('--control-layer',action='store_true')
    args=parser.parse_args();assert args.remaining>=1;start=time.monotonic()
    data=json.loads(args.seed.read_text());n=data['n'];prefix=data['prefix'];cap=2**args.remaining
    clauses,actions,result=build(n,prefix,cap)
    if args.control_layer:
        chosen=set(map(tuple,data['control_layer']))
        clauses += [[a['variable'] if tuple(a['edge']) in chosen else -a['variable']]
                    for a in actions if a['edge'] is not None]
    result.update(status='BUILT',n=n,prefix=prefix,remaining_after_next=args.remaining,
        seed_sha256=digest(args.seed),source_sha256=digest(Path(__file__)),
        dependencies_sha256={name:digest(HERE/name) for name in ('endpoint_cegar.py','netsat.py')},
        actions=actions,scope='All next matching layers for a fixed prefix; rank bounds and saturated-cone parity only')
    def save():
        result['seconds']=time.monotonic()-start
        args.out.write_text(json.dumps(result,indent=2)+'\n')
    save()
    with Solver(name='cadical195',bootstrap_with=clauses,with_proof=True) as solver:
        sat=solver.solve()
        if sat:
            model=set(solver.get_model());layer=[a['edge'] for a in actions if a['edge'] and a['variable'] in model]
            oracle=IntervalOracle(n,sorted(prefix_images(n,prefix)))
            intervals=oracle.evaluate([layer])
            assert all(row['width']<=cap for row in intervals)
            full=[r for r in intervals if r['width']==cap]
            assert all(max(0,min(x['hi'],y['hi'])-max(x['lo'],y['lo'])+1)%2==0
                       for x,y in itertools.combinations(full,2))
            result.update(status='SURVIVOR',next_layer=layer,intervals=intervals)
        else:
            directory=args.out.with_suffix('');directory.mkdir(parents=True,exist_ok=True)
            cnf,proof=directory/'problem.cnf',directory/'proof.drat'
            cnf.write_text(f'p cnf {result["variables"]} {len(clauses)}\n'+''.join(' '.join(map(str,c))+' 0\n' for c in clauses))
            proof.write_text('\n'.join(solver.get_proof())+'\n')
            result.update(status='UNSAT_UNCHECKED',certificate_directory=str(directory),
                          cnf_sha256=digest(cnf),proof_sha256=digest(proof))
    save();print(json.dumps({k:v for k,v in result.items() if k not in ('prefix','actions','initial_intervals','intervals')}),flush=True)


if __name__=='__main__':main()
