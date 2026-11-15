#!/usr/bin/env python3
"""Audit the hand proof for L1=01 23 45, L2=06 78; no solver imports.

This checker deliberately does not import any exploratory restriction code.
The proof uses the listed traces, prices, and small matching classifications.
The matching scans and all-real-order runs are independent cross-checks.
"""
import hashlib
import itertools
import json
from pathlib import Path

FIRST = ((0, 1), (2, 3), (4, 5))
SECOND = ((0, 6), (7, 8))
PAIRS = ((2, 3), (4, 5), (7, 8))
THIRDS = (
    ((1, 2), (3, 4), (5, 7), (6, 8)),
    ((1, 2), (3, 4), (5, 8), (6, 7)),
    ((1, 2), (3, 5), (4, 7), (6, 8)),
    ((1, 2), (3, 6), (4, 7), (5, 8)),
    ((1, 2), (3, 6), (4, 8), (5, 7)),
    ((1, 3), (2, 4), (5, 7), (6, 8)),
    ((1, 6), (2, 4), (3, 7), (5, 8)),
    ((1, 6), (2, 5), (3, 7), (4, 8)),
)


def placement(text):
    return {int(token[1:]): 1 if token[0] == '+' else -1 for token in text.split()}


# Each row consists of an input placement and the five real positions after L3.
ROWS = {
    1: [('+0 +1 +2 +4', '01356'), ('+0 +1 +2 -7', '01367'),
        ('-0 +2 +4 +7', '12356'), ('-0 -2 -4 -7', '24678')],
    2: [('+0 +1 +2 +4', '01356'), ('+0 +1 -4 +7', '01456'),
        ('+0 +2 +4 -7', '01357'), ('-0 -2 -4 -7', '24578')],
    3: [('+0 +1 +2 -4', '01367'), ('-0 -2 +4 +7', '23467'),
        ('-0 -2 +4 -7', '23678'), ('-0 -2 -4 +7', '23567')],
    4: [('+0 +1 +4 -7', '01357'), ('-0 +2 +4 -7', '12357'),
        ('-0 -2 +4 -7', '23567'), ('-2 +4 +6 -7', '02357')],
    5: [('+0 +1 +4 +7', '01345'), ('-0 +2 +4 +7', '12345'), ('-0 +2 -4 -7', '12378'),
        ('-0 -2 +4 +7', '23456'), ('-0 -2 -4 -7', '23678'),
        ('-2 +4 +6 +7', '02345'), ('-2 -4 +6 -7', '02378')],
    6: [('+0 +1 -2 +4', '01456'), ('+0 +1 -2 -7', '01467'),
        ('-0 +2 +4 +7', '12456'), ('-0 +2 -4 -7', '14678'),
        ('-0 -2 +4 +7', '13456')],
    7: [('+0 +2 -4 +7', '01345'), ('+0 -2 +4 -7', '01457'),
        ('-0 +2 -4 +7', '13456'), ('-0 -2 +4 -7', '14567')],
    8: [('+0 +2 +4 +7', '01234'), ('+0 -2 -4 -7', '01578'),
        ('-0 +2 +4 +7', '12346'), ('-0 -2 -4 -7', '15678')],
}
TWICE_PRICES = {
    1: (1, 3, 1, 3, 1, 1, 3, 1, 1),
    2: (3, 3, 1, 1, 1, 3, 1, 1, 1),
    6: (0, 5, 0, 0, 5, 2, 5, 2, 0),
    7: (2, 4, 0, 0, 4, 4, 2, 0, 0),
    8: (0, 4, 2, 2, 2, 2, 0, 2, 2),
}
CONTACTS = {
    3: {'A': ('+0', '2', ('35', '47', '68')),
        'B': ('+0 +1', '28', ('35', '47')),
        'C': ('+0 +2', '25', ('47', '68')),
        'D': ('+0 -4', '24', ('35', '68'))},
    4: {'A': ('+0', '2', ('36', '47', '58')),
        'B': ('+0 +1', '26', ('13', '47', '58')),
        'C': ('+0 +4', '28', ('36', '47')),
        'D': ('+0 -4', '24', ('36', '58'))},
    5: {'E': ('+0 +4', '27', ('36', '48'))},
}
CONTACT_TABLES = {
    3: ('ADAB', 'AADC', 'ACBA'),  # optional edge -,45,48,58
    4: ('ADAC', 'AADB', 'ABCA'),  # optional edge -,46,48,68
}


