#!/usr/bin/env python3
"""Bounded certificate discovery for the third layer of 02 14 56."""
import itertools
import json
import time
from pathlib import Path
from netlib import placements, matchings
from h9_feedback_round5_probe import FIRST, SECOND, norm
from h9_feedback_reschedule_extend import prefix_state
from h9_feedback_round4_proof import propagated_order


def main():
    start = time.monotonic()
    prefix = (FIRST, SECOND)
    ordered = propagated_order(prefix)
    layers = [m for m in matchings(9) if not set(m) & ordered and
              all(sum(a not in s and b not in s for a,b in m) >= 3 for s in ({0,1},{0,6}))]
    print('deletion and order',len(layers))
    blind = {0:1,2:-1,4:1}
    layers = [m for m in layers if len(prefix_state(prefix + (m,),blind)['gates']) >= 2]
    print('blind-six',len(layers))
    p2 = list(placements(9,2))
    p3 = [p for p in placements(9,3) if len(prefix_state(prefix,p)['gates']) <= 1]
    blind_rows = [(p,5-k) for k in (3,4) for p in placements(9,k)
                  if not prefix_state(prefix,p)['gates']]
    cuts = {}
    for i,m in enumerate(layers):
        for p,demand in blind_rows:
            if len(prefix_state(prefix+(m,),p)['gates'])<demand:
                cuts.setdefault(('blind',tuple(p.items())),set()).add(i)
        for p in p2:
            r=prefix_state(prefix+(m,),p)
            if len(r['gates'])<=4 and max(r['depths'])<=2:
                cuts.setdefault(('reschedule',tuple(p.items())),set()).add(i)
        good=[]
        for p in p3:
            r=prefix_state(prefix+(m,),p)
            if len(r['gates'])<=2 and max(r['depths'])<=1:
                good.append((tuple(p.items()),frozenset(j for j,s in enumerate(r['state']) if not s)))
        for (p,r),(q,s) in itertools.combinations(good,2):
            if len(r&s)%2:
                cuts.setdefault(('odd',p,q),set()).add(i)
    target={i for i,m in enumerate(layers) if len(m)!=4 or (4,6) not in m or any(0 in e for e in m)}
    left=set(target); selected=[]
    while left:
        key=max(cuts,key=lambda k:len(cuts[k]&left))
        hit=cuts[key]&left
        assert hit, sorted(left)
        print(key,'hits',len(hit),flush=True)
        selected.append(dict(kind=key[0],placements=[dict(p) for p in key[1:]], layers=[layers[i] for i in sorted(hit)]))
        left-=hit
    report=dict(status='DISCOVERY_ONLY',initial_layers=layers,selected=selected,
                survivors=[layers[i] for i in range(len(layers)) if i not in target],elapsed_seconds=time.monotonic()-start)
    (Path(__file__).parents[1]/'results/h9-feedback-round5-reduction.json').write_text(json.dumps(report,indent=2)+'\n')
    print('DONE',len(selected),'survivors',len(report['survivors']),report['elapsed_seconds'])


if __name__=='__main__':main()
