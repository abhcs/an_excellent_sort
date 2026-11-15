#!/usr/bin/env python3
"""Exact two-real collision criterion and structural completion obstructions.

No SAT dependency. A pair edge joins two channels which can hold the differing
bits of two equal-weight binary prefix outputs. Every such pair must collide
in any sorting suffix. See two-real-hand-proofs.md for the proofs and scope.
"""
import argparse
from collections import Counter, deque
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'depth-hand-proofs/verify'))
from netlib import matchings


def run_bits(net, x):
    for layer in net:
        for a, b in layer:
            if x >> a & 1 and not (x >> b & 1):
                x ^= (1 << a) | (1 << b)
    return x


def sorted_bits(n, weight):
    return ((1 << weight) - 1) << (n - weight)


def images(n, net):
    if not net:
        return set(range(1 << n))
    first = net[0]
    free = sorted(set(range(n)) - {a for edge in first for a in edge})
    values = set()
    for states in itertools.product((0, 1, 2), repeat=len(first)):
        base = 0
        for (a, b), state in zip(first, states):
            if state >= 1:
                base |= 1 << b
            if state == 2:
                base |= 1 << a
        for idle in itertools.product((0, 1), repeat=len(free)):
            values.add(base | sum(bit << a for a, bit in zip(free, idle)))
    for layer in net[1:]:
        values = {run_bits([layer], x) for x in values}
    return values


def images_with_witness(n, net):
    if not net:
        return {x:x for x in range(1 << n)}
    current = {x:x for x in images(n, net[:1])}
    for layer in net[1:]:
        nxt = {}
        for value, source in current.items():
            nxt.setdefault(run_bits([layer], value), source)
        current = nxt
    return current


def edges_and_examples(n, values):
    edges = {}
    for x in sorted(values):
        for a in range(n):
            if not (x >> a & 1):
                continue
            for b in range(a + 1, n):
                if x >> b & 1:
                    continue
                y = x ^ (1 << a) ^ (1 << b)
                if y in values:
                    edges.setdefault((a, b), (x, y))
    return edges


def inversion_edges(n, values):
    """The same graph, certified by one inverted output per edge."""
    result = {}
    for x in sorted(values):
        for a in range(n):
            if x >> a & 1:
                for b in range(a + 1, n):
                    if not (x >> b & 1):
                        result.setdefault((a, b), x)
    return result


