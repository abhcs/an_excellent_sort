#!/usr/bin/env python3
"""Bare small merger feedback: matching and data constraints only."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'depth-hand-proofs/verify'))
from sentinel_cegar import Master, neg
from pysat.solvers import Solver
from netsat import apply_layers, sorted_mask


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--blocks',required=True)
    ap.add_argument('--depth',type=int,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    blocks=[int(x) for x in args.blocks.split(',')]
    n=sum(blocks);depth=args.depth;started=time.monotonic()
    starts=[sum(blocks[:i]) for i in range(len(blocks))]
    universe=sorted({sum(1<<v for size,start,z in zip(blocks,starts,zeros) for v in range(start+z,start+size))
                     for zeros in itertools.product(*(range(size+1) for size in blocks))})
    m=Master(n,depth+1,first=0,adjacent=False,no_repeat=False)
    for x in universe:
        if x==sorted_mask(n,x.bit_count()):continue
        cur=[bool(x>>c&1) for c in range(n)]
        for t in range(1,depth+1):
            nxt=[m.var() for _ in range(n)]
            for a,b in m.pairs:m.gate(cur[a],cur[b],nxt[a],nxt[b],m.g[t,a,b])
            for c in range(n):m.eq(cur[c],nxt[c],neg(m.used[t,c]))
            cur=nxt
        target=sorted_mask(n,x.bit_count())
        for c in range(n):m.add(cur[c] if target>>c&1 else neg(cur[c]))
    result=dict(status='BUILT',blocks=blocks,depth=depth,inputs=len(universe),variables=m.pool.top,
                clauses=len(m.clauses),normal_forms=False,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    with Solver(name='cadical195',bootstrap_with=m.clauses,with_proof=True) as solver:
        sat=solver.solve();result['status']='SAT' if sat else 'UNSAT_UNCHECKED'
        if sat:
            truth=set(solver.get_model())
            layers=[[(a,b) for a,b in m.pairs if m.g[t,a,b] in truth] for t in range(1,depth+1)]
            assert all(apply_layers(layers,x)==sorted_mask(n,x.bit_count()) for x in universe)
            result.update(merger=layers,directly_verified=True)
        else:
            directory=args.out.with_suffix('');directory.mkdir(parents=True,exist_ok=True)
            cnf=directory/'problem.cnf';proof=directory/'proof.drat'
            cnf.write_text(f'p cnf {m.pool.top} {len(m.clauses)}\n'+''.join(' '.join(map(str,c))+' 0\n' for c in m.clauses))
            proof.write_text('\n'.join(solver.get_proof())+'\n')
            result.update(certificate_directory=str(directory),cnf_sha256=hashlib.sha256(cnf.read_bytes()).hexdigest(),proof_sha256=hashlib.sha256(proof.read_bytes()).hexdigest())
    result['seconds']=time.monotonic()-started
    args.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)


if __name__=='__main__':main()
