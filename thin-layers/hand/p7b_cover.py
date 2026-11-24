"""Does (P7b) -- no depth-6 7-sorter has at most one comparator in its second layer -- close the
leftover exceptional prefixes at (8, 2)?  For each prefix, look for one infinity whose residual
(7 reals) has height 2 with a schedule whose second layer holds at most one real comparison, or a
schedule of height h <= 2 that fits (P7b) with the free layers.  usage: hand/exc_8_2.json"""
import json, os, sys, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, '..')]
import sentinel_prover as sp

d = json.load(open(sys.argv[1]))
n, f = d['n'], d['depth'] - 3
closed, how = 0, []
for P in d['left']:
    layers = tuple(tuple(tuple(c) for c in L) for L in P)
    found = None
    for c in range(n):
        for sg in '+-':
            r, R, h, asap, alap = sp.residual2(n, layers, {c: sg})
            if r != 7 or h + f > 6:
                continue
            for name, prof in (('asap', asap), ('alap', alap)):
                sizes = list(prof) + [r // 2] * f
                if len(sizes) >= 2 and sizes[1] <= 1:
                    found = (c, sg, name, prof)
                    break
            if found:
                break
        if found:
            break
    if found:
        closed += 1
    how.append(found)
print(f'{closed} of {len(d["left"])} leftover prefixes close by one infinity and (P7b)')
for P, h in list(zip(d['left'], how))[:6]:
    print('  ', P, '->', h)
