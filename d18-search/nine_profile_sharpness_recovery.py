#!/usr/bin/env python3
"""Positive controls for the sharp first-two-layer counts (3,4) and (4,3)."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import netsat
from pysat.card import CardEnc, EncType
from d17_second_recovery_exact import bounded

ROOT = Path(__file__).resolve().parent


def worker(profile, out):
    a, b = map(int, profile)
    prefix = [[(2*i, 2*i+1) for i in range(a)]]
    inputs = sorted(x for x in netsat.prefix_images(9, prefix)
                    if not netsat.is_sorted(x, 9))
    model = netsat.Model(9, 6, inputs, nored0=False)
    try:
        for x in inputs:
            model.add_input(x)
        exact = CardEnc.equals(list(model.g[0].values()), b,
                               top_id=model.nv, encoding=EncType.seqcounter)
        model.nv = max(model.nv, exact.nv)
        for clause in exact.clauses:
            model.add(clause)
        started = time.monotonic()
        sat = model.S.solve()
        result = {'profile': [a,b], 'n': 9, 'depth': 7,
                  'solve_seconds': time.monotonic()-started,
                  'status': 'SAT' if sat else 'UNSAT_UNCHECKED',
                  'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        if sat:
            network = prefix + model.network(model.S.get_model())
            assert len(network) == 7 and [len(layer) for layer in network[:2]] == [a,b]
            for mask in range(512):
                values = [(mask>>i)&1 for i in range(9)]
                for layer in network:
                    used = set()
                    for i,j in layer:
                        assert 0 <= i < j < 9 and i not in used and j not in used
                        used.update((i,j))
                        values[i],values[j] = min(values[i],values[j]),max(values[i],values[j])
                assert values == sorted(values)
            result.update(network=network, direct_binary_runs=512)
        out.write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result),flush=True)
    finally:
        model.S.delete()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', choices=('34','43'))
    parser.add_argument('--out',type=Path)
    args = parser.parse_args()
    if args.worker:
        worker(args.worker,args.out)
        return
    records = []
    for profile in ('34','43'):
        directory=ROOT/f'results/nine-profile-sharpness-recovery-{profile}'
        directory.mkdir(exist_ok=False)
        output=directory/'result.json'
        terminal=bounded([sys.executable,str(Path(__file__).resolve()),'--worker',profile,
                          '--out',str(output)],10,directory/'solve.log')
        (directory/'terminal.json').write_text(json.dumps(terminal,indent=2)+'\n')
        record={'profile':profile,'terminal':terminal}
        if not terminal['timeout'] and terminal['returncode']==0:
            record['result']=json.loads(output.read_text())
        records.append(record)
    report={'scope':'Positive sorting networks; these disprove stronger universal first-two count bounds.',
            'all_jobs_terminal':True,'records':records}
    (ROOT/'results/nine-profile-sharpness-recovery.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
