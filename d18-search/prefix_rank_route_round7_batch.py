#!/usr/bin/env python3
"""Bounded round-seven routing comparisons; terminal records are authoritative."""
import hashlib,json,subprocess,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
PY=Path('/Users/abhishek/Documents/an_excellent_sort/depth-hand-proofs/verify/.venv/bin/python')
CHECKER=Path('/private/tmp/d18-structural-drat-trim/drat-trim')

def run(cmd,cap):
    started=time.monotonic()
    try:
        r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True,timeout=cap)
        return dict(terminal='EXITED',returncode=r.returncode,stdout=r.stdout,stderr=r.stderr,
                    seconds=time.monotonic()-started,wall_cap_seconds=cap)
    except subprocess.TimeoutExpired as exc:
        return dict(terminal='TIMEOUT_KILLED',seconds=time.monotonic()-started,
                    wall_cap_seconds=cap,stdout=(exc.stdout or b'').decode(),stderr=(exc.stderr or b'').decode())

def main():
    records=[]
    for control in (True,False):
        for normal in (False,True):
            for name in (('control',) if control else ('beam00','beam16')):
                label=('normal' if normal else 'arbitrary')+'-'+name
                out=HERE/'results'/('prefix-rank-route-round7-'+label+'.json')
                seed=HERE/'results'/('prefix-rank-round6-control-p6-c9-seed.json' if control else 'prefix-rank-round6-p4-'+name+'-seed.json')
                cmd=[PY,HERE/'prefix_rank_route_round7.py','--seed',seed,'--depth',11 if control else 10,'--cut',9 if control else 8,'--out',out]
                if normal:cmd+=['--normal']
                if control:cmd+=['--witness',HERE/'results/dobbelaere18-78-11.json']
                rec=run(cmd,30)
                rec['label']=label
                out.with_name(out.stem+'-terminal.json').write_text(json.dumps(rec,indent=2)+'\n')
                if rec['terminal']=='EXITED' and rec['returncode']==0:
                    d=json.loads(out.read_text());rec['result_status']=d['status']
                    if d['status']=='UNSAT_UNCHECKED':
                        folder=out.with_suffix('')
                        check=run([CHECKER,folder/'problem.cnf',folder/'proof.drat'],30)
                        verified=check.get('returncode')==0 and 's VERIFIED' in check.get('stdout','')
                        (folder/'check.log').write_text(check.get('stdout','')+check.get('stderr',''))
                        check.pop('stdout',None);check.pop('stderr',None);check['verified']=verified
                        check['checker_sha256']=hashlib.sha256(CHECKER.read_bytes()).hexdigest()
                        (folder/'check-terminal.json').write_text(json.dumps(check,indent=2)+'\n')
                        rec['check']=check
                if control:assert rec.get('result_status')=='SURVIVOR',rec
                records.append(rec)
                (HERE/'results/prefix-rank-route-round7-batch.json').write_text(json.dumps(records,indent=2)+'\n')
                print(json.dumps({k:v for k,v in rec.items() if k not in ('stdout','stderr')}),flush=True)
if __name__=='__main__':main()
