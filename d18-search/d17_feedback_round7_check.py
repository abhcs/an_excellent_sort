#!/usr/bin/env python3
"""Independent stdlib checker of the complete noncritical arithmetic proof.

Imports no generator, discovery code, prior checker, or SAT package. Coverage
uses a different recursion: each of twelve variables is paired, idle, or sent
to the next common-real label. Proof leaves use the crossing-edge criterion.
"""
import gzip
import hashlib
from itertools import combinations
import json
from pathlib import Path
import time

ROOT=Path(__file__).parent
SOURCE=ROOT/'results/d17-feedback-fourteen-hand606-states.json'
CERT=ROOT/'results/d17-feedback-round7-core-certificate.json.gz'


def canonical_codes(states):
    incomparable={(a,b) for a in range(12) for b in range(12)
                  if any(s[a]<s[b] for s in states) and any(s[a]>s[b] for s in states)}
    def recurse(todo,pairs,idles,external):
        if not todo:
            if len(idles) not in (0,2) or len(external)%2:return
            n=12+len(external);partners=list(range(n))
            for a,b in pairs+tuple((a,12+j) for j,a in enumerate(external)):
                partners[a]=b;partners[b]=a
            yield ''.join(format(p,'x') for p in partners);return
        v,*rest=todo
        for j,w in enumerate(rest):
            if (v,w)==(5,8):continue
            yield from recurse(rest[:j]+rest[j+1:],pairs+((v,w),),idles,external)
        if len(idles)<2 and all((v,w) in incomparable for w in idles):
            yield from recurse(rest,pairs,idles+(v,),external)
        if len(external)<4 and all((v,w) in incomparable for w in external):
            yield from recurse(rest,pairs,idles,external+(v,))
    return recurse(list(range(12)),(),(),())


def legal(K):
    endpoints=[v for e in K for v in e]
    return all(a<b for a,b in K) and len(endpoints)==len(set(endpoints))


def branches(S,K):
    need=2-sum(a in S and b in S for a,b in K)
    assert need in (1,2)
    available=S-{v for e in K for v in e}
    candidates=[tuple(P) for P in combinations(list(combinations(sorted(available),2)),need) if legal(P)]
    # Canonical order by the chosen vertex set, then lexicographic pairing.
    return sorted(candidates,key=lambda P:(tuple(sorted(v for e in P for v in e)),P))


def verify(node,K,required,stats,depth=0):
    stats['nodes']+=1;stats['max_depth']=max(stats['max_depth'],depth)
    assert isinstance(node['p'],list)
    if not legal(K):
        assert node=={'p':[],'x':-1};stats['conflicting_cores']+=1;return
    for i in node['p']:
        assert i in required;S=required[i];available=S-{v for e in K for v in e}
        assert sum(a in S and b in S for a,b in K)==1 and len(available)==2
        K=K|{tuple(sorted(available))};assert legal(K);stats['forced_edges']+=1
    if 'x' in node:
        assert set(node)=={'p','x'} and node['x'] in required
        S=required[node['x']]
        # A perfect matching on a five-set with two internal edges has only
        # one edge crossing its boundary. Two forced crossings refute it.
        assert sum((a in S)!=(b in S) for a,b in K)>=2
        stats['capacity_leaves']+=1;return
    assert set(node)=={'p','s','b'} and node['s'] in required
    choices=branches(required[node['s']],K);assert len(choices)>1
    assert len(node['b'])==len(choices);stats['branch_nodes']+=1
    for P,child in zip(choices,node['b']):verify(child,K|set(P),required,stats,depth+1)


def main():
    start=time.monotonic();supplied=json.loads(SOURCE.read_text())['states']
    assert len(supplied)==20 and all(len(s)==14 and s[:2]==[0,0] for s in supplied)
    states=[s[2:] for s in supplied]
    rows=({1,2},{2,3},{3,4},{0,2})
    columns=({9,6,7},{9,7,8},{9,8,10},{11,8,10},{9,7,5})
    negative={1,2,6,7,9}
    exact=[[(-1 if v in negative else 1) if v in A|B else 0 for v in range(12)]
           for A in rows for B in columns]
    assert states==exact
    expected=set();enumerated=0
    for code in canonical_codes(states):
        assert code not in expected;expected.add(code);enumerated+=1
    assert enumerated==86370
    data=json.loads(gzip.decompress(CERT.read_bytes()))
    assert data['version']==1 and data['input_sha256']==hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    seen=set();hist={};full=partial=0;zero_cross=0
    stats=dict(nodes=0,max_depth=0,conflicting_cores=0,capacity_leaves=0,forced_edges=0,branch_nodes=0)
    for record in data['cases']:
        code=record['m'];assert code in expected and code not in seen;seen.add(code)
        n=len(code);p=[int(x,16) for x in code]
        assert n in (12,14,16) and all(v<n and p[v]==i for i,v in enumerate(p))
        M={(i,v) for i,v in enumerate(p) if i<v};I={i for i,v in enumerate(p) if i==v}
        assert len(I) in (0,2) and (5,8) not in M and legal(M)
        deficit=len(I)//2;key=str((deficit,n));hist[key]=hist.get(key,0)+1
        zero_cross+=not any(a<5<=b<12 for a,b in M)
        required={}
        for i,base in enumerate(states):
            s=base+[0]*(n-12)
            if sum(s[a]==s[b]==0 for a,b in M)>=n//2-3:continue
            for a,b in M:s[a],s[b]=min(s[a],s[b]),max(s[a],s[b])
            required[i]={v for v,x in enumerate(s) if x};assert len(required[i])==5
        mask=record['r'];assert isinstance(mask,int) and 0<=mask<16
        K=set()
        for r in range(4):
            if not mask&(1<<r):continue
            assert all(5*r+j in required for j in range(5))
            S=[required[5*r+j] for j in range(5)]
            fixed=set.intersection(*S);left=(S[0]&S[1])-fixed;right=(S[2]&S[3])-fixed
            assert len(fixed)==len(left)==len(right)==2 and len(fixed|left|right)==6
            core={tuple(sorted(e)) for e in (fixed,left,right)}
            assert legal(core) and all(sum(a in s and b in s for a,b in core)==2 for s in S)
            K|=core
        if mask:full+=1
        else:partial+=1
        verify(record['t'],K,required,stats)
    assert seen==expected
    report=dict(status='VERIFIED',sat_used=False,canonical_cases=len(seen),case_counts=hist,
                full_row_cases=full,partial_row_cases=partial,zero_cross_cases=zero_cross,stats=stats,
                exact_twenty_state_family_checked=True,independent_coverage_recursion=True,
                finite_verification_is_a_premise=True,complete_pure_hand_classification=False,
                input_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                certificate_sha256=hashlib.sha256(CERT.read_bytes()).hexdigest(),
                checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                seconds=round(time.monotonic()-start,4))
    (ROOT/'results/d17-feedback-round7-core-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
