#!/usr/bin/env python3
"""Check restriction transport and certify a limit of pure layer blinding.

This uses finite enumeration and matching sampling, not SAT. The resulting
third-layer witnesses are NOT sorting-network witnesses: they show that no
half-width sentinel placement blinds all three layers of that prefix.
"""
import argparse
from collections import Counter
import hashlib
import itertools
import json
import math
from pathlib import Path
import random

from two_layer_cover import (components, family_count, half_blind_family,
                             network, sentences, type_step)


def real_mask(state):
    return sum(1 << i for i, x in enumerate(state) if x == 0)


def real_comparators(mask, layer):
    return sum((mask >> a & 1) and (mask >> b & 1) for a, b in layer)


def random_matching(n, rng):
    order = list(range(n))
    rng.shuffle(order)
    return sorted(tuple(sorted(order[i:i + 2])) for i in range(0, n - 1, 2))


def stick_chain(word):
    """Consecutive independent sets on the alternating path: 0^j 1^(m-j)."""
    m = len(word) // 2
    prefix = network((('S', word),))
    chain = []
    for j in range(m + 1):
        before = [0] * (2 * m)
        for i in range(m):
            a, b = 2 * i, 2 * i + 1
            left, right = (a, b) if word[2 * i:2 * i + 2] == '12' else (b, a)
            sentinel = right if i < j else left
            before[sentinel] = -1 if sentinel == a else 1
        assert real_comparators(real_mask(before), prefix[0]) == 0
        assert real_comparators(real_mask(before), prefix[1]) == 0
        chain.append(type_step(before, prefix[1]))
    assert len({real_mask(s) for s in chain}) == m + 1
    assert set(map(real_mask, chain)) == set(half_blind_family(2 * m, prefix))
    return chain


def check_transport(a, b, layer):
    # Sorting a pair is nonexpansive in L1. Equal zero counts then bound
    # how many real positions and real-real comparators can differ.
    distance = sum(abs(x - y) for x, y in zip(a, b))
    after_a, after_b = type_step(a, layer), type_step(b, layer)
    new_distance = sum(abs(x - y) for x, y in zip(after_a, after_b))
    assert new_distance <= distance
    mask_a, mask_b = real_mask(a), real_mask(b)
    exchange = (mask_a ^ mask_b).bit_count() // 2
    assert exchange * 2 <= distance
    assert abs(real_comparators(mask_a, layer) - real_comparators(mask_b, layer)) <= exchange
    return after_a, after_b


def check_chains():
    # Exhaustive local four-symbol check of the analytic contraction lemma.
    for a, b, c, d in itertools.product((-1, 0, 1), repeat=4):
        x, y = sorted((a, b)), sorted((c, d))
        assert abs(x[0] - y[0]) + abs(x[1] - y[1]) <= abs(a - c) + abs(b - d)

    rng = random.Random(20261115)
    sticks = transitions = 0
    for kind, word in components(18):
        if kind != 'S':
            continue
        states = stick_chain(word)
        n, m = len(word), len(word) // 2
        mixed = sum(word[i] != word[i + 1] for i in range(1, n - 1, 2))
        masks = list(map(real_mask, states))
        union = intersection = masks[0]
        for mask in masks[1:]:
            union |= mask
            intersection &= mask
        assert union.bit_count() == m + 1 + mixed
        assert intersection == 0
        if mixed == 0:
            assert set(masks) == {union ^ (1 << i) for i in range(n) if union >> i & 1}
        for a, b in zip(states, states[1:]):
            assert (real_mask(a) ^ real_mask(b)).bit_count() == 2
            assert sum(abs(x - y) for x, y in zip(a, b)) == 2
            assert all(x <= y for x, y in zip(a, b)) or all(x >= y for x, y in zip(a, b))
            for _ in range(40):
                layer = random_matching(n, rng)
                a, b = check_transport(a, b, layer)
                assert sum(abs(x - y) for x, y in zip(a, b)) == 2
                assert (real_mask(a) ^ real_mask(b)).bit_count() == 2
                transitions += 1
        sticks += 1

    for n in range(6, 19, 2):
        for sentence in sentences(n):
            # Integer form of F <= 2^(n/3), avoiding floating point.
            assert family_count(sentence) ** 3 <= 2 ** n
    print(f'{sticks} stick components, {transitions} transport steps, '
          'and saturated-family bounds through n=18 checked', flush=True)
    return dict(stick_components=sticks, transport_steps=transitions,
                local_contraction_cases=81, family_bound_max_n=18)


