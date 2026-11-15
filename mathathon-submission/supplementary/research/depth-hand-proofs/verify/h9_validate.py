"""h9_validate.py -- checks of the SAT encoding (satnet.py) and of the normal forms used for (H9).

1. Exact model counts.  Models projected onto the comparator variables must be exactly the sorting
   networks of the given shape, so their number must equal the brute-force count of small_facts.c
   (which enumerates ALL networks with the given per-layer caps).
2. The fixed-prefix and allowed-pairs mechanisms, against a brute force written here.
3. Known values at the sizes of the real instance: D(7) = 6 and D(9) = 7 with the first layer fixed.
4. The last-layer lemma (h9.md, Lemma 6): in a sorting network, a last-layer comparator (i, j)
   with j >= i + 2 never fires.  Checked on every sorting network on 4 and 5 channels of depth 3..5
   and on depth-7 networks on 9 channels found by SAT with an unrestricted last layer.
5. Side facts: the seven-channel analogue of (H9), and the thin-layer profiles on five channels.

usage: .venv/bin/python h9_validate.py     (needs ./small_facts; about a minute)
"""
import itertools
import os
import random
import re
import subprocess

from netlib import matchings
from satnet import Encoding, adjacent_pairs, apply, count, solve, sorts

HERE = os.path.dirname(os.path.abspath(__file__))


def small_facts(n, caps):
    out = subprocess.run([os.path.join(HERE, 'small_facts'), str(n)] + [str(c) for c in caps],
                         capture_output=True, text=True, check=True).stdout
    return int(re.search(r': (\d+) sorting networks', out).group(1))


def brute_count(n, prefix, free_layers):
    """Number of choices of the free layers (each from its list) for which prefix + free sorts."""
    inputs = sorted({tuple(apply(prefix, x)) for x in itertools.product((0, 1), repeat=n)})
    w = [sum(1 << q for q, x in enumerate(inputs) if x[c]) for c in range(n)]   # bit-parallel wires
    target = [sum(1 << q for q, x in enumerate(inputs) if c >= n - sum(x)) for c in range(n)]
    total = 0
    for choice in itertools.product(*free_layers):
        v = list(w)
        for L in choice:
            for (a, b) in L:
                v[a], v[b] = v[a] & v[b], v[a] | v[b]
        total += v == target
    return total


def fires(layers, t, comp, n):
    """Does comparator comp of layer t fire on some binary input?"""
    a, b = comp
    for x in itertools.product((0, 1), repeat=n):
        y = apply(layers[:t], x)
        if y[a] > y[b]:
            return True
    return False


def last_layer_ok(net, n):
    return all(not fires(net, len(net) - 1, (a, b), n) for (a, b) in net[-1] if b >= a + 2)


def enumerate_networks(n, d, prefix=(), caps=None, allowed=None, limit=None):
    from pysat.solvers import Solver
    enc = Encoding(n, d, caps=caps, prefix=prefix, allowed=allowed)
    gv = enc.gvars()
    with Solver(name='cadical195', bootstrap_with=enc.clauses) as s:
        while s.solve():
            m = s.get_model()
            yield [list(L) for L in prefix] + enc.network(m)
            val = {abs(l): l > 0 for l in m}
            s.add_clause([-v if val[v] else v for v in gv])
            if limit is not None:
                limit -= 1
                if limit == 0:
                    return


