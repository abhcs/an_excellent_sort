#!/usr/bin/env python3
"""Enumerate every abstract family of four distinct three-element sets."""
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path

from d12_triangle_lemmas_classify import prices
from d12_triangle_lemmas_verify import maximum_weight


def hand_obstruction(triangles):
    """The hand criterion proved in d12_triangle_lemmas_complete.md."""
    sets = list(map(set, triangles))
    if len(set.union(*sets)) >= 8:
        return False
    counts = Counter(pair for tri in triangles for pair in itertools.combinations(sorted(tri), 2))
    if any(count >= 3 for count in counts.values()):
        return False
    for pair, count in counts.items():
        if count == 2:
            edge = set(pair)
            residual = [tri - edge for tri in sets if not edge <= tri]
            assert len(residual) == 2
            a, b = residual
            if len(a) != 2 or len(b) != 2 or len(a & b) != 1:
                return False
    return True


def enumerate_families():
    permutations = list(itertools.permutations(range(4)))
    translations = [[sum(1 << p[i] for i in range(4) if mask >> i & 1) for mask in range(16)]
                    for p in permutations]
    shared = sorted((mask for mask in range(1, 16) if mask.bit_count() >= 2),
                    key=lambda mask: (-mask.bit_count(), mask))
    classes = {}
    incidence_vectors = 0

    def rec(index, remaining, columns):
        nonlocal incidence_vectors
        if index == len(shared):
            full = columns + [1 << row for row in range(4) for _ in range(remaining[row])]
            triangles = tuple(tuple(v for v, mask in enumerate(full) if mask >> row & 1) for row in range(4))
            assert all(len(tri) == 3 for tri in triangles)
            if len(set(triangles)) != 4:
                return
            incidence_vectors += 1
            key = min(tuple(sorted(table[mask] for mask in full)) for table in translations)
            classes.setdefault(key, tuple(tuple(v for v, mask in enumerate(key) if mask >> row & 1)
                                          for row in range(4)))
            return
        mask = shared[index]
        used_rows = [row for row in range(4) if mask >> row & 1]
        for count in range(1 + min(remaining[row] for row in used_rows)):
            next_remaining = [value - (count if row in used_rows else 0) for row, value in enumerate(remaining)]
            rec(index + 1, next_remaining, columns + [mask] * count)

    rec(0, [3, 3, 3, 3], [])
    return incidence_vectors, classes


def main():
    labelled_rows, classes = enumerate_families()
    by_union, unsat_union, unsat, min_control_fail = Counter(), Counter(), [], []
    for key, triangles in sorted(classes.items(), key=lambda item: (len(item[0]), item[0])):
        by_union[len(key)] += 1
        maximum, _ = maximum_weight(triangles)
        assert hand_obstruction(triangles) == (maximum < 4), triangles
        if maximum < 4:
            cert = prices(triangles)
            controls = [maximum_weight([tri for i, tri in enumerate(triangles) if i != omitted])[0]
                        for omitted in range(4)]
            if any(value != 3 for value in controls):
                min_control_fail.append(triangles)
            unsat_union[len(key)] += 1
            item = dict(id=len(unsat) + 1, incidence_masks=key, triangles=triangles,
                        vertices=len(key), maximum_hit=maximum,
                        twice_vertex_prices=cert, deletion_control_maxima=controls)
            unsat.append(item)
            print(item, flush=True)
    result = dict(distinct_labelled_row_incidence_vectors=labelled_rows,
                  abstract_four_triple_families=len(classes), by_union_size=dict(by_union),
                  unsatisfiable_types=len(unsat), unsatisfiable_by_union_size=dict(unsat_union),
                  all_unsatisfiable_vertex_price_certified=all(item['twice_vertex_prices'] is not None for item in unsat),
                  all_unsatisfiable_inclusion_minimal=not min_control_fail,
                  exact_hand_criterion_agrees_on_all_66=True,
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  types=unsat)
    target = Path(__file__).parent / 'results/d12_triangle_lemmas_allfour.json'
    target.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'types'}))


if __name__ == '__main__':
    main()
