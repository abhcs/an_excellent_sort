"""Run a script on many argument lists in parallel subprocesses with a wall-clock limit each.
usage: W LIMIT OUTLOG -- python-script [fixed args] ::: argsA ::: argsB ...
Each ':::'-separated group is appended to the command; the last line of each run's output (or
TIMEOUT) goes to OUTLOG with the elapsed time."""
import subprocess, sys, time, concurrent.futures as cf
W, LIMIT, OUT = int(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
rest = sys.argv[5:]
groups, cur = [], []
for x in rest:
    if x == ':::':
        groups.append(cur); cur = []
    else:
        cur.append(x)
groups.append(cur)
base, jobs = groups[0], groups[1:]
PY = sys.executable


def run(args):
    t0 = time.time()
    try:
        p = subprocess.run([PY] + base + args, capture_output=True, text=True, timeout=LIMIT)
        lines = [l for l in p.stdout.splitlines() if l.strip()]
        last = lines[-1] if lines else p.stderr[-300:]
    except subprocess.TimeoutExpired:
        last = 'TIMEOUT'
    return f'{" ".join(args)}\t{time.time() - t0:.1f}s\t{last}'


with open(OUT, 'a') as f, cf.ThreadPoolExecutor(W) as ex:
    for line in ex.map(run, jobs):
        print(line, flush=True)
        f.write(line + '\n')
        f.flush()
