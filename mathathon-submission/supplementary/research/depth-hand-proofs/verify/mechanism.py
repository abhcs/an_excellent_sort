"""Run the constructions of Theorem 2 and Lemma 4 on actual sorting networks and check, by brute
force over the real inputs, that they do what the proofs say:
  Theorem 2: after filling layer 1, the placement X of Lemma 1 leaves ceil(n/2) reals that never
             meet in layers 1-2, the network still sorts with the infinities in place, and the reals
             meet in at most depth-2 layers.
  Lemma 4:   on 7 channels, +inf on hi_i and -inf on lo_j (i != j, chosen as in the proof) leave
             5 reals that meet in at most one comparator in each of layers 1 and 2.
Test networks: Batcher's odd-even merge sort for n = 3..12 under random relabelling + untangling,
plus the depth-optimal networks for n <= 9 from Dobbelaere's list."""
import itertools
import random
from netlib import sorts

INF = 10 ** 9

DOBBELAERE = {  # depth-optimal networks (bertdobbelaere.github.io/sorting_networks_extended.html)
    5: [[(0, 3), (1, 4)], [(0, 2), (1, 3)], [(0, 1), (2, 4)], [(1, 2), (3, 4)], [(2, 3)]],
    6: [[(0, 5), (1, 3), (2, 4)], [(1, 2), (3, 4)], [(0, 3), (2, 5)], [(0, 1), (2, 3), (4, 5)], [(1, 2), (3, 4)]],
    7: [[(0, 6), (2, 3), (4, 5)], [(0, 2), (1, 4), (3, 6)], [(0, 1), (2, 5), (3, 4)], [(1, 2), (4, 6)],
        [(2, 3), (4, 5)], [(1, 2), (3, 4), (5, 6)]],
    8: [[(0, 2), (1, 3), (4, 6), (5, 7)], [(0, 4), (1, 5), (2, 6), (3, 7)], [(0, 1), (2, 3), (4, 5), (6, 7)],
        [(2, 4), (3, 5)], [(1, 4), (3, 6)], [(1, 2), (3, 4), (5, 6)]],
    9: [[(0, 3), (1, 7), (2, 5), (4, 8)], [(0, 7), (2, 4), (3, 8), (5, 6)], [(0, 2), (1, 3), (4, 5), (7, 8)],
        [(1, 4), (3, 6), (5, 7)], [(0, 1), (2, 4), (3, 5), (6, 8)], [(2, 3), (4, 5), (6, 7)],
        [(1, 2), (3, 4), (5, 6)]],
}


def batcher(n):
    comps, t = [], 1
    while (1 << t) < n:
        t += 1
    p = 1 << (t - 1)
    while p > 0:
        q, r, d = 1 << (t - 1), 0, p
        while d > 0:
            comps += [(i, i + d) for i in range(n - d) if (i & p) == r]
            d, q, r = q - p, q >> 1, p
        p >>= 1
    layers, last = [], [-1] * n
    for (a, b) in comps:
        L = max(last[a], last[b]) + 1
        while len(layers) <= L:
            layers.append([])
        layers[L].append((a, b))
        last[a] = last[b] = L
    return layers


def relabel_untangle(layers, n, rng):
    """Random channel relabelling, then Knuth's untangling: a standard network that still sorts."""
    pi = list(range(n))
    rng.shuffle(pi)
    perm, out = list(range(n)), []
    for L in layers:
        out.append([])
        for (a, b) in L:
            a2, b2 = perm[pi[a]], perm[pi[b]]
            if a2 > b2:  # swap the roles of channels a2, b2 from here on
                ia, ib = perm.index(a2), perm.index(b2)
                perm[ia], perm[ib] = perm[ib], perm[ia]
                a2, b2 = b2, a2
            out[-1].append((a2, b2))
    return out


