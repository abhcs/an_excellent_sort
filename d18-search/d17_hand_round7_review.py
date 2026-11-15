#!/usr/bin/env python3
"""Independent normalization/count/core review of the round7 case606 proof."""
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


def matchings(vertices):
    if not vertices:
        yield ()
        return
    x, *rest = vertices
    yield from matchings(rest)
    for y in rest:
        for tail in matchings([v for v in rest if v != y]):
            yield ((x, y),) + tail


def pairings(count):
    if count % 2:
        return 0
    answer = 1
    for k in range(count-1, 0, -2):
        answer *= k
    return answer


def main():
    source = OUT / 'd17-feedback-fourteen-hand606-states.json'
    base = [s[2:] for s in json.loads(source.read_text())['states']]
    def incomparable(a, b):
        return any(s[a] < s[b] for s in base) and any(s[a] > s[b] for s in base)
    pairs = [p for p in itertools.combinations(range(12), 2) if incomparable(*p)]
    fours = [p for p in itertools.combinations(range(12), 4)
             if all(incomparable(a, b) for a, b in itertools.combinations(p, 2))]
    assert len(pairs) == 23 and len(fours) == 6
    assert not any(all(incomparable(a, b) for a, b in itertools.combinations(p, 2))
                   for p in itertools.combinations(range(12), 5))
    assert incomparable(5, 8)
    antichains = [()] + pairs + fours
    counts, zero = {}, {}
    for idle in [()] + pairs:
        for external in antichains:
            if set(idle) & set(external):
                continue
            remaining = set(range(12)) - set(idle) - set(external)
            key = str((len(idle)//2, 12+len(external)))
            total = pairings(len(remaining))
            if {5, 8} <= remaining:
                total -= pairings(len(remaining)-2)
            counts[key] = counts.get(key, 0) + total
            a = len(remaining & set(range(5)))
            b = len(remaining) - a
            internal_b = pairings(b)
            if {5, 8} <= remaining:
                internal_b -= pairings(b-2)
            zero[key] = zero.get(key, 0) + pairings(a)*internal_b
    assert sum(counts.values()) == 86370 and sum(zero.values()) == 2700

    # Independently corroborate the hand full-row core necessity on its
    # three canonical noncritical B transports, rather than merely checking
    # that the proposed core is sufficient.
    # Common pair is0,1; q,a,b,c,d,e,r are2,...,8.
    bsets = ({2, 3, 4}, {2, 4, 5}, {2, 5, 7}, {8, 5, 7}, {2, 4, 6})
    expected_core = {(0, 1), (2, 4), (5, 7)}
    all_last = list(matchings(list(range(9))))
    assert len(all_last) == 2620
    static = []
    for label, first in (('none', []), ('de', [(6, 7)]), ('dr', [(6, 8)])):
        sets = []
        for bset in bsets:
            state = [(-1 if v in (2, 3, 4) else 1) if v in bset | {0, 1} else 0
                     for v in range(9)]
            for a, b in first:
                state[a], state[b] = min(state[a], state[b]), max(state[a], state[b])
            sets.append({v for v, value in enumerate(state) if value})
        satisfying = [layer for layer in all_last
                      if all(sum(set(edge) <= s for edge in layer) >= 2 for s in sets)]
        assert satisfying and all(expected_core <= set(layer) for layer in satisfying)
        static.append(dict(transport=label, partial_matchings_checked=2620,
                           satisfying_matchings=len(satisfying), unique_forced_core=sorted(expected_core)))

    checker_path = HERE / 'd17_feedback_round7_check.py'
    spec = importlib.util.spec_from_file_location('round7_independent_review_checker', checker_path)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    with tempfile.TemporaryDirectory(prefix='d17-round7-review-') as temporary:
        checker.ROOT = Path(temporary)
        (checker.ROOT / 'results').mkdir()
        checker.main()
        replay = json.loads((checker.ROOT / 'results/d17-feedback-round7-core-check.json').read_text())
    assert replay['status'] == 'VERIFIED'
    assert replay['case_counts'] == counts and replay['zero_cross_cases'] == sum(zero.values())
    result = dict(status='REVIEWED_SOUND', uses_sat=False,
                  hand_normalization_review='Full-family comparability preserves deficit and cannot create dc; normalized idles are variable incomparable pairs; external antichains have even size0/2/4.',
                  full_family_incomparable_pairs=23, full_family_four_antichains=6,
                  no_five_antichain=True, critical_pair_incomparable=True,
                  independent_double_factorial_counts=counts,
                  independent_zero_cross_counts=zero,
                  static_full_row_necessity_controls=static,
                  independent_checker_replay=replay,
                  finite_arithmetic_verification_remains_a_premise=True,
                  pure_hand_global_lower_bound_claimed=False, substantive_gaps=[],
                  reviewed_scope='Case606 full twenty-state two-layer peak obstruction, arbitrary extra common reals; odd-width padding and fixed-sentinel/global-flip extensions are sound under their stated hypotheses.',
                  source_sha256=sha(Path(__file__)),
                  reduction_sha256=sha(HERE / 'd17_feedback_round7_reduction.md'),
                  certificate_sha256=sha(OUT / 'd17-feedback-round7-core-certificate.json.gz'))
    (OUT / 'd17-hand-round7-review.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'independent_checker_replay'}, indent=2))


if __name__ == '__main__':
    main()
