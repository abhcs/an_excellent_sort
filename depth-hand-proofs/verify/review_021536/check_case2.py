"""Independent check of the case-2 idle-wire argument from the printed note."""
import re
from common import *

text = open(DOC + 'h9_recovery_021536_case2.md').read()
M = edges('12 34 78')
C = (L1, L2, M)
runs = {}
for name, inp, out in re.findall(r'^\| ([A-K]) \| `(\d{9})` \| `(\d{9})` \|$', text, re.M):
    x = [int(c) for c in inp]
    assert sorted(x) == list(range(9))
    y = run(C, x)
    assert ''.join(map(str, y)) == out, (name, y, out)
    runs[name] = y
assert len(runs) == 11
Y = list(runs.values())

worst = []
for p in range(9):
    vals = [y[p] for y in Y]
    assert max(vals) - min(vals) >= 4, ('Q idle', p)
    for q in range(9):
        if q == p:
            continue
        for r in [None] + [v for v in range(9) if v not in (p, q)]:
            best = 0
            for f in (min, max):
                out = []
                for y in Y:
                    z = y[q] if r is None else (min(y[q], y[r]) if q < r else max(y[q], y[r]))
                    out.append(f(y[p], z))
                best = max(best, max(out) - min(out))
            assert best >= 4, (p, q, r)
            worst.append(best)
print('all 9 Q-idle and 576 paired local modes have a gap >= 4; min gap', min(worst))

# parse and verify each printed guard independently
labels = 'ABCDEFGHIJK'
rows = re.findall(r'^\| (\d) \| (idle|\d) \| (.+) \|$', text, re.M)
assert len(rows) == 81, len(rows)
for p, qm, guards in rows:
    p = int(p)
    q = None if qm == 'idle' else int(qm)
    modes_all = {None} if q is None else {None} | {v for v in range(9) if v not in (p, q)}
    covered = set()
    for g in guards.split('; '):
        m = re.fullmatch(r'([A-K])–([A-K])/(idle|min|max) \{([I0-8,]+)\}', g)
        assert m, g
        a, b, op, ms = m.groups()
        ya, yb = runs[a], runs[b]
        listed = {None if t == 'I' else int(t) for t in ms.split(',')}
        for r in listed:
            assert r in modes_all
            if op == 'idle':
                va, vb = ya[p], yb[p]
            else:
                f = min if op == 'min' else max
                def val(y):
                    z = y[q] if r is None else (min(y[q], y[r]) if q < r else max(y[q], y[r]))
                    return f(y[p], z)
                va, vb = val(ya), val(yb)
            assert abs(va - vb) >= 4, (p, q, g, r, va, vb)
        covered |= listed
    assert covered == modes_all, (p, q, modes_all - covered)
print('all 81 printed guard rows verified and cover every local mode')
print('CASE2 OK')
