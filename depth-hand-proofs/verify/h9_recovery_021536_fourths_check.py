#!/usr/bin/env python3
"""Check fixed hand recipes and local (at most five unused wires) tables."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import time
from h9_recovery_021536_reduction_verify import C, FORMS, direct, normalize, trace

ROOT = Path(__file__).resolve().parents[1]


def ordered(prefix):
    rel = {(v, v) for v in range(9)}
    for layer in prefix:
        for a, b in layer:
            old = rel
            rel = {(u, v) for u, v in old if u not in (a, b) and v not in (a, b)}
            rel |= {(a, a), (b, b), (a, b)}
            for v in set(range(9)) - {a, b}:
                if (a, v) in old or (b, v) in old: rel.add((a, v))
                if (a, v) in old and (b, v) in old: rel.add((b, v))
                if (v, a) in old or (v, b) in old: rel.add((v, b))
                if (v, a) in old and (v, b) in old: rel.add((v, a))
    return {(a, b) for a, b in rel if a < b}


def pairing4(T):
    a, b, c, d = sorted(T)
    return [normalize(((a, b), (c, d))), normalize(((a, c), (b, d))),
            normalize(((a, d), (b, c)))]


def has(c, S, demand=2):
    assert any(set(r['real']) == set(S) and r['demand'] >= demand for r in c['rows'])


def cores(c):
    """Necessary cores derived by the written matching lemmas; no 9-wire scan."""
    number = c['case']; forbidden = set(map(tuple, c['forbidden'])); answer = []
    if number in (4, 11, 12, 18):
        T, edges = {
            4: ({5, 7, 8}, [(2, 3), (0, 1), (1, 4), (1, 2), (2, 4)]),
            11: ({2, 6, 8}, [(0, 1), (0, 4), (1, 7), (4, 7)]),
            12: ({2, 5, 8}, [(0, 1), (0, 4), (1, 7), (4, 7)]),
            18: ({2, 4, 5}, [(7, 8), (0, 1), (1, 8), (0, 7)])}[number]
        V = {v for e in edges for v in e}; assert not T & V
        for e in edges: has(c, T | set(e))
        for v in V:
            residual = [e for e in edges if v not in e]
            assert len({w for e in residual for w in e}) < 2 * len(residual)
        return []
    if number == 6:
        for S in ({0, 1, 2, 7, 8}, {3, 4, 6, 7, 8}): has(c, S)
        for S in ({1, 4, 5, 7, 8}, {1, 3, 4, 5, 7}, {1, 3, 4, 5, 8},
                  {0, 3, 5, 7, 8}, {0, 3, 4, 5, 7}, {0, 3, 4, 5, 8}): has(c, S, 1)
        assert (7, 8) in forbidden
        # The two odd triples and common pair force the four-edge shape
        # in the note; paired contacts force its unmatched A vertex to
        # be both0 and1. No finite matching table is a premise.
        return []
    if number == 17:
        weights = [2, 1, 2, 2, 3]
        prices = [0, 3, 3, 0, 3, 0, 1, 3, 3]
        assert len(c['rows']) == len(weights)
        demand = sum(w * r['demand'] for w, r in zip(weights, c['rows']))
        for a, b in itertools.combinations(range(9), 2):
            if (a, b) in forbidden: continue
            cost = sum(w for w, r in zip(weights, c['rows']) if {a, b} <= set(r['real']))
            assert cost <= prices[a] + prices[b]
        assert demand == 17 and sum(prices) == 16
        return []
    if number in (3, 7, 8, 16, 17):
        T, outside = {
            3: ({2, 6, 7, 8}, (5, 1)),
            7: ({3, 6, 7, 8}, (2, 4)),
            8: ({0, 1, 2, 8}, (4, 3)),
            16: ({0, 1, 2, 8}, (3, 5)),
            17: ({1, 4, 6, 8}, (2, 7))}[number]
        x, y = outside
        has(c, T | {x}); has(c, T | {y})
        answer.extend(pairing4(T))
        for e in itertools.combinations(sorted(T), 2):
            u, v = sorted(T - set(e))
            answer.extend([normalize((e, (x, u), (y, v))),
                           normalize((e, (x, v), (y, u)))])
    elif number in (5, 13, 15):
        A, B, pair = {
            5: ({0, 1, 2}, {3, 4, 5}, (7, 8)),
            13: ({1, 3, 6}, {0, 2, 5}, (7, 8)),
            15: ({0, 2, 3}, {4, 6, 7}, (1, 8))}[number]
        u, v = pair; assert not A & B and not (A | B) & set(pair)
        has(c, A | set(pair)); has(c, B | set(pair))
        for e in itertools.combinations(sorted(A), 2):
            a = next(iter(A - set(e)))
            for f in itertools.combinations(sorted(B), 2):
                b = next(iter(B - set(f)))
                answer.extend([normalize((pair, e, f)),
                               normalize((e, f, (a, u), (b, v))),
                               normalize((e, f, (a, v), (b, u)))])
    elif number == 10:
        has(c, {0, 1, 2, 7, 8}); has(c, {1, 3, 6, 7, 8})
        assert (7, 8) in forbidden
        # Shared triangle178 forces17 or18. Each original demand then
        # requires an edge in its three unused vertices.
        for e in ((1, 7), (1, 8)):
            A = {0, 1, 2, 7, 8} - set(e)
            B = {1, 3, 6, 7, 8} - set(e)
            for f in itertools.combinations(sorted(A), 2):
                for g in itertools.combinations(sorted(B), 2):
                    if not set(f) & set(g): answer.append(normalize((e, f, g)))
    elif number == 1:
        for S in ({0, 1, 4, 7, 8}, {2, 4, 5, 7, 8}, {1, 4, 5, 7, 8}): has(c, S)
        has(c, {1, 2, 3, 4, 7}, 1); has(c, {1, 2, 3, 4, 8}, 1)
        assert (7, 8) in forbidden
        # Shared triangle478 forces47/48; the three residual triangle
        # contacts force18+25 or58+01, and the exchanged alternatives.
        answer = [((4, 7), (1, 8), (2, 5)), ((4, 7), (5, 8), (0, 1)),
                  ((4, 8), (1, 7), (2, 5)), ((4, 8), (5, 7), (0, 1))]
    elif number == 9:
        for S in ({0, 1, 2, 7, 8}, {0, 2, 4, 7, 8}, {1, 3, 5, 7, 8}, {3, 4, 5, 7, 8}): has(c, S)
        assert (7, 8) in forbidden
        answer = [((0, 2), (1, 7), (3, 5), (4, 8)),
                  ((0, 2), (1, 8), (3, 5), (4, 7))]
    elif number == 14:
        for S in ({0, 1, 2, 7, 8}, {2, 3, 5, 7, 8}, {1, 3, 5, 7, 8}, {0, 2, 5, 7, 8}): has(c, S)
        assert (0, 5) in forbidden and (1, 7) in forbidden
        answer = [((7, 8), (0, 2), (3, 5))]
    else:
        raise AssertionError(number)
    return sorted({normalize(M) for M in answer if not set(normalize(M)) & forbidden
                   and len({v for e in M for v in e}) == 2 * len(M)})


def pending(c, core):
    free = set(range(9)) - {v for e in core for v in e}
    allowed = set(itertools.combinations(sorted(free), 2)) - set(map(tuple, c['forbidden']))
    result = []
    for i, r in enumerate(c['rows'], 1):
        R = set(r['real']); need = r['demand'] - sum(set(e) <= R for e in core)
        if need > 0:
            result.append(dict(row=i, need=need, edges=sorted(e for e in allowed if set(e) <= R)))
    return free, allowed, result


def local_proof(free, allowed, clauses):
    """One anchor and at most one remaining edge; this is the hand table rule."""
    assert len(free) in (1, 3, 5)
    if len(free) <= 3:
        if not clauses: return {()} | {(e,) for e in allowed}, []
        good = set(allowed)
        for r in clauses:
            if r['need'] > 1: good.clear()
            good &= set(map(tuple, r['edges']))
        return {(e,) for e in good}, []
    assert clauses  # All five-free-wire table cores retain an unmet demand.
    anchor = min(clauses, key=lambda r: (len(r['edges']), r['row']))
    result = set(); arms = []
    for e in map(tuple, anchor['edges']):
        rest = free - set(e)
        available = {f for f in allowed if set(f) <= rest}
        residual = []
        for r in clauses:
            need = r['need'] - int(e in set(map(tuple, r['edges'])))
            if need > 0: residual.append(dict(row=r['row'], need=need, edges=r['edges']))
        finishes, _ = local_proof(rest, available, residual)
        result |= {normalize((e,) + tail) for tail in finishes}
        arms.append(dict(edge=e, tails=sorted(finishes)))
    return result, arms


def es(M): return ' '.join(''.join(map(str, e)) for e in M) or 'none'


def table_line(row):
    clauses = '; '.join(f"{r['row']}:{r['need']}({es(r['edges'])})" for r in row['clauses']) or 'none'
    answer = ' / '.join(es(x) for x in row['completions']) or 'impossible'
    return f"| `{es(row['core'])}` | {clauses} | `{answer}` |"


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--out', type=Path); args = parser.parse_args()
    start = time.monotonic()
    path = ROOT / 'results/h9-recovery-021536-fourths-certificate.json'
    data = json.loads(path.read_text())
    table = (ROOT / 'h9_recovery_021536_fourths_tables.md').read_text()
    assert [c['case'] for c in data['cases']] == [i for i in range(1, 19) if i != 2]
    runs = row_count = core_count = arm_count = 0; counts = {}
    for c in data['cases']:
        number = c['case']; M = normalize(c['third'])
        assert M == normalize(tuple(map(int, e)) for e in FORMS[number - 1].split())
        assert set(map(tuple, c['forbidden'])) == ordered(C + (M,))
        for i, r in enumerate(c['rows'], 1):
            p = {int(v): s for v, s in r['placement'].items()}
            trace_row = trace(C + (M,), p)
            assert trace_row['real'] == set(r['real']) and len(r['real']) == 5
            assert len(trace_row['gates']) == 3 - r['demand'] and r['demand'] in (1, 2)
            runs += direct(C + (M,), p, trace_row); row_count += 1
            ps = ' '.join(('+' if p[v] > 0 else '-') + str(v) for v in sorted(p))
            assert f"| {i} | `{ps}` | {''.join(map(str, r['real']))} | {r['demand']} |" in table
        obtained = set(); required = cores(c)
        assert required == [normalize(row['core']) for row in c['core_tables']]
        for row in c['core_tables']:
            core = normalize(row['core']); free, allowed, available_clauses = pending(c, core)
            by_index = {r['row']: r for r in available_clauses}
            assert row['clauses'] and len({r['row'] for r in row['clauses']}) == len(row['clauses']) or not available_clauses
            for r in row['clauses']:
                assert r == json.loads(json.dumps(by_index[r['row']]))
            finishes, arms = local_proof(free, allowed, row['clauses'])
            assert finishes == {normalize(x) for x in row['completions']}
            for tail in finishes:
                whole = normalize(core + tail)
                assert all(sum(set(e) <= set(r['real']) for e in whole) >= r['demand'] for r in c['rows'])
                obtained.add(whole)
            assert table_line(row) in table
            core_count += 1; arm_count += len(arms)
        assert obtained == {normalize(x) for x in c['fourths']}
        counts[number] = len(obtained)
    assert sum(counts.values()) == 31
    assert {i: n for i, n in counts.items() if n} == {1: 6, 5: 18, 8: 2, 9: 2, 14: 1, 16: 2}
    assert time.monotonic() - start < 30
    report = dict(status='VERIFIED_SEVENTEEN_CLASSIFICATIONS', solver_free=True,
                  global_nine_wire_matching_scan=False, omitted_case=2, accepted_new_H9_classes=0,
                  third_layer_forms=17, fourth_layer_forms=31, counts=counts,
                  signed_demand_rows=row_count, direct_order_replays=runs,
                  local_cores=core_count, local_first_edge_arms=arm_count,
                  certificate_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  table_sha256=hashlib.sha256((ROOT / 'h9_recovery_021536_fourths_tables.md').read_bytes()).hexdigest(),
                  elapsed_seconds=time.monotonic() - start)
    if args.out: args.out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__': main()
