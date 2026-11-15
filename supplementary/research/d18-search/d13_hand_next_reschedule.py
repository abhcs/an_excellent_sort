#!/usr/bin/env python3
"""D13 two-free-layer screen using hand-proved H7/H8 after commuting L1--L3."""
import argparse,json,sys,time,hashlib
from pathlib import Path
from itertools import product
from d13_hand_next_commute import prune
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'depth-hand-proofs/verify'))
from sentinel_cegar import Master,neg,simulate
from pysat.solvers import Solver


def collect(case):
    first=case['layers'][0]
    idle=next(v for v in range(13) if not any(v in e for e in first))
    opts=((-1,-1),(-1,0),(-1,1),(0,0),(0,1),(1,1))
    out={}
    for vals in product(opts,repeat=6):
        for z in (-1,0,1):
            r=sum(p.count(0) for p in vals)+(z==0)
            if r not in (7,8):continue
            p=[0]*13;p[idle]=z
            for (a,b),v in zip(first,vals):p[a],p[b]=v
            state,tracks,rr=prune(case['layers'],p)
            gates=rr[0]+rr[1];vs=[v for e in gates for v in e]
            if len(vs)!=len(set(vs)):continue
            used=sum(1<<c for c,t in enumerate(tracks) if t in vs)
            key=(tuple(state),used,len(gates),r)
            out.setdefault(key,dict(initial=p,state=state,used=used,q=len(gates),r=r,retained=rr))
    return list(out.values())


def valid(item,layers):
    state=item['state'];used=item['used'];q=item['q'];r=item['r']
    rr=[(a,b) for a,b in layers[0] if state[a]==state[b]==0]
    if any((used>>a&1) or(used>>b&1) for a,b in rr):return True
    p=simulate(layers,state);c=q+p[0];minimum,peak={7:(2,3),8:(3,4)}[r]
    return c>=minimum and p[1]>=minimum and max(c,p[1])>=peak


def add(cnf,item):
    state=item['state'];used=item['used'];q=item['q'];r=item['r']
    minimum,peak={7:(2,3),8:(3,4)}[r]
    row1=[cnf.g[1,a,b] for a,b in cnf.pairs if state[a]==state[b]==0]
    escape=[cnf.g[1,a,b] for a,b in cnf.pairs if state[a]==state[b]==0 and ((used>>a&1)or(used>>b&1))]
    cur=[(v>=0,v>=1) for v in state];nxt=[(cnf.var(),cnf.var()) for _ in range(13)]
    for a,b in cnf.pairs:
        for bit in (0,1):cnf.gate(cur[a][bit],cur[b][bit],nxt[a][bit],nxt[b][bit],cnf.g[1,a,b])
    for a in range(13):
        for bit in (0,1):cnf.eq(cur[a][bit],nxt[a][bit],neg(cnf.used[1,a]))
    real=[cnf.conj([lo,neg(hi)]) for lo,hi in nxt]
    row2=[cnf.disj(cnf.conj([cnf.g[2,a,b],real[a],real[b]]) for b in range(a+1,13)) for a in range(12)]
    cnf.add(*escape,cnf.ge(row1,minimum-q))
    cnf.add(*escape,cnf.ge(row2,minimum))
    cnf.add(*escape,cnf.ge(row1,peak-q),cnf.ge(row2,peak))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--case',type=int,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--collect-only',action='store_true');args=ap.parse_args()
    cover=ROOT/'d18-search/prefixes/complete13.jsonl';case=[json.loads(s) for s in cover.read_text().splitlines()][args.case]
    items=collect(case)
    result=dict(case_id=case['case_id'],family_size=len(items),families_by_retained={r:sum(x['r']==r for x in items) for r in (7,8)},status='BUILT',scope='Necessary H7/H8 profiles when the retained first three layers commute into one; only L3,L4 searched',prefix=case['layers'],source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    args.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
    if args.collect_only:return
    cnf=Master(13,3,first=0,adjacent=False,no_repeat=True)
    for a,b in case['layers'][1]:cnf.add(-cnf.g[1,a,b])
    included=[];records=[];started=time.monotonic()
    with Solver(name='cadical195',bootstrap_with=cnf.clauses) as solver:
        while True:
            if not solver.solve():result['status']='UNSAT';break
            layers=cnf.network(solver.get_model())[1:]
            bad=[i for i,item in enumerate(items) if not valid(item,layers)]
            records.append(dict(iteration=len(records),violations=len(bad)))
            print(json.dumps(records[-1]),flush=True)
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
