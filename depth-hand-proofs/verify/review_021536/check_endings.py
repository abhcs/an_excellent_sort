"""Independent check of the 31 ending certificates from the printed note."""
import re
import itertools
from common import *

text = open(DOC + 'h9_recovery_021536_endings.md').read()
ftext = open(DOC + 'h9_recovery_021536_fourths_tables.md').read()

inputs = {}
for name, r in re.findall(r'^\| ([A-P]) \| `(\d{9})` \|$', text, re.M):
    x = [int(c) for c in r]
    assert sorted(x) == list(range(9))
    inputs[name] = x
assert len(inputs) == 16

pref = {}
for lab, M, N, piv, obs in re.findall(r'^\| (\d+\.\d+) \| `([\d ]+)` \| `([\d ]+)` \| ([\d,]+) \| (.+) \|$', text, re.M):
    pref[lab] = dict(M=edges(M), N=edges(N), piv=[int(v) for v in piv.split(',')], obs=obs)
assert len(pref) == 31, len(pref)

# coverage: compare with fourths survivors
surv = {}
for blk in re.split(r'^## Case ', ftext, flags=re.M)[1:]:
    num = int(blk.split(':')[0])
    M = edges(re.search(r'M=`([\d ]+)`', blk).group(1))
    line = re.search(r'Surviving N: (.*)\.$', blk, re.M).group(1)
    for s in re.findall(r'`([\d ]+)`', line):
        surv[(num, edges(s))] = M
got = {}
for lab, d in pref.items():
    num = int(lab.split('.')[0])
    got[(num, d['N'])] = d['M']
assert got == surv, (set(got) ^ set(surv))
print('31 ending prefixes match the 31 fourth-layer survivors exactly')

OUT = {}


def outputs(d):
    pre = (L1, L2, d['M'], d['N'])
    return {k: run(pre, x) for k, x in inputs.items()}


def rng(vals):
    return min(vals), max(vals)


results = {}
for lab, d in sorted(pref.items(), key=lambda kv: tuple(map(int, kv[0].split('.')))):
    Y = outputs(d)
    OUT[lab] = Y
    ys = list(Y.values())
    mand = [w for w in range(9) if max(y[w] for y in ys) - min(y[w] for y in ys) >= 4]
    allowed = set()
    parity_ex = []
    for a, b in itertools.combinations(range(9), 2):
        lo_min, hi_min = rng([min(y[a], y[b]) for y in ys])
        lo_max, hi_max = rng([max(y[a], y[b]) for y in ys])
        if hi_min - lo_min >= 4 or hi_max - lo_max >= 4:
            continue
        if hi_min - lo_min == 3 and hi_max - lo_max == 3:
            inter = set(range(lo_min, hi_min + 1)) & set(range(lo_max, hi_max + 1))
            if len(inter) % 2 == 1:
                parity_ex.append((a, b))
                continue
        allowed.add((a, b))
    # does some matching in the allowed graph cover all mandatory wires?
    def coverable(rem, used):
        if not rem:
            return True
        v = rem[0]
        for a, b in allowed:
            if v in (a, b):
                w = b if a == v else a
                if w not in used:
                    if coverable([u for u in rem[1:] if u != w], used | {v, w}):
                        return True
        return False
    cov = coverable(mand, frozenset())
    # edges needed without parity
    allowed_np = allowed | set(parity_ex)
    def coverable_np(rem, used):
        if not rem:
            return True
        v = rem[0]
        for a, b in allowed_np:
            if v in (a, b):
                w = b if a == v else a
                if w not in used and coverable_np([u for u in rem[1:] if u != w], used | {v, w}):
                    return True
        return False
    results[lab] = dict(mand=mand, cov=cov, parity_needed=coverable_np(mand, frozenset()) and not cov,
                        parity_ex=parity_ex, partners={v: sorted(w for e in allowed for w in e if v in e and w != v) for v in mand})
    assert not cov, lab
    assert set(d['piv']) <= set(mand), (lab, d['piv'], mand)

