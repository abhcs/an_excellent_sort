#!/usr/bin/env python3
"""exc13.py: four sentinels on a 13-channel network, chosen together.

Four sentinels whose tracks absorb max(0, c_t - 2) distinct comparators in each of the first three
layers (c_t = size of layer t) leave a 9-channel sorter of the same depth whose first three layers
have <= 2 comparators each (Fact B).  So a 13-channel depth-8 sorter with such a 4-tuple contradicts
SS(9,8,2,3).  This script finds every three-layer prefix with NO such 4-tuple ("4-exceptional").

L1 is the maximal normal form (6 comparators, channel 6 idle).  Since c_1 = 6, the four sentinels
start on four different L1 comparators (+inf on a max end, -inf on a min end).  L2 runs over all
matchings without an L1 pair, up to the symmetries of L1; for each, a SAT call per size c of L3
decides whether some L3 blocks every surviving 4-tuple.  Blocking only depends on where the
tracks are after L2: a tuple at positions T absorbs used(T) - pairs(T) comparators of L3.

usage: exc13.py [--m 3] [OUT.json]
"""
import itertools, json, sys, time
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

n, a = 13, 6
L1 = [(0, 1), (2, 3), (4, 5), (7, 8), (9, 10), (11, 12)]
need = lambda c: max(0, c - 2)


def matchings(n, kmax, banned=frozenset()):
    out = []
    def rec(start, used, cur):
        out.append(tuple(cur))
        if len(cur) == kmax:
            return
        for i in range(start, n):
            if used >> i & 1:
                continue
            for j in range(i + 1, n):
                if used >> j & 1 or (i, j) in banned:
                    continue
                cur.append((i, j))
                rec(i + 1, used | (1 << i) | (1 << j), cur)
                cur.pop()
    rec(0, 0, [])
    return out


def group():
    G = []
    for pp in itertools.permutations(range(len(L1))):
        m = {6: 6}
        for i, j in enumerate(pp):
            m[L1[i][0]] = L1[j][0]
            m[L1[i][1]] = L1[j][1]
        G.append(m)
    G += [{k: n - 1 - m[k] for k in range(n)} for m in G]
    return G


def img(g, L):
    return tuple(sorted(tuple(sorted((g[x], g[y]))) for x, y in L))


def step(layer, tracks):
    """tracks: list of (pos, sign); returns new tracks and #distinct comparators absorbed."""
    where = {}
    for c in layer:
        where[c[0]] = c
        where[c[1]] = c
    hit = {}
    for k, (p, s) in enumerate(tracks):
        c = where.get(p)
        if c is not None:
            hit.setdefault(c, []).append(k)
    new = list(tracks)
    for c, ks in hit.items():
        if len(ks) == 1:
            k = ks[0]
            new[k] = (c[1] if tracks[k][1] > 0 else c[0], tracks[k][1])
        else:                                         # two sentinels in one comparator
            k1, k2 = ks
            s1, s2 = tracks[k1][1], tracks[k2][1]
            if s1 != s2:
                hi_k, lo_k = (k1, k2) if s1 > 0 else (k2, k1)
                new[hi_k] = (c[1], tracks[hi_k][1])
                new[lo_k] = (c[0], tracks[lo_k][1])
    return new, len(hit)


def alive_sets(L2):
    out = set()
    for comps in itertools.combinations(L1, 4):
        for signs in itertools.product((1, -1), repeat=4):
            tr = [(hi if s > 0 else lo, s) for (lo, hi), s in zip(comps, signs)]
            tr, k1 = step(L1, tr)
            assert k1 == 4
            tr, k2 = step(list(L2), tr)
            if k2 >= need(len(L2)):
                out.add(frozenset(p for p, _ in tr))
    return out


def exceptional_L3(alive, c, enumerate_all=False, limit=100000):
    """L3 matchings of exactly c comparators with used(T) - pairs(T) <= c - 3 for all T."""
    pairs = list(itertools.combinations(range(n), 2))
    x = {p: k + 1 for k, p in enumerate(pairs)}
    top = len(pairs)
    used = {}
    cls = []
    for ch in range(n):
        top += 1
        used[ch] = top
        inc = [x[p] for p in pairs if ch in p]
        cls.append([-top] + inc)
        for v in inc:
            cls.append([top, -v])
        enc = CardEnc.atmost(lits=inc, bound=1, top_id=top, encoding=EncType.pairwise)
        cls += enc.clauses
    enc = CardEnc.equals(lits=list(x.values()), bound=c, top_id=top, encoding=EncType.seqcounter)
    cls += enc.clauses
    top = max(top, enc.nv)
    for T in alive:
        T = sorted(T)
        lits = [used[p] for p in T] + [-x[(p, q)] for p, q in itertools.combinations(T, 2)]
        enc = CardEnc.atmost(lits=lits, bound=c - 3 + 6, top_id=top, encoding=EncType.seqcounter)
        cls += enc.clauses
        top = max(top, enc.nv)
    found = []
    with Solver(name='cadical195', bootstrap_with=cls) as S:
        while S.solve():
            mdl = set(v for v in S.get_model() if v > 0)
            L3 = tuple(p for p in pairs if x[p] in mdl)
            found.append(L3)
            if not enumerate_all or len(found) >= limit:
                break
            S.add_clause([-x[p] for p in L3])
    return found


def main():
    m = 3
    out = sys.argv[1] if len(sys.argv) > 1 else None
    t0 = time.time()
    G = group()
    banned = frozenset(L1)
    allL2 = matchings(n, a, banned)
    seen, reps = set(), []
    for L in allL2:
        k = tuple(sorted(L))
        if k in seen:
            continue
        orb = {img(g, k) for g in G}
        seen |= orb
        reps.append((k, len(orb)))
    print(f'{len(allL2)} second layers, {len(reps)} classes ({time.time() - t0:.0f}s)', flush=True)
    bad = []
    for r, (L2, osz) in enumerate(reps):
        al = alive_sets(L2)
        if not al:
            bad.append({'l2': L2, 'orbit': osz, 'alive': 0, 'L3': 'any with >= 3 comparators'})
            continue
        exc = {}
        for c in range(3, a + 1):
            f = exceptional_L3(al, c)
            if f:
                exc[c] = f[0]
        if exc:
            bad.append({'l2': L2, 'orbit': osz, 'alive': len(al), 'example_L3': exc})
        if r % 200 == 0:
            print(f'  {r}/{len(reps)} classes, {len(bad)} with exceptional L3 ({time.time() - t0:.0f}s)', flush=True)
    print(f'classes with a 4-exceptional L3: {len(bad)} of {len(reps)} ({time.time() - t0:.0f}s)')
    for b in bad[:20]:
        print(json.dumps(b))
    if out:
        json.dump({'L1': L1, 'classes': len(reps), 'bad': bad}, open(out, 'w'))


if __name__ == '__main__':
    main()
