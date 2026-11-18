#!/usr/bin/env python3
"""D17 profile with at least three retained gates in each of layers3 and4.

The first count uses the accepted round-ten theorem; the second uses
H9, N4 image rescheduling and the checked UU/UD five-layer exclusions.
The fixed first-two-layer cover is unchanged. Later matchings remain
arbitrary except deletion of immediately repeated comparators.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

from two_layer_cover import half_blind_family, type_step
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'depth-hand-proofs/verify'))
from sentinel_cegar import Master, neg, simulate
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--case',type=int,default=608)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--solver',default='cadical195')
    ap.add_argument('--proof',action='store_true')
    args=ap.parse_args()
    started=time.monotonic()
    cover=Path(__file__).with_name('prefixes')/'complete17.jsonl'
    case=[json.loads(x) for x in cover.read_text().splitlines()][args.case]
    states=[type_step(p,case['layers'][1]) for p in half_blind_family(17,case['layers']).values()]
    cnf=Master(17,3,first=0,adjacent=False,no_repeat=True)
    for a,b in case['layers'][1]:
        cnf.add(-cnf.g[1,a,b])
    second_rows=[]
    groups=[]
    for index,state in enumerate(states):
        begin=len(cnf.clauses)
        peak_first=cnf.var()
        real_first=[v==0 for v in state]
        missing=[cnf.var() for _ in range(17)]
        enc=CardEnc.atmost(missing,1,vpool=cnf.pool,encoding=EncType.seqcounter)
        cnf.clauses.extend(enc.clauses)
        for a in range(17):
            if real_first[a]:
                row=[cnf.g[1,min(a,b),max(a,b)] for b in range(17) if b!=a and real_first[b]]
                cnf.add(-peak_first,missing[a],*row)
        # Strengthened necessary first-layer bound (H9 plus image rescheduling).
        cnf.clauses.extend(CardEnc.atleast([cnf.g[1,a,b] for a,b in cnf.pairs if real_first[a] and real_first[b]], 3, vpool=cnf.pool, encoding=EncType.seqcounter).clauses)
        cur=[(v>=0,v>=1) for v in state]
        nxt=[(cnf.var(),cnf.var()) for _ in range(17)]
        for a,b in cnf.pairs:
            for q in (0,1):
                cnf.gate(cur[a][q],cur[b][q],nxt[a][q],nxt[b][q],cnf.g[1,a,b])
        for a in range(17):
            for q in (0,1):
                cnf.eq(cur[a][q],nxt[a][q],neg(cnf.used[1,a]))
        reals=[cnf.conj([lo,neg(hi)]) for lo,hi in nxt]
        # Proven second>=3: H9, N4 rescheduling, and checked UU/UD lemmas.
        second_edges=[cnf.conj([cnf.g[2,a,b],reals[a],reals[b]]) for a,b in cnf.pairs]
        cnf.clauses.extend(CardEnc.atleast(second_edges,3,vpool=cnf.pool,encoding=EncType.seqcounter).clauses)
        missing=[cnf.var() for _ in range(17)]
        enc=CardEnc.atmost(missing,1,vpool=cnf.pool,encoding=EncType.seqcounter)
        cnf.clauses.extend(enc.clauses)
        for a in range(17):
            # An idle real is one of the missing real vertices.
            cnf.add(peak_first,neg(reals[a]),missing[a],cnf.used[2,a])
        for a,b in cnf.pairs:
            g=cnf.g[2,a,b]
            # A real matched to a sentinel is also missing.
            cnf.add(peak_first,-g,neg(reals[a]),reals[b],missing[a])
            cnf.add(peak_first,-g,neg(reals[b]),reals[a],missing[b])
        second_rows.append(reals)
        groups.append(dict(index=index,begin=begin,end=len(cnf.clauses)))
    result=dict(case_id=case['case_id'],family_size=len(states),
                scope='Necessary first>=3, second>=3, no-repeat, and H9 peak4 conditions on all half-blind nine-real restrictions',
                cover_sha256=hashlib.sha256(cover.read_bytes()).hexdigest(),
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                status='BUILT',variables=cnf.pool.top,clauses=len(cnf.clauses),
                independently_proof_checked=False,iterations=0)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    def save():
        args.out.write_text(json.dumps(result,indent=2)+'\n')
    save()
    added=set()
    with Solver(name=args.solver,bootstrap_with=cnf.clauses,with_proof=args.proof) as solver:
        while True:
            ok=solver.solve()
            result['iterations']+=1
            if not ok:
                result['status']='UNSAT'
                if args.proof:
                    cert=args.out.with_suffix('')
                    cert.mkdir(parents=True,exist_ok=True)
                    problem=cert/'problem.cnf'
                    problem.write_text(f'p cnf {cnf.pool.top} {len(cnf.clauses)}\n'+''.join(' '.join(map(str,c))+' 0\n' for c in cnf.clauses))
                    proof=cert/'proof.drat'
                    proof.write_text('\n'.join(solver.get_proof())+'\n')
                    (cert/'groups.json').write_text(json.dumps(groups,indent=2)+'\n')
                    result.update(certificate_directory=str(cert),cnf_sha256=hashlib.sha256(problem.read_bytes()).hexdigest(),
                                  proof_sha256=hashlib.sha256(proof.read_bytes()).hexdigest())
                break
            layers=cnf.network(solver.get_model())[1:]
            profiles=[simulate(layers,state) for state in states]
            assert all(max(p)==4 and min(p)>=3 for p in profiles)
            bad=[i for i,p in enumerate(profiles) if p[1]==0]
            result.update(next_layers=layers,profiles=profiles,second_nonempty_refinements=len(added))
            if not bad:
                result['status']='SURVIVOR'
                break
            for i in bad:
                assert i not in added
                added.add(i)
                before=len(cnf.clauses)
                real=second_rows[i]
                cnf.add(cnf.disj(cnf.conj([cnf.g[2,a,b],real[a],real[b]]) for a,b in cnf.pairs))
                for clause in cnf.clauses[before:]:
                    solver.add_clause(clause)
            save()
    result.update(seconds=round(time.monotonic()-started,4),variables=cnf.pool.top,clauses=len(cnf.clauses))
    save()
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
