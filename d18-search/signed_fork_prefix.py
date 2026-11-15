#!/usr/bin/env python3
"""Find explicit signed-fork families after fully blinded fixed prefixes.

First-layer normalized placements are exhaustively generated. A found
family is independently replayed; a missing family is only a limitation
of this specific obstruction, not evidence of a sorting completion.
"""
import argparse
from collections import defaultdict
import hashlib
from itertools import combinations
import json
from pathlib import Path
import time


def validate(n, layers):
    for layer in layers:
        assert all(0 <= a < b < n for a, b in layer)
        used = [v for edge in layer for v in edge]
        assert len(used) == len(set(used))


def encode(state):
    return (sum(1 << v for v, t in enumerate(state) if t < 0),
            sum(1 << v for v, t in enumerate(state) if t > 0))


def decode(n, key):
    minus, plus = key
    assert not minus & plus
    return [-1 if minus >> v & 1 else 1 if plus >> v & 1 else 0 for v in range(n)]


def replay(layers, initial):
    state = list(initial)
    trace = [state.copy()]
    counts = []
    for layer in layers:
        counts.append(sum(state[a] == state[b] == 0 for a, b in layer))
        for a, b in layer:
            state[a], state[b] = min(state[a], state[b]), max(state[a], state[b])
        trace.append(state.copy())
    return state, counts, trace


def blind_states(n, layers, reals):
    validate(n, layers)
    assert layers and 0 <= reals <= n
    first = layers[0]
    used = {v for edge in first for v in edge}
    blocks = [(tuple(edge), ((-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1)))
              for edge in first]
    blocks += [((v,), ((-1,), (0,), (1,))) for v in range(n) if v not in used]
    initial = [0] * n
    outputs = {}
    placements = 0
    accepted = 0

    def generate(i, real_count):
        nonlocal placements, accepted
        if real_count > reals or real_count + len(blocks) - i < reals:
            return
        if i == len(blocks):
            placements += 1
            state = initial.copy()
            for layer in layers[1:]:
                for a, b in layer:
                    if state[a] == state[b] == 0:
                        return
                    if state[a] > state[b]:
                        state[a], state[b] = state[b], state[a]
            accepted += 1
            outputs.setdefault(encode(state), tuple(initial))
            return
        vertices, choices = blocks[i]
        for values in choices:
            for v, t in zip(vertices, values):
                initial[v] = t
            generate(i + 1, real_count + values.count(0))

    generate(0, 0)
    return outputs, dict(normalized_placements=placements,
                         fully_blind_placements=accepted,
                         distinct_cut_states=len(outputs))


def recognize(n, reals, states):
    """Exact recognition of the twenty-state theorem's literal pattern."""
    if reals < 7 or n-reals < 3 or len(states) < 20:
        return None, dict(candidate_fixed_sentinel_groups=0)
    groups = defaultdict(list)
    for minus, plus in states:
        sentinel_vertices = [v for v in range(n) if (minus | plus) >> v & 1]
        assert len(sentinel_vertices) == n-reals
        for triple in combinations(sentinel_vertices, 3):
            mask = sum(1 << v for v in triple)
            key = (minus & ~mask, plus & ~mask)
            literals = tuple(2*v + int(plus >> v & 1) for v in triple)
            groups[key].append(literals)
    eligible = [(core, triples) for core, triples in groups.items() if len(triples) >= 20]
    stats = dict(candidate_fixed_sentinel_groups=len(eligible),
                 maximum_group_states=max(map(len, groups.values()), default=0))
    even_bits = sum(1 << (2*v) for v in range(n))

    def positions_count(mask):
        return ((mask | mask >> 1) & even_bits).bit_count()

    def exclude(mask, literals):
        for lit in literals:
            mask &= ~(3 << (2*(lit//2)))
        return mask

    for core, triples in eligible:
        links = defaultdict(int)
        for triple in triples:
            for i in range(3):
                pair = tuple(sorted(triple[j] for j in range(3) if j != i))
                links[pair] |= 1 << triple[i]
        neighbors = defaultdict(list)
        for (a, b), mask in links.items():
            if positions_count(mask) >= 5:
                neighbors[a].append(b)
                neighbors[b].append(a)

        def link(a, b):
            return links.get(tuple(sorted((a, b))), 0)

        for b in sorted(neighbors):
            for a in neighbors[b]:
                if a % 2 != b % 2:
                    continue
                for c in neighbors[b]:
                    if c % 2 == b % 2 or len({a//2, b//2, c//2}) != 3:
                        continue
                    pair_mask = exclude(link(a, b) & link(b, c), (a, b, c))
                    if positions_count(pair_mask) < 5:
                        continue
                    for d in neighbors[b]:
                        if d % 2 != c % 2 or len({a//2,b//2,c//2,d//2}) != 4:
                            continue
                        three_mask = exclude(pair_mask & link(b, d), (d,))
                        if positions_count(three_mask) < 5:
                            continue
                        for e in neighbors[c]:
                            if e % 2 != c % 2 or len({a//2,b//2,c//2,d//2,e//2}) != 5:
                                continue
                            common = exclude(three_mask & link(c, e), (e,))
                            if positions_count(common) < 5:
                                continue
                            B = []
                            for v in range(n):
                                choices = [2*v+s for s in (0, 1) if common >> (2*v+s) & 1]
                                if choices:
                                    B.append(choices[0])
                            B = B[:5]
                            return dict(A_literals=[a,b,c,d,e], B_literals=B,
                                        fixed_sentinels=list(core)), stats
    return None, stats


def certificate(n, reals, layers, states, pattern):
    a,b,c,d,e = pattern['A_literals']
    rows = ((a,b),(b,c),(c,e),(b,d))
    core = tuple(pattern['fixed_sentinels'])
    placements = []
    for row in rows:
        for q in pattern['B_literals']:
            key = list(core)
            for lit in (*row,q):
                key[lit % 2] |= 1 << (lit//2)
            key = tuple(key)
            assert key in states
            initial = states[key]
            final, counts, trace = replay(layers, initial)
            assert not any(counts) and encode(final) == key
            assert final.count(0) == reals
            placements.append(dict(initial=list(initial), cut=final, retained_counts=counts))
    assert len({tuple(p['cut']) for p in placements}) == 20
    return dict(**pattern, placements=placements,
                common_reals=sorted(set(range(n)) -
                    {lit//2 for lit in pattern['A_literals']+pattern['B_literals']} -
                    {v for v in range(n) if (core[0]|core[1]) >> v & 1}))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--case', type=int)
    ap.add_argument('--cut', type=int, required=True)
    ap.add_argument('--reals', type=int, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    start = time.monotonic()
    raw = args.input.read_text()
    record = json.loads(raw.splitlines()[args.case]) if args.case is not None else json.loads(raw)
    n = record['n']
    layers = (record.get('layers') or record.get('network'))[:args.cut]
    assert len(layers) == args.cut
    states, counts = blind_states(n, layers, args.reals)
    pattern, stats = recognize(n, args.reals, states)
    result = dict(status='FORK_FOUND' if pattern else 'NO_EXACT_FORK', n=n,
                  reals=args.reals, cut=args.cut, layers=layers, **counts, **stats,
                  scope='Exact theorem pattern after a fixed fully blinded prefix; absence is not a sorting witness',
                  sat_used=False, input_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    if pattern:
        result['certificate'] = certificate(n, args.reals, layers, states, pattern)
    result['seconds'] = round(time.monotonic()-start, 4)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('certificate','layers')}))


if __name__ == '__main__':
    main()
