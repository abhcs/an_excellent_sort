#!/usr/bin/env python3
"""Bounded exact-price feedback on the2728 zero-full-row forms."""
import gzip
import json
from pathlib import Path
import time
from d17_feedback_round8_patterns import prices
from d17_feedback_round7_screen import transport

ROOT=Path(__file__).parent


def main():
    start=time.monotonic();base=[s[2:] for s in json.loads((ROOT/'results/d17-feedback-fourteen-hand606-states.json').read_text())['states']]
    cert=json.loads(gzip.decompress((ROOT/'results/d17-feedback-round7-core-certificate.json.gz').read_bytes()))
    counts={};hard=[];examples={}
    for record in cert['cases']:
        if record['r']:continue
        code=record['m'];n=len(code);M=[(i,int(x,16)) for i,x in enumerate(code) if i<int(x,16)]
        family=[s+[0]*(n-12) for s in base]
        required={i:transport(s,M) for i,s in enumerate(family) if sum(s[a]==s[b]==0 for a,b in M)<n//2-3}
        q,cost,target=prices(list(required.values()))
        kind='STRICT' if cost<target else 'EQUALITY' if cost==target else 'GAP'
        counts[kind]=counts.get(kind,0)+1
        examples.setdefault(kind,dict(code=code,required=list(required),prices=q,cost=cost,target=target))
        if kind!='STRICT':hard.append(dict(code=code,kind=kind,required=list(required),cost=cost,target=target))
    report=dict(status='COMPLETED_FEEDBACK',sat_used=False,cases=sum(counts.values()),counts=counts,
                examples=examples,hard=hard,seconds=round(time.monotonic()-start,4))
    (ROOT/'results/d17-feedback-round8-price-screen.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='hard'},indent=2))


if __name__=='__main__':main()
