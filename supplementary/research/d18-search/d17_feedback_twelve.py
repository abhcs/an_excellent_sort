#!/usr/bin/env python3
"""Direct pure two-matching peak coverage on supplied 12-wire nine-real states.

There are no fixed prefix gates, nonrepetition clauses, nonemptiness
conditions, or ending normal forms. Each state must retain four gates in
the first matching or in the second after exact ternary transport.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'depth-hand-proofs/verify'))
from sentinel_cegar import Master,neg
from pysat.card import CardEnc,EncType
from pysat.solvers import Solver


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replay(layers,state):
    """Direct value replay, independent of the SAT type variables."""
    values=list(state)
    counts=[]
    for matching in layers:
        used=[v for edge in matching for v in edge]
        assert len(used)==len(set(used))
        counts.append(sum(values[a]==values[b]==0 for a,b in matching))
        for a,b in matching:
            values[a],values[b]=sorted((values[a],values[b]))
    return counts


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--states',type=Path,required=True)
    ap.add_argument('--indices',type=int,nargs='+')
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--solver',default='cadical195')
    ap.add_argument('--proof',action='store_true')
    args=ap.parse_args()
    started=time.monotonic()
    supplied=json.loads(args.states.read_text())
    n=supplied['n']
    assert n==12
    indices=args.indices if args.indices is not None else list(range(len(supplied['states'])))
    assert len(set(indices))==len(indices)
    states=[supplied['states'][i] for i in indices]
    assert all(len(s)==n and s.count(0)==9 and set(s)<={-1,0,1} for s in states)
    cnf=Master(n,3,first=0,adjacent=False,no_repeat=False)
    groups=[]
    for index,state in zip(indices,states):
        begin=len(cnf.clauses)
        peak_first=cnf.var()
        real_first=[v==0 for v in state]
        missing=[cnf.var() for _ in range(n)]
        cnf.clauses.extend(CardEnc.atmost(missing,1,vpool=cnf.pool,encoding=EncType.seqcounter).clauses)
        for a in range(n):
            if real_first[a]:
                cnf.add(-peak_first,missing[a],
                        *(cnf.g[1,min(a,b),max(a,b)] for b in range(n) if b!=a and real_first[b]))
        cur=[(v>=0,v>=1) for v in state]
        nxt=[(cnf.var(),cnf.var()) for _ in range(n)]
        for a,b in cnf.pairs:
            for q in (0,1):
                cnf.gate(cur[a][q],cur[b][q],nxt[a][q],nxt[b][q],cnf.g[1,a,b])
        for a in range(n):
            for q in (0,1):
                cnf.eq(cur[a][q],nxt[a][q],neg(cnf.used[1,a]))
        reals=[cnf.conj([lo,neg(hi)]) for lo,hi in nxt]
        missing=[cnf.var() for _ in range(n)]
        cnf.clauses.extend(CardEnc.atmost(missing,1,vpool=cnf.pool,encoding=EncType.seqcounter).clauses)
        for a in range(n):
            cnf.add(peak_first,neg(reals[a]),missing[a],cnf.used[2,a])
        for a,b in cnf.pairs:
            g=cnf.g[2,a,b]
            cnf.add(peak_first,-g,neg(reals[a]),reals[b],missing[a])
            cnf.add(peak_first,-g,neg(reals[b]),reals[a],missing[b])
        groups.append(dict(index=index,begin=begin,end=len(cnf.clauses)))
    result=dict(status='BUILT',n=n,indices=indices,family_size=len(states),
                scope='Pure peak coverage by two arbitrary 12-wire matching layers; repeats and empty retained layers allowed',
                variables=cnf.pool.top,clauses=len(cnf.clauses),
                states_sha256=digest(args.states),source_sha256=digest(Path(__file__)),
                library_sha256=digest(Path(__file__).resolve().parents[1]/'depth-hand-proofs/verify/sentinel_cegar.py'),
                compact_to_original=supplied['compact_to_original'],
                independently_proof_checked=False)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    def save():
        args.out.write_text(json.dumps(result,indent=2)+'\n')
    save()
    with Solver(name=args.solver,bootstrap_with=cnf.clauses,with_proof=args.proof) as solver:
        ok=solver.solve()
        result['status']='SURVIVOR' if ok else 'UNSAT'
        if ok:
            layers=cnf.network(solver.get_model())[1:]
            profiles=[replay(layers,s) for s in states]
            assert all(max(p)==4 for p in profiles)
            result.update(next_layers=layers,profiles=profiles,independently_replayed=True)
        elif args.proof:
            cert=args.out.with_suffix('')
            cert.mkdir(parents=True,exist_ok=True)
            problem=cert/'problem.cnf'
            problem.write_text(f'p cnf {cnf.pool.top} {len(cnf.clauses)}\n'+''.join(' '.join(map(str,c))+' 0\n' for c in cnf.clauses))
            proof=cert/'proof.drat'
            proof.write_text('\n'.join(solver.get_proof())+'\n')
            (cert/'groups.json').write_text(json.dumps(groups,indent=2)+'\n')
            result.update(certificate_directory=str(cert),cnf_sha256=digest(problem),proof_sha256=digest(proof))
    result['seconds']=round(time.monotonic()-started,4)
    save()
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
