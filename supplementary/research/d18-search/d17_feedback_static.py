#!/usr/bin/env python3
"""Reproduce the 10,395-matching static audit for the case-608 family."""
import argparse
import json
from pathlib import Path
from two_layer_cover import half_blind_family, type_step


def matchings(xs):
    if not xs:
        yield []
        return
    a,*rest=xs
    for j,b in enumerate(rest):
        for tail in matchings(rest[:j]+rest[j+1:]):
            yield [(a,b)]+tail


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    cover=Path(__file__).with_name('prefixes')/'complete17.jsonl'
    case=[json.loads(x) for x in cover.read_text().splitlines()][608]
    states=[type_step(p,case['layers'][1]) for p in half_blind_family(17,case['layers']).values()]
    realsets=[{i for i,v in enumerate(s) if v==0} for s in states]
    common=set.intersection(*realsets)
    used=set.union(*realsets)
    assert common=={1,2}
    residual=sorted(used-common)
    left={4,5,6,7,8}
    right=set(residual)-left
    distribution={}
    maxima={}
    count=0
    for matching in matchings(residual):
        count+=1
        cross=sum((a in left)!=(b in left) for a,b in matching)
        near=sum(sum(a in s and b in s for a,b in matching)==3 for s in realsets)
        distribution.setdefault(cross,{})
        distribution[cross][near]=distribution[cross].get(near,0)+1
        if cross not in maxima or near>maxima[cross][0]:
            maxima[cross]=(near,matching)
    result=dict(status='EXHAUSTIVE_STATIC_MAXIMUM',common_reals=sorted(common),
                never_real=sorted(set(range(17))-used),remaining_A=sorted(left),remaining_B=sorted(right),
                perfect_matchings=count,distribution=distribution,maxima_by_cross_edges=maxima,
                maximum=max(v[0] for v in maxima.values()),
                scope='Static depth-two family only; common-pair compression and filling justify perfect matchings on twelve remaining vertices')
    assert count==10395 and result['maximum']==11
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