def fill_first_layer(layers, n):
    used = {c for e in layers[0] for c in e}
    idle = [c for c in range(n) if c not in used]
    return [list(layers[0]) + [(idle[2 * i], idle[2 * i + 1]) for i in range(len(idle) // 2)]] + \
           [list(L) for L in layers[1:]]


def lemma1_X(L1, L2, n):
    """Proper 2-colouring of L1 u L2, one class per component, avoiding the L1-idle channel."""
    adj = {c: [] for c in range(n)}
    for (a, b) in L1 + L2:
        adj[a].append(b)
        adj[b].append(a)
    on_L1 = {c for e in L1 for c in e}
    colour, X = {}, set()
    for start in [c for c in range(n) if c not in on_L1] + list(range(n)):
        if start in colour:
            continue
        colour[start], stack, comp = 0, [start], [start]
        while stack:
            v = stack.pop()
            for w in adj[v]:
                if w not in colour:
                    colour[w] = 1 - colour[v]
                    stack.append(w)
                    comp.append(w)
        X |= {v for v in comp if colour[v] == 1}
    return X


def simulate(layers, n, inf_at, max_perms=5040, rng=None):
    """Run every (or many) orderings of the reals; return the set of layers where two reals meet,
    and assert that the output is sorted."""
    reals = [c for c in range(n) if c not in inf_at]
    r = len(reals)
    perms = itertools.permutations(range(r)) if r <= 7 else (rng.sample(range(r), r) for _ in range(max_perms))
    meet = set()
    for p in perms:
        x = [0] * n
        for c, v in inf_at.items():
            x[c] = v
        for c, v in zip(reals, p):
            x[c] = v
        for t, L in enumerate(layers):
            for (a, b) in L:
                if abs(x[a]) < INF and abs(x[b]) < INF:
                    meet.add(t)
                if x[a] > x[b]:
                    x[a], x[b] = x[b], x[a]
        assert x == sorted(x), 'network failed to sort with sentinels'
    return meet, r


def check_theorem2(layers, n, rng):
    layers = fill_first_layer(layers, n)
    assert sorts(layers, n)
    L1, L2 = layers[0], layers[1]
    X = lemma1_X(L1, L2, n)
    assert all(len(X & set(e)) == 1 for e in L1) and all(X & set(e) for e in L2)
    inf_at = {}
    for (a, b) in L1:
        if b in X:
            inf_at[b] = INF
        else:
            inf_at[a] = -INF
    meet, r = simulate(layers, n, inf_at, rng=rng)
    assert r == (n + 1) // 2 and not meet & {0, 1} and len(meet) <= len(layers) - 2
    return r, len(layers), len(meet)


def check_lemma4(layers, rng):
    n = 7
    layers = fill_first_layer(layers, n)
    L1, L2 = layers[0], layers[1]
    for (i, j) in itertools.permutations(range(3), 2):
        hi, lo = max(L1[i]), min(L1[j])
        X = {hi, lo}
        if sum(1 for (a, b) in L2 if a not in X and b not in X) <= 1:
            meet_count = []
            reals_meet = {0: 0, 1: 0}
            # count real-real comparators in layers 1, 2 (they are input independent)
            cfg_pos = {hi: INF, lo: -INF}
            meet, r = simulate(layers, n, cfg_pos, rng=rng)
            x = {c: (INF if c == hi else -INF if c == lo else 0) for c in range(n)}
            for t in (0, 1):
                cnt = 0
                for (a, b) in layers[t]:
                    if x[a] == 0 and x[b] == 0:
                        cnt += 1
                    if x[a] > x[b]:
                        x[a], x[b] = x[b], x[a]
                reals_meet[t] = cnt
            assert reals_meet[0] == 1 and reals_meet[1] <= 1 and r == 5
            return (i, j)
    raise AssertionError('Lemma 4 found no good pair')


if __name__ == '__main__':
    rng = random.Random(2026)
    for n in range(3, 13):
        base = batcher(n)
        for _ in range(30):
            r, d, u = check_theorem2(relabel_untangle(base, n, rng), n, rng)
        print(f'Theorem 2, n={n:2d}: 30 networks of depth {d}; {r} reals never meet in layers 1-2 '
              f'and meet in {u} <= {d - 2} later layers')
    for n, net in DOBBELAERE.items():
        r, d, u = check_theorem2(net, n, rng)
        print(f'Theorem 2, depth-optimal {n}-sorter (depth {d}): {r} reals meet in {u} layers, so D({r}) <= {u}')
    nets7 = [DOBBELAERE[7]] + [relabel_untangle(batcher(7), 7, rng) for _ in range(200)]
    for net in nets7:
        check_lemma4(net, rng)
    print(f'Lemma 4: {len(nets7)} sorting networks on 7 channels, each pruned to 5 reals that meet at most '
          f'once in each of layers 1 and 2, still sorted')
