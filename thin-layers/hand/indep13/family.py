"""family.py L2CLASSES.json: the family file for cls.c (n a, the first layer, the second-layer classes)
from a results/l2classes_{n}_{a}.json file (l2classes.py; cover checked by verify_cover.py)."""
import json, sys
d = json.load(open(sys.argv[1]))
row = lambda L: ' '.join([str(len(L))] + [f'{min(p)} {max(p)}' for p in L])
print(d['n'], d['a']); print(row(d['L1'])); print(len(d['reps']))
for r in d['reps']:
    print(row(r))
