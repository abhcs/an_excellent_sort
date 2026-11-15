#!/usr/bin/env python3
"""No-solver reconstruction and binding of the round9 exact-triple artifacts."""
import hashlib
import json
from pathlib import Path
import time

import netsat
from netsat import neg,prefix_images,verify_all
from probe_frontier import ProbeModel
from interval_frontier import add_state_bounds,actual_intervals
from endpoint_cegar import wire_endpoints
from rank_block_capacity_cnf import add_block_capacity
from exact_rank_triples import add_exact_endpoints,add_no_full_triples
from relabel import relabel_vec
from d13_feedback_round8_capacity_review import Recorder,digest

HERE=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    start=time.monotonic();netsat.Solver=Recorder
    batch=json.loads((HERE/'results/rank-triples-round9-batch.json').read_text())
    bylabel={r['label']:r for r in batch}
    cover=[json.loads(s) for s in (HERE/'prefixes/complete13.jsonl').read_text().splitlines()]
    audits=[]
    for label in ('positive4','negative4','positive18','d13-0004','d13-0055','d13-0111'):
        info=json.loads((HERE/f'results/rank-triples-round9-{label}.json').read_text())
        terminal=bylabel[label]
        assert terminal['terminal']=='EXITED' and terminal['returncode']==0
        cmd=terminal['command']
        d13=label.startswith('d13-')
        source='d13_rank_triples_round9.py' if d13 else 'prefix_rank_triples_round9.py'
        assert info['source_sha256']==sha(HERE/source)
        for name,value in info['dependencies_sha256'].items():assert value==sha(HERE/name),name
        n=13 if d13 else info['n'];prefix=info['prefix']
        universe=sorted(prefix_images(n,prefix))
        assert len(universe)==info['inputs']
        if d13:
            case=int(label[-4:]);assert info['source_case']==cover[case]
            assert info['cover_sha256']==sha(HERE/'prefixes/complete13.jsonl')
            assert {relabel_vec(x,info['output_permutation'],n) for x in prefix_images(n,cover[case]['layers'])}==set(universe)
            free=4;m=ProbeModel(n,6,universe,phi=False)
            lower=[[True]+[m.new_var() for _ in range(n-1)]+[False] for _ in range(n)]
            upper=[[False]+[m.new_var() for _ in range(n-1)]+[True] for _ in range(n)]
            for c in range(n):
                l,u=lower[c],upper[c]
                for k in range(n):
                    m.add([neg(l[k+1]),l[k]]);m.add([neg(u[k]),u[k+1]]);m.add([neg(l[k]),neg(u[k])])
                m.add([neg(l[c+1])]);m.add([neg(u[c])])
            assert add_block_capacity(m,lower,upper)==info['block_capacity']
            selectors=[]
            for c in range(n):
                a=m.new_var();selectors.append(a)
                for k in range(n-4):m.add([-a,lower[c][k+1],upper[c][k+4]])
        else:
            seed_path=Path(cmd[cmd.index('--seed')+1]);assert sha(seed_path)==info['seed_sha256']
            assert json.loads(seed_path.read_text())['prefix']==prefix
            free=info['cut']-len(prefix)
            assert free>=0 and info['depth']-info['cut']==2
            m=ProbeModel(n,info['depth']-len(prefix),universe,phi=False,nored0=False)
            lower,upper=wire_endpoints(m,list(range(n)),4)
            assert add_block_capacity(m,lower,upper)==info['block_capacity']
            assert info['combined_clauses']==0
            if '--witness' in cmd:
                network=json.loads(Path(cmd[cmd.index('--witness')+1]).read_text())['layers']
                assert len(network)==info['depth'] and network[:len(prefix)]==prefix and verify_all(n,network)
                for t,layer in enumerate(network[len(prefix):]):
                    chosen=set(map(tuple,layer));assert chosen<=set(m.g[t])
                    for e,v in m.g[t].items():m.add([v if e in chosen else -v])
                iv,_,_=actual_intervals(n,prefix,network[len(prefix):len(prefix)+free])
                assert iv==[(r['lo'],r['hi']) for r in info['intervals']]
                assert not any(all(iv[c]==(a,a+2) for c in range(a,a+3)) for a in range(n-2))
                assert info['exact_endpoint_assignment_replayed'] and info['no_full_triples_replayed']
        states={x:m.simulate_to_cut(x,free) for x in universe}
        for x,state in states.items():add_state_bounds(m,x,state,lower,upper)
        reverse_begin=m.ncl
        assert add_exact_endpoints(m,states,lower,upper)==info['exact_endpoints']
        triple_begin=m.ncl
        assert add_no_full_triples(m,lower,upper)==info['full_triple_clauses']
        triple_end=m.ncl
        if d13:
            for a in selectors:m.add([a])
        assert m.nv==info['variables'] and m.ncl==info['clauses']
        directory=Path(info['certificate_directory']) if not d13 else HERE/f'results/rank-triples-round9-{label}'
        assert digest(m.nv,m.S.clauses)==info['cnf_sha256']==sha(directory/'problem.cnf')
        row=dict(label=label,whole_cnf_reconstructed=True,cnf_sha256=info['cnf_sha256'],
                 variables=m.nv,clauses=m.ncl,exact_reverse_clause_range=[reverse_begin,triple_begin],
                 full_triple_clause_range=[triple_begin,triple_end],worker_seconds=terminal['seconds'])
        if 'proof_sha256' in info:
            assert info['independently_proof_checked']
            assert sha(directory/'proof.drat')==info['proof_sha256']
            assert 's VERIFIED' in (directory/'check.log').read_text()
            check=json.loads((directory/'check-terminal.json').read_text())
            assert check['verified'] and check['terminal']=='EXITED' and check['returncode']==0
            row.update(proof_sha256=info['proof_sha256'],check_seconds=check['seconds'],
                       check_log_sha256=sha(directory/'check.log'),status='CHECKED_UNSAT')
        else:row.update(status='FIXED_SORTER_POSITIVE_CONTROL',actual_endpoints_replayed=True)
        audits.append(row)
    timeouts=[]
    for label in ('beam00','beam16'):
        terminal=bylabel[label];assert terminal['terminal']=='TIMEOUT_KILLED'
        info=json.loads((HERE/f'results/rank-triples-round9-{label}.json').read_text())
        assert info['status']=='BUILT'
        assert info['cnf_sha256']==sha(HERE/f'results/rank-triples-round9-{label}/problem.cnf')
        assert info['source_sha256']==sha(HERE/'prefix_rank_triples_round9.py')
        timeouts.append(dict(label=label,status='TIMEOUT_NOT_UNSAT',seconds=terminal['seconds']))
    previous=json.loads((HERE/'results/structural-cover-progress-round8.json').read_text())['D13']['cases']
    new=[4,55,111];assert not set(new)&set(previous)
    complete=sorted(set(previous)|set(new));assert len(complete)==15
    report=dict(status='REVIEWED_SOUND',uses_sat=False,new_solver_calls=0,substantive_issues=[],
                reviewed_delta=[
                    'The D13 worker changes no CNF construction: the only delta from reviewed round8 is exact endpoint and no-full-triple replay on SAT.',
                    'The generic worker additionally allows zero free prefix layers. simulate_to_cut(x,0) returns the complete fixed-prefix bits; all endpoint and capacity obligations remain well-defined with two remaining layers.',
                    'Positive model literal evaluation handles Boolean boundary constants and signed integer variables correctly. Replayed upper predicates use strict hi<k.',
                    'No actual ending data simulation is added; survivors remain necessary-condition witnesses. Fixed sorter controls additionally have their full sorting property checked.'
                ],
                certificate_and_control_audits=audits,timeout_audits=timeouts,
                accepted_new_complete_cover_cases=new,accepted_total_cases=complete,accepted_count=15,total_cover_cases=117,
                minor_metadata_note='The negative4 result still says UNSAT_UNCHECKED although independently_proof_checked is true and its hash-matched DRAT log is VERIFIED; the review records its actual checked status.',
                performance_scope='No parity/capacity baseline is reviewed for these three new cases. The results establish coverage but not that exact triples alone caused the exclusions.',
                reviewed_sha256={s:sha(HERE/s) for s in ['d13_rank_triples_round9.py','prefix_rank_triples_round9.py','exact_rank_triples.py','rank_block_capacity_cnf.py','d13_rank_triples_round8.py','prefix_rank_triples_round8.py']},
                source_sha256=sha(Path(__file__)),seconds=time.monotonic()-start,running_jobs=[])
    (HERE/'results/d13-feedback-round9-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],reconstructed_cnfs=len(audits),new_cases=new,accepted_count=15,seconds=report['seconds']),indent=2))


if __name__=='__main__':main()
