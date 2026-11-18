#!/usr/bin/env python3
"""Fixed local-mode checker: eleven runs, no matching enumeration or SAT."""
import hashlib
import json
import time
from pathlib import Path

ROOT=Path(__file__).parents[1]
PREFIX=(((0,1),(2,3),(4,5)),((0,2),(1,5),(3,6)),((1,2),(3,4),(7,8)))
CERTIFICATE_SHA256='a79f54ef1e26d47b7e11679506d0c9bff2be8175e641b7c4c04d95df5a847808'

def run(values):
    x=list(values)
    for layer in PREFIX:
        for a,b in layer:x[a],x[b]=min(x[a],x[b]),max(x[a],x[b])
    return x

def evaluate(y,p,q,r,output):
    if q is None:
        assert r is None and output=='idle';return y[p]
    assert output in ('min','max')
    z=y[q]
    if r is not None:z=min(y[q],y[r]) if q<r else max(y[q],y[r])
    return min(y[p],z) if output=='min' else max(y[p],z)

def guard_text(g):
    a,b=g['inputs'];modes=','.join('I' if r is None else str(r) for r in g['modes'])
    return f"{chr(65+a)}–{chr(65+b)}/{g['output']} {{{modes}}}"

def main():
    start=time.monotonic();path=ROOT/'results/h9-recovery-021536-case2-certificate.json'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==CERTIFICATE_SHA256
    data=json.loads(path.read_text());assert data['prefix']==[[list(e)for e in layer]for layer in PREFIX]
    note=ROOT/'h9_recovery_021536_case2.md';text=note.read_text()
    inputs=data['rank_inputs'];assert len(inputs)==11 and len(set(map(tuple,inputs)))==11
    outputs=[]
    for i,x in enumerate(inputs):
        assert sorted(x)==list(range(9));y=run(x);outputs.append(y)
        assert f"| {chr(65+i)} | `{''.join(map(str,x))}` | `{''.join(map(str,y))}` |" in text
    expected={(p,None,None) for p in range(9)}|{(p,q,r)for p in range(9)for q in range(9)if q!=p for r in [None]+[v for v in range(9)if v not in(p,q)]}
    seen=set()
    for row in data['rows']:
        p,q,r=row['idle_N'],row['Q_partner'],row['N_partner_of_Q_partner'];key=(p,q,r)
        assert key in expected and key not in seen;seen.add(key)
        low=evaluate(outputs[row['low_input']],p,q,r,row['output'])
        high=evaluate(outputs[row['high_input']],p,q,r,row['output'])
        assert low==row['low'] and high==row['high'] and high-low>=4
    assert seen==expected and len(seen)==585
    seen_pairs=set();guard_count=0
    for row in data['compressed_guards']:
        p,q=row['idle_N'],row['Q_partner'];key=(p,q);assert key not in seen_pairs;seen_pairs.add(key)
        modes={r for a,b,r in expected if(a,b)==key};covered=set()
        for g in row['guards']:
            a,b=g['inputs'];assert 0<=a<b<len(outputs)
            permitted={r for r in modes if abs(evaluate(outputs[a],p,q,r,g['output'])-evaluate(outputs[b],p,q,r,g['output']))>=4}
            assert permitted==set(g['modes']) and len(permitted)==len(g['modes'])
            covered|=permitted;guard_count+=1
        assert covered==modes
        mode='idle' if q is None else str(q)
        assert f"| {p} | {mode} | {'; '.join(guard_text(g) for g in row['guards'])} |" in text
    assert seen_pairs=={(p,q)for p,q,r in expected} and guard_count==140
    report=dict(status='VERIFIED',scope='Excludes third-layer form2 after fixed H9firsttwo layers; other forms need separate proofs.',
                fixed_inputs=11,individual_local_modes=585,compressed_guards=guard_count,
                idle_N_wire_cases=9,Q_modes_per_idle_wire=9,uses_sat=False,matching_enumeration=False,
                certificate_sha256=CERTIFICATE_SHA256,
                checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                proof_note_sha256=hashlib.sha256(note.read_bytes()).hexdigest(),seconds=time.monotonic()-start)
    (ROOT/'results/h9-recovery-021536-case2-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
