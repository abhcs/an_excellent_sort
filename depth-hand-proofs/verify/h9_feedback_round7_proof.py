#!/usr/bin/env python3
"""Independently replay fixed H9 03 16 57 hand premises.

No solver, discovery imports, all-nine-wire matching scan, or rank-input
search. Fourth-layer coverage uses only explicit five-wire base cases
and one-edge clause intersections on at most three remaining vertices.
"""
import hashlib
import itertools
import json
import time
from pathlib import Path

ROOT = Path(__file__).parents[1]
FIRST = ((0, 1), (2, 3), (4, 5))
SECOND = ((0, 3), (1, 6), (5, 7))
CERTIFICATE_SHA256 = 'd9237f438467d95088717b2016cc8734453ea62f4540f3ecbe48994a9cc6ca60'
EXPECTED_M = ('01 24 36 58', '01 28 36 45', '04 12 36 58',
              '04 15 28 36', '08 12 36 45', '08 14 25 36')


def normalize(edges):
    return tuple(sorted(tuple(sorted(e)) for e in edges))


def es(edges):
    return ' '.join(''.join(map(str, e)) for e in edges) or 'none'


def ps(p):
    return ' '.join(('+' if sign > 0 else '-') + str(i)
                    for i, sign in sorted((int(i), s) for i, s in p.items()))


def run(prefix, values):
    result = list(values)
    for layer in prefix:
        for a, b in layer:
            result[a], result[b] = min(result[a], result[b]), max(result[a], result[b])
    return tuple(result)


def trace(prefix, placement):
    placement = {int(i): s for i, s in placement.items()}
    signs = [placement.get(i, 0) for i in range(9)]
    tracks = list(range(9))
    gates = []
    for layer in prefix:
        for a, b in layer:
            if signs[a] == signs[b] == 0:
                gates.append((tracks[a], tracks[b]))
            elif signs[a] > signs[b]:
                signs[a], signs[b] = signs[b], signs[a]
                tracks[a], tracks[b] = tracks[b], tracks[a]
    positions = {v: i for i, v in enumerate(tracks)}
    boundary = [(positions[a], positions[b]) for a, b in gates]
    height = [0] * 9
    for a, b in boundary:
        height[a] = height[b] = max(height[a], height[b]) + 1
    return dict(placement=placement, signs=signs, tracks=tracks, gates=gates,
                boundary=boundary, height=max(height), real=[i for i, s in enumerate(signs) if not s])


def direct_orders(prefix, row):
    p = row['placement']
    real = sorted(set(range(9)) - set(p))
    count = 0
    for ranks in itertools.permutations(range(len(real))):
        values = [100 * p.get(i, 0) for i in range(9)]
        for i, value in zip(real, ranks):
            values[i] = value
        retained = run((row['gates'],), values)
        assert run(prefix, values) == tuple(retained[i] for i in row['tracks'])
        count += 1
    return count


def propagated_order(prefix):
    # Each update is a min/max inequality implication; no input enumeration.
    relation = {(i, i) for i in range(9)}
    for layer in prefix:
        for a, b in layer:
            old = relation
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


def two_edge_bases(real, forbidden):
    """The explicit five-vertex recipe: choose idle, then one of three pairings."""
    assert len(real) == 5
    bases = set()
    for idle in real:
        a, b, c, d = sorted(set(real) - {idle})
        for pairs in (((a, b), (c, d)), ((a, c), (b, d)), ((a, d), (b, c))):
            if not set(pairs) & forbidden:
                bases.add(normalize(pairs))
    return bases


def perfect_six(vertices):
    """Fifteen third-layer K choices, using the elementary 5*3 recipe."""
    a = min(vertices)
    for b in sorted(set(vertices) - {a}):
        c, d, e, f = sorted(set(vertices) - {a, b})
        for rest in (((c, d), (e, f)), ((c, e), (d, f)), ((c, f), (d, e))):
            yield normalize(((a, b),) + rest)


