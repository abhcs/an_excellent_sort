#!/usr/bin/env python3
"""Explore fourth-layer constraints after the three-layer rescheduling screen."""
import json
from pathlib import Path
from netlib import matchings, placements
from h9_feedback_commute import FIRST


def prefix_state(prefix, p):
    state = [p.get(i, 0) for i in range(9)]
    labels = list(range(9))
    depths = [0] * 9
    last = [-1] * 9
    gates = []
    for layer in prefix:
        for a, b in layer:
            if state[a] == state[b] == 0:
                x, y = labels[a], labels[b]
                last[x] = last[y] = len(gates)
                depths[x] = depths[y] = 1 + max(depths[x], depths[y])
                gates.append((x, y))
            elif state[a] > state[b]:
                state[a], state[b] = state[b], state[a]
                labels[a], labels[b] = labels[b], labels[a]
    # Express all information at the physical boundary: later RR gates use these wires.
    inverse = {label: wire for wire, label in enumerate(labels)}
    return dict(placement=p, state=state, depths=[depths[t] for t in labels],
                last=[last[t] for t in labels], gates=[(inverse[x], inverse[y]) for x, y in gates])


def fourth_witness(layer, rows):
    for row in rows:
        k = len(row['placement'])
        state, depths, last, gates = row['state'], row['depths'], row['last'], row['gates']
        extra = [(a, b) for a, b in layer if state[a] == state[b] == 0]
        total = len(gates) + len(extra)
        if k == 4:
            if total <= 2:
                return row
            continue
        h = max([0, *depths, *(1 + max(depths[a], depths[b]) for a, b in extra)])
        if k == 3:
            if h <= 2 and total <= 4:
                return row
            continue
        if h > 3:
            continue
        touched = {i for edge in extra for i in edge}
        sinks = len(extra) + sum(last[a] == last[b] == index and a not in touched and b not in touched
                                 for index, (a, b) in enumerate(gates))
        if total - sinks <= (6 if k == 1 else 4):
            return row
    return None


def screen():
    second = ((0, 2), (1, 4), (3, 6))
    source = Path(__file__).parents[1] / 'results/h9-feedback-reschedule-screen.json'
    entry = next(item for item in json.loads(source.read_text()) if item['label'] == '(0,2)(1,4)(3,6)')
    layers = matchings(9)
    outputs = []
    for third in entry['surviving_third_layers']:
        prefix = [FIRST, second, third]
        rows = [prefix_state(prefix, p) for k in (1, 2, 3, 4) for p in placements(9, k)]
        # Five-real placements often refute most fourth layers immediately.
        rows.sort(key=lambda row: (len(row['gates']), -len(row['placement'])))
        survivors = [fourth for fourth in layers if fourth_witness(fourth, rows) is None]
        print(third, 'fourths', len(survivors), flush=True)
        outputs.append(dict(third=third, fourth_count=len(survivors), fourths=survivors))
    target = Path(__file__).parents[1] / 'results/h9-feedback-reschedule-fourths.json'
    target.write_text(json.dumps(outputs, indent=2) + '\n')


if __name__ == '__main__':
    screen()
