#!/usr/bin/env python3
"""descent.py -- the sentinel descent of README section 4, run on actual networks (positive control).

Given a sorting network on n channels, repeatedly: pad the first layer to a comparators (Fact A),
pick a sentinel whose track is good for layers 1-3 (track lemma), delete it (Fact B), untangle the
residual into a standard network, and check by brute force that it sorts and that its first three
layers have at most a-1 comparators.
"""
import itertools
import json
import math
import sys


def sorts(n, layers):
    for x in range(1 << n):
        v = [(x >> i) & 1 for i in range(n)]
        for L in layers:
            for i, j in L:
                if v[i] > v[j]:
                    v[i], v[j] = v[j], v[i]
        if any(v[i] > v[i + 1] for i in range(n - 1)):
            return False
    return True


def pad_first_layer(n, layers, a):
    L1 = [tuple(c) for c in layers[0]]
    used = {c for p in L1 for c in p}
    idle = [c for c in range(n) if c not in used]
    while len(L1) < a:
        u, v = idle[0], idle[1]
        idle = idle[2:]
        L1.append((u, v))
    return [sorted(L1)] + [list(map(tuple, L)) for L in layers[1:]]


def track(layers, start, sign, upto=None):
    """Channels of a sentinel (+1: +inf, -1: -inf) after each layer, and which layers it meets."""
    pos, meets, path = start, [], []
    for t, L in enumerate(layers[:upto] if upto else layers):
        partner = None
        for i, j in L:
            if pos == i:
                partner = j
            elif pos == j:
                partner = i
        if partner is None:
            meets.append(False)
        else:
            meets.append(True)
            pos = max(pos, partner) if sign > 0 else min(pos, partner)
        path.append(pos)
    return path, meets


def good_sentinels(n, layers, a):
    full = [len(layers[t]) == a for t in range(3)]
    out = []
    for i, j in layers[0]:
        for start, sign in ((j, +1), (i, -1)):     # +inf on either input ends on max end j
            _, meets = track(layers, start, sign, upto=3)
            if all(meets[t] or not full[t] for t in range(3)) and meets[0]:
                out.append((start, sign))
    return out


def residual(n, layers, start, sign):
    """Delete the sentinel; return the untangled standard network on n-1 channels."""
    owner = list(range(n))                 # channel -> track id; sentinel is track 'S'
    owner[start] = 'S'
    gen = []                               # generalized layers: (min_track, max_track)
    for L in layers:
        G = []
        new_owner = owner[:]
        for i, j in L:
            a, b = owner[i], owner[j]
            if a == 'S' or b == 'S':
                # sentinel goes to j (max end) if +inf, to i (min end) if -inf; the real to the other
                real = b if a == 'S' else a
                if sign > 0:
                    new_owner[j], new_owner[i] = 'S', real
                else:
                    new_owner[i], new_owner[j] = 'S', real
            else:
                G.append((a, b))           # min on channel i (track a), max on channel j (track b)
        owner = new_owner
        gen.append(G)
    # final: output order of tracks = channel order without the sentinel
    order = [t for t in owner if t != 'S']
    # relabel tracks so that the k-th output track is line k; then untangle (Knuth 5.3.4 ex. 16)
    line = {t: k for k, t in enumerate(order)}
    sigma = list(range(n - 1))
    std = []
    for G in gen:
        S = []
        for (x, y) in G:
            p, q = sigma[line[x]], sigma[line[y]]
            if p < q:
                S.append((p, q))
            else:
                S.append((q, p))
                # interchange physical lines p and q in everything that follows
                for z in range(n - 1):
                    if sigma[z] == p:
                        sigma[z] = q
                    elif sigma[z] == q:
                        sigma[z] = p
        std.append(sorted(S))
    return std


def lemma_condition(n, a):
    k = n - 2 * a
    return math.ceil((2 * a - k) / 2) > k and 2 * math.ceil(a / 2) > k


def descend(n, layers, steps, log=print):
    a = n // 2
    cur = [list(map(tuple, L)) for L in layers]
    assert sorts(n, cur)
    for s in range(steps):
        assert all(len(cur[t]) <= a for t in range(3)), 'input violates caps'
        cond = lemma_condition(n, a)
        cur = pad_first_layer(n, cur, a)
        assert sorts(n, cur)
        good = good_sentinels(n, cur, a)
        log(f'step {s}: n={n} a={a} lemma condition={cond} good sentinels={len(good)} of {2 * a}')
        if cond:
            assert good, 'track lemma violated'
        if not good:
            return n, cur, False
        start, sign = good[0]
        res = residual(n, cur, start, sign)
        ok = sorts(n - 1, res)
        sizes = [len(L) for L in res]
        log(f'   sentinel {"+" if sign > 0 else "-"}inf at {start}: residual on {n - 1} channels sorts={ok} '
            f'depth={sum(1 for L in res if L)} sizes={sizes}')
        assert ok and all(sizes[t] <= a - 1 for t in range(3))
        n, a, cur = n - 1, a - 1, res
    return n, cur, True


if __name__ == '__main__':
    data = json.load(open(sys.argv[1]))
    steps = int(sys.argv[2])
    n, net, ok = descend(data['n'], data['layers'], steps)
    print(json.dumps({'final_n': n, 'ok': ok, 'layers': net}))
