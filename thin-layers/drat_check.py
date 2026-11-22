#!/usr/bin/env python3
"""drat_check.py CNF_DIR OUT.jsonl [--workers W]: for every case<i>.cnf in CNF_DIR (dumped by
thinsat.py --dump on UNSAT), re-solve with the standalone CaDiCaL writing a DRAT proof, check the
proof with drat-trim, and record the CNF's SHA-256, both times and the verdict.  Proof files are
deleted after a successful check; the CNF is kept.  Already recorded cases are skipped."""
import argparse, concurrent.futures as cf, hashlib, json, os, re, subprocess, time

HERE = os.path.dirname(os.path.abspath(__file__))
import satcert
CADICAL = satcert.CADICAL
DRATTRIM = os.environ.get('DRATTRIM', os.path.join(HERE, '..', 'build', 'drat-trim', 'drat-trim'))


def check(path):
    proof = path[:-4] + '.drat'
    sha = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    t = time.time()
    p = subprocess.run([CADICAL, '-q', '--binary=false', path, proof], capture_output=True, text=True)
    t_solve = time.time() - t
    solver = 'UNSAT' if p.returncode == 20 else f'rc={p.returncode}'
    t = time.time()
    q = subprocess.run([DRATTRIM, path, proof, '-t', '100000'], capture_output=True, text=True)
    t_check = time.time() - t
    out = q.stdout.replace('\r', '\n')          # drat-trim draws progress lines with carriage returns
    verified = bool(re.search(r'^s VERIFIED\s*$', out, re.M))
    size = os.path.getsize(proof) if os.path.exists(proof) else 0
    if verified and os.path.exists(proof):
        os.remove(proof)
    m = re.match(r'case(\d+)\.cnf', os.path.basename(path))
    return {'case': int(m.group(1)) if m else None, 'cnf': os.path.basename(path), 'cnf_sha256': sha,
            'cadical': solver, 'solve_seconds': round(t_solve, 1), 'drat_bytes': size,
            'drat_trim': 'VERIFIED' if verified else out[-300:], 'check_seconds': round(t_check, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('dir'); ap.add_argument('out'); ap.add_argument('--workers', type=int, default=2)
    args = ap.parse_args()
    done = set()
    if os.path.exists(args.out):
        done = {json.loads(l)['cnf'] for l in open(args.out)}
    todo = sorted(f for f in os.listdir(args.dir) if re.match(r'case\d+\.cnf$', f) and f not in done)
    with cf.ThreadPoolExecutor(args.workers) as ex, open(args.out, 'a') as f:
        for r in ex.map(lambda x: check(os.path.join(args.dir, x)), todo):
            f.write(json.dumps(r) + '\n'); f.flush()
            print(r['cnf'], r['cadical'], r['drat_trim'], r['solve_seconds'], r['check_seconds'], flush=True)


if __name__ == '__main__':
    main()
