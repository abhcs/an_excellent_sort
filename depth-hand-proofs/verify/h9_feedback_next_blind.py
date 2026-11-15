#!/usr/bin/env python3
"""Combine the earlier rescheduling screen with blind 5/6-real restrictions."""
import json
from pathlib import Path
from netlib import placements, run
from h9_feedback_commute import FIRST
from h9_feedback_reschedule_extend import prefix_state


def screen():
    root = Path(__file__).parents[1]
    data = json.loads((root / 'results/h9-feedback-reschedule-screen.json').read_text())
    out = []
    for item in data:
        prefix = (FIRST, item['second_layer'])
        constraints = {}
        for k in (3, 4):
            for p in placements(9, k):
                row = prefix_state(prefix, p)
                if not row['gates']:
                    real = tuple(i for i, value in enumerate(row['state']) if not value)
                    constraints.setdefault((real, 5 - k), p)
        passing = [third for third in item['surviving_third_layers']
                   if all(sum(a in real and b in real for a, b in third) >= minimum
                          for real, minimum in constraints)]
        result = dict(label=item['label'], second=item['second_layer'], constraints=len(constraints),
                      old_third_count=item['surviving_count'], new_third_count=len(passing), thirds=passing)
        out.append(result)
        print({key: value for key, value in result.items() if key != 'thirds'}, flush=True)
    (root / 'results/h9-feedback-next-blind.json').write_text(json.dumps(out, indent=2) + '\n')


if __name__ == '__main__':
    screen()
