"""prep.py FILE.json [IDX...]: one tok.c input line per representative (idx n D p layers) of a reps file
(keys n, depth, reps), for the given indices or all of them."""
import json, sys
d = json.load(open(sys.argv[1]))
idxs = list(map(int, sys.argv[2:])) or range(len(d['reps']))
for i in idxs:
    pre = d['reps'][i]
    print(i, d['n'], d['depth'], len(pre), ' '.join(' '.join([str(len(L))] + [f'{a} {b}' for a, b in L]) for L in pre))
