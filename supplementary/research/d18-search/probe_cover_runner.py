#!/usr/bin/env python3
"""Bounded probe-frontier tests for named complete-cover cases.

Builds a relabelled prefix seed without running a full sorting SAT problem.
Every child has a wall limit; TIME_LIMIT is never an UNSAT result.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

from cover_solve import relabel_prefix
from netsat import prefix_images
from relabel import relabel_vec


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cover',type=Path,required=True)
    ap.add_argument('--depth',type=int,required=True)
    ap.add_argument('--case',required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--seconds',type=float,default=180)
    ap.add_argument('--checker',type=Path)
    args=ap.parse_args()
    payload=args.cover.read_bytes()
    digest=hashlib.sha256(payload).hexdigest()
    assert digest==json.loads(args.cover.with_suffix('.summary.json').read_text())['sha256']
    cases=[json.loads(line) for line in payload.splitlines()]
    case=next(c for c in cases if c['case_id']==args.case)
    args.out.mkdir(parents=True,exist_ok=True)
    assert not (args.out/'result.json').exists(),'Choose a fresh output directory.'
    original=prefix_images(case['n'],case['layers'])
    prefix,lab,mapping,before,after=relabel_prefix(case['n'],case['layers'],original,200)
    assert {relabel_vec(x,mapping,case['n']) for x in original}==prefix_images(case['n'],prefix)
    seed=dict(case_id=case['case_id'],n=case['n'],depth=args.depth,prefix=prefix,
              input_permutation=lab,output_permutation=mapping,cover_sha256=digest,
              source_case=case,original_window_cost=before,window_cost=after)
    seed_path=args.out/'seed.json'
    seed_path.write_text(json.dumps(seed,indent=2)+'\n')
    result_path=args.out/'result.json'
    command=[sys.executable,str(Path(__file__).with_name('probe_frontier.py')),
             '--result',str(seed_path),'--out',str(result_path),
             '--cut',str(args.depth-2),'--both','--route']
    if args.checker:
        command+=['--checker',str(args.checker)]
    started=time.monotonic()
    print('START',args.case,'depth',args.depth,'limit',args.seconds,flush=True)
    status=None
    with (args.out/'run.log').open('w') as log:
        try:
            run=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=args.seconds)
            if run.returncode:
                status='ERROR'
        except subprocess.TimeoutExpired:
            status='TIME_LIMIT'
    result=json.loads(result_path.read_text()) if result_path.exists() else {}
    if status:
        result['status']=status
    result.update(case_id=case['case_id'],cover_sha256=digest,
                  wall_limit_seconds=args.seconds,wall_seconds=round(time.monotonic()-started,3))
    result_path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('prefix','free_layers','supports','ending_matchings')}),flush=True)


if __name__=='__main__':
    main()
