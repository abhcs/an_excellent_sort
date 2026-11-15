#!/usr/bin/env python3
"""Falsify proposed all-placement size/depth budget lemmas with bounded search.

Success here is a NONSORTING comparator network passing the selected necessary
conditions for EVERY signed placement, not a solution to D(18). Failure to find
one is inconclusive. The exact adversary is the previously validated encoder.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'depth-hand-proofs/verify'))
from sentinel_cegar import (CNF, KNOWN_DEPTH, KNOWN_SIZE, adversary, fixed_step,
                            neg, simulate)
from pysat.solvers import Solver
from two_layer_cover import half_blind_family
from netsat import apply_layers, is_sorted, prefix_images, verify_all


def size_adversary(net,r,minimize=False):
    c=CNF()
    xs=[(c.var(),c.var()) for _ in range(18)]
    for lo,hi in xs:c.add(-hi,lo)
    real=[c.conj([lo,-hi]) for lo,hi in xs]
    c.add(c.ge(real,r));c.add(neg(c.ge(real,r+1)))
    for a,b in net[0]:
        for q in (0,1):c.add(-xs[a][q],xs[b][q])
    cur=xs;leaks=[]
    for layer in net:
        cur,row=fixed_step(c,cur,layer);leaks.extend(row)
    c.add(neg(c.ge(leaks,KNOWN_SIZE[r])))
    best=None
    with Solver(name='cadical195',bootstrap_with=c.clauses) as s:
        sent=len(c.clauses)
        while s.solve():
            model=set(s.get_model())
            best=[int(lo in model)+int(hi in model)-1 for lo,hi in xs]
            count=sum(simulate(net,best))
            assert best.count(0)==r and count<KNOWN_SIZE[r]
            if not minimize:return best
            c.add(neg(c.ge(leaks,count)))
            s.append_formula(c.clauses[sent:]);sent=len(c.clauses)
    return best


def matrix(net):
    rows=[]
    for layer in net:
        row=[-1]*18
        for a,b in layer:row[a]=b;row[b]=a
        rows.append(row)
    return rows


def irredundant_profile(net, placement):
    """Remove real-real comparators that never swap on any retained binary input.

    A truth-table bit represents one assignment to the independent real inputs.
    Fixed infinities are represented by their threshold bits and tracked
    separately by type. Threshold commutation makes the redundancy check valid
    for arbitrary real values, not merely the binary sample.
    """
    r=placement.count(0)
    full=(1<<(1<<r))-1
    state=list(placement);values=[];j=0
    for value in state:
        if value:
            values.append(0 if value<0 else full)
        else:
            half=1<<j
            values.append((((1<<half)-1)<<half)*(full//((1<<(2*half))-1)))
            j+=1
    raw=[];retained=[];removed=[]
    for t,layer in enumerate(net):
        before=after=0
        for a,b in layer:
            if state[a]==state[b]==0:
                before+=1
                if values[a]&~values[b]:after+=1
                else:removed.append(dict(layer=t+1,comparator=[a,b]))
            values[a],values[b]=values[a]&values[b],values[a]|values[b]
            state[a],state[b]=min(state[a],state[b]),max(state[a],state[b])
        raw.append(before);retained.append(after)
    return dict(r=r,binary_assignments=1<<r,raw_profile=raw,irredundant_profile=retained,
                never_swapping_comparators=removed)


def exhaustive_audit(net, retained, size_only, work, limit=64):
    source=work/'audit-input.txt'
    source.write_text(f'18 {len(net)}\n'+'\n'.join(' '.join(map(str,row)) for row in matrix(net))+'\n')
    completed=subprocess.run([str(HERE/'restriction_budget_audit'),str(source),
                              str(sum(1<<r for r in retained)),str(int(size_only)),str(limit)],
                             capture_output=True,text=True,check=True,timeout=15)
    result=json.loads(completed.stdout)
    polynomial=[1]
    for _ in range(9):
        nxt=[0]*(len(polynomial)+2)
        for i,value in enumerate(polynomial):
            for j,multiplicity in enumerate((3,2,1)):nxt[i+j]+=value*multiplicity
        polynomial=nxt
    for row in result['results']:
        assert row['placements']==polynomial[row['r']]
        assert sum(simulate(net,row['minimum_witness']))==row['minimum_comparators']
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--seconds',type=float,default=45)
    ap.add_argument('--retained',default='9')
    ap.add_argument('--size-only',action='store_true')
    ap.add_argument('--minimize',action='store_true',help='return a minimum-budget violating placement')
    ap.add_argument('--exhaustive',action='store_true',help='use direct complete enumeration instead of a SAT adversary')
    ap.add_argument('--resume',type=Path)
    ap.add_argument('--worker',action='store_true',help=argparse.SUPPRESS)
    args=ap.parse_args()
    if not args.worker:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        command=[sys.executable,str(Path(__file__).resolve()),*sys.argv[1:],'--worker']
        try:subprocess.run(command,timeout=args.seconds+5,check=True)
        except subprocess.TimeoutExpired:
            record=json.loads(args.out.read_text()) if args.out.exists() else {}
            record.update(status='TIME_LIMIT',note='Hard parent limit; a partial ledger proves no universal claim')
            args.out.write_text(json.dumps(record,indent=2)+'\n')
            print('TIME_LIMIT (hard parent limit)',flush=True)
        return
    started=time.monotonic();rng=random.Random(20261115)
    retained=[int(r) for r in args.retained.split(',')]
    original=[[tuple(edge) for edge in layer] for layer in
              json.loads((HERE/'results/e18_4_d11.json').read_text())['layers']]
    assert verify_all(18,original)
    net=original[:4]+original[5:]
    samples=[]
    if args.resume:
        old=json.loads(args.resume.read_text())
        net=[[tuple(edge) for edge in layer] for layer in old['network']]
        samples=old['samples']
    seen={tuple(s) for s in samples}
    def add(state):
        if tuple(state) not in seen:samples.append(list(state));seen.add(tuple(state))
    if 9 in retained:
        for state in half_blind_family(18,net[:2]).values():add(state)
    # A few diverse initial placements; later placements come from exact search.
    for r in retained:
        for _ in range(8):
            positions=rng.sample(range(18),18-r);state=[0]*18
            for i in positions:state[i]=rng.choice([-1,1])
            add(state)
    work=args.out.with_suffix('');work.mkdir(parents=True,exist_ok=True)
    record=dict(status='INCOMPLETE',n=18,depth=10,retained=retained,
                size_only=args.size_only,minimize=args.minimize,exhaustive=args.exhaustive,
                network=net,samples=samples,rounds=[],
                scope='Counterexample search for restriction-budget lemmas; not a sorting-network solver',
                encoder_sha256=hashlib.sha256((HERE.parent/'depth-hand-proofs/verify/sentinel_cegar.py').read_bytes()).hexdigest())
    def save():
        record.update(network=net,samples=samples,seconds=round(time.monotonic()-started,3))
        args.out.write_text(json.dumps(record,indent=2)+'\n')
    save()
    iteration=0
    while time.monotonic()-started<args.seconds:
        iteration+=1
        inp=work/'input.txt';out=work/'output.txt'
        rows=matrix(net)
        inp.write_text('\n'.join(' '.join(map(str,row)) for row in rows)+'\n'+str(len(samples))+'\n'+
                       '\n'.join(str(s.count(0))+' '+' '.join(map(str,s)) for s in samples)+'\n')
        run=subprocess.run([str(HERE/'restriction_budget_search'),str(inp),str(out),'0.4',str(1000+iteration),
                            str(int(args.size_only))],capture_output=True,text=True,timeout=3,check=True)
        stats=json.loads(run.stdout)
        rows=[list(map(int,line.split())) for line in out.read_text().splitlines()]
        assert len(rows)==10 and all(len(row)==18 for row in rows)
        net=[[(a,b) for a,b in enumerate(row) if b>a] for row in rows]
        assert net[:2]==original[:2] and net[-1]==original[-1]
        entry=dict(iteration=iteration,samples=len(samples),**stats)
        record['rounds'].append(entry)
        if stats['energy']==0:
            bad=[];checked=[]
            if args.exhaustive:
                audit=exhaustive_audit(net,retained,args.size_only,work)
                for row in audit['results']:
                    checked.append(dict(**row,result='ALL_PLACEMENTS_PASS' if not row['violations'] else 'COUNTEREXAMPLE'))
                bad=audit['sampled_bad_placements']
                assert bool(bad)==any(row['violations'] for row in audit['results'])
                for placement in bad:
                    assert tuple(placement) not in seen
                    add(placement)
            else:
                for r in retained:
                    placement=(size_adversary(net,r,args.minimize) if args.size_only else
                               adversary(net,18,r,KNOWN_DEPTH,True,True,'cadical195',True))
                    checked.append(dict(r=r,result='ALL_PLACEMENTS_PASS' if placement is None else 'COUNTEREXAMPLE'))
                    if placement is not None:
                        checked[-1]['retained_comparators']=sum(simulate(net,placement))
                        assert tuple(placement) not in seen
                        bad.append(placement);add(placement)
            entry['exact_checks']=checked
            if not bad:
                record['status']='BUDGET_SURVIVOR'
                record['sorts_all_binary_inputs']=verify_all(18,net)
                if not record['sorts_all_binary_inputs']:
                    failure=next(x for x in range(1<<18) if not is_sorted(apply_layers(net,x),18))
                    record['binary_counterexample']=dict(input=failure,output=apply_layers(net,failure))
                save();print(json.dumps({k:v for k,v in record.items() if k not in ('network','samples','rounds')}),flush=True)
                return
        if iteration%10==0:
            print(json.dumps(entry),flush=True)
        save()
    record['status']='TIME_LIMIT';save()
    print(json.dumps(dict(status=record['status'],rounds=iteration,samples=len(samples),seconds=record['seconds'])),flush=True)


if __name__=='__main__':main()
