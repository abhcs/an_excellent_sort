#!/usr/bin/env python3
"""Check fixed31 endpoint certificates; no SAT, discovery, or nine-wire matching scan."""
import hashlib
import itertools
import json
import time
from pathlib import Path

ROOT=Path(__file__).parents[1]
FIRST=((0,1),(2,3),(4,5));SECOND=((0,2),(1,5),(3,6))
CERTIFICATE_SHA256='297a617997cc977dcf284a76b504ef6fda71c83359750d9450470d0be3cb9065'

def run(prefix,values):
    x=list(values)
    for layer in prefix:
        for a,b in layer:
            x[a],x[b]=min(x[a],x[b]),max(x[a],x[b])
    return x

def endpoint(record,outputs):
    p=record['pivot']
    assert record['low']==min(x[p] for x in outputs)
    assert record['high']==max(x[p] for x in outputs)
    assert outputs[record['low_input']][p]==record['low']
    assert outputs[record['high_input']][p]==record['high']

def guard(g,p,low,high,outputs):
    row=outputs[g['input']]
    if g['kind']=='low':
        assert row[p]<=high-4
        excluded={q for q in range(9) if q!=p and row[q]<=high-4}
    else:
        assert g['kind']=='high' and row[p]>=low+4
        excluded={q for q in range(9) if q!=p and row[q]>=low+4}
    assert excluded==set(g['excluded'])
    return excluded

def edge_text(edges):return ' '.join(''.join(map(str,e)) for e in edges) or 'none'
def ep(r):return f"{chr(65+r['low_input'])}:{r['low']}–{chr(65+r['high_input'])}:{r['high']}"
def gs(g):return f"{chr(65+g['input'])} {'lo' if g['kind']=='low' else 'hi'}:{''.join(map(str,g['excluded'])) or 'none'}"

def main():
    start=time.monotonic();path=ROOT/'results/h9-recovery-021536-endings-certificate.json'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==CERTIFICATE_SHA256
    data=json.loads(path.read_text());table=(ROOT/'h9_recovery_021536_endings.md').read_text()
    assert data['first']==[list(e) for e in FIRST] and data['second']==[list(e) for e in SECOND]
    inputs=data['rank_inputs'];assert len(inputs)==16 and len(set(map(tuple,inputs)))==16
    for i,x in enumerate(inputs):
        assert sorted(x)==list(range(9))
        assert f"| {chr(65+i)} | `{''.join(map(str,x))}` |" in table
    expected={1:6,5:18,8:2,9:2,14:1,16:2};seen=set();own=reciprocal=parity_count=0
    kinds={};mandatory_rows=0
    for r in data['records']:
        key=(r['case'],r['number']);assert key not in seen;seen.add(key)
        assert r['case'] in expected and 1<=r['number']<=expected[r['case']]
        prefix=(FIRST,SECOND,r['third'],r['fourth'])
        for layer in prefix:
            assert all(0<=a<b<9 for a,b in layer)
            assert len({v for e in layer for v in e})==2*len(layer)
        outputs=[run(prefix,x) for x in inputs];forbidden=set()
        par=r['parity']
        if par:
            a,b=par['edge'];assert 0<=a<b<9
            intervals=[]
            assert [item['output'] for item in par['ranges']]==['min','max']
            for item,func in zip(par['ranges'],(min,max)):
                vals=[func(x[a],x[b]) for x in outputs]
                assert vals[item['low_input']]==item['low']==min(vals)
                assert vals[item['high_input']]==item['high']==max(vals)
                assert item['high']-item['low']==3
                intervals.append(set(range(item['low'],item['high']+1)))
            overlap=intervals[0]&intervals[1]
            assert len(overlap)%2==1 and sorted(overlap)==par['odd_intersection']
            forbidden.add((a,b));parity_count+=1
            assert f"| {key[0]}.{key[1]} | `{a}{b}` | {ep(par['ranges'][0])} | {ep(par['ranges'][1])} | {''.join(map(str,sorted(overlap)))} |" in table
        remaining_sets=[];pivots=[]
        for p in r['pivots']:
            v=p['pivot'];assert v not in pivots;pivots.append(v);mandatory_rows+=1
            endpoint(p,outputs);assert p['high']-p['low']>=4
            excluded=set()
            for g in p['guards']:
                excluded|=guard(g,v,p['low'],p['high'],outputs);own+=1
            remaining=set(range(9))-{v}-excluded;assert sorted(remaining)==p['remaining']
            reciprocal_pivots=[]
            for q in p['reciprocal']:
                w=q['pivot'];assert w in remaining and w not in reciprocal_pivots;reciprocal_pivots.append(w)
                endpoint(q,outputs)
                assert v in guard(q['guard'],w,q['low'],q['high'],outputs);reciprocal+=1
                assert f"| {key[0]}.{key[1]} | {v} | {w} | {ep(q)} | {gs(q['guard'])} |" in table
            remaining-=set(reciprocal_pivots);assert sorted(remaining)==p['allowed_before_parity']
            remaining={w for w in remaining if tuple(sorted((v,w))) not in forbidden}
            assert sorted(remaining)==p['allowed_after_parity'];remaining_sets.append(remaining)
            assert f"| {key[0]}.{key[1]} | {v} | {ep(p)} | {'; '.join(gs(g) for g in p['guards'])} | {''.join(map(str,p['remaining'])) or 'empty'} | {''.join(map(str,p['allowed_before_parity'])) or 'empty'} |" in table
        if len(pivots)==1:
            assert not remaining_sets[0]
            assert r['kind']==('isolated_with_parity' if par else 'isolated')
        else:
            neighbors=set().union(*remaining_sets)
            assert not neighbors&set(pivots) and len(neighbors)<len(pivots)
            assert r['kind']=='hall_with_parity' and par
        kinds[r['kind']]=kinds.get(r['kind'],0)+1
        assert f"| {key[0]}.{key[1]} | `{edge_text(r['third'])}` | `{edge_text(r['fourth'])}` |" in table
    assert seen=={(c,j) for c,count in expected.items() for j in range(1,count+1)}
    assert kinds=={'isolated':26,'hall_with_parity':1,'isolated_with_parity':4}
    result=dict(status='VERIFIED',scope='31 listed fourth-layer prefixes only; coverage must be proved independently.',
                fixed_inputs=16,prefixes=31,input_runs=16*31,mandatory_pivot_rows=mandatory_rows,
                own_guards=own,reciprocal_guards=reciprocal,saturated_cone_parity_exclusions=parity_count,
                conclusions=kinds,uses_sat=False,global_matching_scan=False,
                certificate_sha256=CERTIFICATE_SHA256,
                checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                proof_note_sha256=hashlib.sha256((ROOT/'h9_recovery_021536_endings.md').read_bytes()).hexdigest(),
                seconds=time.monotonic()-start)
    (ROOT/'results/h9-recovery-021536-endings-check.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
