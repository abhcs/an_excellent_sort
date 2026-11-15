#!/usr/bin/env python3
"""SAT-free checks of the perfect critical two-cross hand reduction."""
import collections
import hashlib
from itertools import combinations,product
import json
from pathlib import Path
import time

ROOT=Path(__file__).parent
INPUT=ROOT/'results/d17-feedback-fourteen-hand606-states.json'
G=((3,4),(4,5),(5,6),(2,4))
SIGN={2:1,3:-1,4:-1,5:1,6:1}
PATH=((4,5),(4,6),(6,7)) # b--q--e--r = 5--4--6--7


def matchings(xs,perfect=False):
    if not xs:
        yield ();return
    a,*rest=xs
    if not perfect:yield from matchings(rest)
    for j,b in enumerate(rest):
        for tail in matchings(rest[:j]+rest[j+1:],perfect):yield ((a,b),)+tail


def edge(a,b):return tuple(sorted((a,b)))


def near_pair(M,sets):return all(sum(a in S and b in S for a,b in M)>=2 for S in sets)


def step(s,M):
    s=list(s)
    for a,b in M:s[a],s[b]=sorted((s[a],s[b]))
    return s


def image(v,M):
    for a,b in M:
        if v in (a,b):return a if SIGN[v]<0 else b
    return v


def signature(sets):
    return tuple(sorted(sum(1<<i for i,S in enumerate(sets) if v in S) for v in set.union(*sets)))


def double_family(p,q):
    return ([{0,1,2,*[3 if v==q else v for v in e]} for e in PATH]+
            [{0,1,3,*[2 if v==p else v for v in e]} for e in PATH])


def local_core(p,q):
    if (p,q)==(4,6):
        return [tuple(sorted(((4,5),(6,7))+P)) for P in matchings([0,1,2,3],True)]
    if (p,q)==(5,7):return [((0,1),(2,4),(3,6))]
    return []


def cap(core,S):
    used={v for e in core for v in e}
    return sum(a in S and b in S for a,b in core)+len(S-used)//2


def main():
    started=time.monotonic();states=json.loads(INPUT.read_text())['states'];unsat=set();local=[]
    # Previously proved ordinary and single-transfer patterns, included directly.
    for y in [None,4,5,6,7]:
        S=[{0,1,2,*e} for e in PATH]+[{0,1,3,*[2 if v==y else v for v in e]} for e in PATH]
        unsat.update((signature(S),signature(S[3:]+S[:3])))
        assert not any(near_pair(M,S) for M in matchings(list(range(8))))
    # Six new exact double-transfer classifications.
    for p,q in combinations(range(4,8),2):
        S=double_family(p,q);cores=local_core(p,q);good=0
        for M in matchings(list(range(8))):
            actual=near_pair(M,S)
            expected=any(set(C)<=set(M) for C in cores)
            assert actual==expected,(p,q,M)
            good+=actual
        if not cores:unsat.update((signature(S),signature(S[3:]+S[:3])))
        local.append(dict(partners=[p,q],sets=[sorted(s) for s in S],cores=cores,local_matchings=764,solutions=good))

    counts=collections.Counter();exception_examples={};firsts=0
    for tail in matchings([v for v in range(14) if v not in (7,10)],True):
        M=((7,10),)+tail
        crosses={a:b for a,b in M if a in SIGN and b>=7}
        if len(crosses)!=2:continue
        firsts+=1
        rows=[];bad=[]
        for i,(u,v) in enumerate(G):
            if edge(u,v) in M:continue
            family=states[5*i+1:5*i+4]
            if any(sum(s[a]==s[b]==0 for a,b in M)>=4 for s in family):
                bad.append((u,v));continue
            rows.append((i,edge(image(u,M),image(v,M))))
        assert len(bad)<=1
        if bad:assert set(bad[0])==set(crosses)
        incident=[(i,j) for (i,a),(j,b) in combinations(rows,2) if a!=b and set(a)&set(b)]
        assert incident
        local_closed=False
        for i,j in incident:
            S=[{v for v,x in enumerate(step(s,M)) if x} for r in (i,j) for s in states[5*r+1:5*r+4]]
            if signature(S) in unsat:
                local_closed=True;break
        if local_closed:
            counts['two_row_lemma']+=1;continue
        assert set(crosses)=={2,3} and (4,5) in M,M
        assert (crosses[3],crosses[2]) in ((11,12),(9,13)),M
        kind='inner' if crosses[3]==11 else 'outer'
        # Route B coordinates against a reference where both crossed A sentinels are active.
        refs=[]
        for col in (1,2,3):
            s=[0]*7+states[col][7:]
            s[3]=-1;s[2]=1;refs.append(s)
        perm=list(range(14))
        for a,b in M:
            if not all(s[a]<=s[b] for s in refs):
                assert all(s[a]>=s[b] for s in refs)
                perm[a],perm[b]=perm[b],perm[a]
        k,u,x,y=perm[10],image(4,M),image(3,M),image(2,M)
        q,b,e,r=[perm[v] for v in (11,9,12,13)]
        assert len({k,u,x,y,q,b,e,r})==8
        cores=([((q,b),(e,r))+P for P in matchings([k,u,x,y],True)] if kind=='inner'
               else [((k,u),(x,q),(y,e))])
        # CE is outside M; all three of its selected states miss the first peak.
        family=states[11:14]
        assert all(sum(s[a]==s[b]==0 for a,b in M)<4 for s in family)
        S=[{v for v,z in enumerate(step(s,M)) if z} for s in family]
        caps=[[cap(C,T) for T in S] for C in cores]
        assert all(min(row)<2 for row in caps),(M,kind,cores,S,caps)
        counts[kind+'_third_row']+=1
        exception_examples.setdefault(kind,dict(M=M,cores=cores,CE_sets=[sorted(T) for T in S],caps=caps))
    assert firsts==3600
    report=dict(status='VERIFIED',sat_used=False,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                input_sha256=hashlib.sha256(INPUT.read_bytes()).hexdigest(),double_transfer_classes=local,
                critical_two_cross_perfect_matchings=firsts,classification_counts=dict(counts),
                exceptional_examples=exception_examples,seconds=round(time.monotonic()-started,4),
                theorem_scope='Perfect first matching, critical dc, exactly two A--B edges; arbitrary even active width',
                full_case606_hand_proof=False)
    (ROOT/'results/d17-feedback-round4-verified.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('double_transfer_classes','exceptional_examples')},indent=2))


if __name__=='__main__':main()
