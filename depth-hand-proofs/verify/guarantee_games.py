#!/usr/bin/env python3
"""guarantee_games.py -- the two guarantee games of d13.md that need no channel identities.

Write tau0(c) for the least number of inputs whose zeros force channel c to 0, and tau1(c) for the least
number whose ones force it to 1.  For a comparator with inputs u, v (d13.md Lemma 16)
    tau0(min) = min(tau0(u), tau0(v)),  tau0(max) <= tau0(u) + tau0(v),
    tau1(max) = min(tau1(u), tau1(v)),  tau1(min) <= tau1(u) + tau1(v).
A game that applies these rules with "<=" read as "=" computes upper bounds z >= tau0 and m >= tau1.

1. The free game (n = 5..9).  Each channel carries (z, m); the ranks it can hold form the interval
   [tau0 - 1, n - tau1] (Lemma 15), which contains [z - 1, n - m].  A sorting network of depth d needs,
   after layer t, every rank in at most 2^(d-t) intervals (Lemma 15), so if no reachable multiset of
   labels passes, D(n) > d.  The rules ignore which channels the labels sit on, so multisets suffice.
   Starts after a maximal first layer (Tool B).  Expected: no multiset survives at depth D(n) - 1 for
   n = 5, 6, 7, 8 (killed after layers 4, 2, 3, 3), and for n = 9 at depth 6 some multiset survives
   every layer (the search stops at the first one after the last layer).
2. The free tau0 game (13 channels).  Values z only, all 1 at the start, and every matching in every
   layer, the first included (so no normal form is assumed).  Values are capped at 8, which keeps
   "z >= 8" exact; the last layer uses a closed formula (best_next), checked against the enumeration on
   the earlier layers.  Expected: at most 0, 0, 1, 3 channels with z >= 8 after layers 1, 2, 3, 4.  Since
   z >= tau0, every network on 13 channels has h_3 <= 1 and h_4 <= 3, where h counts the channels with
   tau0 >= 8 (certainly above the median), and by the mirror image l_3 <= 1 and l_4 <= 3.

3. Both games are too weak for 13 channels.  For each, an explicit 6-layer prefix (found by search) on
   which the game keeps every rank within 2^(8-t) intervals after every layer t <= 6, as a depth-8
   sorter would need, while the exact intervals (brute force) put some rank in 8 or more channels.
   Here the free game runs on the channels of the given network.  The witness game keeps one
   zero-forcing set Z and one one-forcing set M per channel: min takes the smaller Z (the first on a
   tie) and the union of the M's, max the union of the Z's and the smaller M (see witness_game.c).

Needs only python3.  Exit status 0 iff every expected value is found.  About 25 seconds.
usage: python3 guarantee_games.py
"""
import sys


def one_layer(ms, combine):
    """every multiset that one layer (any matching) can make from the multiset ms (a sorted tuple).
    combine(x, y) gives the labels of (min, max).  Pairs are formed up to swapping equal labels."""
    out = set()

    def rec(rest, acc):
        if not rest:
            out.add(tuple(sorted(acc)))
            return
        x, r = rest[0], rest[1:]
        rec(r, acc + [x])                                       # x idle
        seen = set()
        for i, y in enumerate(r):
            if y not in seen:
                seen.add(y)
                rec(r[:i] + r[i + 1:], acc + list(combine(x, y)))
    rec(list(ms), [])
    return out


