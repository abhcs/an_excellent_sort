#!/usr/bin/env python3
"""Export a reduced group formula or check an existing defect certificate."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
from pysat.formula import CNF
from pysat.solvers import Solver


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--certificate',type=Path,required=True)
    ap.add_argument('--selected',type=Path)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--checker',type=Path,required=True)
    args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    result=dict(independently_proof_checked=False)
    cert=args.certificate
    if args.selected:
        raw=CNF(from_file=str(cert/'problem.cnf'))
        groups=json.loads((cert/'groups.json').read_text())
        selected=json.loads(args.selected.read_text())['selected']
        omit={i for g in groups if g['index'] not in selected for i in range(g['begin'],g['end'])}
        clauses=[c for i,c in enumerate(raw.clauses) if i not in omit]
        cert=args.out
        problem=cert/'problem.cnf'
        problem.write_text(f'p cnf {raw.nv} {len(clauses)}\n'+''.join(' '.join(map(str,c))+' 0\n' for c in clauses))
        started=time.monotonic()
        with Solver(name='cadical195',bootstrap_with=clauses,with_proof=True) as solver:
            assert not solver.solve()
            (cert/'proof.drat').write_text('\n'.join(solver.get_proof())+'\n')
        result.update(selected=selected,clauses=len(clauses),solve_seconds=round(time.monotonic()-started,4))
    started=time.monotonic()
    cmd=[str(args.checker),str(cert/'problem.cnf'),str(cert/'proof.drat'),'-c',str(args.out/'core.cnf'),'-t','100']
    checked=subprocess.run(cmd,capture_output=True,text=True,timeout=110)
    (args.out/'check.log').write_text(checked.stdout+checked.stderr)
    result.update(check_seconds=round(time.monotonic()-started,4),returncode=checked.returncode,
                  independently_proof_checked=checked.returncode==0 and 's VERIFIED' in checked.stdout,
                  cnf_sha256=digest(cert/'problem.cnf'),proof_sha256=digest(cert/'proof.drat'),
                  checker_sha256=digest(args.checker),source_sha256=digest(Path(__file__)))
    (args.out/'certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
