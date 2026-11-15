#!/usr/bin/env python3
"""median_sat.py -- the median count of d13.md section 4 as a SAT problem.

Is there a network on 13 channels with T layers and first layer (0,1)(2,3)...(10,11) after which
h + l >= K?  Here h is the number of channels that are 1 on every input with 6 ones (tau0 >= 8:
certainly above the median) and l the number that are 0 on every input with 7 ones (tau1 >= 8:
certainly below).  Only inputs with 6 or 7 ones matter.  The encoding is exact, as in satnet.py: one
variable per possible comparator of each free layer, and value variables for every state after the
fixed layers, tied to them by full equivalences.

  median_sat.py T K               one instance, layers 2..T free.
  median_sat.py T K --cubes [W]   one instance per class of L2 up to permuting the pairs of L1, on W
                                  worker processes (default 8).  There are 896 classes: a second layer
                                  that repeats a comparator of L1 is covered by the class without it
                                  (h9.md section 2).

A SAT answer is printed and checked by brute force.  "4 6" is SAT in seconds: the bound h_4 + l_4 <= 6
of d13.md Proposition 18 is attained.  "4 7 --cubes" is UNSAT (about 14 minutes on 4 workers), which
confirms the bound for this first layer without the game of guarantee_games.py.  ("6 9" is SAT:
median_networks.py has such a network.)
Needs python-sat (.venv, see h9.md section 10).
"""
import itertools
import sys
import time
from multiprocessing import Pool

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver

n = 13
L1 = [(2 * i, 2 * i + 1) for i in range(6)]
PAIRS = list(itertools.combinations(range(n), 2))


def apply(x, L):
    x = list(x)
    for a, b in L:
        if x[a] > x[b]:
            x[a], x[b] = x[b], x[a]
    return tuple(x)


def h_and_l(net):
    """brute force: (h, l) after the layers of net."""
    def run(v):
        for L in net:
            v = apply(v, L)
        return v
    ins = [v for v in itertools.product((0, 1), repeat=n) if sum(v) in (6, 7)]
    out = [(sum(v), run(v)) for v in ins]
    h = sum(1 for c in range(n) if all(y[c] == 1 for w, y in out if w == 6))
    l = sum(1 for c in range(n) if all(y[c] == 0 for w, y in out if w == 7))
    return h, l


def encode(T, K, prefix):
    """clauses for: the fixed layers `prefix`, then T - len(prefix) free layers, then h + l >= K."""
    p, d = len(prefix), T - len(prefix)
    pool = IDPool()
    clauses = []

    def add(cl):
        out = []
        for lit in cl:
            if lit is True:
                return
            if lit is not False:
                out.append(lit)
        clauses.append(out)
    neg = lambda lit: (not lit) if isinstance(lit, bool) else -lit
    g = {(t, a, b): pool.id(('g', t, a, b)) for t in range(d) for (a, b) in PAIRS}
    used = {}
    for t in range(d):
        for k in range(n):
            inc = [g[t, min(k, m), max(k, m)] for m in range(n) if m != k]
            for x, y in itertools.combinations(inc, 2):
                add([-x, -y])                                   # at most one comparator per channel
            u = used[t, k] = pool.id(('u', t, k))
            add([-u] + inc)
            for x in inc:
                add([-x, u])
    states = {6: set(), 7: set()}
    for v in itertools.product((0, 1), repeat=n):
        if sum(v) in states:
            for L in prefix:
                v = apply(v, L)
            states[sum(v)].add(v)
    vals = {}                                   # vals[w][s]: value literals of every state after s free layers
    for w, S in states.items():
        vals[w] = [[] for _ in range(d + 1)]
        for xi, x in enumerate(sorted(S)):
            cur = [bool(b) for b in x]
            vals[w][0].append(cur)
            for t in range(d):
                nxt = [pool.id(('v', w, xi, t, k)) for k in range(n)]
                for k in range(n):
                    vk, nk = cur[k], nxt[k]
                    for m in range(n):
                        if m == k:
                            continue
                        gl, vm = g[t, min(k, m), max(k, m)], cur[m]
                        if k > m:                               # k receives the max: OR
                            add([-gl, neg(vk), nk]); add([-gl, neg(vm), nk]); add([-gl, vk, vm, -nk])
                        else:                                   # k receives the min: AND
                            add([-gl, vk, -nk]); add([-gl, vm, -nk]); add([-gl, neg(vk), neg(vm), nk])
                    u = used[t, k]
                    add([u, neg(vk), nk]); add([u, vk, -nk])    # idle channel keeps its value
                cur = nxt
                vals[w][t + 1].append(cur)

    def decided(s):
        """variables H_c, L_c after s free layers: H_c -> c is 1 on every input with 6 ones, L_c -> c is
        0 on every input with 7 ones."""
        H = [pool.id(('H', s, c)) for c in range(n)]
        Lo = [pool.id(('L', s, c)) for c in range(n)]
        for c in range(n):
            six = [st[c] for st in vals[6][s]]
            seven = [st[c] for st in vals[7][s]]
            for lit in six:
                add([-H[c], lit])
            for lit in seven:
                add([-Lo[c], neg(lit)])
        return H, Lo
    H, Lo = decided(d)
    clauses.extend(CardEnc.atleast(lits=H + Lo, bound=K, vpool=pool, encoding=EncType.seqcounter).clauses)
    return clauses, g, d, sum(len(S) for S in states.values())


