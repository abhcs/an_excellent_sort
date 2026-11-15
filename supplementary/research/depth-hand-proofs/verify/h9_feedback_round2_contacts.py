#!/usr/bin/env python3
"""Discover short contact cores for four 4+3+2 merger starts."""
import itertools
import json
import random
from pathlib import Path
from netlib import placements, matchings
from h9_feedback_reschedule_extend import prefix_state

PREFIX = (((0, 1), (2, 3), (4, 5)), ((0, 3), (1, 2), (4, 6)),
          ((0, 1), (2, 3), (5, 6), (7, 8)))
FOURTHS = (
    ((1, 7), (2, 4), (3, 6), (5, 8)),
    ((1, 7), (2, 6), (3, 4), (5, 8)),
    ((1, 8), (2, 4), (3, 6), (5, 7)),
    ((1, 8), (2, 6), (3, 4), (5, 7)),
)


def main():
    layers = matchings(9)
    allmask = (1 << len(layers)) - 1
    rng = random.Random(5638)
    output = []
    for fourth in FOURTHS:
        prefix = PREFIX + (fourth,)
        rows = {}
        for p in placements(9, 4):
            row = prefix_state(prefix, p)
            if len(row['gates']) != 3 or max(row['depths']) > 3:
                continue
            real = frozenset(i for i, s in enumerate(row['state']) if not s)
            for j, (a, b) in enumerate(row['gates']):
                if row['last'][a] == row['last'][b] == j:
                    rows.setdefault((real, frozenset((a, b))), row)
        items = list(rows.items())
        covers = []
        for (real, sink), row in items:
            cover = sum(1 << j for j, layer in enumerate(layers)
                        if not any(a in real and b in real and bool({a, b} & sink) for a, b in layer))
            covers.append(cover)
        best = list(range(len(items)))
        assert (lambda x: x)(allmask) == __import__('functools').reduce(int.__or__, covers, 0)
        for _ in range(500):
            order = list(range(len(items)))
            rng.shuffle(order)
            core = order[:]
            for index in order:
                union = 0
                for other in core:
                    if other != index:
                        union |= covers[other]
                if union == allmask:
                    core.remove(index)
            if len(core) < len(best):
                best = sorted(core)
        core = []
        for index in best:
            (real, sink), row = items[index]
            core.append(dict(real=sorted(real), sink=sorted(sink), placement=row['placement'],
                             gates=row['gates'], depths=row['depths']))
        print('N', fourth, 'clauses',len(items),'core',len(core),flush=True)
        print(json.dumps(core),flush=True)
        output.append(dict(fourth=fourth, core=core))
    target = Path(__file__).parents[1]/'results/h9-feedback-round2-contacts.json'
    target.write_text(json.dumps(output, indent=2)+'\n')


if __name__ == '__main__':
    main()
