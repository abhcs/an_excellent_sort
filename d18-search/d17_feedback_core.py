#!/usr/bin/env python3
"""Shrink the restriction groups of an already exported defect formula."""
import argparse
import json
from pathlib import Path
import time
from pysat.formula import CNF
from pysat.solvers import Solver


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--certificate',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    raw=CNF(from_file=str(args.certificate/'problem.cnf'))
    groups=json.loads((args.certificate/'groups.json').read_text())
    selectors={g['index']:raw.nv+1+g['index'] for g in groups}
    grouped={i:g['index'] for g in groups for i in range(g['begin'],g['end'])}
    clauses=[c+[selectors[grouped[i]]] if i in grouped else c for i,c in enumerate(raw.clauses)]
    result=dict(status='STARTED',certificate=str(args.certificate),trials=[],
                selected=[g['index'] for g in groups],minimal=False)
    def save():
        args.out.write_text(json.dumps(result,indent=2)+'\n')
    save()
    with Solver(name='cadical195',bootstrap_with=clauses) as solver:
        selected=result['selected'][:]
        started=time.monotonic()
        assert not solver.solve(assumptions=[-selectors[i] for i in selected])
        result['initial_unsat_seconds']=round(time.monotonic()-started,4)
        result['status']='UNSAT_SUBFAMILY'
        for candidate in selected[:]:
            if candidate not in selected:
                continue
            trial=[i for i in selected if i!=candidate]
            started=time.monotonic()
            ok=solver.solve(assumptions=[-selectors[i] for i in trial])
            result['trials'].append(dict(removed=candidate,satisfiable=ok,seconds=round(time.monotonic()-started,4)))
            if not ok:
                core=set(solver.get_core())
                selected=[i for i in trial if -selectors[i] in core]
            result['selected']=selected[:]
            save()
        result['minimal']=True
        result['status']='MINIMAL_UNSAT_SUBFAMILY'
        save()
        print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
