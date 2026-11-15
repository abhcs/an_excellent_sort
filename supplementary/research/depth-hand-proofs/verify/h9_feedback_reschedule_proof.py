#!/usr/bin/env python3
"""Directly verify the parameterized hand proof for H9 prefixes 02 14 3b."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
from netlib import matchings, run
from h9_feedback_commute import FIRST, classes
from h9_feedback_commute_proof import OLD_HAND, CASES

BASE = {
    5: ({1: 1, 3: 1}, {2: -1, 4: -1}, {0: -1, 5: 1}),
    6: ({1: 1, 3: 1}, {2: -1, 4: -1}, {1: 1, 2: -1}),
}
EXPECTED_PAIRS = {5: ((4, 5), (0, 1), (0, 5)), 6: ((4, 6), (0, 1), (0, 4))}
DUAL = (5, 4, 3, 2, 1, 0, 8, 7, 6)


def trace(prefix, p):
    state = [p.get(i, 0) for i in range(9)]
    labels = list(range(9))
    height = [0] * 9
    gates, snapshots, scheduled = [], [list(state)], []
    for layer in prefix:
        for a, b in layer:
            if state[a] == state[b] == 0:
                x, y = labels[a], labels[b]
                h = 1 + max(height[x], height[y])
                height[x] = height[y] = h
                gates.append((x, y))
                while len(scheduled) < h:
                    scheduled.append([])
                scheduled[h - 1].append((x, y))
            elif state[a] > state[b]:
                state[a], state[b] = state[b], state[a]
                labels[a], labels[b] = labels[b], labels[a]
        snapshots.append(list(state))
    for layer in scheduled:
        used = [i for edge in layer for i in edge]
        assert len(used) == len(set(used))
    return dict(placement=p, sentinel_states=snapshots, final_track_labels=labels,
                retained_gates=gates, schedule=scheduled,
                real_positions=[i for i, v in enumerate(state) if not v],
                physical_track_heights=[height[i] for i in labels])


def direct(prefix, certificate):
    p = certificate['placement']
    positions = [i for i in range(9) if i not in p]
    checked = 0
    for values in itertools.permutations(range(1, len(positions) + 1)):
        original = [0] * 9
        for i, value in zip(positions, values):
            original[i] = value
        for i, sign in p.items():
            original[i] = sign * 100
        actual = run(prefix, original)
        rescheduled = run(certificate['schedule'], original)
        state = certificate['sentinel_states'][-1]
        expected = [100 * state[i] if state[i] else rescheduled[certificate['final_track_labels'][i]]
                    for i in range(9)]
        assert actual == expected
        checked += 1
    return checked


def canonical_thirds(b):
    vertices = [i for i in range(9) if i not in (0, 4, b)]
    return {tuple(sorted(((4, b), *(tuple(sorted((vertices[a], vertices[c]))) for a, c in layer))))
            for layer in matchings(6, maximal=True)
            if (vertices.index(1), vertices.index(2)) not in layer}


def dual_layer(layer):
    return tuple(sorted(tuple(sorted((DUAL[a], DUAL[b]))) for a, b in layer))


def check():
    layers = matchings(9)
    known = OLD_HAND | {second for second, _ in CASES}
    representatives = {second for _, second in classes()}
    new = {((0, 2), (1, 4), (3, b)) for b in (5, 6)}
    assert new <= representatives and not new & known and len(known | new) == 23
    total_direct, records = 0, []
    for b in (5, 6):
        second = ((0, 2), (1, 4), (3, b))
        prefix = (FIRST, second)
        base = [trace(prefix, p) for p in BASE[b]]
        for certificate, pair in zip(base, EXPECTED_PAIRS[b]):
            assert len(certificate['retained_gates']) == 2 and len(certificate['schedule']) == 1
            assert tuple(i for i in range(9) if i not in certificate['real_positions']) == pair
            certificate['direct_permutation_checks'] = direct(prefix, certificate)
            total_direct += certificate['direct_permutation_checks']
        forced, survivors, reschedules = [], [], []
        canonical = canonical_thirds(b)
        assert len(canonical) == 12
        if b == 5:
            for layer in prefix:
                assert dual_layer(layer) == tuple(sorted(layer))
                assert all(DUAL[a] > DUAL[c] for a, c in layer)
        for third in layers:
            passes = all(sum(a in c['real_positions'] and d in c['real_positions'] for a, d in third) >= 3
                         for c in base)
            used = {i for edge in third for i in edge}
            alternative = len(third) == 4 and (
                (0 not in used and (4, b) in third) or
                ((5 if b == 5 else 4) not in used and (0, 1) in third))
            assert passes == alternative
            if not passes:
                continue
            forced.append(third)
            if b == 6 and 4 not in used:
                cert = trace((*prefix, third), {0: -1, 3: 1})
                assert len(cert['retained_gates']) == 4 and len(cert['schedule']) == 2
                cert['third_layer'] = third
                cert['reason'] = 'exclude_idle_4'
                cert['direct_permutation_checks'] = direct((*prefix, third), cert)
                total_direct += cert['direct_permutation_checks']
                reschedules.append(cert)
                continue
            normalized = dual_layer(third) if b == 5 and 5 not in used else tuple(third)
            if (1, 2) in normalized:
                cert = trace((*prefix, normalized), {3: 1, 4: -1})
                assert len(cert['retained_gates']) == 4 and len(cert['schedule']) == 2
                cert['third_layer'] = normalized
                cert['reason'] = 'exclude_12_after_optional_duality'
                cert['direct_permutation_checks'] = direct((*prefix, normalized), cert)
                total_direct += cert['direct_permutation_checks']
                reschedules.append(cert)
                continue
            assert normalized in canonical
            survivors.append((third, normalized))
        assert len(forced) == 30
        assert len(survivors) == (24 if b == 5 else 12)
        assert {normalized for _, normalized in survivors} == canonical
        finishing = []
        for third in sorted(canonical):
            partner = {a: c for a, c in third} | {c: a for a, c in third}
            t, u = partner[1], partner[2]
            assert t > 2 and u > 2 and t != u
            cert_p = trace((*prefix, third), {0: -1, 3: 1, 4: -1})
            cert_q = trace((*prefix, third), {2: 1, 3: 1, 4: -1})
            rp, rq = set(cert_p['real_positions']), set(cert_q['real_positions'])
            assert rp == set(range(9)) - {0, 1, b}
            assert rq == rp - {u} | {0} and len(rp & rq) == 5
            for cert in (cert_p, cert_q):
                assert len(cert['retained_gates']) == 2 and len(cert['schedule']) == 1
                cert['direct_permutation_checks'] = direct((*prefix, third), cert)
                total_direct += cert['direct_permutation_checks']
            assert not any(sum(a in rp and c in rp for a, c in fourth) == 3 and
                           sum(a in rq and c in rq for a, c in fourth) == 3 for fourth in layers)
            finishing.append(dict(third_layer=third, partner_of_1=t, partner_of_2=u,
                                  placement_p=cert_p, placement_q=cert_q,
                                  intersection=sorted(rp & rq)))
        records.append(dict(b=b, second_layer=second, base_certificates=base,
                            third_layers_checked=len(layers), path_alternatives_count=len(forced),
                            raw_surviving_thirds=len(survivors), canonical_thirds=len(canonical),
                            rescheduling_certificates=reschedules, finishing_certificates=finishing))
    return dict(new_classes=2, previously_covered=21, combined_hand_classes=23,
                direct_permutation_checks=total_direct,
                canonical_finishing_forms=24, cases=records,
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = check()
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'cases'}))
