#!/usr/bin/env python3
"""structure.py -- what a node without residual reductions is made of (README §8.6).

usage: structure.py N T 'PREFIX_JSON' [--strengthen RUNS] [--no-layouts]

For the node EXT(N, PREFIX, T) it prints, all by SAT (run with the venv python, which has pysat):
  * blocks: the groups of channels that no comparator of the prefix joins, each block's order (the
    relations x_i <= x_j true on every output, as covers), and whether the outputs are exactly the
    combinations of the 0/1 vectors that respect each block's order;
  * job costs: fewest further layers for the whole node, for the blocks given sorted (merge only),
    and for each block left as it is while the others are given sorted;
  * weights: which single weight classes, and which minimal ranges of consecutive weights, have no
    T-layer sorter;
  * layouts: the equivalent nodes obtained by moving the blocks over the channels (each block keeps
    its internal order, so the prefix stays standard and the output set only changes by a channel
    permutation), and in how many of them one fixed value x_c = v (channel kept) leaves a set
    without a T-layer sorter. x_c = 1 on a maximal element is a +inf that must travel to channel
    N-1; x_c = 0 on a minimal element is a -inf that must travel to channel 0;
  * with --strengthen R: R greedy random runs that add order relations (anywhere) while the node
    stays without a T-layer sorter, printing the distinct maximal additions; and, exhaustively for
    each block, the maximal additions inside that block.
"""
import collections, itertools, json, os, random, sys, time
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sentinel_prover as sp
from irreducible import sortable


