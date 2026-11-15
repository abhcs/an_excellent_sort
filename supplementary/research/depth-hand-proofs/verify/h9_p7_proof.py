#!/usr/bin/env python3
"""h9_p7_proof.py -- checks the proof of (P7) in h9.md (section 7.5 and appendix B) as written.

(P7): no sorting network on 7 channels with at most 6 layers has at most one comparator in its first
layer.  The checks, in the order of section 7.5:

1. The reduction to (beta) after Lemma 12: on every prefix (L1, L2, L3) of form (alpha), reversing,
   relabelling 5,6,0..4 as 0..6 and untangling gives a prefix of form (beta), with no comparator in two
   consecutive layers; this maps the 150 (alpha) prefixes onto the 150 (beta) prefixes.  The ten
   third layers are the six cases of appendix B and their images under 3<->5, 4<->6.
2. The description of the states and probes after layer 2, against all 2^7 inputs.
3. The table of probes after layer 2 in section 7.5 (tokens on 1, 3, 4), and the rules (R2), (R3), (R4)
   for each of the ten third layers.
4. Appendix B, read from h9.md: every row (the left state is a probe after layer 2 for its output, L3
   turns it into the right state, and the arrows are right), and every bullet (the rows named make the
   comparators named two-sided; the fourth layers listed are exactly the three-comparator matchings
   avoiding L3 and the median's two-sided comparators; each gets the positions stated, from the rows
   and (R2)/(R4) alone; together they are all of them).
5. Brute force with probes from inputs: for each of the ten third layers, every fourth layer avoiding L3
   lets some output's probes reach at least five channels after layer 4.

Needs only python3.  Exit status 0 iff everything holds.  usage: python3 h9_p7_proof.py [path/to/h9.md]
"""
import itertools
import os
import re
import sys

N = 7
L1 = [(0, 1)]
L2 = [(0, 2), (3, 4), (5, 6)]
failures = []


def check(cond, msg):
    if not cond:
        failures.append(msg)
        print('  FAIL:', msg)
    return cond


def apply(state, layer):
    """state: tuple of bits; layer: list of (low end, high end)."""
    s = list(state)
    for a, b in layer:
        if s[a] > s[b]:
            s[a], s[b] = s[b], s[a]
    return tuple(s)


def perfect_matchings(chans):
    chans = sorted(chans)
    if not chans:
        yield []
        return
    a = chans[0]
    for b in chans[1:]:
        rest = [c for c in chans if c not in (a, b)]
        for m in perfect_matchings(rest):
            yield [(a, b)] + m


def matchings(avoid=(), sizes=(0, 1, 2, 3)):
    pairs = [(a, b) for a in range(N) for b in range(a + 1, N) if (a, b) not in avoid]
    for r in sizes:
        for m in itertools.combinations(pairs, r):
            if len({x for e in m for x in e}) == 2 * r:
                yield list(m)


def pairs_up(layer, chans):
    inside = {x for a, b in layer if a in chans and b in chans for x in (a, b)}
    return inside == set(chans)


def fmt(m):
    return ''.join('(%d,%d)' % e for e in m)


# ---------------------------------------------------------------- 1. the reduction to (beta)
def untangle(layers):
    """layers: lists of (min end, max end), possibly reversed; returns standard layers (Knuth 5.3.4-16)."""
    layers = [list(L) for L in layers]
    for t in range(len(layers)):
        for i, (a, b) in enumerate(layers[t]):
            if a > b:
                layers[t][i] = (b, a)
                sw = {a: b, b: a}
                for u in range(t + 1, len(layers)):
                    layers[u] = [(sw.get(x, x), sw.get(y, y)) for x, y in layers[u]]
    return [sorted(L) for L in layers]


def no_repeats(layers):
    return all(not (set(layers[t]) & set(layers[t + 1])) for t in range(len(layers) - 1))


def is_alpha(P):
    a, b, c3 = P
    if a != L1 or not pairs_up(b, range(1, 7)) or not no_repeats(P):
        return False
    c = [y for x, y in b if x == 1]
    return len(c) == 1 and pairs_up(c3, [x for x in range(N) if x != c[0]])


def is_beta(P):
    a, b, c3 = P
    return a == L1 and pairs_up(b, [0, 2, 3, 4, 5, 6]) and pairs_up(c3, range(1, 7)) and no_repeats(P)


