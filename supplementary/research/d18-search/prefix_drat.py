#!/usr/bin/env python3
"""Export and independently check an exact fixed-prefix UNSAT proof."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

import netsat
from pysat.solvers import Solver


class RecordingSolver:
    def __init__(self,name):
        self.inner=Solver(name=name,with_proof=True)
        self.clauses=[]

    def add_clause(self,clause):
        self.clauses.append(list(clause))
        self.inner.add_clause(clause)

    def __getattr__(self,name):
        return getattr(self.inner,name)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--result',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--checker',type=Path,required=True)
    ap.add_argument('--weights',type=int,nargs='+')
    args=ap.parse_args()
    original=json.loads(args.result.read_text())
    prefix,n=original['prefix'],len(original['output_permutation'])
    universe=sorted(x for x in netsat.prefix_images(n,prefix) if not netsat.is_sorted(x,n))
    args.out.mkdir(parents=True,exist_ok=True)
    netsat.Solver=RecordingSolver
    m=netsat.Model(n,original['depth']-len(prefix),universe)
    groups=[]
    for x in universe:
        if args.weights and x.bit_count() not in args.weights:
            continue
        begin=len(m.S.clauses)
        m.add_input(x)
        groups.append(dict(input=x,weight=x.bit_count(),clause_begin=begin,clause_end=len(m.S.clauses)))
    cnf=args.out/'problem.cnf'
    with cnf.open('w') as f:
        f.write(f'p cnf {m.nv} {len(m.S.clauses)}\n')
        for c in m.S.clauses:
            f.write(' '.join(map(str,c))+' 0\n')
    (args.out/'groups.json').write_text(json.dumps(groups)+'\n')
    result=dict(case_id=original['case_id'],n=n,depth=original['depth'],prefix=prefix,
                weights=args.weights or list(range(1,n)),inputs=len(groups),
                variables=m.nv,clauses=len(m.S.clauses),cnf_sha256=sha(cnf),
                encoder_sha256=sha(Path(netsat.__file__)),source_sha256=sha(Path(__file__)),
                checker_sha256=sha(args.checker),independently_proof_checked=False,status='BUILT')
    def save():
        (args.out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    save()
    print('BUILT',len(groups),m.nv,len(m.S.clauses),flush=True)
    try:
        started=time.monotonic()
        ok=m.S.solve()
        result.update(status='SAT' if ok else 'UNSAT',solve_seconds=round(time.monotonic()-started,3))
        if ok:
            result['network']=prefix+m.network(m.S.get_model())
            assert all(netsat.is_sorted(netsat.apply_layers(result['network'][len(prefix):],x),n)
                       for x in universe if not args.weights or x.bit_count() in args.weights)
        else:
            proof=args.out/'proof.drat'
            proof.write_text('\n'.join(m.S.get_proof())+'\n')
            result['proof_sha256']=sha(proof)
            save()
            started=time.monotonic()
            command=[str(args.checker.resolve()),str(cnf.resolve()),str(proof.resolve()),
                     '-c',str((args.out/'core.cnf').resolve()),'-t','120']
            check=subprocess.run(command,capture_output=True,text=True,timeout=130)
            (args.out/'check.log').write_text(check.stdout+check.stderr)
            result.update(check_seconds=round(time.monotonic()-started,3),checker_returncode=check.returncode,
                          independently_proof_checked=check.returncode==0 and 's VERIFIED' in check.stdout)
            assert result['independently_proof_checked'],check.stdout[-2000:]+check.stderr
        save()
        print(json.dumps({k:v for k,v in result.items() if k not in ('network','prefix')}),flush=True)
    finally:
        m.S.delete()


if __name__=='__main__':
    main()
