#!/usr/bin/env python3
"""Local arithmetic and witness checks for the hand621 merger proof."""
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIRST = [((1, 8), (3, 6), (4, 7)), ((1, 8), (3, 7), (4, 6))]
INPUTS = {
    'L': (0, 1, 3, 4, 5, 6, 7, 8, 2),
    'H': (0, 1, 2, 3, 4, 5, 6, 7, 8),
    'K': (3, 4, 5, 6, 7, 8, 1, 2, 0),
    'J': (0, 1, 2, 3, 4, 6, 5, 7, 8),
}
ROWS = [
    (0, 'max', 'L', 2, 'H', 8),
    (1, 'max', 'L', 2, 'H', 8),
    (2, 'max', 'L', 3, 'H', 8),
    (3, 'max', 'K', 4, 'H', 8),
    (4, 'max', 'K', 4, 'H', 8),
    (5, 'min', 'L', 2, 'J', 6),
    (6, 'min', 'L', 2, 'H', 6),
    (7, 'min', 'L', 2, 'H', 7),
]


def apply(x, layer):
    y = list(x)
    for a, b in layer:
        y[a], y[b] = min(y[a], y[b]), max(y[a], y[b])
    return y


def valid(x):
    return sorted(x) == list(range(9)) and list(x[:6]) == sorted(x[:6]) and x[6] < x[7]


def main():
    triples = [set(range(i, i + 3)) for i in range(4)]
    assert not set.intersection(*triples)
    intersections = []
    for j in range(6):
        available = [t for t in triples if j not in t]
        intersections.append(sorted(set.intersection(*available)))
    assert intersections == [[3], [3, 4], [3, 4, 5], [0, 1, 2], [1, 2], [2]]
    blind_checks = []
    for j, adjacent in ((2, (0, 1)), (3, (4, 5))):
        reals = set(adjacent) | {6, 7, 8}
        for u, v in itertools.permutations(intersections[j], 2):
            first = [(j, 8), (u, 6), (v, 7)]
            assert all(not set(e) <= reals for e in first)
            blind_checks.append(dict(first=first, reals=sorted(reals)))
    assert all(valid(x) for x in INPUTS.values())
    interleavings = []
    for a in itertools.combinations(range(9), 6):
        remaining = [v for v in range(9) if v not in a]
        for b in itertools.combinations(remaining, 2):
            c = next(v for v in remaining if v not in b)
            x = a + b + (c,)
            assert valid(x)
            interleavings.append(x)
    assert len(interleavings) == 252
    audit = []
    for first in FIRST:
        fixed = {name: apply(x, first) for name, x in INPUTS.items()}
        assert fixed['L'][8] == 2 and fixed['H'][8] == 8
        row_checks = []
        for v, which, low, lo, high, hi in ROWS:
            operation = min if which == 'min' else max
            assert operation(fixed[low][8], fixed[low][v]) == lo
            assert operation(fixed[high][8], fixed[high][v]) == hi
            assert hi - lo >= 4
            support = sorted({operation(y[8], y[v]) for x in interleavings
                              for y in [apply(x, first)]})
            assert support == list(range(min(support), max(support) + 1))
            assert len(support) >= 5
            row_checks.append(dict(partner=v, output=which, low_input=low, low=lo,
                                   high_input=high, high=hi, exact_support=support))
        audit.append(dict(first=first, witness_outputs=fixed, partner_rows=row_checks))
    result = dict(status='VERIFIED', uses_sat=False, enumerates_matchings=False,
                  triple_intersections=intersections, blind_221_checks=blind_checks,
                  input_witnesses=INPUTS, complete_input_count=len(interleavings),
                  first_layer_audits=audit,
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  proof_sha256=hashlib.sha256((HERE / 'd13_feedback_round4_merger621.md').read_bytes()).hexdigest())
    output = HERE / 'results/d13_feedback_round4-merger621-verification.json'
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(status=result['status'], first_layers=2, endpoint_rows=16,
                         complete_input_count=252, uses_sat=False)))


if __name__ == '__main__':
    main()
