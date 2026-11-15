#!/usr/bin/env python3
"""Explicit short common suffixes for 79 half-blind families at width 18.

These are partial-task witnesses, not 18-wire sorting networks. This shows why
the half-blind restrictions alone cannot settle their two-layer prefix cases.
The two small sorters are from B. Dobbelaere's public sorting-network table:
https://bertdobbelaere.github.io/sorting_networks.html (10/31/7 and 12/40/8).
Both are independently verified below on all binary inputs.
"""
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path

from two_layer_cover import half_blind_family, type_step
from two_real_graph import images, run_bits, sorted_bits

NET10 = [
    [(0,1),(2,5),(3,6),(4,7),(8,9)],
    [(0,6),(1,8),(2,4),(3,9),(5,7)],
    [(0,2),(1,3),(4,5),(6,8),(7,9)],
    [(0,1),(2,7),(3,5),(4,6),(8,9)],
    [(1,2),(3,4),(5,6),(7,8)],
    [(1,3),(2,4),(5,7),(6,8)],
    [(2,3),(4,5),(6,7)],
]
NET12 = [
    [(0,8),(1,7),(2,6),(3,11),(4,10),(5,9)],
    [(0,2),(1,4),(3,5),(6,8),(7,10),(9,11)],
    [(0,1),(2,9),(4,7),(5,6),(10,11)],
    [(1,3),(2,7),(4,9),(8,10)],
    [(0,1),(2,3),(4,5),(6,7),(8,9),(10,11)],
    [(1,2),(3,5),(6,8),(9,10)],
    [(2,4),(3,6),(5,8),(7,9)],
    [(1,2),(3,4),(5,6),(7,8),(9,10)],
]


def cube(state):
    positions = [i for i, x in enumerate(state) if x == 0]
    fixed = sum(1 << i for i, x in enumerate(state) if x == 1)
    for bits in itertools.product((0, 1), repeat=len(positions)):
        yield fixed | sum(bit << i for i, bit in zip(positions, bits))


def main():
    for n, net in ((10, NET10), (12, NET12)):
        assert len(images(n, net)) == n + 1
    here = Path(__file__).resolve().parent
    source = here / 'prefixes/complete18.jsonl'
    cases = [json.loads(line) for line in source.read_text().splitlines()]
    records = []
    for case in cases:
        prefix = case['layers']
        states = [type_step(s, prefix[1]) for s in half_blind_family(18, prefix).values()]
        minus = [i for i in range(18) if all(s[i] == -1 for s in states)]
        plus = [i for i in range(18) if all(s[i] == 1 for s in states)]
        core = [i for i in range(18) if i not in minus + plus]
        if len(core) > 12:
            continue
        order = minus + core + plus
        labels = [order.index(i) for i in range(18)]
        mapped = [sorted((labels[a], labels[b]) for a, b in layer) for layer in prefix]
        assert all(a < b for layer in mapped for a, b in layer)
        start = len(minus)
        width = 10 if len(core) <= 10 else 12
        if len(core) == 11 and start:
            start -= 1  # Include one fixed negative infinity in the 12-wire sorter.
        small = NET10 if width == 10 else NET12
        suffix = [[(a + start, b + start) for a, b in layer] for layer in small]
        family = half_blind_family(18, mapped)
        assert len(family) == len(states)
        inputs = set()
        for placement in family.values():
            after = type_step(placement, mapped[1])
            assert all(x == -1 for x in after[:start])
            assert all(x == 1 for x in after[start + width:])
            inputs.update(cube(after))
        assert all(run_bits(suffix, x) == sorted_bits(18, x.bit_count()) for x in inputs)
        whole = mapped + suffix
        full_outputs = images(18, whole)
        assert len(full_outputs) > 19
        records.append(dict(case_id=case['case_id'], family_size=len(family), core_width=len(core),
                            depth=len(whole), input_labels=labels, network=whole,
                            checked_family_binary_inputs=len(inputs), full_output_count=len(full_outputs),
                            scope='Sorts every half-blind restriction, not all 18-wire inputs'))
    assert len(records) == 79
    result = dict(cover_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  cases=len(records), core_width_counts=dict(sorted(Counter(x['core_width'] for x in records).items())),
                  witnesses=records)
    target = here / 'results/coupled-family-witnesses18.json'
    target.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'witnesses'}), flush=True)


if __name__ == '__main__':
    main()
