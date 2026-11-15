#!/usr/bin/env python3
"""Find incompatible six-real pairings after a commuting three-layer prefix."""
import itertools
import json
from pathlib import Path
from netlib import placements
from h9_feedback_commute import FIRST
from h9_feedback_reschedule_extend import prefix_state


def forced_sets(prefix):
    by_set = {}
    for p in placements(9, 3):
        row = prefix_state(prefix, p)
        if max(row['depths']) <= 1 and len(row['gates']) <= 2:
            mask = sum(1 << i for i, v in enumerate(row['state']) if not v)
            by_set.setdefault(mask, row)
    return by_set


def conflict(forced):
    for a, b in itertools.combinations(forced, 2):
        if (a & b).bit_count() % 2:
            return [forced[a], forced[b]]
    return None


def screen():
    root = Path(__file__).parents[1] / 'results'
    records = json.loads((root / 'h9-feedback-reschedule-screen.json').read_text())
    result = []
    for case in records:
        survivors, certificates = [], []
        for third in case['surviving_third_layers']:
            found = conflict(forced_sets([FIRST, case['second_layer'], third]))
            if found:
                certificates.append(dict(third=third, conflict=found))
            else:
                survivors.append(third)
        print(case['label'], case['surviving_count'], '->',len(survivors), flush=True)
        result.append(dict(label=case['label'], second_layer=case['second_layer'],
                           surviving_thirds=survivors, eliminated=certificates))
    (root / 'h9-feedback-reschedule-six.json').write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    screen()
