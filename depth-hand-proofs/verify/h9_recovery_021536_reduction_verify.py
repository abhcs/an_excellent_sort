#!/usr/bin/env python3
"""Fixed, solver-free checks for the 02 15 36 hand third-layer reduction."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
C = (((0, 1), (2, 3), (4, 5)), ((0, 2), (1, 5), (3, 6)))
ORDERED = {(0, 2), (0, 5), (0, 6), (1, 5), (3, 6), (4, 5)}
FORMS = ['12 34 56 78', '12 34 78', '12 37 48', '12 37 48 56',
         '13 24 56 78', '13 24 78', '13 27 48', '13 27 48 56',
         '14 23 56 78', '14 23 78', '14 27 38', '14 27 38 56',
         '17 23 48', '17 23 48 56', '17 24 38', '17 24 38 56',
         '17 28 34', '17 28 34 56']
A = {0: -1, 2: 1, 4: 1}
B = {0: -1, 2: 1, 4: -1}
D = {0: -1, 1: -1, 2: 1}


def normalize(M):
    return tuple(sorted(tuple(sorted(e)) for e in M))


def perfect(vertices):
    vertices = sorted(vertices)
    if not vertices:
        yield ()
        return
    a, *rest = vertices
    for b in rest:
        for M in perfect(set(rest) - {b}):
            yield normalize(((a, b),) + M)


def run(prefix, values):
    x = list(values)
    for layer in prefix:
        for a, b in layer:
            x[a], x[b] = min(x[a], x[b]), max(x[a], x[b])
    return tuple(x)


def trace(prefix, placement):
    signs = [placement.get(v, 0) for v in range(9)]
    tracks = list(range(9))
    gates = []
    for layer in prefix:
        for a, b in layer:
            if signs[a] == signs[b] == 0:
                gates.append((tracks[a], tracks[b]))
            elif signs[a] > signs[b]:
                signs[a], signs[b] = signs[b], signs[a]
                tracks[a], tracks[b] = tracks[b], tracks[a]
    positions = {v: i for i, v in enumerate(tracks)}
    boundary = [(positions[a], positions[b]) for a, b in gates]
    return dict(signs=signs, tracks=tracks, gates=gates, boundary=boundary,
                real={v for v in range(9) if signs[v] == 0})


def direct(prefix, placement, row, reschedule=None):
    real = sorted(set(range(9)) - set(placement))
    count = 0
    for ranks in itertools.permutations(range(len(real))):
        x = [100 * placement.get(v, 0) for v in range(9)]
        for v, rank in zip(real, ranks):
            x[v] = rank
        retained = run((row['gates'],), x)
        assert run(prefix, x) == tuple(retained[v] for v in row['tracks'])
        if reschedule is not None:
            boundary_input = tuple(x[v] for v in row['tracks'])
            assert run(reschedule, boundary_input) == run(prefix, x)
        count += 1
    return count


def disjoint_two(row):
    assert len(row['gates']) == 2
    assert len({v for e in row['gates'] for v in e}) == 4


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    start = time.monotonic()
    replay_count = 0
    note = ROOT / 'h9_recovery_021536_reduction.md'
    text = note.read_text()
    # Direct inequality controls are supplemental to the displayed min/max proof.
    for x in itertools.product((0, 1), repeat=9):
        y = run(C, x)
        assert all(y[a] <= y[b] for a, b in ORDERED)
    for p, sentinel, gates in [({0: 1, 2: 1}, {5, 6}, [(4, 1), (0, 2)]),
                                ({0: 1, 2: -1}, {0, 5}, [(4, 1), (3, 6)])]:
        row = trace(C, p)
        assert set(range(9)) - row['real'] == sentinel
        assert row['boundary'] == gates
        disjoint_two(row)
        replay_count += direct(C, p, row)
    for p, sentinel, gates in [(A, {0: -1, 5: 1, 6: 1}, []),
                                (B, {0: -1, 4: -1, 6: 1}, [(1, 5)]),
                                (D, {0: -1, 1: -1, 6: 1}, [(4, 5)])]:
        row = trace(C, p)
        assert {v: s for v, s in enumerate(row['signs']) if s} == sentinel
        assert row['boundary'] == gates

    # Enumerate only the elementary perfect-eight recipe for an independent
    # cross-check of the parameterized idle-5 argument, not all nine matchings.
    idle_five = [M for M in perfect({0, 1, 2, 3, 4, 6, 7, 8})
                 if not set(M) & ORDERED]
    exchange_counts = {'AB': 0, 'AC': 0}
    all_cross = paired = 0
    for M in idle_five:
        partner = {a: b for e in M for a, b in (e, e[::-1])}
        ab = partner[1] in (0, 6) and partner[4] not in (0, 6)
        ac = partner[4] in (0, 1, 6) and partner[1] not in (0, 6)
        if ab or ac:
            p = B if ab else D
            first, second = trace(C + (M,), A), trace(C + (M,), p)
            disjoint_two(first)
            disjoint_two(second)
            assert len(first['real']) == len(second['real']) == 6
            assert len(first['real'] & second['real']) == 5
            replay_count += direct(C + (M,), A, first)
            replay_count += direct(C + (M,), p, second)
            exchange_counts['AB' if ab else 'AC'] += 1
            continue
        assert (1, 4) not in M
        assert ((0, 1) in M) == ((4, 6) in M)
        assert ((0, 4) in M) == ((1, 6) in M)
        if (0, 1) not in M and (0, 4) not in M:
            left = {0, 1, 4, 6}
            assert all(len(set(e) & left) == 1 for e in M)
            p = {0: -1, 1: -1, 2: 1, 4: -1}
            initial = trace(C, p)
            assert set(range(9)) - initial['real'] == left and not initial['gates']
            row = trace(C + (M,), p)
            assert not row['gates'] and len(row['real']) == 5
            replay_count += direct(C + (M,), p, row)
            all_cross += 1
        else:
            base = {(0, 1), (4, 6)} if (0, 1) in M else {(0, 4), (1, 6)}
            K = normalize(set(M) - base)
            assert {v for e in K for v in e} == {2, 3, 7, 8}
            p = {0: -1, 2: 1}
            row = trace(C + (M,), p)
            assert row['boundary'] == [(4, 5), (1, 5)] + list(K)
            schedule = (((4, 5), K[0]), ((1, 5), K[1]))
            replay_count += direct(C + (M,), p, row, schedule)
            paired += 1
    assert len(idle_five) == 63
    assert sum(exchange_counts.values()) == 43 and all_cross == 14 and paired == 6

    def canonical(M):
        pi = {v: v for v in range(9)}
        pi[7], pi[8] = 8, 7
        return min(normalize(M), normalize((pi[a], pi[b]) for a, b in M))

    actual = {canonical(K + extra) for K in perfect({1, 2, 3, 4, 7, 8})
              for extra in ((), ((5, 6),))}
    listed = {normalize(tuple(map(int, edge)) for edge in line.split()) for line in FORMS}
    assert actual == listed and len(actual) == 18
    for number, line in enumerate(FORMS, 1):
        assert f'| {number} | `{line}` |' in text
    assert time.monotonic() - start < 30
    report = dict(status='VERIFIED_REDUCTION_ONLY', solver_free=True,
                  accepted_new_H9_classes=0, third_layer_representatives=18,
                  idle_five_crosscheck_forms=63, exchange_crosschecks=exchange_counts,
                  all_cross_blind_forms=14, paired_rescheduling_forms=6,
                  direct_order_replays=replay_count,
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  note_sha256=hashlib.sha256(note.read_bytes()).hexdigest(),
                  elapsed_seconds=time.monotonic() - start)
    if args.out:
        args.out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
