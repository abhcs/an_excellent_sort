#!/usr/bin/env python3
"""Small direct controls for the shared-middle-pair hand lemma; no SAT."""
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREFIX = [[(0, 1), (2, 4)], [(0, 5)], [(4, 5)],
          [(1, 2), (3, 4)], [(2, 3)], [(3, 5)]]


def run(x, network):
    x = list(x)
    for layer in network:
        for a, b in layer:
            x[a], x[b] = min(x[a], x[b]), max(x[a], x[b])
    return x


def matchings(vertices):
    if not vertices:
        yield ()
        return
    x, *rest = vertices
    yield from matchings(rest)
    for y in rest:
        for tail in matchings([z for z in rest if z != y]):
            yield ((x, y),) + tail


def cone(c, network):
    reached = {c}
    for layer in network:
        reached |= {v for a, b in layer if a in reached or b in reached for v in (a, b)}
    return reached


def main():
    permutations = list(itertools.permutations(range(6)))
    outputs = [run(x, PREFIX) for x in permutations]
    supports = [sorted({x[c] for x in outputs}) for c in range(6)]
    assert supports == [[0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2],
                        [3, 4], [2, 3, 4, 5], [4, 5]]
    degrees = [sum(r in row for row in supports) for r in range(6)]
    assert max(map(len, supports)) <= 4 and max(degrees) <= 4
    full = [set(row) for row in supports if len(row) == 4]
    assert all(len(a & b) % 2 == 0 for a, b in itertools.combinations(full, 2))
    outer = (0, 1, 4, 5)
    target = {c: set(range(4)) if c < 2 else set(range(2, 6)) for c in outer}
    layers = list(matchings(list(range(6))))
    assert len(layers) == 76
    triples = list(itertools.combinations(outer, 3))
    triple_survivors = {t: 0 for t in triples}
    positive = {}
    for p, s in itertools.product(layers, repeat=2):
        satisfied = {c for c in outer if cone(c, (p, s)) == target[c]}
        for triple in triples:
            triple_survivors[triple] += set(triple) <= satisfied
        for pair in itertools.combinations(outer, 2):
            if set(pair) <= satisfied:
                positive.setdefault(pair, (p, s))
    assert not any(triple_survivors.values()) and len(positive) == 6
    # A known valid completion controls the application to actual intervals.
    sorter = [[(i, i+1) for i in range(t % 2, 5, 2)] for t in range(6)]
    assert all(run(x, sorter) == list(range(6)) for x in permutations)
    control = [run(x, sorter[:4]) for x in permutations]
    control_supports = [set(x[c] for x in control) for c in range(6)]
    assert sum(control_supports[c] == target[c] for c in outer) <= 2
    assert all(control_supports[c] <= cone(c, sorter[4:]) for c in range(6))
    # Exhaust all families of four-position intervals at width13.
    compatible = 0
    windows = [set(range(a, a+4)) for a in range(10)]
    for mask in range(1 << 10):
        starts = [a for a in range(10) if mask >> a & 1]
        if any(len(windows[a] & windows[b]) % 2 for a, b in itertools.combinations(starts, 2)):
            continue
        matching = set()
        for a in starts:
            matching |= {(a, a+1), (a+2, a+3)}
        endpoints = [v for edge in matching for v in edge]
        assert len(set(endpoints)) == len(endpoints)
        assert all(all(any(v in edge and set(edge) <= windows[a] for edge in matching)
                       for v in windows[a]) for a in starts)
        compatible += 1
    report = dict(status='VERIFIED', uses_sat=False, actual_prefix=PREFIX,
                  actual_prefix_permutations=720, actual_rank_supports=supports,
                  actual_rank_degrees=degrees, violating_outer_wires=[0, 1, 4],
                  matching_pairs_checked=76**2,
                  forbidden_triples={','.join(map(str, k)): v for k, v in triple_survivors.items()},
                  two_demand_positive_controls={','.join(map(str, k)): v for k, v in positive.items()},
                  complete_sorter=sorter, complete_sorter_permutations=720,
                  full_interval_families_checked=1024, parity_compatible_families=compatible,
                  n13_endpoint_clauses=32,
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  proof_sha256=hashlib.sha256((HERE / 'd13_feedback_round6_middle_pair.md').read_bytes()).hexdigest())
    (HERE / 'results/d13_feedback_round6-middle-pair-verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
