#!/usr/bin/env python3
"""Find prefix exclusions using compression plus exact matching/price bounds."""
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time

ROOT=Path(__file__).parent


def weights(n,states):
    return [[sum(bool(s['real_mask']>>a&1) and bool(s['real_mask']>>b&1) for s in states)
             if a!=b else 0 for b in range(n)] for a in range(n)]


def vertex_prices(w):
    """Hungarian potentials on the symmetric double cover, then direct check.

    Returned prices are doubled integers; their pair inequalities alone
    constitute the certificate and do not require trusting optimality.
    """
    n=len(w);u=[0]*(n+1);v=[0]*(n+1);p=[0]*(n+1);way=[0]*(n+1)
    for i in range(1,n+1):
        p[0]=i;j0=0;minimum=[10**12]*(n+1);used=[False]*(n+1)
        while True:
            used[j0]=True;i0=p[j0];delta=10**12;j1=0
            for j in range(1,n+1):
                if used[j]:continue
                current=-w[i0-1][j-1]-u[i0]-v[j]
                if current<minimum[j]:minimum[j]=current;way[j]=j0
                if minimum[j]<delta:delta=minimum[j];j1=j
            for j in range(n+1):
                if used[j]:u[p[j]]+=delta;v[j]-=delta
                else:minimum[j]-=delta
            j0=j1
            if p[j0]==0:break
        while j0:
            j1=way[j0];p[j0]=p[j1];j0=j1
    prices=[-u[i+1]-v[i+1] for i in range(n)]
    assert all(q>=0 for q in prices)
    assert all(prices[a]+prices[b]>=2*w[a][b] for a in range(n) for b in range(n) if a!=b)
    return prices


def maximum_matching(w):
    n=len(w)
    @lru_cache(None)
    def dp(mask):
        if not mask:return 0,()
        a=(mask&-mask).bit_length()-1;rest=mask^(1<<a)
        best=dp(rest)
        for b in range(a+1,n):
            if rest>>b&1:
                value,pairs=dp(rest^(1<<b));value+=w[a][b]
                if value>best[0]:best=(value,((a,b),)+pairs)
        return best
    return dp((1<<n)-1)


def classify(n,reals,states,minimize=True):
    peak=reals//2;minimum_first=peak-1
    for index,state in enumerate(states):
        if len(state['compressed_oriented_pairs'])<minimum_first:
            return dict(status='DIRECT_HAND_EXCLUSION',core_indices=[index])
    if not states:return dict(status='EMPTY_RESTRICTION_FAMILY')
    w=weights(n,states);prices=vertex_prices(w);target=peak*len(states)
    if sum(prices)<2*target:
        indices=list(range(len(states)))
        if minimize:
            for index in indices[:]:
                candidate=[j for j in indices if j!=index]
                next_prices=vertex_prices(weights(n,[states[j] for j in candidate]))
                if sum(next_prices)<2*peak*len(candidate):indices=candidate;prices=next_prices
        return dict(status='VERTEX_PRICE_HAND_EXCLUSION',core_indices=indices,
                    twice_vertex_prices=prices,twice_bound=sum(prices),
                    required_sum=peak*len(indices))
    score,matching=maximum_matching(w)
    if score<target:
        return dict(status='MATCHING_DP_EXCLUSION',maximum_sum=score,required_sum=target,
                    core_indices=list(range(len(states))))
    assert score==target
    assert all(sum(bool(s['real_mask']>>a&1) and bool(s['real_mask']>>b&1) for a,b in matching)==peak for s in states)
    return dict(status='PROFILE_SURVIVOR',matching=matching)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--seconds',type=float,default=90)
    args=ap.parse_args();start=time.monotonic()
    records=[json.loads(s) for s in args.input.read_text().splitlines()]
    results=[];complete=True
    with tempfile.TemporaryDirectory(prefix='commuting-prefix-audit-') as temp:
        binary=Path(temp)/'enumerate'
        subprocess.run(['c++','-O3','-std=c++17',str(ROOT/'commuting_prefix_states.cpp'),'-o',str(binary)],check=True,capture_output=True,timeout=30)
        for index,record in enumerate(records):
            if time.monotonic()-start>args.seconds:complete=False;break
            n=record['n'];layers=record['layers'][:5]
            if n!=18 or len(layers)!=5:continue
            text=[f'{n} {len(layers)}']
            for layer in layers:
                mate=[-1]*n
                for a,b in layer:assert mate[a]==mate[b]==-1;mate[a]=b;mate[b]=a
                text.append(' '.join(map(str,mate)))
            net=Path(temp)/'prefix.txt';net.write_text('\n'.join(text)+'\n')
            row=dict(index=index,layers=layers,retained={})
            for reals in (7,8):
                run=subprocess.run([str(binary),str(net),str(reals),str(reals//2-1)],capture_output=True,text=True,check=True,timeout=30)
                enumeration=json.loads(run.stdout)
                classification=classify(n,reals,enumeration['states'])
                item=dict(**classification,normalized_placements=enumeration['normalized_placements'],
                          accepted_placements=enumeration['accepted_placements'],cut_real_sets=len(enumeration['states']))
                if 'core_indices' in item:item['witnesses']=[enumeration['states'][j] for j in item['core_indices']]
                row['retained'][reals]=item
            results.append(row)
    counts={}
    for row in results:
        for item in row['retained'].values():counts[item['status']]=counts.get(item['status'],0)+1
    report=dict(status='COMPLETE' if complete else 'TIME_LIMIT',prefixes_checked=len(results),
                input_prefixes=len(records),classification_counts=counts,seconds=round(time.monotonic()-start,4),
                scope='Specified five-layer samples, not a complete D18 cover; each hand exclusion supplies explicit restriction/price witnesses',
                sat_used=False,results=results,
                sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                        (args.input,Path(__file__),ROOT/'commuting_prefix_states.cpp')})
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('results','sha256')},indent=2))


if __name__=='__main__':main()