def free_game(n, d):
    """returns the layer after which nothing survives, or None if something survives all d layers."""
    def combine(x, y):                  # tau0, tau1 <= n, so capping at n keeps the bounds sound
        (z1, m1), (z2, m2) = x, y
        return (min(z1, z2), min(n, m1 + m2)), (min(n, z1 + z2), min(m1, m2))
    start = [(1, 2), (2, 1)] * (n // 2) + [(1, 1)] * (n % 2)
    layer = {tuple(sorted(start))}
    for t in range(2, d + 1):
        cap = 1 << (d - t)
        nxt = set()
        for st in layer:
            for s in one_layer(st, combine):
                if cap >= n or all(sum(1 for z, m in s if z - 1 <= k <= n - m) <= cap for k in range(n)):
                    nxt.add(s)
                    if t == d:
                        print(f'    after layer {t} (at most {cap} channel per rank): a multiset survives:', s, flush=True)
                        return None
        layer = nxt
        print(f'    after layer {t} (at most {cap} channels per rank): {len(layer)} multisets survive', flush=True)
        if not layer:
            return t
    return None


def best_next(s, top=8):
    """the most values >= top that one more layer can make from the multiset s.  A value at top stays at
    top whatever it meets, and pairing it with x < top makes one top value and x, as leaving both idle
    does.  So top values gain nothing from comparators, and each new one is the max of a pair of smaller
    values with sum >= top: the answer is the number of top values plus a maximum set of disjoint such
    pairs, found greedily (pair the largest value left with the smallest that reaches top)."""
    a = sorted(v for v in s if v < top)
    i, j, pairs = 0, len(a) - 1, 0
    while i < j:
        if a[i] + a[j] >= top:
            pairs += 1
            j -= 1
        i += 1
    return s.count(top) + pairs


def tau0_game(n=13, rounds=4, top=8):
    """layers 1..rounds-1 by enumerating every matching; the last layer by best_next, which is checked
    against the enumeration on the layers before it."""
    best = []
    layer = {tuple([1] * n)}
    for t in range(1, rounds + 1):
        predicted = max(best_next(s, top) for s in layer)
        if t == rounds:
            best.append(predicted)
            print(f'    after layer {t}: at most {predicted} channels with z >= {top} (by best_next)', flush=True)
            break
        nxt = set()
        for s in layer:
            nxt |= one_layer(s, lambda x, y: (min(x, y), min(top, x + y)))
        layer = nxt
        best.append(max(s.count(top) for s in layer))
        print(f'    after layer {t}: {len(layer)} multisets; at most {best[-1]} channels with z >= {top}'
              f' (best_next predicted {predicted})', flush=True)
        if predicted != best[-1]:
            print('    best_next DISAGREES with the enumeration')
            return None
    return best



FREE_PASSES = [[(0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11)],
               [(0, 9), (1, 6), (2, 10), (3, 12), (4, 7), (5, 8)],
               [(0, 10), (1, 4), (2, 5), (3, 8), (6, 9), (7, 12)],
               [(0, 3), (1, 11), (2, 7), (4, 5), (6, 10), (8, 9)],
               [(1, 4), (2, 10), (3, 5), (6, 9), (7, 8), (11, 12)],
               [(0, 8), (1, 6), (2, 12), (3, 4), (5, 11), (7, 10)]]
WITNESS_PASSES = [[(0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11)],
                  [(0, 8), (1, 9), (2, 10), (3, 5), (4, 6), (7, 11)],
                  [(0, 2), (1, 3), (5, 9), (6, 11), (7, 10), (8, 12)],
                  [(1, 4), (2, 6), (3, 12), (5, 10), (7, 8), (9, 11)],
                  [(0, 1), (2, 7), (3, 10), (4, 8), (5, 6), (9, 12)],
                  [(1, 3), (4, 5), (6, 8), (7, 9), (11, 12)]]


def worst_rank(intervals, n):
    return max(sum(1 for a, b in intervals if a <= k <= b) for k in range(n))


def game_on_network(net, n, kind):
    """the game's worst rank after each layer of net."""
    if kind == 'free':
        z, m = [1] * n, [1] * n
    else:
        Z, M = [1 << c for c in range(n)], [1 << c for c in range(n)]
    size = lambda x: bin(x).count('1')
    worst = []
    for L in net:
        for a, b in L:                                          # a < b: a receives the min
            if kind == 'free':
                z[a], z[b] = min(z[a], z[b]), min(n, z[a] + z[b])
                m[a], m[b] = min(n, m[a] + m[b]), min(m[a], m[b])
            else:
                Z[a], Z[b] = (Z[a] if size(Z[a]) <= size(Z[b]) else Z[b]), Z[a] | Z[b]
                M[a], M[b] = M[a] | M[b], (M[a] if size(M[a]) <= size(M[b]) else M[b])
        if kind == 'free':
            iv = [(z[c] - 1, n - m[c]) for c in range(n)]
        else:
            iv = [(size(Z[c]) - 1, n - size(M[c])) for c in range(n)]
        worst.append(worst_rank(iv, n))
    return worst


def exact_worst(net, n):
    tau0, tau1 = [n + 1] * n, [n + 1] * n
    for x in range(1 << n):
        y = x
        for L in net:
            for a, b in L:
                if (y >> a & 1) and not (y >> b & 1):
                    y ^= (1 << a) | (1 << b)
        w = bin(x).count('1')
        for c in range(n):
            if y >> c & 1:
                tau1[c] = min(tau1[c], w)
            else:
                tau0[c] = min(tau0[c], n - w)
    return worst_rank([(tau0[c] - 1, n - tau1[c]) for c in range(n)], n)


ok = True
print('free game: is depth D(n) - 1 refuted by the size rules alone?')
for n, d, expect in [(5, 4, 4), (6, 4, 2), (7, 5, 3), (8, 5, 3), (9, 6, None)]:
    print(f'  n = {n}, depth {d}:')
    got = free_game(n, d)
    good = got == expect
    ok &= good
    print(f'  n = {n}, depth {d}: ' + (f'refuted after layer {got}' if got else 'NOT refuted (some multiset survives)')
          + ('' if good else f'   UNEXPECTED (expected {expect})'))
print('free tau0 game on 13 channels, every matching in every layer:')
best = tau0_game()
good = best == [0, 0, 1, 3]
ok &= good
print('  hence h_3 <= 1, h_4 <= 3, and by the mirror image l_3 <= 1, l_4 <= 3: h_4 + l_4 <= 6'
      if good else f'  UNEXPECTED: {best}')
print('13 channels, depth 8: prefixes that the games let through')
for kind, net in (('free', FREE_PASSES), ('witness', WITNESS_PASSES)):
    worst = game_on_network(net, 13, kind)
    caps = [1 << (8 - t) for t in range(1, 7)]
    passes = all(w <= c for w, c in zip(worst, caps))
    real = exact_worst(net, 13)
    good = passes and real > 4
    ok &= good
    print(f'  {kind} game: most intervals at one rank after layers 1-6 = {worst} (limits {caps});'
          f' exact after layer 6: {real}' + ('' if good else '   UNEXPECTED'))
print('all expected values found' if ok else 'SOME VALUE DIFFERS')
sys.exit(0 if ok else 1)