def all_prefixes():
    ms = [sorted(m) for m in matchings(sizes=(3,))]
    for b in ms:
        for c3 in ms:
            yield [L1, b, c3]


print('1. the reduction of form (alpha) to form (beta)')
alphas = [P for P in all_prefixes() if is_alpha(P)]
betas = [P for P in all_prefixes() if is_beta(P)]
relabel = {5: 0, 6: 1, 0: 2, 1: 3, 2: 4, 3: 5, 4: 6}
images = set()
for P in alphas:
    rev = [[(6 - j, 6 - i) for i, j in L] for L in P]                 # min to 6-j, max to 6-i
    rel = [[(relabel[x], relabel[y]) for x, y in L] for L in rev]     # (min end, max end)
    Q = untangle(rel)
    check(is_beta(Q), 'reduction of %s gives %s, not of form (beta)' % ('|'.join(map(fmt, P)), '|'.join(map(fmt, Q))))
    images.add(tuple(tuple(L) for L in Q))
check(len(alphas) == 150 and len(betas) == 150, 'expected 150 prefixes of each form, got %d and %d' % (len(alphas), len(betas)))
check(images == {tuple(tuple(L) for L in P) for P in betas}, 'the reduction does not map (alpha) onto (beta)')
print('   %d prefixes of form (alpha) map onto the %d of form (beta)' % (len(alphas), len(betas)))
TEN = [m for m in perfect_matchings(range(1, 7)) if (3, 4) not in m and (5, 6) not in m]
check(len(TEN) == 10, 'expected ten third layers')

# ---------------------------------------------------------------- 2. states and probes after layer 2
print('2. states and probes after layer 2')
A_STATES = ['000', '010', '001', '011', '111']
P_STATES = ['00', '01', '11']
A_PROBES = ['*11', '0*0', '0*1', '00*', '01*']
P_PROBES = ['*1', '0*']


def described_states():
    return {a + b + c for a in A_STATES for b in P_STATES for c in P_STATES}


def described_probes():
    out = set()
    for a in A_STATES + A_PROBES:
        for b in P_STATES + P_PROBES:
            for c in P_STATES + P_PROBES:
                if (a + b + c).count('*') == 1:
                    out.add(a + b + c)
    return out


def tostr(state, token=None):
    return ''.join('*' if i == token else str(state[i]) for i in range(N))


occurring = {apply(apply(tuple(x >> i & 1 for i in range(N)), L1), L2) for x in range(1 << N)}
check({tostr(s) for s in occurring} == described_states(), 'the states after layer 2 are not as described')
pairs = set()
for s in occurring:
    for j in range(N):
        if s[j] == 0:
            t = list(s)
            t[j] = 1
            if tuple(t) in occurring:
                pairs.add(tostr(s, j))
check(pairs == described_probes(), 'the probes after layer 2 are not as described')
from_inputs = set()
for x in range(1 << N):
    xs = tuple(x >> i & 1 for i in range(N))
    for p in range(N):
        if not xs[p]:
            ys = list(xs)
            ys[p] = 1
            s, t = apply(apply(xs, L1), L2), apply(apply(tuple(ys), L1), L2)
            j = [i for i in range(N) if s[i] != t[i]]
            check(len(j) == 1, 'Lemma 13 fails')
            from_inputs.add(tostr(s, j[0]))
check(from_inputs == pairs, 'probes from inputs differ from pairs of states')
print('   %d states, %d probes (the same from pairs of inputs one bit apart)' % (len(occurring), len(pairs)))


def probes2(k):
    """probes after layer 2 for output k: 6-k ones besides the token."""
    return sorted(p for p in described_probes() if p.count('1') == 6 - k)


def step(p, layer):
    """apply a layer to a probe, moving the token by Lemma 13's rule."""
    s = [0 if ch == '*' else int(ch) for ch in p]        # the state without the token's 1
    j = p.index('*')
    for a, b in layer:
        if j in (a, b):
            bit = s[b if j == a else a]
            s[a], s[b] = 0, bit
            j = b if bit == 0 else a
        elif s[a] > s[b]:
            s[a], s[b] = s[b], s[a]
    return tostr(s, j)


