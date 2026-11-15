#!/usr/bin/env python3
"""Exact last-two-layer completion by rank blocks and a path dynamic program.

Input sets must be full binary images of standard comparator prefixes.
The proof is in two-layer-capacity-proofs.md. No SAT or exponential search
over suffix orientations is used once the prefix image is available.
"""
import argparse
import itertools
import json
from pathlib import Path
import time

from two_real_graph import (components, edges_and_examples, images,
                            images_with_witness, matchings, run_bits, sorted_bits)
from two_layer_topology import adjacent_matchings, matching_blocks, normal_last_two


def profile(n, values):
    counts = [0] * (n + 1)
    for x in values:
        counts[n - x.bit_count()] += 1
    return counts


def rank_blocks(counts):
    cuts = [i for i, count in enumerate(counts) if count == 1]
    assert cuts[0] == 0 and cuts[-1] == len(counts) - 1 and all(counts)
    return list(zip(cuts, cuts[1:]))


def reverse_layer(values, layer):
    result = set()
    for x in values:
        choices = [x]
        for a, b in layer:
            left, right = (x >> a) & 1, (x >> b) & 1
            if left > right:
                choices = []
                break
            if left < right:
                choices += [y ^ (1 << a) ^ (1 << b) for y in choices]
        result.update(choices)
    return result


def accepted_inputs(n, suffix):
    values = {sorted_bits(n, w) for w in range(n + 1)}
    for layer in reversed(suffix):
        values = reverse_layer(values, layer)
    return values


def path_patterns(n):
    if n == 1:
        return [dict(last=[], blocks=[(0,)], capacity=[1, 1])]
    results = []
    for start in (0, 1):
        last = [(a, a + 1) for a in range(start, n - 1, 2)]
        blocks, _ = matching_blocks(n, last)
        assert all(len(block) == 2 for block in blocks[1:-1])
        capacity = [1] * (n + 1)
        if len(blocks) == 1:
            capacity[1] = 2
        else:
            for index, block in enumerate(blocks):
                if len(block) == 2:
                    capacity[block[0] + 1] = 3 if index in (0, len(blocks) - 1) else 5
                if index + 1 < len(blocks):
                    capacity[block[-1] + 1] = 2
        results.append(dict(last=last, blocks=blocks, capacity=capacity))
    return results


def capacity_patterns(n):
    result = [p['capacity'] for p in path_patterns(n)]
    if n == 4:
        result.append([1, 4, 4, 4, 1])
    return result


def profile_test(counts):
    failures = []
    for left, right in rank_blocks(counts):
        observed = counts[left:right + 1]
        patterns = capacity_patterns(right - left)
        if not any(all(a <= b for a, b in zip(observed, candidate)) for candidate in patterns):
            failures.append(dict(block=[left, right], observed=observed, capacity_patterns=patterns))
    return dict(rules_out_two_layers=bool(failures), failures=failures)


def short_certificate(n, prefix):
    """Six-run level-cap or ten-run heavy-neighbor certificate, when available."""
    sources = images_with_witness(n, prefix)
    levels = [[] for _ in range(n + 1)]
    for x in sorted(sources):
        levels[n - x.bit_count()].append(x)
    kind, needed = None, None
    for z, level in enumerate(levels):
        if len(level) > 5:
            kind, needed = 'LEVEL_CAP', {z: 6}
            break
    if needed is None:
        for start in range(1, n - 3):
            if not all(len(levels[z]) >= 2 for z in range(start, start + 4)):
                continue
            heavy = next((z for z in range(start, start + 3)
                          if len(levels[z]) >= 3 and len(levels[z + 1]) >= 3), None)
            if heavy is not None:
                kind = 'HEAVY_NEIGHBORS'
                needed = {z: 3 if z in (heavy, heavy + 1) else 2 for z in range(start, start + 4)}
                break
    if needed is None:
        return None
    runs = [dict(input=sources[x], output=x) for z, count in needed.items() for x in levels[z][:count]]
    result = dict(n=n, prefix=prefix, obstruction=kind, runs=runs)
    verify_short_certificate(result)
    return result


def verify_short_certificate(record):
    n, prefix = record['n'], record['prefix']
    for layer in prefix:
        used = set()
        for a, b in layer:
            assert 0 <= a < b < n and a not in used and b not in used
            used.update((a, b))
    outputs = set()
    for row in record['runs']:
        assert 0 <= row['input'] < 1 << n and 0 <= row['output'] < 1 << n
        assert run_bits(prefix, row['input']) == row['output']
        outputs.add(row['output'])
    counts = profile(n, outputs)
    if record['obstruction'] == 'LEVEL_CAP':
        assert max(counts) >= 6
    else:
        assert record['obstruction'] == 'HEAVY_NEIGHBORS'
        assert any(all(counts[z] >= 2 for z in range(start, start + 4))
                   and any(counts[z] >= 3 and counts[z + 1] >= 3 for z in range(start, start + 3))
                   for start in range(1, n - 3))
    return True


def port(block, choice, side):
    if len(block) == 1:
        return block[0]
    return block[choice if side == 'left' else 1 - choice]


