#!/usr/bin/env python3
"""Discover a compact shared bank of explicit rank-endpoint witnesses.

Only the exported real-input runs are proof premises. The finite binary
seed pool is a discovery device, not used by the final certificate checker.
"""
import itertools
import json
import random
from pathlib import Path
from h9_feedback_round3_021637 import FIRST, SECOND
from netlib import run

PLANS = {
    (2, 1): ('isolated', [(0, [])]), (2, 2): ('isolated', [(0, [])]),
    (4, 1): ('forced', [(0, [3]), (1, [4]), (5, [2]), (6, [8])]),
    (6, 1): ('forced', [(8, [7]), (6, [2]), (3, [4]), (1, [5])]),
    (6, 2): ('isolated', [(5, [])]), (6, 3): ('isolated', [(5, [])]),
    (6, 4): ('hall', [(3, [2, 4]), (5, [2, 4]), (8, [2, 4])]),
    (8, 1): ('isolated', [(8, [])]), (8, 2): ('isolated', [(8, [])]),
    (8, 3): ('isolated', [(8, [])]),
    (10, 1): ('isolated', [(1, [])]), (10, 2): ('isolated', [(1, [])]),
    (14, 1): ('isolated', [(8, [])]), (14, 2): ('isolated', [(8, [])]),
}


def lift(bits):
    zeros = [i for i, b in enumerate(bits) if not b]
    ones = [i for i, b in enumerate(bits) if b]
    output = [0] * 9
    for rank, wire in enumerate(zeros + ones):
        output[wire] = rank
    return tuple(output)


def main():
    root = Path(__file__).parents[1]
    data = json.loads((root / 'results/h9-feedback-round3-021637.json').read_text())
    seeds = sorted({lift(bits) for bits in itertools.product((0, 1), repeat=9)})
    actions, records = [], []
    seed_pool = {tuple(range(9))}
    for (case, number), (kind, plan) in PLANS.items():
        item = data[case - 1]
        fourth = item['fourths'][number - 1]['fourth']
        prefix = (FIRST, SECOND, item['third'], fourth)
        values = [run(prefix, x) for x in seeds]
        used, requirements = set(), []
        for pivot, allowed in plan:
            assert pivot not in used
            partners = [None, *sorted(set(range(9)) - used - {pivot} - set(allowed))]
            for partner in partners:
                operations = ['idle'] if partner is None else ['min', 'max']
                possibilities = []
                for operation in operations:
                    vals = [y[pivot] if operation == 'idle' else
                            min(y[pivot], y[partner]) if operation == 'min' else
                            max(y[pivot], y[partner]) for y in values]
                    lo, hi = min(vals), max(vals)
                    if hi - lo >= 4:
                        low = next(seeds[i] for i, v in enumerate(vals) if v == lo)
                        high = next(seeds[i] for i, v in enumerate(vals) if v == hi)
                        seed_pool.update((low, high))
                        possibilities.append(operation)
                assert possibilities, (case, number, pivot, partner)
                action = dict(case=case, number=number, prefix=prefix, pivot=pivot,
                              partner=partner, operations=possibilities)
                requirements.append(len(actions))
                actions.append(action)
            if kind == 'forced':
                assert len(allowed) == 1
                used.update((pivot, allowed[0]))
        records.append(dict(case=case, number=number, kind=kind, third=item['third'], fourth=fourth,
                            plan=plan, requirements=requirements))

    pool = sorted(seed_pool)
    identity = pool.index(tuple(range(9)))
    measurements = []
    for action in actions:
        outputs = [run(action['prefix'], x) for x in pool]
        pivot, partner = action['pivot'], action['partner']
        measurements.append([[y[pivot] if operation == 'idle' else
                              min(y[pivot], y[partner]) if operation == 'min' else
                              max(y[pivot], y[partner]) for y in outputs]
                             for operation in action['operations']])

    def covered(selected):
        return {i for i, choices in enumerate(measurements)
                if any(max(vals[j] for j in selected) - min(vals[j] for j in selected) >= 4
                       for vals in choices)}

    rng = random.Random(261637)
    best = list(range(len(pool)))
    for attempt in range(8):
        selected = [identity]
        while len(covered(selected)) < len(actions):
            old = covered(selected)
            candidates = [i for i in range(len(pool)) if i not in selected]
            rng.shuffle(candidates)
            winner = max(candidates, key=lambda i: len(covered(selected + [i])))
            if len(covered(selected + [winner])) == len(old):
                winner_pair = max(itertools.combinations(candidates, 2),
                                  key=lambda pair: len(covered(selected + list(pair))))
                assert len(covered(selected + list(winner_pair))) > len(old)
                selected.extend(winner_pair)
            else:
                selected.append(winner)
        for i in selected[:]:
            if len(selected) > 1 and len(covered([j for j in selected if j != i])) == len(actions):
                selected.remove(i)
        if len(selected) < len(best):
            best = selected
    inputs = [pool[i] for i in best]
    index = {old: new for new, old in enumerate(best)}
    witness_rows = []
    for action, choices in zip(actions, measurements):
        options = []
        for operation, vals in zip(action['operations'], choices):
            low = min(best, key=lambda i: vals[i])
            high = max(best, key=lambda i: vals[i])
            if vals[high] - vals[low] >= 4:
                options.append((vals[high] - vals[low], operation, low, high, vals[low], vals[high]))
        gap, operation, low, high, lo, hi = max(options)
        witness_rows.append(dict(case=action['case'], number=action['number'],
                                 pivot=action['pivot'], partner=action['partner'], output=operation,
                                 low_input=index[low], low=lo, high_input=index[high], high=hi))
    endings = json.loads((root / 'results/h9-feedback-round4-endings.json').read_text())
    contacts = []
    for case, number, fifth, row_index in (
        (4, 1, ((0, 3), (1, 4), (2, 5), (6, 8)), 4),
        (6, 1, ((1, 5), (2, 6), (3, 4), (7, 8)), 1),
    ):
        record = next(x for x in endings if x['case'] == case and x['number'] == number)
        row = record['rows'][row_index]
        assert not any(set(edge) <= set(row['real']) and set(edge) & set(row['sink']) for edge in fifth)
        contacts.append(dict(case=case, number=number, fifth=fifth, **row))
    report = dict(status='EXPLICIT_WITNESSES_FOUND', inputs=inputs, cases=records,
                  endpoint_rows=witness_rows, final_contacts=contacts,
                  discovery_pool=len(pool), original_seed_pool=len(seeds))
    (root / 'results/h9-feedback-round4-rank-witnesses.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(status=report['status'], shared_inputs=len(inputs), endpoint_rows=len(actions),
                         fourth_layer_cases=len(records), final_contacts=len(contacts), pool=len(pool)), indent=2))


if __name__ == '__main__':
    main()