def structural_checks(data):
    prefix = (FIRST, SECOND)
    # Exhaustive checks here concern only the 120 orders of one five-wire
    # image and six orders of the separate fork, not network completions.
    core = (0, 1, 2, 3, 6)
    images = set()
    for values in itertools.permutations(range(5)):
        x = [0] * 9
        for i, v in zip(core, values):
            x[i] = v
        images.add(tuple(run(prefix, x)[i] for i in core))
    expected = {x for x in itertools.permutations(range(5))
                if x[0] <= x[3] and x[0] <= x[4] and x[1] <= x[4] and x[2] <= x[3]}
    assert images == expected
    for x in expected:
        inp = [0] * 9
        for i, v in zip(core, (x[0], x[4], x[2], x[3], x[1])):
            inp[i] = v
        assert tuple(run(prefix, inp)[i] for i in core) == x
        assert (x[0], x[2], x[1], x[4], x[3]) in expected
    fork = (4, 5, 7)
    outputs = set()
    for values in itertools.permutations(range(3)):
        x = [0] * 9
        for i, v in zip(fork, values):
            x[i] = v
        outputs.add(tuple(run(prefix, x)[i] for i in fork))
    assert outputs == {(0, 1, 2), (1, 0, 2)}
    specs = [({0: -1, 5: 1}, {0: -1, 7: 1}, ((2, 3), (1, 6))),
             ({0: 1, 2: 1, 5: 1}, {3: 1, 6: 1, 7: 1}, ()),
             ({0: 1, 5: 1}, {6: 1, 7: 1}, ((2, 3), (0, 3))),
             ({0: 1, 2: 1}, {3: 1, 6: 1}, ((4, 5), (5, 7))),
             ({0: 1, 2: 1, 4: -1, 5: -1}, {3: 1, 4: -1, 5: -1, 6: 1}, ()),
             ({0: 1, 2: 1, 4: -1}, {3: 1, 4: -1, 6: 1}, ((5, 7),))]
    runs = 0
    for placement, signs, boundary in specs:
        row = trace(prefix, placement)
        assert row['signs'] == [signs.get(i, 0) for i in range(9)]
        assert tuple(row['boundary']) == boundary
        runs += direct_orders(prefix, row)
    exceptional = ('08 13 26 45', '02 13 45 68', '01 26 38 45')
    for text in exceptional:
        m = tuple(tuple(map(int, edge)) for edge in text.split())
        p = trace(prefix + (m,), {0: 1, 2: 1, 5: 1})
        b = trace(prefix + (m,), {0: 1, 2: 1, 4: -1})
        assert len(p['gates']) == len(b['gates']) == 2
        assert p['height'] == b['height'] == 1
        assert len(set(p['real']) & set(b['real'])) == 5
        assert set(p['real']) - set(b['real']) == {4}
        assert set(b['real']) - set(p['real']) == {7}
        runs += direct_orders(prefix + (m,), p) + direct_orders(prefix + (m,), b)
    forms = set()
    for k in perfect_six((0, 1, 2, 4, 5, 8)):
        orbit = []
        for swap12, swap45 in itertools.product((False, True), repeat=2):
            def perm(v):
                if swap12 and v in (1, 2):
                    return 3 - v
                if swap45 and v in (4, 5):
                    return 9 - v
                return v
            orbit.append(normalize([(3, 6)] + [(perm(a), perm(b)) for a, b in k]))
        forms.add(min(orbit))
    assert {es(m) for m in forms} == set(EXPECTED_M)
    assert [es(m) for m in data['third_forms']] == list(EXPECTED_M)
    return dict(core_orders=120, fork_orders=6, named_restriction_order_runs=runs,
                six_wire_matchings=15, third_layer_orbits=6)