def try_path(n, values, pattern):
    blocks = pattern['blocks']
    domains = [range(len(block)) for block in blocks]
    states = {choice: [choice] for choice in domains[0]}
    relations = []
    for index in range(len(blocks) - 1):
        cut = blocks[index][-1] + 1
        prefix_mask = (1 << cut) - 1
        deficits = [(x, (x & prefix_mask).bit_count() - max(0, x.bit_count() - (n - cut)))
                    for x in values]
        allowed = []
        for a, b in itertools.product(domains[index], domains[index + 1]):
            u = port(blocks[index], a, 'right')
            v = port(blocks[index + 1], b, 'left')
            if all(deficit == int(bool(x >> u & 1) and not (x >> v & 1)) for x, deficit in deficits):
                allowed.append((a, b))
        relations.append(dict(cut=cut, allowed=allowed))
        nxt = {}
        for a, b in allowed:
            if a in states:
                nxt.setdefault(b, states[a] + [b])
        states = nxt
        if not states:
            return None, relations
    choices = next(iter(states.values()))
    first = [(port(blocks[i], choices[i], 'right'), port(blocks[i + 1], choices[i + 1], 'left'))
             for i in range(len(blocks) - 1)]
    suffix = [first, pattern['last']]
    assert all(run_bits(suffix, x) == sorted_bits(n, x.bit_count()) for x in values)
    return suffix, relations


def complete(n, values):
    """Full prefix image -> exact completion, including small cycle components."""
    started = time.monotonic()
    values = set(values)
    counts = profile(n, values)
    records, suffix = [], [[], []]
    for left, right in rank_blocks(counts):
        size = right - left
        local = {(x >> left) & ((1 << size) - 1) for x in values}
        observed = counts[left:right + 1]
        assert profile(size, local) == observed
        attempts = []
        found = None
        for pattern in path_patterns(size):
            if not all(a <= b for a, b in zip(observed, pattern['capacity'])):
                attempts.append(dict(kind='path', last=pattern['last'], capacity=pattern['capacity'], status='PROFILE_EXCLUDED'))
                continue
            candidate, relations = try_path(size, local, pattern)
            attempts.append(dict(kind='path', last=pattern['last'], capacity=pattern['capacity'],
                                 status='SAT' if candidate else 'EMPTY_PATH_RELATION', relations=relations))
            if candidate is not None:
                found = candidate
                break
        if found is None and size == 4:
            for first in [[(0, 2), (1, 3)], [(0, 3), (1, 2)]]:
                candidate = [first, [(0, 1), (2, 3)]]
                sorts = all(run_bits(candidate, x) == sorted_bits(size, x.bit_count()) for x in local)
                attempts.append(dict(kind='cycle', first=first, status='SAT' if sorts else 'FAILING_INPUT'))
                if sorts:
                    found = candidate
                    break
        records.append(dict(block=[left, right], profile=observed, attempts=attempts))
        if found is None:
            return dict(status='UNSAT', profile=counts, components=records, seconds=time.monotonic() - started)
        for layer in range(2):
            suffix[layer].extend((a + left, b + left) for a, b in found[layer])
    assert all(run_bits(suffix, x) == sorted_bits(n, x.bit_count()) for x in values)
    return dict(status='SAT', suffix=suffix, profile=counts, components=records, seconds=time.monotonic() - started)


def maximum_capacities(n):
    maxima = [1]
    for size in range(1, n + 1):
        maxima.append(max(max(sum(p) for p in capacity_patterns(part)) + maxima[size - part] - 1
                          for part in range(1, size + 1)))
    return maxima


def check():
    suffixes = 0
    for n in range(2, 9):
        for last in adjacent_matchings(n):
            for first in matchings(n):
                if not normal_last_two(n, first, last):
                    continue
                accepted = accepted_inputs(n, [first, last])
                direct = {x for x in range(1 << n) if run_bits([first, last], x) == sorted_bits(n, x.bit_count())}
                assert accepted == direct
                cuts = components(n, list(first) + list(last))
                expected = [1]
                for group in cuts:
                    left, right = group[0], group[-1] + 1
                    local_first = [(a - left, b - left) for a, b in first if a in group]
                    local_last = [(a - left, b - left) for a, b in last if a in group]
                    local_profile = profile(len(group), accepted_inputs(len(group), [local_first, local_last]))
                    assert local_profile in capacity_patterns(len(group))
                    expected.extend(local_profile[1:])
                assert expected == profile(n, accepted)
                suffixes += 1
    prefixes = positives = 0
    for n in (3, 4, 5):
        layers = matchings(n)
        if n == 5:
            networks = ([[ (0, 1), (2, 3)], a, b] for a, b in itertools.product(layers, repeat=2))
        else:
            networks = itertools.chain.from_iterable(itertools.product(layers, repeat=d) for d in range(4))
        for prefix in networks:
            values = images(n, prefix)
            blocks = [list(range(a, b)) for a, b in rank_blocks(profile(n, values))]
            assert blocks == components(n, edges_and_examples(n, values))
            reference = any(len({run_bits([a, b], x) for x in values}) == n + 1 for a in layers for b in layers)
            result = complete(n, values)
            assert result['status'] == ('SAT' if reference else 'UNSAT'), (n, prefix, result)
            prefixes += 1
            positives += reference
    maxima = maximum_capacities(64)
    assert all(maxima[n] == 7 * n // 2 - 3 for n in range(17, 65))
    return dict(normal_suffixes=suffixes, unrestricted_prefix_checks=prefixes, completable=positives,
                maximum_capacities_through_32=maxima[1:33], large_width_formula_checked_through=64)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--network', type=Path)
    parser.add_argument('--prefix-depth', type=int)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.check:
        result = check()
    elif args.network:
        record = json.loads(args.network.read_text())
        prefix = record.get('prefix', record.get('network', record.get('layers')))
        if args.prefix_depth is not None:
            prefix = prefix[:args.prefix_depth]
        result = complete(record['n'], images(record['n'], prefix))
        result.update(n=record['n'], prefix=prefix)
    else:
        parser.error('choose --check or --network')
    if args.out:
        args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
