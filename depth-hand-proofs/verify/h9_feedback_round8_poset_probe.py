#!/usr/bin/env python3
"""Bounded literal-component scan for the new nine-real poset obstruction.

Only normalized restrictions with zero or one RR gate in L1 are scanned.
This is not a search over all signed restrictions or all poset containments.
"""
from collections import Counter
import hashlib,itertools,json,time
from pathlib import Path
ROOT=Path(__file__).parents[1]
SOURCE=ROOT.parent/'d18-search/results/rank-layer-round6-hand-certificate.json'

def patterns(rr_count):
    if rr_count==0:
        for choices in itertools.product((0,1),repeat=9):
            s=[]
            for choice in choices:s.extend((-1,0) if choice==0 else (0,1))
            yield tuple(s)
    else:
        assert rr_count==1
        for real_pair in range(9):
            for sentinel_pair in range(9):
                if sentinel_pair==real_pair:continue
                other=[i for i in range(9) if i not in(real_pair,sentinel_pair)]
                for fixed in((-1,-1),(-1,1),(1,1)):
                    for choices in itertools.product((0,1),repeat=7):
                        s=[0]*18;s[2*sentinel_pair:2*sentinel_pair+2]=fixed
                        for pair,choice in zip(other,choices):s[2*pair:2*pair+2]=(-1,0) if choice==0 else (0,1)
                        yield tuple(s)

def trace(prefix,initial):
    s=list(initial);labels=list(range(18));gates=[]
    for layer in prefix:
        for a,b in layer:
            if s[a]==s[b]==0:gates.append((labels[a],labels[b]))
            elif s[a]>s[b]:
                s[a],s[b]=s[b],s[a];labels[a],labels[b]=labels[b],labels[a]
    real={i for i,x in enumerate(initial) if x==0};parent={i:i for i in real}
    def root(i):
        while parent[i]!=i:i=parent[i]
        return i
    for a,b in gates:parent[root(a)]=root(b)
    parts={}
    for v in real:parts.setdefault(root(v),[]).append(v)
    components=sorted((sorted(v)for v in parts.values()),key=lambda v:(-len(v),v))
    return components,gates,s,labels

def packs(sizes):
    # Necessary for an independent-component realization inside5+3+1.
    def rec(index,bins):
        if index==len(sizes):return True
        k=sizes[index]
        return any(rec(index+1,tuple(b-k if j==i else b for j,b in enumerate(bins)))
                   for i,b in enumerate(bins) if b>=k)
    return rec(0,(5,3,1))

def main():
    start=time.monotonic();records=[];data=json.loads(SOURCE.read_text())
    for record in data['records']:
        prefix=record['prefix'][:5];hist=Counter();candidates=[];counts={}
        assert prefix[0]==[[2*i,2*i+1]for i in range(9)]
        for rr_count in(0,1):
            count=0
            for signs in patterns(rr_count):
                components,gates,final,labels=trace(prefix,signs)
                sizes=tuple(map(len,components));hist[(rr_count,sizes)]+=1
                if packs(sizes):
                    candidates.append(dict(initial=signs,first_rr=rr_count,components=components,gates=gates,final=final,labels=labels))
                count+=1
                if count%1024==0:assert time.monotonic()-start<30
            counts[rr_count]=count
        assert counts=={0:512,1:27648}
        out=dict(name=record['name'],counts=counts,histogram=[dict(first_rr=k,sizes=s,count=v)for(k,s),v in sorted(hist.items())],candidates=candidates)
        records.append(out);print(record['name'],'candidates',len(candidates),'hist',dict(hist),flush=True)
    report=dict(status='BOUNDED_COMPONENT_RECOGNITION',complete_image_containment_search=False,records=records,
                source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),elapsed_seconds=time.monotonic()-start)
    (ROOT/'results/h9-feedback-round8-poset-probe.json').write_text(json.dumps(report,indent=2)+'\n')
    print('terminal',report['elapsed_seconds'])
if __name__=='__main__':main()