def matchings(vertices):
    if not vertices:
        yield ()
        return
    a, *rest = vertices
    yield from matchings(rest)
    for j, b in enumerate(rest):
        for tail in matchings(rest[:j] + rest[j + 1:]):
            yield ((a, b),) + tail


def run(prefix, values):
    values = list(values)
    for layer in prefix:
        for a, b in layer:
            if values[a] > values[b]:
                values[a], values[b] = values[b], values[a]
    return values


def trace(prefix, p):
    signs = [p.get(i, 0) for i in range(9)]
    labels = list(range(9))
    gates = []
    for layer in prefix:
        for a, b in layer:
            if signs[a] == signs[b] == 0:
                gates.append((labels[a], labels[b]))
            elif signs[a] > signs[b]:
                signs[a], signs[b] = signs[b], signs[a]
                labels[a], labels[b] = labels[b], labels[a]
    location = {label: wire for wire, label in enumerate(labels)}
    boundary_gates = [(location[a], location[b]) for a, b in gates]
    depths, last = [0] * 9, [-1] * 9
    for index, (a, b) in enumerate(boundary_gates):
        depths[a] = depths[b] = max(depths[a], depths[b]) + 1
        last[a] = last[b] = index
    sinks = [tuple(sorted((a, b))) for index, (a, b) in enumerate(boundary_gates)
             if last[a] == last[b] == index]
    return dict(placement=p, signs=signs, labels=labels, gates=gates,
                boundary_gates=boundary_gates, depth=max(depths), sinks=sorted(sinks),
                real=[i for i, sign in enumerate(signs) if sign == 0])


def check_all_real_orders(prefix, p, row):
    initial_real = [i for i in range(9) if i not in p]
    count = 0
    for ordering in itertools.permutations(range(len(initial_real))):
        values = [100 * p.get(i, 0) for i in range(9)]
        for wire, value in zip(initial_real, ordering):
            values[wire] = value
        actual = run(prefix, values)
        reduced = values[:]
        for a, b in row['gates']:
            if reduced[a] > reduced[b]:
                reduced[a], reduced[b] = reduced[b], reduced[a]
        assert actual == [reduced[label] for label in row['labels']]
        count += 1
    return count


def symmetry_permutations():
    for targets in itertools.permutations(PAIRS):
        for swap in (False, True):
            perm = list(range(9))
            perm[1], perm[6] = (6, 1) if swap else (1, 6)
            for (a, b), (x, y) in zip(PAIRS, targets):
                perm[a], perm[b] = x, y
            yield perm


def canonical(layer):
    return min(tuple(sorted(tuple(sorted((p[a], p[b]))) for a, b in layer))
               for p in symmetry_permutations())


def count_inside(layer, vertices):
    return sum(a in vertices and b in vertices for a, b in layer)


