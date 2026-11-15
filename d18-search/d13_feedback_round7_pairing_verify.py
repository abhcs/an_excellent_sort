#!/usr/bin/env python3
"""Exhaustive small-width controls for the interval pairing projection."""
import hashlib
import itertools
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent


def matchings(vertices):
    if not vertices:
        yield ()
        return
    x, *rest = vertices
    yield from matchings(rest)
    for y in rest:
        for tail in matchings([v for v in rest if v != y]):
            yield ((x, y),) + tail


def valid(edges):
    vertices = [v for e in edges for v in e]
    return len(vertices) == len(set(vertices)) and all(a < b for a, b in edges)


def mask(layer, windows):
    return sum(1 << i for i, (a, length) in enumerate(windows)
               if sum(a <= x < y < a+length for x, y in layer) >= length-2)


def dominate(layer, n):
    result = set(layer)
    starts = [a for a in range(n-3)
              if sum(a <= x < y < a+4 for x, y in layer) == 2]
    unions = []
    for a in starts:
        if unions and a <= unions[-1][1]:
            unions[-1][1] = a+3
        else:
            unions.append([a, a+3])
    fixed = set()
    for lo, hi in unions:
        assert (hi-lo+1) % 2 == 0
        inside = set(range(lo, hi+1))
        assert not any((x in inside) != (y in inside) for x, y in result)
        result = {e for e in result if not set(e) & inside}
        result |= {(x, x+1) for x in range(lo, hi, 2)}
        fixed |= inside
    result = {(a, b) for a, b in result if b-a <= 2}
    while any(b-a == 2 for a, b in result):
        i, _ = next(e for e in result if e[1]-e[0] == 2)
        assert not fixed & {i, i+1, i+2}
        partners = {v: w for a, b in result for v, w in ((a, b), (b, a))}
        j = partners.get(i+1)
        result.remove((i, i+2))
        if j is None:
            result.add((i, i+1))
        else:
            assert j in (i-1, i+3)
            result.remove(tuple(sorted((i+1, j))))
            result |= ({(i-1, i), (i+1, i+2)} if j == i-1 else
                       {(i, i+1), (i+2, i+3)})
        assert valid(result)
    assert valid(result) and all(b-a == 1 for a, b in result)
    return result


def downward(masks, count):
    feasible = bytearray(1 << count)
    for m in masks:
        feasible[m] = 1
    for m in range((1 << count)-1, -1, -1):
        if feasible[m]:
            for bit in range(count):
                if m >> bit & 1:
                    feasible[m ^ (1 << bit)] = 1
    return feasible


def main():
    started = time.monotonic()
    rows = []
    for n in range(3, 11):
        windows = [(a, length) for length in (3, 4) for a in range(n-length+1)]
        all_masks, adjacent_masks = set(), set()
        count = adjacent = 0
        for layer in matchings(list(range(n))):
            count += 1
            original = mask(layer, windows)
            changed = dominate(layer, n)
            assert not original & ~mask(changed, windows)
            all_masks.add(original)
            if all(b-a == 1 for a, b in layer):
                adjacent += 1
                adjacent_masks.add(original)
        arbitrary = downward(all_masks, len(windows))
        path = downward(adjacent_masks, len(windows))
        assert arbitrary == path
        rows.append(dict(n=n, arbitrary_matchings=count, adjacent_matchings=adjacent,
                         interval_families_checked=len(path), feasible_families=sum(path),
                         every_matching_constructively_dominated=True))
    supports = [{0, 1, 2, 3}, {0, 1, 2, 3}, {0, 1, 2}, {3, 4}, {2, 3, 4, 5}, {4, 5}]
    final_blocks = [{0, 1}, {2, 3}, {4, 5}]
    assert all(sum(bool(s & block) for block in final_blocks) <= 2 for s in supports)
    assert sum(supports[c] == (set(range(4)) if c < 2 else set(range(2, 6)))
               for c in (0, 1, 4, 5)) == 3
    counts = {}
    for n in (13, 18):
        triples = sum(len(range(max(0, a-1), min(n-1, a+3)+1)) for a in range(n-2))
        fours = 2*4*(n-3)
        matching = n-2
        assert triples+fours+matching == 14*n-38
        counts[n] = dict(variables=n-1, triple_clauses=triples,
                         full_four_clauses=fours, matching_clauses=matching,
                         total=triples+fours+matching)
    report = dict(status='VERIFIED', uses_sat=False, widths=rows,
                  total_arbitrary_matchings=sum(r['arbitrary_matchings'] for r in rows),
                  total_interval_families=sum(r['interval_families_checked'] for r in rows),
                  shared_middle_pair_separation_verified=True, endpoint_counts=counts,
                  seconds=time.monotonic()-started,
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  proof_sha256=hashlib.sha256((HERE / 'd13_feedback_round7_pairing.md').read_bytes()).hexdigest())
    (HERE / 'results/d13_feedback_round7-pairing-verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
