#!/usr/bin/env python3
"""Bounded discovery of small price certificates for the 02 16 37 case."""
import itertools
import json
from pathlib import Path
import z3
from h9_feedback_round3_021637 import FIRST, SECOND
from h9_feedback_reschedule_extend import prefix_state
from netlib import placements, run

SUBSETS = {1: (0, 1, 2, 3, 6), 3: (0, 1, 2, 6), 5: (1, 2, 5, 6),
           7: (1, 2, 4), 9: (0, 2, 3, 4), 11: (0, 1, 4, 6),
           12: (0, 2, 3, 5), 13: (0, 1, 2, 3)}


def ordered(prefix):
    relation = {(i, i) for i in range(9)}
    for layer in prefix:
        for a, b in layer:
            old = set(relation)
            relation = {(u, v) for u, v in old if u not in (a, b) and v not in (a, b)}
            relation |= {(a, a), (b, b), (a, b)}
            for v in range(9):
                if v in (a, b):
                    continue
                if (a, v) in old or (b, v) in old:
                    relation.add((a, v))
                if (a, v) in old and (b, v) in old:
                    relation.add((b, v))
                if (v, a) in old or (v, b) in old:
                    relation.add((v, b))
                if (v, a) in old and (v, b) in old:
                    relation.add((v, a))
    return sorted((a, b) for a, b in relation if a < b)


def main():
    root = Path(__file__).parents[1]
    third_data = json.loads((root / 'results/h9-feedback-round3-021637.json').read_text())
    output = []
    for case, selected in SUBSETS.items():
        third = third_data[case - 1]['third']
        prefix = (FIRST, SECOND, third)
        rows = {}
        for p in placements(9, 4):
            row = prefix_state(prefix, p)
            if len(row['gates']) == 1:
                real = tuple(i for i, s in enumerate(row['state']) if not s)
                rows.setdefault(real, row)
        chosen = [list(rows.items())[i] for i in selected]
        forbidden = ordered(prefix)
        image = [run(prefix, x) for x in itertools.product((0, 1), repeat=9)]
        exact = [edge for edge in itertools.combinations(range(9), 2)
                 if all(x[edge[0]] <= x[edge[1]] for x in image)]
        assert set(forbidden) <= set(exact)
        weights = {edge: sum(set(edge) <= set(real) for real, row in chosen)
                   for edge in itertools.combinations(range(9), 2) if edge not in forbidden}
        prices = [z3.Int(f'p{case}_{v}') for v in range(9)]
        gate = z3.Int(f'g{case}')
        solver = z3.Optimize()
        solver.set(timeout=5000)
        solver.add(*[z3.And(p >= 0, p <= 20) for p in prices], gate >= 0, gate <= 10)
        for (a, b), weight in weights.items():
            solver.add(2 * weight <= prices[a] + prices[b] + gate)
        solver.add(z3.Sum(prices) + 4 * gate < 4 * len(chosen))
        solver.minimize(z3.Sum(prices) + 4 * gate)
        solver.minimize(gate)
        status = solver.check()
        record = dict(case=case, third=third, forbidden=forbidden, additional_exact_comparabilities=sorted(set(exact)-set(forbidden)),
                      rows=[dict(real=real, placement=row['placement']) for real, row in chosen],
                      status=str(status))
        if status == z3.sat:
            model = solver.model()
            ps = [model.eval(p).as_long() for p in prices]
            g = model.eval(gate).as_long()
            assert all(2 * weight <= ps[a] + ps[b] + g for (a, b), weight in weights.items())
            assert sum(ps) + 4 * g < 4 * len(chosen)
            record.update(twice_prices=ps, twice_gate_price=g, twice_budget=sum(ps) + 4 * g)
        print(record, flush=True)
        output.append(record)
        (root / 'results/h9-feedback-round4-prices.json').write_text(json.dumps(output, indent=2) + '\n')
    (root / 'results/h9-feedback-round4-prices.json').write_text(json.dumps(output, indent=2) + '\n')


if __name__ == '__main__':
    main()
