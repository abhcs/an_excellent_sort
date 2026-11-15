#!/usr/bin/env python3
"""Local image checks, independent model replay, and checked-CNF bindings."""
from collections import Counter
import gzip
import hashlib
import importlib.util
from itertools import permutations
import json
from pathlib import Path
import sys
import tempfile
import time
from d17_feedback_round9_check import states_of,apply,legal

ROOT=Path(__file__).parent


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def image(layers,n):
    out=set()
    for x in permutations(range(n)):
        for L in layers:x=apply(x,L)
        out.add(tuple(x))
    return out


def perfect(xs):
    if not xs:yield ();return
    a,*rest=xs
    for j,b in enumerate(rest):
        for P in perfect(rest[:j]+rest[j+1:]):yield ((a,b),)+P


def local_images():
    C=image((((0,1),),((0,2),(1,3))),4)
    D=image((((0,1),(2,3)),((1,2),)),4)
    P={x for x in permutations(range(4)) if x[0]<x[2] and x[0]<x[3] and x[1]<x[3]}
    assert C==P and {(x[1],x[0],x[3],x[2]) for x in D}==P and len(P)==5
    hand=image((((0,1),(2,3)),((0,3),)),4)
    assert {(x[0],x[2],x[1],x[3]) for x in hand}==P
    counts=Counter()
    for idle in range(9):
        for N in perfect([v for v in range(9) if v!=idle]):
            free=[e for e in N if not(set(e)&set(range(4)))]
            if free:counts['commuting']+=1
            else:
                counts['two_N4_components']+=1
                assert all(len(set(e)&set(range(4)))==1 for e in N)
                partner={a:b for e in N for a,b in (e,e[::-1])}
                parts=[{a,b,partner[a],partner[b]} for a,b in ((0,1),(2,3))]
                assert all(len(p)==4 for p in parts) and not(parts[0]&parts[1])
            assert sum(not(set(e)&{0,1}) for e in N)>=2
    assert counts=={'commuting':825,'two_N4_components':120}
    return dict(N4_order_types=5,second_four_gate_matchings=945,classification=dict(counts),
                hand_case_note_sha256=sha(ROOT.parent/'depth-hand-proofs/h9_feedback_commute.md'),
                hand_case_audit_sha256=sha(ROOT.parent/'depth-hand-proofs/results/h9-feedback-commute-proof.json'))


def rebuild(source,case):
    spec=importlib.util.spec_from_file_location(f'round10_build_{source.stem}_{case}',source)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    captured={}
    class StopBuild(Exception):pass
    class NoSolver:
        def __init__(self,**kwargs):captured['clauses']=kwargs['bootstrap_with'];raise StopBuild
    module.Solver=NoSolver;old=sys.argv
    try:
        with tempfile.TemporaryDirectory(prefix='d17-round10-build-') as temp:
            out=Path(temp)/'result.json';sys.argv=[str(source),'--case',str(case),'--out',str(out)]
            try:module.main()
            except StopBuild:pass
            else:raise AssertionError('Solver was not intercepted')
            result=json.loads(out.read_text())
    finally:sys.argv=old
    clauses=captured['clauses']
    raw=(f'p cnf {result["variables"]} {len(clauses)}\n'+''.join(' '.join(map(str,c))+' 0\n' for c in clauses)).encode()
    return result['variables'],len(clauses),hashlib.sha256(raw).hexdigest()


