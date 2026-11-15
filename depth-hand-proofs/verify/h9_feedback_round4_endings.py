#!/usr/bin/env python3
"""Bounded contact-price discovery; exact signed traces are exported."""
import itertools
import json
from pathlib import Path
import z3
from h9_feedback_round3_021637 import FIRST, SECOND, cone
from h9_feedback_reschedule_extend import prefix_state
from netlib import placements, matchings


def main():
    root = Path(__file__).parents[1]
    data = json.loads((root / 'results/h9-feedback-round3-021637.json').read_text())
    layers = matchings(9)
    edges = list(itertools.combinations(range(9), 2))
    output = []
    for case, item in enumerate(data, 1):
        for number, suffix in enumerate(item['fourths'], 1):
            fourth = tuple(map(tuple, suffix['fourth']))
            prefix = (FIRST, SECOND, item['third'], fourth)
            unique = {}
            for p in placements(9, 4):
                row = prefix_state(prefix, p)
                if len(row['gates']) != 3:
                    continue
                real = frozenset(i for i, s in enumerate(row['state']) if not s)
                for j, (a, b) in enumerate(row['gates']):
                    if row['last'][a] == row['last'][b] == j:
                        unique.setdefault((real, frozenset((a, b))), row)
            rows, clauses = [], []
            for (real, sink), row in unique.items():
                clause = {e for e in edges if set(e) <= real and bool(set(e) & sink)}
                clauses.append(clause)
                rows.append(dict(real=sorted(real), sink=sorted(sink), placement=row['placement'],
                                 gates=row['gates'], depths=row['depths']))
            passing = [layer for layer in layers if all(set(layer) & clause for clause in clauses)]
            record = dict(case=case, number=number, third=item['third'], fourth=fourth, rows=rows,
                          passing=[dict(fifth=layer, cone=cone(prefix + (layer,), 2)) for layer in passing])
            if not passing:
                weights = [z3.Int(f'w{case}_{number}_{i}') for i in range(len(rows))]
                prices = [z3.Int(f'p{case}_{number}_{i}') for i in range(9)]
                gate = z3.Int(f'g{case}_{number}')
                solver = z3.Optimize()
                solver.set(timeout=3000)
                solver.add(*[z3.And(w >= 0, w <= 6) for w in weights])
                solver.add(*[z3.And(p >= 0, p <= 100) for p in prices], gate >= 0, gate <= 30)
                for a, b in edges:
                    if (a, b) not in fourth:
                        load = z3.Sum([w for w, clause in zip(weights, clauses) if (a, b) in clause])
                        solver.add(2 * load <= prices[a] + prices[b] + gate)
                solver.add(z3.Sum(prices) + 4 * gate < 2 * z3.Sum(weights))
                solver.minimize(z3.Sum([z3.If(w > 0, 1, 0) for w in weights]))
                solver.minimize(z3.Sum(weights))
                status = solver.check()
                record['price_status'] = str(status)
                if status == z3.sat:
                    model = solver.model()
                    ws = [model.eval(w).as_long() for w in weights]
                    ps = [model.eval(p).as_long() for p in prices]
                    g = model.eval(gate).as_long()
                    assert all(2 * sum(w for w, clause in zip(ws, clauses) if edge in clause)
                               <= sum(ps[v] for v in edge) + g for edge in edges if edge not in fourth)
                    assert sum(ps) + 4 * g < 2 * sum(ws)
                    record.update(weights=ws, twice_prices=ps, twice_gate_price=g,
                                  twice_budget=sum(ps) + 4 * g)
            assert all(x['cone'] is not None for x in record['passing'])
            output.append(record)
            (root / 'results/h9-feedback-round4-endings.json').write_text(json.dumps(output, indent=2) + '\n')
            print(case, number, 'contacts', len(rows), 'passing', len(passing),
                  'price', record.get('price_status'), 'support', sum(w > 0 for w in record.get('weights', [])), flush=True)


if __name__ == '__main__':
    main()
