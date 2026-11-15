#!/usr/bin/env python3
"""Explore the 06 78 case using prefix-image symmetry and small restrictions."""
import itertools
import json
from pathlib import Path
from h9_feedback_next_screen import compact_row, witness, image
from h9_feedback_reschedule_extend import prefix_state
from h9_feedback_commute import FIRST
from netlib import matchings, placements

SECOND = ((0, 6), (7, 8))
PAIRS = ((2, 3), (4, 5), (7, 8))


def permutations():
    for target in itertools.permutations(PAIRS):
        for swap in (False, True):
            p = list(range(9))
            p[1], p[6] = (6, 1) if swap else (1, 6)
            for s, t in zip(PAIRS, target):
                p[s[0]], p[s[1]] = t
            yield p


def canonical(third):
    return min(tuple(sorted(tuple(sorted((p[a], p[b]))) for a, b in third)) for p in permutations())


def screen():
    layers = matchings(9)
    masks = [tuple((1 << a) | (1 << b) for a, b in layer) for layer in layers]
    thirds = sorted({canonical(layer) for layer in layers if len(layer) == 4
                     and not any(0 in edge for edge in layer) and not set(layer) & set(PAIRS)})
    out = []
    for third in thirds:
        prefix = (FIRST, SECOND, third)
        rows = [prefix_state(prefix, p) for k in (1, 2, 3, 4) for p in placements(9, k)]
        unique = {}
        for row in rows:
            unique.setdefault(compact_row(row), row)
        records = list(unique.items())
        remaining = {i for i, m in enumerate(masks) if witness(m, records) is None}
        states = image(prefix)
        forbidden = [edge for edge in itertools.combinations(range(9), 2) if all(s[edge[0]] <= s[edge[1]] for s in states)]
        valid = {i for i, layer in enumerate(layers) if not set(layer) & set(forbidden)}
        print(third, 'unrestricted_left', len(remaining), 'nonredundant', len(remaining & valid), flush=True)
        # Greedily compress the explanation for all nonredundant fourth layers.
        cover = [(sum(1 << i for i in valid if witness(masks[i], [record])), record)
                 for record in records]
        left = sum(1 << i for i in valid)
        chosen = []
        while left:
            bitset, (key, row) = max(cover, key=lambda pair: (pair[0] & left).bit_count())
            gain = (bitset & left).bit_count()
            if not gain:
                break
            chosen.append(dict(key=key, placement=row['placement'], state=row['state'],
                               gates=row['gates'], depths=row['depths'], gain=gain))
            left &= ~bitset
        print(' chosen', chosen, flush=True)
        out.append(dict(third=third, forbidden=forbidden, unrestricted_survivors=[layers[i] for i in sorted(remaining)],
                        chosen=chosen, uncovered=left.bit_count()))
    target = Path(__file__).parents[1] / 'results/h9-feedback-next-p9.json'
    target.write_text(json.dumps(out, indent=2) + '\n')


if __name__ == '__main__':
    screen()
