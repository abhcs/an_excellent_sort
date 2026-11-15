#!/usr/bin/env python3
"""Independent enumeration checks for the cover and half-blind family theorem."""
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'depth-hand-proofs/verify'))
from netlib import matchings, placements
from two_layer_cover import (family_count, half_blind_family, network,
                             reflection, sentences, signature, type_step)


def direct_states(n, prefix):
    result = set()
    for assignment in placements(n, n // 2):
        current = tuple(assignment.get(i, 0) for i in range(n))
        for layer in prefix:
            if any(current[a] == current[b] == 0 for a, b in layer):
                break
            current = type_step(current, layer)
        else:
            result.add(current)
    return result


def main():
    # Raw graph orbits, saturated graph orbits, and reflection orbits from
    # Table 3, arXiv:1412.5302. These are checks, not the coverage proof.
    published = {
        3: (4, 2, 1), 4: (8, 2, 2), 5: (16, 6, 4), 6: (20, 6, 5),
        7: (52, 14, 8), 8: (61, 15, 12), 9: (165, 37, 22),
        10: (152, 27, 21), 11: (482, 88, 48), 12: (414, 70, 50),
        13: (1378, 212, 117), 14: (1024, 136, 94), 15: (3780, 494, 262),
        16: (2627, 323, 211), 17: (10187, 1149, 609), 18: (6422, 651, 411),
    }
    for n, expected in published.items():
        actual = (len(sentences(n, False, False)), len(sentences(n, True, False)), len(sentences(n)))
        assert actual == expected, (n, actual, expected)
    print('all 48 published class counts agree, n=3..18', flush=True)

    checked = 0
    ternary = 0
    for n in range(3, 11):
        first = [(2 * i, 2 * i + 1) for i in range(n // 2)]
        found = set()
        for second in matchings(n):
            prefix = [first, second]
            sentence = signature(n, *prefix)
            found.add(sentence)
            assert signature(n, *network(sentence)) == sentence
            reflected = [[tuple(sorted((n - 1 - a, n - 1 - b))) for a, b in layer]
                         for layer in prefix]
            assert signature(n, *reflected) == reflection(sentence)
            family = half_blind_family(n, prefix)
            assert len(family) == family_count(sentence)
            if n % 4 == 2:
                assert len(family) >= 2
            if n <= 7:
                actual_states = {type_step(x, second) for x in family.values()}
                assert actual_states == direct_states(n, prefix)
                ternary += 1
            checked += 1
        assert found == set(sentences(n, False, False)), n
        print(f'n={n}: all matchings covered and family formula verified', flush=True)

    for n in range(3, 19):
        for sentence in sentences(n):
            prefix = network(sentence)
            assert signature(n, *prefix) == sentence
            family = half_blind_family(n, prefix)
            assert len(family) == family_count(sentence)
            if n % 4 == 2:
                assert len(family) >= 2
    print(f'{checked} labelled prefixes checked; {ternary} independently checked over all signed placements', flush=True)
    print('all generated saturated representatives through n=18 satisfy the family theorem', flush=True)


if __name__ == '__main__':
    main()
