#!/usr/bin/env python3
"""Separate semantic rank and wire interval bounds for the case116 cut6 problem."""
import argparse,hashlib,json,time
from pathlib import Path
from pysat.card import CardEnc,EncType
from netsat import neg,prefix_images,verify_all
from probe_frontier import ProbeModel
from interval_frontier import actual_intervals,add_state_bounds


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--ranks',default='');ap.add_argument('--wires',default='all');ap.add_argument('--proof',action='store_true');args=ap.parse_args()
    root=Path(__file__).parent
    seed=json.loads((root/'results/complete13-d8-single-structural/n13-r0116/result.json').read_text())
    n=13;prefix=seed['prefix'];universe=sorted(prefix_images(n,prefix));start=time.monotonic()
    ranks=list(range(n)) if args.ranks=='all' else [int(s) for s in args.ranks.split(',') if s]
    wires=list(range(n)) if args.wires=='all' else [int(s) for s in args.wires.split(',') if s]
    if args.proof:
        import netsat
        from prefix_drat import RecordingSolver
        netsat.Solver=RecordingSolver
    m=ProbeModel(n,6,universe,phi=False)
    lower=[[True]+[m.new_var() for _ in range(n-1)]+[False] for _ in range(n)]
    upper=[[False]+[m.new_var() for _ in range(n-1)]+[True] for _ in range(n)]
    for c in range(n):
        L,U=lower[c],upper[c]
        for k in range(n):
            m.add([neg(L[k+1]),L[k]]);m.add([neg(U[k]),U[k+1]]);m.add([neg(L[k]),neg(U[k])])
        m.add([neg(L[c+1])]);m.add([neg(U[c])])
    groups=[];assumptions=[]
    for c in wires:
        guard=m.new_var();assumptions.append(guard);groups.append(dict(kind='wire',index=c,selector=guard))
        for k in range(n-4):m.add([-guard,lower[c][k+1],upper[c][k+4]])
    for k in ranks:
        guard=m.new_var();assumptions.append(guard);groups.append(dict(kind='rank',index=k,selector=guard));row=[]
        for c in range(n):
            s=m.new_var();row.append(s)
            m.add([-s,neg(lower[c][k+1])]);m.add([-s,neg(upper[c][k])]);m.add([s,lower[c][k+1],upper[c][k]])
        enc=CardEnc.atmost(row,4,top_id=m.nv,encoding=EncType.seqcounter);m.nv=max(m.nv,enc.nv)
        for clause in enc.clauses:m.add([-guard,*clause])
    for x in universe:add_state_bounds(m,x,m.simulate_to_cut(x,4),lower,upper)
    if args.proof:
        for a in assumptions:m.add([a])
        certificate=args.out.with_suffix('');certificate.mkdir(parents=True,exist_ok=True)
        cnf=certificate/'problem.cnf'
        cnf.write_text(f'p cnf {m.nv} {len(m.S.clauses)}\n'+''.join(' '.join(map(str,c))+' 0\n' for c in m.S.clauses))
    result=dict(case_id='n13-r0116',scope='Every four-layer continuation of the fixed relabelled prefix; cut6 endpoint bounds only, no common-ending routing',prefix=prefix,wires=wires,ranks=ranks,variables=m.nv,clauses=m.ncl,status='BUILT',independently_proof_checked=False,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    args.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='prefix'}),flush=True)
    try:
        ok=m.S.solve(assumptions=[] if args.proof else assumptions)
        result['status']='SURVIVOR' if ok else 'UNSAT'
        if ok:
            layers=m.network(m.S.get_model())[:4]
            intervals,lo,hi=actual_intervals(n,prefix,layers)
            assert all(intervals[c][1]-intervals[c][0]+1<=4 for c in wires)
            assert all(sum(a<=k<=b for a,b in intervals)<=4 for k in ranks)
            result.update(free_layers=layers,intervals=intervals,rank_degrees=[sum(a<=k<=b for a,b in intervals) for k in range(n)],wire_degrees=[b-a+1 for a,b in intervals],low_witnesses=lo,high_witnesses=hi)
        else:
            if args.proof:
                proof=certificate/'proof.drat';proof.write_text('\n'.join(m.S.get_proof())+'\n')
                result.update(certificate_directory=str(certificate),cnf_sha256=hashlib.sha256(cnf.read_bytes()).hexdigest(),proof_sha256=hashlib.sha256(proof.read_bytes()).hexdigest())
            else:
                core=set(m.S.get_core());result['semantic_assumption_core']=[g for g in groups if g['selector'] in core]
        result['seconds']=time.monotonic()-start;args.out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],result['seconds'],flush=True)
    finally:m.S.delete()

if __name__=='__main__':main()
