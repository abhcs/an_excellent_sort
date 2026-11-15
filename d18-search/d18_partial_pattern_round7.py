#!/usr/bin/env python3
"""Test the proved partial-L6 clauses against the earlier combined relaxation.

Run under an external30-second cap. SAT only gives a necessary-condition
survivor. It never establishes a sorting completion.
"""
import hashlib,json,time
from pathlib import Path
from pysat.solvers import Solver
from d18_hand_next_reschedule import PAIRS,G,build
from d18_hand_round5_combined import replay_demands

HERE=Path(__file__).resolve().parent

def main():
    fixed_path=HERE/'results/d18-rank-partner-round7-partial-certificate.json'
    fixed=json.loads(fixed_path.read_text())
    for name in ('beam00','beam16','beam32'):
        start=time.monotonic();path=HERE/'results'/f'd18_hand_round5_combined-{name}.json'
        data=json.loads(path.read_text());families=[r for r in fixed['families'] if r['source']==name]
        assert all(r['prefix']==data['prefix'] for r in families)
        clauses,nv,_=build(data['rescheduling_items'],assumptions=False)
        clauses += [r['clause'] for r in data['component_cuts']]
        cuts=[[-G[tuple(e)] for e in r['fixed_sixth']] for r in families]
        clauses+=cuts
        folder=HERE/'results'/f'd18-partial-pattern-round7-{name}';folder.mkdir(exist_ok=True)
        cnf=folder/'problem.cnf'
        cnf.write_text(f'p cnf {nv} {len(clauses)}\n'+''.join(' '.join(map(str,c))+' 0\n' for c in clauses))
        with Solver(name='cadical195',bootstrap_with=clauses,with_proof=True) as solver:
            sat=solver.solve()
            result=dict(status='SURVIVOR' if sat else 'UNSAT_UNCHECKED',name=name,prefix=data['prefix'],
                new_clauses=cuts,variables=nv,clauses=len(clauses),
                scope='Common L6 satisfying R7/R8 rescheduling, R9 components, and proved partial-pattern exclusions',
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                hand_certificate_sha256=hashlib.sha256(fixed_path.read_bytes()).hexdigest(),
                cnf_sha256=hashlib.sha256(cnf.read_bytes()).hexdigest())
            if sat:
                model=set(solver.get_model());layer=[list(e) for e in PAIRS if G[e] in model]
                assert all(not set(map(tuple,r['fixed_sixth']))<=set(map(tuple,layer)) for r in families)
                result.update(layer6=layer,replay=replay_demands(data,layer))
            else:
                proof=folder/'proof.drat';proof.write_text('\n'.join(solver.get_proof())+'\n')
                result['proof_sha256']=hashlib.sha256(proof.read_bytes()).hexdigest()
        result['seconds']=time.monotonic()-start
        folder.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({k:v for k,v in result.items() if k not in ('prefix','new_clauses')}),flush=True)
if __name__=='__main__':main()
