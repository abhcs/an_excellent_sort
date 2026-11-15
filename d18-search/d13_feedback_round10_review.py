#!/usr/bin/env python3
"""Independent no-SAT review of the mode-path and mandatory-matching CNFs."""
from collections import deque
import hashlib,itertools,json,random,time
from pathlib import Path
import netsat
from netsat import prefix_images,verify_all
from probe_frontier import ProbeModel
from two_layer_mode_path import add_mode_path_ending
from two_layer_matching_ending import add_matching_ending
from d13_feedback_round8_capacity_review import Recorder as BuildRecorder,digest
from d13_feedback_round10_matching_verify import matchings,run,sorts

HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


class FixedRecorder:
    def __init__(self,n,matching=False):
        self.n=n;self.nv=self.ncl=0;self.clauses=[]
        if matching:
            pen={e:self.new_var() for e in itertools.combinations(range(n),2)};self.g=[pen,{}]
            for c in range(n):
                for u,v in itertools.combinations([v for e,v in pen.items() if c in e],2):self.add([-u,-v])
    def new_var(self):self.nv+=1;return self.nv
    def add(self,c):self.clauses.append(list(c));self.ncl+=1


def dual_horn(clauses,fixed=None):
    """Exact greatest-model evaluation of clauses with at most one negative literal."""
    fixed=fixed or {};reduced=[]
    for clause in clauses:
        if any(abs(v) in fixed and fixed[abs(v)]==(v>0) for v in clause):continue
        c=[v for v in clause if abs(v) not in fixed]
        assert sum(v<0 for v in c)<=1
        reduced.append(c)
    remaining=[];negative=[];uses={};queue=deque();false=set()
    def force(v):
        if v not in false:false.add(v);queue.append(v)
    for j,c in enumerate(reduced):
        positive=[v for v in c if v>0];neg=[-v for v in c if v<0]
        remaining.append(len(positive));negative.append(neg[0] if neg else None)
        for v in positive:uses.setdefault(v,[]).append(j)
        if not positive:
            if not neg:return False
            force(neg[0])
    while queue:
        for j in uses.get(queue.popleft(),[]):
            remaining[j]-=1
            if remaining[j]==0:
                if negative[j] is None:return False
                force(negative[j])
    return True


