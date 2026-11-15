#!/usr/bin/env python3
"""Independent finite checks of the sentinel relaxation's two encodings."""
import itertools
import json
from pathlib import Path
import random

from pysat.solvers import Solver

from netlib import matchings, placements
from sentinel_cegar import (CNF, HAND_DEPTH, Master, adversary, passes,
                           profile_condition, simulate)


def check_profiles():
    cases = 0
    # No network assumptions: check the Boolean property against its direct
    # definition, including empty layers before/between the first active ones.
    for r, d in [(3, 4), (5, 6), (7, 7), (9, 8)]:
        rng = random.Random(r)
        profiles = list(itertools.product(range(r // 2 + 1), repeat=min(d, 4)))
        profiles += [tuple(rng.randrange(r // 2 + 1) for _ in range(d)) for _ in range(300)]
        for p in profiles:
            for strong, h9, sizes in [(False, False, False), (True, False, False),
                                      (True, True, False), (True, True, True)]:
                cnf = CNF()
                rows = [[True] * k for k in p]
                v = profile_condition(cnf, rows, r, HAND_DEPTH, strong, h9, sizes)
                cnf.add(v)
                with Solver(name='cadical195', bootstrap_with=cnf.clauses) as s:
                    assert s.solve() == passes(p, r, HAND_DEPTH, strong, h9, sizes), (r, p)
                cases += 1
    print(f'profile properties: {cases} cases passed', flush=True)


def check_master():
    cases = 0
    for n, d, r, sizes in [(4, 3, 3, False), (5, 3, 4, True)]:
        layers = matchings(n)
        for placement in placements(n, n - r):
            p = [placement.get(i, 0) for i in range(n)]
            master = Master(n, d, adjacent=False)
            master.restriction(p, HAND_DEPTH, True, True, sizes)
            with Solver(name='cadical195', bootstrap_with=master.clauses) as s:
                for tail in itertools.product(layers, repeat=d - 1):
                    net = [master.prefix, *tail]
                    assumptions = [v if (a, b) in tail[t - 1] else -v
                                   for (t, a, b), v in master.g.items()]
                    expected = passes(simulate(net, p), r, HAND_DEPTH, True, True, sizes)
                    assert s.solve(assumptions=assumptions) == expected, (net, p)
                    cases += 1
    print(f'master vs direct ternary simulation: {cases} cases passed', flush=True)


def check_adversary():
    cases = 0
    rng = random.Random(20261114)
    for n, d, rs in [(5, 5, [3]), (7, 6, [3, 5]), (8, 6, [7]), (10, 7, [9])]:
        layers = matchings(n)
        for _ in range(30):
            net = [[(i, i + 1) for i in range(0, n - 1, 2)]]
            net += [rng.choice(layers) for _ in range(d - 1)]
            for r in rs:
                bad = []
                for placement in placements(n, n - r):
                    p = [placement.get(i, 0) for i in range(n)]
                    if not passes(simulate(net, p), r, HAND_DEPTH, True, True):
                        bad.append(p)
                for sizes in [False, True]:
                    if sizes:
                        bad = []
                        for placement in placements(n, n - r):
                            p = [placement.get(i, 0) for i in range(n)]
                            if not passes(simulate(net, p), r, HAND_DEPTH, True, True, sizes):
                                bad.append(p)
                    found = adversary(net, n, r, HAND_DEPTH, True, True, 'cadical195', sizes)
                    assert (found is not None) == bool(bad), (n, net, r)
                    if found is not None:
                        assert found in bad
                    cases += 1
    print(f'adversary vs ALL signed placements: {cases} networks/retained sizes passed', flush=True)


def check_positive():
    # An exact SAT witness found independently with satnet.py; all 512 binary
    # inputs are checked again. It must survive every selected restriction.
    from netlib import sorts
    path = Path(__file__).resolve().parents[1] / 'results/profile-9-2-8.json'
    net = json.loads(path.read_text())['network']
    assert sorts(net, 9)
    for r in [3, 5, 7]:
        for sizes in [False, True]:
            assert adversary(net, 9, r, HAND_DEPTH, True, True, 'cadical195', sizes) is None
    master = Master(9, 8, first=2)
    assert [list(x) for x in master.prefix] == net[0]
    rng = random.Random(1917)
    for _ in range(20):
        r = rng.choice([3, 5, 7])
        p = [rng.choice([-1, 1]) for _ in range(9)]
        for i in rng.sample(range(9), r):
            p[i] = 0
        master.restriction(p, HAND_DEPTH, True, True, True)
    assumptions = [v if [a, b] in net[t] else -v for (t, a, b), v in master.g.items()]
    with Solver(name='cadical195', bootstrap_with=master.clauses) as s:
        assert s.solve(assumptions=assumptions)
    print('positive control: verified 9-channel sorter survives all adversaries and 20 master rows', flush=True)


if __name__ == '__main__':
    check_profiles()
    check_master()
    check_adversary()
    check_positive()