def blocks(n, P):
    par = list(range(n))

    def f(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a
    for L in P:
        for i, j in L:
            par[f(i)] = f(j)
    comps = collections.defaultdict(list)
    for c in range(n):
        comps[f(c)].append(c)
    return sorted(comps.values(), key=lambda c: (-len(c), c))


def order(n, X):
    return frozenset((a, b) for a in range(n) for b in range(n)
                     if a != b and all(((x >> a) & 1) <= ((x >> b) & 1) for x in X))


def covers(R, chans):
    return sorted((a, b) for a, b in R if a in chans and b in chans
                  and not any((a, c) in R and (c, b) in R for c in chans if c not in (a, b)))


def monotone(n, R):
    return frozenset(x for x in range(1 << n) if all(((x >> a) & 1) <= ((x >> b) & 1) for a, b in R))


def closure(R):
    R = set(R)
    while True:
        add = {(a, d) for a, b in R for c, d in R if b == c and a != d} - R
        if not add:
            return frozenset(R)
        R |= add


def mindepth(n, Y, tmax=8):
    for t in range(tmax + 1):
        if t == 0:
            if all(x == ((1 << n) - 1) ^ ((1 << (n - x.bit_count())) - 1) for x in Y):
                return 0
            continue
        if sortable(n, Y, t, seconds=300) == 'YES':
            return t
    return None


def sorted_block(n, X, G, R):
    """X with block G replaced by sorted patterns (G's order made a chain in channel order)."""
    chain = {(a, b) for a, b in itertools.combinations(G, 2)}
    return monotone(n, closure(set(R) | chain))


def layouts(n, P, B):
    sizes = [len(b) for b in B]

    def assign(free, k):
        if k == len(B):
            yield []
            return
        for S in itertools.combinations(free, sizes[k]):
            rest = [c for c in free if c not in S]
            for tail in assign(rest, k + 1):
                yield [S] + tail
    for parts in assign(list(range(n)), 0):
        m = {}
        for b, S in zip(B, parts):
            for c, p in zip(b, S):
                m[c] = p
        yield tuple(tuple(tuple(sorted((m[i], m[j]))) for i, j in L) for L in P), m


def fixed_values(args):
    n, t, P = args
    X = sp.outputs(n, P)
    return [(c, v) for c in range(n) for v in (0, 1)
            if sortable(n, frozenset(x for x in X if ((x >> c) & 1) == v), t, seconds=120) != 'YES']


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    n, t = int(args[0]), int(args[1])
    P = tuple(tuple(tuple(c) for c in L) for L in json.loads(args[2]))
    X = sp.outputs(n, P)
    R = order(n, X)
    B = blocks(n, P)
    t0 = time.time()
    print(f'node: n={n} t={t} prefix={json.dumps(P)}; {len(X)} outputs')
    # blocks
    for G in B:
        pats = {tuple((x >> c) & 1 for c in G) for x in X}
        print(f'  block {G}: {len(pats)} patterns; order (covers a<b): {covers(R, G)}')
    complete = monotone(n, R) == X
    print(f'  outputs = all 0/1 vectors respecting the order: {"yes" if complete else "no"}')
    # job costs
    big = [G for G in B if len({tuple((x >> c) & 1 for c in G) for x in X}) > len(G) + 1]
    if complete:
        merge = X
        for G in big:
            merge = sorted_block(n, merge, G, order(n, merge))
        print(f'  fewest layers: whole {mindepth(n, X)}; merge only (blocks sorted) {mindepth(n, merge)}')
        for G in big:
            Y = X
            for H in big:
                if H != G:
                    Y = sorted_block(n, Y, H, order(n, Y))
            print(f'    block {G} as it is, the others sorted: {mindepth(n, Y)}')
    # weights
    by = {w: frozenset(x for x in X if x.bit_count() == w) for w in range(n + 1)}
    res = {}
    for a in range(1, n):
        for b in range(a, n):
            res[(a, b)] = sortable(n, frozenset().union(*[by[w] for w in range(a, b + 1)]), t, seconds=120)
    single = [w for w in range(1, n) if res[(w, w)] != 'YES']
    minimal = [k for k, v in res.items() if v == 'NO'
               and all(res.get(k2) != 'NO' for k2 in [(k[0] + 1, k[1]), (k[0], k[1] - 1)] if k2[0] <= k2[1])]
    print(f'  weights: single classes without a {t}-layer sorter: {single or "none"}; '
          f'minimal ranges without one: {minimal} ({time.time() - t0:.0f}s)')
    # layouts
    if '--no-layouts' not in sys.argv:
        Ls = list(layouts(n, P, B))
        with Pool(os.cpu_count()) as pool:
            out = pool.map(fixed_values, [(n, t, Q) for Q, _ in Ls])
        stats = collections.Counter()
        good = 0
        for (Q, m), res2 in zip(Ls, out):
            good += bool(res2)
            inv = {p: c for c, p in m.items()}
            for c, v in res2:
                e = inv[c]
                if v == 1 and not any(a == e for a, b in R):
                    kind = f'+inf on element {e}, travel {n - 1 - c}'
                elif v == 0 and not any(b == e for a, b in R):
                    kind = f'-inf on element {e}, travel {c}'
                else:
                    kind = f'x = {v} on element {e} (not extreme)'
                stats[kind] += 1
        print(f'  layouts: {good} of {len(Ls)} have a fixed value without a sorter ({time.time() - t0:.0f}s)')
        for k, c in sorted(stats.items()):
            print(f'    {k}: {c} layouts')
    # strengthenings
    if '--strengthen' in sys.argv:
        runs = int(sys.argv[sys.argv.index('--strengthen') + 1])
        cache = {}

        def status(S):
            if S not in cache:
                cache[S] = sortable(n, monotone(n, S), t, seconds=120)
            return cache[S]
        base = closure(R)
        found = collections.Counter()
        for run in range(runs):
            rng = random.Random(run)
            S = base
            while True:
                cands = [(a, b) for a, b in itertools.permutations(range(n), 2) if (a, b) not in S and (b, a) not in S]
                rng.shuffle(cands)
                for a, b in cands:
                    S2 = closure(S | {(a, b)})
                    if not any((d, c) in S2 for c, d in S2) and status(S2) == 'NO':
                        S = S2
                        break
                else:
                    break
            added = covers(S, range(n))
            found[(len(monotone(n, S)), tuple(c for c in added if c not in R))] += 1
        print(f'  maximal added relations keeping no {t}-layer sorter ({runs} runs, {len(cache)} SAT calls):')
        for (nv, add), c in sorted(found.items()):
            print(f'    {list(add)} -> {nv} vectors (found {c} times)')
        for G in B:
            if len(G) < 2:
                continue
            frontier, seen, maximal = [base], {base}, []
            while frontier:
                nxt = []
                for S in frontier:
                    ext = False
                    for a, b in itertools.permutations(G, 2):
                        if (a, b) in S or (b, a) in S:
                            continue
                        S2 = closure(S | {(a, b)})
                        if any((d, c) in S2 for c, d in S2) or status(S2) != 'NO':
                            continue
                        ext = True
                        if S2 not in seen:
                            seen.add(S2)
                            nxt.append(S2)
                    if not ext:
                        maximal.append(S)
                frontier = nxt
            adds = sorted({tuple(c for c in covers(S, G) if c not in R) for S in maximal})
            print(f'    inside block {G} (exhaustive): maximal additions {[list(a) for a in adds]}')


if __name__ == '__main__':
    main()