def step_bruteforce(p, layer):
    s = tuple(0 if ch == '*' else int(ch) for ch in p)
    t = list(s)
    t[p.index('*')] = 1
    s2, t2 = apply(s, layer), apply(tuple(t), layer)
    j = [i for i in range(N) if s2[i] != t2[i]]
    assert len(j) == 1
    return tostr(s2, j[0])


for p in described_probes():
    for L3 in TEN:
        check(step(p, L3) == step_bruteforce(p, L3), 'token rule disagrees on %s' % p)

# ---------------------------------------------------------------- 3. the table of 7.5 and (R2)-(R4)
print('3. the table of probes after layer 2, and (R2), (R3), (R4)')
TABLE = {  # token on: {output: probes}, as printed in section 7.5
    1: {3: '0*0 01 11, 0*0 11 01, 0*1 00 11, 0*1 01 01, 0*1 11 00',
        4: '0*0 00 11, 0*0 01 01, 0*0 11 00, 0*1 01 00, 0*1 00 01',
        2: '0*0 11 11, 0*1 01 11, 0*1 11 01'},
    3: {3: '000 *1 11, 010 *1 01, 001 *1 01, 011 *1 00',
        4: '000 *1 01, 010 *1 00, 001 *1 00',
        2: '010 *1 11, 001 *1 11, 011 *1 01, 111 *1 00'},
    4: {3: '010 0* 11, 001 0* 11, 011 0* 01, 111 0* 00',
        4: '000 0* 11, 010 0* 01, 001 0* 01, 011 0* 00',
        2: '011 0* 11, 111 0* 01'},
}


def swap_last_blocks(p):
    return p[:3] + p[5:] + p[3:5]


for u, row in TABLE.items():
    for k, txt in row.items():
        listed = {x.replace(' ', '') for x in txt.split(', ')}
        actual = {p for p in probes2(k) if p.index('*') == u}
        check(listed == actual, 'section 7.5 table: token on %d, output %d' % (u, k))
        # token on 2: replace 0*0, 0*1 by 00*, 01*; token on 5, 6: swap the last two blocks of 3, 4
        if u == 1:
            other = {p.replace('0*0', '00*', 1) if p.startswith('0*0') else '01*' + p[3:] for p in listed}
            check(other == {p for p in probes2(k) if p.index('*') == 2}, 'token on 2, output %d' % k)
        else:
            other = {swap_last_blocks(p) for p in listed}
            check(other == {p for p in probes2(k) if p.index('*') == u + 2}, 'token on %d, output %d' % (u + 2, k))
check(all(p.index('*') != 0 or p.startswith('*11') for k in (2, 3, 4) for p in probes2(k)), 'token on 0')


def seen(k, u, v):
    """values on channel v seen by output-k probes after layer 2 with the token on u."""
    return {p[v] for p in probes2(k) if p.index('*') == u}


FREE = {1: [2, 3, 4, 5, 6], 2: [1, 3, 4, 5, 6], 3: [1, 2, 5, 6], 4: [1, 2, 5, 6], 5: [1, 2, 3, 4], 6: [1, 2, 3, 4]}
EXCEPT = {3: {}, 4: {(3, 5): '0', (5, 3): '0'},
          2: {(u, v): '1' for u in (1, 2) for v in (4, 6)} | {(u, v): '1' for u in (4, 6) for v in (1, 2, 4, 6) if v != u}}
for k in (2, 3, 4):
    for u, vs in FREE.items():
        for v in vs:
            want = {EXCEPT[k][(u, v)]} if (u, v) in EXCEPT[k] else {'0', '1'}
            check(seen(k, u, v) == want, '(R%d) text: token on %d, channel %d sees %s' % (k, u, v, sorted(seen(k, u, v))))


def reach3(L3, k):
    return {step(p, L3).index('*') for p in probes2(k)}


def rule(L3, k):
    if k == 3:
        return set(range(N))
    if k == 4:
        return set(range(N)) - ({3} if (3, 5) in L3 else set())
    return set(range(N)) - {b for a, b in L3 if a in (1, 2, 4) and b in (4, 6)}


for L3 in TEN:
    for k in (2, 3, 4):
        check(reach3(L3, k) == rule(L3, k), '(R%d) for L3 = %s' % (k, fmt(L3)))
print('   the table, the statements on which values a token sees, and (R2)-(R4) for all ten third layers')

