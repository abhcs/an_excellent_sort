#!/usr/bin/env python3
"""Bind the existing pure608 proof to its current encoder and exact family.

Rebuilds CNF but intercepts Solver construction: no SAT or DRAT rerun.
The already checked proof is reused only after all byte hashes agree.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import time
from d17_feedback_round9_check import states_of

ROOT=Path(__file__).parent


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    start=time.monotonic();audit=json.loads((ROOT/'results/d17-feedback-fourteen-audit.json').read_text())
    manifest=json.loads((ROOT/'results/d17-feedback-fourteen-main/result/check/certificate.json').read_text())
    source=ROOT/'d17_feedback_fourteen.py';states_path=ROOT/'results/d17-feedback-fourteen-states.json'
    problem=ROOT/'results/d17-feedback-fourteen-main/result/problem.cnf'
    proof=ROOT/'results/d17-feedback-fourteen-main/result/proof.drat'
    library=ROOT.parent/'depth-hand-proofs/verify/sentinel_cegar.py'
    checker=Path('/private/tmp/d18-structural-drat-trim/drat-trim')
    for key,path in [('source_sha256',source),('states_sha256',states_path),('cnf_sha256',problem),
                     ('proof_sha256',proof),('library_sha256',library),('checker_sha256',checker)]:
        assert digest(path)==audit[key],(key,path)
    assert manifest['independently_proof_checked'] and manifest['returncode']==0
    assert all(manifest[k]==audit[k] for k in ('cnf_sha256','proof_sha256','checker_sha256'))
    cover=[json.loads(s) for s in (ROOT/'prefixes/complete17.jsonl').read_text().splitlines()]
    original=states_of(cover[608]);small=json.loads(states_path.read_text())
    labels=small['compact_to_original'];removed=sorted(set(range(17))-set(labels))
    assert removed==[0,3,11] and all(s[v]==-1 for s in original for v in removed)
    assert {tuple(s[v] for v in labels) for s in original}==set(map(tuple,small['states']))
    assert len(original)==len(small['states'])==20

    spec=importlib.util.spec_from_file_location('pure608_encoder_audit',source)
    encoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(encoder)
    captured={}
    class BuildCaptured(Exception):pass
    class NoSolver:
        def __init__(self,**kwargs):
            captured['clauses']=kwargs['bootstrap_with'];raise BuildCaptured
    encoder.Solver=NoSolver
    real_argv=sys.argv
    try:
        with tempfile.TemporaryDirectory(prefix='d17-round9-pure608-build-') as temp:
            output=Path(temp)/'build.json'
            sys.argv=[str(source),'--states',str(states_path),'--out',str(output)]
            try:encoder.main()
            except BuildCaptured:pass
            else:raise AssertionError('Solver interception did not occur')
            built=json.loads(output.read_text())
    finally:sys.argv=real_argv
    clauses=captured['clauses']
    raw=(f'p cnf {built["variables"]} {len(clauses)}\n'+''.join(' '.join(map(str,c))+' 0\n' for c in clauses)).encode()
    assert hashlib.sha256(raw).hexdigest()==audit['cnf_sha256']
    assert built['variables']==2150 and len(clauses)==19412
    result=dict(status='VERIFIED_EXISTING_PURE_PROOF_BINDING',new_sat_run=False,new_drat_run=False,
                original_case='n17-r0608',original_width=17,pruned_width=14,
                original_to_pruned_labels=labels,removed_fixed_negative_wires=removed,
                exact_signed_family_reconstructed=True,rebuilt_cnf_identical_to_checked_cnf=True,
                empty_retained_layers_allowed=True,repeated_gates_allowed=True,
                first_matching_arbitrary=True,second_matching_arbitrary=True,
                variables=2150,clauses=19412,
                encoder_sha256=digest(source),cnf_sha256=digest(problem),proof_sha256=digest(proof),
                reused_checked_manifest=str(manifest and ROOT/'results/d17-feedback-fourteen-main/result/check/certificate.json'),
                audit_source_sha256=digest(Path(__file__)),seconds=round(time.monotonic()-start,4))
    (ROOT/'results/d17-feedback-round9-pure608-binding.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
