#!/usr/bin/env python3
"""Direct controls for the four-wire borrower and full-triple obstruction."""
import hashlib
import itertools
import json
from pathlib import Path
import time

from adjacent_rank_ending import ending
from d13_feedback_round8_discover import old_pass
from fixed_ending_block_capacity_verify import matchings, cones

HERE=Path(__file__).resolve().parent


def real_support(n,prefix):
    q=[set() for _ in range(n)]
    witnesses=[{} for _ in range(n)]
    outputs=[]
    for perm in itertools.permutations(range(n)):
        x=list(perm)
        for layer in prefix:
            for a,b in layer:
                if x[a]>x[b]:x[a],x[b]=x[b],x[a]
        outputs.append(x)
        for c,r in enumerate(x):
            q[c].add(r);witnesses[c].setdefault(r,perm)
    return q,witnesses,outputs


def main():
    start=time.monotonic()
    cases=[]
    for n,prefix in [(4,[[(0,3)],[(1,3)],[(2,3)]]),
                     (5,[[(1,3)],[(1,2)],[(2,3)],[(0,2),(3,4)],[(1,4),(2,3)]])]:
        q,witnesses,outputs=real_support(n,prefix)
        expected=[set(range(3))]*3+([set([3])] if n==4 else [set([3,4])]*2)
        assert q==expected
        iv=[(min(s),max(s)) for s in q]
        assert old_pass(iv)
        ms=list(matchings(list(range(n))))
        req=[sum(1<<r for r in s) for s in q]
        cone_witness=None;sorters=[]
        for p,s in itertools.product(ms,repeat=2):
            cs=cones(n,p,s)
            if cone_witness is None and all(r & ~c ==0 for r,c in zip(req,cs)):
                cone_witness=[p,s]
            good=True
            for out in outputs:
                x=out[:]
                for a,b in p+s:
                    if x[a]>x[b]:x[a],x[b]=x[b],x[a]
                if x!=list(range(n)):
                    good=False;break
            if good:sorters.append([p,s])
        assert not sorters
        assert (cone_witness is not None)==(n==4)
        assert (ending(iv)[0] is not None)==(n==4)
        cases.append(dict(n=n,prefix=prefix,intervals=iv,real_orders=len(outputs),
                          witnesses=witnesses,matching_pairs=len(ms)**2,
                          cone_witness=cone_witness,sorting_completions=0))

    # A minimal four-demand core at width five. Each deletion routes directly.
    demands=[(0,0b00111),(1,0b00111),(2,0b00111),(3,0b11000)]
    ms=list(matchings(list(range(5))))
    controls=[]
    for omit in range(4):
        witness=next(([p,s] for p,s in itertools.product(ms,repeat=2)
                      if all(bits & ~cones(5,p,s)[c]==0 for i,(c,bits) in enumerate(demands) if i!=omit)),None)
        assert witness is not None
        controls.append(dict(omitted_demand=omit,matching_pair=witness))
    assert not any(all(bits & ~cones(5,p,s)[c]==0 for c,bits in demands)
                   for p,s in itertools.product(ms,repeat=2))

    # Audit the universal forced-component statement for all P,S through n=7.
    audits=[]
    for n in range(3,8):
        ms=list(matchings(list(range(n))))
        triples=list(itertools.combinations(range(n),3))
        hits=0
        for p,s in itertools.product(ms,repeat=2):
            cs=cones(n,p,s)
            for t in triples:
                mask=sum(1<<v for v in t)
                if not all(mask & ~cs[v]==0 for v in t):continue
                candidates=[u for u in range(n) if u not in t
                            and all(cs[v]==mask|(1<<u) for v in (*t,u))]
                assert len(candidates)==1,(n,p,s,t,candidates)
                e=set(t)|set(candidates)
                assert all(not (set(edge)&e) or set(edge)<=e for edge in p+s)
                hits+=1
        audits.append(dict(n=n,matching_pairs=len(ms)**2,full_triple_occurrences=hits))

    wider=[]
    for n in (13,18):
        iv=[(0,2)]*3+[(c,c) for c in range(3,n)]
        pair,_=ending(iv)
        assert pair is not None and old_pass(iv)
        assert all(sum(1<<r for r in range(a,b+1)) & ~cone ==0
                   for (a,b),cone in zip(iv,cones(n,*pair)))
        wider.append(dict(n=n,intervals=iv,cone_witness=pair,
                          actual_prefix_construction='cross-block sweeps; proved in note',
                          sorting_rejected_by='full-triple theorem'))
    iv13=[(0,2)]*3+[(3,4)]*2+[(5,8)]*4+[(9,12)]*4
    assert old_pass(iv13) and ending(iv13)[0] is None
    result=dict(status='VERIFIED',uses_sat=False,cases=cases,
                minimal_four_demand_controls=controls,borrower_lemma_audits=audits,
                wider_reachability_positive_controls=wider,
                thirteen_no_borrower_intervals=iv13,seconds=time.monotonic()-start,
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                proof_sha256=hashlib.sha256((HERE/'d13_feedback_round8_triples.md').read_bytes()).hexdigest())
    (HERE/'results/d13_feedback_round8-triples-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('cases','wider_reachability_positive_controls')},indent=2))


if __name__=='__main__':main()
