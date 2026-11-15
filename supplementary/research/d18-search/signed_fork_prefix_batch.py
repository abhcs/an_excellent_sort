#!/usr/bin/env python3
"""Bounded fixed-prefix audit of the signed-fork criterion; no SAT."""
import hashlib
import json
from pathlib import Path
import time
from signed_fork_prefix import blind_states, recognize, certificate

ROOT=Path(__file__).parent


def main():
    start=time.monotonic()
    sources=[ROOT/'prefixes'/name for name in
             ('halves_d4.jsonl','symbeam_pb_d4.jsonl','symbeam_bz_d4.jsonl',
              'e18_3_L4.jsonl','e18_3_L4sym.jsonl')]
    sources += [ROOT/'results'/name for name in
                ('budget-counterexample18.json','combined-prefix-probe18.json',
                 'cube-free-prefix-probe18.json')]
    prefixes={}
    for source in sources:
        if source.suffix=='.jsonl':
            records=[json.loads(line) for line in source.read_text().splitlines()]
        else:records=[json.loads(source.read_text())]
        for index,record in enumerate(records):
            if record.get('n')!=18:continue
            layers=(record.get('layers') or record.get('network'))[:4]
            if len(layers)!=4:continue
            key=tuple(tuple(tuple(edge) for edge in layer) for layer in layers)
            prefixes.setdefault(key,[]).append(dict(source=str(source.relative_to(ROOT)),index=index))
    results=[]
    for layers,origins in prefixes.items():
        row=dict(layers=layers,origins=origins,retained={})
        for reals in (7,8):
            states,counts=blind_states(18,layers,reals)
            pattern,stats=recognize(18,reals,states)
            item=dict(status='FORK_FOUND' if pattern else 'NO_EXACT_FORK',**counts,**stats)
            if pattern:item['certificate']=certificate(18,reals,layers,states,pattern)
            row['retained'][reals]=item
        results.append(row)
    summary=dict(prefixes=len(results),cut=4,
                 patterns_found=sum(item['status']=='FORK_FOUND' for row in results for item in row['retained'].values()),
                 no_seven_real_blind_state=sum(row['retained'][7]['distinct_cut_states']==0 for row in results),
                 max_seven_real_cut_states=max(row['retained'][7]['distinct_cut_states'] for row in results),
                 max_eight_real_cut_states=max(row['retained'][8]['distinct_cut_states'] for row in results),
                 seconds=round(time.monotonic()-start,4),sat_used=False,
                 scope='These fixed prefixes are samples, not a complete cover of D18 candidates')
    report=dict(summary=summary,results=results,
                sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in sources+[Path(__file__),ROOT/'signed_fork_prefix.py']})
    (ROOT/'results/signed-fork-prefix18-samples.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
