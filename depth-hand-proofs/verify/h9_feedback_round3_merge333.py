#!/usr/bin/env python3
"""Audit the three-sorted-triples four-layer merger obstruction; no SAT."""
import hashlib
import itertools
import json
from pathlib import Path


def matchings(vertices):
    if not vertices:
        yield ()
        return
    a, *rest = vertices
    yield from matchings(rest)
    for j, b in enumerate(rest):
        for tail in matchings(rest[:j] + rest[j + 1:]):
            yield ((a, b),) + tail


def main():
    blocks = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
    middles = {1, 4, 7}
    endpoints = set(range(9)) - middles
    forbidden = {edge for block in blocks for edge in itertools.combinations(block, 2)}
    deletions = [set(choice) for choice in itertools.product(*[(b[0], b[2]) for b in blocks])]
    real_sets = [set(range(9)) - deletion for deletion in deletions]
    weights = {edge: sum(set(edge) <= real for real in real_sets)
               for edge in itertools.combinations(range(9), 2) if edge not in forbidden}
    for edge, weight in weights.items():
        assert weight == 2 ** (1 + len(set(edge) & middles))
    layers = [layer for layer in matchings(list(range(9))) if not set(layer) & forbidden]
    equalities, failures = [], []
    for layer in layers:
        total = sum(weights[edge] for edge in layer)
        mm = [edge for edge in layer if set(edge) <= middles]
        if not mm:
            assert total <= 14
        else:
            assert len(mm) == 1 and total <= 16
        rr = [sum(set(edge) <= real for edge in layer) for real in real_sets]
        assert not all(count >= 2 for count in rr)
        if total == 16:
            me = [edge for edge in layer if len(set(edge) & middles) == 1]
            ee = [edge for edge in layer if set(edge) <= endpoints]
            assert len(layer) == 4 and len(mm) == 1 and len(me) == 1 and len(ee) == 2
            idle = set(range(9)) - {v for edge in layer for v in edge}
            assert len(idle) == 1 and idle <= endpoints
            v = next(iter(idle))
            block = next(b for b in blocks if v in b)
            u = next(x for x in (block[0], block[2]) if x != v)
            selected = [deletion for deletion in deletions if u in deletion]
            assert len(selected) == 4 and all(v not in deletion for deletion in selected)
            covers = [sum(set(edge) <= deletion for deletion in selected) for edge in ee]
            assert sum(covers) <= 3
            uncovered = [sorted(deletion) for deletion in selected if not any(set(edge) <= deletion for edge in ee)]
            assert uncovered
            equalities.append(dict(layer=layer, idle=v, selected_deletions=[sorted(x) for x in selected],
                                   edge_cover_counts=covers, uncovered=uncovered))
    # Positive controls: none of the eight demands is redundant in this small
    # matching system. Dropping any one has a matching meeting all the others.
    controls = []
    for omitted in range(8):
        witness = next((layer for layer in layers if all(
            sum(set(edge) <= real for edge in layer) >= 2
            for j, real in enumerate(real_sets) if j != omitted)), None)
        controls.append(dict(omitted=omitted, witness=witness))
    report = dict(status='VERIFIED', restrictions=8, allowed_matchings=len(layers),
                  equality_shapes=len(equalities), matching_survivors=0,
                  real_sets=[sorted(x) for x in real_sets], equalities=equalities,
                  deletion_controls=controls,
                  all_single_deletions_satisfiable=all(x['witness'] is not None for x in controls),
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    target = Path(__file__).parents[1] / 'results/h9-feedback-round3-merge333.json'
    target.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('equalities', 'real_sets', 'deletion_controls')}, indent=2))


if __name__ == '__main__':
    main()