def local_classification(c, table):
    number = c['case']
    forbidden = set(map(tuple, c['forbidden']))
    assert forbidden == propagated_order((FIRST, SECOND, c['third']))
    assert f"| {number} | `{es(c['third'])}` | `{es(c['forbidden'])}` |" in table
    real = c['base_real']
    assert any(r['real'] == real and r['demand'] == 2 for r in c['rows'])
    bases = two_edge_bases(real, forbidden)
    assert len(bases) == 12
    assert {normalize(r['base']) for r in c['branches']} == bases
    assert len(c['branches']) == 12
    assert f"### Case {number}: base set {''.join(map(str,real))}" in table
    all_completions = set()
    arms_checked = 0
    for branch in c['branches']:
        base = normalize(branch['base'])
        free = set(range(9)) - {v for e in base for v in e}
        assert sorted(free) == branch['free'] and len(free) == 5
        allowed = set(itertools.combinations(sorted(free), 2)) - forbidden
        clauses = {}
        for item in branch['clauses']:
            r = c['rows'][item['row'] - 1]
            remaining = r['demand'] - sum(set(e) <= set(r['real']) for e in base)
            edges = {e for e in allowed if set(e) <= set(r['real'])}
            assert remaining == item['need'] and remaining in (1, 2)
            assert edges == set(map(tuple, item['edges']))
            assert item['row'] not in clauses
            clauses[item['row']] = (remaining, edges)
        anchor = clauses[branch['anchor']]
        assert {tuple(a['edge']) for a in branch['arms']} == anchor[1]
        assert len(branch['arms']) == len(anchor[1])
        obtained = set()
        for arm in branch['arms']:
            e = tuple(arm['edge'])
            remaining_vertices = free - set(e)
            available = set(itertools.combinations(sorted(remaining_vertices), 2)) - forbidden
            residual = [(i, need - (e in edges), edges) for i, (need, edges) in clauses.items()]
            pending = [(i, need, edges) for i, need, edges in residual if need > 0]
            need_two = any(need > 1 for _, need, _ in pending)
            assert arm['pending'] == [i for i, _, _ in pending]
            assert arm['impossible_need_two'] == need_two
            assert arm['optional'] == (not pending)
            second = available.copy()
            for _, _, edges in pending:
                second &= edges
            if need_two:
                second.clear()
            assert second == set(map(tuple, arm['seconds']))
            if not pending:
                obtained.add((e,))
            for f in second:
                obtained.add(normalize((e, f)))
            arms_checked += 1
        assert obtained == {normalize(x) for x in branch['completions']}
        for completion in obtained:
            whole = normalize(base + completion)
            assert len({v for e in whole for v in e}) == 2 * len(whole)
            assert all(sum(set(e) <= set(r['real']) for e in whole) >= r['demand'] for r in c['rows'])
            all_completions.add(whole)
        clause_text = '; '.join(f"{x['row']}:{x['need']}({es(x['edges'])})" for x in branch['clauses'])
        arm_text = '; '.join(es([x['edge']]) + '→' + ('optional ' if x['optional'] else '') +
                             ('{' + es(x['seconds']) + '}' if x['seconds'] else ('none' if x['optional'] else '∅'))
                             for x in branch['arms']) or 'empty anchor'
        completions = ' / '.join(es(x) for x in branch['completions']) or 'impossible'
        assert f"| `{es(branch['base'])}` | {clause_text} | {branch['anchor']} | {arm_text} | `{completions}` |" in table
    assert all_completions == {normalize(m) for m in c['fourths']}
    return arms_checked


def endpoints(row, outputs):
    p = row['pivot']
    assert row['low'] == min(x[p] for x in outputs)
    assert row['high'] == max(x[p] for x in outputs)
    assert outputs[row['low_input']][p] == row['low']
    assert outputs[row['high_input']][p] == row['high']


def guard(g, p, low, high, outputs):
    x = outputs[g['input']]
    if g['kind'] == 'low':
        assert x[p] <= high - 4
        excluded = {q for q in range(9) if q != p and x[q] <= high - 4}
    else:
        assert g['kind'] == 'high' and x[p] >= low + 4
        excluded = {q for q in range(9) if q != p and x[q] >= low + 4}
    assert excluded == set(g['excluded'])
    return excluded


