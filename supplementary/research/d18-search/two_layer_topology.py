#!/usr/bin/env python3
"""Hand-checkable topology obstructions for two-layer sorting completion.

The proof uses the nonredundant last-layer normal forms of Codish et al.
This is a necessary-condition filter, not a full D(18) verification.
"""
import argparse
import itertools
import json
from pathlib import Path

from two_real_graph import (collision_host, edges_and_examples, images,
                            images_with_witness, matchings, parity_obstruction,
                            run_bits)


def adjacent_matchings(n, start=0):
    if start >= n:
        yield []
        return
    yield from adjacent_matchings(n, start + 1)
    if start + 1 < n:
        for rest in adjacent_matchings(n, start + 2):
            yield [(start, start + 1)] + rest


def matching_blocks(n, layer):
    blocks = [tuple(e) for e in layer]
    used = {a for edge in layer for a in edge}
    blocks += [(a,) for a in range(n) if a not in used]
    blocks.sort()
    owner = {v: k for k, block in enumerate(blocks) for v in block}
    return blocks, owner


def normal_last_two(n, first, last):
    if any(b != a + 1 for a, b in last):
        return False
    _, owner = matching_blocks(n, last)
    # A comparator within a last-layer pair would make that final gate
    # redundant. Remaining penultimate gates join adjacent final blocks.
    return all(abs(owner[a] - owner[b]) == 1 for a, b in first)


def host_paths(n, first, last):
    """Produce the path of one/two-vertex bags, checking all claims exactly."""
    assert normal_last_two(n, first, last)
    blocks, owner = matching_blocks(n, first)
    adjacent = [set() for _ in blocks]
    for a, b in last:
        i, j = owner[a], owner[b]
        assert i != j
        adjacent[i].add(j)
        adjacent[j].add(i)
    assert all(len(a) <= 2 for a in adjacent)
    remaining = set(range(len(blocks)))
    paths = []
    while remaining:
        start = next((i for i in sorted(remaining) if len(adjacent[i]) <= 1), None)
        assert start is not None, 'a cycle of three or more first-layer bags'
        path, previous, current = [], None, start
        while current is not None:
            assert current in remaining
            remaining.remove(current)
            path.append(list(blocks[current]))
            nxt = adjacent[current] - ({previous} if previous is not None else set())
            assert len(nxt) <= 1
            previous, current = current, next(iter(nxt), None)
        paths.append(path)
    host = set()
    for path in paths:
        for block in path:
            host.update(itertools.combinations(block, 2))
        for left, right in zip(path, path[1:]):
            host.update(tuple(sorted((a, b))) for a in left for b in right)
    return paths, host


def edge_limit(n):
    return 0 if n < 2 else 5 * n // 2 - 4


def distances(neighbors, root):
    distance, queue = {root: 0}, [root]
    for v in queue:
        for a in sorted(neighbors[v] - distance.keys()):
            distance[a] = distance[v] + 1
            queue.append(a)
    return distance