def main():
    start=time.monotonic();local=local_images()
    coverpath=ROOT/'prefixes/complete17.jsonl';cover=[json.loads(s) for s in coverpath.read_text().splitlines()]
    repaired=json.loads((ROOT/'results/d17-feedback-round10-repair.json').read_text())['records']
    records={r['case']:r for r in repaired}
    for i in (476,477,478):
        saved=json.loads((ROOT/f'results/d17-feedback-round10-case{i}/result.json').read_text())
        assert saved['status']=='SURVIVOR';M,N=saved['next_layers'];records[i]=dict(case=i,M=M,N=N)
    assert set(records)==set(range(606))
    failures=[];total=0;first_min_hist=Counter();models=[]
    for i,r in sorted(records.items()):
        states=states_of(cover[i]);M,N=r['M'],r['N'];assert legal(M) and legal(N)
        assert not(set(map(tuple,M))&set(map(tuple,N)))
        assert not(set(map(tuple,M))&set(map(tuple,cover[i]['layers'][1])))
        profiles=[]
        for s in states:
            a=sum(s[u]==s[v]==0 for u,v in M);after=apply(s,M)
            b=sum(after[u]==after[v]==0 for u,v in N)
            assert min(a,b)>=1 and max(a,b)==4;profiles.append([a,b]);total+=1
        first=min(p[0] for p in profiles);first_min_hist[first]+=1
        if first<3:failures.append(i)
        models.append(dict(case=i,M=M,N=N,profiles=profiles))
    witness=ROOT/'results/d17-feedback-round10-oldprofile606.json.gz'
    witness.write_bytes(gzip.compress((json.dumps(dict(cover_sha256=sha(coverpath),cases=models),separators=(',',':'))+'\n').encode(),mtime=0))

    bindings=[];newsource=ROOT/'d17_feedback_round10_profile.py'
    for i in (604,605):
        oldnv,oldnc,_=rebuild(ROOT/'d17_feedback_defects.py',i)
        nv,nc,digest=rebuild(newsource,i);assert nv-oldnv==1584 and nc-oldnc==2672
        cert=ROOT/f'results/d17-feedback-round10-first3-case{i}/result'
        manifest=json.loads((cert/'check/certificate.json').read_text())
        assert manifest['independently_proof_checked'] and manifest['returncode']==0
        assert manifest['cnf_sha256']==digest==sha(cert/'problem.cnf')
        assert manifest['proof_sha256']==sha(cert/'proof.drat') and manifest['encoder_sha256']==sha(newsource)
        assert manifest['checker_sha256']==sha(Path('/private/tmp/d18-structural-drat-trim/drat-trim'))
        assert 'VERIFIED' in (cert/'check/check.log').read_text()
        bindings.append(dict(case=i,variables=nv,clauses=nc,variable_delta=nv-oldnv,clause_delta=nc-oldnc,
                             rebuilt_cnf_sha256=digest,proof_sha256=manifest['proof_sha256']))
    strengthened={r['case']:r for r in models if min(p[0] for p in r['profiles'])>=3}
    for i in (476,477,478,587,600):
        saved=json.loads((ROOT/f'results/d17-feedback-round10-first3-case{i}/result.json').read_text())
        assert saved['status']=='SURVIVOR';M,N=saved['next_layers']
        assert legal(M) and legal(N) and not(set(map(tuple,M))&set(map(tuple,N)))
        assert not(set(map(tuple,M))&set(map(tuple,cover[i]['layers'][1])))
        profiles=[]
        for s in states_of(cover[i]):
            after=apply(s,M);a=sum(s[u]==s[v]==0 for u,v in M);b=sum(after[u]==after[v]==0 for u,v in N)
            assert a>=3 and b>=1 and max(a,b)==4
            profiles.append([a,b])
        strengthened[i]=dict(case=i,M=M,N=N,profiles=profiles)
    assert set(strengthened)==set(range(604))
    newwitness=ROOT/'results/d17-feedback-round10-first3-all604.json.gz'
    newwitness.write_bytes(gzip.compress((json.dumps(dict(cover_sha256=sha(coverpath),cases=[strengthened[i] for i in sorted(strengthened)]),separators=(',',':'))+'\n').encode(),mtime=0))
    report=dict(status='VERIFIED',new_sat_or_drat_runs=False,local_image_checks=local,
                old_profile_cases=606,old_profile_restrictions=total,old_profile_witness_sha256=sha(witness),
                old_models_first_minimum_histogram=dict(first_min_hist),old_models_failing_new_first3=failures,
                new_checked_UNSAT_bindings=bindings,new_first3_positive_controls=[476,477,478,587,600],
                new_first3_positive_cases=len(strengthened),new_first3_positive_restrictions=sum(len(r['profiles']) for r in strengthened.values()),
                new_first3_witness_sha256=sha(newwitness),
                full_H9_dependency_explicit=True,checker_sha256=sha(Path(__file__)),seconds=round(time.monotonic()-start,4))
    (ROOT/'results/d17-feedback-round10-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
