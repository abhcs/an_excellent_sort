#!/usr/bin/env python3
"""Three bounded complete-cover D13 tests; each solve/check gets30 seconds."""
import hashlib,json
from prefix_rank_route_round7_batch import run,PY,HERE,CHECKER

def main():
    records=[]
    for case in (3,56,112):
        out=HERE/'results'/f'd13-rank-capacity-round8-r{case:04}.json'
        cmd=[PY,HERE/'d13_rank_capacity_round8.py','--case',case,'--out',out,'--proof']
        rec=run(cmd,30);rec['case']=case;rec['command']=list(map(str,cmd))
        out.with_name(out.stem+'-terminal.json').write_text(json.dumps(rec,indent=2)+'\n')
        if rec.get('returncode')==0:
            d=json.loads(out.read_text());rec['result_status']=d['status']
            if d['status']=='UNSAT':
                folder=out.with_suffix('');check=run([CHECKER,folder/'problem.cnf',folder/'proof.drat'],30)
                (folder/'check.log').write_text(check.get('stdout','')+check.get('stderr',''))
                check['verified']=check.get('returncode')==0 and 's VERIFIED' in check.get('stdout','')
                check.pop('stdout',None);check.pop('stderr',None)
                check['checker_sha256']=hashlib.sha256(CHECKER.read_bytes()).hexdigest()
                (folder/'check-terminal.json').write_text(json.dumps(check,indent=2)+'\n');rec['check']=check
                if check['verified']:
                    d['independently_proof_checked']=True;d['check_seconds']=check['seconds'];d['checker_sha256']=check['checker_sha256']
                    out.write_text(json.dumps(d,indent=2)+'\n')
        records.append(rec);(HERE/'results/d13-rank-capacity-round8-batch.json').write_text(json.dumps(records,indent=2)+'\n')
        print(json.dumps({k:v for k,v in rec.items() if k not in ('stdout','stderr','command')}),flush=True)
if __name__=='__main__':main()
