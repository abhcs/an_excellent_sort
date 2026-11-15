#!/usr/bin/env python3
"""Exact two-layer completion by context constraints on a single matching.

No SAT solver is used. A timeout remains inconclusive. The local constraints
retain every common-bit context of each required pair, not just its endpoints.
"""
import argparse
import itertools
import json
from pathlib import Path
import time

from two_real_graph import (edges_and_examples, images, images_with_witness,
                            inversion_edges, matchings, run_bits)


def contexts(n, values):
    result = {}
    for x in sorted(values):
        for a in range(n):
            if not (x >> a & 1):
                continue
            for b in range(a + 1, n):
                if not (x >> b & 1) and x ^ (1 << a) ^ (1 << b) in values:
                    result.setdefault((a, b), []).append(x & ~(1 << a))
    return result


def cubes(n, values, dimension=3):
    for base in sorted(values):
        axes = [a for a in range(n) if not (base >> a & 1) and base | (1 << a) in values]
        for chosen in itertools.combinations(axes, dimension):
            corners = [base | sum(1 << a for i, a in enumerate(chosen) if mask >> i & 1)
                       for mask in range(1 << dimension)]
            if all(x in values for x in corners):
                yield dict(base=base, axes=list(chosen), corners=corners)


def rectangle_forbidden(n, values):
    """Four outputs forbid penultimate comparisons involving the free bit."""
    forbidden = {}
    for (u, v), rows in contexts(n, values).items():
        row_set = set(rows)
        for z in rows:
            for w in range(n):
                if w in (u, v) or z >> w & 1 or z | (1 << w) not in row_set:
                    continue
                outputs = [z | (1 << u), z | (1 << v),
                           z | (1 << u) | (1 << w), z | (1 << v) | (1 << w)]
                witness = dict(exchange=[u, v], free=w, outputs=outputs)
                for a in (u, v):
                    forbidden.setdefault(tuple(sorted((a, w))), witness)
    return forbidden


def port(u, mate, context):
    if u == mate:
        return u
    return min(u, mate) if context >> mate & 1 else max(u, mate)


def requirements(u, v, p, q, rows):
    if p == v and q == u:
        return 0  # The marked pair meets in the first layer.
    if p == v or q == u or p == q:
        return None  # The proposed partners are not a matching.
    mask = 0
    for context in rows:
        a, b = sorted((port(u, p, context), port(v, q, context)))
        if b != a + 1:
            return None  # Nonredundant final comparisons must be adjacent.
        mask |= 1 << a
        if mask & (mask << 1):
            return None  # Two contexts require overlapping final comparisons.
    return mask


class Completion:
    """Values must be the complete image of a standard comparator prefix."""
    def __init__(self, n, values, limit=5):
        self.n, self.values = n, set(values)
        self.start = time.monotonic()
        self.deadline = self.start + limit
        self.nodes = self.propagations = 0
        self.forbidden = rectangle_forbidden(n, self.values)
        self.domains = []
        for u in range(n):
            domain = {u}  # Being idle.
            for p in range(max(0, u - 3), min(n, u + 4)):
                a, b = sorted((u, p))
                if a == b or (a, b) in self.forbidden:
                    continue
                # A redundant first-suffix comparator can be deleted WLOG.
                if any(x >> a & 1 and not (x >> b & 1) for x in self.values):
                    domain.add(p)
            self.domains.append(domain)
        self.tables = {}
        for (u, v), rows in contexts(n, self.values).items():
            self.tables[u, v] = {(p, q): requirements(u, v, p, q, rows)
                                 for p in self.domains[u] for q in self.domains[v]}

    def propagate(self, domains, fixed):
        changed = True
        while changed:
            self.propagations += 1
            if time.monotonic() > self.deadline:
                raise TimeoutError
            changed = False
            for u in range(self.n):
                keep = {p for p in domains[u] if u in domains[p]}
                if not keep:
                    return None
                if keep != domains[u]:
                    domains[u] = keep
                    changed = True
            for (u, v), table in self.tables.items():
                pairs = []
                for p in domains[u]:
                    for q in domains[v]:
                        mask = table[p, q]
                        if mask is not None and not ((mask | fixed) & ((mask | fixed) << 1)):
                            pairs.append((p, q, mask))
                if not pairs:
                    return None
                for vertex, index in ((u, 0), (v, 1)):
                    keep = {pair[index] for pair in pairs}
                    if keep != domains[vertex]:
                        domains[vertex] = keep
                        changed = True
                forced = (1 << self.n) - 1
                for _, _, mask in pairs:
                    forced &= mask
                if forced & ~fixed:
                    fixed |= forced
                    if fixed & (fixed << 1):
                        return None
                    changed = True
        return fixed

    def search(self, domains, fixed=0):
        self.nodes += 1
        fixed = self.propagate(domains, fixed)
        if fixed is None:
            return None
        undecided = [u for u in range(self.n) if len(domains[u]) > 1]
        if not undecided:
            first = [(u, next(iter(domain))) for u, domain in enumerate(domains) if u < next(iter(domain))]
            last = [(a, a + 1) for a in range(self.n - 1) if fixed >> a & 1]
            suffix = [first, last]
            assert all(run_bits(suffix, x) == ((1 << x.bit_count()) - 1) << (self.n - x.bit_count())
                       for x in self.values)
            return suffix
        u = min(undecided, key=lambda v: len(domains[v]))
        for p in sorted(domains[u]):
            child = [set(d) for d in domains]
            child[u], child[p] = {p}, {u}
            found = self.search(child, fixed)
            if found is not None:
                return found
        return None

    def solve(self):
        try:
            suffix = self.search([set(d) for d in self.domains])
            status = 'SAT' if suffix is not None else 'UNSAT'
        except TimeoutError:
            suffix, status = None, 'TIME_LIMIT'
        return dict(status=status, suffix=suffix, seconds=time.monotonic() - self.start,
                    search_nodes=self.nodes, propagation_rounds=self.propagations,
                    required_pairs=len(self.tables), forbidden_by_rectangle=len(self.forbidden),
                    initial_domains=[sorted(d) for d in self.domains])


