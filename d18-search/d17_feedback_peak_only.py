#!/usr/bin/env python3
"""Test pure two-layer peak coverage, allowing repeats and empty restrictions."""
import argparse
import json
from pathlib import Path
import sys
import time
from two_layer_cover import half_blind_family,type_step
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'depth-hand-proofs/verify'))
from sentinel_cegar import Master,simulate
from pysat.formula import CNF
from pysat.solvers import Solver


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    raw=CNF(from_file=str(Path(__file__).with_name('results')/'d17-feedback-repeat-r0608/result/problem.cnf'))
    structure=Master(17,3,first=0,adjacent=False,no_repeat=True)
    firstvars={structure.g[1,a,b] for a,b in structure.pairs}
    cover=Path(__file__).with_name('prefixes')/'complete17.jsonl'
    case=[json.loads(x) for x in cover.read_text().splitlines()][608]
    forbid={-structure.g[1,a,b] for a,b in case['layers'][1]}
    removed=[i for i,c in enumerate(raw.clauses) if (len(c)==36 and set(c)<=firstvars) or (len(c)==1 and c[0] in forbid)]
    assert len(removed)==26
    chosen=set(removed)
    clauses=[c for i,c in enumerate(raw.clauses) if i not in chosen]
    result=dict(status='BUILT',removed_clauses=removed,scope='Case608 pure peak coverage by arbitrary two matchings: repeats and empty retained layers allowed',independently_proof_checked=False)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    started=time.monotonic()
    with Solver(name='cadical195',bootstrap_with=clauses,with_proof=True) as solver:
        ok=solver.solve()
        result['status']='SURVIVOR' if ok else 'UNSAT'
        if ok:
            layers=structure.network(solver.get_model())[1:]
            states=[type_step(p,case['layers'][1]) for p in half_blind_family(17,case['layers']).values()]
            profiles=[simulate(layers,s) for s in states]
            assert all(max(p)==4 for p in profiles)
            result.update(next_layers=layers,profiles=profiles)
        else:
            cert=args.out.with_suffix('')
            cert.mkdir(parents=True,exist_ok=True)
            (cert/'problem.cnf').write_text(f'p cnf {raw.nv} {len(clauses)}\n'+''.join(' '.join(map(str,c))+' 0\n' for c in clauses))
            (cert/'proof.drat').write_text('\n'.join(solver.get_proof())+'\n')
            result['certificate_directory']=str(cert)
    result['seconds']=round(time.monotonic()-started,4)
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='removed_clauses'}),flush=True)


if __name__=='__main__':
    main()
