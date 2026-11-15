#!/usr/bin/env python3
"""Rational contact-price discovery; every returned witness is checked exactly."""
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
import z3


def main():
    root = Path(__file__).parents[1]
    data = json.loads((root / 'results/h9-feedback-round4-endings.json').read_text())
    out = []
    for rec in data:
        if rec['passing']:
            continue
        rows, forbidden = rec['rows'], set(map(tuple, rec['fourth']))
        weights = [z3.Real(f'w{i}') for i in range(len(rows))]
        prices = [z3.Real(f'p{i}') for i in range(9)]
        gate = z3.Real('g')
        solver = z3.SolverFor('QF_LRA')
        solver.set(timeout=3000)
        solver.add(*[x >= 0 for x in weights + prices + [gate]])
        for a, b in itertools.combinations(range(9), 2):
            if (a, b) not in forbidden:
                load = z3.Sum([w for w, row in zip(weights, rows)
                               if {a, b} <= set(row['real']) and {a, b} & set(row['sink'])])
                solver.add(load <= prices[a] + prices[b] + gate)
        solver.add(z3.Sum(weights) - z3.Sum(prices) - 4 * gate >= 1)
        status = solver.check()
        record = dict(case=rec['case'], number=rec['number'], status=str(status))
        if status == z3.sat:
            model = solver.model()
            values = [model.eval(x, model_completion=True) for x in weights + prices + [gate]]
            fs = [Fraction(v.numerator_as_long(), v.denominator_as_long()) for v in values]
            scale = math.lcm(*(v.denominator for v in fs))
            ws = [int(v * scale) for v in fs[:len(rows)]]
            ps = [int(v * scale) for v in fs[len(rows):-1]]
            g = int(fs[-1] * scale)
            assert sum(ws) > sum(ps) + 4 * g
            for a, b in itertools.combinations(range(9), 2):
                if (a, b) not in forbidden:
                    load = sum(w for w, row in zip(ws, rows)
                               if {a, b} <= set(row['real']) and {a, b} & set(row['sink']))
                    assert load <= ps[a] + ps[b] + g
            record.update(weights=ws, prices=ps, gate_price=g, budget=sum(ps) + 4 * g)
        print(record, flush=True)
        out.append(record)
    (root / 'results/h9-feedback-round4-contact-lp.json').write_text(json.dumps(out, indent=2) + '\n')


if __name__ == '__main__':
    main()
