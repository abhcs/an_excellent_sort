#!/usr/bin/env python3
"""Verify the displayed hand proof for H9 second layer 03 14 26."""
import argparse
import hashlib
import json
from pathlib import Path

from netlib import matchings
from h9_feedback_commute import FIRST, classes
from h9_feedback_commute_proof import OLD_HAND, CASES
from h9_feedback_reschedule_proof import trace, direct

SECOND = ((0, 3), (1, 4), (2, 6))
BASE = (({1: 1, 3: 1}, (3, 4)), ({1: 1, 2: -1}, (2, 4)), ({3: 1, 4: -1}, (1, 3)))


def check():
    known = OLD_HAND | {second for second, _ in CASES} | {((0, 2), (1, 4), (3, b)) for b in (5, 6)}
    assert len(known) == 23 and SECOND not in known
    assert SECOND in {second for _, second in classes()}
    prefix = (FIRST, SECOND)
    base, direct_total = [], 0
    for placement, deleted in BASE:
        cert = trace(prefix, placement)
        assert len(cert['retained_gates']) == 2 and len(cert['schedule']) == 1
        assert tuple(i for i in range(9) if i not in cert['real_positions']) == deleted
        cert['direct_permutation_checks'] = direct(prefix, cert)
        direct_total += cert['direct_permutation_checks']
        base.append(cert)
    blind = trace(prefix, {0: -1, 2: -1, 4: -1})
    assert blind['retained_gates'] == [] and blind['real_positions'] == list(range(3, 9))
    blind['direct_permutation_checks'] = direct(prefix, blind)
    direct_total += blind['direct_permutation_checks']
    layers = matchings(9)
    path_forms, final_forms, blind_checks = [], [], []
    for third in layers:
        passes = all(sum(a in row['real_positions'] and b in row['real_positions'] for a, b in third) >= 3
                     for row in base)
        used = {i for edge in third for i in edge}
        expected = len(third) == 4 and ((4 not in used and (1, 3) in third) or
                                       (3 not in used and (2, 4) in third))
        assert passes == expected
        if not passes:
            continue
        path_forms.append(third)
        blind3 = trace((*prefix, third), {0: -1, 2: -1, 4: -1})
        count = len(blind3['retained_gates'])
        expected_survivor = ((4 not in used and (0, 2) in third) or
                             (3 not in used and (0, 1) in third))
        assert (count >= 2) == expected_survivor
        blind_checks.append(dict(third=third, real_comparators=count))
        if count < 2:
            continue
        cert = trace((*prefix, third), {2: -1, 4: -1})
        assert [len(layer) for layer in cert['schedule']] == [3, 1]
        assert cert['retained_gates'][:2] == [(0, 1), (0, 3)]
        assert {i for edge in cert['retained_gates'][2:] for i in edge} == {5, 6, 7, 8}
        cert['third_layer'] = third
        cert['direct_permutation_checks'] = direct((*prefix, third), cert)
        direct_total += cert['direct_permutation_checks']
        final_forms.append(cert)
    assert len(path_forms) == 30 and len(final_forms) == 6
    expected_thirds = {tuple(sorted((*fixed, *((a + 5, b + 5) for a, b in k))))
                       for fixed in (((0, 2), (1, 3)), ((0, 1), (2, 4)))
                       for k in matchings(4, maximal=True)}
    assert {tuple(row['third_layer']) for row in final_forms} == expected_thirds
    return dict(status='VERIFIED', new_classes=1, previous_hand_classes=23,
                combined_hand_classes=24, second_layer=SECOND,
                third_layers_checked=len(layers), path_forms=30, final_forms=6,
                direct_permutation_checks=direct_total, base_certificates=base,
                blind_prefix=blind, blind_third_counts=blind_checks,
                rescheduling_certificates=final_forms,
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = check()
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items()
                      if key not in ('base_certificates', 'blind_prefix', 'blind_third_counts', 'rescheduling_certificates')}))
