#!/usr/bin/env python3
"""Independent trace/classification audit for the 03 12 46 hand proof.

No SAT, no exploratory-module imports. Full matching enumeration below
cross-checks conclusions already derived in the accompanying hand notes.
The two nontrivial partner tables also have separate small branch checkers.
"""
import hashlib
import itertools
import json
import time
from pathlib import Path

ROOT = Path(__file__).parents[1]
FIRST = ((0, 1), (2, 3), (4, 5))
SECOND = ((0, 3), (1, 2), (4, 6))
THIRD = ((0, 1), (2, 3), (5, 6), (7, 8))
PREFIX = (FIRST, SECOND, THIRD)
A, B, F, I = {0, 1}, {2, 3}, {5, 6}, {7, 8}
C, V, H = F | I, set(range(9)), 4
FOURTHS = (
    ((1, 7), (2, 4), (3, 6), (5, 8)),
    ((1, 7), (2, 6), (3, 4), (5, 8)),
    ((1, 8), (2, 4), (3, 6), (5, 7)),
    ((1, 8), (2, 6), (3, 4), (5, 7)),
)
CONTACTS = {
    1: [('+0 +1 +2 -4', '01358', '58'), ('+0 -1 -2 -4', '34578', '58'),
        ('+0 +1 +2 +7', '01235', '35'), ('+0 -1 -4 +7', '13457', '35'),
        ('+0 +2 +4 +5', '01257', '17'), ('-0 -2 +4 +5', '23457', '57'),
        ('-0 -2 +4 +5', '23457', '24'), ('-0 -2 -4 -5', '34678', '78'),
        ('-0 -2 -4 -5', '34678', '36'), ('+0 +2 +4 -7', '02578', '58')],
    3: [('+0 +1 +2 -4', '01357', '57'), ('+0 -1 -2 -4', '34578', '57'),
        ('+0 -1 -4 -5', '13478', '18'), ('+0 -1 -4 +7', '13457', '14'),
        ('+0 +2 +4 +5', '01258', '18'), ('+0 +2 -4 -5', '01378', '18'),
        ('-0 -2 -4 -5', '34678', '78'), ('-0 -2 -4 -5', '34678', '36'),
        ('-0 -2 +4 -7', '23478', '24'), ('+0 -4 -5 +7', '01347', '01')],
}


def place(text):
    return {int(token[1:]): 1 if token[0] == '+' else -1 for token in text.split()}


def normalize(layer):
    return tuple(sorted(tuple(sorted(edge)) for edge in layer))


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
    return tuple(values)


def trace(prefix, p):
    signs = [p.get(i, 0) for i in range(9)]
    identities = list(range(9))
    gates = []
    for layer in prefix:
        for a, b in layer:
            if signs[a] == signs[b] == 0:
                gates.append((identities[a], identities[b]))
            elif signs[a] > signs[b]:
                signs[a], signs[b] = signs[b], signs[a]
                identities[a], identities[b] = identities[b], identities[a]
    positions = {label: wire for wire, label in enumerate(identities)}
    boundary = [(positions[a], positions[b]) for a, b in gates]
    last, depths = [-1] * 9, [0] * 9
    for j, (a, b) in enumerate(boundary):
        last[a] = last[b] = j
        depths[a] = depths[b] = 1 + max(depths[a], depths[b])
    sinks = sorted(tuple(sorted((a, b))) for j, (a, b) in enumerate(boundary)
                   if last[a] == last[b] == j)
    return dict(placement=p, signs=signs, identities=identities, gates=gates,
                boundary_gates=boundary, height=max(depths), depths=depths,
                real=[i for i, sign in enumerate(signs) if not sign], sinks=sinks)


def direct_orders(prefix, p, row):
    real_inputs = [i for i in range(9) if i not in p]
    count = 0
    for ordering in itertools.permutations(range(len(real_inputs))):
        values = [100 * p.get(i, 0) for i in range(9)]
        for wire, value in zip(real_inputs, ordering):
            values[wire] = value
        reduced = list(values)
        for a, b in row['gates']:
            if reduced[a] > reduced[b]:
                reduced[a], reduced[b] = reduced[b], reduced[a]
        assert run(prefix, values) == tuple(reduced[label] for label in row['identities'])
        count += 1
    return count


def rr(layer, real):
    return [(a, b) for a, b in layer if a in real and b in real]


def active(edges):
    return {v for edge in edges for v in edge}


def passes_BFK(layer):
    forbidden = {tuple(sorted((a, b))) for a in A for b in B} | {(4, 5), (4, 6)}
    if set(layer) & forbidden:
        return False
    if any(len(rr(layer, side | C)) < 2 for side in (A, B)):
        return False
    for side in (A, B):
        edges = rr(layer, V - side)
        vertices = active(edges)
        if len(edges) <= 2 and not (H in vertices or F <= vertices):
            return False
    for side, other in ((A, B), (B, A)):
        for s in side:
            edges = rr(layer, V - {H, s})
            vertices = active(edges)
            if len(edges) <= 2 and not (side - {s} <= vertices or other <= vertices):
                return False
    return True


