#!/usr/bin/env python3
"""Check exact transport of normalized sentinel placements; no SAT dependency.

The local seven-type calculation proves closure and the distance-loss rule.
The larger checks audit its application to the complete two-layer cover.
No cover case is eliminated by these checks.
"""
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import random

from two_layer_cover import half_blind_family, type_step
from verify_restriction_structure import random_matching, read_cover, real_mask

TYPES = tuple((a, b) for a in (-1, 0, 1) for b in (-1, 0, 1)
              if abs(a - b) <= 1)
LOWER = {(-1, 0), (0, -1)}
UPPER = {(0, 1), (1, 0)}


def distance(p, q):
    assert p.count(0) == q.count(0)
    return (real_mask(p) ^ real_mask(q)).bit_count() // 2


def losses(p, q, layer):
    joint = list(zip(p, q))
    lower = sum({joint[a], joint[b]} == LOWER for a, b in layer)
    upper = sum({joint[a], joint[b]} == UPPER for a, b in layer)
    return lower, upper


def check_local():
    records = []
    for x, y in itertools.product(TYPES, repeat=2):
        low = (min(x[0], y[0]), min(x[1], y[1]))
        high = (max(x[0], y[0]), max(x[1], y[1]))
        assert low in TYPES and high in TYPES
        kind = 'lower' if {x, y} == LOWER else 'upper' if {x, y} == UPPER else None
        if kind:
            assert low == ((-1, -1) if kind == 'lower' else (0, 0))
            assert high == ((0, 0) if kind == 'lower' else (1, 1))
        else:
            assert Counter((x, y)) == Counter((low, high))
        records.append(dict(inputs=[x, y], outputs=[low, high], loss=kind))

    # Pure-minus versus pure-plus: an exact count on each first-layer pair.
    pure = ((-1, 0), (0, 0), (0, 1), (-1, 1))
    for x, y in itertools.product(pure, repeat=2):
        low = (min(x[0], y[0]), min(x[1], y[1]))
        high = (max(x[0], y[0]), max(x[1], y[1]))
        real_comparisons = int(x[0] == y[0] == 0) + int(x[1] == y[1] == 0)
        common_after = (low, high).count((0, 0))
        extra = int(x == y == (-1, 0)) + int(x == y == (0, 1))
        assert real_comparisons == common_after + extra
    return records


def check_pair(p, q, layer):
    assert all(t in TYPES for t in zip(p, q))
    before = distance(p, q)
    lo, hi = losses(p, q, layer)
    pp, qq = type_step(p, layer), type_step(q, layer)
    after = distance(pp, qq)
    assert all(t in TYPES for t in zip(pp, qq))
    assert after == before - lo - hi
    assert after >= abs(p.count(1) - q.count(1))
    if real_mask(p) == real_mask(q):
        assert p == q and pp == qq
    comparable = all(a <= b for a, b in zip(p, q)) or all(a >= b for a, b in zip(p, q))
    if comparable:
        assert before == after == abs(p.count(1) - q.count(1))
    return pp, qq


def check_cover(cover):
    cases, sha = read_cover(cover)
    rng = random.Random(20261115)
    records, transport_steps = [], 0
    for case in cases:
        n = case['n']
        states = [type_step(p, case['layers'][1])
                  for p in half_blind_family(n, case['layers']).values()]
        pairs = []
        for i, j in itertools.combinations(range(len(states)), 2):
            p, q = states[i], states[j]
            assert all(t in TYPES for t in zip(p, q))
            d = distance(p, q)
            delta = abs(p.count(1) - q.count(1))
            comparable = all(a <= b for a, b in zip(p, q)) or all(a >= b for a, b in zip(p, q))
            assert comparable == (d == delta)
            pairs.append(dict(first=i, second=j, distance=d, rank_gap=delta,
                              rigid=comparable, required_losses=d-delta))
            for _ in range(6):
                p, q = check_pair(p, q, random_matching(n, rng))
                transport_steps += 1
        records.append(dict(case_id=case['case_id'], family_size=len(states),
                            states=states, pairs=pairs))
    rigid = lambda r: [p for p in r['pairs'] if p['rigid']]
    two = Counter((r['pairs'][0]['distance'], r['pairs'][0]['rank_gap'])
                  for r in records if r['family_size'] == 2)
    stats = dict(cases=len(records),
                 cases_with_rigid_pair=sum(bool(rigid(r)) for r in records),
                 cases_with_rigid_odd_pair=sum(any(p['distance'] % 2 for p in rigid(r)) for r in records),
                 cases_with_rigid_distance_at_least_3=sum(any(p['distance'] >= 3 for p in rigid(r)) for r in records),
                 sampled_transport_steps=transport_steps,
                 two_state_histogram=[dict(distance=d, rank_gap=g, cases=c)
                                      for (d, g), c in sorted(two.items())])
    if cases[0]['n'] == 18:
        assert stats['cases'] == 411
        assert stats['cases_with_rigid_pair'] == 390
        assert stats['cases_with_rigid_odd_pair'] == 382
        assert stats['cases_with_rigid_distance_at_least_3'] == 319
    return dict(cover_sha256=sha, summary=stats, cases=records)


def check_sorters():
    """Check the exact merger totals on two independently verified sorters."""
    from two_real_graph import images, sorted_bits
    rng = random.Random(20261116)
    records = []
    for name in ('e18_4_d11.json', 'dobbelaere18-78-11.json'):
        path = Path(__file__).parent / 'results' / name
        data = json.loads(path.read_text())
        n, net = data['n'], data['layers']
        assert images(n, net) == {sorted_bits(n, k) for k in range(n + 1)}
        first = net[0]
        for _ in range(256):
            states = []
            for run in range(2):
                state = [0] * n
                for a, b in first:
                    choice = rng.randrange(2)
                    state[b if choice else a] = 1 if choice else -1
                states.append(tuple(state))
            p, q = states
            delta = abs(p.count(1) - q.count(1))
            expected = distance(p, q) - delta
            joint = list(zip(p, q))
            expected_lower = min(joint.count((-1, 0)), joint.count((0, -1)))
            expected_upper = min(joint.count((0, 1)), joint.count((1, 0)))
            lower = upper = 0
            for layer in net:
                lo, hi = losses(p, q, layer)
                lower, upper = lower + lo, upper + hi
                p, q = check_pair(p, q, layer)
            assert list(p) == sorted(p) and list(q) == sorted(q)
            assert distance(p, q) == delta and lower + upper == expected
            assert lower == expected_lower and upper == expected_upper
        records.append(dict(file=name, source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                            verified_binary_inputs=1 << n, checked_placement_pairs=256))
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cover', type=Path, default=Path(__file__).parent / 'prefixes/complete18.jsonl')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    local = check_local()
    result = check_cover(args.cover)
    result.update(local_cases=len(local), local_table=local,
                  pure_support_count_cases=16,
                  sorting_controls=check_sorters(),
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope='Structural relations only: no sorting-network cover case is eliminated.')
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('cases','local_table')}), flush=True)


if __name__ == '__main__':
    main()
