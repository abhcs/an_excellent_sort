#!/usr/bin/env python3
"""Independent review checks for the critical two-idle reduction; no SAT."""
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def incomparable(a, b, states):
    return any(s[a] < s[b] for s in states) and any(s[a] > s[b] for s in states)


def main():
    source = OUT / 'd17-feedback-fourteen-hand606-states.json'
    supplied = json.loads(source.read_text())['states']
    assert len(supplied) == 20 and all(len(s) == 14 and s[:2] == [0, 0] for s in supplied)
    states = [s[2:] for s in supplied]
    # Physical order is D,A,B,C,E,d,a,b,c,q,e,r.
    rows = ({1, 2}, {2, 3}, {3, 4}, {0, 2})
    columns = ({9, 6, 7}, {9, 7, 8}, {9, 8, 10}, {11, 8, 10}, {9, 7, 5})
    negative = {1, 2, 6, 7, 9}
    exact = [[(-1 if v in negative else 1) if v in (r | c) else 0
              for v in range(12)] for r in rows for c in columns]
    assert exact == states
    selected = [s for i, s in enumerate(states) if i % 5 in (1, 2, 3)]
    aa = [list(p) for p in itertools.combinations(range(5), 2) if incomparable(*p, states)]
    assert aa == [[0, 3], [0, 4]]
    noncritical_b = (6, 7, 9, 10, 11)
    assert all(not incomparable(a, b, states) for a, b in itertools.combinations(noncritical_b, 2))
    for s in states:
        assert s[9] <= s[7] <= s[6] <= 0 <= s[11] <= s[10]
    mixed_full = [(a, b) for a in range(5) for b in noncritical_b if incomparable(a, b, states)]
    mixed_selected = [(a, b) for a in range(5) for b in noncritical_b if incomparable(a, b, selected)]
    assert len(mixed_full) == 12 and len(mixed_selected) == 10
    assert set(mixed_full) - set(mixed_selected) == {(1, 6), (2, 6)}
    antichains = [p for p in itertools.combinations(range(12), 4)
                  if all(incomparable(a, b, states) for a, b in itertools.combinations(p, 2))]
    assert antichains and all(5 in p for p in antichains)

    cert_path = OUT / 'd17-feedback-round6-core-certificate.json'
    certificate = json.loads(cert_path.read_text())
    path_rows = cross_metadata = 0
    for record in certificate['cases']:
        n, first = record['n'], record['M']
        assert record['cross'] == sum(a in range(5) and b in noncritical_b for a, b in first)
        cross_metadata += 1
        family = [s + [0] * (n - 12) for s in states]
        required = {}
        for i, initial in enumerate(family):
            if sum(initial[a] == initial[b] == 0 for a, b in first) >= n//2 - 3:
                continue
            transported = initial[:]
            for a, b in first:
                transported[a], transported[b] = min(transported[a], transported[b]), max(transported[a], transported[b])
            required[i] = {v for v, value in enumerate(transported) if value}
            assert len(required[i]) == 5
        full_rows = [r for r in range(4) if all(5*r+c in required for c in (1, 2, 3))]
        assert len(full_rows) >= 2
        for r in full_rows:
            sets = [required[5*r+c] for c in (1, 2, 3)]
            fixed = set.intersection(*sets)
            assert len(fixed) == 3
            q, = (sets[0] & sets[1]) - fixed
            e, = (sets[1] & sets[2]) - fixed
            b, = sets[0] - fixed - {q}
            tail, = sets[2] - fixed - {e}
            assert len({q, e, b, tail}) == 4 and not (fixed & {q, e, b, tail})
            assert sets == [fixed | {q, b}, fixed | {q, e}, fixed | {e, tail}]
            path_rows += 1

    # Execute the independent checker unchanged, redirecting only its report
    # directory; the original certificate and state source remain read-only.
    checker_path = HERE / 'd17_feedback_round6_check.py'
    spec = importlib.util.spec_from_file_location('critical_two_idle_review_checker', checker_path)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    with tempfile.TemporaryDirectory(prefix='d17-round6-review-') as temporary:
        checker.ROOT = Path(temporary)
        (checker.ROOT / 'results').mkdir()
        checker.main()
        replay = json.loads((checker.ROOT / 'results/d17-feedback-round6-core-check.json').read_text())
    assert replay['status'] == 'VERIFIED' and replay['canonical_cases'] == 1584
    result = dict(status='REVIEWED_SOUND', uses_sat=False,
                  exact_twenty_state_family_verified=True, aa_incomparable_pairs=aa,
                  mixed_idle_pairs_full_family=len(mixed_full),
                  mixed_idle_pairs_selected_family=len(mixed_selected),
                  selected_only_comparable_pairs=[[1, 6], [2, 6]],
                  four_coordinate_antichains=len(antichains), all_contain_critical_d=True,
                  full_rows_with_distinct_path_coordinates=path_rows,
                  cross_metadata_records_checked=cross_metadata,
                  independent_checker_replay=replay,
                  substantive_gaps=[],
                  prose_note='Section2 should say every USED A vertex other than C has unchanged status; D changes status but is idle.',
                  checker_hardening_note='The review explicitly checked four distinct path coordinates and cross-count metadata for the actual certificate.',
                  finite_certificate_remains_a_premise=True,
                  source_sha256=sha(Path(__file__)),
                  reduction_sha256=sha(HERE / 'd17_feedback_round6_reduction.md'),
                  certificate_sha256=sha(cert_path), input_sha256=sha(source))
    (OUT / 'd17-hand-round6-review.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'independent_checker_replay'}, indent=2))


if __name__ == '__main__':
    main()
