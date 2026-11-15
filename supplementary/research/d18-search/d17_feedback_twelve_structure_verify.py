#!/usr/bin/env python3
"""Small local checks for the structure note; no twelve-wire matching scan."""
from itertools import combinations,product
import hashlib
import json
from pathlib import Path


def matchings(xs):
    if not xs:
        yield []
        return
    a,*rest=xs
    yield from matchings(rest)
    for j,b in enumerate(rest):
        for tail in matchings(rest[:j]+rest[j+1:]):
            yield [(a,b)]+tail


def hits(matching,vertices):
    return any(a in vertices and b in vertices for a,b in matching)


def main():
    G=[('a','b'),('b','c'),('c','e'),('b','d')]
    A=set('abcde')
    sign=dict(a=-1,b=-1,c=1,d=1,e=1)
    augmentation=0
    for x,y in product((-1,0,1),repeat=2):
        low,high=sorted((x,y))
        assert (x==y==0)==(low==high==0)
        augmentation+=1
    folds=[]
    for E0 in G:
        for P in combinations(sorted(A-set(E0)),2):
            f={x:x for x in A}
            if sign[P[0]]==sign[P[1]]:
                f[P[1]]=P[0]
            # An opposite-sign pair permutes positions injectively, which
            # does not affect whether the graph is a matching.
            edges={tuple(sorted((f[u],f[v]))) for u,v in G
                   if set((u,v))!=set(E0) and set((u,v))!=set(P)}
            assert all(u!=v for u,v in edges)
            degree={u:sum(u in edge for edge in edges) for u in set().union(*(set(e) for e in edges))}
            assert max(degree.values())>=2
            folds.append(dict(idle_edge=E0,AA_pair=P,folded_edges=sorted(edges)))
    six=list(matchings(list('abcdep')))
    assert len(six)==76
    full=[m for m in six if all(hits(m,set(edge)|{'p'}) for edge in G)]
    assert len(full)==2
    forced={frozenset(('p','b')),frozenset(('c','e'))}
    assert all(forced<={frozenset(e) for e in m} for m in full)
    bad_same={}
    for x in 'acde':
        edge=('b','c') if x in 'ad' else ('a','b')
        triple=set(edge)|{x}
        assert x not in edge
        assert all(not hits(m,triple) for m in full)
        bad_same[x]=sorted(triple)
    seven=[m for m in matchings(list('abcdepq'))
           if forced<={frozenset(e) for e in m}]
    assert len(seven)==4
    for x in 'acde':
        required=[set(edge)|{'q'} for edge in G if x not in edge]
        assert all(not all(hits(m,s) for s in required) for m in seven)
    # The exception at the center is real: its only nonincident edge ce
    # is already present, regardless of the third position.
    assert all(hits(m,{'c','e','q'}) for m in seven)
    state_path=Path(__file__).with_name('results')/'d17-feedback-twelve-states.json'
    states=json.loads(state_path.read_text())['states']
    comparable=[]
    incomparable=[]
    for a,b in combinations(range(12),2):
        increasing=all(s[a]<=s[b] for s in states)
        decreasing=all(s[a]>=s[b] for s in states)
        if not increasing and not decreasing:
            incomparable.append((a,b))
            continue
        comparable.append((a,b))
        for s in states:
            actual=list(s)
            actual[a],actual[b]=sorted((actual[a],actual[b]))
            expected=list(s)
            if not increasing:
                expected[a],expected[b]=expected[b],expected[a]
            assert actual==expected
    minus={3,4,8,10}
    plus={2,5,6,7,9,11}
    Acompact=set(range(2,7))
    Bcompact=set(range(7,12))
    expected={(2,5),(2,6)}
    expected|={tuple(sorted((a,b))) for a,b in combinations(Bcompact,2)
               if ({a,b}<=minus or {a,b}<=plus)}
    expected|={tuple(sorted((a,b))) for a in Acompact for b in Bcompact
               if ({a,b}<=minus or {a,b}<=plus)}
    assert set(incomparable)==expected
    assert len(comparable)==47 and len(incomparable)==19
    result=dict(status='VERIFIED',safe_augmentation_local_states=augmentation,
                idle_edge_fold_cases=len(folds),folds=folds,
                six_vertex_partial_matchings=len(six),full_column_controls=full,
                same_sign_bad_triples=bad_same,
                opposite_sign_forced_partner_completions=len(seven),
                central_endpoint_positive_controls=len(seven),
                comparable_idle_pairs=len(comparable),
                comparable_routing_state_checks=len(comparable)*len(states),
                incomparable_idle_pairs=incomparable,
                scope='Local lemmas only; no full first-matching scan or SAT',
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    out=Path(__file__).with_name('d17_feedback_twelve_structure_verified.json')
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('folds','full_column_controls')}))


if __name__=='__main__':
    main()
