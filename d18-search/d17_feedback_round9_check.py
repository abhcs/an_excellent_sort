#!/usr/bin/env python3
"""Independent witness replay and small parity checks; no solver imports."""
from collections import Counter
import gzip
import hashlib
from itertools import combinations,product
import json
from pathlib import Path
import time

ROOT=Path(__file__).parent


def apply(s,matching):
    out=list(s)
    for a,b in matching:
        if out[a]>out[b]:out[a],out[b]=out[b],out[a]
    return out


def states_of(case):
    first,second=case['layers'];assert case['n']==17 and len(first)==8
    outputs={}
    for choices in product((0,1),repeat=8):
        s=[0]*17
        for (a,b),c in zip(first,choices):s[b if c else a]=1 if c else -1
        assert apply(s,first)==s and all(not(s[a]==s[b]==0) for a,b in first)
        if any(s[a]==s[b]==0 for a,b in second):continue
        t=tuple(apply(s,second));mask=sum(1<<v for v,x in enumerate(t) if x==0)
        if mask in outputs:assert outputs[mask]==t
        outputs[mask]=t
    states=sorted(outputs.values());assert len(states)==case['half_blind_sets']
    return states


def legal(M):
    used=[v for e in M for v in e]
    return all(0<=a<b<17 for a,b in M) and len(used)==len(set(used))


def three_sets():
    patterns=[]
    for mask in range(256):
        P={v for v in range(8) if mask>>v&1}
        xor=0
        for v in P:xor^=v
        if len(P)%2 or xor!=7:continue
        if len(P)==2:
            edges=[tuple(sorted(P))]
        elif len(P)==4:
            edge=next((a,b) for a,b in combinations(sorted(P),2) if (a^b).bit_count()==1)
            edges=[edge,tuple(sorted(P-set(edge)))]
        else:
            assert len(P)==6;x=min(set(range(8))-P)
            assert set(range(8))-P=={x,x^7}
            edges=[(a^x,b^x) for a,b in ((1,3),(2,6),(4,5))]
        assert {v for e in edges for v in e}==P
        assert all(sum(((a>>bit)&1)!=((b>>bit)&1) for a,b in edges)==1 for bit in range(3))
        patterns.append(dict(patterns=sorted(P),pairs=edges))
    assert len(patterns)==16
    return patterns


def main():
    start=time.monotonic();coverpath=ROOT/'prefixes/complete17.jsonl'
    cases=[json.loads(s) for s in coverpath.read_text().splitlines()];assert len(cases)==609
    two_stage=json.loads((ROOT/'results/d17-feedback-round9-two-stage.json').read_text())['records']
    price=json.loads((ROOT/'results/d17-feedback-round9-static.json').read_text())['records']
    witnesses=[];family_members=0;first_fail_hist=Counter();strict_static=0;extra_profile_controls=[]
    for i,case in enumerate(cases):
        states=states_of(case);r=price[i];assert r['case_id']==case['case_id']
        q={int(v):x for v,x in r['doubled_vertex_prices'].items()};assert all(x>=0 for x in q.values())
        for a,b in combinations(range(17),2):
            assert q.get(a,0)+q.get(b,0)>=2*sum(s[a]==s[b]==0 for s in states)
        strict_static+=sum(q.values())<8*len(states)
        if i>=606:continue
        if i<604:
            source=two_stage[i];assert source['status']=='PURE_PEAK_COVER'
            M,N=source['M'],source['N']
        else:
            source=json.loads((ROOT/f'results/d17-feedback-round9-case{i}/result.json').read_text())
            assert source['status']=='SURVIVOR';M,N=source['next_layers']
        assert legal(M) and legal(N)
        profiles=[]
        for s in states:
            first_count=sum(s[a]==s[b]==0 for a,b in M);t=apply(s,M)
            second_count=sum(t[a]==t[b]==0 for a,b in N)
            assert max(first_count,second_count)==4
            profiles.append([first_count,second_count])
        misses=sum(p[0]<4 for p in profiles);first_fail_hist[misses]+=1;family_members+=len(states)
        witnesses.append(dict(case_id=case['case_id'],M=M,N=N,profiles=profiles))
    assert len(witnesses)==606 and strict_static==30
    for i in (587,600,604,605):
        source=json.loads((ROOT/f'results/d17-feedback-round9-case{i}/result.json').read_text())
        assert source['status']=='SURVIVOR';M,N=source['next_layers'];states=states_of(cases[i])
        assert legal(M) and legal(N)
        assert not(set(map(tuple,M))&set(map(tuple,cases[i]['layers'][1])))
        assert not(set(map(tuple,M))&set(map(tuple,N)))
        for s in states:
            a=sum(s[u]==s[v]==0 for u,v in M);t=apply(s,M);b=sum(t[u]==t[v]==0 for u,v in N)
            assert min(a,b)>=1 and max(a,b)==4
        extra_profile_controls.append(i)
    output=ROOT/'results/d17-feedback-round9-all606-covers.json.gz'
    data=dict(cover_sha256=hashlib.sha256(coverpath.read_bytes()).hexdigest(),cases=witnesses,
              states_order='Lexicographic signed states from independent first-pair enumeration',
              scope='Pure two-layer RR-peak covers, not sorting suffixes')
    output.write_bytes(gzip.compress((json.dumps(data,separators=(',',':'))+'\n').encode(),compresslevel=9,mtime=0))
    parity=three_sets()
    report=dict(status='VERIFIED',sat_used_by_checker=False,covered_cases=606,
                covered_case_range=[0,605],restriction_profiles_checked=family_members,
                first_layer_failure_counts=dict(sorted(first_fail_hist.items())),
                static_price_obstructions=30,stronger_profile_controls=extra_profile_controls,
                three_odd_set_parity_patterns=len(parity),
                witness_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                witness_bytes=output.stat().st_size,seconds=round(time.monotonic()-start,4),
                scope='No other D17 cover case can be excluded by this pure two-layer peak relaxation on its full nine-real half-blind family')
    (ROOT/'results/d17-feedback-round9-check.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'results/d17-feedback-round9-three-set-parity.json').write_text(json.dumps(parity,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