def main():
    print('1. model counts against small_facts (brute force over all networks with these caps)')
    for n, caps in [(3, [1, 1, 1]), (4, [2, 2, 2]), (4, [1, 2, 2]), (4, [2, 2, 2, 2]), (5, [2, 2, 2, 2]),
                    (5, [1, 1, 2, 2, 2]), (5, [1, 2, 2, 2, 2]), (5, [2, 1, 2, 2, 2]),
                    (5, [2, 2, 2, 2, 2])]:
        c, ref = count(Encoding(n, len(caps), caps=caps)), small_facts(n, caps)
        print(f'   n={n} caps {caps}: SAT models {c}, brute force {ref}')
        assert c == ref

    print('2. fixed prefix and allowed pairs, against a brute force')
    M5 = matchings(5)
    adj5 = [m for m in M5 if all(b == a + 1 for (a, b) in m)]
    for prefix, frees, allowed in [
            ([[(0, 1), (2, 3)]], [M5] * 4, None),
            ([[(0, 1), (2, 3)]], [M5] * 3 + [adj5], [None, None, None, adjacent_pairs(5)]),
            ([[(0, 2)], [(1, 3)]], [M5] * 3 + [adj5], [None, None, None, adjacent_pairs(5)]),
            ([[(0, 4), (1, 3)]], [[m for m in M5 if len(m) <= 1]] + [M5] * 3, None)]:
        caps = [max(len(m) for m in f) for f in frees]
        c = count(Encoding(5, len(frees), caps=caps, prefix=prefix, allowed=allowed))
        ref = brute_count(5, prefix, frees)
        print(f'   prefix {prefix}, {len(frees)} free layers{" (last adjacent)" if allowed else ""}: '
              f'SAT models {c}, brute force {ref}')
        assert c == ref

    print('3. known depths with a fixed maximal first layer')
    for n, first, d_bad, d_good in [(7, [(0, 1), (2, 3), (4, 5)], 5, 6),
                                    (9, [(0, 1), (2, 3), (4, 5), (6, 7)], 6, 7)]:
        ok_bad, _ = solve(Encoding(n, d_bad - 1, prefix=[first]))
        ok_good, m = solve(enc := Encoding(n, d_good - 1, prefix=[first]))
        net = [first] + enc.network(m)
        print(f'   n={n}: depth {d_bad} {"SAT" if ok_bad else "UNSAT"}, depth {d_good} '
              f'{"SAT" if ok_good else "UNSAT"} (witness sorts: {sorts(net, n)})')
        assert not ok_bad and ok_good and sorts(net, n)

    print('4. the last-layer lemma on actual sorting networks')
    for n, d in [(4, 3), (4, 4), (5, 5)]:
        nets = list(enumerate_networks(n, d))
        assert all(sorts(net, n) for net in nets)
        bad = [net for net in nets if not last_layer_ok(net, n)]
        long_ = sum(1 for net in nets for (a, b) in net[-1] if b >= a + 2)
        print(f'   n={n}, depth {d}: {len(nets)} sorting networks (all of them), {long_} last-layer '
              f'comparators of length >= 2, none fires: {not bad}')
        assert not bad
    nets = list(enumerate_networks(9, 6, prefix=[[(0, 1), (2, 3), (4, 5), (6, 7)]], limit=60))
    long_ = sum(1 for net in nets for (a, b) in net[-1] if b >= a + 2)
    bad = [net for net in nets if not last_layer_ok(net, 9)]
    print(f'   n=9, depth 7: {len(nets)} sorting networks from SAT, {long_} last-layer comparators of '
          f'length >= 2, none fires: {not bad}')
    assert not bad

    print('5. side facts')
    ok, _ = solve(Encoding(7, 5, caps=[2, None, None, None, None], prefix=[[(0, 1), (2, 3)]]))
    print(f'   7 channels, depth 6, |L1| = |L2| = 2 (the analogue of (H9) at n = 7): '
          f'{"a sorting network exists" if ok else "no sorting network"}')
    assert not ok
    ok, _ = solve(Encoding(7, 5, caps=[3, None, None, None, None], prefix=[[(0, 1), (2, 3)]]))
    print(f'   7 channels, depth 6, |L1| = 2, |L2| = 3: {"a sorting network exists" if ok else "none"}')
    ok, _ = solve(Encoding(9, 6, caps=[4, None, None, None, None, None], prefix=[[(0, 1), (2, 3), (4, 5)]]))
    print(f'   9 channels, depth 7, |L1| = 3, |L2| <= 4: {"a sorting network exists" if ok else "none"}')
    ok, _ = solve(Encoding(9, 6, caps=[3, None, None, None, None, None],
                           prefix=[[(0, 1), (2, 3), (4, 5), (6, 7)]]))
    print(f'   9 channels, depth 7, |L1| = 4, |L2| <= 3: {"a sorting network exists" if ok else "none"}')
    thin = []
    for caps in itertools.product((1, 2), repeat=5):
        if not solve(Encoding(5, 5, caps=list(caps)))[0]:
            thin.append(caps)
    assert all(sum(c == 1 for c in caps) >= 2 for caps in thin)
    assert all(caps in thin for caps in itertools.product((1, 2), repeat=5) if sum(c == 1 for c in caps) >= 2)
    print(f'   5 channels, depth 5, caps in {{1,2}}: no sorting network exactly when at least two '
          f'layers have one comparator ({len(thin)} of 32 cap vectors)')
    ok, _ = solve(Encoding(7, 7, caps=[1, 1, 3, 3, 3, 3, 3]))
    print(f'   7 channels, layer sizes at most (1,1,3,3,3,3,3): '
          f'{"a sorting network exists" if ok else "none"} (so two infinities alone cannot refute (H9))')
    assert ok
    near = [[(0, 1), (2, 3), (4, 5)], [(0, 2), (1, 6), (7, 8)], [(1, 7), (2, 3), (4, 8), (5, 6)],
            [(0, 1), (2, 8), (3, 4), (5, 7)], [(1, 3), (2, 5), (4, 7), (6, 8)], [(0, 1), (2, 3), (4, 5), (6, 7)],
            [(1, 2), (3, 4), (5, 6), (7, 8)]]
    fails = sum(1 for x in itertools.product((0, 1), repeat=9) if apply(near, x) != sorted(x))
    print(f'   the near miss of h9.md section 6 fails on {fails} of the 512 binary inputs')
    assert fails == 18

    print('6. (P7) and the classes it settles (h9.md section 7.4)')
    for name in ('cadical195', 'glucose4'):
        ok, _ = solve(Encoding(7, 6, caps=[1, None, None, None, None, None]), name)
        print(f'   (P7): 7 channels, at most 6 layers, at most one comparator in layer 1 -- '
              f'{"a sorting network exists" if ok else "no sorting network"} ({name})')
        assert not ok
    print(f'   the 5-channel analogue is false: {count(Encoding(5, 5, caps=[1, 2, 2, 2, 2]))} depth-5 sorters '
          f'on 5 channels have one comparator in layer 1')
    inf = float('inf')
    L1 = [(0, 1), (2, 3), (4, 5)]
    reductions = {'(0,2)(1,3)': ([(0, 2), (1, 3)], {0: -1, 3: 1}), '(0,2)(1,6)': ([(0, 2), (1, 6)], {1: 1, 2: -1}),
                  '(0,3)(4,6)': ([(0, 3), (4, 6)], {0: -1, 4: -1}), '(0,3)(1,6)': ([(0, 3), (1, 6)], {1: 1, 3: 1}),
                  '(0,6)(3,7)': ([(0, 6), (3, 7)], {0: -1, 3: 1}), '(0,6)(2,7)': ([(0, 6), (2, 7)], {0: -1, 2: -1}),
                  '(0,2)(4,6)': ([(0, 2), (4, 6)], {0: -1, 4: -1}), '(0,2)(5,6)': ([(0, 2), (5, 6)], {0: -1, 5: 1})}
    for name, (L2, cfg) in reductions.items():
        x = [inf * cfg[c] if c in cfg else c + 0.5 for c in range(9)]
        per_layer = []
        for L in (L1, L2):
            per_layer.append(sum(1 for (a, b) in L if abs(x[a]) != inf and abs(x[b]) != inf))
            for (a, b) in L:
                if x[a] > x[b]:
                    x[a], x[b] = x[b], x[a]
        sign = ' '.join(f'{"+" if v > 0 else "-"}{c}' for c, v in sorted(cfg.items()))
        print(f'   L2 = {name}: infinities {sign} leave {per_layer[0]} comparator between reals in layer 1 '
              f'and {per_layer[1]} in layer 2')
        assert per_layer == [1, 0]
    print('all validation checks passed')


if __name__ == '__main__':
    random.seed(0)
    main()
