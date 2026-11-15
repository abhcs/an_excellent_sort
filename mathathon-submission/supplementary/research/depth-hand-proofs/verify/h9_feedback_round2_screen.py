#!/usr/bin/env python3
"""Bounded discovery for the 03 12 46 case; no SAT calls."""
import itertools
import json
from pathlib import Path
from netlib import matchings, placements, run
from h9_feedback_reschedule_extend import prefix_state

FIRST = ((0, 1), (2, 3), (4, 5))
SECOND = ((0, 3), (1, 2), (4, 6))


def dag(gates):
    last = [-1] * 9
    pred = []
    heights = []
    for a, b in gates:
        p = {last[a], last[b]} - {-1}
        pred.append(sum(1 << i for i in p))
        heights.append(1 + max((heights[i] for i in p), default=0))
        last[a] = last[b] = len(pred) - 1
    return pred, max(heights, default=0)


def layers_left(gates, discard):
    pred, height = dag(gates)
    mask = (1 << len(gates)) - 1
    for _ in range(discard):
        nonsinks = 0
        for i, p in enumerate(pred):
            if mask & (1 << i):
                nonsinks |= p
        mask &= nonsinks
    return mask.bit_count(), height


def witness(layer, rows, prefix_length):
    for row in rows:
        k = len(row['placement'])
        real = row['real_set']
        extra = [(a, b) for a, b in layer if a in real and b in real]
        target_depth, first_two_min = ((5, 3) if k == 4 else (5, 5) if k == 3
                                      else (6, 5) if k == 2 else (6, 7))
        compressed = target_depth - (7 - prefix_length - 1)
        left, height = layers_left(row['gates'] + extra, compressed - 2)
        if height <= compressed and left < first_two_min:
            return row
    return None


def screen():
    root = Path(__file__).parents[1]
    data = json.loads((root / 'results/h9-feedback-next-fourths-combined.json').read_text())
    entry = next(x for x in data if x['label'] == '(0,3)(1,2)(4,6)')
    layers = matchings(9)
    report = []
    for subcase in entry['rows']:
        third = subcase['third']
        for fourth in subcase['fourths']:
            prefix = [FIRST, SECOND, third, fourth]
            unique = {}
            for k in (4, 3, 2, 1):
                for p in placements(9, k):
                    row = prefix_state(prefix, p)
                    row['real_set'] = set(i for i, s in enumerate(row['state']) if not s)
                    key = (k, tuple(row['state']), tuple(row['gates']))
                    unique.setdefault(key, row)
            rows = list(unique.values())
            survivors = []
            explanations = {}
            for fifth in layers:
                found = witness(fifth, rows, 4)
                if found is None:
                    survivors.append(fifth)
                else:
                    key = tuple(sorted(found['placement'].items()))
                    explanations[key] = explanations.get(key, 0) + 1
            states = [run(prefix, x) for x in itertools.product((0, 1), repeat=9)]
            valid = [layer for layer in survivors if all(any(s[a] > s[b] for s in states) for a, b in layer)]
            print('fourth', fourth, 'rows', len(rows), 'survivors',len(survivors),'nonredundant',len(valid), flush=True)
            report.append(dict(third=third, fourth=fourth, fifths=survivors, nonredundant=valid,
                               explanations=[dict(placement=dict(p), count=count) for p, count in explanations.items()]))
    (root / 'results/h9-feedback-round2-screen.json').write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    screen()