# ---------------------------------------------------------------- 4. appendix B
path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'h9.md')
print('4. appendix B of', os.path.normpath(path))
text = open(path, encoding='utf-8').read()
m = re.search(r'<!-- p7-tables -->(.*?)<!-- /p7-tables -->', text, re.S)
check(m is not None, 'no appendix B markers in h9.md')
section = m.group(1) if m else ''
parts = re.split(r'^\*\*(β\d): \$L_3=((?:\(\d,\d\))+)\$\.\*\*$', section, flags=re.M)
cases = [(parts[i], parts[i + 1], parts[i + 2]) for i in range(1, len(parts) - 2, 3)]
check([c[0] for c in cases] == ['β1', 'β2', 'β3', 'β4', 'β5', 'β6'], 'expected cases β1-β6')


def comps(s):
    return [(int(a), int(b)) for a, b in re.findall(r'\((\d),(\d)\)', s)]


def three(s):
    return [tuple(comps(x)) for x in re.findall(r'(?:\(\d,\d\)){3}', s)]


def labels(s):
    r = re.fullmatch(r'([a-z])–([a-z])', s.strip())
    if r:
        return [chr(c) for c in range(ord(r.group(1)), ord(r.group(2)) + 1)]
    return [x.strip() for x in re.split(r', | and ', s.strip())]


def two_sided(rows, e):
    u, v = e
    dirs = set()
    for r in rows:
        j = r.index('*')
        if j in (u, v):
            dirs.add('up' if r[v if j == u else u] == '0' else 'down')
    return dirs == {'up', 'down'}


def reach_text(s):
    s = s.strip()
    if s == 'all channels':
        return set(range(N))
    r = re.fullmatch(r'all channels but ((?:\d(?:, | and )?)+)', s)
    return set(range(N)) - {int(x) for x in re.findall(r'\d', r.group(1))} if r else None


seen_L3 = []
total_rows = total_l4 = 0
for name, l3s, body in cases:
    L3 = sorted(comps(l3s))
    seen_L3.append(L3)
    rows = {}
    for lab, k, a2, a3, arrows in re.findall(r'^\| ([a-z]) \| (\d) \| `([01* ]+)` \| `([01*]{7})` \| (.*?) \|$', body, re.M):
        k = int(k)
        a2 = a2.replace(' ', '')
        check(a2 in probes2(k), '%s row %s: %s is not a probe after layer 2 for output %d' % (name, lab, a2, k))
        check(step(a2, L3) == a3, '%s row %s: L3 gives %s, not %s' % (name, lab, step(a2, L3), a3))
        j = a3.index('*')
        for u, v, arr in re.findall(r'\((\d),(\d)\)([↑↓])', arrows):
            u, v = int(u), int(v)
            ok = j in (u, v) and (a3[v if j == u else u] == '0') == (arr == '↑')
            check(ok, '%s row %s: arrow (%d,%d)%s is wrong' % (name, lab, u, v, arr))
        rows[lab] = (k, a3)
    total_rows += len(rows)
    bullets = re.findall(r'^\* (.*?)(?=^\* |\Z)', body, re.M | re.S)
    bullets = [' '.join(b.split()) for b in bullets]
    T, left, kills, twos = None, None, {}, {}
    for b in bullets:
        r = re.fullmatch(r'Rows (.+?) make (.+?) two-sided for the median, so \$L_4\$ is one of (.+)\.', b)
        if r:
            labs = labels(r.group(1))
            check(all(rows.get(x, (0,))[0] == 3 for x in labs), '%s: rows %s are not all median rows' % (name, r.group(1)))
            T = comps(r.group(2))
            rs = [rows[x][1] for x in labs if x in rows]
            for e in T:
                check(two_sided(rs, e), '%s: rows %s do not make %s two-sided' % (name, r.group(1), fmt([e])))
            left = three(r.group(3))
            continue
        r = re.fullmatch(r'Rows (.+?) make (.+?) two-sided for output (\d), which reaches (.+?) after layer 3 by \(R(\d)\)\. This gives (.+)\.', b)
        if check(r is not None, '%s: cannot read the bullet "%s..."' % (name, b[:50])):
            k = int(r.group(3))
            check(int(r.group(5)) == k and k in (2, 4), '%s: output %d cites (R%s)' % (name, k, r.group(5)))
            labs = labels(r.group(1))
            check(all(rows.get(x, (0,))[0] == k for x in labs), '%s: rows %s are not all output-%d rows' % (name, r.group(1), k))
            rs = [rows[x][1] for x in labs if x in rows]
            twos[k] = comps(r.group(2))
            for e in twos[k]:
                check(two_sided(rs, e), '%s: rows %s do not make %s two-sided for output %d' % (name, r.group(1), fmt([e]), k))
            R = reach_text(r.group(4))
            check(R == rule(L3, k), '%s: output %d reach "%s" is not (R%d)' % (name, k, r.group(4), k))
            for seg in r.group(6).split('; and '):
                g = re.fullmatch(r'(2 \+ 1 \+ 1 \+ 1|2 \+ 2 \+ 1) for (.+)', seg)
                if not check(g is not None, '%s: cannot read "%s"' % (name, seg)):
                    continue
                for M in three(g.group(2)):
                    z = [c for c in range(N) if all(c not in e for e in M)][0]
                    hit = sum(1 for blk in [set(e) for e in M] + [{z}] if blk & (R or set()))
                    nt = sum(1 for e in M if e in twos[k])
                    if g.group(1) == '2 + 1 + 1 + 1':
                        check(hit == 4 and nt >= 1, '%s: %s does not get 2+1+1+1 for output %d' % (name, fmt(M), k))
                    else:
                        check(hit >= 3 and nt >= 2, '%s: %s does not get 2+2+1 for output %d' % (name, fmt(M), k))
                    kills.setdefault(M, []).append(k)
    check(T is not None and left is not None, '%s: no median bullet' % name)
    T = T or []
    expected = {tuple(m) for m in matchings(avoid=set(L3) | set(T), sizes=(3,))}
    check(set(left or []) == expected and len(left or []) == len(expected),
          '%s: the fourth layers listed are not those left' % name)
    check(set(kills) == expected, '%s: the fourth layers settled are not those listed' % name)
    total_l4 += len(expected)
    print('   %s L3 = %s: %d rows; %d comparators two-sided for the median; %d fourth layers, each settled'
          % (name, fmt(L3), len(rows), len(T), len(expected)))
