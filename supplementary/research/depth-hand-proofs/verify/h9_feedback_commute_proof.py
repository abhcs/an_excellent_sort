#!/usr/bin/env python3
"""Verify the three displayed hand certificates in h9_feedback_commute.md."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

from netlib import matchings, run
from h9_feedback_commute import FIRST, classes, constraints

CASES = (
    (((0, 3), (6, 7)), (
        ({0: -1}, ((2, 3), (4, 5), (6, 7)), (0,)),
        ({3: 1}, ((0, 1), (4, 5), (6, 7)), (3,)),
    )),
    (((0, 6), (1, 7)), (
        ({0: -1}, ((2, 3), (4, 5), (1, 7)), (0,)),
        ({1: 1}, ((2, 3), (4, 5), (0, 6)), (7,)),
    )),
    (((0, 3), (4, 6), (5, 7)), (
        ({0: -1, 4: -1}, ((2, 3), (5, 7)), (0, 4)),
        ({0: -1, 5: 1}, ((2, 3), (4, 6)), (0, 7)),
        ({3: 1, 4: -1}, ((0, 1), (5, 7)), (3, 4)),
        ({3: 1, 5: 1}, ((0, 1), (4, 6)), (3, 7)),
    )),
)

# h9.md section 7: two initial cases, seven in section 7.3,
# eight from P7, and the separately proved six-cycle class.
OLD_HAND = {
    (), ((6, 7),),
    ((0, 2),), ((0, 3),), ((0, 2), (1, 4)), ((0, 2), (1, 5)),
    ((0, 3), (1, 2)), ((0, 3), (1, 4)), ((0, 6),),
    ((0, 2), (1, 3)), ((0, 2), (1, 6)), ((0, 3), (4, 6)),
    ((0, 3), (1, 6)), ((0, 6), (3, 7)), ((0, 6), (2, 7)),
    ((0, 2), (4, 6)), ((0, 2), (5, 6)),
    ((0, 3), (1, 4), (2, 5)),
}


def trace(second, placement):
    state = [placement.get(i, 0) for i in range(9)]
    tracks = list(range(9))
    retained, states = [], [tuple(state)]
    for layer in (FIRST, second):
        current = []
        for a, b in layer:
            if state[a] == state[b] == 0:
                current.append((tracks[a], tracks[b]))
            elif state[a] > state[b]:
                state[a], state[b] = state[b], state[a]
                tracks[a], tracks[b] = tracks[b], tracks[a]
        retained.append(current)
        states.append(tuple(state))
    return states, tracks, retained


def direct_checks(second, placement, retained, tracks, state):
    """Compare full prefix with one merged layer plus fixed track routing."""
    real_inputs = [i for i in range(9) if i not in placement]
    checked = 0
    for values in itertools.permutations(range(1, len(real_inputs) + 1)):
        original = [0] * 9
        for i, value in zip(real_inputs, values):
            original[i] = value
        for i, sign in placement.items():
            original[i] = sign * 100
        actual = run((FIRST, second), original)
        merged = run((retained,), original)
        expected = [state[i] * 100 if state[i] else merged[tracks[i]] for i in range(9)]
        assert actual == expected, (second, placement, original, actual, expected)
        checked += 1
    return checked


def check():
    all_layers = matchings(9)
    representatives = {second for _, second in classes()}
    assert len(representatives) == 50 and len(OLD_HAND) == 18
    assert OLD_HAND <= representatives
    new = {second for second, _ in CASES}
    assert len(new) == 3 and new <= representatives and not new & OLD_HAND
    records, total_direct = [], 0
    for second, rows in CASES:
        checks, constraints_for_rows = [], []
        for placement, retained, sentinel_positions in rows:
            states, tracks, retained_layers = trace(second, placement)
            flat = tuple(pair for layer in retained_layers for pair in layer)
            assert flat == retained
            support = [i for pair in retained for i in pair]
            assert len(support) == len(set(support))
            assert tuple(i for i, value in enumerate(states[-1]) if value) == sentinel_positions
            assert len(retained) == 4 - len(placement)
            minimum = 5 - len(placement)
            constraints_for_rows.append((set(sentinel_positions), minimum))
            direct = direct_checks(second, placement, retained, tracks, states[-1])
            total_direct += direct
            checks.append(dict(placement=placement, retained_layers=retained_layers,
                               sentinel_states=states, final_track_labels=tracks,
                               sentinel_positions=sentinel_positions,
                               required_real_comparators_in_third=minimum,
                               direct_permutation_checks=direct))
        passing_counts = []
        candidates = all_layers
        for deleted, minimum in constraints_for_rows:
            candidates = [layer for layer in candidates
                          if sum(a not in deleted and b not in deleted for a, b in layer) >= minimum]
            passing_counts.append(len(candidates))
        assert not candidates
        records.append(dict(second_layer=second, certificates=checks,
                            third_layers_checked=len(all_layers),
                            sequential_remaining_third_layers=passing_counts))

    # Check the deletion-pair lemma directly for every matching and pair,
    # including matchings with fewer than four edges.
    pairs = list(itertools.combinations(range(9), 2))
    deletion_checks = 0
    for layer in all_layers:
        used = {i for pair in layer for i in pair}
        for a, b in pairs:
            surviving = sum(a not in edge and b not in edge for edge in layer)
            if len(layer) == 4:
                idle = next(iter(set(range(9)) - used))
                assert (surviving >= 3) == (idle in (a, b) or (a, b) in layer)
            elif len(layer) == 3:
                assert (surviving >= 3) == (a not in used and b not in used)
            else:
                assert surviving < 3
            deletion_checks += 1
    screened_out = set()
    for label, second in classes():
        cons = constraints(second)
        passing = any(all(sum(a in c['real_support'] and b in c['real_support'] for a, b in layer)
                          >= c['minimum'] for c in cons) for layer in all_layers)
        if not passing:
            screened_out.add(second)
    assert screened_out - OLD_HAND == new
    assert total_direct == 181440
    return dict(new_classes=3, old_hand_classes=18, combined_hand_classes=21,
                total_second_layer_classes=50, direct_permutation_checks=total_direct,
                matching_deletion_checks=deletion_checks,
                commuting_screen_total_excluded=len(screened_out),
                commuting_screen_new_excluded=sorted(screened_out - OLD_HAND),
                cases=records, source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = check()
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'cases'}))
