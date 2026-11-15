#!/usr/bin/env python3
"""Exact integer closure of monotonicity and the proved two-layer recurrence.

The three seed levels distinguish hand results, the local H9 computation,
and published computer-assisted depth bounds. This does not search for or
claim new seed values. Output includes a checkable derivation for every n.
"""
import argparse
import json
from pathlib import Path


SEEDS = {
    'hand': {1: 0, 2: 1, 3: 3, 5: 5, 7: 6, 9: 7},
    'local': {1: 0, 2: 1, 3: 3, 5: 5, 7: 6, 9: 7, 11: 8},
    'published': {1: 0, 2: 1, 3: 3, 5: 5, 7: 6, 9: 7, 11: 8, 13: 9, 17: 10},
}


def closure(limit, level):
    seeds = SEEDS[level]
    out = {}
    for n in range(1, limit + 1):
        choices = []
        if n in seeds:
            choices.append((seeds[n], 'seed', None))
        if n > 1:
            choices.append((out[n - 1]['lower_bound'], 'monotonicity', n - 1))
        if n >= 3:
            parent = (n + 1) // 2
            choices.append((out[parent]['lower_bound'] + 2, 'two-layer restriction', parent))
        value, rule, parent = max(choices, key=lambda x: x[0])
        out[n] = dict(lower_bound=value, rule=rule, parent=parent)
    return out


def check(rows, level):
    rows = {int(n): row for n, row in rows.items()}
    for n, row in rows.items():
        n = int(n)
        value, rule, parent = row['lower_bound'], row['rule'], row['parent']
        if rule == 'seed':
            assert SEEDS[level][n] == value and parent is None
        elif rule == 'monotonicity':
            assert parent == n - 1 and rows[parent]['lower_bound'] == value
        else:
            assert rule == 'two-layer restriction' and n >= 3
            assert parent == (n + 1) // 2 and rows[parent]['lower_bound'] + 2 == value


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--limit', type=int, default=128)
    ap.add_argument('--out', type=Path)
    args = ap.parse_args()
    result = {level: closure(args.limit, level) for level in SEEDS}
    for level, rows in result.items():
        check(rows, level)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2) + '\n')
    print('n | hand | local H9 | published seeds')
    previous = None
    for n in range(1, args.limit + 1):
        values = tuple(result[level][n]['lower_bound'] for level in SEEDS)
        if values != previous:
            print(f'{n} | ' + ' | '.join(map(str, values)))
            previous = values


if __name__ == '__main__':
    main()