def ep(r):
    return f"{chr(65+r['low_input'])}:{r['low']}–{chr(65+r['high_input'])}:{r['high']}"


def gs(g):
    return f"{chr(65+g['input'])} {'lo' if g['kind']=='low' else 'hi'}:{''.join(map(str,g['excluded']))}"


def rank_checks(data, table):
    inputs = data['rank_inputs']
    assert len(inputs) == 19 and len({tuple(x) for x in inputs}) == 19
    for i, x in enumerate(inputs):
        assert sorted(x) == list(range(9))
        assert f"| {chr(65+i)} | `{''.join(map(str,x))}` |" in table
    expected = {(c['case'], i): (c['third'], n)
                for c in data['cases'] for i, n in enumerate(c['fourths'], 1)}
    for row in data['sinks']:
        expected.pop((row['case'], row['number']))
    seen = set()
    own = reciprocal = 0
    for r in data['rank_records']:
        key = (r['case'], r['number'])
        assert key in expected and key not in seen
        seen.add(key)
        m, n = expected[key]
        assert r['third'] == m and r['fourth'] == n
        outputs = [run((FIRST, SECOND, m, n), x) for x in inputs]
        endpoints(r, outputs)
        p = r['pivot']
        assert r['high'] - r['low'] >= 4
        excluded = set()
        for g in r['guards']:
            excluded |= guard(g, p, r['low'], r['high'], outputs)
            own += 1
        remaining = set(range(9)) - {p} - excluded
        assert remaining == set(r['remaining'])
        assert remaining == {q['pivot'] for q in r['reciprocal']}
        for q in r['reciprocal']:
            endpoints(q, outputs)
            assert p in guard(q['guard'], q['pivot'], q['low'], q['high'], outputs)
            reciprocal += 1
            assert f"| {key[0]}.{key[1]} | {p} | {q['pivot']} | {ep(q)} | {gs(q['guard'])} |" in table
        assert f"| {key[0]}.{key[1]} | `{es(n)}` | {p} |" in table
        assert f"| {key[0]}.{key[1]} | {p} | {ep(r)} | {'; '.join(gs(g) for g in r['guards'])} | {''.join(map(str,r['remaining'])) or 'empty'} |" in table
    assert seen == set(expected) and len(seen) == 16
    return dict(rank_inputs=19, rank_prefix_runs=19*16, isolated_pivots=16,
                own_threshold_guards=own, reciprocal_guards=reciprocal)


def local_positive_control():
    # Two demand-one clauses on five free vertices, sharing edge02.
    # The valid one-edge completion must not be lost to maximality.
    vertices = {0, 2, 4, 6, 7}
    clauses = ({(0, 2), (0, 4), (2, 4)}, {(0, 2), (0, 7), (2, 7)})
    allowed = set(itertools.combinations(sorted(vertices), 2)) - {(4, 7)}
    result = set()
    for e in clauses[0]:
        pending = [c for c in clauses if e not in c]
        available = {f for f in allowed if not set(e) & set(f)}
        if not pending:
            result.add((e,))
        for c in pending:
            available &= c
        result.update(normalize((e, f)) for f in available)
    expected = {((0, 2),), ((0, 2), (4, 6)), ((0, 2), (6, 7)),
                ((0, 4), (2, 7)), ((0, 7), (2, 4))}
    assert result == expected
    return dict(nonmaximal_completion_preserved=True, completions=5)


