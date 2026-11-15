#!/usr/bin/env python3
"""Explore sentinel restrictions whose first two retained layers commute."""
import itertools
import argparse
import re
from pathlib import Path

from netlib import matchings, placements

FIRST = ((0, 1), (2, 3), (4, 5))


def restriction(prefix, placement):
    state = [placement.get(i, 0) for i in range(9)]
    rails = list(range(9))
    retained = []
    for layer in prefix:
        edges = []
        for a, b in layer:
            if state[a] == state[b] == 0:
                edges.append((rails[a], rails[b]))
            elif state[a] > state[b]:
                state[a], state[b] = state[b], state[a]
                rails[a], rails[b] = rails[b], rails[a]
        retained.append(edges)
    edges = [edge for layer in retained for edge in layer]
    support = [i for edge in edges for i in edge]
    if len(set(support)) != len(support):
        return None
    return len(edges), tuple(state), retained


def constraints(second):
    out = {}
    for k in (1, 2):
        for p in placements(9, k):
            r = restriction((FIRST, second), p)
            if r is None:
                continue
            gates, state, retained = r
            minimum = {1: {3: 4, 4: 3}, 2: {2: 3, 3: 2}}[k].get(gates, 99)
            support = tuple(i for i, v in enumerate(state) if not v)
            key = (support, minimum)
            if key not in out:
                out[key] = dict(placement=p, retained=retained, state=state,
                                real_support=support, minimum=minimum)
    return list(out.values())


def classes():
    source = Path(__file__).parents[1] / 'h9.md'
    lines = source.read_text().split('## Appendix A:')[1].split('## Appendix B:')[0].splitlines()
    result = []
    for line in lines:
        if not line.startswith('| (') and not line.startswith('| empty '):
            continue
        label = line.split('|')[1].strip()
        second = tuple((int(a), int(b)) for a, b in re.findall(r'\((\d),(\d)\)', label))
        result.append((label, second))
    return result


def screen(details=False):
    layers = matchings(9)
    for label, second in classes():
        cons = constraints(second)
        passing = [m for m in layers if all(sum(a in c['real_support'] and b in c['real_support']
                                               for a, b in m) >= c['minimum'] for c in cons)]
        if cons:
            print(label, 'constraints', len(cons), 'thirds', len(passing))
            if not passing and details:
                for c in cons:
                    print(' ', c)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--details', action='store_true')
    screen(parser.parse_args().details)