def residual(clause, chosen):
    assert not clause & chosen
    used = active(chosen)
    return {edge for edge in clause if not set(edge) & used}


def main():
    start = time.perf_counter()
    all_layers = list(matchings(list(range(9))))
    assert len(all_layers) == 2620
    binary = list(itertools.product((0, 1), repeat=9))
    prefix2 = (FIRST, SECOND)
    expected2 = {x for x in binary if all(x[a] <= x[b] for a in A for b in B)
                 and all(x[H] <= x[f] for f in F)}
    assert {run(prefix2, x) for x in binary} == expected2
    for bits in itertools.product((False, True), repeat=4):
        permutation = list(range(9))
        for flip, (a, b) in zip(bits, ((0, 1), (2, 3), (5, 6), (7, 8))):
            if flip:
                permutation[a], permutation[b] = permutation[b], permutation[a]
        assert {tuple(x[permutation[i]] for i in range(9)) for x in expected2} == expected2

    direct_count = 0
    basic_traces = []
    for text, sentinel_set, count, deep in (
        ('+0 +2 -4', {2, 3, 4}, 0, set()),
        ('-0 -2 -4', {0, 1, 4}, 0, set()),
        ('-0 -2', {0, 1}, 2, {4, 6}),
        ('+0 +2', {2, 3}, 2, {4, 6}),
        ('-0 -4', {0, 4}, 2, {1, 2}),
        ('+0 -4', {2, 4}, 2, {0, 3}),
    ):
        p = place(text)
        row = trace(prefix2, p)
        assert V - set(row['real']) == sentinel_set
        assert len(row['gates']) == count
        assert {i for i, d in enumerate(row['depths']) if d == 2} == deep
        direct_count += direct_orders(prefix2, p, row)
        basic_traces.append(dict(input=text, **row))

    desired = {normalize(((0, 1), (2, 3)) + k) for k in matchings(sorted(C)) if len(k) == 2}
    exceptions = {((0, 1), (2, 3), (5, 6))}
    for i in I:
        for e in itertools.combinations(sorted(C - {i}), 2):
            exceptions.add(normalize(((0, 1), (2, 3), (H, i), e)))
    for targets in itertools.permutations(sorted(I)):
        exceptions.add(normalize(((0, 1), (5, 6), (2, targets[0]), (3, targets[1]))))
        exceptions.add(normalize(((2, 3), (5, 6), (0, targets[0]), (1, targets[1]))))
    surviving = {layer for layer in all_layers if passes_BFK(layer)}
    assert surviving == desired | exceptions
    assert len(desired) == 3 and len(exceptions) == 11
    exceptional_traces = []
    for layer in sorted(exceptions):
        if H in active(layer):
            family, texts, expected_sentinels = 'X', ('+0 +2 -4', '+0 -1 -4'), ('234', '034')
        elif (0, 1) in layer and (2, 3) in layer:
            family, texts, expected_sentinels = 'Y', ('+0 +2 +4', '+0 +2 -4'), ('236', '234')
        elif (0, 1) in layer:
            family, texts, expected_sentinels = 'ZA', ('+0 +2 +4', '+0 +2 -4'), ('678', '478')
        else:
            family, texts, expected_sentinels = 'ZB', ('-0 -2 +4', '-0 -2 -4'), ('016', '014')
        traces = []
        for text, expected in zip(texts, expected_sentinels):
            p = place(text)
            row = trace(prefix2 + (layer,), p)
            assert len(row['gates']) == 2 and row['height'] == 1
            assert V - set(row['real']) == set(map(int, expected))
            direct_count += direct_orders(prefix2 + (layer,), p, row)
            traces.append(dict(input=text, **row))
        assert len(set(traces[0]['real']) & set(traces[1]['real'])) == 5
        exceptional_traces.append(dict(family=family, third=layer, traces=traces))

    crossed = ((0, 1), (2, 3), (5, 7), (6, 8))
    cross_rows = []
    for text, expected in (('+0 +2 +4 +5', '01456'), ('-0 -2 +4 +5', '23456')):
        p = place(text)
        row = trace(prefix2 + (crossed,), p)
        assert len(row['gates']) == 1 and row['real'] == list(map(int, expected))
        direct_count += direct_orders(prefix2 + (crossed,), p, row)
        cross_rows.append(dict(input=text, **row))
    cross_prices = [int(i in {4, 5, 6}) for i in range(9)]
    for a, b in itertools.combinations(range(9), 2):
        if (a, b) not in {(0, 1), (2, 3)}:
            weight = sum(a in row['real'] and b in row['real'] for row in cross_rows)
            assert weight <= cross_prices[a] + cross_prices[b]
    assert sum(cross_prices) == 3 < 4

    blocks = (set(range(4)), {4, 5, 6}, {7, 8})
    expected3 = {x for x in binary if all(x[a] <= x[b] for block in blocks
                                        for a, b in itertools.combinations(sorted(block), 2))}
    assert {run(PREFIX, x) for x in binary} == expected3
    forbidden_N = {edge for block in blocks for edge in itertools.combinations(sorted(block), 2)}
    interval_sets = [{i, i + 1, j, j + 1, 7, 8} for i in range(3) for j in (4, 5)]
    merger_starts = {layer for layer in all_layers if not set(layer) & forbidden_N
                     and all(len(rr(layer, real)) >= 2 for real in interval_sets)}
    predicted = set()
    for a, opposites in ((1, (2, 3)), (2, (0, 1))):
        for x4, x6 in itertools.permutations(opposites):
            for c, d in ((7, 8), (8, 7)):
                predicted.add(normalize(((a, c), (5, d), (4, x4), (6, x6))))
    assert merger_starts == predicted and len(predicted) == 8
    rho = (3, 2, 1, 0, 6, 5, 4, 8, 7)
    dual = lambda layer: normalize((rho[a], rho[b]) for a, b in layer)
    assert merger_starts == set(FOURTHS) | {dual(layer) for layer in FOURTHS}

    for case, c, d in ((2, 8, 7), (4, 7, 8)):
        CONTACTS[case] = [
            ('+0 +1 +2 +4', ''.join(map(str, sorted({0, 1, 3, 5, c}))), f'5{c}'),
            ('+0 +1 +2 -4', ''.join(map(str, sorted({0, 1, 2, 5, c}))), f'5{c}'),
            ('+0 -1 -2 +4', ''.join(map(str, sorted({2, 3, 5, c, d}))), f'5{c}'),
            ('-0 -1 -2 -4', ''.join(map(str, sorted({4, 5, 6, c, d}))), f'5{c}'),
            ('-0 -2 +4 +5', ''.join(map(str, sorted({2, 3, 4, 5, d}))), f'5{d}'),
            ('-0 -2 -4 -5', ''.join(map(str, sorted({2, 4, 6, c, d}))), '78'),
        ]
    source = ROOT / 'results/h9-feedback-round2-contacts.json'
    discovery_data = json.loads(source.read_text())
    merger_cases = []
    for case, fourth in enumerate(FOURTHS, 1):
        traces, clauses = [], []
        for index, (text, expected_real, expected_sink) in enumerate(CONTACTS[case], 1):
            p = place(text)
            row = trace(PREFIX + (fourth,), p)
            real, sink = set(map(int, expected_real)), tuple(sorted(map(int, expected_sink)))
            assert row['real'] == sorted(real)
            assert len(row['gates']) == 3 and row['height'] <= 3 and sink in row['sinks']
            direct_count += direct_orders(PREFIX + (fourth,), p, row)
            if case in (1, 3):
                reference = discovery_data[case - 1]['core'][index - 1]
                assert sorted(reference['real']) == sorted(real) and sorted(reference['sink']) == list(sink)
                assert {int(k): v for k, v in reference['placement'].items()} == p
            clauses.append({edge for edge in itertools.combinations(sorted(real), 2)
                            if set(edge) & set(sink) and edge not in fourth})
            traces.append(dict(input=text, required_sink=sink, **row))
        passing = [layer for layer in all_layers if not set(layer) & set(fourth)
                   and all(set(layer) & clause for clause in clauses)]
        assert not passing
        uniform_partner_sets = None
        if case in (2, 4):
            c, d = (8, 7) if case == 2 else (7, 8)
            triples = ({0, 1, 3}, {0, 1, 2}, {2, 3, d}, {4, 6, d})
            assert not set.intersection(*triples)
            hitting = {pair for pair in itertools.combinations(sorted(V - {5, c}), 2)
                       if all(set(pair) & triple for triple in triples)}
            assert hitting == {tuple(sorted((0, d))), tuple(sorted((1, d)))}
            for a in (0, 1):
                assert not residual(clauses[4], set(normalize(((5, a), (c, d)))))
                assert not residual(clauses[5], set(normalize(((5, d), (c, a)))))
            uniform_partner_sets = sorted(hitting)
        merger_cases.append(dict(case=case, fourth=fourth, contacts=traces,
                                 contact_count=len(clauses), matching_crosscheck_survivors=len(passing),
                                 uniform_partner_sets=uniform_partner_sets))

    dependencies = ['h9_round2_case1_branch_check.py', 'h9_root_helper_case3.py']
    report = dict(status='VERIFIED', second=SECOND, matching_count=len(all_layers),
                  BFK_survivors=len(surviving), exceptional_count=len(exceptions),
                  final_third_count=len(desired), merger_first_layer_count=len(merger_starts),
                  normalized_merger_cases=4, contact_rows=sum(len(x) for x in CONTACTS.values()),
                  direct_real_order_runs=direct_count, basic_traces=basic_traces,
                  exceptional_traces=exceptional_traces, crossed_third_traces=cross_rows,
                  merger_cases=merger_cases, elapsed_seconds=time.perf_counter() - start,
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  contact_data_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  branch_checker_sha256={name: hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest()
                                         for name in dependencies},
                  proof_scope='One new H9 second-layer class and the standalone four-three-two merging lower bound; scans only cross-check hand classifications')
    (ROOT / 'results/h9-feedback-round2-proof.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in
                      ('basic_traces', 'exceptional_traces', 'crossed_third_traces', 'merger_cases')}, indent=2))


if __name__ == '__main__':
    main()
