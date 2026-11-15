#!/usr/bin/env python3
"""Screen H9 third layers using three-layer real-track rescheduling."""
import argparse
import json
from pathlib import Path

from netlib import matchings, placements
from h9_feedback_commute import FIRST, classes
from h9_feedback_commute_proof import OLD_HAND, CASES


def restriction(second, placement):
    state = [placement.get(i, 0) for i in range(9)]
    tracks = list(range(9))
    depths = [0] * 9
    retained = []
    for layer in (FIRST, second):
        for a, b in layer:
            if state[a] == state[b] == 0:
                x, y = tracks[a], tracks[b]
                depths[x] = depths[y] = 1 + max(depths[x], depths[y])
                retained.append((x, y))
            elif state[a] > state[b]:
                state[a], state[b] = state[b], state[a]
                tracks[a], tracks[b] = tracks[b], tracks[a]
    return dict(placement=placement, state=state, retained=retained,
                real_mask=sum(1 << i for i, value in enumerate(state) if not value),
                depth2_mask=sum(1 << i for i, t in enumerate(tracks) if not state[i] and depths[t] == 2),
                cap=(6 if len(placement) == 1 else 4) - len(retained))


def constraints(second):
    records = {}
    for k in (1, 2):
        for placement in placements(9, k):
            item = restriction(second, placement)
            if item['cap'] < 0:
                continue
            key = (item['real_mask'], item['depth2_mask'], item['cap'])
            records.setdefault(key, item)
    return list(records.values())


def witness(layer_masks, records):
    for item in records:
        real, deep, cap = item['real_mask'], item['depth2_mask'], item['cap']
        retained = [edge for edge in layer_masks if edge & real == edge]
        if len(retained) <= cap and all(not edge & deep for edge in retained):
            return item
    return None


def screen():
    layers = matchings(9)
    masks = [tuple((1 << a) | (1 << b) for a, b in layer) for layer in layers]
    known = OLD_HAND | {second for second, _ in CASES}
    records = []
    for label, second in classes():
        if second in known:
            continue
        cons = constraints(second)
        passing = [layer for layer, layer_masks in zip(layers, masks) if witness(layer_masks, cons) is None]
        item = dict(second_layer=second, label=label, constraints=len(cons), surviving_third_layers=passing,
                    surviving_count=len(passing))
        records.append(item)
        print(label, 'constraints', len(cons), 'thirds', len(passing), flush=True)
    return records


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = screen()
    if args.out:
        args.out.write_text(json.dumps(result, indent=2) + '\n')
