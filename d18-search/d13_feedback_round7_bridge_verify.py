#!/usr/bin/env python3
"""All real-order and matching controls for the three-rank bridge lemma."""
import hashlib
import itertools
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
PREFIX = [[(2, 3), (4, 5), (6, 7)], [(1, 2), (3, 4), (7, 8)],
          [(0, 1), (2, 3), (4, 5)], [(1, 2), (5, 6)],
          [(0, 1), (4, 5), (6, 7)], [(3, 4), (5, 6), (7, 8)],
          [(2, 3), (4, 5), (6, 7)], [(1, 2), (3, 4), (5, 6)],
          [(2, 3), (4, 5), (6, 7)]]


def matchings(vertices):
    if not vertices:
        yield ()
        return
    x, *rest = vertices
    yield from matchings(rest)
    for y in rest:
        for tail in matchings([v for v in rest if v != y]):
            yield ((x, y),) + tail


def cone(c, network):
    reached = {c}
    for layer in network:
        reached |= {v for a, b in layer if a in reached or b in reached for v in (a, b)}
    return reached


def main():
    started = time.monotonic()
    supports = [set() for _ in range(9)]
    witnesses = [{} for _ in range(9)]
    flat = [edge for layer in PREFIX for edge in layer]
    runs = 0
    for permutation in itertools.permutations(range(9)):
        values = list(permutation)
        for a, b in flat:
            if values[a] > values[b]:
                values[a], values[b] = values[b], values[a]
        for c, rank in enumerate(values):
            supports[c].add(rank)
            witnesses[c].setdefault(rank, permutation)
        runs += 1
    intervals = [(0, 3), (0, 2), (0, 2), (3, 5), (2, 4),
                 (5, 8), (4, 6), (6, 8), (6, 8)]
    assert runs == 362880
    assert all(s == set(range(lo, hi+1)) for s, (lo, hi) in zip(supports, intervals))
    rank_degrees = [sum(k in s for s in supports) for k in range(9)]
    assert max(map(len, supports)) <= 4 and max(rank_degrees) <= 4
    full = [s for s in supports if len(s) == 4]
    assert all(len(a & b) % 2 == 0 for a, b in itertools.combinations(full, 2))
    for a in range(4):
        assert sum(intervals[c] == ((a, a+3) if c < a+2 else (a+2, a+5))
                   for c in (a, a+1, a+4, a+5)) <= 2
    left, bridge, right = set(range(4)), {3, 4, 5}, set(range(5, 9))
    last_layers = list(matchings(list(range(9))))
    assert len(last_layers) == 2620
    preserve = [layer for layer in last_layers
                if sum(set(e) <= left for e in layer) == 2
                and sum(set(e) <= right for e in layer) == 2]
    assert len(preserve) == 9
    assert not any(any(set(e) <= bridge for e in layer) for layer in preserve)
    targets = {0: left, 3: bridge, 5: right}
    controls = {
        'omit_left': [[(3, 6), (5, 7)], [(0, 1), (3, 4), (5, 6), (7, 8)]],
        'omit_bridge': [[(0, 2), (5, 7)], [(0, 1), (2, 3), (5, 6), (7, 8)]],
        'omit_right': [[(0, 2), (3, 4)], [(0, 1), (2, 3), (4, 5), (6, 7)]],
    }
    for label, network in controls.items():
        omitted = {'omit_left': 0, 'omit_bridge': 3, 'omit_right': 5}[label]
        for layer in network:
            vertices = [v for e in layer for v in e]
            assert len(vertices) == len(set(vertices))
        assert all(target <= cone(c, network) for c, target in targets.items() if c != omitted)
        assert not targets[omitted] <= cone(omitted, network)
    clauses = {}
    for n in (13, 18):
        count = 0
        for a in range(n-8):
            for i, j, c in itertools.product(range(a, a+4), range(a+5, a+9), range(a+3, a+6)):
                if len({i, j, c}) == 3:
                    count += 1
        assert count == 40 * (n-8)
        clauses[n] = count
    result = dict(status='VERIFIED', uses_sat=False, prefix=PREFIX,
                  real_permutations_checked=runs, exact_intervals=intervals,
                  rank_degrees=rank_degrees, real_order_witnesses=witnesses,
                  final_matchings_checked=2620, final_matchings_preserving_full_intervals=9,
                  surviving_final_matchings=0, two_demand_controls=controls,
                  endpoint_clause_counts=clauses, seconds=time.monotonic()-started,
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  proof_sha256=hashlib.sha256((HERE / 'd13_feedback_round7_bridge.md').read_bytes()).hexdigest())
    (HERE / 'results/d13_feedback_round7-bridge-verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('real_order_witnesses', 'prefix')}, indent=2))


if __name__ == '__main__':
    main()
