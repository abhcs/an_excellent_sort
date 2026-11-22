#!/usr/bin/env python3
"""split_profile.py -- what happens one split below a node (README §8.7).

usage: split_profile.py N T 'PREFIX_JSON' [--track C+|C-] [--deep]

Splits EXT(N, PREFIX, T) on its next layer the way sprove.py does (every non-empty layer of
non-redundant comparators; children grouped up to a channel permutation and complement) and asks,
by SAT, for every child class:
  * quick: some single-sentinel residual has height h with h + (T-1) < D(N-1);
  * residual: some single-sentinel residual has no (T-1)-layer completion. One sentinel is enough to
    test: if a residual of S plus one more sentinel has no completion, neither has the residual of S;
  * open: neither; the child needs a split of its own.
With --track C-: also counts the children whose residual of that one sentinel has no completion.
These are exactly the children that the tracked node (inputs restricted to x_C = -inf, all
channels kept) can close by a residual, since a tracked child can only drop its sentinel.
With --deep: for each child closed by a residual, does that residual close in one step as well?
"""
import collections, json, os, sys, time
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sentinel_prover as sp
from sprove import inv_hash
from irreducible import sortable

DLOW = {1: 0, 2: 1, 3: 3, 4: 3, 5: 5, 6: 5, 7: 6, 8: 6, 9: 7, 10: 7, 11: 8, 12: 8}


def children(n, P):
    X = sp.outputs(n, P)
    nonred = [(i, j) for i in range(n) for j in range(i + 1, n)
              if any((x >> i) & 1 and not (x >> j) & 1 for x in X)]
    layers = []

    def gen(start, used, cur):
        if cur:
            layers.append(tuple(cur))
        for k in range(start, len(nonred)):
            i, j = nonred[k]
            if used >> i & 1 or used >> j & 1:
                continue
            cur.append((i, j))
            gen(k + 1, used | (1 << i) | (1 << j), cur)
            cur.pop()
    gen(0, 0, [])
    classes = {}
    for L in layers:
        Y = frozenset(sp.apply_layer(L, x) for x in X)
        bucket = classes.setdefault((inv_hash(Y, n), len(Y)), [])
        for rep in bucket:
            if rep[1] == Y or sp.equivalent(rep[1], Y, n):
                rep[2] += 1
                break
        else:
            bucket.append([L, Y, 1])
    return layers, [rep for b in classes.values() for rep in b]


_cache = {}


def residual_status(r, R, h, t):
    if h + t < DLOW[r]:
        return 'quick'
    XR = sp.outputs(r, R)
    if XR not in _cache:
        _cache[XR] = sortable(r, XR, t, seconds=120)
    return 'residual' if _cache[XR] == 'NO' else ('open' if _cache[XR] == 'YES' else 'unknown')


def one_step(n, P, t):
    """Best single-sentinel closure of EXT(n, P, t): ('quick'|'residual'|'open', S, R)."""
    best = ('open', None, None)
    for c in range(n):
        for s in '+-':
            r, R, h, _, _ = sp.residual2(n, P, {c: s})
            st = residual_status(r, R, h, t)
            if st == 'quick':
                return st, {c: s}, R
            if st == 'residual' and best[0] == 'open':
                best = (st, {c: s}, R)
    return best


def profile(args):
    n, P, t, track, deep = args
    st, S, R = one_step(n, P, t)
    tracked = None
    if track:
        c, s = track
        r, R2, h, _, _ = sp.residual2(n, P, {c: s})
        tracked = residual_status(r, R2, h, t) in ('quick', 'residual')
    deeper = None
    if deep and st == 'residual':
        deeper = one_step(n - 1, R, t)[0]
    return st, tracked, deeper


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    n, t = int(args[0]), int(args[1])
    P = tuple(tuple(tuple(c) for c in L) for L in json.loads(args[2]))
    track = None
    if '--track' in sys.argv:
        v = sys.argv[sys.argv.index('--track') + 1]
        track = (int(v[:-1]), v[-1])
    deep = '--deep' in sys.argv
    t0 = time.time()
    layers, reps = children(n, P)
    print(f'node: n={n} t={t} prefix={json.dumps(P)}')
    print(f'  {len(layers)} non-empty layers of non-redundant comparators, {len(reps)} child classes '
          f'({time.time() - t0:.0f}s)')
    work = [(n, P + (L,), t - 1, track, deep) for L, _, _ in reps]
    with Pool(os.cpu_count()) as pool:
        res = pool.map(profile, work, chunksize=4)
    cnt = collections.Counter(st for st, _, _ in res)
    print(f'  child classes closed by one sentinel: quick {cnt["quick"]}, residual without completion '
          f'{cnt["residual"]}; open {cnt["open"]}; unknown {cnt["unknown"]} ({time.time() - t0:.0f}s)')
    if track:
        k = sum(1 for _, tr, _ in res if tr)
        home = sum(1 for L, _, _ in reps if (0, track[0]) in L) if track[1] == '-' else \
            sum(1 for L, _, _ in reps if (track[0], n - 1) in L)
        print(f'  tracked {track[0]}{track[1]}: {k} child classes close by dropping the sentinel '
              f'(the only residual a tracked child has); {len(reps) - k} do not; '
              f'{home} classes bring it home in this layer')
    if deep:
        d = collections.Counter(dp for st, _, dp in res if st == 'residual')
        print(f'  residuals of the closed children, one step further: {dict(d)}')


if __name__ == '__main__':
    main()
