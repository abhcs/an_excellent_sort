#!/usr/bin/env python3
"""Seek small weighted-count certificates; resulting inequalities are replayable."""
import itertools
import json
from pathlib import Path
import z3
from h9_feedback_next_p9 import FIRST, SECOND, placements, prefix_state


def main():
    root = Path(__file__).parents[1]
    data = json.loads((root / 'results/h9-feedback-next-p9.json').read_text())
    out = []
    for index, item in enumerate(data):
        rows = {}
        for placement in placements(9, 4):
            row = prefix_state((FIRST, SECOND, item['third']), placement)
            if len(row['gates']) == 1:
                real = tuple(i for i, value in enumerate(row['state']) if not value)
                rows.setdefault(real, placement)
        real_sets = list(rows)
        opt = z3.Optimize()
        opt.set(timeout=5000)
        multipliers = [z3.Int(f'w_{i}') for i in range(len(rows))]
        prices = [z3.Int(f'p_{i}') for i in range(9)]
        gate_charge = z3.Int('gate_charge')
        opt.add(*[z3.And(0 <= w, w <= 4) for w in multipliers])
        opt.add(*[p >= 0 for p in prices], gate_charge >= 0)
        for a, b in itertools.combinations(range(9), 2):
            weight = z3.Sum([w for w, real in zip(multipliers, real_sets) if a in real and b in real])
            opt.add(2 * weight <= prices[a] + prices[b] + gate_charge)
        opt.add(z3.Sum(prices) + 4 * gate_charge < 4 * z3.Sum(multipliers))
        opt.minimize(z3.Sum(multipliers))
        opt.minimize(gate_charge)
        answer = str(opt.check())
        record = dict(case=index + 1, status=answer)
        if answer == 'sat':
            model = opt.model()
            values = [model.eval(w).as_long() for w in multipliers]
            p = [model.eval(x).as_long() for x in prices]
            g = model.eval(gate_charge).as_long()
            assert sum(p) + 4 * g < 4 * sum(values)
            assert all(2 * sum(w for w, real in zip(values, real_sets) if a in real and b in real) <= p[a] + p[b] + g
                       for a, b in itertools.combinations(range(9), 2))
            record |= dict(twice_prices=p, twice_gate_charge=g,
                           rows=[dict(weight=w, real_set=real, placement=rows[real])
                                 for w, real in zip(values, real_sets) if w])
        print(record, flush=True)
        out.append(record)
    (root / 'results/h9-feedback-next-prices.json').write_text(json.dumps(out, indent=2) + '\n')


if __name__ == '__main__':
    main()