def solve(args):
    T, K, prefix = args
    clauses, g, d, nstates = encode(T, K, prefix)
    t0 = time.time()
    with Solver(name='cadical195', bootstrap_with=clauses) as s:
        if not s.solve():
            return prefix, None, time.time() - t0, nstates
        m = set(lit for lit in s.get_model() if lit > 0)
    net = list(prefix) + [[(a, b) for (a, b) in PAIRS if g[t, a, b] in m] for t in range(d)]
    return prefix, net, time.time() - t0, nstates


def canonical_L2():
    """one second layer per class up to permuting the pairs of L1 (none repeating a comparator of L1)."""
    def matchings(chans):
        if not chans:
            yield []
            return
        a, rest = chans[0], chans[1:]
        yield from matchings(rest)
        for b in rest:
            for M in matchings([c for c in rest if c != b]):
                yield [(a, b)] + M
    perms = list(itertools.permutations(range(6)))

    def key(M, q):
        mp = {12: 12}
        for i in range(6):
            mp[2 * i], mp[2 * i + 1] = 2 * q[i], 2 * q[i] + 1
        part = list(range(n))
        for a, b in M:
            part[mp[a]], part[mp[b]] = mp[b], mp[a]
        return tuple(part)
    out = []
    for M in matchings(list(range(n))):
        if set(M) & set(L1):
            continue
        k0 = key(M, perms[0])
        if all(key(M, q) >= k0 for q in perms[1:]):
            out.append(M)
    return out


def report(net, T, K):
    h, l = h_and_l(net)
    print('  network:', ' | '.join(''.join(f'({a},{b})' for a, b in L) for L in net))
    print(f'  brute force: h = {h}, l = {l}, h + l = {h + l}' + ('' if h + l >= K else '   ENCODING ERROR'))
    return h + l >= K


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    T, K = int(sys.argv[1]), int(sys.argv[2])
    cubes = '--cubes' in sys.argv
    if not cubes:
        _, net, dt, nstates = solve((T, K, [L1]))
        print(f'T = {T}, K = {K}: {nstates} states after layer 1')
        if net is None:
            print(f'UNSAT in {dt:.0f} s: no {T}-layer network has h + l >= {K}')
            sys.exit(0)
        print(f'SAT in {dt:.0f} s')
        sys.exit(0 if report(net, T, K) else 1)
    W = int(sys.argv[sys.argv.index('--cubes') + 1]) if len(sys.argv) > sys.argv.index('--cubes') + 1 else 8
    classes = canonical_L2()
    print(f'T = {T}, K = {K}: {len(classes)} classes of L2, {W} workers', flush=True)
    start, done, slowest = time.time(), 0, 0.0
    with Pool(W) as pool:
        for prefix, net, dt, _ in pool.imap_unordered(solve, [(T, K, [L1, L2]) for L2 in classes]):
            done += 1
            slowest = max(slowest, dt)
            if net is not None:
                print(f'SAT for L2 = {prefix[1]} after {time.time() - start:.0f} s')
                ok = report(net, T, K)
                pool.terminate()
                sys.exit(0 if ok else 1)
            if done % 50 == 0:
                print(f'  {done}/{len(classes)} classes UNSAT, {time.time() - start:.0f} s, slowest {slowest:.0f} s', flush=True)
    print(f'UNSAT for every class ({time.time() - start:.0f} s): no {T}-layer network has h + l >= {K}')
