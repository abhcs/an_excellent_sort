#!/usr/bin/env python3
"""symlabel.py -- run the self-dual (--sym) search over many self-dual labelings of one prefix.

For unrestricted networks the labeling of a prefix does not matter (untangling), but the set of
self-dual networks extending it does depend on the labeling.  A self-dual prefix P comes with the
anti-automorphism delta(k) = n-1-k.  A self-dual labeling is a bijection lam onto 0..n-1 with
lam(u) < lam(v) for every comparator (u, v) of P and lam(delta(u)) = n-1-lam(u); it is built from
both ends at once, choosing a random minimal element for position p and its mirror for n-1-p.
Only constraints valid for self-dual networks are used (phi, nored0; no co-saturation).
"""
import argparse
import json
import random
import sys
import time

sys.path.insert(0, __import__('os').path.dirname(__file__))
from netsat import is_self_dual, load_prefix, search, verify_all  # noqa: E402


def random_selfdual_labeling(n, prefix, rng):
    preds = {u: set() for u in range(n)}
    for L in prefix:
        for (u, v) in L:
            preds[v].add(u)
    # transitive closure is not needed: we only place an element after all its direct preds
    lam = {}
    left = set(range(n))
    for p in range(n // 2):
        cands = [u for u in left if not (preds[u] & left) and (n - 1 - u) != u]
        rng.shuffle(cands)
        for u in cands:
            m = n - 1 - u
            if m not in left:
                continue
            # m goes to position n-1-p: everything must precede it, i.e. nothing in left is
            # a successor of m (guaranteed by duality when u is minimal), check anyway
            if any(m in preds[w] for w in left if w != m):
                continue
            lam[u], lam[m] = p, n - 1 - p
            left -= {u, m}
            break
        else:
            return None
    return lam


def relabel(prefix, lam):
    return [sorted((lam[u], lam[v]) for (u, v) in L) for L in prefix]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--prefix', required=True)
    ap.add_argument('--depth', type=int, required=True)
    ap.add_argument('--count', type=int, default=50)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--out', default='results/symlabel_found.json')
    args = ap.parse_args()
    n, P = load_prefix(args.prefix)
    assert is_self_dual(n, P)
    rng = random.Random(args.seed)
    seen = set()
    stats = {'unsat': 0, 'found': 0}
    for c in range(args.count):
        lam = random_selfdual_labeling(n, P, rng)
        if lam is None:
            continue
        Q = relabel(P, lam)
        key = json.dumps(Q)
        if key in seen:
            continue
        seen.add(key)
        assert is_self_dual(n, Q) and all(i < j for L in Q for (i, j) in L)
        t0 = time.time()
        res = search(n, Q, args.depth - len(Q), sym=True, init=10 ** 6, log=lambda s: None)
        dt = time.time() - t0
        if isinstance(res, list):
            stats['found'] += 1
            print(time.strftime('%H:%M:%S'), f'labeling {c}: FOUND in {dt:.1f}s', json.dumps(res), flush=True)
            assert verify_all(n, res)
            with open(args.out, 'a') as f:
                f.write(json.dumps({'n': n, 'prefix': Q, 'layers': res}) + '\n')
        else:
            stats['unsat' if res is None else str(res)] = stats.get('unsat' if res is None else str(res), 0) + 1
            print(time.strftime('%H:%M:%S'), f'labeling {c}: {"UNSAT" if res is None else res} in {dt:.1f}s  prefix={json.dumps(Q)}', flush=True)
    print('DONE', stats, flush=True)


if __name__ == '__main__':
    main()
