#!/usr/bin/env python3
"""SAT-free audit of the critical-edge, at-most-one-cross hand theorem."""
import collections
import hashlib
from itertools import combinations
import json
from pathlib import Path
import time

ROOT=Path(__file__).parent
SOURCE=ROOT/'results/d17-feedback-fourteen-hand606-states.json'
G=((3,4),(4,5),(5,6),(2,4))
SIGN={2:1,3:-1,4:-1,5:1,6:1}


def matchings(xs):
    if not xs:
        yield ();return
    a,*rest=xs
    yield from matchings(rest)
    for j,b in enumerate(rest):
        for tail in matchings(rest[:j]+rest[j+1:]):yield ((a,b),)+tail


def edge(a,b):return tuple(sorted((a,b)))


def matching(edges):
    partner={}
    for a,b in edges:
        if a==b or a in partner and partner[a]!=b or b in partner and partner[b]!=a:return False
        partner[a]=b;partner[b]=a
    return True


def step(s,M):
    s=list(s)
    for a,b in M:s[a],s[b]=sorted((s[a],s[b]))
    return s


def image(v,M):
    for a,b in M:
        if v in (a,b):return min(a,b) if SIGN[v]<0 else max(a,b)
    return v


def fold(M,omit=None):
    return {edge(image(a,M),image(b,M)) for a,b in G if edge(a,b) not in M and (a,b)!=omit}


def signature(sets):
    return tuple(sorted(sum(1<<i for i,S in enumerate(sets) if v in S) for v in set.union(*sets)))


def near_pair(M,sets):
    return all(sum(a in S and b in S for a,b in M)>=2 for S in sets)


def path_sets(common,pair,path):
    return [{common,*pair,*p} for p in path]


def main():
    started=time.monotonic();states=json.loads(SOURCE.read_text())['states']
    # One row: C={0,1,2}, path b-q-e-r = 4-3-5-6.
    family=[{0,1,2,*p} for p in [(3,4),(3,5),(5,6)]]
    cores=[]
    for fixed,quartet in [((5,6),[0,1,2,3]),((3,4),[0,1,2,5])]:
        cores += [frozenset((fixed,)+p) for p in matchings(quartet) if len(p)==2]
    assert len(cores)==6
    one_row=0
    for M in matchings(list(range(7))):
        actual=near_pair(M,family)
        expected=any(C<=set(M) for C in cores)
        assert actual==expected
        one_row+=1
    assert one_row==232

    # Two incident rows; optionally transfer one B-path coordinate to x=2.
    # Common sentinel c=0, A pairs {u=1,x=2} and {u=1,w=3}; B path=5-4-6-7.
    path=((4,5),(4,6),(6,7));templates={};patterns=[]
    for transferred in [None,4,5,6,7]:
        first=path_sets(0,(1,2),path)
        second_path=[tuple(2 if v==transferred else v for v in p) for p in path]
        second=path_sets(0,(1,3),second_path)
        family=first+second
        assert all(len(S)==5 for S in family)
        for M in matchings(list(range(8))):assert not near_pair(M,family)
        templates[signature(family)]=transferred
        templates[signature(second+first)]=transferred
        patterns.append(dict(transferred=transferred,sets=[sorted(S) for S in family]))
    # Removing the middle B edge leaves an explicit positive control.
    ordinary=path_sets(0,(1,2),path)+path_sets(0,(1,3),path)
    assert near_pair(((0,1),(4,5),(6,7)),[ordinary[i] for i in (0,2,3,5)])

    # Abstract A folding, including deletion of an edge whose endpoints have no A--A partners.
    folded=deletions=0
    for M in matchings(sorted(SIGN)):
        assert not matching(fold(M));folded+=1
        used={v for e in M for v in e}
        for bad in G:
            if not set(bad)&used:
                assert not matching(fold(M,bad));deletions+=1
    assert folded==26

    # Direct finite corroboration of all hypotheses on the original fourteen labels.
    # No second-layer enumeration here: incidence signatures select one of the five local hand lemmas.
    counts=collections.Counter();types=collections.Counter();checked=0
    for tail in matchings([v for v in range(14) if v not in (7,10)]):
        M=((7,10),)+tail
        cross=[(a,b) for a,b in M if (a in SIGN)!=(b in SIGN) and a>=2 and b>=2 and (a>=7 or b>=7)]
        if len(cross)>1:continue
        outside=[(i,p) for i,p in enumerate(G) if edge(*p) not in M]
        bad=[]
        for row,p in outside:
            if any(sum(s[a]==s[b]==0 for a,b in M)>=4 for s in states[5*row+1:5*row+4]):bad.append((row,p))
        assert len(bad)<=1
        if bad:
            aa_used={v for a,b in M if a in SIGN and b in SIGN for v in (a,b)}
            assert not set(bad[0][1])&aa_used
        rows=[(i,p) for i,p in outside if not bad or p!=bad[0][1]]
        images={i:edge(image(a,M),image(b,M)) for i,(a,b) in rows}
        incident=next((i,j) for i,j in combinations(images,2)
                      if images[i]!=images[j] and set(images[i])&set(images[j]))
        transported=[]
        for row in incident:
            for s in states[5*row+1:5*row+4]:
                assert sum(s[a]==s[b]==0 for a,b in M)<4
                transported.append({v for v,x in enumerate(step(s,M)) if x})
        sig=signature(transported)
        assert sig in templates,(M,incident,transported)
        kind=templates[sig]
        types[str(kind)]+=1
        counts[(len(M),len(cross),len(bad))]+=1
        checked+=1
    report=dict(status='VERIFIED',sat_used=False,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                input_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                one_row_matchings=one_row,two_row_templates=patterns,matchings_per_two_row_template=764,
                local_A_matchings=folded,local_deleted_edge_cases=deletions,
                fourteen_first_matchings_checked=checked,
                direct_counts=[dict(gates=m,cross=c,bad_rows=b,count=v) for (m,c,b),v in sorted(counts.items())],
                template_uses=dict(types),seconds=round(time.monotonic()-started,4),
                theorem_scope='Every first matching containing critical dc and at most one A--B edge; any even width>=12',
                full_case606_hand_proof=False)
    (ROOT/'results/d17-feedback-round3-verified.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('two_row_templates','direct_counts')},indent=2))


if __name__=='__main__':main()
