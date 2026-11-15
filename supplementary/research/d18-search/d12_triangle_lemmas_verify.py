#!/usr/bin/env python3
"""Verify hand price certificates without canonicalization or matching search."""
from collections import Counter
import hashlib
import itertools
import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).parent
CORE_FILE = ROOT / 'results/d12-triangle-scan-four-cores.jsonl'
STATE_FILE = ROOT / 'results/d17-feedback-twelve-states.json'

# Letters are just a readable presentation of these explicit vertex labels.
TEMPLATES = {
    'I': dict(letters='xabcdef', triangles=((0, 1, 2), (0, 1, 3), (0, 4, 5), (0, 4, 6)),
              prices=(2, 2, 0, 0, 2, 0, 0)),
    'II': dict(letters='xyzabcd', triangles=((0, 2, 3), (1, 2, 4), (0, 1, 5), (0, 1, 6)),
               prices=(2, 2, 1, 1, 1, 0, 0)),
    'III': dict(letters='abcxyz', triangles=((0, 1, 2), (0, 1, 3), (0, 2, 4), (1, 2, 5)),
                prices=(2, 2, 2, 0, 0, 0)),
    'IV': dict(letters='xabcd', triangles=((0, 1, 2), (0, 1, 3), (0, 2, 4), (0, 3, 4)),
               prices=(3, 1, 1, 1, 1)),
}


def price_check(triangles, prices):
    vertices = sorted(set().union(*map(set, triangles)))
    weights = Counter(pair for triple in triangles for pair in itertools.combinations(sorted(triple), 2))
    assert set(vertices) == set(prices)
    assert all(value >= 0 for value in prices.values())
    assert sum(prices.values()) < 2 * len(triangles)
    checked = 0
    for a, b in itertools.combinations(vertices, 2):
        assert prices[a] + prices[b] >= 2 * weights[a, b]
        checked += 1
    return checked


def degree_prices(triangles):
    degree = Counter(v for triple in triangles for v in triple)
    signature = tuple(sorted(degree.values()))
    if signature == (1, 1, 1, 1, 2, 2, 4):
        return 'I', {v: 2 if d >= 2 else 0 for v, d in degree.items()}
    if signature == (1, 1, 1, 1, 2, 3, 3):
        heavy = {v for v, d in degree.items() if d == 3}
        # Leaves on a triple containing both heavy vertices receive zero;
        # the other two leaves and the degree-two vertex receive one half.
        free = {v for triple in triangles if heavy <= set(triple) for v in triple if v not in heavy}
        return 'II', {v: 2 if v in heavy else 0 if v in free else 1 for v in degree}
    if signature == (1, 1, 1, 3, 3, 3):
        return 'III', {v: 2 if d == 3 else 0 for v, d in degree.items()}
    if signature == (2, 2, 2, 2, 4):
        return 'IV', {v: 3 if d == 4 else 1 for v, d in degree.items()}
    raise AssertionError(('Unexpected degree signature', signature, triangles))


def hits(triangles, matching):
    used = [v for edge in matching for v in edge]
    assert len(used) == len(set(used))
    return all(any(set(edge) <= set(triple) for edge in matching) for triple in triangles)


def positive_controls():
    # Fixed explicit controls. Each row omits the corresponding indexed triple.
    controls = {
        'I': (((0, 4), (1, 3)), ((0, 4), (1, 2)), ((0, 1), (4, 6)), ((0, 1), (4, 5))),
        'II': (((0, 1), (2, 4)), ((0, 1), (2, 3)), ((0, 6), (1, 4), (2, 3)),
               ((0, 5), (1, 4), (2, 3))),
        'III': (((0, 3), (1, 5), (2, 4)), ((0, 2), (1, 5)),
                ((0, 1), (2, 5)), ((0, 1), (2, 4))),
        'IV': (((0, 3), (2, 4)), ((0, 2), (3, 4)), ((0, 1), (3, 4)), ((0, 1), (2, 4))),
    }
    records = []
    for name, template in TEMPLATES.items():
        for omitted, matching in enumerate(controls[name]):
            remaining = [tri for i, tri in enumerate(template['triangles']) if i != omitted]
            assert hits(remaining, matching), (name, omitted, matching)
            records.append(dict(type=name, omitted_triple=omitted, matching=matching))
    return records


def isomorphism(triangles, template):
    """Independent direct bijection search, not incidence canonicalization."""
    degree = Counter(v for tri in triangles for v in tri)
    target_degree = Counter(v for tri in template['triangles'] for v in tri)
    source_groups = [[v for v in sorted(degree) if degree[v] == d] for d in sorted(set(degree.values()))]
    target_groups = [[v for v in sorted(target_degree) if target_degree[v] == d]
                     for d in sorted(set(degree.values()))]
    target = {tuple(sorted(tri)) for tri in template['triangles']}
    for choices in itertools.product(*(itertools.permutations(group) for group in target_groups)):
        mapping = {a: b for source, choice in zip(source_groups, choices) for a, b in zip(source, choice)}
        if {tuple(sorted(mapping[v] for v in tri)) for tri in triangles} == target:
            return mapping
    raise AssertionError(('No template isomorphism', triangles, template))


