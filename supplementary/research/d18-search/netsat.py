#!/usr/bin/env python3
"""netsat.py -- iterative SAT search for a sorting network that extends a fixed prefix.

Conventions: channels 0..n-1; a comparator (i, j) with i < j puts the minimum on i; a layer is a
matching.  Binary vectors are ints, bit k = value on channel k.

Problem: given a prefix P (a list of layers) and r free layers, find layers F_0..F_{r-1} such that
P + F sorts all 2^n binary inputs, i.e. F sorts the set U of unsorted images of {0,1}^n under P.

Restrictions used.  Each holds in some sorting network with prefix P whenever any network with
prefix P exists, so none of them loses solutions:
  * standard comparators only (untangling, Knuth TAOCP 5.3.4 ex. 16);
  * no redundant comparator in the free layers (deleting a comparator that never swaps changes
    nothing), hence by Codish, Cruz-Filipe, Schneider-Kamp, "Sorting networks: the end game"
    (arXiv 1411.6408), Lemma 3 and Corollary 2:
      - last layer: only (i, i+1)                                                     [phi1]
      - penultimate layer: only (i, j) with j - i <= 3                                 [phi2]
      - (i, i+3) in the penultimate layer -> (i,i+1) and (i+2,i+3) in the last layer   [phi3]
      - (i, i+2) in the penultimate layer -> (i,i+1) or (i+1,i+2) in the last layer    [phi4]
    and a comparator of the first free layer must swap on some output of P.          [nored0]
  * --cosat: the co-saturation normal form (same paper, Theorem 4.2, constraints psi1..psi3b),
    which they combine with phi in their experiments.  The added comparators join adjacent
    blocks, so they keep phi2..phi4; nored0 only touches the first free layer, so it needs r >= 3.
  * --lex (self-dual prefix): the network and its dual are both solutions, so require the first
    free layer to be lexicographically <= its mirror image.

Consequences used as unit clauses (with phi): before the last layer an input with z zeros is
0^(z-1) ab 1^(n-z-1), ab in {01,10}, and ab = 10 forces (z-1,z) into the last layer, so the last
layer is absorbed; and before the penultimate layer channels <= z-4 hold 0 and channels >= z+3
hold 1 (a stray 1 at z-4 can only leave by (z-4,z-1), and phi3 then blocks (z-1,z)).

Encoding (exact, both directions, in the style of Ehlers & Mueller 2015): for an input x with
window [a, e] (x = 0^a x' 1^(n-1-e)) channels outside the window are constant in every standard
network, so only channels a..e get value variables, and a comparator leaving the window acts as
the identity.  For free layer t and channel k in the window:
    new_k >= old_k  unless k is the min end of a comparator inside the window   (Down)
    new_k <= old_k  unless k is the max end of a comparator inside the window   (Up)
    g(t,i,j) -> new_j >= old_i,  new_j <= old_i | old_j,  new_i >= old_i & old_j,  new_i <= old_j

CEGAR: start from a sample of U, solve, run the candidate on all of U, add failing inputs
(smallest window first), repeat until a network sorts U (found) or the solver says UNSAT.  UNSAT
on a subset of U implies UNSAT on U.  Every network found is re-checked on all 2^n inputs.

--sym (n even): only self-dual networks (layer t has (i,j) iff it has (n-1-j, n-1-i)).  A
restriction (it can lose solutions); needs a self-dual prefix.  Then only one input of each pair
{x, rc(x)} is needed, rc = reverse-complement.
"""
import argparse
import itertools
import json
import os
import random
import sys
import time

from pysat.solvers import Solver


# ------------------------------------------------------------------ networks on ints

def apply_layers(layers, x):
    for L in layers:
        for (i, j) in L:
            if (x >> i) & 1 and not (x >> j) & 1:
                x ^= (1 << i) | (1 << j)
    return x


def sorted_mask(n, w):
    """The sorted vector with w ones (ones on channels n-w..n-1)."""
    return ((1 << n) - 1) ^ ((1 << (n - w)) - 1)


