#!/usr/bin/env python3
"""Controlled thirty-second trials of symbolic ending-path propagation."""
import hashlib,json
from prefix_rank_route_round7_batch import run,PY,HERE,CHECKER
def main():
    records=[];results=HERE/'results'
    for label in ('positive4','negative4','positive18','beam00','beam16','d13-0030','d13-0090'):
        out=results/f'matching-ending-round10-{label}.json'
        if label.startswith('d13-'):
            case=int(label[4:]);cover=HERE/'prefixes/complete13.jsonl'
            row=json.loads(cover.read_text().splitlines()[case]);depth=8
            seed=results/f'matching-ending-round10-{label}-seed.json'
            seed.write_text(json.dumps(dict(n=13,prefix=row['layers'],source_case=row,cover_sha256=hashlib.sha256(cover.read_bytes()).hexdigest()))+'\n')
        elif label.endswith('4'):
            seed=results/f'rank-triples-round9-{label}-seed.json';depth=3 if label=='positive4' else 5
        else:
            seed=results/('prefix-rank-round6-control-p6-c9-seed.json' if label=='positive18' else f'prefix-rank-round6-p4-{label}-seed.json')
            depth=11 if label=='positive18' else 10
        cmd=[PY,HERE/'prefix_matching_ending_round10.py','--seed',seed,'--depth',depth,'--out',out]
        if label=='positive4':cmd+=['--witness',results/'rank-triples-round9-positive4-witness.json']
        if label=='positive18':cmd+=['--witness',results/'dobbelaere18-78-11.json']
        rec=run(cmd,30);rec['label']=label;rec['command']=list(map(str,cmd))
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
        if label.startswith('positive'):assert rec.get('result_status')=='SORTER',rec
        if label=='negative4':assert rec.get('check',{}).get('verified'),rec
        records.append(rec);(results/'matching-ending-round10-batch.json').write_text(json.dumps(records,indent=2)+'\n')
        print(json.dumps({k:v for k,v in rec.items() if k not in ('stdout','stderr','command')}),flush=True)
if __name__=='__main__':main()
