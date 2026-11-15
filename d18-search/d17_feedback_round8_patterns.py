#!/usr/bin/env python3
"""Bounded arithmetic feedback for the four depth-two noncritical forms."""
import gzip
from itertools import combinations
import json
from pathlib import Path
import time
from d17_feedback_round7_partial import solve
from d17_feedback_round7_screen import transport

ROOT=Path(__file__).parent


def prices(sets):
    """Exact doubled fractional vertex prices from symmetric assignment duals."""
    vertices=sorted(set.union(*sets));n=len(vertices)
    w=[[0]*n for _ in range(n)]
    for i,a in enumerate(vertices):
        for j,b in enumerate(vertices):
            if i!=j:w[i][j]=sum(a in S and b in S for S in sets)
    # Integer Hungarian potentials for minimum assignment with costs -w.
    u=[0]*(n+1);v=[0]*(n+1);p=[0]*(n+1);way=[0]*(n+1)
    for i in range(1,n+1):
        p[0]=i;j0=0;minimum=[10**9]*(n+1);used=[False]*(n+1)
        while True:
            used[j0]=True;i0=p[j0];delta=10**9;j1=0
            for j in range(1,n+1):
                if not used[j]:
                    cur=-w[i0-1][j-1]-u[i0]-v[j]
                    if cur<minimum[j]:minimum[j]=cur;way[j]=j0
                    if minimum[j]<delta:delta=minimum[j];j1=j
            for j in range(n+1):
                if used[j]:u[p[j]]+=delta;v[j]-=delta
                else:minimum[j]-=delta
            j0=j1
            if p[j0]==0:break
        while True:
            j1=way[j0];p[j0]=p[j1];j0=j1
            if j0==0:break
    q=[-u[i+1]-v[i+1] for i in range(n)]
    assert all(x>=0 for x in q)
    assert all(q[i]+q[j]>=2*w[i][j] for i in range(n) for j in range(n))
    return dict(zip(vertices,q)),sum(q),4*len(sets)


def depth(t):return 0 if 'x' in t else 1+max(map(depth,t['b']))


def main():
    start=time.monotonic();base=[s[2:] for s in json.loads((ROOT/'results/d17-feedback-fourteen-hand606-states.json').read_text())['states']]
    cert=json.loads(gzip.decompress((ROOT/'results/d17-feedback-round7-core-certificate.json.gz').read_bytes()))
    reports=[]
    for r in cert['cases']:
        if depth(r['t'])<2:continue
        code=r['m'];n=len(code);M=[(i,int(x,16)) for i,x in enumerate(code) if i<int(x,16)]
        family=[s+[0]*(n-12) for s in base]
        required={i:transport(s,M) for i,s in enumerate(family) if sum(s[a]==s[b]==0 for a,b in M)<n//2-3}
        core=dict(required)
        for i in tuple(core):
            smaller={j:S for j,S in core.items() if j!=i}
            if solve(smaller)[0] is None:core=smaller
        q,value,target=prices(list(core.values()))
        reports.append(dict(code=code,M=M,required=list(required),core={i:sorted(S) for i,S in core.items()},
                            doubled_prices=q,doubled_price_total=value,doubled_demand=target,
                            deletion_minimal=True))
    report=dict(status='COMPLETED_FEEDBACK',sat_used=False,patterns=reports,seconds=round(time.monotonic()-start,4))
    (ROOT/'results/d17-feedback-round8-hard-patterns.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