def read_cover(path):
    payload = path.read_bytes()
    sha = hashlib.sha256(payload).hexdigest()
    summary = json.loads(path.with_suffix('.summary.json').read_text())
    assert sha == summary['sha256']
    cases = [json.loads(line) for line in payload.splitlines() if line]
    assert len(cases) == summary['cases']
    return cases, sha


def verify_certificate(cases, sha, certificate):
    assert certificate['cover_sha256'] == sha
    witnesses = certificate['witnesses']
    assert len(witnesses) == len(cases)
    by_id = {w['case_id']: w for w in witnesses}
    assert len(by_id) == len(cases)
    direct_placements = 0
    for case in cases:
        witness = by_id[case['case_id']]
        n, layer = case['n'], witness['third_layer']
        assert len(layer) == n // 2
        assert sorted(x for edge in layer for x in edge) == list(range(n))
        assert all(a < b for a, b in layer)
        family = half_blind_family(n, case['layers'])
        assert len(family) == witness['family_size'] == case['half_blind_sets']
        leaks = [real_comparators(mask, layer) for mask in family]
        assert min(leaks) == witness['min_real_comparators'] >= 1
        # Also replay every normalized placement directly, without calling
        # half_blind_family or relying on its deduplication/count formula.
        first, second = case['layers']
        for choices in itertools.product((0, 1), repeat=len(first)):
            state = [0] * n
            for (a, b), choice in zip(first, choices):
                state[a if choice == 0 else b] = -1 if choice == 0 else 1
            if any(state[a] == state[b] == 0 for a, b in second):
                continue
            for a, b in second:
                state[a], state[b] = sorted((state[a], state[b]))
            assert any(state[a] == state[b] == 0 for a, b in layer)
            direct_placements += 1
    print(f'{len(cases)} third-layer witnesses replayed, including '
          f'{direct_placements} direct normalized placements', flush=True)


def make_certificate(cases, sha):
    rng = random.Random(20261115)
    witnesses = []
    for case in cases:
        n = case['n']
        assert n % 2 == 0 and n >= 18
        family = half_blind_family(n, case['layers'])
        assert len(family) ** 3 <= 2 ** n
        assert len(family) * 2 ** (n // 2) < math.comb(n, n // 2)
        for attempt in range(1, 10001):
            layer = random_matching(n, rng)
            leaks = [real_comparators(mask, layer) for mask in family]
            if min(leaks) > 0:
                break
        else:
            raise RuntimeError('sampling limit reached; no claim made for this case')
        witnesses.append(dict(case_id=case['case_id'], third_layer=layer,
                              family_size=len(family), min_real_comparators=min(leaks),
                              sampling_attempts=attempt))
    report = dict(claim='No half-width signed-infinity placement blinds all three layers',
                  scope='These are obstruction witnesses for pure blinding, not sorting networks',
                  cover_sha256=sha, witnesses=witnesses,
                  max_sampling_attempts=max(w['sampling_attempts'] for w in witnesses),
                  family_histogram=dict(sorted(Counter(w['family_size'] for w in witnesses).items())))
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cover', type=Path, default=Path(__file__).parent / 'prefixes/complete18.jsonl')
    ap.add_argument('--out', type=Path, default=Path(__file__).parent / 'results/half-blind-obstructions18.json')
    ap.add_argument('--replay', action='store_true', help='verify an existing certificate without sampling')
    args = ap.parse_args()
    if not args.replay:
        checks = check_chains()
    cases, sha = read_cover(args.cover)
    if args.replay:
        certificate = json.loads(args.out.read_text())
    else:
        certificate = make_certificate(cases, sha)
        certificate['checks'] = checks
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(certificate, indent=2) + '\n')
    verify_certificate(cases, sha, certificate)
    print(json.dumps({k: v for k, v in certificate.items() if k != 'witnesses'}), flush=True)


if __name__ == '__main__':
    main()