def triangle_checks(data, note):
    cases = {c['case']: c for c in data['cases']}
    expected_sets = {4: ((3,4,5,6,8), (2,4,5,7,8)),
                     6: ((3,4,5,6,8), (0,4,5,7,8))}
    seen = set()
    completions = {4: set(), 6: set()}
    for item in data['triangles']:
        number = item['case']
        c = cases[number]
        forbidden = set(map(tuple, c['forbidden']))
        a, b = map(set, expected_sets[number])
        assert a & b == {4,5,8} and len(a | b) == 7
        assert a - b == {3,6} and (3,6) in forbidden
        assert all(any(set(r['real']) == real and r['demand'] == 2 for r in c['rows'])
                   for real in (a,b))
        e, t = tuple(item['e']), item['t']
        assert set(e) | {t} == {4,5,8} and len(set(e)) == 2
        key = (number,e)
        assert key not in seen
        seen.add(key)
        cd = tuple(sorted(b-a))
        first = c['rows'][item['first_row']-1]
        second = c['rows'][item['second_row']-1]
        assert first['demand'] == second['demand'] == 1
        f = tuple(item['forced'])
        for partner in (3,6):
            core = normalize((e, cd, (partner,t)))
            used = {v for edge in core for v in edge}
            assert len(used) == 6 and not set(core) & forbidden
            assert not any(set(edge) <= set(first['real']) for edge in core)
            possible = {edge for edge in itertools.combinations(sorted(set(range(9))-used),2)
                        if edge not in forbidden and set(edge) <= set(first['real'])}
            assert possible == {f}
            whole = normalize(core+(f,))
            hits = sum(set(edge) <= set(second['real']) for edge in whole)
            assert hits == (1 if partner == 3 else 0)
            if partner == 3:
                assert all(sum(set(edge) <= set(r['real']) for edge in whole) >= r['demand'] for r in c['rows'])
                completions[number].add(whole)
        assert f"| {number} | {es([e])} | {t} | {item['first_row']} | {es([f])} | {item['second_row']} |" in note
    assert seen == {(number,e) for number in (4,6) for e in ((4,5),(4,8),(5,8))}
    for number in (4,6):
        assert completions[number] == {normalize(n) for n in cases[number]['fourths']}
        assert len(completions[number]) == 3
    return dict(shared_triangle_cases=2,triangle_edges=6,partner_choices=12,completed_forms=6)


def sink_checks(data, note, table):
    cases = {c['case']: c for c in data['cases']}
    runs = 0
    seen = set()
    for item in data['sinks']:
        number = item['case']
        c = cases[number]
        m,n = c['third'],c['fourths'][item['number']-1]
        old = trace((FIRST,SECOND,m),item['placement'])
        whole = trace((FIRST,SECOND,m,n),item['placement'])
        assert len(old['gates']) == 5 and old['height'] == 2
        extra = [e for e in n if all(old['signs'][v] == 0 for v in e)]
        assert len(extra) == 2 and len(whole['gates']) == 7
        sink = tuple(item['old_sink'])
        assert sink in old['boundary']
        index = old['boundary'].index(sink)
        moved = [index,5,6]
        assert len({v for i in moved for v in whole['gates'][i]}) == 6
        for i in moved:
            assert not any(set(whole['gates'][i]) & set(whole['gates'][j])
                           for j in range(i+1,7) if j not in moved)
        heights = [0]*9
        for i,e in enumerate(whole['gates']):
            if i not in moved:
                a,b = e
                heights[a] = heights[b] = 1+max(heights[a],heights[b])
        assert max(heights) <= 2 and 7-len(moved) == 4
        runs += direct_orders((FIRST,SECOND,m,n),whole)
        sentinel_positions = ''.join(str(i) for i,s in enumerate(old['signs']) if s)
        old_edges = ','.join(''.join(map(str,e)) for e in old['boundary'])
        extra_edges = ','.join(''.join(map(str,e)) for e in extra)
        assert f"| {number} | `{es(m)}` | `{es(n)}` | `{ps(item['placement'])}` | {sentinel_positions} | `{old_edges}` | `{extra_edges}` | {es([sink])} |" in note
        assert f"| {number}.{item['number']} | `{es(n)}` | sink |" in table
        seen.add((number,item['number']))
    assert seen == {(1,2),(3,2)}
    return dict(cases=2,real_order_runs=runs,first_two_gates_after_rescheduling=4)


