#!/usr/bin/env python3
"""Check the fixed 02 16 37 hand certificates, without a solver.

Rank verification evaluates only the fourteen printed real inputs.
Matching scans below corroborate the hand classifications; they are not
used to discover a suffix or to establish any endpoint exclusion.
"""
import hashlib
import itertools
import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
FIRST = ((0, 1), (2, 3), (4, 5))
SECOND = ((0, 2), (1, 6), (3, 7))
K = (((1, 2), (3, 4), (5, 8)), ((1, 2), (3, 5), (4, 8)),
     ((1, 3), (2, 4), (5, 8)), ((1, 3), (2, 5), (4, 8)),
     ((1, 4), (2, 5), (3, 8)), ((1, 4), (2, 8), (3, 5)),
     ((1, 5), (2, 4), (3, 8)))
TAU = (0, 3, 2, 1, 4, 5, 7, 6, 8)
PLANS = {
    (2, 1): ('isolated', [(0, [])]), (2, 2): ('isolated', [(0, [])]),
    (4, 1): ('forced', [(0, [3]), (1, [4]), (5, [2]), (6, [8])]),
    (6, 1): ('forced', [(8, [7]), (6, [2]), (3, [4]), (1, [5])]),
    (6, 2): ('isolated', [(5, [])]), (6, 3): ('isolated', [(5, [])]),
    (6, 4): ('hall', [(3, [2, 4]), (5, [2, 4]), (8, [2, 4])]),
    (8, 1): ('isolated', [(8, [])]), (8, 2): ('isolated', [(8, [])]),
    (8, 3): ('isolated', [(8, [])]),
    (10, 1): ('isolated', [(1, [])]), (10, 2): ('isolated', [(1, [])]),
    (14, 1): ('isolated', [(8, [])]), (14, 2): ('isolated', [(8, [])]),
}


def layer(text):
    return tuple(sorted(tuple(map(int, word)) for word in text.split()))


EXPECTED_N = {
    2: [layer('01 26 45'), layer('01 26 45 78')],
    4: [layer('01 26 34 58')],
    6: [layer('01 23 48 56'), layer('01 25 36 48'), layer('01 26 35 48'), layer('02 18 35 46')],
    8: [layer('01 28 36'), layer('01 28 36 57'), layer('01 28 36 47')],
    10: [layer('03 24 68'), layer('03 24 57 68')],
    14: [layer('02 18 35 46'), layer('03 12 45 68')],
}


def normalized(edges):
    return tuple(sorted(tuple(sorted(edge)) for edge in edges))


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
    for gates in prefix:
        for a, b in gates:
            if values[a] > values[b]:
                values[a], values[b] = values[b], values[a]
    return tuple(values)


def trace(prefix, placement):
    p = {int(i): s for i, s in placement.items()}
    signs = [p.get(i, 0) for i in range(9)]
    labels = list(range(9))
    gates = []
    for gates_in_layer in prefix:
        for a, b in gates_in_layer:
            if signs[a] == signs[b] == 0:
                gates.append((labels[a], labels[b]))
            elif signs[a] > signs[b]:
                signs[a], signs[b] = signs[b], signs[a]
                labels[a], labels[b] = labels[b], labels[a]
    position = {v: i for i, v in enumerate(labels)}
    boundary = [(position[a], position[b]) for a, b in gates]
    depths, last = [0] * 9, [-1] * 9
    for j, (a, b) in enumerate(boundary):
        depths[a] = depths[b] = 1 + max(depths[a], depths[b])
        last[a] = last[b] = j
    sinks = sorted(tuple(sorted((a, b))) for j, (a, b) in enumerate(boundary)
                   if last[a] == last[b] == j)
    return dict(placement=p, signs=signs, labels=labels, gates=gates, boundary=boundary,
                real=[i for i, s in enumerate(signs) if not s], height=max(depths), sinks=sinks)


def direct_orders(prefix, row):
    p = row['placement']
    real = [i for i in range(9) if i not in p]
    count = 0
    for ranks in itertools.permutations(range(len(real))):
        values = [100 * p.get(i, 0) for i in range(9)]
        for i, value in zip(real, ranks):
            values[i] = value
        reduced = list(values)
        for a, b in row['gates']:
            if reduced[a] > reduced[b]:
                reduced[a], reduced[b] = reduced[b], reduced[a]
        assert run(prefix, values) == tuple(reduced[i] for i in row['labels'])
        count += 1
    return count


