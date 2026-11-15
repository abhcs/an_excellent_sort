#!/usr/bin/env python3
"""median_networks.py -- the lemmas and networks of d13.md sections 2 and 4, checked by brute force.

After t layers, P_t(k) is the set of channels that can hold the element of rank k (0 = smallest).  It is
read off the probes (x, x + e_p) with |x| = n - 1 - k: the images differ on one channel, the token,
which holds that element.  tau0(c) is the least number of zeros forcing channel c to 0, tau1(c) the
least number of ones forcing it to 1.  A pair u, v in P_t(k) is one-sided DOWN if, whenever one of them
holds rank k, the other holds a larger element, and UP if it holds a smaller one.

1. Lemma 15 (rank intervals): the ranks channel c can hold are exactly tau0(c) - 1, ..., n - tau1(c);
   and tau0(c) + tau1(c) <= n + 1.  Checked after every layer of random networks on 9 channels.
2. Lemma 17 (one layer): |P_{t+1}(k)| = |P_t(k)| minus the number of comparators of layer t+1 that join
   a one-sided pair of P_t(k).  Checked for every rank and every layer of the same networks.
3. 13 channels, median (rank 6).  h = #channels with tau0 >= 8 (certainly above the median), l = #with
   tau1 >= 8 (certainly below), and |P_t(6)| = 13 - h - l.
   * h_3 = l_3 = 1 and h_4 = l_4 = 3 are attained, so the bounds of guarantee_games.py are tight;
   * a network with h_6 = 5 and l_6 = 4: only 4 channels can hold the median after six layers, as a
     depth-8 sorter needs.  So the median alone cannot prove D(13) >= 9 (Conjecture (M13) is false).
     Its five-layer prefix has h = 3, l = 2 and four disjoint one-sided pairs (Psi_5 = 9), which are
     its sixth layer.  The same network fails the probe condition at other ranks: ranks 7 and 8 lie
     in 9 channels' intervals.
4. Five layers are not enough to use Lemma 15(c) at 13 channels and depth 8: a five-layer prefix keeps
   every rank within 2^(8-t) channels after every layer t <= 5 (found by a search for this).

Needs only python3.  Exit status 0 iff every check passes.  About 5 seconds.
usage: python3 median_networks.py
"""
import random
import sys

L1_13 = [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11)]
TOURNAMENT = [L1_13, [(0, 2), (1, 3), (4, 6), (5, 7)], [(0, 4), (3, 7)]]
FOUR_LAYERS = [L1_13,                                   # found by median_sat.py 4 6
               [(0, 2), (1, 6), (3, 4), (5, 8), (7, 10), (9, 11)],
               [(0, 3), (1, 9), (2, 10), (4, 6), (5, 7), (11, 12)],
               [(0, 9), (1, 3), (2, 5), (4, 12), (6, 7), (8, 10)]]
FIVE_LAYERS = [L1_13,                                   # state compression, then the best sixth layer
               [(0, 8), (1, 9), (2, 6), (3, 7), (4, 10), (5, 11)],
               [(0, 2), (1, 5), (3, 8), (4, 6), (7, 9), (10, 12)],
               [(0, 9), (1, 8), (2, 12), (3, 4), (5, 6), (7, 11)],
               [(0, 6), (1, 2), (4, 10), (5, 7), (8, 12)]]
SIXTH = [(1, 5), (2, 4), (6, 10), (7, 8)]
FIVE_PASSES = [L1_13,                                   # passes the depth-8 per-rank condition
               [(0, 10), (1, 2), (4, 6), (5, 8), (7, 12), (9, 11)],
               [(1, 9), (2, 3), (4, 10), (5, 7), (6, 11), (8, 12)],
               [(0, 7), (1, 4), (2, 10), (3, 12), (5, 6), (8, 9)],
               [(0, 5), (1, 7), (2, 6), (3, 11), (4, 8), (9, 10)]]


def apply(x, L):
    for a, b in L:
        if (x >> a & 1) and not (x >> b & 1):
            x ^= (1 << a) | (1 << b)
    return x


class Prefix:
    """everything about the network `net` on n channels that the checks need, by brute force."""

    def __init__(self, net, n):
        self.n = n
        img = list(range(1 << n))
        for L in net:
            img = [apply(y, L) for y in img]
        self.img = img
        self.tau0 = [n + 1] * n
        self.tau1 = [n + 1] * n
        for x in range(1 << n):
            w = bin(x).count('1')
            for c in range(n):
                if img[x] >> c & 1:
                    self.tau1[c] = min(self.tau1[c], w)
                else:
                    self.tau0[c] = min(self.tau0[c], n - w)
        full = (1 << n) - 1
        self.P = [0] * n                                  # P[k]: bitmask of channels that can hold rank k
        self.smaller = [[0] * n for _ in range(n)]        # smaller[k][j]: channels seen below rank k at j
        self.larger = [[0] * n for _ in range(n)]
        for x in range(1 << n):
            k = n - 1 - bin(x).count('1')
            s = img[x]
            for p in range(n):
                if not x >> p & 1:
                    tok = s ^ img[x | 1 << p]
                    j = tok.bit_length() - 1
                    self.P[k] |= tok
                    self.smaller[k][j] |= full & ~s & ~tok
                    self.larger[k][j] |= s

    def one_sided(self, k):
        """(DOWN, UP): sets of pairs u < v of P[k]."""
        V = [c for c in range(self.n) if self.P[k] >> c & 1]
        down, up = set(), set()
        for i, u in enumerate(V):
            for v in V[i + 1:]:
                if not (self.smaller[k][u] >> v & 1) and not (self.smaller[k][v] >> u & 1):
                    down.add((u, v))
                if not (self.larger[k][u] >> v & 1) and not (self.larger[k][v] >> u & 1):
                    up.add((u, v))
        return down, up

    def size(self, k):
        return bin(self.P[k]).count('1')


