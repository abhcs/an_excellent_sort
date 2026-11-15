#!/usr/bin/env python3
"""Cheap cut-budget screen before testing unknown transported layers."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import time
from two_layer_cover import half_blind_family,type_step
from d17_feedback_round8_patterns import prices

ROOT=Path(__file__).parent


def main():
    start=time.monotonic();source=ROOT/'prefixes/complete17.jsonl'
    cases=[json.loads(s) for s in source.read_text().splitlines()];records=[];counts=Counter()
    for case in cases:
        states=[type_step(s,case['layers'][1]) for s in half_blind_family(17,case['layers']).values()]
        real=[{v for v,x in enumerate(s) if x==0} for s in states];assert all(len(R)==9 for R in real)
        q,cost,_=prices(real);target=8*len(real)
        variable=[v for v in range(17) if len({s[v] for s in states})>1]
        commonreal=[v for v in range(17) if all(s[v]==0 for s in states)]
        kind='STATIC_ONE_LAYER_IMPOSSIBLE' if cost<target else 'NO_STRICT_STATIC_BOUND'
        counts[kind]+=1
        records.append(dict(case_id=case['case_id'],family_size=len(states),variable_coordinates=len(variable),
                            common_reals=len(commonreal),result=kind,doubled_vertex_prices=q,
                            doubled_price_total=cost,doubled_internal_edge_demand=target))
    report=dict(status='VERIFIED_PRICE_INEQUALITIES',sat_used=False,cover_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                classifications=dict(counts),records=records,seconds=round(time.monotonic()-start,4),
                scope='Static single-layer RR-maximum only; not a two-layer obstruction or a prefix exclusion')
    (ROOT/'results/d17-feedback-round9-static.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2))
    for r in records:
        if r['family_size']>=12:print(json.dumps(r))


if __name__=='__main__':main()