def transfer_checks(data):
    source = ROOT/'results/h9-feedback-round6-certificate.json'
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    assert digest == data['transfer_certificate_sha256'] == 'c258d102a019b789a5a01edfae1b410629d1e61f8a2ba3f1976e09c6eabf05ae'
    previous = json.loads(source.read_text())
    old_second = ((0,3),(1,6),(4,7))
    for number in (2,5):
        new_m = normalize(data['third_forms'][number-1])
        old_m = normalize(previous['cases'][number-1]['third'])
        assert (4,5) in new_m and (5,7) in old_m
        assert set(new_m)-{(4,5)} == set(old_m)-{(5,7)}
        assert set(SECOND)-{(5,7)} == set(old_second)-{(4,7)}
        assert not any(set(e)&{4,5,7} for e in set(new_m)-{(4,5)})
    triple_runs = 0
    for order in itertools.permutations(range(3)):
        inp = [0]*9
        for i,x in zip((4,5,7),order):
            inp[i] = x
        first = run((((4,5),),((5,7),),((4,5),)),inp)
        second = run((((4,5),),((4,7),),((5,7),)),inp)
        assert tuple(first[i] for i in (4,5,7)) == tuple(second[i] for i in (4,5,7)) == (0,1,2)
        triple_runs += 1
    return dict(transferred_cases=[2,5],three_wire_orders=triple_runs,previous_certificate_sha256=digest)


def main():
    start = time.monotonic()
    cert = ROOT / 'results/h9-feedback-round7-certificate.json'
    note = ROOT / 'h9_feedback_round7_031657.md'
    tablefile = ROOT / 'h9_feedback_round7_tables.md'
    assert hashlib.sha256(cert.read_bytes()).hexdigest() == CERTIFICATE_SHA256
    data = json.loads(cert.read_text())
    table = tablefile.read_text()
    assert normalize(data['first']) == FIRST and normalize(data['second']) == SECOND
    structural = structural_checks(data)
    runs = clauses = branches = 0
    for c in data['cases']:
        prefix = (FIRST, SECOND, c['third'])
        for i, r in enumerate(c['rows'], 1):
            row = trace(prefix, r['placement'])
            assert row['real'] == r['real'] and len(row['real']) == 5
            assert len(row['gates']) == 3 - r['demand'] and r['demand'] in (1, 2)
            runs += direct_orders(prefix, row)
            assert f"| {c['case']} | {i} | `{ps(r['placement'])}` | {''.join(map(str,r['real']))} | {r['demand']} |" in table
        if c['case'] in (1, 3):
            branches += local_classification(c, table)
        else:
            assert not c['branches']
            assert set(map(tuple,c['forbidden'])) == propagated_order(prefix)
            assert f"| {c['case']} | `{es(c['third'])}` | `{es(c['forbidden'])}` |" in table
        clauses += sum(len(b['clauses']) for b in c['branches'])
    assert [len(c['fourths']) for c in data['cases']] == [6, 6, 3, 3]
    triangle = triangle_checks(data, note.read_text())
    sink = sink_checks(data, note.read_text(), table)
    transfer = transfer_checks(data)
    ranks = rank_checks(data, table)
    assert time.monotonic() - start < 30
    report = dict(status='VERIFIED',solver_free=True, global_matching_enumeration=False,
                  structural=structural, demand_rows=29,demand_order_runs=runs,
                  total_restriction_order_runs=runs+structural['named_restriction_order_runs']+sink['real_order_runs'],
                  five_vertex_bases=24,local_clauses=clauses,local_edge_branches=branches,
                  fourth_counts=[6,6,3,3],rank=ranks,triangle=triangle,sinks=sink,transfer=transfer,
                  positive_control=local_positive_control(),
                  certificate_sha256=CERTIFICATE_SHA256,
                  table_sha256=hashlib.sha256(tablefile.read_bytes()).hexdigest(),
                  note_sha256=hashlib.sha256(note.read_bytes()).hexdigest(),
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  elapsed_seconds=time.monotonic()-start)
    (ROOT / 'results/h9-feedback-round7-proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