def max_matching(edges, verts):
    best = []

    def rec(vs, acc):
        nonlocal best
        if len(acc) > len(best):
            best = list(acc)
        if len(vs) < 2 or len(acc) + len(vs) // 2 <= len(best):
            return
        a, rest = vs[0], vs[1:]
        rec(rest, acc)
        for b in rest:
            if (a, b) in edges:
                rec([c for c in rest if c != b], acc + [(a, b)])
    rec(sorted(verts), [])
    return best


def random_matching(n, rng):
    ch = list(range(n))
    rng.shuffle(ch)
    m = rng.randint(0, n // 2)
    return [tuple(sorted(ch[2 * i:2 * i + 2])) for i in range(m)]


ok = True


def expect(cond, text):
    global ok
    ok &= bool(cond)
    print(('  ' if cond else '  FAILED: ') + text)


print('Lemmas 15 and 17 on 40 random networks of 6 layers on 9 channels (L1 maximal), every layer, every rank')
rng = random.Random(2026)
n = 9
bad15 = bad18 = 0
transitions = lost_total = 0
for trial in range(40):
    net = [[(0, 1), (2, 3), (4, 5), (6, 7)]]
    pre = Prefix(net, n)
    for t in range(2, 7):
        for c in range(n):
            ranks = [k for k in range(n) if pre.P[k] >> c & 1]
            if ranks != list(range(pre.tau0[c] - 1, n - pre.tau1[c] + 1)) or pre.tau0[c] + pre.tau1[c] > n + 1:
                bad15 += 1
        L = random_matching(n, rng)
        nxt = Prefix(net + [L], n)
        for k in range(n):
            down, up = pre.one_sided(k)
            lost = sum(1 for e in L if e in down or e in up)
            lost_total += lost
            if nxt.size(k) != pre.size(k) - lost:
                bad18 += 1
        transitions += 1
        net, pre = net + [L], nxt
expect(bad15 == 0, f'Lemma 15: rank sets are the intervals [tau0 - 1, n - tau1], tau0 + tau1 <= n + 1 ({bad15} exceptions)')
expect(bad18 == 0, f'Lemma 17: |P_t+1(k)| = |P_t(k)| - #one-sided comparators, {transitions} layers x {n} ranks, {lost_total} one-sided comparators ({bad18} exceptions)')

print('13 channels, the median (rank 6): h = #(tau0 >= 8), l = #(tau1 >= 8)')


def hl(pre):
    return sum(1 for v in pre.tau0 if v >= 8), sum(1 for v in pre.tau1 if v >= 8)


for name, net, want in [('3 layers (two tournaments)', TOURNAMENT, (1, 1)),
                        ('4 layers (median_sat.py 4 6)', FOUR_LAYERS, (3, 3))]:
    pre = Prefix(net, 13)
    h, l = hl(pre)
    expect((h, l) == want and pre.size(6) == 13 - h - l,
           f'{name}: h = {h}, l = {l}, {pre.size(6)} channels can hold the median')
pre5 = Prefix(FIVE_LAYERS, 13)
h5, l5 = hl(pre5)
down, up = pre5.one_sided(6)
M = max_matching(down | up, [c for c in range(13) if pre5.P[6] >> c & 1])
expect((h5, l5, len(M)) == (3, 2, 4) and set(SIXTH) <= down | up and len(SIXTH) == len(M),
       f'5 layers: h = {h5}, l = {l5}, {len(down)} DOWN and {len(up)} UP pairs, largest matching {len(M)}: '
       f'Psi_5 = {h5 + l5 + len(M)}; the sixth layer {SIXTH} is such a matching')
pre6 = Prefix(FIVE_LAYERS + [SIXTH], 13)
h6, l6 = hl(pre6)
expect((h6, l6) == (5, 4) and pre6.size(6) == 4,
       f'6 layers: h = {h6}, l = {l6}, so only {pre6.size(6)} channels can hold the median (depth 8 allows 4)')
per_rank = [pre6.size(k) for k in range(13)]
longest = max(13 - pre6.tau1[c] - pre6.tau0[c] + 2 for c in range(13))
expect(max(per_rank) == 9 and longest == 7,
       f'  but channels per rank k = 0..12 are {per_rank} (depth 8 allows 4), longest interval {longest}')
worst = [max(Prefix(FIVE_PASSES[:t], 13).size(k) for k in range(13)) for t in range(1, 6)]
caps = [1 << (8 - t) for t in range(1, 6)]
expect(all(w <= c for w, c in zip(worst, caps)),
       f'a 5-layer prefix: most channels at one rank after layers 1-5 = {worst} (depth 8 allows {caps})')
print('all checks passed' if ok else 'SOME CHECK FAILED')
sys.exit(0 if ok else 1)