for lab, r in results.items():
    print(lab, 'mandatory', r['mand'], 'partners', r['partners'], 'parity needed' if r['parity_needed'] else '', r['parity_ex'] if r['parity_needed'] else '')

# verify printed guard table rows
labels = 'ABCDEFGHIJKLMNOP'
grows = re.findall(r'^\| (\d+\.\d+) \| (\d) \| ([A-P]):(\d)–([A-P]):(\d) \| (.+?) \| (\w+) \| (\w+) \|$', text, re.M)
assert len(grows) == 32, len(grows)
for lab, piv, la, lv, ha, hv, guards, direct, before in grows:
    Y = OUT[lab]; p = int(piv); lv = int(lv); hv = int(hv)
    vals = [y[p] for y in Y.values()]
    assert Y[la][p] == lv == min(vals) and Y[ha][p] == hv == max(vals) and hv - lv >= 4, (lab, p)
    excl = set()
    for g in guards.split('; '):
        m = re.fullmatch(r'([A-P]) (lo|hi):(\d+)', g)
        name, kind, ex = m.groups()
        y = Y[name]
        if kind == 'lo':
            assert y[p] <= hv - 4
            calc = {q for q in range(9) if q != p and y[q] <= hv - 4}
        else:
            assert y[p] >= lv + 4
            calc = {q for q in range(9) if q != p and y[q] >= lv + 4}
        assert calc == {int(c) for c in ex}, (lab, p, g, calc)
        excl |= calc
    rem = set(range(9)) - {p} - excl
    assert rem == (set() if direct == 'empty' else {int(c) for c in direct}), (lab, p, rem, direct)
print('32 printed guard rows verified')

rrows = re.findall(r'^\| (\d+\.\d+) \| (\d) \| (\d) \| ([A-P]):(\d)–([A-P]):(\d) \| ([A-P]) (lo|hi):(\d+) \|$', text, re.M)
assert len(rrows) == 12, len(rrows)
for lab, piv, w, la, lv, ha, hv, name, kind, ex in rrows:
    Y = OUT[lab]; p = int(piv); w = int(w); lv = int(lv); hv = int(hv)
    vals = [y[w] for y in Y.values()]
    assert Y[la][w] == lv == min(vals) and Y[ha][w] == hv == max(vals), (lab, w)
    y = Y[name]
    if kind == 'lo':
        assert y[w] <= hv - 4
        calc = {q for q in range(9) if q != w and y[q] <= hv - 4}
    else:
        assert y[w] >= lv + 4
        calc = {q for q in range(9) if q != w and y[q] >= lv + 4}
    assert calc == {int(c) for c in ex} and p in calc, (lab, p, w, calc)
print('12 printed reciprocal rows verified')

prows = re.findall(r'^\| (\d+\.\d+) \| `(\d)(\d)` \| ([A-P]):(\d)–([A-P]):(\d) \| ([A-P]):(\d)–([A-P]):(\d) \| (\d+) \|$', text, re.M)
assert len(prows) == 5
for lab, a, b, n1, v1, n2, v2, n3, v3, n4, v4, inter in prows:
    Y = OUT[lab]; a = int(a); b = int(b)
    mins = {k: min(y[a], y[b]) for k, y in Y.items()}
    maxs = {k: max(y[a], y[b]) for k, y in Y.items()}
    assert mins[n1] == int(v1) == min(mins.values()) and mins[n2] == int(v2) == max(mins.values())
    assert maxs[n3] == int(v3) == min(maxs.values()) and maxs[n4] == int(v4) == max(maxs.values())
    assert int(v2) - int(v1) == 3 and int(v4) - int(v3) == 3
    I = set(range(int(v1), int(v2) + 1)) & set(range(int(v3), int(v4) + 1))
    assert sorted(I) == [int(c) for c in inter] and len(I) % 2 == 1
print('5 printed parity rows verified')
print('ENDINGS OK')
