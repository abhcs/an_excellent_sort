#!/usr/bin/env python3
"""D13: first four retained layers need depth >=3 or >=5/7 gates on7/8reals."""
import argparse,json,sys,time,hashlib
from pathlib import Path
from itertools import product
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'depth-hand-proofs/verify'))
from sentinel_cegar import Master,neg
from pysat.solvers import Solver


def run(layers,state,depths=None):
    state=list(state);depths=list(depths or [0]*13);count=0
    for layer in layers:
        for a,b in layer:
            if state[a]==state[b]==0:
                count+=1;depths[a]=depths[b]=1+max(depths[a],depths[b])
            elif state[a]>state[b]:
                state[a],state[b]=state[b],state[a];depths[a],depths[b]=depths[b],depths[a]
    return state,depths,count


def collect(case):
    first=case['layers'][0];idle=next(v for v in range(13) if not any(v in e for e in first))
    opts=((-1,-1),(-1,0),(-1,1),(0,0),(0,1),(1,1));items={}
    for vals in product(opts,repeat=6):
        for z in (-1,0,1):
            r=sum(p.count(0) for p in vals)+(z==0)
            if r not in (7,8):continue
            p=[0]*13;p[idle]=z
            for (a,b),v in zip(first,vals):p[a],p[b]=v
            state,depths,q=run(case['layers'],p)
            if q>={7:5,8:7}[r]:continue
            key=(tuple(state),tuple(depths),q,r)
            items.setdefault(key,dict(initial=p,state=state,depths=depths,q=q,r=r))
    return list(items.values())


def valid(item,layers):
    state,depths,count=run(layers,item['state'],item['depths'])
    return max(depths)>=3 or item['q']+count>={7:5,8:7}[item['r']]


def add(cnf,item):
    state=item['state'];depths=item['depths'];threshold={7:5,8:7}[item['r']]
    rr3=[cnf.g[1,a,b] for a,b in cnf.pairs if state[a]==state[b]==0]
    long3=[cnf.g[1,a,b] for a,b in cnf.pairs if state[a]==state[b]==0 and max(depths[a],depths[b])>=2]
    cur=[(v>=0,v>=1) for v in state];nxt=[(cnf.var(),cnf.var()) for _ in range(13)]
    deep=[cnf.var() for _ in range(13)]
    for a,b in cnf.pairs:
        g=cnf.g[1,a,b]
        for bit in (0,1):cnf.gate(cur[a][bit],cur[b][bit],nxt[a][bit],nxt[b][bit],g)
        if state[a]==state[b]==0:
            da=db=max(depths[a],depths[b])>=1
        elif state[a]>state[b]:da,db=depths[b]>=2,depths[a]>=2
        else:da,db=depths[a]>=2,depths[b]>=2
        cnf.eq(deep[a],da,g);cnf.eq(deep[b],db,g)
    for a in range(13):
        for bit in (0,1):cnf.eq(cur[a][bit],nxt[a][bit],neg(cnf.used[1,a]))
        cnf.eq(deep[a],depths[a]>=2,neg(cnf.used[1,a]))
    real=[cnf.conj([lo,neg(hi)]) for lo,hi in nxt]
    rr4={(a,b):cnf.conj([cnf.g[2,a,b],real[a],real[b]]) for a,b in cnf.pairs}
    row4=[cnf.disj(rr4[a,b] for b in range(a+1,13)) for a in range(12)]
    long4=[cnf.conj([rr4[a,b],cnf.disj([deep[a],deep[b]])]) for a,b in cnf.pairs]
    cnf.add(*long3,*long4,cnf.ge(rr3+row4,threshold-item['q']))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--case',type=int,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    cover=ROOT/'d18-search/prefixes/complete13.jsonl';case=[json.loads(s) for s in cover.read_text().splitlines()][args.case]
    items=collect(case);cnf=Master(13,3,first=0,adjacent=False,no_repeat=True)
    for a,b in case['layers'][1]:cnf.add(-cnf.g[1,a,b])
    result=dict(case_id=case['case_id'],family_size=len(items),families_by_retained={r:sum(x['r']==r for x in items) for r in (7,8)},status='BUILT',scope=__doc__,prefix=case['layers'],source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    args.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
    included=[];records=[];started=time.monotonic()
    with Solver(name='cadical195',bootstrap_with=cnf.clauses) as solver:
        while True:
            if not solver.solve():result['status']='UNSAT';break
            layers=cnf.network(solver.get_model())[1:]
            bad=[i for i,item in enumerate(items) if not valid(item,layers)]
            records.append(dict(iteration=len(records),violations=len(bad)));print(json.dumps(records[-1]),flush=True)
            if not bad:result.update(status='SURVIVOR',next_layers=layers);break
            batch=bad if len(bad)<=16 else [bad[i*len(bad)//16] for i in range(16)]
            begin=len(cnf.clauses)
            for i in batch:
                assert i not in included
                included.append(i);add(cnf,items[i])
            solver.append_formula(cnf.clauses[begin:])
            result.update(iterations=records,included_indices=included,variables=cnf.pool.top,clauses=len(cnf.clauses),seconds=time.monotonic()-started)
            args.out.write_text(json.dumps(result,indent=2)+'\n')
    result.update(iterations=records,included_restrictions=[items[i] for i in included],variables=cnf.pool.top,clauses=len(cnf.clauses),seconds=time.monotonic()-started)
    args.out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],result['seconds'],flush=True)

if __name__=='__main__':main()
