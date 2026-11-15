#!/usr/bin/env python3
"""Independent direct-ending controls of the fixed-cut finite-state DP."""
import hashlib
import itertools
import json
from pathlib import Path
import random
import time
from d13_feedback_round9_data_dp import profiles,ending,FREE

HERE=Path(__file__).resolve().parent


def matchings(xs):
    if not xs:yield ();return
    a,*rest=xs
    yield from matchings(rest)
    for b in rest:
        for tail in matchings([v for v in rest if v!=b]):yield ((a,b),)+tail


def run(x,net):
    x=list(x)
    for layer in net:
        for a,b in layer:x[a],x[b]=min(x[a],x[b]),max(x[a],x[b])
    return tuple(x)


def sorts(xs,net):return all(run(x,net)==tuple(sorted(x)) for x in xs)


def main():
    start=time.monotonic();rng=random.Random(90620261115)
    reports=[];accepted=rejected=0
    for n in range(2,7):
        ms=list(matchings(list(range(n))))
        last=[s for s in ms if all(b==a+1 for a,b in s)]
        if n<=4:prefixes=list(itertools.product(ms,repeat=2))
        else:prefixes=[tuple(rng.choice(ms) for _ in range(rng.randrange(1,7))) for _ in range(35)]
        seen=set();cases=0
        for prefix in prefixes:
            xs=tuple(sorted({run(x,prefix) for x in itertools.product((False,True),repeat=n)}))
            if xs in seen:continue
            seen.add(xs)
            direct=next(([p,s] for p,s in itertools.product(ms,last) if sorts(xs,[p,s])),None)
            pair,stats=ending(profiles(xs))
            assert (pair is not None)==(direct is not None),(n,prefix,xs)
            if pair is not None:
                assert sorts(xs,pair)
                assert all(b-a<=3 for a,b in pair[0]) and all(b-a==1 for a,b in pair[1])
                accepted+=1
            else:rejected+=1
            cases+=1
        reports.append(dict(n=n,actual_prefix_images=cases,arbitrary_P_count=len(ms),adjacent_S_count=len(last)))
    # Scope counterexample: a family sortable with a long P gate, not span<=3.
    xs=[tuple([False]*k+[True]*(6-k)) for k in range(7)]+[(True,False,False,False,False,False)]
    assert sorts(xs,[[(0,5)],[]])
    assert ending(profiles(xs))[0] is None
    boundary=[(a,b) for a in range(-3,0) for b in range(3) if b-a<=3]
    counts={k:sum(len({v for e in es for v in e})==2*k for es in itertools.combinations(boundary,k)) for k in range(4)}
    assert counts=={0:1,1:6,2:7,3:1}
    n=10000
    mode=[{j:FREE for j in range(max(0,c-3),min(n,c+4))} for c in range(n)]
    pair,stats=ending(mode);assert pair is not None
    assert stats['max_boundary_states']<=30 and stats['states']<=30*n and stats['transitions']<=240*n
    for layer in pair:
        assert len({v for e in layer for v in e})==2*len(layer)
    report=dict(status='VERIFIED',uses_sat=False,actual_prefix_comparisons=reports,accepted=accepted,rejected=rejected,
                scope_counterexample={'n':6,'states':xs,'arbitrary_ending':[[(0,5)],[]],'bounded_span_rejected':True},
                crossing_matching_counts=counts,large_free_profile_control={'n':n,**stats},
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                algorithm_sha256=hashlib.sha256((HERE/'d13_feedback_round9_data_dp.py').read_bytes()).hexdigest(),
                proof_sha256=hashlib.sha256((HERE/'d13_feedback_round9_data_ending.md').read_bytes()).hexdigest(),
                seconds=time.monotonic()-start)
    (HERE/'results/d13-feedback-round9-data-dp-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='scope_counterexample'},indent=2))


if __name__=='__main__':main()