def components(n, edges):
    parent = list(range(n))
    def root(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for a, b in edges:
        parent[root(a)] = root(b)
    groups = {}
    for a in range(n):
        groups.setdefault(root(a), []).append(a)
    return sorted(groups.values())


def parity_obstruction(n, edges):
    """Degree-five closed neighborhoods must be unions of penultimate pairs."""
    neighbors = [set() for _ in range(n)]
    for a, b in edges:
        neighbors[a].add(b)
        neighbors[b].add(a)
    centers = [a for a, adjacent in enumerate(neighbors) if len(adjacent) == 5]
    six_sets = [{a} | neighbors[a] for a in centers]
    cells = {}
    for a in range(n):
        signature = tuple(i for i, six in enumerate(six_sets) if a in six)
        cells.setdefault(signature, []).append(a)
    odd_cells = [dict(members=members, included_in=list(signature))
                 for signature, members in cells.items() if signature and len(members) % 2]
    odd_intersections = [dict(first=sorted(a), second=sorted(b), intersection=sorted(a & b))
                         for i, a in enumerate(six_sets) for b in six_sets[i + 1:]
                         if len(a & b) % 2]
    return dict(six_sets=[sorted(s) for s in six_sets], six_set_centers=centers, odd_cells=odd_cells,
                odd_intersections=odd_intersections,
                rules_out_two_layers=bool(odd_cells))


def blind_trace(net, state):
    current = list(state)
    trace = [list(current)]
    for layer in net:
        if any(current[a] == current[b] == 0 for a, b in layer):
            return None
        for a, b in layer:
            current[a], current[b] = min(current[a], current[b]), max(current[a], current[b])
        trace.append(list(current))
    return trace


def placements(n):
    for a, b in itertools.combinations(range(n), 2):
        rest = [i for i in range(n) if i not in (a, b)]
        for signs in itertools.product((-1, 1), repeat=n - 2):
            state = [0] * n
            for i, sign in zip(rest, signs):
                state[i] = sign
            yield state


def failure_to_blind(n, net, failure):
    """At most floor(n/2)+1 evaluations turn a binary failure into a proof witness."""
    anchor = sorted_bits(n, failure.bit_count())
    assert run_bits(net, failure) != anchor
    current = failure
    current_out = run_bits(net, current)
    steps = 0
    while current != anchor:
        extra = current & ~anchor
        missing = anchor & ~current
        a = (extra & -extra).bit_length() - 1
        b = (missing & -missing).bit_length() - 1
        nxt = current ^ (1 << a) ^ (1 << b)
        next_out = run_bits(net, nxt)
        steps += 1
        if next_out != current_out:
            state = [0 if i in (a, b) else (1 if current >> i & 1 else -1) for i in range(n)]
            trace = blind_trace(net, state)
            assert trace is not None
            return dict(placement=state, trace=trace, binary_corners=[current, nxt],
                        corner_outputs=[current_out, next_out], path_steps=steps)
        current, current_out = nxt, next_out
    raise AssertionError('a failed input and the sorted anchor cannot have identical outputs')


def collision_host(n, suffix):
    """Pairs that could meet with arbitrary routing choices, ignoring sentinel signs."""
    edges = set()
    for a, b in itertools.combinations(range(n), 2):
        states = {(a, b)}
        possible = False
        for layer in suffix:
            partner = {i: j for x, y in layer for i, j in ((x, y), (y, x))}
            nxt = set()
            for x, y in states:
                if partner.get(x) == y:
                    possible = True
                    break
                for xx in {x, partner.get(x, x)}:
                    for yy in {y, partner.get(y, y)}:
                        if xx != yy:
                            nxt.add(tuple(sorted((xx, yy))))
            if possible:
                break
            states = nxt
        if possible:
            edges.add((a, b))
    return edges


def analyse(n, prefix):
    from two_layer_topology import obstructions
    sources = images_with_witness(n, prefix)
    values = set(sources)
    examples = edges_and_examples(n, values)
    degree = [sum(i in edge for edge in examples) for i in range(n)]
    groups = components(n, examples)
    assert all(group == list(range(min(group), max(group) + 1)) for group in groups)
    worst = max(range(n), key=lambda i: degree[i])
    def edge_certificate(edge):
        corners = examples[edge]
        return dict(pair=edge, outputs=corners, inputs=[sources[x] for x in corners])
    star = [edge_certificate(edge) for edge in sorted(examples) if worst in edge]
    parity = parity_obstruction(n, examples)
    topology = obstructions(n, examples)
    result = dict(n=n, prefix=prefix, prefix_depth=len(prefix), outputs=len(values),
                pair_edges=len(examples), degree=degree, max_degree=degree[worst],
                interval_blocks=groups, star_vertex=worst, star_certificate=star,
                parity=parity, topology=topology,
                two_layer_completion_ruled_out=degree[worst] > 5 or parity['rules_out_two_layers']
                    or topology['rules_out_two_layers'])
    if parity['odd_intersections']:
        chosen = min(parity['odd_intersections'], key=lambda x:len(x['intersection']))
        stars = []
        for key in ('first', 'second'):
            index = parity['six_sets'].index(chosen[key])
            center = parity['six_set_centers'][index]
            stars.append(dict(center=center, requirements=[edge_certificate(e) for e in sorted(examples) if center in e]))
        result['parity_certificate'] = dict(n=n, prefix=prefix, stars=stars)
        verify_parity_certificate(result['parity_certificate'])
    return result


def verify_parity_certificate(certificate):
    """Check only 20 explicitly supplied binary runs, not an enumerated output set."""
    n, prefix = certificate['n'], certificate['prefix']
    for layer in prefix:
        used = set()
        for a, b in layer:
            assert 0 <= a < b < n and a not in used and b not in used
            used.update((a, b))
    sets = []
    for star in certificate['stars']:
        center = star['center']
        neighbors = set()
        assert len(star['requirements']) == 5
        for requirement in star['requirements']:
            a, b = requirement['pair']
            assert a < b and center in (a, b)
            neighbors.add(b if a == center else a)
            x, y = requirement['outputs']
            u, v = requirement['inputs']
            assert 0 <= u < 1 << n and 0 <= v < 1 << n
            assert run_bits(prefix, u) == x and run_bits(prefix, v) == y
            assert x.bit_count() == y.bit_count()
            assert x ^ y == (1 << a) | (1 << b)
        assert len(neighbors) == 5 and center not in neighbors
        sets.append(neighbors | {center})
    assert len(sets) == 2 and len(sets[0] & sets[1]) % 2 == 1
    return True


def small_checks():
    checked = 0
    for n in (3, 4):
        layers = matchings(n)
        for depth in range(4):
            for net in itertools.product(layers, repeat=depth):
                values = images(n, net)
                sorts = len(values) == n + 1
                surviving = [s for s in placements(n) if blind_trace(net, s) is not None]
                assert sorts == (not surviving)
                graph = edges_and_examples(n, values)
                assert set(graph) == set(inversion_edges(n, values))
                blocks = components(n, graph)
                blind_edges = set()
                for state in surviving:
                    final = blind_trace(net, state)[-1]
                    blind_edges.add(tuple(i for i, x in enumerate(final) if x == 0))
                assert blind_edges <= set(graph)
                assert components(n, blind_edges) == blocks
                assert all(b == list(range(min(b), max(b) + 1)) for b in blocks)
                if not sorts:
                    failure = next(x for x in range(1 << n) if run_bits(net, x) != sorted_bits(n, x.bit_count()))
                    failure_to_blind(n, net, failure)
                if depth:
                    before = edges_and_examples(n, images(n, net[:-1]))
                    assert sorts == (set(before) <= {tuple(e) for e in net[-1]})
                checked += 1
    host_checks = 0
    for n in range(3, 7):
        layers = matchings(n)
        for first in layers:
            for second in layers:
                host = collision_host(n, [first, second])
                assert max(sum(i in e for e in host) for i in range(n)) <= 5
                assert not parity_obstruction(n, host)['rules_out_two_layers']
                host_checks += 1
    # An explicit obstruction missed by the maximum-degree bound: K_{2,5}.
    forbidden = {(a, b) for a in (0, 1) for b in range(2, 7)}
    assert parity_obstruction(7, forbidden)['rules_out_two_layers']
    rng = random.Random(20261115)
    for _ in range(500):
        suffix = []
        for _ in range(2):
            order = list(range(18))
            rng.shuffle(order)
            suffix.append([tuple(sorted(order[i:i + 2])) for i in range(0, 18, 2)])
        host = collision_host(18, suffix)
        assert not parity_obstruction(18, host)['rules_out_two_layers']
        subgraph = {edge for edge in host if rng.randrange(4)}
        assert not parity_obstruction(18, subgraph)['rules_out_two_layers']
    print(f'{checked} complete small networks and {host_checks} two-layer collision hosts checked', flush=True)
    return dict(networks=checked, two_layer_hosts=host_checks, random_18_wire_hosts=500)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--network', type=Path)
    ap.add_argument('--prefix-depth', type=int)
    ap.add_argument('--out', type=Path)
    args = ap.parse_args()
    if args.check:
        small_checks()
    if args.network:
        record = json.loads(args.network.read_text())
        net = record.get('network', record.get('layers'))
        if args.prefix_depth is not None:
            net = net[:args.prefix_depth]
        result = analyse(record['n'], net)
        result['source_sha256'] = hashlib.sha256(args.network.read_bytes()).hexdigest()
        if args.out:
            args.out.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({k:v for k,v in result.items() if k not in ('prefix','star_certificate','parity_certificate')}), flush=True)


if __name__ == '__main__':
    main()
