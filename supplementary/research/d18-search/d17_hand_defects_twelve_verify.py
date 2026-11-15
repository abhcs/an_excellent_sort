#!/usr/bin/env python3
"""Direct check of the no-A--B-cross-edge branch on twelve wires; no SAT."""
import hashlib
import json
from collections import Counter
from itertools import combinations
from pathlib import Path

ROOT=Path(__file__).parent
V=(1,2,4,5,6,7,8,10,11,12,15,16)
A={4,5,6,7,8};B={10,11,12,15,16}
A_STATES=({5:-1,6:-1},{6:-1,7:1},{7:1,8:1},{4:1,6:-1})
B_STATES={11:-1,15:-1,16:1,12:1,10:1}
SIGNS={4:1,5:-1,6:-1,7:1,8:1,**B_STATES}


def matchings(vertices):
    if not vertices:yield ();return
    a,*rest=vertices
    yield from matchings(tuple(rest))
    for j,b in enumerate(rest):
        if (a in A and b in B) or (a in B and b in A):continue
        for M in matchings(tuple(rest[:j]+rest[j+1:])):yield ((a,b),)+M


def sorted_edge(a,b):return tuple(sorted((a,b)))


def options(pair,images):
    a,b=pair;images=sorted(images)
    if not images:return [()]
    assert a!=b and a not in images and b not in images
    if len(images)>=3:return [((a,b),)]
    if len(images)==1:
        c=images[0];return [((a,b),),((a,c),),((b,c),)]
    c,d=images
    return [((a,b),),((a,c),(b,d)),((a,d),(b,c))]


def compatible(groups,chosen=()):
    if not groups:return chosen
    mate={a:b for e in chosen for a,b in (e,e[::-1])}
    for option in groups[0]:
        if all((a not in mate or mate[a]==b) and (b not in mate or mate[b]==a) for a,b in option):
            extended=tuple(sorted(set(chosen)|{sorted_edge(*e) for e in option}))
            out=compatible(groups[1:],extended)
            if out is not None:return out
    return None


def analyze(M):
    mate={a:b for e in M for a,b in (e,e[::-1])}
    def image(c):
        d=mate.get(c,c)
        return min(c,d) if SIGNS[c]<0 else max(c,d)
    groups=[];evidence=[]
    for state in A_STATES:
        a,b=sorted(state)
        pair=(a,b) if mate.get(a)==b else tuple(sorted((image(a),image(b))))
        needed=[]
        for c in B_STATES:
            S={a,b,c}
            count=sum(not(S&set(e)) for e in M)
            if count<4:needed.append(c)
        images={image(c) for c in needed}
        groups.append(options(pair,images));evidence.append(dict(A_pair=[a,b],needed_B=needed,images=sorted(images),transported_pair=pair))
    return compatible(groups),evidence


def main():
    totals=Counter();idle_counts=Counter()
    for M in matchings(V):
        solution,evidence=analyze(M)
        assert solution is None,(M,solution,evidence)
        totals[len(M)]+=1
        used={c for e in M for c in e}
        idle_counts[f'{len(M)} edges, {len(A-used)} idle A']+=1
    result=dict(status='VERIFIED',scope='All arbitrary first matchings with no A--B cross edge; second matching arbitrary via safe final-layer filling',vertices=V,A=sorted(A),B=sorted(B),matchings_checked=sum(totals.values()),by_size=dict(sorted(totals.items())),by_idle_A=dict(sorted(idle_counts.items())),sat_used=False,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (ROOT/'results/d17-hand-defects-twelve-no-cross.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
