#!/usr/bin/env python3
"""Exact static maximum of near-full half-blind restrictions in one matching.

This does not refute a sorting-network prefix. A peak is four retained gates
on a nine-real restriction. The states are fixed at the depth-two cut.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

from two_layer_cover import half_blind_family, type_step
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'depth-hand-proofs/verify'))
from sentinel_cegar import CNF
from pysat.solvers import Solver


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--case', type=int, default=608)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--solver', default='cadical195')
    args = ap.parse_args()
    started = time.monotonic()
    cover = Path(__file__).with_name('prefixes') / 'complete17.jsonl'
    case = [json.loads(x) for x in cover.read_text().splitlines()][args.case]
    states = [type_step(p, case['layers'][1])
              for p in half_blind_family(17, case['layers']).values()]
    cnf = CNF()
    gates = {(a,b): cnf.var() for a in range(17) for b in range(a+1,17)}
    for a in range(17):
        inc = [v for edge,v in gates.items() if a in edge]
        for i,u in enumerate(inc):
            for v in inc[i+1:]:
                cnf.add(-u,-v)
    peaks = []
    for state in states:
        peaks.append(cnf.ge([g for (a,b),g in gates.items() if state[a] == state[b] == 0],4))
    thresholds = [cnf.ge(peaks,k) for k in range(1,len(states)+1)]
    result = dict(case_id=case['case_id'],states=states,
                  cover_sha256=hashlib.sha256(cover.read_bytes()).hexdigest(),
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope='Maximum number of nine-real states near-fully paired at the depth-two cut',
                  variables=cnf.pool.top,clauses=len(cnf.clauses),status='BUILT',trials=[])
    args.out.parent.mkdir(parents=True,exist_ok=True)
    def save():
        args.out.write_text(json.dumps(result,indent=2)+'\n')
    save()
    with Solver(name=args.solver,bootstrap_with=cnf.clauses) as solver:
        low,high=0,len(states)+1
        while high>low+1:
            k=(low+high)//2
            start=time.monotonic()
            ok=solver.solve(assumptions=[thresholds[k-1]])
            result['trials'].append(dict(at_least=k,satisfiable=ok,seconds=round(time.monotonic()-start,4)))
            if ok:
                model=set(solver.get_model())
                layer=[edge for edge,g in gates.items() if g in model]
                counts=[sum(s[a]==s[b]==0 for a,b in layer) for s in states]
                assert sum(x==4 for x in counts)>=k
                low=sum(x==4 for x in counts)
                result.update(witness_matching=layer,witness_counts=counts,lower_bound=low)
            else:
                high=k
                result['upper_bound']=k-1
            save()
        result.update(status='MAXIMUM_COMPUTED',maximum=low,
                      independently_proof_checked=False,seconds=round(time.monotonic()-started,4))
        save()
        print(json.dumps({k:v for k,v in result.items() if k not in ('states',)}),flush=True)


if __name__ == '__main__':
    main()
