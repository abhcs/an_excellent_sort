#!/usr/bin/env python3
"""batch.py CLASSES.json OUT.jsonl --n N --depth D --a A [--capped C] [--workers W] [--limit SEC]
Runs thinsat.py on every second-layer class (prefix L1;L2) in parallel, one process per case with a
hard wall-clock limit (the process is killed).  Appends one JSON line per finished case; cases already
present in OUT.jsonl with a terminal status (UNSAT/FOUND) are skipped, so the batch can be resumed."""
import argparse, concurrent.futures as cf, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))


def run_case(idx, l2, args):
    cmd = [sys.executable, os.path.join(HERE, 'thinsat.py'), str(args.n), str(args.depth), str(args.a),
           '--l2', json.dumps(l2), '--capped', str(args.capped), '--solver', args.solver]
    if args.dump_dir:
        cmd += ['--dump', os.path.join(args.dump_dir, f'case{idx}.cnf')]
    t = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=args.limit)
        out = p.stdout
        status = 'UNSAT' if 'UNSAT' in out else ('FOUND' if 'FOUND' in out else f'ERROR rc={p.returncode}')
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b'').decode() if isinstance(e.stdout, bytes) else (e.stdout or '')
        status = 'TIMEOUT'
    last = [l for l in out.splitlines() if l.strip()][-1:] 
    return {'case': idx, 'l2': l2, 'status': status, 'seconds': round(time.time() - t, 1),
            'last_line': last[0][:400] if last else '', 'n': args.n, 'depth': args.depth, 'a': args.a,
            'capped': args.capped, 'solver': args.solver, 'limit': args.limit}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('classes'); ap.add_argument('out')
    ap.add_argument('--n', type=int, required=True); ap.add_argument('--depth', type=int, required=True)
    ap.add_argument('--a', type=int, required=True); ap.add_argument('--capped', type=int, default=2)
    ap.add_argument('--workers', type=int, default=4); ap.add_argument('--limit', type=float, default=600)
    ap.add_argument('--solver', default='cadical195'); ap.add_argument('--order', default='size-asc')
    ap.add_argument('--only', default=None, help='comma-separated case indices')
    ap.add_argument('--dump-dir', default=None, help='write each UNSAT case CNF to DIR/case<i>.cnf')
    args = ap.parse_args()
    reps = json.load(open(args.classes))['reps']
    done = set()
    if os.path.exists(args.out):
        for line in open(args.out):
            r = json.loads(line)
            if r['status'] in ('UNSAT', 'FOUND'):
                done.add(r['case'])
    todo = [i for i in range(len(reps)) if i not in done]
    if args.only:
        keep = {int(x) for x in args.only.split(',')}
        todo = [i for i in todo if i in keep]
    if args.order == 'size-desc':
        todo.sort(key=lambda i: -len(reps[i]))
    print(f'{len(todo)} cases to run, {len(done)} already terminal', flush=True)
    with cf.ThreadPoolExecutor(args.workers) as ex, open(args.out, 'a') as f:
        futs = {ex.submit(run_case, i, reps[i], args): i for i in todo}
        for fu in cf.as_completed(futs):
            r = fu.result()
            f.write(json.dumps(r) + '\n'); f.flush()
            print(f"case {r['case']} |L2|={len(r['l2'])} {r['status']} {r['seconds']}s", flush=True)


if __name__ == '__main__':
    main()
