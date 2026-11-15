#!/usr/bin/env python3
"""Bounded discovery for L2=02 16 37, after its deletion-triangle reduction."""
import itertools
import json
from pathlib import Path
from h9_feedback_round2_screen import witness
from h9_feedback_reschedule_extend import prefix_state
from netlib import placements, matchings, run

FIRST = ((0, 1), (2, 3), (4, 5))
SECOND = ((0, 2), (1, 6), (3, 7))
SWAP = (0, 3, 2, 1, 4, 5, 7, 6, 8)


def canonical(layer):
    layer = tuple(map(tuple, layer))
    return min(layer, tuple(sorted(tuple(sorted((SWAP[a], SWAP[b]))) for a, b in layer)))


def cone(prefix, remaining):
    states = {tuple(run(prefix, x)): x for x in itertools.product((0, 1), repeat=9)}
    for rank in range(9):
        pairs = {}
        for x in states:
            if sum(x) != 8 - rank:
                continue
            for c in range(9):
                if not x[c]:
                    y = x[:c] + (1,) + x[c + 1:]
                    if y in states:
                        pairs[c] = (states[x], states[y], x, y)
        if len(pairs) > 2 ** remaining:
            return dict(rank=rank, pairs=pairs)
    return None


def main():
    root = Path(__file__).parents[1]
    entry = next(x for x in json.loads((root / 'results/h9-feedback-next-fourths-combined.json').read_text())
                 if x['label'] == '(0,2)(1,6)(3,7)')
    thirds = {canonical(row['third']) for row in entry['rows']}
    layers = matchings(9)
    report = []
    for third in sorted(thirds):
        source = next(row for row in entry['rows'] if tuple(map(tuple, row['third'])) == third)
        outcomes = []
        for fourth in source['fourths']:
            prefix = (FIRST, SECOND, third, fourth)
            unique = {}
            for k in (4, 3, 2, 1):
                for p in placements(9, k):
                    row = prefix_state(prefix, p)
                    row['real_set'] = {i for i, s in enumerate(row['state']) if not s}
                    unique.setdefault((k, tuple(row['state']), tuple(row['gates'])), row)
            rows = list(unique.values())
            passing = [fifth for fifth in layers if witness(fifth, rows, 4) is None]
            ending = [dict(fifth=fifth, cone=cone(prefix + (fifth,), 2)) for fifth in passing]
            c4 = cone(prefix, 3)
            print('M', third, 'N',fourth,'C4',bool(c4),'fifths',len(ending),
                  'noC5',sum(x['cone'] is None for x in ending),flush=True)
            outcomes.append(dict(fourth=fourth, cone4=c4, endings=ending))
        report.append(dict(third=third, fourths=outcomes))
    (root / 'results/h9-feedback-round3-021637.json').write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    main()
