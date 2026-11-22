#!/usr/bin/env python3
"""prefix_cert.py -- hand-checkable certificates for sparse-start statements (no SAT).

SS(n, d, a, m): no n-channel sorting network of depth d has at most a comparators in each of its
first m layers.  Only the prefix P = (L1..Lm) is constrained; the last f = d - m layers are free.
A certificate for a prefix is a set of infinities (channel, level): positive levels are +inf of
increasing size, negative ones -inf.  Their tracks through P are forced.  The comparisons between two
real inputs inside P form a comparator DAG on the real tracks; let h be its height (longest chain of
comparisons sharing a track, in time order) -- the DAG can be rescheduled into h layers.  So the r
real inputs are sorted by a network of depth at most h + f, and the certificate applies one rule:
  D      h + f < D(r)                                   (D(r) proved by hand for r <= 10)
  P7     r = 7, the DAG schedules into 6 - f layers whose first has at most one comparator   (P7)
  SS7    r = 7, f = 4, at most 3 real comparisons in P: as three one-comparator layers they give a
         depth-7 7-sorter with at most one comparator in each of its first three layers  (SS(7,7,1,3))
Every rule is a statement proved by hand in this repository (README, h9.md section 7.5).
"""
import itertools, json, random, sys, time

D = {1: 0, 2: 1, 3: 3, 4: 3, 5: 5, 6: 5, 7: 6, 8: 6, 9: 7, 10: 7}


def residual_dag(n, layers, sents):
    """Return list of real-real comparisons as (layer, track_a, track_b), tracks = input ids."""
    owner = list(range(n))           # channel -> input id
    val = {ch: v for ch, v in sents}  # input id (= start channel) -> level
    out = []
    for t, L in enumerate(layers):
        for i, j in L:
            a, b = owner[i], owner[j]
            va, vb = val.get(a, 0), val.get(b, 0)
            if a in val or b in val:
                if va > vb:
                    owner[i], owner[j] = b, a
                continue
            out.append((t, a, b))
    return out


def height_and_first(dag):
    """Height of the comparison DAG (chains through shared tracks) and, for a schedule of that
    height, the fewest comparisons in its first layer (comparisons that must start at depth 1)."""
    last = {}
    depth = []
    for k, (t, a, b) in enumerate(dag):
        d0 = max(last.get(a, 0), last.get(b, 0)) + 1
        depth.append(d0)
        last[a] = last[b] = d0
    h = max(depth) if depth else 0
    # latest-start schedule: comparisons with no successor chain long enough can move later.
    # A comparison must be in layer 1 of every height-h schedule iff its longest chain through it
    # (before + after) has length h and it has no predecessor.
    after = [0] * len(dag)
    nxt = {}
    for k in range(len(dag) - 1, -1, -1):
        t, a, b = dag[k]
        after[k] = max(nxt.get(a, 0), nxt.get(b, 0)) + 1
        nxt[a] = nxt[b] = after[k]
    forced_first = sum(1 for k in range(len(dag)) if depth[k] == 1 and after[k] == h)
    return h, forced_first


def certify(n, d, a, m, layers, kmax=4):
    f = d - m
    for k in range(0, kmax + 1):
        r = n - k
        if r < 1:
            break
        for chans in itertools.combinations(range(n), k):
            for signs in itertools.product((1, -1), repeat=k):
                levels = []
                cp = cn = 0
                for s in signs:
                    if s > 0:
                        cp += 1; levels.append(cp)
                    else:
                        cn += 1; levels.append(-cn)
                for perm in set(itertools.permutations(levels)):
                    sents = list(zip(chans, perm))
                    dag = residual_dag(n, layers, sents)
                    h, ff = height_and_first(dag)
                    if r in D and h + f < D[r]:
                        return ('D', k, sents, h)
                    if r == 7 and h + f <= 6 and ff <= 1:
                        return ('P7', k, sents, h)
                    if r == 7 and f == 4 and len(dag) <= 3:
                        return ('SS7', k, sents, len(dag))
    return None


def rand_matching(n, size, rng, banned=()):
    while True:
        ch = list(range(n)); rng.shuffle(ch)
        L = [tuple(sorted(ch[2 * i:2 * i + 2])) for i in range(size)]
        if not set(L) & set(banned):
            return sorted(L)


if __name__ == '__main__':
    sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
    from thinsat import middle_layer
    n, d, a, m, trials = map(int, sys.argv[1:6])
    rng = random.Random(7)
    L1 = middle_layer(n, a)
    stats, fails, t0 = {}, [], time.time()
    for _ in range(trials):
        layers = [L1] + [rand_matching(n, rng.choice(range(a + 1)) if rng.random() < 0.2 else a, rng, L1)
                         for _ in range(m - 1)]
        c = certify(n, d, a, m, layers)
        key = 'none' if c is None else f'{c[0]}/k={c[1]}'
        stats[key] = stats.get(key, 0) + 1
        if c is None:
            fails.append(layers)
    print(json.dumps({'statement': f'SS({n},{d},{a},{m})', 'random_prefixes': trials, 'certificates': stats,
                      'seconds': round(time.time() - t0, 1), 'uncertified_example': fails[:2]}))