def main():
    layers = list(matchings(list(range(9))))
    assert len(layers) == 2620
    prefix2 = (FIRST, SECOND)
    binary = list(itertools.product((0, 1), repeat=9))
    actual_image = {tuple(run(prefix2, bits)) for bits in binary}
    expected_image = {bits for bits in binary if bits[0] <= bits[1] and bits[0] <= bits[6]
                      and all(bits[a] <= bits[b] for a, b in PAIRS)}
    assert actual_image == expected_image
    forced = trace(prefix2, placement('-0'))
    assert forced['signs'][0] == -1
    assert set(map(frozenset, forced['gates'])) == set(map(frozenset, PAIRS))
    thirds = [layer for layer in layers if len(layer) == 4
              and all(0 not in edge for edge in layer) and not set(layer) & set(PAIRS)]
    assert len(thirds) == 68
    assert sorted({canonical(layer) for layer in thirds}) == list(THIRDS)
    orbit_sizes = [sum(canonical(layer) == third for layer in thirds) for third in THIRDS]
    assert orbit_sizes == [12, 12, 12, 6, 6, 12, 6, 2]
    results = []
    direct_runs = check_all_real_orders(prefix2, placement('-0'), forced)
    for case, third in enumerate(THIRDS, 1):
        prefix = (FIRST, SECOND, third)
        row_traces = []
        sets = []
        for text, expected in ROWS[case]:
            p = placement(text)
            row = trace(prefix, p)
            assert len(row['gates']) == 1, (case, text, row)
            assert row['real'] == list(map(int, expected)), (case, text, row)
            direct_runs += check_all_real_orders(prefix, p, row)
            sets.append(set(row['real']))
            row_traces.append(dict(input=text, **row))
        survivors = [layer for layer in layers if all(count_inside(layer, s) >= 2 for s in sets)]
        price_record = None
        if case in TWICE_PRICES:
            prices = TWICE_PRICES[case]
            weights = {(a, b): sum(a in s and b in s for s in sets)
                       for a, b in itertools.combinations(range(9), 2)}
            assert all(2 * weight <= prices[a] + prices[b] for (a, b), weight in weights.items())
            assert sum(prices) < 4 * len(sets) if case in (1, 2, 6) else sum(prices) == 4 * len(sets)
            tight = [edge for edge, w in weights.items() if 2 * w == sum(prices[v] for v in edge)]
            if case in (7, 8):
                # Check exactly the equality conditions used in the parity proofs.
                positive = {i for i, value in enumerate(prices) if value}
                saturating = [layer for layer in layers if set(layer) <= set(tight)
                              and positive <= {v for edge in layer for v in edge}]
                assert not saturating
                if case == 7:
                    assert [{v for e in tight if a in e for v in e if v != a} for a in (0, 6)] == [{3, 7}, {3, 7}]
                else:
                    assert {v for e in tight if 1 in e for v in e if v != 1} == {0, 6}
            assert not survivors
            price_record = dict(twice_prices=prices, twice_budget=sum(prices),
                                twice_required=4 * len(sets), tight_edges=tight)
        contacts = {}
        if case in CONTACTS:
            for name, (text, expected_sentinels, expected_sinks) in CONTACTS[case].items():
                p = placement(text)
                row = trace(prefix, p)
                assert [i for i, s in enumerate(row['signs']) if s] == list(map(int, expected_sentinels))
                assert row['sinks'] == sorted(tuple(map(int, e)) for e in expected_sinks)
                assert len(row['gates']) == (7 if len(p) == 1 else 5)
                assert row['depth'] == 2
                direct_runs += check_all_real_orders(prefix, p, row)
                contacts[name] = dict(input=text, **row)
        refutations = []
        if case in (3, 4):
            T, C = ((2, 3, 6, 7), (4, 5, 8)) if case == 3 else ((2, 3, 5, 7), (4, 6, 8))
            predicted = []
            for row_index, partner in enumerate(T[1:]):
                rest = tuple(v for v in T if v not in (2, partner))
                for col, optional in enumerate([None, *itertools.combinations(C, 2)]):
                    layer = tuple(sorted(((0, 1), (2, partner), rest) + (() if optional is None else (optional,))))
                    predicted.append(layer)
                    name = CONTACT_TABLES[case][row_index][col]
                    contact = contacts[name]
                    real = set(contact['real'])
                    touched = {v for a, b in layer if a in real and b in real for v in (a, b)}
                    untouched = [e for e in contact['sinks'] if not set(e) & touched]
                    assert untouched
                    refutations.append(dict(fourth=layer, contact=name, untouched_sinks=untouched))
            assert set(survivors) == set(predicted)
        if case == 5:
            assert survivors == [((0, 1), (2, 3), (4, 5), (7, 8))]
            layer = survivors[0]
            contact = contacts['E']
            real = set(contact['real'])
            touched = {v for a, b in layer if a in real and b in real for v in (a, b)}
            assert not {3, 6} & touched
            refutations.append(dict(fourth=layer, contact='E', untouched_sinks=[(3, 6)]))
        results.append(dict(case=case, third=third, five_real_rows=row_traces,
                            five_real_survivors=len(survivors), prices=price_record,
                            contacts=contacts, fourth_refutations=refutations))
    report = dict(status='VERIFIED', second=SECOND, third_count=len(thirds),
                  orbit_sizes=orbit_sizes, all_matching_count=len(layers),
                  direct_real_order_runs=direct_runs, cases=results,
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    target = Path(__file__).parents[1] / 'results/h9-feedback-next-078.json'
    target.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: value for key, value in report.items() if key != 'cases'}, indent=2))


if __name__ == '__main__':
    main()
