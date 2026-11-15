#!/usr/bin/env python3
"""Exact-endpoint/triple controls, then bounded D18 and new D13 cases."""
import hashlib,json
from prefix_rank_route_round7_batch import run,PY,HERE,CHECKER

def main():
    results=HERE/'results';records=[]
    good=[[[0,1],[2,3]],[[0,2],[1,3]],[[1,2]]]
    for label,prefix in [('positive4',good[:1]),('negative4',[[[0,3]],[[1,3]],[[2,3]]])]:
        (results/f'rank-triples-round9-{label}-seed.json').write_text(json.dumps(dict(n=4,prefix=prefix))+'\n')
    witness=results/'rank-triples-round9-positive4-witness.json'
    witness.write_text(json.dumps(dict(n=4,layers=good))+'\n')
    for label in ('positive4','negative4','positive18','beam00','beam16','d13-0004','d13-0055','d13-0111'):
        out=results/f'rank-triples-round9-{label}.json'
        if label.startswith('d13-'):
            cmd=[PY,HERE/'d13_rank_triples_round9.py','--case',int(label[4:]),'--out',out,'--proof']
        else:
            if label.endswith('4'):
                seed=results/f'rank-triples-round9-{label}-seed.json'
                depth,cut=(3,1) if label=='positive4' else (5,3)
            else:
                seed=results/('prefix-rank-round6-control-p6-c9-seed.json' if label=='positive18' else f'prefix-rank-round6-p4-{label}-seed.json')
                depth,cut=(11,9) if label=='positive18' else (10,8)
            cmd=[PY,HERE/'prefix_rank_triples_round9.py','--seed',seed,'--depth',depth,'--cut',cut,'--out',out]
            if label=='positive4':cmd+=['--witness',witness]
            if label=='positive18':cmd+=['--witness',results/'dobbelaere18-78-11.json']
        rec=run(cmd,30);rec['label']=label;rec['command']=list(map(str,cmd))
        out.with_name(out.stem+'-terminal.json').write_text(json.dumps(rec,indent=2)+'\n')
        if rec.get('returncode')==0:
            d=json.loads(out.read_text());rec['result_status']=d['status']
            if d['status'] in ('UNSAT','UNSAT_UNCHECKED'):
                folder=out.with_suffix('');check=run([CHECKER,folder/'problem.cnf',folder/'proof.drat'],30)
                (folder/'check.log').write_text(check.get('stdout','')+check.get('stderr',''))
                check['verified']=check.get('returncode')==0 and 's VERIFIED' in check.get('stdout','')
                check.pop('stdout',None);check.pop('stderr',None)
                check['checker_sha256']=hashlib.sha256(CHECKER.read_bytes()).hexdigest()
                (folder/'check-terminal.json').write_text(json.dumps(check,indent=2)+'\n');rec['check']=check
                if check['verified']:
                    d['independently_proof_checked']=True;d['check_seconds']=check['seconds'];d['checker_sha256']=check['checker_sha256']
                    out.write_text(json.dumps(d,indent=2)+'\n')
        if label.startswith('positive'):assert rec.get('result_status')=='SURVIVOR',rec
        if label=='negative4':assert rec.get('check',{}).get('verified'),rec
        records.append(rec);(results/'rank-triples-round9-batch.json').write_text(json.dumps(records,indent=2)+'\n')
        print(json.dumps({k:v for k,v in rec.items() if k not in ('stdout','stderr','command')}),flush=True)

if __name__=='__main__':main()
