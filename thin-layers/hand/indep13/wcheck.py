"""wcheck.py FAMILY.txt WITNESS.txt MEMBERS.txt LEMMAS10.txt LEMMAS11.txt K [SEED]: re-verify K random
prefixes of the certificate (env ONLY=direct: only prefixes of classes settled directly) written by cls.c, recomputing every set from the comparators (plain Python,
no code shared with cls.c):
  1. the prefix's reachable set (or its complement), relabelled by its MEMBERS permutation, is the
     reachable set of its class representative;
  2. the class witness holds: for 'residual', the sentinel's subcube image through the settling prefix has
     the sentinel value on the track end, and with that bit deleted (and complemented if stated) it
     relabels onto the reachable set of the named 10-channel lemma; for 'direct', the representative's
     set (or complement) relabels onto the reachable set of the named 11-channel lemma."""
import os, random, re, sys


def run(n, layers, inputs):
    out = set()
    for x in inputs:
        for L in layers:
            for a, b in L:
                if (x >> a) & 1 and not (x >> b) & 1:
                    x ^= (1 << a) | (1 << b)
        out.add(x)
    return out


def relabel(S, perm, comp, n):
    full = (1 << n) - 1
    res = set()
    for u in S:
        if comp:
            u ^= full
        t = 0
        for c in range(n):
            if (u >> c) & 1:
                t |= 1 << perm[c]
        res.add(t)
    return res


def pairs(s):
    v = list(map(int, re.findall(r'-?\d+', s)))
    return [(v[2 * i], v[2 * i + 1]) for i in range(len(v) // 2)]


def lemmas(path):
    out = {}
    for line in open(path):
        f = list(map(int, line.split()))
        idx, n, D, p = f[:4]; k = 4; layers = []
        for _ in range(p):
            m = f[k]; layers.append([(f[k + 1 + 2 * c], f[k + 2 + 2 * c]) for c in range(m)]); k += 1 + 2 * m
        out[idx] = (n, layers)
    return out


fam = open(sys.argv[1]).read().split('\n')
n, a = map(int, fam[0].split())
row = lambda s: pairs(' '.join(s.split()[1:]))
L1 = row(fam[1]); R = int(fam[2]); L2 = [row(fam[3 + r]) for r in range(R)]
wit = {}
for line in open(sys.argv[2]):
    if line.startswith('#'):
        continue
    f = line.rstrip('\n').split('\t')
    rr, l3 = f[1].split(' ', 1)
    wit[int(f[0])] = (int(rr), pairs(l3), f[2], f[3])
members = open(sys.argv[3]).read().splitlines()
by_key = {}                                # (second-layer class, third layer) -> MEMBERS line, filled on demand
lem10, lem11 = lemmas(sys.argv[4]), lemmas(sys.argv[5])
K = int(sys.argv[6]); random.seed(int(sys.argv[7]) if len(sys.argv) > 7 else 1)
ALLIN = range(1 << n)
checked = {'member': 0, 'residual': 0, 'direct': 0}
pool = members
if os.environ.get('ONLY') == 'direct':      # sample only prefixes of classes settled directly
    pool = [l for l in members if wit[int(l.split('|')[2].split()[0])][2] == 'direct']
sample = random.sample(pool, min(K, len(pool)))
need = set()
for line in sample:
    cl = int(line.split('|')[2].split()[0]); rr, rl3, how, w = wit[cl]
    if how == 'residual':
        m = re.match(r'prefix (\d+) (\[.*?\])', w); need.add((int(m.group(1)), tuple(pairs(m.group(2)))))
for line in members:
    r, l3, rest = line.split('|')
    k = (int(r), tuple(pairs(l3)))
    if k in need:
        by_key[k] = line


def member_ok(line):
    r, l3, rest = line.split('|')
    r = int(r); l3 = pairs(l3); f = list(map(int, rest.split()))
    cl, comp, perm = f[0], f[1], f[2:]
    rr, rl3, how, w = wit[cl]
    S = run(n, [L1, L2[r], l3], ALLIN)
    assert relabel(S, perm, comp, n) == run(n, [L1, L2[rr], rl3], ALLIN), ('member', line)
    return cl


for line in sample:
    cl = member_ok(line)
    rr, rl3, how, w = wit[cl]
    Srep = run(n, [L1, L2[rr], rl3], ALLIN)
    checked['member'] += 1
    if how == 'residual':
        m = re.match(r'prefix (\d+) (\[.*?\]) sentinel ([+-])inf at input (\d+), track end (\d+); '
                     r'10-channel lemma (\d+), complement (\d), perm ([\d ]+)$', w)
        pr, pl3, sign, s, e, lem, cc, pp = m.groups()
        assert member_ok(by_key[(int(pr), tuple(pairs(pl3)))]) == cl, ('settling prefix not in the class', line)
        v = 1 if sign == '+' else 0; s, e = int(s), int(e)
        T = run(n, [L1, L2[int(pr)], pairs(pl3)], [x for x in ALLIN if (x >> s) & 1 == v])
        assert all((u >> e) & 1 == v for u in T), ('track end', line)
        Rset = {(u & ((1 << e) - 1)) | ((u >> (e + 1)) << e) for u in T}
        ln, ll = lem10[int(lem)]
        assert relabel(Rset, list(map(int, pp.split())), int(cc), n - 1) == run(ln, ll, range(1 << ln)), ('residual', line)
        checked['residual'] += 1
    elif how == 'direct':
        m = re.match(r'11-channel lemma (\d+), complement (\d), perm ([\d ]+)$', w)
        lem, cc, pp = m.groups()
        ln, ll = lem11[int(lem)]
        assert relabel(Srep, list(map(int, pp.split())), int(cc), n) == run(ln, ll, range(1 << ln)), ('direct', line)
        checked['direct'] += 1
    else:
        raise SystemExit(f'class {cl} is not settled')
print(f'{len(sample)} random prefixes re-verified: {checked}')
