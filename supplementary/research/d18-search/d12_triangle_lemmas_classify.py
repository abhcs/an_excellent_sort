#!/usr/bin/env python3
"""Canonicalize small triangle matching obstructions by incidence masks."""
import argparse
from collections import Counter, defaultdict
import itertools
import json
from pathlib import Path


def canonical(triangles):
    vertices = sorted(set().union(*map(set, triangles)))
    masks = [sum(1 << i for i, tri in enumerate(triangles) if v in tri) for v in vertices]
    best = None
    for perm in itertools.permutations(range(len(triangles))):
        changed = tuple(sorted(sum(1 << perm[i] for i in range(len(perm)) if mask >> i & 1)
                               for mask in masks))
        if best is None or changed < best:
            best = changed
    normalized = tuple(tuple(v for v, mask in enumerate(best) if mask >> i & 1)
                       for i in range(len(triangles)))
    return best, normalized


def prices(triangles):
    n = len(set().union(*map(set, triangles)))
    weights = Counter(pair for tri in triangles for pair in itertools.combinations(tri, 2))
    adjacency = defaultdict(dict)
    for (a, b), weight in weights.items():
        adjacency[a][b] = adjacency[b][a] = 2 * weight
    order = sorted(range(n), key=lambda v: (-sum(adjacency[v].values()), -len(adjacency[v])))
    assigned = {}
    budget = 2 * len(triangles) - 1

    def rec(index, remaining):
        if index == n:
            return dict(assigned)
        v = order[index]
        low = max([0, *(weight - assigned[u] for u, weight in adjacency[v].items() if u in assigned)])
        future = order[index + 1:]
        for value in range(low, remaining + 1):
            assigned[v] = value
            bounds = {u: max([0, *(w - assigned[z] for z, w in adjacency[u].items() if z in assigned)])
                      for u in future}
            if sum(bounds.values()) <= remaining - value:
                found = rec(index + 1, remaining - value)
                if found is not None:
                    return found
            del assigned[v]
        return None
    result = rec(0, budget)
    if result is not None:
        assert sum(result.values()) < 2 * len(triangles)
        assert all(result[a] + result[b] >= 2 * w for (a, b), w in weights.items())
    return result


def main(source, out):
    groups = {}
    for line in source.read_text().splitlines():
        entry = json.loads(line)
        key, normalized = canonical(entry['triangles'])
        if key not in groups:
            groups[key] = dict(triangles=normalized, labelled_cores=0, matching_count=0,
                               example=entry)
        groups[key]['labelled_cores'] += 1
        groups[key]['matching_count'] += entry['count']
    records = []
    for key, group in sorted(groups.items(), key=lambda item:(len(item[1]['triangles']),item[0])):
        group['id'] = len(records) + 1
        group['incidence_masks'] = key
        group['twice_vertex_prices'] = prices(group['triangles'])
        records.append(group)
        print(group['id'], 'triangles',group['triangles'],'counts',group['labelled_cores'],group['matching_count'],
              'prices',group['twice_vertex_prices'],flush=True)
    out.write_text(json.dumps(records, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('out', type=Path)
    args = parser.parse_args()
    main(args.source, args.out)
