#!/usr/bin/env python3
"""layer4.py -- find next layers that shrink the output set of a prefix (simulated annealing).

Given a prefix P with output set S, look for a layer L (standard comparators, each one swapping on
some x in S) that makes |L(S)| small, optionally self-dual.  Collects many distinct good layers
and writes the extended prefixes (P + L) to a JSON-lines file for conquer.py.
"""
import argparse
import json
import math
import random
import sys

sys.path.insert(0, __import__('os').path.dirname(__file__))
from netsat import apply_layers, is_self_dual, is_sorted, load_prefix, mirror, prefix_images, window  # noqa: E402


def out_size(S, L):
    return len({apply_layers([L], x) for x in S})


def symmetrize(n, pairs):
    full = set(pairs) | {mirror(n, p) for p in pairs}
    used = {}
    for (i, j) in full:
        for k in (i, j):
            if k in used:
                return None
            used[k] = (i, j)
    return sorted(full)


def anneal(n, S, allowed, rng, iters=3000, sym=False, T0=None, start=None):
    L = list(start or [])
    cost = out_size(S, L)
    best, bestL = cost, L[:]
    T0 = T0 if T0 is not None else max(1.0, 0.02 * cost)
    allowed_list = sorted(allowed)
    for it in range(iters):
        T = T0 * (1 - it / iters) + 1e-6
        used = {k for p in L for k in p}
        Lset = set(L)
        mv = rng.random()
        new = None
        if mv < 0.35:                                   # add a comparator on free channels
            cand = [p for p in rng.sample(allowed_list, min(40, len(allowed_list)))
                    if p[0] not in used and p[1] not in used]
            if cand:
                new = Lset | {cand[0]}
        elif mv < 0.5 and L:                            # remove one
            p = rng.choice(L)
            new = Lset - {p}
        elif L:                                         # move one endpoint / rewire two
            p = rng.choice(L)
            if rng.random() < 0.5 or len(L) < 2:
                a = rng.choice(p)
                free = [c for c in range(n) if c not in used]
                if free:
                    c = rng.choice(free)
                    q = tuple(sorted((a, c)))
                    if q in allowed:
                        new = (Lset - {p}) | {q}
            else:
                q = rng.choice([x for x in L if x != p])
                a, b = p
                c, d = q
                opts = [(tuple(sorted((a, c))), tuple(sorted((b, d)))), (tuple(sorted((a, d))), tuple(sorted((b, c))))]
                o1, o2 = rng.choice(opts)
                if o1 in allowed and o2 in allowed:
                    new = (Lset - {p, q}) | {o1, o2}
        if new is None:
            continue
        new = sorted(new)
        if sym:
            new = symmetrize(n, new)
            if new is None or any(p not in allowed for p in new):
                continue
        c = out_size(S, new)
        if c <= cost or rng.random() < math.exp((cost - c) / T):
            L, cost = new, c
            if c < best:
                best, bestL = c, new[:]
    return best, bestL


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--prefix', required=True)
    ap.add_argument('--restarts', type=int, default=20)
    ap.add_argument('--iters', type=int, default=3000)
    ap.add_argument('--sym', action='store_true')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--keep', type=float, default=1.10, help='keep layers within this factor of the best')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    n, P = load_prefix(args.prefix)
    if args.sym:
        assert is_self_dual(n, P)
    S = sorted(prefix_images(n, P))
    U = [x for x in S if not is_sorted(x, n)]
    allowed = {(i, j) for i in range(n) for j in range(i + 1, n)
               if any((x >> i) & 1 and not (x >> j) & 1 for x in U)}
    rng = random.Random(args.seed)
    found = {}
    for rs in range(args.restarts):
        best, L = anneal(n, S, allowed, rng, iters=args.iters, sym=args.sym)
        key = json.dumps(L)
        found[key] = best
        print(f'restart {rs}: |outputs| = {best}  layer = {L}', flush=True)
    bestall = min(found.values())
    with open(args.out, 'w') as f:
        for key, c in sorted(found.items(), key=lambda kv: kv[1]):
            if c <= bestall * args.keep:
                L = json.loads(key)
                f.write(json.dumps({'n': n, 'outputs': c, 'layers': [list(map(list, l)) for l in P] + [L]}) + '\n')
    print('best', bestall, 'kept', sum(1 for c in found.values() if c <= bestall * args.keep), 'of', len(found))


if __name__ == '__main__':
    main()
