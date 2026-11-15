#!/usr/bin/env python3
"""Check the threshold-partner compression, independently of its builder."""
import hashlib
import itertools
import json
from pathlib import Path

ROOT=Path(__file__).parents[1]
FIRST=((0,1),(2,3),(4,5));SECOND=((0,2),(1,4),(5,6))


def run(prefix,values):
    out=list(values)
    for layer in prefix:
        for a,b in layer:
            if out[a]>out[b]:out[a],out[b]=out[b],out[a]
    return out


def candidates(outputs,p,c):
    n=len(outputs[0]);lo=min(x[p] for x in outputs);hi=max(x[p] for x in outputs)
    keep=set(range(n))-{p}
    for x in outputs:
        if x[p]<=hi-c:keep&={q for q in range(n) if x[q]>=hi-c+1}
        if x[p]>=lo+c:keep&={q for q in range(n) if x[q]<=lo+c-1}
    return keep


def endpoints(row,outputs):
    p=row['pivot'];assert row['low']==min(x[p] for x in outputs) and row['high']==max(x[p] for x in outputs)
    assert outputs[row['low_input']][p]==row['low'] and outputs[row['high_input']][p]==row['high']


def guard(g,p,lo,hi,outputs,c):
    x=outputs[g['input']]
    if g['kind']=='low':
        assert x[p]<=hi-c
        expected={q for q in range(len(x)) if q!=p and x[q]<=hi-c}
    else:
        assert g['kind']=='high' and x[p]>=lo+c
        expected={q for q in range(len(x)) if q!=p and x[q]>=lo+c}
    assert set(g['excluded'])==expected
    return expected


def endpoint_text(r):return f"{chr(65+r['low_input'])}:{r['low']}–{chr(65+r['high_input'])}:{r['high']}"
def guard_text(r):return f"{chr(65+r['input'])} {'lo' if r['kind']=='low' else 'hi'}:{''.join(map(str,r['excluded']))}"


def equivalence(outputs,c):
    n=len(outputs[0]);allowed=[candidates(outputs,p,c) for p in range(n)];pairs=0
    for a,b in itertools.combinations(range(n),2):
        minimum=[min(x[a],x[b]) for x in outputs];maximum=[max(x[a],x[b]) for x in outputs]
        direct=max(minimum)-min(minimum)<c and max(maximum)-min(maximum)<c
        assert ((b in allowed[a] and a in allowed[b])==direct)
        pairs+=1
    return pairs


def controls():
    specs=[(2,(),((0,1),),()),
           (3,(((0,1),),),((1,2),),(((0,1),),)),
           (3,(((0,1),),),((0,2),),(((1,2),),)),
           (4,(((0,1),(2,3)),),((0,2),(1,3)),(((1,2),),))]
    checked=0
    for n,prefix,q,suffix in specs:
        inputs=list(itertools.permutations(range(n)));whole=prefix+(q,)+suffix
        assert all(run(whole,x)==list(range(n)) for x in inputs)
        outputs=[run(prefix,x) for x in inputs];c=2**len(suffix)
        allowed=[candidates(outputs,p,c) for p in range(n)]
        mandatory={p for p in range(n) if max(x[p] for x in outputs)-min(x[p] for x in outputs)>=c}
        assert mandatory<={v for edge in q for v in edge}
        assert all(b in allowed[a] and a in allowed[b] for a,b in q)
        equivalence(outputs,c);checked+=len(inputs)
    return dict(sorters=len(specs),permutation_runs=checked)


def main():
    original=ROOT/'results/h9-feedback-round5-certificate.json'
    source=ROOT/'results/h9-feedback-round5-partner-certificate.json'
    note=ROOT/'h9_feedback_round5_rank_partner.md'
    fixed=json.loads(original.read_text());data=json.loads(source.read_text());text=note.read_text()
    original_hash=hashlib.sha256(original.read_bytes()).hexdigest()
    assert original_hash==data['original_certificate_sha256']=='401ef85aadeb797511deaa7d0bf4e4c20a6ffde1c83553fa2ae65c577e14d722'
    forms={(r['case'],r['number']):r for r in fixed['rank_cases']};seen=set();c=data['capacity'];assert c==4
    pair_checks=0;own_guards=0;reciprocal_guards=0;direct=0;reciprocal_forms=[]
    for row in data['records']:
        key=(row['case'],row['number']);assert key in forms and key not in seen;seen.add(key)
        form=forms[key];outputs=[run((FIRST,SECOND,form['third'],form['fourth']),x) for x in fixed['rank_inputs']]
        endpoints(row,outputs);p=row['pivot'];assert row['high']-row['low']>=c
        excluded=set()
        for g in row['guards']:excluded|=guard(g,p,row['low'],row['high'],outputs,c);own_guards+=1
        remaining=set(range(9))-{p}-excluded
        assert remaining==set(row['remaining'])==candidates(outputs,p,c)
        assert {r['pivot'] for r in row['reciprocal']}==remaining
        for reciprocal in row['reciprocal']:
            endpoints(reciprocal,outputs)
            assert p in guard(reciprocal['guard'],reciprocal['pivot'],reciprocal['low'],reciprocal['high'],outputs,c)
            line=f"| {key[0]}.{key[1]} | {p} | {reciprocal['pivot']} | {endpoint_text(reciprocal)} | {guard_text(reciprocal['guard'])} |"
            assert line in text;reciprocal_guards+=1
        assert not any(p in candidates(outputs,q,c) for q in remaining)
        guards_cell='; '.join(guard_text(g) for g in row['guards']);remainder=''.join(map(str,row['remaining'])) or 'empty'
        assert f"| {key[0]}.{key[1]} | {p} | {endpoint_text(row)} | {guards_cell} | {remainder} |" in text
        pair_checks+=equivalence(outputs,c)
        if remaining:reciprocal_forms.append(key)
        else:direct+=1
    assert seen==set(forms) and len(seen)==47 and direct==44 and reciprocal_forms==[(4,1),(5,5),(5,6)]
    positive=controls()
    report=dict(status='VERIFIED',solver_free=True,matching_enumeration=False,rank_inputs=15,prefix_runs=705,
                direct_intersections=direct,reciprocal_forms=reciprocal_forms,own_guards=own_guards,
                reciprocal_guards=reciprocal_guards,exact_pair_equivalence_checks=pair_checks,positive_controls=positive,
                original_certificate_sha256=original_hash,certificate_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                note_sha256=hashlib.sha256(note.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (ROOT/'results/h9-feedback-round5-partner-proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
