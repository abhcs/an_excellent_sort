#!/usr/bin/env python3
"""Review artifacts and reconstruct the three capacity CNFs without solving."""
import hashlib
import json
from pathlib import Path
import time

import netsat
from netsat import neg,prefix_images
from probe_frontier import ProbeModel
from interval_frontier import add_state_bounds
from rank_block_capacity_cnf import add_block_capacity
from relabel import relabel_vec

HERE=Path(__file__).resolve().parent


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


class Recorder:
    def __init__(self,**kw):self.clauses=[]
    def add_clause(self,c):self.clauses.append(list(c))


def digest(nv,clauses):
    h=hashlib.sha256(f'p cnf {nv} {len(clauses)}\n'.encode())
    for c in clauses:h.update((' '.join(map(str,c))+' 0\n').encode())
    return h.hexdigest()


def main():
    start=time.monotonic()
    netsat.Solver=Recorder
    cover=[json.loads(x) for x in (HERE/'prefixes/complete13.jsonl').read_text().splitlines()]
    audits=[]
    for case in (3,56,112):
        path=HERE/f'results/d13-rank-capacity-round8-r{case:04}.json'
        info=json.loads(path.read_text());n=13
        assert info['source_case']==cover[case]
        assert info['source_sha256']==sha(HERE/'d13_rank_capacity_round8.py')
        assert info['cover_sha256']==sha(HERE/'prefixes/complete13.jsonl')
        for name,value in info['dependencies_sha256'].items():assert value==sha(HERE/name),name
        universe=sorted(prefix_images(n,info['prefix']))
        original=prefix_images(n,cover[case]['layers'])
        assert {relabel_vec(x,info['output_permutation'],n) for x in original}==set(universe)
        assert len(universe)==info['inputs']
        m=ProbeModel(n,6,universe,phi=False)
        lower=[[True]+[m.new_var() for _ in range(n-1)]+[False] for _ in range(n)]
        upper=[[False]+[m.new_var() for _ in range(n-1)]+[True] for _ in range(n)]
        for c in range(n):
            l,u=lower[c],upper[c]
            for k in range(n):
                m.add([neg(l[k+1]),l[k]])
                m.add([neg(u[k]),u[k+1]])
                m.add([neg(l[k]),neg(u[k])])
            m.add([neg(l[c+1])]);m.add([neg(u[c])])
        begin=m.ncl
        stats=add_block_capacity(m,lower,upper)
        end=m.ncl
        assert stats==info['block_capacity'] and end-begin==498
        parity=[]
        for c in range(n):
            for d in range(c+1,n):
                for a in range(max(0,c-3),min(c,n-4)+1):
                    for b in range(max(0,d-3),min(d,n-4)+1):
                        if abs(a-b) in (1,3):
                            parity.append([lower[c][a+1],upper[c][a+3],lower[d][b+1],upper[d][b+3]])
        assert len(parity)==222
        selectors=[]
        for c in range(n):
            a=m.new_var();selectors.append(a)
            for k in range(n-4):m.add([-a,lower[c][k+1],upper[c][k+4]])
        for x in universe:add_state_bounds(m,x,m.simulate_to_cut(x,4),lower,upper)
        for a in selectors:m.add([a])
        assert m.nv==info['variables'] and m.ncl==info['clauses']
        assert digest(m.nv,m.S.clauses)==info['cnf_sha256']
        baseline=json.loads((HERE/f'results/d13-rank-capacity-round8-baseline-r{case:04}.json').read_text())
        assert baseline['prefix']==info['prefix'] and baseline['variables']==m.nv
        replaced=m.S.clauses[:begin]+parity+m.S.clauses[end:]
        assert digest(m.nv,replaced)==baseline['cnf_sha256']
        certificates=[]
        for tag,data in [('capacity',info),('parity_baseline',baseline)]:
            directory=Path(data['certificate_directory'])
            assert data['status']=='UNSAT' and data['independently_proof_checked']
            assert sha(directory/'problem.cnf')==data['cnf_sha256']
            assert sha(directory/'proof.drat')==data['proof_sha256']
            assert 's VERIFIED' in (directory/'check.log').read_text()
            terminal=json.loads((directory/'check-terminal.json').read_text())
            assert terminal['terminal']=='EXITED' and terminal['returncode']==0 and terminal['verified']
            worker=json.loads(directory.with_name(directory.name+'-terminal.json').read_text())
            assert worker['terminal']=='EXITED' and worker['returncode']==0
            certificates.append(dict(kind=tag,cnf_sha256=data['cnf_sha256'],proof_sha256=data['proof_sha256'],
                                     check_log_sha256=sha(directory/'check.log'),worker_seconds=worker['seconds'],
                                     check_seconds=terminal['seconds']))
        audits.append(dict(case=case,capacity_clause_range_zero_based=[begin,end],
                           capacity_clauses=498,baseline_parity_clauses=222,
                           remaining_cnf_identical=True,complete_cnf_reconstruction=True,
                           final_adjacent_edge_variables={str(k):v for k,v in m.g[-1].items()},
                           lower_variables=lower,strict_upper_variables=upper,certificates=certificates))
    control=json.loads((HERE/'results/rank-block-capacity-cnf-verification.json').read_text())
    assert control['source_sha256']==sha(HERE/'rank_block_capacity_cnf.py')
    assert control['checker_sha256']==sha(HERE/'rank_block_capacity_cnf_verify.py')
    report=dict(status='REVIEWED_SOUND',uses_sat=False,new_solver_calls=0,
                scope='Exact adjacent-ending required-interval reachability; necessary for sorting completions after deleting redundant suffix comparisons. It does not claim data sorting.',
                mathematical_review=[
                    'A singleton guard is absence of both adjacent last edges; a two-wire guard is its last edge. Matching constraints make these exact block predicates.',
                    'Strict U[c,k]=(hi<k): left demand is not L[c,start], right demand is not U[c,end+1]. The one-direction disjunction and adjacent-neighbor extent bounds are correctly indexed.',
                    'Given no bidirectional wire demand, max(0,RA-LB)+max(0,LC-RB)<=b-LB-RB is equivalent to RA+RB<=b, LB+LC<=b, and RA+LC<=b.',
                    'Every forbidden cardinal subset has the correct negated block guards. Boundary constants, tautologies, duplicates, and missing neighbors are handled without additional variables.',
                    'The worker changes the previous parity encoder only by replacing 222 parity clauses with 498 capacity clauses and adding direct reachability replay on SAT. All matching, endpoint, simulation, and semantic-selector clauses retain identical variable IDs.',
                    'Full fixed-prefix binary images are used. Genuine completions can choose the exact attainable intervals, so interval overapproximation does not remove a genuine completion.',
                    'Last-layer adjacency follows Lemma 3 for nonredundant sorters. Removing redundant gates preserves the fixed-prefix cut image; restoring fixed-prefix redundant gates therefore preserves the normalized completion.'
                ],
                primary_normal_form_source='https://arxiv.org/html/1411.6408#S3',
                primary_source_checked='Lemma 3 and preceding redundancy definition, read independently during review.',
                independent_finite_control=control,
                certificate_audits=audits,
                performance_scope='The original parity worker also closes all three cases in the fresh bounded baseline. These certificates establish new tested case coverage, not a separation proving these cases require the capacity strengthening.',
                substantive_issues=[],
                documentation_note='The old interval_frontier.py module docstring describes U non-strictly, but its code and the new capacity code consistently use strict U; no encoding error.',
                reviewed_sha256={name:sha(HERE/name) for name in ['rank-block-capacity-encoding.md','fixed-ending-block-capacity.md','rank_block_capacity_cnf.py','rank_block_capacity_cnf_verify.py','d13_rank_capacity_round8.py','d13_rank_parity_probe.py']},
                source_sha256=sha(Path(__file__)),seconds=time.monotonic()-start)
    (HERE/'results/d13_feedback_round8-capacity-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],cases=[x['case'] for x in audits],seconds=report['seconds'],new_solver_calls=0),indent=2))


if __name__=='__main__':main()