def cube_certificate(n, prefix):
    sources = images_with_witness(n, prefix)
    face = next(cubes(n, sources))
    result = dict(n=n, prefix=prefix, obstruction='THREE_CUBE', **face,
                  inputs=[sources[x] for x in face['corners']])
    verify_cube_certificate(result)
    return result


def verify_cube_certificate(record):
    n, prefix = record['n'], record['prefix']
    for layer in prefix:
        used = set()
        for a, b in layer:
            assert 0 <= a < b < n and a not in used and b not in used
            used.update((a, b))
    axes, base = record['axes'], record['base']
    assert len(axes) == len(set(axes)) == 3 and all(0 <= a < n for a in axes)
    assert 0 <= base < 1 << n and all(not (base >> a & 1) for a in axes)
    expected = {base | sum(1 << a for i, a in enumerate(axes) if mask >> i & 1) for mask in range(8)}
    assert set(record['corners']) == expected and len(record['inputs']) == len(record['corners']) == 8
    for source, output in zip(record['inputs'], record['corners']):
        assert 0 <= source < 1 << n and run_bits(prefix, source) == output
    return True


def check():
    from two_layer_topology import obstructions
    count = satisfiable = 0
    for n in (3, 4):
        layers = matchings(n)
        for depth in range(4):
            for prefix in itertools.product(layers, repeat=depth):
                values = images(n, prefix)
                assert set(edges_and_examples(n, values)) == set(inversion_edges(n, values))
                reference = any(len({run_bits([first, last], x) for x in values}) == n + 1
                                for first in layers for last in layers)
                result = Completion(n, values).solve()
                assert result['status'] == ('SAT' if reference else 'UNSAT'), (n, prefix, result)
                if reference:
                    assert not obstructions(n, edges_and_examples(n, values))['rules_out_two_layers']
                    assert next(cubes(n, values), None) is None
                # Check every rectangle exclusion against every actual completion.
                for first in layers:
                    if not set(first) & set(rectangle_forbidden(n, values)):
                        continue
                    assert not any(len({run_bits([first, last], x) for x in values}) == n + 1 for last in layers)
                count += 1
                satisfiable += reference
    five_checked = five_sat = 0
    layers = matchings(5)
    for second, third in itertools.product(layers, repeat=2):
        values = images(5, [[(0, 1), (2, 3)], second, third])
        assert set(edges_and_examples(5, values)) == set(inversion_edges(5, values))
        reference = any(len({run_bits([first, last], x) for x in values}) == 6
                        for first in layers for last in layers)
        result = Completion(5, values).solve()
        assert result['status'] == ('SAT' if reference else 'UNSAT')
        if reference:
            assert not obstructions(5, edges_and_examples(5, values))['rules_out_two_layers']
            assert next(cubes(5, values), None) is None
        five_checked += 1
        five_sat += reference
    cube_record = json.loads((Path(__file__).parent / 'results/three-cube-certificate18.json').read_text())
    assert verify_cube_certificate(cube_record)
    corrupted = json.loads(json.dumps(cube_record))
    corrupted['corners'][0] ^= 1
    try:
        verify_cube_certificate(corrupted)
    except AssertionError:
        pass
    else:
        raise AssertionError('corrupted cube certificate accepted')
    return dict(exhaustive_prefixes=count, completable_prefixes=satisfiable,
                five_wire_canonical_first_layer_prefixes=five_checked, five_wire_completable=five_sat,
                unrestricted_matching_enumeration_agrees=True, rectangle_exclusions_checked=True,
                inversion_graph_equality_checked=True, positive_topology_and_cube_checks=True,
                cube_certificate_runs=8, corrupted_cube_rejected=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--network', type=Path)
    parser.add_argument('--prefix-depth', type=int)
    parser.add_argument('--limit', type=float, default=5)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.check:
        result = check()
    elif args.network:
        record = json.loads(args.network.read_text())
        prefix = record.get('prefix', record.get('network', record.get('layers')))
        if args.prefix_depth is not None:
            prefix = prefix[:args.prefix_depth]
        result = Completion(record['n'], images(record['n'], prefix), args.limit).solve()
        result.update(n=record['n'], prefix=prefix)
    else:
        parser.error('choose --check or --network')
    if args.out:
        args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