swap = {3: 5, 5: 3, 4: 6, 6: 4}
orbit = {tuple(sorted(L)) for L in seen_L3} | {tuple(sorted(tuple(sorted((swap.get(a, a), swap.get(b, b)))) for a, b in L)) for L in seen_L3}
check(orbit == {tuple(sorted(L)) for L in TEN}, 'the six cases and their images are not the ten third layers')
print('   %d rows and %d fourth layers in all; the six cases and their images are the ten third layers' % (total_rows, total_l4))

# ---------------------------------------------------------------- 5. brute force
print('5. brute force: probes from inputs, every fourth layer avoiding L3')


def probes_after(layers, k):
    """probe states after the given layers, from all inputs x of weight 6-k and channels p with x_p = 0."""
    w, out = N - 1 - k, set()
    for x in range(1 << N):
        xs = tuple(x >> i & 1 for i in range(N))
        if sum(xs) != w:
            continue
        for p in range(N):
            if xs[p]:
                continue
            ys = list(xs)
            ys[p] = 1
            s, t = xs, tuple(ys)
            for L in layers:
                s, t = apply(s, L), apply(t, L)
            out.add((s, t))
    return out


count = 0
for L3 in TEN:
    after3 = {k: probes_after([L1, L2, L3], k) for k in range(N)}
    for L4 in matchings(avoid=set(L3)):
        best = 0
        for k in range(N):
            R = set()
            for s, t in after3[k]:
                s4, t4 = apply(s, L4), apply(t, L4)
                d = [i for i in range(N) if s4[i] != t4[i]]
                check(len(d) == 1, 'Lemma 13 fails')
                R |= set(d)
            best = max(best, len(R))
        check(best >= 5, 'L3 = %s, L4 = %s: no output reaches five channels' % (fmt(L3), fmt(L4)))
        count += 1
print('   %d pairs (L3, L4): in each, some output reaches at least five channels after layer 4' % count)

print('all checks of the (P7) proof hold' if not failures else '%d CHECKS FAIL' % len(failures))
sys.exit(1 if failures else 0)
