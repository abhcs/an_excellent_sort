#!/usr/bin/env python3
"""conquer.py -- run netsat.py on many prefixes in parallel, each with a wall-clock limit.

Input: a JSON-lines file, one prefix per line ({"n":..,"layers":..}).  Each prefix becomes its own
netsat.py process (killed after --timeout seconds).  Results go to <out>.jsonl, one line per
prefix: status FOUND / UNSAT / TIMEOUT / ERROR, the time, and the network if one was found.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))


def run_one(idx, spec, args, workdir):
    if args.claim_dir:
        # Share a case list with a pool that is already running on claim_dir: skip cases it has
        # started (its run log exists) and mark ours so that its netsat.py exits at once (code 3).
        if os.path.exists(os.path.join(args.claim_dir, f'run_{idx:05d}.log')):
            return {'idx': idx, 'status': 'SKIPPED', 'time': 0, 'outputs': spec.get('outputs'),
                    'prefix': spec['layers'], 'network': None}
        open(os.path.join(args.claim_dir, f'prefix_{idx:05d}.json.claimed'), 'w').close()
    pfile = os.path.join(workdir, f'prefix_{idx:05d}.json')
    with open(pfile, 'w') as f:
        json.dump(spec, f)
    logf = os.path.join(workdir, f'run_{idx:05d}.log')
    cmd = [sys.executable, os.path.join(HERE, 'netsat.py'), '--prefix', pfile, '--depth', str(args.depth),
           '--init', str(args.init), '--solver', args.solver]
    for flag in ('sym', 'cosat', 'lex', 'full'):
        if getattr(args, flag):
            cmd.append('--' + flag)
    t0 = time.time()
    with open(logf, 'w') as lf:
        p = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT)
        try:
            rc = p.wait(timeout=args.timeout)
            status = {0: 'FOUND', 1: 'UNSAT', 3: 'SKIPPED'}.get(rc, f'ERROR{rc}')
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait()
            status = 'TIMEOUT'
    dt = time.time() - t0
    net = None
    if status == 'FOUND':
        with open(logf) as lf:
            for line in lf:
                if line.startswith('NETWORK '):
                    net = json.loads(line[len('NETWORK '):])
    return {'idx': idx, 'status': status, 'time': round(dt, 1), 'outputs': spec.get('outputs'),
            'prefix': spec['layers'], 'network': net}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--prefixes', required=True)
    ap.add_argument('--depth', type=int, required=True)
    ap.add_argument('--timeout', type=float, default=600)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--init', type=int, default=100000)
    ap.add_argument('--solver', default='cadical195')
    ap.add_argument('--sym', action='store_true')
    ap.add_argument('--cosat', action='store_true')
    ap.add_argument('--lex', action='store_true')
    ap.add_argument('--full', action='store_true')
    ap.add_argument('--out', required=True, help='results basename (writes <out>.jsonl and <out>_runs/)')
    ap.add_argument('--reverse', action='store_true', help='take the prefixes from the end of the list')
    ap.add_argument('--claim-dir', default=None,
                    help='runs dir of another pool working on the same list (see run_one)')
    args = ap.parse_args()
    specs = [json.loads(l) for l in open(args.prefixes) if l.strip()]
    workdir = args.out + '_runs'
    os.makedirs(workdir, exist_ok=True)
    counts = {}
    order = list(enumerate(specs))
    if args.reverse:
        order.reverse()
    with ThreadPoolExecutor(max_workers=args.workers) as ex, open(args.out + '.jsonl', 'a') as out:
        futs = [ex.submit(run_one, i, s, args, workdir) for i, s in order]
        for fu in futs:
            r = fu.result()
            counts[r['status']] = counts.get(r['status'], 0) + 1
            out.write(json.dumps(r) + '\n')
            out.flush()
            print(time.strftime('%H:%M:%S'), f"prefix {r['idx']}: {r['status']} in {r['time']}s "
                  f"(outputs={r['outputs']}) totals={counts}", flush=True)
            if r['status'] == 'FOUND':
                print('FOUND NETWORK', json.dumps(r['network']), flush=True)
    print('DONE', counts, flush=True)


if __name__ == '__main__':
    main()