def propagated_order(prefix):
    relation = {(i, i) for i in range(9)}
    for gates in prefix:
        for a, b in gates:
            old = set(relation)
            relation = {(u, v) for u, v in old if u not in (a, b) and v not in (a, b)}
            relation |= {(a, a), (b, b), (a, b)}
            for v in set(range(9)) - {a, b}:
                if (a, v) in old or (b, v) in old:
                    relation.add((a, v))
                if (a, v) in old and (b, v) in old:
                    relation.add((b, v))
                if (v, a) in old or (v, b) in old:
                    relation.add((v, b))
                if (v, a) in old and (v, b) in old:
                    relation.add((v, a))
    return {(a, b) for a, b in relation if a < b}


def rr(gates, real):
    return [edge for edge in gates if set(edge) <= set(real)]


def verify_printed_tables(data, text):
    def edge_text(edges):
        return ' '.join(''.join(map(str, e)) for e in edges)

    def placement_text(p):
        return ' '.join(('+' if sign > 0 else '-') + str(i)
                        for i, sign in sorted((int(i), sign) for i, sign in p.items()))

    def real_text(row):
        return ''.join(map(str, row['real']))

    input_rows = re.findall(r'^\| ([A-Z]) \| `([0-8]{9})` \|$', text, flags=re.M)
    assert [tuple(map(int, values)) for _, values in input_rows] == list(map(tuple, data['rank_inputs']))
    printed = set()
    section = None
    for line in text.splitlines():
        heading = re.fullmatch(r'### (\d+)\.(\d+)', line)
        if heading:
            section = tuple(map(int, heading.groups()))
        row = re.fullmatch(r'\| (\d) \| ([\d,idle]+) \| (idle|min|max) \| ([A-Z]):(\d) \| ([A-Z]):(\d) \|', line)
        if row:
            assert section is not None
            pivot, partners, operation, low, lo, high, hi = row.groups()
            for partner in partners.split(','):
                printed.add((*section, int(pivot), None if partner == 'idle' else int(partner), operation,
                             ord(low) - 65, int(lo), ord(high) - 65, int(hi)))
    expected = {(r['case'], r['number'], r['pivot'], r['partner'], r['output'],
                 r['low_input'], r['low'], r['high_input'], r['high']) for r in data['rank_rows']}
    assert printed == expected
    for group in data['direct_cases']:
        for row in group['rows']:
            line = f"| {group['case']} | `{placement_text(row['placement'])}` | {real_text(row)} |"
            assert line in text
        if group['kind'] == 'strict_price':
            line = f"| {group['case']} | `{','.join(map(str,group['twice_prices']))}` | {group['twice_gate_price']} | {group['twice_budget']} | {4*len(group['rows'])} |"
            assert line in text
    for case in data['cases']:
        line = f"| {case['case']} | `{' '.join(''.join(map(str,e)) for e in case['third'])}` | `{' '.join(''.join(map(str,e)) for e in case['forbidden'])}` |"
        assert line in text
    for group in data['fourth_reductions']:
        for row in group['rows']:
            line = f"| {group['case']} | `{placement_text(row['placement'])}` | {real_text(row)} | {row['demand']} |"
            assert line in text
        for row in group['contacts']:
            line = f"| {group['case']} | `{placement_text(row['placement'])}` | {real_text(row)} | `{edge_text(row['sinks'])}` |"
            assert line in text
        for number, fourth in enumerate(group['fourths'], 1):
            assert f"| {group['case']}.{number} | `{edge_text(fourth)}` |" in text
    for group in data['rank_cases']:
        if group['kind'] == 'isolated':
            description = f"wire{group['plan'][0][0]} must be used but has no partner"
        elif group['kind'] == 'hall':
            description = 'required wires3,5,8 can only meet2,4'
        else:
            description = 'force ' + ', then '.join(f'{p}{a[0]}' for p, a in group['plan'])
        assert f"| {group['case']}.{group['number']} | {description} |" in text
    for row in data['final_contacts']:
        line = (f"| {row['case']}.{row['number']} | `{edge_text(row['fifth'])}` | "
                f"`{placement_text(row['placement'])}` | {real_text(row)} | {''.join(map(str, row['sink']))} |")
        assert line in text


