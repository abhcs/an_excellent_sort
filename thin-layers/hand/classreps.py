"""One representative prefix per reachable-set class, from a classcount DUMP file (efficient-prefixes.md §9).
usage: classreps.py L2CLASSES.json DUMP.txt OUT.json  -> {'n','a','depth','reps': [prefix], 'hash': [...], 'size': [...]}"""
import json, sys, collections
d = json.load(open(sys.argv[1])); L1 = d['L1']; R = d['reps']
first = {}; size = collections.Counter()
for line in open(sys.argv[2]):
    f = line.split(); h = f[0]; r = int(f[1]); L3 = [[int(f[k]), int(f[k + 1])] for k in range(2, len(f), 2)]
    size[h] += 1
    if h not in first:
        first[h] = [L1, R[r], L3]
hs = sorted(first)
json.dump({'n': d['n'], 'a': d['a'], 'depth': int(sys.argv[4]) if len(sys.argv) > 4 else 8, 'reps': [first[h] for h in hs],
           'hash': hs, 'size': [size[h] for h in hs]}, open(sys.argv[3], 'w'))
print(len(hs), 'classes')
