"""h9_certs_check.py -- the certificates of h9_tree.c never fire on a real sorting network.

Each certificate B3, B4, C4, B5, B5s, C5 of h9_tree.c claims "no completion of this prefix sorts".
So none of them may fire on any prefix of an actual depth-7 sorting network on 9 channels.  This
script re-implements the certificates independently -- by simulating the network on real numbers
with +-infinity, and by computing images of all 512 binary inputs -- and runs them on sorting
networks found by SAT, including networks whose first or second layer is thin.  It also checks that
the certificates DO fire where they should, on the prefixes of non-sorting networks used as controls.

usage: .venv/bin/python h9_certs_check.py [count]   (networks per shape, default 40)
"""
import itertools
import random
import sys

from satnet import Encoding, solve, sorts

N = 9
INF = float('inf')


def run_counts(layers, cfg):
    """cfg: channel -> +1/-1 (infinities); the other channels get distinct finite reals.  Returns the
    number of comparators per layer that meet two reals (an actual simulation on numbers)."""
    x = [INF * cfg[c] if c in cfg else float(c) + 0.5 for c in range(N)]
    out = []
    for L in layers:
        cnt = 0
        for (a, b) in L:
            if abs(x[a]) != INF and abs(x[b]) != INF:
                cnt += 1
            if x[a] > x[b]:
                x[a], x[b] = x[b], x[a]
        out.append(cnt)
    return out


def placements():
    for pos in itertools.combinations(range(N), 4):
        for sg in itertools.product((1, -1), repeat=4):
            yield dict(zip(pos, sg))


def blinding_certs(prefix):
    """Which of B3, B4, B5, B5s fire for this prefix (len(prefix) = 3, 4 or 5)?"""
    t = len(prefix)
    fired = set()
    for cfg in placements():
        cnt = run_counts(prefix, cfg)
        nz = [c for c in cnt if c]
        if t == 3 and not nz:
            fired.add('B3')
        if t == 4 and (len(nz) <= 1 or (len(nz) == 2 and nz == [1, 1])):
            fired.add('B4')
        if t == 5:
            # layers 6, 7 add at most two nonempty layers with at most 2 comparators each
            if len(nz) <= 2 or (len(nz) == 3 and nz[:2] == [1, 1]):
                fired.add('B5')
            elif sum(nz) + 4 <= 8:
                fired.add('B5s')
    return fired


def image(prefix):
    S = set()
    for v in itertools.product((0, 1), repeat=N):
        x = list(v)
        for L in prefix:
            for (a, b) in L:
                if x[a] > x[b]:
                    x[a], x[b] = x[b], x[a]
        S.add(tuple(x))
    return S


def cone_cert(prefix, need):
    S = image(prefix)
    for k in range(N):                              # output k must be 1 iff weight >= 9 - k
        dep = 0
        for c in range(N):
            if any(s[c] == 0 and sum(s) == 8 - k and s[:c] + (1,) + s[c + 1:] in S for s in S):
                dep += 1
        if dep >= need:
            return True
    return False


def certificates(net):
    fired = set()
    for t in (3, 4, 5):
        fired |= {f'{c}@{t}' for c in blinding_certs(net[:t])}
    if cone_cert(net[:4], 9):
        fired.add('C4')
    if cone_cert(net[:5], 5):
        fired.add('C5')
    return fired


def networks(first, cap2, count, seed):
    """Up to `count` distinct depth-7 sorting networks with the given first layer and |L2| <= cap2."""
    enc = Encoding(N, 6, caps=[cap2, None, None, None, None, None], prefix=[first])
    from pysat.solvers import Solver
    rng = random.Random(seed)
    gv = enc.gvars()
    out = []
    with Solver(name='cadical195', bootstrap_with=enc.clauses) as s:
        while len(out) < count:
            assum = [v if rng.random() < 0.03 else -v for v in rng.sample(gv, 12)]
            if not s.solve(assumptions=assum):
                if not s.solve():
                    break
            model = s.get_model()
            net = [list(first)] + enc.network(model)
            out.append(net)
            val = {abs(l): l > 0 for l in model}
            s.add_clause([-v if val[v] else v for v in gv])
    return out


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    shapes = [([(0, 1), (2, 3), (4, 5), (6, 7)], 4), ([(0, 1), (2, 3), (4, 5), (6, 7)], 3),
              ([(0, 1), (2, 3), (4, 5)], 4)]
    total = 0
    for first, cap2 in shapes:
        nets = networks(first, cap2, count, seed=len(first) * 10 + cap2)
        for net in nets:
            assert sorts(net, N) and len(net) == 7
            f = certificates(net)
            assert not f, (net, f)
        total += len(nets)
        print(f'|L1| = {len(first)}, |L2| <= {cap2}: {len(nets)} sorting networks, '
              f'no certificate fires on any prefix', flush=True)
    # controls: the certificates must fire on prefixes of networks that cannot sort
    rng = random.Random(1)
    from netlib import matchings
    M = matchings(N)
    L1 = [(0, 1), (2, 3), (4, 5)]
    fired_any = 0
    for _ in range(30):
        L2 = rng.choice([m for m in M if len(m) <= 3])
        net = [L1, list(L2)] + [list(rng.choice(M)) for _ in range(5)]
        if certificates(net):
            fired_any += 1
    print(f'controls: on 30 random (H9)-shaped networks some certificate fired {fired_any} times')
    assert fired_any > 0
    print(f'checked {total} sorting networks')


if __name__ == '__main__':
    main()
