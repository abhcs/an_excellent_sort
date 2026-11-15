#!/usr/bin/env python3
"""Bounded first comparisons for the block-capacity encoding."""
import hashlib,json
from pathlib import Path
from prefix_rank_route_round7_batch import run,PY,HERE,CHECKER

def main():
    records=[]
    for name in ('control','beam00','beam16'):
        control=name=='control';out=HERE/'results'/f'rank-capacity-round8-{name}.json'
        seed=HERE/'results'/('prefix-rank-round6-control-p6-c9-seed.json' if control else f'prefix-rank-round6-p4-{name}-seed.json')
        cmd=[PY,HERE/'prefix_rank_capacity_round8.py','--seed',seed,'--depth',11 if control else 10,'--cut',9 if control else 8,'--out',out]
        if control:cmd+=['--witness',HERE/'results/dobbelaere18-78-11.json']
        rec=run(cmd,30);rec['label']=name;rec['command']=list(map(str,cmd))
        out.with_name(out.stem+'-terminal.json').write_text(json.dumps(rec,indent=2)+'\n')
        if rec.get('returncode')==0:
            d=json.loads(out.read_text());rec['result_status']=d['status']
            if d['status']=='UNSAT_UNCHECKED':
                folder=out.with_suffix('');check=run([CHECKER,folder/'problem.cnf',folder/'proof.drat'],30)
                (folder/'check.log').write_text(check.get('stdout','')+check.get('stderr',''))
                check['verified']=check.get('returncode')==0 and 's VERIFIED' in check.get('stdout','')
                check.pop('stdout',None);check.pop('stderr',None)
                check['checker_sha256']=hashlib.sha256(CHECKER.read_bytes()).hexdigest()
                (folder/'check-terminal.json').write_text(json.dumps(check,indent=2)+'\n');rec['check']=check
        if control:assert rec.get('result_status')=='SURVIVOR',rec
        records.append(rec);(HERE/'results/rank-capacity-round8-batch.json').write_text(json.dumps(records,indent=2)+'\n')
        print(json.dumps({k:v for k,v in rec.items() if k not in ('stdout','stderr','command')}),flush=True)
if __name__=='__main__':main()
