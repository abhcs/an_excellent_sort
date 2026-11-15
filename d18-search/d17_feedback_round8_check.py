#!/usr/bin/env python3
"""Independent direct checks of cut witnesses and the nine-form hand table."""
import gzip
import hashlib
from itertools import combinations
import json
from pathlib import Path
import time

ROOT=Path(__file__).parent


def family():
    rows=({1,2},{2,3},{3,4},{0,2});columns=({9,6,7},{9,7,8},{9,8,10},{11,8,10},{9,7,5})
    negative={1,2,6,7,9}
    return [[(-1 if v in negative else 1) if v in A|B else 0 for v in range(12)]
            for A in rows for B in columns]


def required(base,n,M):
    out={};counts={}
    for i,s0 in enumerate(base):
        s=s0+[0]*(n-12);counts[i]=sum(s[a]==s[b]==0 for a,b in M)
        for a,b in M:s[a],s[b]=min(s[a],s[b]),max(s[a],s[b])
        if counts[i]<n//2-3:out[i]={v for v,x in enumerate(s) if x}
    return out,counts


def check_radius(sets,radii,n):
    m=len(sets);sig={v:tuple(v in S for S in sets) for v in range(n)}
    assert sum(radii.values())>m and all(isinstance(r,int) and 0<=r<=2 for r in radii.values())
    for v in range(n):assert radii.get(v,0)<=sum(sig[v])
    for u,v in combinations(range(n),2):
        assert radii.get(u,0)+radii.get(v,0)<=sum(a!=b for a,b in zip(sig[u],sig[v]))
    return sig


def main():
    start=time.monotonic();base=family();source=ROOT/'results/d17-feedback-fourteen-hand606-states.json'
    assert [s[2:] for s in json.loads(source.read_text())['states']]==base
    oldpath=ROOT/'results/d17-feedback-round7-core-certificate.json.gz'
    old=json.loads(gzip.decompress(oldpath.read_bytes()))
    expected={r['m'] for r in old['cases'] if r['r']==0};assert len(expected)==2728
    path=ROOT/'results/d17-feedback-round8-cut-certificate.json.gz'
    data=json.loads(gzip.decompress(path.read_bytes()))
    assert data['input_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
    assert data['round7_certificate_sha256']==hashlib.sha256(oldpath.read_bytes()).hexdigest()
    seen=set();sizes={};unit=0
    for rec in data['cases']:
        code=rec['m'];assert code in expected and code not in seen;seen.add(code)
        n=len(code);partners=[int(x,16) for x in code]
        assert all(p<n and partners[p]==i for i,p in enumerate(partners))
        M=[(i,p) for i,p in enumerate(partners) if i<p]
        R,_=required(base,n,M)
        assert not any(all(5*r+c in R for c in range(5)) for r in range(4))
        ids=rec['s'];assert len(set(ids))==len(ids) and all(i in R for i in ids)
        radii=dict(rec['r']);assert len(radii)==len(rec['r']) and all(0<=v<n for v in radii)
        assert 4<=len(ids)<=6 and sum(radii.values())==len(ids)+1
        check_radius([R[i] for i in ids],radii,n)
        sizes[len(ids)]=sizes.get(len(ids),0)+1;unit+=all(r==1 for r in radii.values())
    assert seen==expected
    cutreport=dict(status='VERIFIED',sat_used=False,cases=len(seen),core_size_counts=sizes,
                   unit_radius_cases=unit,radius_two_cases=len(seen)-unit,
                   certificate_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                   checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   finite_first_matching_selection_remains_a_premise=True,
                   scope='All zero-full-row forms from accepted round7; no tree search or pricing solver in this check')
    (ROOT/'results/d17-feedback-round8-cut-check.json').write_text(json.dumps(cutreport,indent=2)+'\n')

    spine={(1,7),(2,9),(3,4),(8,10)};positive=(0,5,11);residual={0,5,6,11}
    expected_spines=set()
    for partner in (5,6,11):
        others=sorted(residual-{0,partner})
        expected_spines.add((12,frozenset(spine|{(0,partner),tuple(others)})))
    for a,b in combinations(positive,2):
        left=tuple(sorted(residual-{a,b}))
        expected_spines.add((14,frozenset(spine|{(a,12),(b,13),left})))
        expected_spines.add((12,frozenset(spine|{left})))
    assert len(expected_spines)==9
    for a,b in combinations(positive,2):
        assert any(s[a]<s[b] for s in base) and any(s[a]>s[b] for s in base)
    assert all(all(s[6]<=s[v] for s in base) for v in positive)
    tablepath=ROOT/'results/d17-feedback-round8-spine-witnesses.json'
    table=json.loads(tablepath.read_text());seen_spines=set();parities={}
    for rec in table['records']:
        n=rec['n'];M={tuple(e) for e in rec['M']};key=(n,frozenset(M))
        assert key in expected_spines and key not in seen_spines;seen_spines.add(key)
        assert set(range(n))-{v for e in M for v in e}==set(rec['idles'])
        R,counts=required(base,n,M);ids=rec['states'];assert len(ids)==len(set(ids))==4
        assert all(i in R for i in ids)
        assert [sorted(R[i]) for i in ids]==rec['sentinel_sets']
        assert [counts[i] for i in ids]==rec['first_counts']
        radii={int(v):r for v,r in rec['radii'].items()}
        assert len(radii)==5 and set(radii.values())=={1}
        sig=check_radius([R[i] for i in ids],radii,n)
        parity={sum(sig[v])%2 for v in radii};assert len(parity)==1
        assert all(any(sig[v]) and list(sig.values()).count(sig[v])==1 for v in radii)
        bit=parity.pop();parities[bit]=parities.get(bit,0)+1
    assert seen_spines==expected_spines
    spinereport=dict(status='VERIFIED',sat_used=False,table_rows=9,required_states_each=4,
                     selected_unique_same_parity_signatures_each=5,parity_counts=parities,
                     table_sha256=hashlib.sha256(tablepath.read_bytes()).hexdigest(),
                     checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                     scope='Corroborates the displayed nine-row hand table and residual-coordinate order; not86k enumeration')
    (ROOT/'results/d17-feedback-round8-spine-check.json').write_text(json.dumps(spinereport,indent=2)+'\n')
    print(json.dumps(dict(cut=cutreport,spine=spinereport,seconds=round(time.monotonic()-start,4)),indent=2))


if __name__=='__main__':main()
