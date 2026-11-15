#!/usr/bin/env python3
"""Explore fourth-layer rescheduling and six-real pairing constraints."""
import argparse
import itertools
import json
from pathlib import Path
from netlib import matchings, placements, run
from h9_feedback_commute import FIRST
from h9_feedback_reschedule_extend import prefix_state


def compact_row(row):
    state, gates, last = row['state'], row['gates'], row['last']
    k = len(row['placement'])
    real = sum(1 << i for i, value in enumerate(state) if not value)
    critical = sum(1 << i for i, d in enumerate(row['depths']) if d == (2 if k == 3 else 3))
    sinks = tuple((1 << a) | (1 << b) for index, (a, b) in enumerate(gates) if last[a] == last[b] == index)
    return k, real, critical, tuple(sinks), len(gates), max(row['depths'])


def witness(layer_masks, records):
    for key, row in records:
        k, real, critical, sinks, total, height = key
        retained = [edge for edge in layer_masks if edge & real == edge]
        q = len(retained)
        if k == 4:
            if total + q <= 2:
                return row
            continue
        if k == 3:
            if height <= 2 and total + q <= 4 and all(not edge & critical for edge in retained):
                return row
            continue
        if height > 3 or any(edge & critical for edge in retained):
            continue
        touched = 0
        for edge in retained:
            touched |= edge
        untouched = sum(not edge & touched for edge in sinks)
        if total - untouched <= (6 if k == 1 else 4):
            return row
    return None


def image(prefix):
    return {tuple(run(prefix, bits)) for bits in itertools.product((0, 1), repeat=9)}


def screen(max_thirds, only=None, blind=False):
    root = Path(__file__).parents[1]
    entries = json.loads((root / 'results/h9-feedback-reschedule-six.json').read_text())
    blind_entries = {item['label']: {tuple(map(tuple, third)) for third in item['thirds']}
                     for item in json.loads((root / 'results/h9-feedback-next-blind.json').read_text())} if blind else {}
    layers = matchings(9)
    layer_masks = [tuple((1 << a) | (1 << b) for a, b in layer) for layer in layers]
    report = []
    for item in entries:
        thirds = item['surviving_thirds']
        if blind:
            thirds = [third for third in thirds if tuple(map(tuple, third)) in blind_entries[item['label']]]
        if not thirds or len(thirds) > max_thirds or only and item['label'] != only:
            continue
        prefix = [FIRST, item['second_layer']]
        states2 = image(prefix)
        viable = [third for third in thirds if all(any(s[a] > s[b] for s in states2) for a, b in third)]
        remaining = []
        for third in viable:
            full_prefix = prefix + [third]
            rows = [prefix_state(full_prefix, p) for k in (1, 2, 3, 4) for p in placements(9, k)]
            unique = {}
            for row in rows:
                key = compact_row(row)
                unique.setdefault(key, row)
            records = sorted(unique.items(), key=lambda pair: (pair[0][4], -pair[0][0]))
            states3 = image(full_prefix)
            allowed_pairs = {(a, b) for a, b in itertools.combinations(range(9), 2)
                             if any(s[a] > s[b] for s in states3)}
            fourths = [layer for layer, masks in zip(layers, layer_masks)
                       if all(edge in allowed_pairs for edge in layer) and witness(masks, records) is None]
            remaining.append(dict(third=third, fourth_count=len(fourths), fourths=fourths))
        output = dict(label=item['label'], second=item['second_layer'], input_thirds=len(thirds),
                      nonredundant_thirds=len(viable), surviving_thirds=sum(bool(x['fourths']) for x in remaining),
                      surviving_pairs=sum(x['fourth_count'] for x in remaining), rows=remaining)
        report.append(output)
        print({key: value for key, value in output.items() if key != 'rows'}, flush=True)
    target = root / ('results/h9-feedback-next-fourths-combined.json' if blind else 'results/h9-feedback-next-fourths.json')
    target.write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--max-thirds', type=int, default=60)
    parser.add_argument('--only')
    parser.add_argument('--blind', action='store_true')
    args = parser.parse_args()
    screen(args.max_thirds, args.only, args.blind)
