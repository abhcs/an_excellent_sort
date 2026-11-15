#!/usr/bin/env python3
"""Bounded discovery for the single H9 class 02 14 56."""
import itertools
import json
import time
from pathlib import Path

from netlib import matchings, run
from h9_feedback_round4_rank_witnesses import lift

FIRST = ((0, 1), (2, 3), (4, 5))
SECOND = ((0, 2), (1, 4), (5, 6))


def norm(layer):
    return tuple(sorted(tuple(sorted(e)) for e in layer))


def canonical(layer):
    return min(norm(layer), norm((8 if a == 7 else 7 if a == 8 else a,
                                 8 if b == 7 else 7 if b == 8 else b) for a, b in layer))


def main():
    start = time.monotonic()
    root = Path(__file__).parents[1]
    source = next(e for e in json.loads((root / 'results/h9-feedback-next-fourths-combined.json').read_text())
                  if e['label'] == '(0,2)(1,4)(5,6)')
    seeds = sorted({lift(bits) for bits in itertools.product((0, 1), repeat=9)})
    layers = matchings(9)
    cases = []
    for row in source['rows']:
        third = norm(row['third'])
        if canonical(third) != third:
            continue
        case = dict(case=len(cases) + 1, third=third, fourths=[])
        for number, fourth in enumerate(row['fourths'], 1):
            outputs = [run((FIRST, SECOND, third, fourth), x) for x in seeds]
            forbidden, required, witnesses = set(), set(), []
            for a in range(9):
                vals = [y[a] for y in outputs]
                if max(vals) - min(vals) >= 4:
                    required.add(a)
                for b in range(a + 1, 9):
                    for op in (min, max):
                        vals = [op(y[a], y[b]) for y in outputs]
                        if max(vals) - min(vals) >= 4:
                            forbidden.add((a, b))
                            break
            passing = [m for m in layers if not set(m) & forbidden
                       and required <= {v for e in m for v in e}]
            isolated = [a for a in required if all(norm([(a, b)])[0] in forbidden for b in range(9) if a != b)]
            record = dict(number=number, fourth=fourth, required=sorted(required),
                          forbidden=sorted(forbidden), isolated=isolated,
                          fifths=passing)
            case['fourths'].append(record)
            print(case['case'], third, number, fourth, 'Q', len(passing), 'isolated', isolated, flush=True)
            assert time.monotonic() - start < 40
        cases.append(case)
    report = dict(status='DISCOVERY_ONLY', second=SECOND, cases=cases,
                  elapsed_seconds=time.monotonic() - start)
    (root / 'results/h9-feedback-round5-probe.json').write_text(json.dumps(report, indent=2) + '\n')
    print('DONE', len(cases), report['elapsed_seconds'])


if __name__ == '__main__':
    main()