def is_sorted(x, n):
    return x == sorted_mask(n, bin(x).count('1'))


def rc(x, n):
    """Reverse-complement: bit k of the result is 1 - bit (n-1-k) of x."""
    y = 0
    for k in range(n):
        if not (x >> (n - 1 - k)) & 1:
            y |= 1 << k
    return y


def prefix_images(n, prefix):
    S = range(1 << n)
    for L in prefix:
        S = {apply_layers([L], x) for x in S}
    return set(S)


def verify_all(n, layers):
    """0-1 principle, bit-parallel: wire k is a 2^n-bit int whose bit x is the value on wire k
    for input x.  The network sorts iff wire k is contained in wire k+1 for every k."""
    N = 1 << n
    full = (1 << N) - 1
    wires = []
    for k in range(n):
        h = 1 << k
        block = ((1 << h) - 1) << h               # 2h bits: low h zeros, high h ones
        wires.append(block * (full // ((1 << (2 * h)) - 1)))
    for L in layers:
        used = set()
        for (i, j) in L:
            assert i < j and i not in used and j not in used, ('not a standard layer', L)
            used |= {i, j}
            a, b = wires[i], wires[j]
            wires[i], wires[j] = a & b, a | b
    return all(wires[k] & ~wires[k + 1] == 0 for k in range(n - 1))


def window(x, n):
    a = 0
    while a < n and not (x >> a) & 1:
        a += 1
    e = n - 1
    while e >= 0 and (x >> e) & 1:
        e -= 1
    return a, e


def remove_redundant(n, layers):
    """Drop comparators that never swap (checked on all 2^n inputs, bit-parallel)."""
    N = 1 << n
    full = (1 << N) - 1
    wires = []
    for k in range(n):
        h = 1 << k
        wires.append((((1 << h) - 1) << h) * (full // ((1 << (2 * h)) - 1)))
    out = []
    for L in layers:
        keep = []
        for (i, j) in L:
            a, b = wires[i], wires[j]
            if a & ~b:
                keep.append((i, j))
            wires[i], wires[j] = a & b, a | b
        out.append(keep)
    return [L for L in out if L]


# ------------------------------------------------------------------ prefixes

def cube_layers(chans, dims):
    """Green-filter layers on the 2^dims channels chans (chans[i] has binary index i)."""
    assert len(chans) == 1 << dims
    return [[(chans[i], chans[i | (1 << b)]) for i in range(len(chans)) if not (i >> b) & 1]
            for b in range(dims)]


def merge_layers(*nets):
    depth = max(len(x) for x in nets)
    return [sorted(c for x in nets if t < len(x) for c in x[t]) for t in range(depth)]


def named_prefix(name):
    """Returns (n, layers)."""
    R = lambda a, b: list(range(a, b))
    table = {
        'g16_3': (16, merge_layers(cube_layers(R(0, 8), 3), cube_layers(R(8, 16), 3))),
        'g16_4': (16, cube_layers(R(0, 16), 4)),
        # Ehlers-Mueller: Green filter on 1..16, channel 0 idle
        'em17': (17, merge_layers(cube_layers(R(1, 9), 3), cube_layers(R(9, 17), 3))),
        'em17_4': (17, cube_layers(R(1, 17), 4)),
        # 18 channels: Green filter on 1..16 plus the pair (0,17)
        'e18_3': (18, merge_layers([[(0, 17)]], cube_layers(R(1, 9), 3), cube_layers(R(9, 17), 3))),
        'e18_4': (18, merge_layers([[(0, 17)]], cube_layers(R(1, 17), 4))),
        # 18 channels: Green filter on 0..7 and 10..17, pair (8,9) in the middle
        'm18_3': (18, merge_layers([[(8, 9)]], cube_layers(R(0, 8), 3), cube_layers(R(10, 18), 3))),
    }
    for m in range(2, 11):   # Parberry first layer only
        table[f'pb{2 * m}'] = (2 * m, [[(2 * i, 2 * i + 1) for i in range(m)]])
    return table[name]


def load_prefix(spec):
    if os.path.exists(spec):
        with open(spec) as f:
            d = json.load(f)
        return d['n'], [[tuple(c) for c in L] for L in d['layers']]
    return named_prefix(spec)


def mirror(n, p):
    return (n - 1 - p[1], n - 1 - p[0])


def is_self_dual(n, layers):
    return all(sorted(mirror(n, p) for p in L) == sorted(L) for L in layers)


# ------------------------------------------------------------------ the SAT model

def neg(l):
    return (not l) if isinstance(l, bool) else -l


class Model:
    def __init__(self, n, r, U, sym=False, phi=True, cosat=False, nored0=True, lex=False,
                 solver='cadical195'):
        assert r >= 1
        self.n, self.r, self.sym, self.phi = n, r, sym, phi
        self.nv = 0
        self.ncl = 0
        self.S = Solver(name=solver)
        nonred0 = None
        if nored0 and r >= 3:
            nonred0 = {(i, j) for i in range(n) for j in range(i + 1, n)
                       if any((x >> i) & 1 and not (x >> j) & 1 for x in U)}
        self.g = []
        for t in range(r):
            gt = {}
            for i in range(n):
                for j in range(i + 1, n):
                    if t == r - 1 and j != i + 1:                    # phi1
                        continue
                    if t == r - 2 and phi and j - i > 3:             # phi2
                        continue
                    if t == 0 and nonred0 is not None and (i, j) not in nonred0:
                        continue
                    if sym and mirror(n, (i, j)) in gt:
                        gt[(i, j)] = gt[mirror(n, (i, j))]
                        continue
                    gt[(i, j)] = self.new_var()
            if sym:
                gt = {p: v for p, v in gt.items() if mirror(n, p) in gt}
            self.g.append(gt)
        for t in range(r):                                           # each layer is a matching
            gt = self.g[t]
            for k in range(n):
                inc = sorted({v for (i, j), v in gt.items() if i == k or j == k})
                for x, y in itertools.combinations(inc, 2):
                    self.add([-x, -y])
        self.down, self.up = {}, {}
        self.ninputs = 0
        if nonred0 is not None and r >= 4:
            self._redundancy_tracking(nonred0)
        if r >= 2 and phi:
            self._phi34()
        if r >= 2 and cosat:
            self._cosat()
        if lex and not sym:
            self._lex_dual(0)

    def fix(self, items):
        """Case constraints: {'g': [t,i,j], 'value': bool} or {'idle': [t,k]}."""
        for it in items:
            if 'g' in it:
                t, i, j = it['g']
                v = self.g[t].get((i, j))
                if v is None:
                    if it['value']:
                        self.add([])                  # forced comparator cannot exist: UNSAT
                else:
                    self.add([v] if it['value'] else [-v])
            else:
                t, k = it['idle']
                for (i, j), v in self.g[t].items():
                    if k in (i, j):
                        self.add([-v])

    # -- basics
    def new_var(self):
        self.nv += 1
        return self.nv

    def add(self, cl):
        out = []
        for l in cl:
            if l is True:
                return
            if l is False:
                continue
            out.append(l)
        if not out:
            v = self.new_var()
            self.S.add_clause([v])
            self.S.add_clause([-v])
            self.ncl += 2
            return
        self.S.add_clause(out)
        self.ncl += 1

    def L(self, i):
        """Comparator (i, i+1) in the last layer (False if it cannot exist)."""
        return self.g[self.r - 1].get((i, i + 1), False)

    def used(self, t, k):
        """Channel k used in free layer t (an aux variable, defined both ways)."""
        key = ('u', t, k)
        if key in self.down:
            return self.down[key]
        inc = sorted({v for (i, j), v in self.g[t].items() if i == k or j == k})
        if not inc:
            res = False
        else:
            res = self.new_var()
            self.add([-res] + inc)
            for v in inc:
                self.add([-v, res])
        self.down[key] = res
        return res

    # -- non-redundancy in the early free layers
    def _redundancy_tracking(self, nonred0):
        """R[t](i,j) is forced true when x_i <= x_j holds for every input after free layer t:
        the prefix already orders them (and t = -1), or layer t has (i,j), or the order held after
        layer t-1 and layer t neither raises i (max end) nor lowers j (min end).  A comparator
        (i,j) in layer t+1 with R[t](i,j) never swaps, so it is forbidden.  Only layers before the
        last two (which co-saturation may fill with redundant comparators) are restricted."""
        n, r = self.n, self.r
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        Rprev = {p: (p not in nonred0) for p in pairs}
        for t in range(0, r - 3):
            Rt = {}
            for (i, j) in pairs:
                gt = self.g[t].get((i, j))
                if Rprev[(i, j)] is False and gt is None:
                    Rt[(i, j)] = False
                    continue
                v = self.new_var()
                if gt is not None:
                    self.add([-gt, v])
                self.add([neg(Rprev[(i, j)]), self.Up(t, 0, i), self.Down(t, j, n - 1), v])
                Rt[(i, j)] = v
                gn = self.g[t + 1].get((i, j))
                if gn is not None:
                    self.add([-gn, -v])
            Rprev = Rt

    # -- end-game constraints
    def _phi34(self):
        pen = self.g[self.r - 2]
        for (i, j), v in pen.items():
            if j - i == 3:
                self.add([-v, self.L(i)])
                self.add([-v, self.L(i + 2)])
            elif j - i == 2:
                self.add([-v, self.L(i), self.L(i + 1)])

    def _cosat(self):
        n, L, P = self.n, self.L, (lambda k: self.used(self.r - 2, k))
        Lx = lambda i: L(i) if 0 <= i <= n - 2 else False
        for i in range(n - 1):                                       # psi1
            self.add([Lx(i - 1), Lx(i), Lx(i + 1)])
        for i in range(n - 3):                                       # psi2a
            X = [neg(Lx(i)), neg(Lx(i + 2))]
            for a in (i, i + 1):
                for b in (i + 2, i + 3):
                    self.add(X + [P(a), P(b)])
        for i in range(n - 2):
            base = [neg(Lx(i)), Lx(i + 1), Lx(i + 2)]                # psi2b: L_i, i+2 unused in d
            self.add(base + [P(i), P(i + 2)])
            self.add(base + [P(i + 1), P(i + 2)])
            base = [Lx(i - 1), Lx(i), neg(Lx(i + 1))]                # psi2c: i unused in d, L_{i+1}
            self.add(base + [P(i), P(i + 1)])
            self.add(base + [P(i), P(i + 2)])
            self.add([neg(Lx(i)), Lx(i + 1), Lx(i + 2), P(i), P(i + 1)])   # psi3a
        for i in range(1, n - 1):                                    # psi3b
            self.add([neg(Lx(i)), Lx(i - 2), Lx(i - 1), P(i), P(i + 1)])

    def _lex_dual(self, t):
        """first free layer <=_lex its mirror image (valid when the problem is self-dual)."""
        n, gt = self.n, self.g[t]
        pairs = sorted(p for p in gt if mirror(n, p) in gt and mirror(n, p) != p)
        if not pairs:
            return
        eq = True                                                    # "equal so far"
        for p in pairs:
            V, D = gt[p], gt[mirror(n, p)]
            self.add([neg(eq), -V, D])                               # V <= D while equal
            nxt = self.new_var()
            self.add([neg(eq), V, D, nxt])                           # both 0: stay equal
            self.add([neg(eq), -V, -D, nxt])                         # both 1: stay equal
            eq = nxt

    # -- comparators "inside the window"
    def Down(self, t, k, e):
        """OR of g(t,k,l) for k < l <= e."""
        key = ('d', t, k, e)
        if key in self.down:
            return self.down[key]
        if e <= k:
            res = False
        else:
            prev = self.Down(t, k, e - 1)
            gl = self.g[t].get((k, e))
            if gl is None:
                res = prev
            elif prev is False:
                res = gl
            else:
                res = self.new_var()
                self.add([-res, prev, gl]); self.add([-prev, res]); self.add([-gl, res])
        self.down[key] = res
        return res

    def Up(self, t, a, k):
        """OR of g(t,l,k) for a <= l < k."""
        key = (t, a, k)
        if key in self.up:
            return self.up[key]
        if a >= k:
            res = False
        else:
            prev = self.Up(t, a + 1, k)
            gl = self.g[t].get((a, k))
            if gl is None:
                res = prev
            elif prev is False:
                res = gl
            else:
                res = self.new_var()
                self.add([-res, prev, gl]); self.add([-prev, res]); self.add([-gl, res])
        self.up[key] = res
        return res

    def add_input(self, x):
        n, r = self.n, self.r
        a, e = window(x, n)
        z = n - bin(x).count('1')
        assert a < e
        cur = {k: bool((x >> k) & 1) for k in range(a, e + 1)}
        if r == 2 and self.phi:
            self._pen_units(cur, a, e, z)
        for t in range(r - 1):
            new = {k: self.new_var() for k in range(a, e + 1)}
            for k in range(a, e + 1):
                self.add([neg(cur[k]), new[k], self.Down(t, k, e)])
                self.add([cur[k], -new[k], self.Up(t, a, k)])
            gt = self.g[t]
            for i in range(a, e + 1):
                for j in range(i + 1, e + 1):
                    gl = gt.get((i, j))
                    if gl is None:
                        continue
                    oi, oj, ni, nj = cur[i], cur[j], new[i], new[j]
                    self.add([-gl, neg(oi), nj])
                    self.add([-gl, oi, oj, -nj])
                    self.add([-gl, neg(oi), neg(oj), ni])
                    self.add([-gl, oj, -ni])
            cur = new
            if t == r - 3 and self.phi:
                self._pen_units(cur, a, e, z)
        for k in range(a, e + 1):                                    # before the last layer
            if k <= z - 2:
                self.add([neg(cur[k])])
            elif k >= z + 1:
                self.add([cur[k]])
        p, q = cur[z - 1], cur[z]
        self.add([p, q])
        self.add([neg(p), neg(q)])
        self.add([neg(p), self.L(z - 1)])
        self.ninputs += 1

    def _pen_units(self, cur, a, e, z):
        for k in range(a, e + 1):                                    # before the penultimate layer
            if k <= z - 4:
                self.add([neg(cur[k])])
            elif k >= z + 3:
                self.add([cur[k]])

    def network(self, model):
        pos = {l for l in model if l > 0}
        return [sorted({p for p, v in self.g[t].items() if v in pos}) for t in range(self.r)]


# ------------------------------------------------------------------ CEGAR driver

def search(n, prefix, r, sym=False, init=300, batch=30, seed=0, solver='cadical195', phi=True,
           cosat=False, nored0=True, lex=False, full=False, log=print, max_iters=10 ** 9, fix=None):
    """Returns the network (list of layers), None if UNSAT, or 'LIMIT' / 'BUG'."""
    t_start = time.time()
    U = sorted(x for x in prefix_images(n, prefix) if not is_sorted(x, n))
    if sym or lex:
        assert n % 2 == 0 and is_self_dual(n, prefix), '--sym/--lex need even n and a self-dual prefix'
    pool = sorted({min(x, rc(x, n)) for x in U}) if sym else U
    wsize = {x: (lambda ae: ae[1] - ae[0] + 1)(window(x, n)) for x in pool}
    log(f'n={n} prefix depth={len(prefix)} free layers={r} sym={sym} phi={phi} cosat={cosat} '
        f'nored0={nored0} lex={lex} solver={solver} |U|={len(U)} pool={len(pool)} '
        f'avg window={sum(wsize.values()) / len(pool):.2f}')
    rng = random.Random(seed)
    M = Model(n, r, U, sym=sym, phi=phi, cosat=cosat, nored0=nored0, lex=lex, solver=solver)
    if fix:
        M.fix(fix)
        log(f'case constraints: {fix}')
    added = set()
    first = pool if (full or init >= len(pool)) else rng.sample(pool, init)
    for x in first:
        M.add_input(x)
        added.add(x)
    log(f'model built: vars={M.nv} clauses={M.ncl} inputs={len(added)} ({time.time() - t_start:.1f}s)')
    it = 0
    while it < max_iters:
        it += 1
        t0 = time.time()
        ok = M.S.solve()      # time limits are enforced by killing the process (see conquer.py)
        dt = time.time() - t0
        if not ok:
            log(f'iter {it}: UNSAT after {dt:.1f}s with {len(added)} inputs; total {time.time() - t_start:.1f}s')
            return None
        net = M.network(M.S.get_model())
        fails = [x for x in pool if x not in added and not is_sorted(apply_layers(net, x), n)]
        log(f'iter {it}: SAT in {dt:.1f}s, inputs={len(added)}, vars={M.nv}, clauses={M.ncl}, '
            f'fails={len(fails)}, elapsed={time.time() - t_start:.0f}s')
        if not fails:
            fullnet = [list(L) for L in prefix] + net
            if verify_all(n, fullnet):
                log(f'FOUND a sorting network: n={n}, depth={len(fullnet)}, size={sum(map(len, fullnet))}, '
                    f'total {time.time() - t_start:.1f}s')
                return fullnet
            log('candidate sorts the pool but fails verification -- encoding bug?')
            return 'BUG'
        fails.sort(key=lambda x: (wsize[x], rng.random()))
        for x in fails[:batch]:
            M.add_input(x)
            added.add(x)
    return 'LIMIT'


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--prefix', required=True,
                    help='a named prefix or a JSON file {"n":..,"layers":[[[i,j],..],..]}')
    ap.add_argument('--depth', type=int, required=True, help='total depth (prefix + free layers)')
    ap.add_argument('--sym', action='store_true', help='self-dual networks only (a restriction)')
    ap.add_argument('--no-phi', action='store_true', help='drop the penultimate-layer constraints')
    ap.add_argument('--cosat', action='store_true', help='add the co-saturation constraints psi')
    ap.add_argument('--no-nored0', action='store_true')
    ap.add_argument('--lex', action='store_true', help='duality symmetry breaking (self-dual prefix)')
    ap.add_argument('--full', action='store_true', help='encode every input up front')
    ap.add_argument('--init', type=int, default=300)
    ap.add_argument('--batch', type=int, default=30)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--solver', default='cadical195')
    ap.add_argument('--out', default=None, help='write a found network here (JSON)')
    args = ap.parse_args()
    if os.path.exists(args.prefix + '.claimed'):     # another conquer.py pool took this case
        print('SKIPPED: claimed by another worker pool', flush=True)
        sys.exit(3)
    n, prefix = load_prefix(args.prefix)
    fix = None
    if os.path.exists(args.prefix):
        with open(args.prefix) as f:
            fix = json.load(f).get('fix')
    r = args.depth - len(prefix)

    def log(s):
        print(time.strftime('%H:%M:%S'), s, flush=True)

    res = search(n, prefix, r, sym=args.sym, init=args.init, batch=args.batch, seed=args.seed,
                 solver=args.solver, phi=not args.no_phi, cosat=args.cosat,
                 nored0=not args.no_nored0, lex=args.lex, full=args.full, log=log, fix=fix)
    if isinstance(res, list):
        print('NETWORK', json.dumps(res), flush=True)
        if args.out:
            with open(args.out, 'w') as f:
                json.dump({'n': n, 'depth': len(res), 'size': sum(map(len, res)), 'layers': res,
                           'pruned': remove_redundant(n, res)}, f)
        sys.exit(0)
    sys.exit(1 if res is None else 2)


if __name__ == '__main__':
    main()
