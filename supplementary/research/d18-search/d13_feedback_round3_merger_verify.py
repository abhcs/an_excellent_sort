#!/usr/bin/env python3
"""Local combinatorial audit and bounded proof checks for the311/441 lemmas."""
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import time

HERE=Path(__file__).resolve().parent


def partitions(total,maximum):
    if total==0:
        yield ()
        return
    for first in range(min(total,maximum),0,-1):
        for rest in partitions(total-first,first):yield(first,)+rest


def pack(parts,capacities):
    if not parts:return not any(capacities)
    x,*rest=parts
    return any(pack(rest,capacities[:i]+(left-x,)+capacities[i+1:])
               for i,left in enumerate(capacities) if left>=x)


def main():
    median_witnesses={}
    for p in itertools.permutations(range(5)):
        if list(p[:3])==sorted(p[:3]) and list(p[3:])==sorted(p[3:]):
            median_witnesses.setdefault(p.index(2),p)
    assert set(median_witnesses)==set(range(5))
    signs=[]
    for a,b in itertools.permutations(range(3),2):
        remaining=next(v for v in range(3) if v not in (a,b))
        values=[0]*5
        for v in (a,b):values[v]=-1 if v<remaining else 1
        assert values[:3]==sorted(values[:3])
        before=values[:]
        layer=[(a,3),(b,4)]
        assert all(not(values[x]==values[y]==0) for x,y in layer)
        for x,y in layer:values[x],values[y]=min(values[x],values[y]),max(values[x],values[y])
        assert values.count(0)==3
        signs.append(dict(first_layer=layer,initial=before,remaining_triple_position=remaining))
    checked=list(partitions(9,4))
    assert all(any(pack(p,target) for target in ((4,3,2),(3,3,3),(4,4,1))) for p in checked)
    assert [p for p in checked if not pack(p,(4,3,2))]==[(4,4,1),(3,3,3)]
    checks=[]
    for name in ('441','311'):
        path=HERE/f'results/d13_feedback_round3-merger{name}-bare.json'
        result=json.loads(path.read_text());directory=Path(result['certificate_directory'])
        if not directory.is_absolute():directory=HERE.parent/directory
        start=time.monotonic()
        command=['/private/tmp/d18-structural-drat-trim/drat-trim',str(directory/'problem.cnf'),str(directory/'proof.drat'),'-t','30']
        try:
            call=subprocess.run(command,capture_output=True,text=True,timeout=30)
            log=call.stdout+call.stderr;(directory/'check.log').write_text(log)
            record=dict(terminal='EXITED',returncode=call.returncode,wall_cap_seconds=30,
                        seconds=time.monotonic()-start,verified=call.returncode==0 and 's VERIFIED' in log)
        except subprocess.TimeoutExpired:
            record=dict(terminal='TIMEOUT_KILLED',wall_cap_seconds=30,seconds=time.monotonic()-start,verified=False)
        (directory/'check-terminal.json').write_text(json.dumps(record,indent=2)+'\n')
        if record['verified']:
            result.update(status='UNSAT_VERIFIED',independently_proof_checked=True,check_seconds=record['seconds'])
            path.write_text(json.dumps(result,indent=2)+'\n')
        checks.append(dict(merger=name,**record))
    report=dict(status='VERIFIED',median_position_witnesses=median_witnesses,
                singleton_triple_pairings=signs,partitions_checked=len(checked),partitions=checked,
                small_drat_checks=checks,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (HERE/'results/d13_feedback_round3-merger-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
