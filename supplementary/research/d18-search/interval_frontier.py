#!/usr/bin/env python3
"""Rank-interval endpoint encoding of the last-two-layer cone conditions.

For a standard comparator prefix each wire's attainable ranks form an
interval [lo,hi] containing its own index. L[c,k] says lo(c)>=k; U[c,k]
says hi(c)<=k. A cut-state zero of weight w forces lo<=n-w-1, and a one
forces hi>=n-w. The chosen intervals may overapproximate the true ones.
Any genuine completion is retained; a SAT result need not be a sorter.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

from pysat.card import CardEnc, EncType
from netsat import neg, prefix_images, apply_layers, verify_all
from probe_frontier import ProbeModel


def endpoints(model,cap):
    n=model.n
    lower=[[True]+[model.new_var() for _ in range(n-1)]+[False] for _ in range(n)]
    upper=[[False]+[model.new_var() for _ in range(n-1)]+[True] for _ in range(n)]
    support=[[model.new_var() for c in range(n)] for k in range(n)]
    for c in range(n):
        L,U=lower[c],upper[c]
        for k in range(n):
            model.add([neg(L[k+1]),L[k]])
            model.add([neg(U[k]),U[k+1]])
            model.add([neg(L[k]),neg(U[k])])  # lo>=k excludes hi<=k-1.
            s=support[k][c]
            model.add([-s,neg(L[k+1])])
            model.add([-s,neg(U[k])])
            model.add([s,L[k+1],U[k]])
        # Sorted inputs show lo<=c<=hi.
        model.add([neg(L[c+1])])
        model.add([neg(U[c])])
        # If lo<=k then hi<=k+cap-1.
        for k in range(n-cap):
            model.add([L[k+1],U[k+cap]])
    for row in support:
        enc=CardEnc.atmost(row,cap,top_id=model.nv,encoding=EncType.seqcounter)
        model.nv=max(model.nv,enc.nv)
        for clause in enc.clauses:
            model.add(clause)
    return lower,upper,support


def add_state_bounds(model,x,state,lower,upper):
    z=model.n-x.bit_count()
    for c in range(model.n):
        model.add([state[c],neg(lower[c][z])])
        model.add([neg(state[c]),neg(upper[c][z])])


def common_ending(model,support):
    pen,last=model.g[-2:]
    def gate(layer,a,b):
        return layer.get((min(a,b),max(a,b)),False) if a!=b else True
    for rank in range(model.n):
        for c in range(model.n):
            if rank==c:
                continue
            paths=[gate(pen,c,rank),gate(last,c,rank)]
            for middle in (rank-1,rank+1):
                if not 0<=middle<model.n or middle==c:
                    continue
                a,b=gate(pen,c,middle),gate(last,middle,rank)
                if a is False or b is False:
                    continue
                v=model.new_var()
                model.add([-v,a]); model.add([-v,b]); model.add([v,neg(a),neg(b)])
                paths.append(v)
            model.add([-support[rank][c],*paths])


def actual_intervals(n,prefix,free):
    lower=[n-1]*n
    upper=[0]*n
    low_witness=[None]*n
    high_witness=[None]*n
    for x in prefix_images(n,prefix):
        y=apply_layers(free,x)
        z=n-x.bit_count()
        for c in range(n):
            if (y>>c)&1:
                if z>=upper[c]:
                    upper[c]=z
                    high_witness[c]=x
            elif z-1<=lower[c]:
                lower[c]=z-1
                low_witness[c]=x
    assert all(0<=a<=c<=b<n for c,(a,b) in enumerate(zip(lower,upper)))
    return list(zip(lower,upper)),low_witness,high_witness


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--seed',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--depth',type=int)
    ap.add_argument('--route',action='store_true')
    ap.add_argument('--witness',type=Path)
    args=ap.parse_args()
    seed=json.loads(args.seed.read_text())
    n=len(seed['output_permutation'])
    depth=args.depth or seed['depth']
    prefix=seed['prefix']
    cut=depth-2
    free=cut-len(prefix)
    start=time.monotonic()
    universe=sorted(prefix_images(n,prefix))
    model=ProbeModel(n,depth-len(prefix),universe,phi=args.route)
    lower,upper,support=endpoints(model,4)
    if args.route:
        common_ending(model,support)
    if args.witness:
        net=json.loads(args.witness.read_text())['network']
        assert len(net)==depth and net[:len(prefix)]==prefix and verify_all(n,net)
        for t,layer in enumerate(net[len(prefix):]):
            chosen=set(map(tuple,layer))
            assert chosen<=set(model.g[t])
            for edge,v in model.g[t].items():
                model.add([v if edge in chosen else -v])
    for x in universe:
        state=model.simulate_to_cut(x,free)
        add_state_bounds(model,x,state,lower,upper)
    result=dict(case_id=seed['case_id'],n=n,depth=depth,cut=cut,
                scope='Rank-interval degree bounds and optional common ending routing',
                shared_ending_routing=args.route,inputs=len(universe),variables=model.nv,clauses=model.ncl,
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                status='BUILT',independently_proof_checked=False,
                build_seconds=round(time.monotonic()-start,3))
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)
    try:
        ok=model.S.solve()
        result['status']='SURVIVOR' if ok else 'UNSAT'
        if ok:
            layers=model.network(model.S.get_model())
            intervals,low,high=actual_intervals(n,prefix,layers[:free])
            assert max(b-a+1 for a,b in intervals)<=4
            assert max(sum(a<=k<=b for a,b in intervals) for k in range(n))<=4
            if args.route:
                for k in range(n):
                    positions={c for c,(a,b) in enumerate(intervals) if a<=k<=b}
                    cone={k}
                    for layer in reversed(layers[-2:]):
                        cone=cone|{v for a,b in layer if a in cone or b in cone for v in (a,b)}
                    assert positions<=cone
            result.update(free_layers=layers,intervals=intervals,low_witnesses=low,high_witnesses=high,
                          full_network_sorts=verify_all(n,prefix+layers))
        result['seconds']=round(time.monotonic()-start,3)
        args.out.write_text(json.dumps(result,indent=2)+'\n')
        print(result['status'],result['seconds'],flush=True)
    finally:
        model.S.delete()


if __name__=='__main__':
    main()
