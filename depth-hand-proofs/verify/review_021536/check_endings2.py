"""Second pass: printed 'remainder before parity' column, pivot lists, and final
obstruction per row, recomputed from the printed guard/reciprocal/parity tables."""
import re
from common import *
text = open(DOC + 'h9_recovery_021536_endings.md').read()
pref = {lab: [int(v) for v in piv.split(',')] for lab, piv in
        re.findall(r'^\| (\d+\.\d+) \| `[\d ]+` \| `[\d ]+` \| ([\d,]+) \| .+ \|$', text, re.M)}
grows = re.findall(r'^\| (\d+\.\d+) \| (\d) \| [A-P]:\d–[A-P]:\d \| .+? \| (\w+) \| (\w+) \|$', text, re.M)
rrows = re.findall(r'^\| (\d+\.\d+) \| (\d) \| (\d) \| [A-P]:\d–[A-P]:\d \| [A-P] (?:lo|hi):\d+ \|$', text, re.M)
prows = {lab: (int(a), int(b)) for lab, a, b in re.findall(r'^\| (\d+\.\d+) \| `(\d)(\d)` \|', text, re.M)}
S = lambda s: set() if s == 'empty' else {int(c) for c in s}
piv_by_lab = {}
for lab, p, direct, before in grows:
    p = int(p)
    rec = {int(w) for l2, p2, w in rrows if l2 == lab and int(p2) == p}
    assert rec <= S(direct), (lab, p)
    assert S(direct) - rec == S(before), (lab, p, S(direct) - rec, before)
    after = {w for w in S(before) if tuple(sorted((p, w))) != prows.get(lab)}
    piv_by_lab.setdefault(lab, {})[p] = after
assert {l: sorted(d) for l, d in piv_by_lab.items()} == pref
for lab, d in piv_by_lab.items():
    if len(d) == 1:
        assert not list(d.values())[0], lab
    else:
        nb = set().union(*d.values())
        assert not nb & set(d) and len(nb) < len(d), lab
        print(lab, 'two-pivot Hall:', d)
print('remainder columns, pivot lists and final obstructions consistent for', len(piv_by_lab), 'prefixes')
