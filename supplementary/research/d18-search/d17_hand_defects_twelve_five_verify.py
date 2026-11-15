#!/usr/bin/env python3
"""Local checks for the complete five-gate hand argument; no SAT/full M scan."""
from itertools import combinations,product
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).parent
A={4,5,6,7,8};B={10,11,12,15,16};V=sorted({1,2}|A|B)
G=((5,6),(6,7),(7,8),(4,6));AS={4:1,5:-1,6:-1,7:1,8:1}


def edge(a,b):return tuple(sorted((a,b)))


def compatible(groups,chosen=()):
    if not groups:return chosen
    mate={a:b for e in chosen for a,b in (e,e[::-1])}
    for option in groups[0]:
        if all((a not in mate or mate[a]==b) and (b not in mate or mate[b]==a) for a,b in option):
            out=compatible(groups[1:],tuple(sorted(set(chosen)|{edge(*e) for e in option})))
            if out is not None:return out
    return None


def two_image_options(a,b,p,q):
    assert len({a,b,p,q})==4
    return [((a,b),),((a,p),(b,q)),((a,q),(b,p))]


def step(s,M):
    s=dict(s)
    for a,b in M:s[a],s[b]=min(s[a],s[b]),max(s[a],s[b])
    return s


def main():
    # Abstract final c=2,b=1 case: idle A vertex; crossed pair;
    # remaining two A vertices paired together or to the two common reals;
    # either sign relation on each cross edge. All240 possibilities are allowed,
    # even if a particular concrete B sign assignment cannot realize one.
    local=[]
    for idle in sorted(A):
        for crossed in combinations(sorted(A-{idle}),2):
            noncross=sorted(A-{idle}-set(crossed))
            for mode in ('AA','AU'):
                f={v:v for v in A}
                aa=edge(*noncross) if mode=='AA' else None
                if aa and AS[aa[0]]==AS[aa[1]]:f[aa[1]]=f[aa[0]]
                for same in product((False,True),repeat=2):
                    Q={v:f[v] if same[j] else 21+j for j,v in enumerate(crossed)}
                    P=20;groups=[]
                    for u,v in G:
                        if edge(u,v)==aa:continue
                        if idle not in (u,v):
                            assert f[u]!=f[v]
                            groups.append([((f[u],f[v]),)])
                        else:
                            w=v if u==idle else u
                            if w in noncross:groups.append([((idle,f[w]),)])
                            else:
                                other=next(t for t in crossed if t!=w)
                                groups.append(two_image_options(idle,f[w],P,Q[other]))
                    assert compatible(groups) is None,(idle,crossed,mode,same,groups)
                    local.append(dict(idle_A=idle,crossed_A=crossed,other_A_mode=mode,cross_same_sign=same))
    assert len(local)==240
    # Directly check the corrected row image count in a physical matching.
    # Both used row endpoints may be paired to the selected B sentinel.
    M=[(5,11),(6,15),(12,16),(7,8),(1,2)]
    mate={a:b for e in M for a,b in (e,e[::-1])}
    row_checks=0;comparability_checks=0
    for signs in product((-1,1),repeat=5):
        BS=dict(zip(sorted(B),signs));allstates=[]
        for u,v in G:
            for w in B:
                s={q:0 for q in V};s[u]=AS[u];s[v]=AS[v];s[w]=BS[w];allstates.append(s)
        for pair in combinations(V,2):
            x,y=pair
            if x in (1,2) or y in (1,2) or (x in AS and y in AS and set(pair) in ({5,6},{7,8})) or ((AS|BS).get(x,0)*(AS|BS).get(y,0)==-1):
                assert all(s[x]<=s[y] for s in allstates) or all(s[x]>=s[y] for s in allstates)
                comparability_checks+=1
        for u,v in ((5,6),(6,7)):
            def f(a):return min(a,mate[a]) if AS[a]<0 else max(a,mate[a])
            fixed={f(u),f(v)};third=set()
            for w in B:
                s={q:0 for q in V};s[u]=AS[u];s[v]=AS[v];s[w]=BS[w]
                after=step(s,M);S={q for q in V if after[q]!=0}
                assert fixed<=S and len(S-fixed)==1
                assert sum(s[a]==s[b]==0 for a,b in M)<=3
                third|=S-fixed;row_checks+=1
            merges=int(BS[12]==BS[16])
            assert len(third)==5-merges
        # Boundary: idle4 and crossed6 with its own B partner15 DOES peak first.
        s={q:0 for q in V};s[4]=1;s[6]=-1;s[15]=BS[15]
        assert sum(s[a]==s[b]==0 for a,b in M)==4
    # The two remaining A-idle pairs after comparable-coordinate augmentation.
    BS={10:1,11:-1,12:1,15:-1,16:1}
    states=[]
    for u,v in G:
        for w in B:
            s={q:0 for q in V};s[u]=AS[u];s[v]=AS[v];s[w]=BS[w];states.append(s)
    incomparable_A=[e for e in combinations(sorted(A),2) if not(all(s[e[0]]<=s[e[1]] for s in states) or all(s[e[0]]>=s[e[1]] for s in states))]
    assert incomparable_A==[(4,7),(4,8)]
    # Full-column forced matching P6,78 rejects the nonincident67 row
    # of the crossed leaf5, whether its B sign is equal or opposite.
    for idle_pair in incomparable_A:
        crossed=A-set(idle_pair);assert 5 in crossed and 6 in crossed
        for third in (5,21):
            N={(6,20),(7,8)};S={6,7,third}
            assert not any(set(e)<=S for e in N)
            assert 6 in S and 7 in S and third not in (8,20)
    result=dict(status='VERIFIED',scope='Local checks for M5 proof; no enumeration of all first or second matchings',sat_used=False,remaining_local_configurations=len(local),local_configuration_table=local,corrected_row_transport_checks=row_checks,B_sign_assignments=32,comparability_checks=comparability_checks,incomparable_A_idle_pairs=incomparable_A,one_idle_row_partner_boundary_passed=True,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (ROOT/'results/d17-hand-defects-twelve-five-local.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='local_configuration_table'},indent=2))

if __name__=='__main__':main()
