#!/usr/bin/env python3
"""Generate short arithmetic matching-core proofs for every noncritical form.

No SAT or arbitrary full-second-matching enumeration is used. Branch only on
the required two internal edges of one five-sentinel set, then propagate.
"""
import gzip
import hashlib
from itertools import combinations
import json
from pathlib import Path
import time
from d17_feedback_round7_screen import ROOT,SOURCE,cases,transport


def perfect(xs):
    if not xs:yield ();return
    a,*rest=xs
    for j,b in enumerate(rest):
        for tail in perfect(rest[:j]+rest[j+1:]):yield ((a,b),)+tail


def options(S,K):
    inside=sum(a in S and b in S for a,b in K)
    need=2-inside
    if need<=0:return [()]
    free=sorted(S-{v for e in K for v in e})
    return [P for xs in combinations(free,2*need) for P in perfect(list(xs))]


def matching(K):
    used=[v for e in K for v in e]
    return len(set(used))==len(used)


def proof(required,K,stats,depth=0):
    result={'p':[]};stats['nodes']+=1;stats['max_depth']=max(stats['max_depth'],depth)
    if not matching(K):
        result['x']=-1;stats['conflicting_cores']+=1;return result
    while True:
        demands=[(len(o),i,o) for i,S in required.items() if (o:=options(S,K))!=[()]]
        assert demands,('A covering second matching was found',K)
        size,i,choices=min(demands,key=lambda x:x[:2])
        if size==0:
            result['x']=i;stats['capacity_leaves']+=1;return result
        if size==1:
            result['p'].append(i);K=tuple(sorted(K+choices[0]));stats['forced_edges']+=1;continue
        result['s']=i;stats['branch_nodes']+=1
        result['b']=[proof(required,tuple(sorted(K+P)),stats,depth+1) for P in choices]
        return result


def encode(n,M):
    p=list(range(n))
    for a,b in M:p[a]=b;p[b]=a
    return ''.join(format(v,'x') for v in p)


def main():
    start=time.monotonic();base=[s[2:] for s in json.loads(SOURCE.read_text())['states']]
    stats=dict(nodes=0,max_depth=0,conflicting_cores=0,capacity_leaves=0,forced_edges=0,branch_nodes=0)
    records=[];counts={};full=partial=0
    for deficit in (0,1):
        for n,I,E,c,M in cases(base,deficit,include_zero=True):
            states=[s+[0]*(n-12) for s in base]
            required={i:transport(s,M) for i,s in enumerate(states)
                      if sum(s[a]==s[b]==0 for a,b in M)<n//2-3}
            rows=[r for r in range(4) if all(5*r+j in required for j in range(5))]
            K=set();mask=0
            for r in rows:
                S=[required[5*r+j] for j in range(5)];T=set.intersection(*S);assert len(T)==2
                core=[T,(S[0]&S[1])-T,(S[2]&S[3])-T];assert all(len(e)==2 for e in core)
                K.update(tuple(sorted(e)) for e in core);mask|=1<<r
                if not matching(K):break
            trace=proof(required,tuple(sorted(K)),stats)
            records.append(dict(m=encode(n,M),r=mask,t=trace))
            key=str((deficit,n));counts[key]=counts.get(key,0)+1
            if rows:full+=1
            else:partial+=1
    assert len(records)==86370 and full==83642 and partial==2728
    certificate=dict(version=1,scope='All normalized noncritical perfect and two-idle case606 forms',
                     input_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),cases=records)
    raw=(json.dumps(certificate,separators=(',',':'))+'\n').encode()
    path=ROOT/'results/d17-feedback-round7-core-certificate.json.gz'
    path.write_bytes(gzip.compress(raw,compresslevel=9,mtime=0))
    report=dict(status='CERTIFICATE_GENERATED',sat_used=False,case_counts=counts,total_cases=len(records),
                full_row_cases=full,partial_row_cases=partial,stats=stats,uncompressed_bytes=len(raw),
                compressed_bytes=path.stat().st_size,certificate_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                input_sha256=certificate['input_sha256'],source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                seconds=round(time.monotonic()-start,4),finite_verification_is_a_premise=True)
    (ROOT/'results/d17-feedback-round7-core-generation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
