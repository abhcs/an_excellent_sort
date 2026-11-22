"""Progress of an s14_case_run.py run: per pass, how many children were tried, proved, hit, left
open, and the worker time spent; overall, how many children are proved.
usage: CASE [LOGDIR]   (reads LOGDIR/s14_case{CASE}_p*_w*.log)"""
import collections, glob, os, re, sys

case = int(sys.argv[1])
logdir = sys.argv[2] if len(sys.argv) > 2 else 'logs'
line = re.compile(r'child (\d+): (\w+) by (\S+) ([\d.]+)s nodes (\d+)')
total = None
proved, last = set(), {}
for p in range(1, 20):
    files = sorted(glob.glob(os.path.join(logdir, f's14_case{case}_p{p}_w*.log')))
    if not files:
        break
    tally, secs, nodes, rules = collections.Counter(), collections.Counter(), 0, collections.Counter()
    done_workers, cap = 0, None
    for fn in files:
        for s in open(fn):
            m = line.search(s)
            if m:
                k, kind, rule, sec, nd = int(m[1]), m[2], m[3], float(m[4]), int(m[5])
                tally[kind] += 1
                secs[kind] += sec
                nodes += nd
                last[k] = kind
                if kind in ('NO', 'HIT'):
                    proved.add(k)
                    if kind == 'NO':
                        rules[rule] += 1
            elif 'children, cap' in s:
                total = int(re.search(r'(\d+) children', s)[1])
                cap = re.search(r'cap (\d+)s', s)[1]
            elif 'done (' in s:
                done_workers += 1
    tried = sum(tally.values())
    print(f'pass {p} (cap {cap}s, {len(files)} workers, {done_workers} done): {tried} tried, '
          f'{dict(tally)}; worker hours {sum(secs.values()) / 3600:.2f} '
          f'(NO {secs["NO"] / 3600:.2f}, OPEN {secs["OPEN"] / 3600:.2f}); nodes {nodes}; NO rules {dict(rules)}')
if total:
    still = sum(1 for k, v in last.items() if v == 'OPEN' and k not in proved)
    print(f'case {case}: {len(proved)}/{total} children proved, {still} open after their last try, '
          f'{total - len(last)} not yet tried')
