#!/usr/bin/env python3
"""Feedback on the one-cross critical perfect branch; no full network SAT."""
import collections
import itertools
import json
from pathlib import Path
import time
from d17_feedback_round3_probe import STATES,requirements,matching_core,prices
from d17_feedback_round2_verify import matchings,cores,compatible,edge,G,ASIGN

ROOT=Path(__file__).parent


def full_row_compatible(M):
    options=[]
    for row,(u,v) in enumerate(G):
        family=STATES[5*row:5*row+5]
        if any(sum(s[a]==s[b]==0 for a,b in M)>=4 for s in family):continue
        permutation=list(range(14))
        for a,b in M:
            if (a,b)==(7,10):continue
            if not all(s[a]<=s[b] for s in family):
                assert all(s[a]>=s[b] for s in family)
                permutation[a],permutation[b]=permutation[b],permutation[a]
        options.append([frozenset(edge(permutation[a],permutation[b]) for a,b in C) for C in cores(u,v)])
    possible={frozenset()}
    for opts in options:
        possible={a|b for a in possible for b in opts if compatible(a|b)}
        if not possible:return False
    return True


def canonical(rows):
    sets=[set(S) for S,indices in rows]
    vertices=sorted(set.union(*sets))
    return min(tuple(sorted(sum((1<<j) for j,i in enumerate(p) if v in sets[i]) for v in vertices))
               for p in itertools.permutations(range(len(sets))))


def main():
    started=time.monotonic();records=[];hist=collections.Counter();classes={};firsts=0
    for tail in matchings([v for v in range(14) if v not in (7,10)],perfect=True):
        M=((7,10),)+tail
        cross=[(a,b) for a,b in M if (a in ASIGN)!=(b in ASIGN) and a>=2 and b>=2 and (a>=7 or b>=7)]
        if len(cross)!=1:continue
        firsts+=1
        if not full_row_compatible(M):continue
        r=matching_core(requirements(M));assert not r['sat'],M
        strict=prices(r['core']);equality=None if strict else prices(r['core'],True)
        key=str(canonical(r['core']))
        entry=classes.setdefault(key,dict(id=len(classes),representative=r['core'],count=0,
                                         strict_price=strict,equality_price=equality))
        entry['count']+=1
        hist[(len(r['core']),strict is not None,equality is not None)]+=1
        records.append(dict(M=M,cross=cross,core=r['core'],class_id=entry['id'],strict_price=strict,equality_price=equality))
    result=dict(status='COMPLETED',scope='Tiny static matching/price feedback only',firsts=firsts,
                full_row_survivors=len(records),classes=list(classes.values()),records=records,
                counts=[dict(core_size=k[0],strict=k[1],equality=k[2],count=v) for k,v in sorted(hist.items())],
                seconds=round(time.monotonic()-started,4))
    (ROOT/'results/d17-feedback-round3-classify.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('classes','records')},indent=2))
    print(json.dumps(result['classes'],indent=2))


if __name__=='__main__':main()
