#!/usr/bin/env python3
"""Construct and exhaustively check the general two-layer restriction lemma.

For a maximal L1 and arbitrary L2, k infinities leave p-k real-real
comparators in L1 and max(0, |L2|-k) in L2, where p=floor(n/2).
No SAT solver is used. See ../extension.md.
"""
import argparse

from netlib import matchings


def placement(n, first, second, k):
    p = n // 2
    assert len(first) == p and 0 <= k <= p
    adj = [[] for _ in range(n)]
    first_used = set()
    second_used = {v for edge in second for v in edge}
    for a, b in first:
        first_used.update([a, b])
    for a, b in [*first, *second]:
        adj[a].append(b)
        adj[b].append(a)
    color = {}
    cover = []
    for root in range(n):
        if root in color:
            continue
        color[root] = 0
        todo, component = [root], []
        while todo:
            a = todo.pop()
            component.append(a)
            for b in adj[a]:
                if b in color:
                    assert color[b] != color[a]
                else:
                    color[b] = 1 - color[a]
                    todo.append(b)
        missing = [v for v in component if v not in first_used]
        choose = 1 - color[missing[0]] if missing else 0
        cover.extend(v for v in component if color[v] == choose)
    assert len(cover) == p
    chosen = set(sorted(cover, key=lambda v: (v not in second_used, v))[:k])
    result = [0] * n
    for a, b in first:
        if a in chosen:
            result[a] = -1
        if b in chosen:
            result[b] = 1
    return result


def verify(max_n=11):
    total = 0
    for n in range(3, max_n + 1):
        p = n // 2
        first = [(2 * i, 2 * i + 1) for i in range(p)]
        count = 0
        for second in matchings(n):
            for k in range(p + 1):
                xs = placement(n, first, second, k)
                assert sum(x != 0 for x in xs) == k
                counts = []
                for layer in [first, second]:
                    counts.append(sum(xs[a] == xs[b] == 0 for a, b in layer))
                    for a, b in layer:
                        xs[a], xs[b] = min(xs[a], xs[b]), max(xs[a], xs[b])
                assert counts == [p - k, max(0, len(second) - k)], (n, second, k)
                count += 1
        total += count
        print(f'n={n}: {count} matching/placement-size cases passed', flush=True)
    print(f'total: {total} cases passed', flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--max-n', type=int, default=11)
    verify(ap.parse_args().max_n)