def main():
    start=time.monotonic();rng=random.Random(1102026);control=[];path_total=matching_total=0
    for n in range(2,7):
        ms=list(matchings(list(range(n))));ss=[s for s in ms if all(b==a+1 for a,b in s)]
        families=[]
        for _ in range(20):
            prefix=[rng.choice(ms) for _ in range(rng.randrange(7))]
            families.append(sorted({run(n,x,prefix) for x in range(1<<n)}))
        families += [sorted(rng.sample(range(1<<n),rng.randrange(1,1<<n))) for _ in range(10)]
        families.append([])
        for xs in families:
            states={x:{c:bool(x&(1<<c)) for c in range(n)} for x in xs}
            direct={p:(all(b-a<=3 for a,b in p) and any(sorts(n,xs,p,s) for s in ss)) for p in ms}
            path=FixedRecorder(n);add_mode_path_ending(path,states)
            assert dual_horn(path.clauses)==any(direct.values());path_total+=1
            graph=FixedRecorder(n,matching=True);add_matching_ending(graph,states)
            for p in ms:
                selected=set(p);fixed={v:e in selected for e,v in graph.g[0].items()}
                assert dual_horn(graph.clauses,fixed)==direct[p],(n,xs,p)
                matching_total+=1
        control.append(dict(n=n,families=len(families),fixed_P_matchings=len(ms)))

    netsat.Solver=BuildRecorder;artifacts=[];cache={}
    for variant,helper in [('mode-path',add_mode_path_ending),('matching-ending',add_matching_ending)]:
        rows=json.loads((HERE/f'results/{variant}-round10-batch.json').read_text())
        for terminal in rows:
            label=terminal['label'];info=json.loads((HERE/f'results/{variant}-round10-{label}.json').read_text())
            source='prefix_mode_path_round10.py' if variant=='mode-path' else 'prefix_matching_ending_round10.py'
            assert info['source_sha256']==sha(HERE/source)
            for name,value in info['dependencies_sha256'].items():assert value==sha(HERE/name)
            cmd=terminal['command'];seed=Path(cmd[cmd.index('--seed')+1]);assert sha(seed)==info['seed_sha256']
            n=info['n'];prefix=info['prefix'];assert json.loads(seed.read_text())['prefix']==prefix
            key=n,tuple(tuple(map(tuple,L)) for L in prefix)
            if key not in cache:cache[key]=sorted(prefix_images(n,prefix))
            universe=cache[key];assert len(universe)==info['inputs']
            free=info['depth']-len(prefix)-2;assert free>=0
            model=ProbeModel(n,free+2,universe,phi=False,nored0=False)
            unused=free if variant=='mode-path' else free+1
            for layer in model.g[unused:]:
                for v in layer.values():model.add([-v])
            if '--witness' in cmd:
                net=json.loads(Path(cmd[cmd.index('--witness')+1]).read_text())['layers']
                assert len(net)==info['depth'] and net[:len(prefix)]==prefix and verify_all(n,net)
                for t,layer in enumerate(net[len(prefix):info['depth']-2]):
                    selected=set(map(tuple,layer));assert selected<=set(model.g[t])
                    for e,v in model.g[t].items():model.add([v if e in selected else -v])
            states={x:model.simulate_to_cut(x,free) for x in universe}
            begin=model.ncl
            assert helper(model,states)==info['mode_path' if variant=='mode-path' else 'matching_ending']
            assert model.nv==info['variables'] and model.ncl==info['clauses']
            folder=Path(info['certificate_directory'])
            assert digest(model.nv,model.S.clauses)==info['cnf_sha256']==sha(folder/'problem.cnf')
            audit=dict(variant=variant,label=label,complete_cnf_reconstructed=True,helper_clause_range=[begin,model.ncl],cnf_sha256=info['cnf_sha256'])
            if terminal['terminal']=='TIMEOUT_KILLED':
                assert info['status']=='BUILT';audit['status']='TIMEOUT_NOT_UNSAT'
            else:
                assert terminal['terminal']=='EXITED' and terminal['returncode']==0
                if 'proof_sha256' in info:
                    assert sha(folder/'proof.drat')==info['proof_sha256']
                    check=json.loads((folder/'check-terminal.json').read_text())
                    assert check['terminal']=='EXITED' and check['returncode']==0 and check['verified']
                    assert 's VERIFIED' in (folder/'check.log').read_text()
                    audit.update(status='CHECKED_UNSAT',proof_sha256=info['proof_sha256'])
                else:
                    assert info['status']=='SORTER' and info['all_binary_inputs_verified'] and verify_all(n,info['layers'])
                    audit['status']='FULL_SORTER_POSITIVE_CONTROL'
            artifacts.append(audit)
    proof='d13_feedback_round10_matching.md'
    report=dict(status='REVIEWED_SOUND',uses_sat=False,new_solver_calls=0,substantive_issues=[],
        source_review=[
            'B, Lgood, and Rgood guard implications have the correct min/max/idle polarities and weight thresholds. Positive use only is sufficient: false invalid predicates cannot be selected, while every valid predicate may be true.',
            'In the path helper, terminal reachability implies an incoming true transition, which implies predecessor reachability and all required guards. Following these choices backwards through strictly decreasing boundaries yields one consistent complete path. Transition-to-target implications are unnecessary.',
            'The relative crossing-P pattern enforces matching consistency, and the pending S bit enforces final adjacency/matching. Duplicate reach states may safely merge because all processed-wire tests are discharged.',
            'In the matching helper, every chosen P mode forces B and Lgood OR Rgood. Long P gates are explicitly false; inactive modes need no predicate. The shared P matching conserves every cut-state weight, so the exact matching theorem supplies the omitted S.',
            'The path worker disables both placeholder ending layers. The matching worker disables only the unused S layer and retains the actual P matching variables. Both disable redundant-edge tracking and penultimate phi constraints, so unused tail choices do not constrain earlier simulated layers.',
            'Known-witness controls fix only layers before the cut. SAT reconstruction independently finds an ending and verifies the full network on all binary inputs.',
            'Span-three completeness is invoked only for actual complete prefix images. On arbitrary fixed families the helper claims only bounded-span exactness; the long-edge counterexample remains valid.'
        ],
        independent_no_sat_fixed_family_checks=control,path_formula_checks=path_total,matching_formula_fixed_P_checks=matching_total,
        fixed_formula_method='Dual-Horn greatest-model propagation after fixing P, compared with direct sorting by all adjacent S; no SAT package solve method called.',
        artifact_audits=artifacts,new_complete_cover_exclusions=0,
        reviewed_sha256={name:sha(HERE/name) for name in ['two_layer_mode_path.py','two_layer_mode_path_verify.py','prefix_mode_path_round10.py','two_layer_matching_ending.py','two_layer_matching_ending_verify.py','prefix_matching_ending_round10.py',proof]},
        source_sha256=sha(Path(__file__)),seconds=time.monotonic()-start,running_jobs=[])
    (HERE/'results/d13-feedback-round10-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],path_checks=path_total,fixed_P_checks=matching_total,reconstructed_cnfs=len(artifacts),seconds=report['seconds']),indent=2))


if __name__=='__main__':main()