def maximum_weight(triangles):
    """Exact matching DP over subsets; independent of price certificates."""
    vertices = sorted(set().union(*map(set, triangles)))
    labels = {v: i for i, v in enumerate(vertices)}
    n = len(vertices)
    weights = [[0] * n for _ in range(n)]
    for tri in triangles:
        for a, b in itertools.combinations(tri, 2):
            i, j = labels[a], labels[b]
            weights[i][j] += 1
            weights[j][i] += 1

    @lru_cache(None)
    def dp(mask):
        if not mask:
            return 0
        first_bit = mask & -mask
        first = first_bit.bit_length() - 1
        rest = mask ^ first_bit
        best = dp(rest)
        for other in range(first + 1, n):
            if rest >> other & 1:
                best = max(best, weights[first][other] + dp(rest ^ (1 << other)))
        return best
    result = dp((1 << n) - 1)
    return result, dp.cache_info().currsize


def main():
    pair_checks = 0
    for template in TEMPLATES.values():
        pair_checks += price_check(template['triangles'], dict(enumerate(template['prices'])))
    controls = positive_controls()
    states = json.loads(STATE_FILE.read_text())['states']
    assert len(states) == 20 and all(len(state) == 12 and state.count(0) == 9 for state in states)
    classes, assigned, representative_states, labelled = Counter(), Counter(), 0, 0
    catalogue, dp_states = [], 0
    for line in CORE_FILE.read_text().splitlines():
        record = json.loads(line)
        triangles = record['triangles']
        assert len(triangles) == 4 and len({tuple(tri) for tri in triangles}) == 4
        assert all(len(tri) == 3 and len(set(tri)) == 3 for tri in triangles)
        name, prices = degree_prices(triangles)
        pair_checks += price_check(triangles, prices)
        template = TEMPLATES[name]
        mapping = isomorphism(triangles, template)
        maximum, subproblems = maximum_weight(triangles)
        assert maximum == 3
        dp_states += subproblems
        catalogue.append(dict(core_index=labelled, type=name, triangles=triangles,
                              original_to_template={v: template['letters'][i] for v, i in sorted(mapping.items())},
                              twice_vertex_prices=prices, maximum_triangles_hit=maximum,
                              first_matching_count=record['count']))
        classes[name] += 1
        assigned[name] += record['count']
        labelled += 1
        matching = record['first_matching']
        assert all(0 <= a < b < 12 for a, b in matching)
        used = [v for edge in matching for v in edge]
        assert len(used) == len(set(used))
        missed = set()
        for original in states:
            state, count = list(original), 0
            for a, b in matching:
                count += state[a] == state[b] == 0
                state[a], state[b] = min(state[a], state[b]), max(state[a], state[b])
            if count < 4:
                missed.add(tuple(i for i, value in enumerate(state) if value))
            representative_states += 1
        assert {tuple(tri) for tri in triangles} <= missed
    assert labelled == 3957 and sum(assigned.values()) == 140152
    assert dict(classes) == {'I': 1187, 'II': 299, 'III': 834, 'IV': 1637}
    result = dict(status='VERIFIED', templates=4, labelled_cores=labelled,
                  labelled_cores_by_template=dict(classes),
                  reported_first_matchings_by_template=dict(assigned),
                  reported_first_matchings=sum(assigned.values()),
                  independently_reenumerated_all_first_matchings=False,
                  representative_signed_state_transports=representative_states,
                  exact_pair_price_inequalities=pair_checks,
                  independent_matching_dp_checked_cores=labelled,
                  independent_matching_dp_subproblems=dp_states,
                  explicit_isomorphisms=len(catalogue),
                  positive_controls=controls, sat_used=False,
                  input_core_sha256=hashlib.sha256(CORE_FILE.read_bytes()).hexdigest(),
                  input_states_sha256=hashlib.sha256(STATE_FILE.read_bytes()).hexdigest(),
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    target = ROOT / 'results/d12_triangle_lemmas_verification.json'
    catalogue_path = ROOT / 'results/d12_triangle_lemmas_catalogue.jsonl'
    catalogue_path.write_text(''.join(json.dumps(item, sort_keys=True) + '\n' for item in catalogue))
    result['catalogue_sha256'] = hashlib.sha256(catalogue_path.read_bytes()).hexdigest()
    target.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'positive_controls'}))


if __name__ == '__main__':
    main()
