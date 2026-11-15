#!/usr/bin/env python3
"""Two-layer necessary-profile screens for D(13) and D(17) prefix covers.

Every half-blind seven-real restriction must have first-two counts
(2,3), (3,2), or (3,3). SAT means only that this relaxation survives.
For D(17), H9 forces at least one four-gate layer on each nine-real
restriction; both early layers must be nonempty by D(9)>=7.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'depth-hand-proofs/verify'))
from sentinel_cegar import Master, neg, simulate
from two_layer_cover import half_blind_family, type_step
from pysat.solvers import Solver


def solve(case, solver, progress=None):
    n = case['n']
    retained, minimum, peak = {13:(7,2,3),17:(9,1,4)}[n]
    states = [type_step(p,case['layers'][1])
              for p in half_blind_family(n,case['layers']).values()]
    assert all(s.count(0)==retained for s in states)
    cnf = Master(n,3,first=0,adjacent=False,no_repeat=True)
    for a,b in case['layers'][1]:
        cnf.add(-cnf.g[1,a,b])
    for state in states:
        cur = [(v>=0,v>=1) for v in state]
        rows = []
        for t in (1,2):
            real = [cnf.conj([lo,neg(hi)]) for lo,hi in cur]
            row = [cnf.disj(cnf.conj([cnf.g[t,a,b],real[a],real[b]])
                            for b in range(a+1,n)) for a in range(n-1)]
            rows.append(row)
            cnf.add(cnf.ge(row,minimum))
            if t == 1:
                nxt = [(cnf.var(),cnf.var()) for _ in range(n)]
                for a,b in cnf.pairs:
                    for q in (0,1):
                        cnf.gate(cur[a][q],cur[b][q],nxt[a][q],nxt[b][q],cnf.g[t,a,b])
                for a in range(n):
                    for q in (0,1):
                        cnf.eq(cur[a][q],nxt[a][q],neg(cnf.used[t,a]))
                cur = nxt
        cnf.add(cnf.disj([cnf.ge(row,peak) for row in rows]))
    started = time.monotonic()
    result = dict(case_id=case['case_id'],family_size=len(states),
                  variables=cnf.pool.top,clauses=len(cnf.clauses),solver=solver,
                  scope=f'Necessary {retained}-real first-two-layer profiles only',
                  minimum=minimum, peak=peak,
                  proof_trace_checked=False)
    if progress:
        progress.write_text(json.dumps(result | {'status':'BUILT'},indent=2)+'\n')
    with Solver(name=solver,bootstrap_with=cnf.clauses) as s:
        ok = s.solve()
        result['status'] = 'SURVIVOR' if ok else 'UNSAT'
        if ok:
            layers = cnf.network(s.get_model())[1:]
            profiles = [simulate(layers,p) for p in states]
            assert all(min(p)>=minimum and max(p)==peak for p in profiles)
            assert not set(layers[0])&set(layers[1])
            assert not set(layers[0])&set(map(tuple,case['layers'][1]))
            result.update(next_layers=layers,profiles=profiles)
    result['solve_seconds'] = time.monotonic()-started
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cover',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--case',type=int)
    parser.add_argument('--seconds',type=float,default=5)
    parser.add_argument('--solver',default='cadical195')
    parser.add_argument('--min-family',type=int,default=0)
    parser.add_argument('--worker',action='store_true')
    args = parser.parse_args()
    payload = args.cover.read_bytes()
    cases = [json.loads(line) for line in payload.splitlines()]
    sha = hashlib.sha256(payload).hexdigest()
    assert sha == json.loads(args.cover.with_suffix('.summary.json').read_text())['sha256']
    if args.worker:
        result = solve(cases[args.case],args.solver,args.out.with_suffix('.progress.json'))
        result['cover_sha256'] = sha
        args.out.write_text(json.dumps(result,indent=2)+'\n')
        return
    args.out.mkdir(parents=True,exist_ok=True)
    records = []
    for index in range(len(cases)) if args.case is None else [args.case]:
        if cases[index]['half_blind_sets'] < args.min_family:
            continue
        destination = args.out / f"{cases[index]['case_id']}.json"
        assert not destination.exists(), 'Use a fresh output directory.'
        cmd = [sys.executable,str(Path(__file__).resolve()),'--worker','--cover',str(args.cover.resolve()),
               '--out',str(destination.resolve()),'--case',str(index),'--solver',args.solver]
        try:
            subprocess.run(cmd,timeout=args.seconds,check=True)
            result = json.loads(destination.read_text())
        except subprocess.TimeoutExpired:
            progress = destination.with_suffix('.progress.json')
            result = json.loads(progress.read_text()) if progress.exists() else {}
            result.update(case_id=cases[index]['case_id'],status='TIME_LIMIT',cover_sha256=sha,
                          wall_limit_seconds=args.seconds)
            destination.write_text(json.dumps(result,indent=2)+'\n')
        records.append(result)
        if result['status'] != 'SURVIVOR':
            print(json.dumps(result),flush=True)
    audit = dict(cover_sha256=sha,cases=len(records),cover_cases=len(cases),
                 statuses=dict(Counter(r['status'] for r in records)),
                 source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                 outcome='ALL_COVER_CASES_UNSAT' if len(records)==len(cases) and all(r['status']=='UNSAT' for r in records)
                 else 'ALL_SELECTED_CASES_UNSAT' if records and all(r['status']=='UNSAT' for r in records) else 'OPEN')
    (args.out/'audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit),flush=True)


if __name__ == '__main__':
    main()
