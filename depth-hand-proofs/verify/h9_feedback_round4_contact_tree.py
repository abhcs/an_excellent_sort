#!/usr/bin/env python3
"""Construct transparent contact proof trees, branching only on stated clauses."""
import itertools
import json
from functools import lru_cache
from pathlib import Path


def edge(a, b):
    return tuple(sorted((a, b)))


def build(record, pivot):
    forbidden = set(map(tuple, record['fourth']))
    clauses = [frozenset(e for e in itertools.combinations(row['real'], 2)
                         if set(e) & set(row['sink']) and e not in forbidden)
               for row in record['rows']]
    u, v = pivot
    pivot_rows = [i for i, row in enumerate(record['rows']) if set(row['sink']) == {u, v}]
    options = []
    for a, b in itertools.product([None, *sorted(set(range(9)) - {u, v})], repeat=2):
        if a is not None and a == b:
            continue
        chosen = frozenset(([edge(u, a)] if a is not None else []) + ([edge(v, b)] if b is not None else []))
        if chosen & forbidden or any(not chosen & clauses[i] for i in pivot_rows):
            continue
        idle = frozenset(([u] if a is None else []) + ([v] if b is None else []))
        options.append((a, b, chosen, idle))

    @lru_cache(None)
    def search(initial, idle):
        chosen = set(initial)
        forced = []
        while True:
            blocked = {v for e in chosen for v in e} | set(idle)
            remaining = []
            for i, clause in enumerate(clauses, 1):
                if clause & chosen:
                    continue
                available = sorted(e for e in clause if not set(e) & blocked)
                if not available:
                    return dict(forced=forced, empty=i)
                remaining.append((len(available), i, available))
            if not remaining:
                return dict(forced=forced, template=sorted(chosen), idle=sorted(idle))
            _, row, available = min(remaining)
            if len(available) == 1:
                forced.append((row, available[0]))
                chosen.add(available[0])
            else:
                break
        children = [dict(edge=e, proof=search(frozenset(chosen | {e}), idle)) for e in available]
        return dict(forced=forced, split=row, children=children)

    branches = [dict(partners=(a, b), proof=search(chosen, idle)) for a, b, chosen, idle in options]
    def size(node):
        return 1 + sum(size(x['proof']) for x in node.get('children', []))
    return dict(pivot=pivot, pivot_rows=[i + 1 for i in pivot_rows], branches=branches,
                nodes=sum(size(x['proof']) for x in branches), states=search.cache_info().currsize)


def main():
    root = Path(__file__).parents[1]
    data = json.loads((root / 'results/h9-feedback-round4-endings.json').read_text())
    output = []
    for record in data:
        candidates = []
        for pivot in map(tuple, record['fourth']):
            if sum(tuple(row['sink']) == pivot for row in record['rows']) >= 2:
                candidates.append(build(record, pivot))
        best = min(candidates, key=lambda x: (x['nodes'], len(x['branches'])))
        print(record['case'], record['number'], 'pivot', best['pivot'], 'branches', len(best['branches']),
              'nodes', best['nodes'], 'states', best['states'], flush=True)
        output.append(dict(case=record['case'], number=record['number'], fourth=record['fourth'], **best))
    (root / 'results/h9-feedback-round4-contact-trees.json').write_text(json.dumps(output, indent=2) + '\n')


if __name__ == '__main__':
    main()
