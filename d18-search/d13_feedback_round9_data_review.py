#!/usr/bin/env python3
"""Review and reconstruct direct-data ending controls without a solver call."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import time
import netsat
from netsat import prefix_images,verify_all,apply_layers
from probe_frontier import ProbeModel
from two_layer_data_ending import add_data_ending
from d13_feedback_round8_capacity_review import Recorder,digest
from d13_feedback_round9_data_dp import profiles,ending

HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    started=time.monotonic();netsat.Solver=Recorder
    # Replay the unchanged truth checker with output redirected, preserving root files.
    checker=HERE/'two_layer_data_ending_verify.py'
    spec=importlib.util.spec_from_file_location('reviewed_data_ending_checker',checker)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    with tempfile.TemporaryDirectory(prefix='d13_feedback_round9_data_review-') as tmp:
        temp=Path(tmp);(temp/'results').mkdir()
        (temp/'two_layer_data_ending.py').symlink_to(HERE/'two_layer_data_ending.py')
        mod.HERE=temp
        with contextlib.redirect_stdout(io.StringIO()):mod.main()
        replay=json.loads((temp/'results/two-layer-data-ending-verification.json').read_text())
    original=json.loads((HERE/'results/two-layer-data-ending-verification.json').read_text())
    assert {k:v for k,v in replay.items() if k!='seconds'}=={k:v for k,v in original.items() if k!='seconds'}
    assert sum(replay['counts'].values())==70800
    audits=[];cache={};known_dp=None
    for variant in ('ending','normal'):
        batch=json.loads((HERE/f'results/data-{variant}-round9-batch.json').read_text())
        bylabel={row['label']:row for row in batch}
        for label in ('positive4','negative4','positive18','beam00','beam16'):
            terminal=bylabel[label]
            path=HERE/f'results/data-{variant}-round9-{label}.json'
            info=json.loads(path.read_text());n=info['n'];prefix=info['prefix']
            source=f'prefix_data_{variant}_round9.py'
            assert info['source_sha256']==sha(HERE/source)
            for name,value in info['dependencies_sha256'].items():assert value==sha(HERE/name)
            cmd=terminal['command'];seed=Path(cmd[cmd.index('--seed')+1])
            assert info['seed_sha256']==sha(seed)
            assert json.loads(seed.read_text())['prefix']==prefix
            key=(n,tuple(tuple(map(tuple,L)) for L in prefix))
            if key not in cache:cache[key]=sorted(prefix_images(n,prefix))
            universe=cache[key];assert len(universe)==info['inputs']
            free=info['depth']-len(prefix)-2;assert free>=0
            model=ProbeModel(n,free+2,universe,phi=info['normal'],nored0=False)
            if '--witness' in cmd:
                network=json.loads(Path(cmd[cmd.index('--witness')+1]).read_text())['layers']
                assert len(network)==info['depth'] and network[:len(prefix)]==prefix and verify_all(n,network)
                for t,layer in enumerate(network[len(prefix):]):
                    selected=set(map(tuple,layer));assert selected<=set(model.g[t])
                    for e,v in model.g[t].items():model.add([v if e in selected else -v])
                assert info['all_binary_inputs_verified'] and verify_all(n,info['layers'])
                if n==18 and known_dp is None:
                    xs=sorted({apply_layers(network[len(prefix):-2],x) for x in universe})
                    arrays=[tuple(bool(x&(1<<c)) for c in range(n)) for x in xs]
                    pair,stats=ending(profiles(arrays));assert pair is not None
                    assert all(apply_layers(pair,x)==netsat.sorted_mask(n,x.bit_count()) for x in xs)
                    known_dp=dict(n=18,cut=info['depth']-2,cut_image_size=len(xs),ending=pair,stats=stats)
            states={x:model.simulate_to_cut(x,free) for x in universe}
            if variant=='normal':
                old=model.ncl
                if info['normal']:
                    for x,state in states.items():model._pen_units(state,0,n-1,n-x.bit_count())
                assert model.ncl-old==info['penultimate_units']
            before=model.nv;clause_begin=model.ncl
            assert add_data_ending(model,states)==info['data_ending']
            assert model.nv==before==info['variables'] and model.ncl==info['clauses']
            directory=Path(info['certificate_directory'])
            assert digest(model.nv,model.S.clauses)==info['cnf_sha256']==sha(directory/'problem.cnf')
            row=dict(variant=variant,label=label,whole_cnf_reconstructed=True,
                     data_clause_range=[clause_begin,model.ncl],cnf_sha256=info['cnf_sha256'],
                     data_added_variables=model.nv-before)
            if label.startswith('beam'):
                assert terminal['terminal']=='TIMEOUT_KILLED' and info['status']=='BUILT'
                row['status']='TIMEOUT_NOT_UNSAT'
            else:
                assert terminal['terminal']=='EXITED' and terminal['returncode']==0
                if 'proof_sha256' in info:
                    assert sha(directory/'proof.drat')==info['proof_sha256']
                    check=json.loads((directory/'check-terminal.json').read_text())
                    assert check['terminal']=='EXITED' and check['returncode']==0 and check['verified']
                    assert 's VERIFIED' in (directory/'check.log').read_text()
                    row.update(status='CHECKED_UNSAT',proof_sha256=info['proof_sha256'],check_log_sha256=sha(directory/'check.log'))
                else:row['status']='FULL_SORTER_POSITIVE_CONTROL'
            audits.append(row)
    report=dict(status='REVIEWED_SOUND',uses_sat=False,new_solver_calls=0,substantive_issues=[],
        exact_formula_review=[
            'For each k-zero state, all pre-final bits away from k-1,k are forced to their sorted values. Without the final boundary edge the two middle bits are forced too; with it, weight conservation supplies complementary middle bits.',
            'Positive incident-P gates correctly guard the idle requirement; -g correctly guards each active comparator. Matching constraints ensure a unique active output mode.',
            'Minimum requiring one and maximum requiring zero each split into two guarded clauses. The other minimum/maximum requirements use the correct two-literal disjunction.',
            'The final edge appears only in the two boundary-wire requirements. Other final edges connect equally forced bits and cannot spoil sorting.',
            'Skipping zero- and full-weight states is sound because the preceding exact simulation preserves their all-equal values.',
            'The helper is exact for arbitrary P and adjacent S, and introduces no output or cardinal variables. The worker uses the full prefix image, simulates every free cut layer, and directly verifies every SAT sorter on all binary inputs.'
        ],
        normal_units_review='The normal fork only adds existing cut units under --normal. Span<=3 makes a one at c<=k-5 unable to reach rank k; at c=k-4 the only potential span-three gate forces the last edge back toward k-2 by phi3, so it still cannot reach k. The zero bound c>=k+3 is symmetric.',
        separator_note_review=[
            'A separated boundary is persistent: values on its left are always below those on its right, making every future cross-boundary comparison redundant.',
            'If all exact Q on a consecutive block stay inside it, rank conservation and outside rank intervals containing their own indices separate both boundaries.',
            'After deleting cross-block comparisons, an odd block has a first-layer idle; its forward cone in d remaining layers has size at most 2^(d-1). Hence some wire must have at most that many attainable ranks.',
            'The conditional no-cross-S clauses have the correct polarity and remain necessary with enclosing intervals wholly on one side of the separator.',
            'If R and S respect a separator, a crossing P edge contributes only an outside S-block to either endpoint cone, so each endpoint demand already fits its own S-block. Deleting the P edge preserves reachability; capacity plus no-cross-S therefore rejects a full triple.'
        ],
        unchanged_truth_checker_replay=replay,artifact_audits=audits,
        independent_fixed_cut_dp_on_known_eighteen_sorter=known_dp,
        no_new_D18_exclusion=True,
        reviewed_sha256={s:sha(HERE/s) for s in ['two_layer_data_ending.py','two_layer_data_ending_verify.py','prefix_data_ending_round9.py','prefix_data_normal_round9.py','rank-separated-blocks.md','d13_feedback_round9_data_ending.md','d13_feedback_round9_data_dp.py']},
        source_sha256=sha(Path(__file__)),seconds=time.monotonic()-started,running_jobs=[])
    (HERE/'results/d13-feedback-round9-data-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],truth_checks=sum(replay['counts'].values()),reconstructed_cnfs=len(audits),known18_dp_passed=known_dp is not None,seconds=report['seconds']),indent=2))


if __name__=='__main__':main()
