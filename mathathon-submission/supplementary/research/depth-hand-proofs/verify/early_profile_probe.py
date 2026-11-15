#!/usr/bin/env python3
"""Bounded exact probes of first-two-layer caps; full free later matchings."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

CASES = [(7, 6, 3, 1), (7, 6, 2, 2), (7, 6, 2, 3),
         (8, 6, 4, 2), (8, 6, 3, 3), (8, 6, 3, 4)]


def solve(case, solver):
    from pysat.solvers import Solver
    from satnet import Encoding, sorts
    n, depth, first_cap, second_cap = case
    first = [(2*i, 2*i+1) for i in range(first_cap)]
    started = time.monotonic()
    enc = Encoding(n, depth-1, prefix=[first], caps=[second_cap]+[None]*(depth-2))
    result = dict(n=n, depth=depth, caps=[first_cap, second_cap],
                  solver=solver, variables=enc.nvars, clauses=len(enc.clauses),
                  proof_trace_checked=False,
                  encoder_sha256=hashlib.sha256(Path(__file__).with_name('satnet.py').read_bytes()).hexdigest())
    with Solver(name=solver, bootstrap_with=enc.clauses) as s:
        ok = s.solve()
        result['status'] = 'SAT' if ok else 'UNSAT'
        if ok:
            net = [first] + enc.network(s.get_model())
            assert sorts(net, n)
            result.update(network=net, verified_binary_inputs=1 << n)
    result['seconds'] = time.monotonic()-started
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', type=int)
    parser.add_argument('--seconds', type=float, default=30)
    parser.add_argument('--solver', default='cadical195')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--worker', action='store_true')
    args = parser.parse_args()
    if args.worker:
        result = solve(CASES[args.case], args.solver)
        args.out.write_text(json.dumps(result, indent=2)+'\n')
        return
    args.out.mkdir(exist_ok=True, parents=True)
    records = []
    for i in range(len(CASES)) if args.case is None else [args.case]:
        destination = args.out / f'case-{i}.json'
        assert not destination.exists(), 'Use a fresh output directory.'
        cmd = [sys.executable, str(Path(__file__).resolve()), '--worker', '--case', str(i),
               '--solver', args.solver, '--out', str(destination)]
        start = time.monotonic()
        try:
            subprocess.run(cmd, timeout=args.seconds, check=True)
            result = json.loads(destination.read_text())
        except subprocess.TimeoutExpired:
            result = dict(case=CASES[i], status='TIME_LIMIT', seconds=time.monotonic()-start)
            destination.write_text(json.dumps(result, indent=2)+'\n')
        records.append(result)
        print(json.dumps({k:v for k,v in result.items() if k!='network'}), flush=True)
    (args.out/'audit.json').write_text(json.dumps(dict(cases=records,
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n')


if __name__ == '__main__':
    main()
