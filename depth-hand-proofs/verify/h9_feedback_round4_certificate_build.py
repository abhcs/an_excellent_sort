#!/usr/bin/env python3
"""Assemble fixed human-readable tables; the separate checker is solver-free."""
import itertools
import json
from pathlib import Path
from h9_feedback_round3_021637 import FIRST, SECOND
from h9_feedback_round4_prices import ordered
from h9_feedback_reschedule_extend import prefix_state
from netlib import placements


def layer_text(layer):
    return ' '.join(f'{a}{b}' for a, b in layer)


def ptext(p):
    return ' '.join(('+' if s > 0 else '-') + str(i) for i, s in sorted((int(k), v) for k, v in p.items()))


def main():
    root = Path(__file__).parents[1]
    thirds = json.loads((root / 'results/h9-feedback-round3-021637.json').read_text())
    prices = json.loads((root / 'results/h9-feedback-round4-prices.json').read_text())
    ranks = json.loads((root / 'results/h9-feedback-round4-rank-witnesses.json').read_text())
    cases = []
    for number, item in enumerate(thirds, 1):
        third = item['third']
        forbidden = set(ordered((FIRST, SECOND, third)))
        if [6, 7] in third:
            forbidden.update(((1, 7), (2, 7), (3, 7)))
        cases.append(dict(case=number, third=third, forbidden=sorted(forbidden)))
    direct = []
    for record in prices:
        case = record['case']
        proof = dict(case=case, rows=record['rows'])
        if case == 5:
            proof['kind'] = 'odd_common_triple'
        elif case == 13:
            proof['kind'] = 'two_odd_triples'
        else:
            assert record['status'] == 'sat'
            proof.update(kind='strict_price', twice_prices=record['twice_prices'],
                         twice_gate_price=record['twice_gate_price'], twice_budget=record['twice_budget'])
        direct.append(proof)
    fourth_reductions = []
    for case in (2, 4, 6, 8, 10, 14):
        third = thirds[case - 1]['third']
        prefix = (FIRST, SECOND, third)
        rows = {}
        for p in placements(9, 4):
            row = prefix_state(prefix, p)
            if len(row['gates']) == 1:
                real = tuple(i for i, s in enumerate(row['state']) if not s)
                rows.setdefault(real, dict(real=real, placement=p, demand=2))
        if case == 6:
            p = {0: 1, 2: 1, 4: -1, 5: -1}
            row = prefix_state(prefix, p)
            assert len(row['gates']) == 2
            real = tuple(i for i, s in enumerate(row['state']) if not s)
            rows[real] = dict(real=real, placement=p, demand=1)
        contacts = []
        if case in (8, 10):
            p = {0: 1, 2: 1}
            row = prefix_state(prefix, p)
            sinks = sorted(tuple(sorted((a, b))) for j, (a, b) in enumerate(row['gates'])
                           if row['last'][a] == row['last'][b] == j)
            contacts.append(dict(placement=p, real=[i for i, s in enumerate(row['state']) if not s], sinks=sinks))
        fourth_reductions.append(dict(case=case, rows=list(rows.values()), contacts=contacts,
                                      fourths=[row['fourth'] for row in thirds[case - 1]['fourths']]))
    certificate = dict(cases=cases, direct_cases=direct, fourth_reductions=fourth_reductions,
                       rank_inputs=ranks['inputs'], rank_cases=ranks['cases'],
                       rank_rows=ranks['endpoint_rows'], final_contacts=ranks['final_contacts'])
    target = root / 'results/h9-feedback-round4-certificate.json'
    target.write_text(json.dumps(certificate, indent=2) + '\n')

    lines = ['# Fixed certificate tables for the H9 case `02 16 37`', '',
             'These are the explicit finite premises of the [hand proof](h9_feedback_round4_021637.md).',
             'A two-digit string denotes an unordered comparator; a longer string denotes a set of positions.',
             'Sentinels are placed at the original network inputs. Every displayed real set is at the stated layer boundary.', '',
             '## 1. Ordered pairs after L3', '',
             'Each pair below is already ordered and may be omitted from L4. The proof gives the min/max derivation rule and the additional common upper bound at wire7.', '',
             '| Case | L3 | Forbidden L4 pairs |', '|---:|---|---|']
    for case in cases:
        lines.append(f"| {case['case']} | `{layer_text(case['third'])}` | `{layer_text(case['forbidden'])}` |")
    lines += ['', '## 2. Direct five-real contradictions', '',
              'Every row in this section retains exactly one RR gate through L3, so L4 requires two edges in R.', '',
              '| Case | Input sentinels | R after L3 |', '|---:|---|---|']
    for record in direct:
        for row in record['rows']:
            lines.append(f"| {record['case']} | `{ptext(row['placement'])}` | {''.join(map(str,row['real']))} |")
    lines += ['', 'For the strict cases, these are twice the vertex prices, the twice-gate charge g, and the resulting budget. The required twice-total is four times the number of rows.', '',
              '| Case | Twice vertex prices at 0,...,8 | g | Budget | Demand |', '|---:|---|---:|---:|---:|']
    for record in direct:
        if record['kind'] == 'strict_price':
            lines.append(f"| {record['case']} | `{','.join(map(str,record['twice_prices']))}` | {record['twice_gate_price']} | {record['twice_budget']} | {4*len(record['rows'])} |")
    lines += ['', 'Cases5 and13 use the two parity arguments in the main proof; no strict price witness is claimed for them.', '',
              '## 3. Fourth-layer demands', '',
              'Demand2 rows retain one RR gate through L3; the sole demand1 row retains two.', '',
              '| Case | Input sentinels | R after L3 | Required L4 edges in R |', '|---:|---|---|---:|']
    for record in fourth_reductions:
        for row in record['rows']:
            lines.append(f"| {record['case']} | `{ptext(row['placement'])}` | {''.join(map(str,row['real']))} | {row['demand']} |")
    lines += ['', 'The two seven-real restrictions retain five gates of height two. Every listed sink must be touched by an L4 RR edge.', '',
              '| Case | Input sentinels | Real positions after L3 | Sinks |', '|---:|---|---|---|']
    for record in fourth_reductions:
        for row in record['contacts']:
            lines.append(f"| {record['case']} | `{ptext(row['placement'])}` | {''.join(map(str,row['real']))} | `{layer_text(row['sinks'])}` |")
    lines += ['', 'The matching arguments in the main proof leave precisely these forms. Labels C.N are used below.', '',
              '| Label | L4 |', '|---|---|']
    for record in fourth_reductions:
        for number, fourth in enumerate(record['fourths'], 1):
            lines.append(f"| {record['case']}.{number} | `{layer_text(fourth)}` |")
    lines += ['', '## 4. Fourteen real inputs for every ending', '',
              'Each nine-digit string is a permutation of ranks0 through8 on the original inputs. No enumeration of rank permutations is a premise.', '',
              '| Input | Ranks on wires0,...,8 |', '|---|---|']
    for i, values in enumerate(ranks['inputs']):
        lines.append(f"| {chr(65+i)} | `{''.join(map(str,values))}` |")
    lines += ['', 'The attainable-rank interval lemma and two-layer forward-cone bound exclude any idle wire or comparison output with two witnessed ranks differing by at least four.',
              'The following plans use only those exclusions. In a forced plan, earlier forced edges remove their vertices from later partner choices. In the Hall row, three required vertices have only two possible outside partners.', '',
              '| Label | Consequence of endpoint rows |', '|---|---|']
    for record in ranks['cases']:
        if record['kind'] == 'isolated':
            desc = f"wire{record['plan'][0][0]} must be used but has no partner"
        elif record['kind'] == 'hall':
            desc = 'required wires3,5,8 can only meet2,4'
        else:
            desc = 'force ' + ', then '.join(f'{p}{a[0]}' for p, a in record['plan'])
        lines.append(f"| {record['case']}.{record['number']} | {desc} |")
    lines += ['', '## 5. Rank endpoint rows', '',
              '`idle` is the value on the pivot itself; `min` or `max` is the indicated output of its proposed next comparison. Each low/high cell names a bank input and the rank actually produced.',
              'Partner lists combine rows with identical witnesses and values. Every gap is at least four.', '']
    for record in ranks['cases']:
        label = f"{record['case']}.{record['number']}"
        lines += [f'### {label}', '', '| Pivot | Excluded partner(s) | Output | Low witness | High witness |',
                  '|---:|---|---|---|---|']
        groups = {}
        for row in ranks['endpoint_rows']:
            if (row['case'], row['number']) != (record['case'], record['number']):
                continue
            key = (row['pivot'], row['output'], row['low_input'], row['low'], row['high_input'], row['high'])
            groups.setdefault(key, []).append(row['partner'])
        for (pivot, operation, low, lo, high, hi), partners in groups.items():
            names = ','.join('idle' if p is None else str(p) for p in partners)
            lines.append(f"| {pivot} | {names} | {operation} | {chr(65+low)}:{lo} | {chr(65+high)}:{hi} |")
        lines.append('')
    lines += ['## 6. The two forced endings violate a sink contact', '',
              'Each row retains exactly three RR gates through L4. The forced L5 matching has no RR edge touching the named sink.', '',
              '| Label | Forced L5 | Input sentinels | R after L4 | Sink |', '|---|---|---|---|---|']
    for row in ranks['final_contacts']:
        lines.append(f"| {row['case']}.{row['number']} | `{layer_text(row['fifth'])}` | `{ptext(row['placement'])}` | {''.join(map(str,row['real']))} | {''.join(map(str,row['sink']))} |")
    lines += ['', 'The [independent checker](verify/h9_feedback_round4_proof.py) checks every displayed premise and the complete coverage of the endpoint plans. Its [audit](results/h9-feedback-round4-proof.json) records the finite counts and source hashes.', '']
    (root / 'h9_feedback_round4_tables.md').write_text('\n'.join(lines))
    print(json.dumps(dict(certificate=str(target), rank_inputs=len(ranks['inputs']),
                          endpoint_rows=len(ranks['endpoint_rows']), table_lines=len(lines))))


if __name__ == '__main__':
    main()
