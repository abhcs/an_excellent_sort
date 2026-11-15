#!/usr/bin/env python3
"""Independent mathematical/data audit and read-only replay of the round8 checker."""
from collections import Counter
import contextlib
import gzip
import hashlib
import importlib.util
import io
import itertools
import json
from pathlib import Path
import tempfile
import time

HERE=Path(__file__).resolve().parent


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    start=time.monotonic()
    labels=['D','A','B','C','E','d','a','b','c','q','e','r','x','y']
    pos={s:i for i,s in enumerate(labels)}
    arows=('AB','BC','CE','BD');bcols=('qab','qbc','qce','rce','qbd')
    minus=set('ABabq')
    family=[]
    for a,b in itertools.product(arows,bcols):
        sent=set(a+b)
        family.append([(-1 if v in minus else 1) if v in sent else 0 for v in labels[:12]])
    input_path=HERE/'results/d17-feedback-fourteen-hand606-states.json'
    assert family==[s[2:] for s in json.loads(input_path.read_text())['states']]
    residual=('D','d','a','r')
    def comparable(a,b):
        x=[s[pos[a]] for s in family] if a!='zero' else [0]*20
        y=[s[pos[b]] for s in family] if b!='zero' else [0]*20
        return all(u<=v for u,v in zip(x,y)) or all(u>=v for u,v in zip(x,y))
    antichains=[c for k in range(6) for c in itertools.combinations((*residual,'zero'),k)
                if all(not comparable(a,b) for a,b in itertools.combinations(c,2))]
    assert max(map(len,antichains))==3
    assert {frozenset(c) for c in antichains if len(c)==2}=={frozenset(c) for c in itertools.combinations(('D','d','r'),2)}
    assert [c for c in antichains if len(c)==3]==[('D','d','r')]

    # Independently verify every entry in both printed hand tables.
    rows=[
        (['Dd','ar'],[],[5,6,10,15],['E','d','a','q','e'],1),
        (['Da','dr'],[],[3,6,8,14],['C','E','q','e','r'],1),
        (['Dr','da'],[],[3,6,10,15],['E','d','q','e','r'],0),
        (['Dx','dy','ar'],[],[5,6,10,15],['E','a','q','e','x'],1),
        (['Dx','ry','da'],[],[5,6,10,15],['E','d','q','e','x'],1),
        (['dx','ry','Da'],[],[5,6,11,16],['C','E','a','q','e'],1),
        (['ar'],['D','d'],[0,1,3,7],['E','a','q','e','r'],1),
        (['da'],['D','r'],[0,1,3,7],['E','d','q','e','r'],1),
        (['Da'],['d','r'],[0,1,3,7],['A','E','q','e','r'],1)]
    sigrows={
        1:([7,8,13,11,2],[15,15,4]),2:([8,14,2,7,13],[11,15,5]),
        3:([6,12,10,3,9],[15,15,4,1]),4:([7,8,13,11,2],[15,15,4]),
        5:([7,8,13,11,2],[15,15,4]),6:([4,7,8,11,14],[1,15,15]),
        7:([8,1,11,14,4],[7,15,3,12]),8:([8,1,11,14,4],[7,15,3,12]),
        9:([7,8,11,14,4],[1,15,3,12])}
    spine={tuple(sorted((pos[a],pos[b]))) for a,b in ('Ab','Bq','CE','ce')}
    table=json.loads((HERE/'results/d17-feedback-round8-spine-witnesses.json').read_text())
    rowaudits=[]
    for j,(tails,idles,ids,chosen,parity) in enumerate(rows,1):
        n=14 if 4<=j<=6 else 12
        M=spine|{tuple(sorted((pos[a],pos[b]))) for a,b in tails}
        assert len({v for e in M for v in e})==2*len(M)
        assert set(range(n))-{v for e in M for v in e}=={pos[v] for v in idles}
        sets=[];rr=[]
        for i in ids:
            x=family[i]+[0]*(n-12)
            rr.append(sum(x[a]==x[b]==0 for a,b in M))
            for a,b in M:x[a],x[b]=min(x[a],x[b]),max(x[a],x[b])
            sets.append({v for v in range(n) if x[v]})
        assert all(len(s)==5 for s in sets)
        assert all(c<n//2-3 for c in rr)
        assert rr==([2,2,1,2] if j==7 else [3]*4 if n==14 else [2]*4)
        sig={v:sum((v in s)<<k for k,s in enumerate(sets)) for v in range(n)}
        selected={pos[v] for v in chosen}
        assert all(sig[v] and list(sig.values()).count(sig[v])==1 and sig[v].bit_count()%2==parity for v in selected)
        assert Counter(sig[v] for v in selected)==Counter(sigrows[j][0])
        assert Counter(sig[v] for v in range(n) if v not in selected and sig[v])==Counter(sigrows[j][1])
        rec=table['records'][j-1]
        assert n==rec['n'] and M==set(map(tuple,rec['M']))
        assert ids==rec['states'] and [sorted(s) for s in sets]==rec['sentinel_sets']
        assert {str(v):1 for v in selected}==rec['radii']
        rowaudits.append(dict(row=j,width=n,first_counts=rr,peak=n//2-3,
                             selected_signatures={labels[v]:format(sig[v],'04b') for v in selected},
                             same_parity=parity))

    # Verify the claimed link to the four former depth-two proof cases.
    old=json.loads(gzip.decompress((HERE/'results/d17-feedback-round7-core-certificate.json.gz').read_bytes()))
    def branch_depth(node):return 1+max(map(branch_depth,node['b'])) if 'b' in node else 0
    deep=[]
    for rec in old['cases']:
        if rec['r'] or branch_depth(rec['t'])<2:continue
        M={(v,int(x,16)) for v,x in enumerate(rec['m']) if v<int(x,16)}
        assert spine<=M
        deep.append(rec['m'])
    assert len(deep)==4

    # Replay the unchanged checker; only its reports go to a temporary directory.
    checker=HERE/'d17_feedback_round8_check.py'
    spec=importlib.util.spec_from_file_location('d17_round8_reviewed_checker',checker)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    inputs=['d17-feedback-fourteen-hand606-states.json','d17-feedback-round7-core-certificate.json.gz',
            'd17-feedback-round8-cut-certificate.json.gz','d17-feedback-round8-spine-witnesses.json']
    with tempfile.TemporaryDirectory(prefix='d17_hand_round8_review-') as tmp:
        root=Path(tmp);(root/'results').mkdir()
        for name in inputs:(root/'results'/name).symlink_to(HERE/'results'/name)
        mod.ROOT=root
        with contextlib.redirect_stdout(io.StringIO()):mod.main()
        replay={kind:json.loads((root/f'results/d17-feedback-round8-{kind}-check.json').read_text()) for kind in ('cut','spine')}
    for kind,value in replay.items():
        assert value==json.loads((HERE/f'results/d17-feedback-round8-{kind}-check.json').read_text())
        assert value['status']=='VERIFIED'

    sources=['d17_feedback_round8_cut_lemma.md','d17_feedback_round8_check.py',
             'd17_feedback_round7_reduction.md','d17_feedback_round5_reduction.md',
             'd17_feedback_round6_reduction.md','d17_feedback_round2_normalization.md']
    report=dict(status='REVIEWED_SOUND',uses_sat=False,substantive_gaps=[],
        mathematical_review=[
            'Completing a matching, with one zero-signature dummy if needed, cannot remove t internal edges of an odd (2t+1)-set. Such a set then has exactly one boundary edge.',
            'Summing signature distances over the perfect matching equals the number m of required states. The pair-radius inequalities bound that sum below by the total radius. The radius-versus-weight condition also covers any added zero-signature wire.',
            'The price formulation p=(frequency-radius)/2 is equivalent and works directly with partial matchings because all prices are nonnegative.',
            'Unique nonzero signatures give distance at least one from every unselected wire. Distinct selected signatures of common parity have distance at least two; five unit radii contradict four required states.',
            'With the four fixed spine gates, only D,d,a,r and common reals remain. Over ALL twenty states a<=0<=D,d,r; only the three positive pairs are incomparable. This is a full-family normalization, not a selected-four-state comparability claim.',
            'Comparable-idle augmentation preserves the spine and yields zero or two idles at even width. Two idles must be a positive pair. Deleting common-real pairs and contracting comparable external partners preserves the deficit and peak coverage, so only the nine printed forms remain.',
            'Perfect forms: three internal pairings, or three choices of an external positive pair. Two-idle forms: three positive idle pairs; the remaining comparable pair contracts internally. No bound on the original matching size or original number of common reals was assumed.',
            'For even width with five sentinels, a completed second matching reaches the RR peak exactly when it contains two SS edges. Odd-width padding adds one idle common real and leaves the required RR peak unchanged.',
            'Common physical relabeling only reorients first-layer gates and causes fixed output swaps absorbed into the second matching. No state-dependent permutation or individual-sign change is assumed.'
        ],
        residual_full_family_antichains=[list(c) for c in antichains if len(c)>=2],
        printed_table_audits=rowaudits,former_depth_two_cases=deep,
        unchanged_checker_replay=replay,
        finite_scope='The nine-form spine branch has a hand normalization and explicit nine-row arithmetic proof. Coverage of all 2,728 zero-full-row forms still uses the accepted round-seven finite set plus the new radius certificate. It is not a pure hand proof of the full case-606 family and does not change a D17 cover count.',
        reviewed_sha256={s:sha(HERE/s) for s in sources},
        input_sha256={s:sha(HERE/'results'/s) for s in inputs},
        source_sha256=sha(Path(__file__)),seconds=time.monotonic()-start,
        root_sources_and_reports_modified=False,running_jobs=[])
    (HERE/'results/d17-hand-round8-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],nine_hand_rows=len(rowaudits),compressed_cases=replay['cut']['cases'],former_depth_two_cases=len(deep),seconds=report['seconds']),indent=2))


if __name__=='__main__':main()