def obstructions(n, edges):
    edges = {tuple(sorted(e)) for e in edges}
    neighbors = [set() for _ in range(n)]
    for a, b in edges:
        neighbors[a].add(b)
        neighbors[b].add(a)
    clique = next((list(c) for c in itertools.combinations(range(n), 5)
                   if all(b in neighbors[a] for a, b in itertools.combinations(c, 2))), None)
    bipartite = None
    for left in itertools.combinations(range(n), 3):
        common = set.intersection(*(neighbors[a] for a in left)) - set(left)
        if len(common) >= 3:
            bipartite = [list(left), sorted(common)[:3]]
            break
    def independent(vertices):
        return all(b not in neighbors[a] for a, b in itertools.combinations(vertices, 2))
    claw4 = next(([center, list(leaves)] for center in range(n)
                  for leaves in itertools.combinations(sorted(neighbors[center]), 4)
                  if independent(leaves)), None)
    induced_k23 = None
    for a, b in itertools.combinations(range(n), 2):
        if b in neighbors[a]:
            continue
        for right in itertools.combinations(sorted(neighbors[a] & neighbors[b]), 3):
            if independent(right):
                induced_k23 = [[a, b], list(right)]
                break
        if induced_k23:
            break
    core = set(range(n))
    while True:
        remove = {i for i in core if len(neighbors[i] & core) < 4}
        if not remove:
            break
        core -= remove
    large_balls = []
    for root in range(n):
        distance = distances(neighbors, root)
        for radius in range(1, (n - 3) // 4 + 1):
            ball = sorted(v for v, d in distance.items() if d <= radius)
            if len(ball) > 4 * radius + 2:
                large_balls.append(dict(root=root, radius=radius, vertices=ball, limit=4 * radius + 2))
    return dict(edge_count=len(edges), edge_limit=edge_limit(n),
                too_many_edges=len(edges) > edge_limit(n), k5=clique, k33=bipartite,
                induced_k14=claw4, induced_k23=induced_k23,
                four_core=sorted(core), oversized_balls=large_balls,
                rules_out_two_layers=bool(len(edges) > edge_limit(n) or clique or bipartite or core
                                         or large_balls or claw4 or induced_k23))


def certificate(n, prefix, kind, vertices):
    sources = images_with_witness(n, prefix)
    examples = edges_and_examples(n, sources)
    if kind == 'K5':
        needed = list(itertools.combinations(vertices, 2))
    else:
        assert kind == 'K33'
        needed = [tuple(sorted(e)) for e in itertools.product(*vertices)]
    requirements = []
    for edge in needed:
        corners = examples[edge]
        requirements.append(dict(pair=edge, outputs=corners, inputs=[sources[x] for x in corners]))
    result = dict(n=n, prefix=prefix, obstruction=kind, vertices=vertices, requirements=requirements)
    verify_certificate(result)
    return result


def ball_certificate(n, prefix, root, radius):
    sources = images_with_witness(n, prefix)
    examples = edges_and_examples(n, sources)
    neighbors = [set() for _ in range(n)]
    for a, b in examples:
        neighbors[a].add(b)
        neighbors[b].add(a)
    distance = distances(neighbors, root)
    ordered = sorted(distance, key=lambda v: (distance[v], v))
    vertices = ordered[:4 * radius + 3]
    assert len(vertices) == 4 * radius + 3 and distance[vertices[-1]] <= radius
    needed = []
    for v in vertices[1:]:
        parent = min(a for a in neighbors[v] if distance.get(a) == distance[v] - 1)
        assert parent in vertices
        needed.append(tuple(sorted((parent, v))))
    requirements = []
    for edge in needed:
        corners = examples[edge]
        requirements.append(dict(pair=edge, outputs=corners, inputs=[sources[x] for x in corners]))
    result = dict(n=n, prefix=prefix, obstruction='BALL', root=root, radius=radius,
                  vertices=vertices, requirements=requirements)
    verify_certificate(result)
    return result


def verify_certificate(record):
    n, prefix = record['n'], record['prefix']
    for layer in prefix:
        used = set()
        for a, b in layer:
            assert 0 <= a < b < n and a not in used and b not in used
            used.update((a, b))
    vertices = record['vertices']
    if record['obstruction'] == 'K5':
        assert len(vertices) == len(set(vertices)) == 5
        required = {tuple(sorted(e)) for e in itertools.combinations(vertices, 2)}
    elif record['obstruction'] == 'K33':
        assert len(vertices) == 2 and all(len(p) == len(set(p)) == 3 for p in vertices)
        assert set(vertices[0]).isdisjoint(vertices[1])
        required = {tuple(sorted(e)) for e in itertools.product(*vertices)}
    else:
        assert record['obstruction'] == 'BALL'
        assert len(vertices) == len(set(vertices)) > 4 * record['radius'] + 2
        assert record['radius'] >= 1 and all(0 <= a < n for a in vertices)
        required = set()
    witnessed = set()
    for requirement in record['requirements']:
        a, b = requirement['pair']
        assert 0 <= a < b < n
        x, y = requirement['outputs']
        u, v = requirement['inputs']
        assert 0 <= u < 1 << n and 0 <= v < 1 << n
        assert run_bits(prefix, u) == x and run_bits(prefix, v) == y
        assert x.bit_count() == y.bit_count() and x ^ y == (1 << a) | (1 << b)
        witnessed.add((a, b))
    assert required <= witnessed
    if record['obstruction'] == 'BALL':
        neighbors = [set() for _ in range(n)]
        for a, b in witnessed:
            neighbors[a].add(b)
            neighbors[b].add(a)
        assert 0 <= record['root'] < n
        distance = distances(neighbors, record['root'])
        assert all(distance.get(a, n + 1) <= record['radius'] for a in vertices)
    return True


def check():
    counts = {}
    for n in range(2, 9):
        checked = 0
        all_first = matchings(n)
        for last in adjacent_matchings(n):
            for first in all_first:
                if not normal_last_two(n, first, last):
                    continue
                paths, host = host_paths(n, first, last)
                assert host == collision_host(n, [first, last])
                assert not obstructions(n, host)['rules_out_two_layers']
                assert not parity_obstruction(n, host)['rules_out_two_layers']
                # The bags give a vertex order of bandwidth at most three.
                order = [v for path in paths for bag in path for v in bag]
                positions = {v: i for i, v in enumerate(order)}
                assert all(abs(positions[a] - positions[b]) <= 3 for a, b in host)
                checked += 1
        counts[n] = checked

    # Control: without final-layer normal forms an alternating six-cycle
    # has collision host K6. Its K5/K33 subgraphs escape degree and parity.
    arbitrary = collision_host(6, [[(0, 1), (2, 3), (4, 5)], [(1, 2), (3, 4), (0, 5)]])
    assert len(arbitrary) == 15 and not normal_last_two(6, [(0, 1), (2, 3), (4, 5)], [(1, 2), (3, 4), (0, 5)])
    k5 = set(itertools.combinations(range(5), 2))
    k33 = set(itertools.product(range(3), range(3, 6)))
    for graph in [k5, k33]:
        assert graph <= arbitrary and not parity_obstruction(6, graph)['rules_out_two_layers']
        assert obstructions(6, graph)['rules_out_two_layers']
    # Nonredundant matching constraints strengthen unsigned routing:
    # an induced K2,3 and a four-leaf star are forbidden too.
    k25 = {(a, b) for a in range(2) for b in range(2, 7)}
    assert parity_obstruction(7, k25)['rules_out_two_layers']
    assert obstructions(7, k25)['induced_k23']
    assert obstructions(5, {(0, b) for b in range(1, 5)})['induced_k14']

    positive = json.loads((Path(__file__).parent / 'results/prefix-parity-crosschecks.json').read_text())[1]['network']
    paths, host = host_paths(18, *positive[-2:])
    required = edges_and_examples(18, images(18, positive[:-2]))
    assert set(required) <= host and not obstructions(18, required)['rules_out_two_layers']
    result = dict(normal_suffixes_by_width=counts, normal_suffixes=sum(counts.values()),
                  known_18_wire_positive=dict(required_edges=len(required), host_edges=len(host), host_paths=paths),
                  arbitrary_cycle_negative_control=True, induced_obstruction_controls=True)
    certificate_checks = []
    for name in ['two-real-k5-certificate6.json', 'two-real-ball-certificate18.json']:
        record = json.loads((Path(__file__).parent / 'results' / name).read_text())
        assert verify_certificate(record)
        corrupted = json.loads(json.dumps(record))
        corrupted['requirements'][0]['outputs'][0] ^= 1
        try:
            verify_certificate(corrupted)
        except AssertionError:
            pass
        else:
            raise AssertionError('corrupted certificate was accepted')
        certificate_checks.append(dict(file=name, binary_runs=2 * len(record['requirements']), corruption_rejected=True))
    result['certificate_checks'] = certificate_checks
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.check:
        result = check()
        if args.out:
            args.out.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
