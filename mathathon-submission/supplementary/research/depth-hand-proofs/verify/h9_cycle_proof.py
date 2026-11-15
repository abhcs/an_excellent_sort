#!/usr/bin/env python3
"""Check the hand proof for the formerly open six-cycle H9 class.

The proof itself is h9-cycle-case.md: a three-colour invariant, forced
layer forms, and a nine-row table. Checks below validate those claims;
they are not assumptions in the proof and use no SAT solver.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

from netlib import matchings

FIRST = ( ((0, 1), (2, 3), (4, 5)), ((0, 3), (1, 4), (2, 5)) )
A, B, C = (0, 1, 2), (3, 4, 5), (6, 7, 8)
MINUS = (-1, -1, -1, 0, 0, 0, 0, 0, 0)
PLUS = (0, 0, 0, 1, 1, 1, 0, 0, 0)


def step(values, layer):
    result = list(values)
    count = sum(values[a] == values[b] == 0 for a, b in layer)
    for a, b in layer:
        result[a], result[b] = min(result[a], result[b]), max(result[a], result[b])
    return tuple(result), count


def trace(prefix, placement):
    current = tuple(placement.get(i, 0) for i in range(9))
    states, counts = [current], []
    for layer in prefix:
        current, count = step(current, layer)
        states.append(current)
        counts.append(count)
    return states, counts


def edge(a, b):
    return tuple(sorted((a, b)))


def normal_form(a, b, x, y, z):
    ap = tuple(i for i in A if i != a)
    bp = tuple(i for i in B if i != b)
    other_a = next(i for i in ap if i != x)
    third = tuple(sorted((ap, bp, (7, 8), (b, 6))))
    fourth = tuple(sorted((edge(a, x), edge(other_a, 15 - y), edge(b, y), edge(6, z))))
    return (*FIRST, third, fourth)


def table_row(a, b, x, y):
    U = {0: 1, 1: 1, 2: -1, 4: -1}
    V = {0: 1, 1: -1, 2: -1, 4: 1}
    W = {0: -1, 1: -1, 2: 1, 4: 1}
    if a == 0 and b in (3, 4):
        return 1, U, [0, 0, 1, 1]
    if a == 1 and b in (4, 5):
        return 2, V, [0, 0, 1, 1]
    if a == 2 and b in (3, 5):
        return 3, W, [0, 0, 1, 1]
    if (a, b) == (0, 5):
        if (x, y) == (2, 7):
            return 4, V, [0, 0, 1, 1]
        return 5, {0: 1, 2: -1, 4: 1, 7: 1}, [0, 1, 0, 1]
    if (a, b) == (1, 3):
        if (x, y) == (2, 7):
            return 6, U, [0, 0, 1, 1]
        return 7, {0: 1, 1: 1, 2: -1, 7: 1}, [1, 0, 0, 1]
    assert (a, b) == (2, 4)
    if (x, y) == (1, 7):
        return 8, U, [0, 0, 1, 1]
    return 9, {0: 1, 1: -1, 4: 1, 7: 1}, [1, 0, 0, 1]


def transform(prefix, permutation, dual=False):
    """Permute a generalized network and untangle, preserving layer sizes."""
    labels = list(permutation)
    result = []
    for layer in prefix:
        new = []
        for a, b in layer:
            low, high = (labels[b], labels[a]) if dual else (labels[a], labels[b])
            new.append(edge(low, high))
            if low > high:
                labels[a], labels[b] = labels[b], labels[a]
        result.append(tuple(sorted(new)))
    return tuple(result)


def canonicalize(prefix):
    prefix = tuple(tuple(sorted(layer)) for layer in prefix)
    _, count = step(MINUS, prefix[2])
    if count != 3:
        prefix = transform(prefix, (5, 4, 3, 2, 1, 0, 8, 7, 6), dual=True)
    assert prefix[:2] == FIRST and step(MINUS, prefix[2])[1] == 3
    crosses = [(a, b) for a, b in prefix[2] if a in B and b in C]
    assert len(crosses) == 1
    _, c = crosses[0]
    paired = sorted(set(C) - {c})
    labels = list(range(9))
    labels[c], labels[paired[0]], labels[paired[1]] = 6, 7, 8
    return transform(prefix, labels)


def invariant_check():
    checked = 0
    for n in range(2, 8):
        all_layers = matchings(n)
        for colours in itertools.product((-1, 0, 1), repeat=n):
            p = tuple(-1 if c == -1 else 0 for c in colours)
            q = tuple(1 if c == 1 else 0 for c in colours)
            for layer in all_layers:
                pp, _ = step(p, layer)
                qq, _ = step(q, layer)
                cc, _ = step(colours, layer)
                assert pp == tuple(-1 if c == -1 else 0 for c in cc)
                assert qq == tuple(1 if c == 1 else 0 for c in cc)
                assert sum(a == b == 0 for a, b in zip(pp, qq)) == colours.count(0)
                checked += 1
    return checked


def overlap_check():
    """Check intersection loss and real-comparison bounds, allowing overlap."""
    types = ((-1, 0), (0, 0), (0, 1), (-1, 1))
    checked = 0
    for n in range(2, 7):
        all_layers = matchings(n)
        for joint in itertools.product(types, repeat=n):
            p, q = tuple(zip(*joint))
            rp, rq = p.count(0), q.count(0)
            shared_real = joint.count((0, 0))
            shared_sentinel = joint.count((-1, 1))
            for layer in all_layers:
                pp, mp = step(p, layer)
                qq, mq = step(q, layer)
                h = sum({joint[a], joint[b]} == {(0, 0), (-1, 1)} for a, b in layer)
                assert sum(a == b == 0 for a, b in zip(pp, qq)) == shared_real - h
                assert sum(a == -1 and b == 1 for a, b in zip(pp, qq)) == shared_sentinel - h
                assert 2 * mp <= rp - h and 2 * mq <= rq - h
                if rp % 2 == rq % 2 == 0 and shared_real % 2 == 1:
                    assert 2 * mp != rp or 2 * mq != rq
                checked += 1
    return checked


def check():
    records = []
    for a, b in itertools.product(A, B):
        for x, y, z in itertools.product([i for i in A if i != a], (7, 8), [i for i in B if i != b]):
            prefix = normal_form(a, b, x, y, z)
            row, placement, expected = table_row(a, b, x, y)
            states, counts = trace(prefix, placement)
            assert counts == expected and [c for c in counts if c] == [1, 1]
            records.append(dict(parameters=dict(a=a, b=b, x=x, y=y, z=z), prefix=prefix,
                                table_row=row, placement=placement, states=states, retained_counts=counts))
    canonical = {tuple(tuple(layer) for layer in r['prefix']) for r in records}
    assert len(canonical) == 72
    all_layers = matchings(9)
    thirds, pairs, transformed = set(), 0, set()
    for third in all_layers:
        p3, pc = step(MINUS, third)
        q3, qc = step(PLUS, third)
        if sorted((pc, qc)) != [2, 3]:
            continue
        thirds.add(tuple(third))
        for fourth in all_layers:
            if set(third) & set(fourth):
                continue
            if step(p3, fourth)[1] != 5 - pc or step(q3, fourth)[1] != 5 - qc:
                continue
            normalized = canonicalize((*FIRST, third, fourth))
            assert normalized in canonical, (third, fourth, normalized)
            transformed.add(normalized)
            pairs += 1
    assert len(thirds) == 54 and pairs == 432 and transformed == canonical
    invariant_cases = invariant_check()
    overlap_cases = overlap_check()
    return dict(n=9, fixed_prefix=FIRST, canonical_prefixes=72, admissible_third_layers=54,
                admissible_layer_pairs=432, table_rows=9, invariant_checks=invariant_cases,
                overlap_checks=overlap_cases,
                all_reductions_verified=True, all_table_profiles_verified=True, certificates=records,
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = check()
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'certificates'}))
