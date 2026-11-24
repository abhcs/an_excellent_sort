"""Minimum-size terms and clauses of the prefix channels (the witness families that suffice, section 7.4).
usage: EXC.json KEY IDX..."""
import json, sys
d = json.load(open(sys.argv[1])); n = d['n']


def tables(pre):
    out = []
    for x in range(1 << n):
        t = x
        for L in pre:
            for i, j in L:
                if (t >> i) & 1 and not (t >> j) & 1:
                    t ^= (1 << i) | (1 << j)
        out.append(t)
    return out


def minfam(pre, c, clauses):
    tab = tables(pre)
    sets = []
    for x in range(1 << n):
        v = (tab[x] >> c) & 1
        if clauses and v:
            continue
        if not clauses and not v:
            continue
        S = (~x & ((1 << n) - 1)) if clauses else x
        sets.append(S)
    m = min(bin(s).count('1') for s in sets)
    return m, sorted({s for s in sets if bin(s).count('1') == m})


def fmt(s):
    return '{' + ''.join(str(i) for i in range(n) if s >> i & 1) + '}'


for idx in map(int, sys.argv[3:]):
    pre = d[sys.argv[2]][idx]
    print(f'prefix {idx}: {pre}')
    for c in range(n):
        a, T = minfam(pre, c, False)
        b, Z = minfam(pre, c, True)
        coreT = (1 << n) - 1
        for s in T: coreT &= s
        coreZ = (1 << n) - 1
        for s in Z: coreZ &= s
        print(f'   ch{c}: interval [{b-1},{n-a}]  min terms (a={a}) {" ".join(fmt(s) for s in T):30s} core {fmt(coreT):8s} | '
              f'min clauses (b={b}) {" ".join(fmt(s) for s in Z):30s} core {fmt(coreZ)}')