def main():
    cert_path = ROOT / 'results/h9-feedback-round4-certificate.json'
    tables_path = ROOT / 'h9_feedback_round4_tables.md'
    data = json.loads(cert_path.read_text())
    verify_printed_tables(data, tables_path.read_text())
    all_layers = list(matchings(list(range(9))))
    assert len(all_layers) == 2620
    prefix2 = (FIRST, SECOND)
    direct_count = 0
    basic = []
    for p, sentinels in (({0: 1, 2: 1}, {6, 7}), ({0: 1, 2: -1}, {0, 6}),
                         ({0: -1, 2: 1}, {0, 7})):
        row = trace(prefix2, p)
        assert set(range(9)) - set(row['real']) == sentinels
        assert len(row['gates']) == 2 and row['height'] == 1
        direct_count += direct_orders(prefix2, row)
        basic.append(row)
    all_K = {m for m in matchings([1, 2, 3, 4, 5, 8]) if len(m) == 3 and (4, 5) not in m}
    assert len(all_K) == 12
    canonical = lambda m: min(m, normalized((TAU[a], TAU[b]) for a, b in m))
    assert {canonical(m) for m in all_K} == set(K)
    expected_M = all_K | {normalized(m + ((6, 7),)) for m in all_K}
    ordered2 = propagated_order(prefix2)
    permitted_M = {m for m in all_layers if not set(m) & ordered2 and all(
        len(rr(m, set(range(9)) - deletion)) >= 3 for deletion in ({0, 6}, {0, 7}, {6, 7}))}
    assert permitted_M == expected_M
    binary = list(itertools.product((0, 1), repeat=9))
    image2 = {run(prefix2, x) for x in binary}
    assert {tuple(x[TAU[i]] for i in range(9)) for x in image2} == image2

    cases = {}
    for record in data['cases']:
        number = record['case']
        third = normalized(record['third'])
        assert third == normalized(K[(number - 1) // 2] + (((6, 7),) if number % 2 == 0 else ()))
        forbidden = propagated_order(prefix2 + (third,))
        if number % 2 == 0:
            forbidden.update(((1, 7), (2, 7), (3, 7)))
        assert set(map(tuple, record['forbidden'])) == forbidden
        assert all(x[a] <= x[b] for x in (run(prefix2 + (third,), bits) for bits in binary)
                   for a, b in forbidden)
        cases[number] = dict(third=third, forbidden=forbidden)
    direct_audit = []
    for group in data['direct_cases']:
        case = group['case']
        prefix = prefix2 + (cases[case]['third'],)
        sets, traces = [], []
        for record in group['rows']:
            row = trace(prefix, record['placement'])
            assert len(row['gates']) == 1 and row['real'] == record['real']
            direct_count += direct_orders(prefix, row)
            sets.append(set(record['real']))
            traces.append(row)
        if group['kind'] == 'strict_price':
            prices, gate = group['twice_prices'], group['twice_gate_price']
            for a, b in itertools.combinations(range(9), 2):
                if (a, b) not in cases[case]['forbidden']:
                    weight = sum({a, b} <= real for real in sets)
                    assert 2 * weight <= prices[a] + prices[b] + gate
            assert sum(prices) + 4 * gate == group['twice_budget'] < 4 * len(sets)
        elif group['kind'] == 'odd_common_triple':
            assert {frozenset(s) for s in sets} == {frozenset({3, 4, 5, a, b}) for a in (2, 8) for b in (6, 7)}
        elif group['kind'] == 'two_odd_triples':
            assert {frozenset(s) for s in sets} == {frozenset({8, a} | block) for a in (3, 7)
                                                   for block in ({0, 1, 2}, {4, 5, 6})}
        else:
            raise AssertionError(group['kind'])
        # Corroboration of the printed arithmetic/parity contradiction.
        assert not any(not set(m) & cases[case]['forbidden'] and all(len(rr(m, real)) >= 2 for real in sets)
                       for m in all_layers)
        direct_audit.append(dict(case=case, kind=group['kind'], traces=traces))
    assert {g['case'] for g in data['direct_cases']} == {1, 3, 5, 7, 9, 11, 12, 13}

    reduction_audit = []
    for group in data['fourth_reductions']:
        case = group['case']
        prefix = prefix2 + (cases[case]['third'],)
        demands, contacts, traces = [], [], []
        for record in group['rows']:
            row = trace(prefix, record['placement'])
            assert row['real'] == record['real']
            assert len(row['gates']) in (1, 2) and record['demand'] == 3 - len(row['gates'])
            direct_count += direct_orders(prefix, row)
            demands.append((set(row['real']), record['demand']))
            traces.append(row)
        for record in group['contacts']:
            row = trace(prefix, record['placement'])
            assert len(row['gates']) == 5 and row['height'] == 2
            assert row['real'] == record['real'] and row['sinks'] == list(map(tuple, record['sinks']))
            direct_count += direct_orders(prefix, row)
            contacts.append(row)
        def permitted(n):
            if set(n) & cases[case]['forbidden'] or any(len(rr(n, real)) < demand for real, demand in demands):
                return False
            for contact in contacts:
                touched = {v for edge in rr(n, contact['real']) for v in edge}
                if any(not set(sink) & touched for sink in contact['sinks']):
                    return False
            return True
        passing = {n for n in all_layers if permitted(n)}
        assert passing == set(EXPECTED_N[case])
        assert [normalized(n) for n in group['fourths']] == EXPECTED_N[case]
        reduction_audit.append(dict(case=case, fourth_count=len(passing), traces=traces, contacts=contacts))
    assert {g['case'] for g in data['fourth_reductions']} == set(EXPECTED_N)

    inputs = list(map(tuple, data['rank_inputs']))
    assert len(inputs) == 14 and all(sorted(x) == list(range(9)) for x in inputs)
    records = {(r['case'], r['number']): r for r in data['rank_cases']}
    assert set(records) == set(PLANS)
    output_cache, expected_actions, forced_fifths = {}, set(), {}
    for key, (kind, plan) in PLANS.items():
        case, number = key
        record = records[key]
        assert record['kind'] == kind and record['plan'] == [[p, a] for p, a in plan]
        assert normalized(record['third']) == cases[case]['third']
        fourth = EXPECTED_N[case][number - 1]
        assert normalized(record['fourth']) == fourth
        prefix = prefix2 + (cases[case]['third'], fourth)
        output_cache[key] = [run(prefix, values) for values in inputs]
        used, forced = set(), []
        for pivot, allowed in plan:
            assert pivot not in used
            expected_actions.add((*key, pivot, None))
            for partner in set(range(9)) - used - {pivot} - set(allowed):
                expected_actions.add((*key, pivot, partner))
            if kind == 'forced':
                assert len(allowed) == 1 and allowed[0] not in used and allowed[0] != pivot
                forced.append(tuple(sorted((pivot, allowed[0]))))
                used.update((pivot, allowed[0]))
        if kind == 'forced':
            forced_fifths[key] = normalized(forced)
        elif kind == 'hall':
            pivots = {p for p, _ in plan}
            neighbors = set().union(*(set(a) for _, a in plan))
            assert not pivots & neighbors and len(pivots) > len(neighbors)
        else:
            assert len(plan) == 1 and not plan[0][1]
    actual_actions = set()
    for row in data['rank_rows']:
        key = (row['case'], row['number'])
        pivot, partner, operation = row['pivot'], row['partner'], row['output']
        actual_actions.add((*key, pivot, partner))
        assert (partner is None) == (operation == 'idle')
        for tag in ('low', 'high'):
            values = output_cache[key][row[f'{tag}_input']]
            value = values[pivot] if operation == 'idle' else min(values[pivot], values[partner]) if operation == 'min' else max(values[pivot], values[partner])
            assert value == row[tag]
        assert row['high'] - row['low'] >= 4
    assert len(actual_actions) == len(data['rank_rows']) == 160
    assert actual_actions == expected_actions
    final_audit = []
    for record in data['final_contacts']:
        key = (record['case'], record['number'])
        case, number = key
        fifth = normalized(record['fifth'])
        assert fifth == forced_fifths[key]
        prefix = prefix2 + (cases[case]['third'], EXPECTED_N[case][number - 1])
        row = trace(prefix, record['placement'])
        assert len(row['gates']) == 3 and row['real'] == record['real']
        assert tuple(record['sink']) in row['sinks']
        touched = {v for edge in rr(fifth, row['real']) for v in edge}
        assert not set(record['sink']) & touched
        direct_count += direct_orders(prefix, row)
        final_audit.append(dict(case=case, number=number, fifth=fifth, trace=row))
    assert {(r['case'], r['number']) for r in data['final_contacts']} == set(forced_fifths)

    report = dict(status='VERIFIED', solver_free=True, closed_second_layer=SECOND,
                  third_matchings=24, canonical_third_cases=14, direct_price_or_parity_cases=8,
                  fourth_layer_forms=14, rank_input_bank=14, rank_input_runs=14 * 14,
                  endpoint_exclusions=160, isolated_rank_cases=11, hall_rank_cases=1,
                  forced_rank_cases=2, final_sink_contacts=2, direct_real_order_runs=direct_count,
                  first_two_traces=basic, direct_audit=direct_audit, fourth_reductions=reduction_audit,
                  final_audit=final_audit,
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  certificate_sha256=hashlib.sha256(cert_path.read_bytes()).hexdigest(),
                  tables_sha256=hashlib.sha256(tables_path.read_bytes()).hexdigest(),
                  main_proof_sha256=hashlib.sha256((ROOT / 'h9_feedback_round4_021637.md').read_bytes()).hexdigest())
    (ROOT / 'results/h9-feedback-round4-proof.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in
                      ('first_two_traces', 'direct_audit', 'fourth_reductions', 'final_audit')}, indent=2))


if __name__ == '__main__':
    main()
