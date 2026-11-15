#!/usr/bin/env python3
"""The fourteen possible local states before a normalized two-layer ending.

See two-layer-capacity-proofs.md for the proof. This restricts individual
states, not the number of states in a whole weight level.
"""
import argparse
import itertools
import json
from pathlib import Path

from two_real_graph import matchings, run_bits
from two_layer_topology import adjacent_matchings, normal_last_two
from two_layer_profiles import accepted_inputs


def allows(n, x):
    assert 0 <= x < 1 << n
    zeros = n - x.bit_count()
    bit = lambda k: 0 if k < 0 else 1 if k >= n else (x >> k) & 1
    if any(bit(k) for k in range(zeros - 3)):
        return False
    if any(not bit(k) for k in range(zeros + 3, n)):
        return False
    return not ((bit(zeros - 3) and bit(zeros - 2)) or
                (not bit(zeros + 1) and not bit(zeros + 2)))


def verify_certificate(record):
    n, prefix = record['n'], record['prefix']
    for layer in prefix:
        used = set()
        for a, b in layer:
            assert 0 <= a < b < n and a not in used and b not in used
            used.update((a, b))
    assert 0 <= record['input'] < 1 << n
    assert run_bits(prefix, record['input']) == record['output']
    assert not allows(n, record['output'])
    return True


def check():
    checked, states = 0, 0
    seen_middle = set()
    for n in range(2, 10):
        for first in matchings(n):
            for last in adjacent_matchings(n):
                if not normal_last_two(n, first, last):
                    continue
                accepted = accepted_inputs(n, [first, last])
                assert all(allows(n, x) for x in accepted), (n, first, last)
                checked += 1
                states += len(accepted)
                if n == 6:
                    seen_middle.update(x for x in accepted if x.bit_count() == 3)
    expected = {sum(1 << i for i in positions) for positions in itertools.combinations(range(6), 3)}
    expected = {x for x in expected if allows(6, x)}
    assert seen_middle == expected and len(expected) == 14
    return dict(normal_endings_checked=checked, accepted_states_checked=states,
                allowed_middle_words=[''.join(str(x >> i & 1) for i in range(6)) for x in sorted(expected)],
                scope='all normal endings of widths 2 through 9; the proof is width independent')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--certificate', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = check() if args.check else dict(valid=verify_certificate(json.loads(args.certificate.read_text())))
    if args.out:
        args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
