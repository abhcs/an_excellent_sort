#!/usr/bin/env python3
"""Audit direct signed-family embeddings in all609 two-layer D17 covers."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import time
from two_layer_cover import half_blind_family,type_step

ROOT=Path(__file__).parent


def signature(states,coordinates):
    return sorted((sum(s[v]<0 for v in coordinates),sum(s[v]>0 for v in coordinates)) for s in states)


def main():
    start=time.monotonic();source=ROOT/'results/d17-feedback-fourteen-hand606-states.json'
    reference=json.loads(source.read_text());base=[tuple(s[2:]) for s in reference['states']]
    sig=signature(base,range(12));flipped=sorted((b,a) for a,b in sig)
    cover=ROOT/'prefixes/complete17.jsonl';cases=[json.loads(s) for s in cover.read_text().splitlines()]
    records=[];hist=Counter()
    for case in cases:
        states=[type_step(s,case['layers'][1]) for s in half_blind_family(17,case['layers']).values()]
        assert len(states)==case['half_blind_sets'] and len(set(states))==len(states)
        record=dict(case_id=case['case_id'],states=len(states))
        if len(states)<20:
            record['result']='TOO_FEW_DISTINCT_STATES'
        else:
            assert len(states)==20
            variable=[v for v in range(17) if len({s[v] for s in states})>1]
            record['variable_coordinates']=variable
            if len(variable)!=12:record['result']='WRONG_VARIABLE_COUNT'
            elif signature(states,variable) not in (sig,flipped):
                record['result']='WRONG_SIGN_COUNT_MULTISET'
                record['variable_sign_counts']=dict((str(k),v) for k,v in Counter(signature(states,variable)).items())
            else:
                mapping=reference['compact_to_original'][2:]
                assert set(mapping)==set(variable)
                assert {tuple(s[v] for v in mapping) for s in states}==set(base)
                record['result']='EXACT_EMBEDDING'
                record['base12_to_original']=mapping
                record['common_reals']=[v for v in range(17) if all(s[v]==0 for s in states)]
                record['fixed_sentinels']={v:states[0][v] for v in range(17)
                                           if v not in variable and states[0][v]!=0}
        hist[record['result']]+=1;records.append(record)
    assert hist=={'TOO_FEW_DISTINCT_STATES':606,'EXACT_EMBEDDING':1,
                  'WRONG_VARIABLE_COUNT':1,'WRONG_SIGN_COUNT_MULTISET':1}
    report=dict(status='VERIFIED',sat_used=False,cover_cases=len(cases),classification=dict(hist),
                cases_with_twenty_states=[r for r in records if r['states']==20],
                reference_sign_counts=dict((str(k),v) for k,v in Counter(sig).items()),
                scope='Direct embedding of this exact signed20-state family, with only fixed/common coordinates outside',
                additional_D17_cover_cases_closed=0,seconds=round(time.monotonic()-start,4),
                input_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                cover_sha256=hashlib.sha256(cover.read_bytes()).hexdigest(),
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (ROOT/'results/d17-feedback-round7-embedding.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
