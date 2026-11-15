#!/usr/bin/env python3
"""Direct validation of safe-B hand criteria, with no SAT or N search."""
from collections import Counter
from itertools import combinations
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).parent
V=(1,2,4,5,6,7,8,10,11,12,15,16)
A={4,5,6,7,8};B={10,11,12,15,16}
G=((5,6),(6,7),(7,8),(4,6))
SIGNS={4:1,5:-1,6:-1,7:1,8:1,10:1,11:-1,12:1,15:-1,16:1}


def matchings(vertices):
    if not vertices:yield ();return
    a,*rest=vertices
    yield from matchings(tuple(rest))
    for j,b in enumerate(rest):
        for M in matchings(tuple(rest[:j]+rest[j+1:])):yield ((a,b),)+M


def is_matching(edges):
    edges=set(edges);vertices=[v for e in edges for v in e]
    return len(vertices)==len(set(vertices))


def main():
    total=Counter();closed=Counter();remaining=Counter();small=Counter();perfect=Counter()
    for M in matchings(V):
        m=len(M);total[m]+=1
        mate={a:b for e in M for a,b in (e,e[::-1])};used=set(mate)
        def f(v):
            q=mate.get(v,v)
            return min(v,q) if SIGNS[v]<0 else max(v,q)
        crosses=[(a,b) for a,b in M if (a in A and b in B) or (a in B and b in A)]
        c=len(crosses)
        b=sum(a in B and z in B and SIGNS[a]==SIGNS[z] for a,z in M)
        z=len(B-used)
        safe=B-{v for e in crosses for v in e if v in B}
        images={f(v) for v in safe};used_images={f(v) for v in safe if v in used}
        assert len(images)==5-c-b
        assert len(used_images)==5-c-b-z
        assert images.isdisjoint({f(v) for v in A})
        H={tuple(sorted((f(a),f(v)))) for a,v in G if mate.get(a)!=v}
        assert all(a!=v for a,v in H)
        assert not is_matching(H)
        H5={tuple(sorted((f(a),f(v)))) for a,v in G if mate.get(a)!=v and (a in used or v in used)}
        if m==5:assert not is_matching(H5)
        rules=[]
        if m<=3:
            assert len(images)>=2
            rules.append('at_most_three')
            small[c]+=1
        if A<=used and len(images)>=2:rules.append('all_A_used')
        if m==6 and len(images)>=2:rules.append('perfect_safe_images')
        if m==4 and len(used_images)>=2:rules.append('four_used_safe_images')
        if m==5 and len(used_images)>=2:rules.append('five_used_safe_images')
        if m==6:perfect[f'c={c},b={b},closed={bool(rules)}']+=1
        # Verify every criterion's claimed miss against the exact first RR count.
        for rule in rules:
            choices=safe if rule not in ('four_used_safe_images','five_used_safe_images') else safe&used
            required=[(a,v) for a,v in G if mate.get(a)!=v and (rule!='five_used_safe_images' or a in used or v in used)]
            for a,v in required:
                for q in choices:
                    S={a,v,q}
                    assert sum(not(set(e)&S) for e in M)<4
            graph={tuple(sorted((f(a),f(v)))) for a,v in required}
            assert not is_matching(graph)
        key=f'm={m},cross={c}'
        if rules:closed[key]+=1
        else:remaining[key]+=1
    # Boundary control: two safe images do not force the A edge itself.
    N={(0,2),(1,3)}
    assert any(set(e)<={0,1,2} for e in N)
    assert any(set(e)<={0,1,3} for e in N)
    assert (0,1) not in N
    result=dict(status='VERIFIED',scope='Safe-B sufficient rejection criteria only; no N enumeration or universal cross-branch closure',sat_used=False,first_matchings_checked=sum(total.values()),by_size=dict(sorted(total.items())),small_M_closed_by_cross_count=dict(sorted(small.items())),closed_by_size_and_cross_count=dict(sorted(closed.items())),unclosed_by_these_criteria=dict(sorted(remaining.items())),perfect_distribution=dict(sorted(perfect.items())),two_image_nonforced_edge_control=True,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (ROOT/'results/d17-hand-defects-twelve-cross-safe.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
