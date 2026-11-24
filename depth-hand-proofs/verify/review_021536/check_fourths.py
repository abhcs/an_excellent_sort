"""Independent check of the fourth-layer classification: parse the printed tables,
re-derive every signed row, verify forbidden edges by the 0-1 principle, then
brute-force ALL matchings N on nine wires (any size, no maximality) against the
printed demands and compare with the printed survivor lists."""
import re
from collections import defaultdict
from common import *

text = open(DOC + 'h9_recovery_021536_fourths_tables.md').read()
blocks = re.split(r'^## Case ', text, flags=re.M)[1:]
ALL = matchings(9)
assert len(ALL) == 2620
cases = {}
for blk in blocks:
    num = int(blk.split(':')[0])
    M = edges(re.search(r'M=`([\d ]+)`', blk).group(1))
    forb = set(edges(re.search(r'Forbidden N edges: `([\d ]+)`', blk).group(1)))
    rows = []
    for i, sig, real, dem in re.findall(r'^\| (\d+) \| `([+\-\d ]+)` \| (\d{5}) \| (\d) \|$', blk, re.M):
        pl = {int(t[1:]): (1 if t[0] == '+' else -1) for t in sig.split()}
        rows.append((int(i), pl, tuple(int(c) for c in real), int(dem)))
    surv_line = re.search(r'Surviving N: (.*)\.$', blk, re.M).group(1)
    surv = set() if surv_line.strip() == 'none' else {edges(s) for s in re.findall(r'`([\d ]+)`', surv_line)}
    cases[num] = dict(M=M, forb=forb, rows=rows, surv=surv)

assert sorted(cases) == [c for c in range(1, 19) if c != 2]
summary = {}
for num, c in sorted(cases.items()):
    M = c['M']
    pre = (L1, L2, M)
    nf, sw = order_info(pre)
    bad_forb = c['forb'] - nf
    assert not bad_forb, (num, bad_forb)
    extra = nf - c['forb']
    # each printed row
    for i, pl, real, dem in c['rows']:
        assert len(pl) == 4
        tr = trace(pre, pl)
        numeric_check(pre, pl, tr, trials=50, seed=i)
        assert tr['real'] == real, (num, i, tr['real'], real)
        assert len(tr['events']) == 3 - dem, (num, i, tr['events'], dem)
    # brute force over every matching avoiding forbidden edges
    ok = []
    for N in ALL:
        if set(N) & c['forb']:
            continue
        if all(sum(1 for a, b in N if a in real and b in real) >= dem for _, _, real, dem in c['rows']):
            ok.append(N)
    ok = set(ok)
    assert ok == c['surv'], (num, sorted(ok - c['surv']), sorted(c['surv'] - ok))
    summary[num] = (len(ok), sorted(extra), sorted(sw))
for num, (n, extra, sw) in summary.items():
    print(f'case {num:2d}: survivors {n:2d}; unlisted never-fire pairs {extra}; always-swap pairs {sw}')
print('total survivors', sum(v[0] for v in summary.values()))
print('FOURTHS OK')
