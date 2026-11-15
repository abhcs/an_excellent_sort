#!/usr/bin/env python3
"""relabel.py -- permute and untangle a prefix so that its outputs have small windows.

A prefix P extends to a sorting network of depth d iff untangle(rho(P)) does, for any relabeling
rho of the channels (untangle the whole network: the prefix part is untangled on its own, and a
standard network that sorts into some fixed order sorts into the standard order).  The SAT model
in netsat.py only has value variables inside each output's window [first 1, last 0], so the
labeling changes the instance size a lot (Ehlers & Mueller 2015, section 3.1).

cost(P) = sum over unsorted outputs x of the number of in-window pairs (w choose 2) + w, which is
proportional to the number of clauses per free layer.
"""
import argparse
import json
import math
import random
import sys

sys.path.insert(0, __import__('os').path.dirname(__file__))
from netsat import is_sorted, named_prefix, prefix_images, window, verify_all  # noqa: E402


def untangle(layers, lab):
    """lab[w] = label of wire w.  Returns (standard layers, final labeling)."""
    m = list(lab)
    out = []
    for L in layers:
        S = []
        for (u, v) in L:                       # min to wire u
            a, b = m[u], m[v]
            if a < b:
                S.append((a, b))
            else:
                S.append((b, a))
                m[u], m[v] = b, a
        out.append(sorted(S))
    return out, m


def relabel_vec(x, m, n):
    y = 0
    for w in range(n):
        if (x >> w) & 1:
            y |= 1 << m[w]
    return y


def cost_of(outs, m, n):
    c = 0
    for x in outs:
        y = relabel_vec(x, m, n)
        if is_sorted(y, n):
            continue
        a, e = window(y, n)
        w = e - a + 1
        c += w * (w - 1) // 2 + w
    return c


def optimize(n, prefix, iters=20000, seed=0, T0=None, log=print):
    rng = random.Random(seed)
    outs = sorted(prefix_images(n, prefix))
    lab = list(range(n))
    _, m = untangle(prefix, lab)
    cur = best = cost_of(outs, m, n)
    best_lab = lab[:]
    log(f'initial cost {cur}')
    T0 = T0 if T0 is not None else cur * 0.002
    for it in range(iters):
        T = T0 * (1 - it / iters) + 1e-9
        i, j = rng.sample(range(n), 2)
        lab[i], lab[j] = lab[j], lab[i]
        _, m = untangle(prefix, lab)
        c = cost_of(outs, m, n)
        if c <= cur or rng.random() < math.exp((cur - c) / T):
            cur = c
            if c < best:
                best, best_lab = c, lab[:]
        else:
            lab[i], lab[j] = lab[j], lab[i]
    P2, _ = untangle(prefix, best_lab)
    log(f'best cost {best}')
    return P2, best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--prefix', required=True)
    ap.add_argument('--iters', type=int, default=20000)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    n, P = named_prefix(args.prefix)
    P2, c = optimize(n, P, iters=args.iters, seed=args.seed)
    # sanity: same number of distinct outputs
    assert len(prefix_images(n, P2)) == len(prefix_images(n, P))
    with open(args.out, 'w') as f:
        json.dump({'n': n, 'source': args.prefix, 'cost': c, 'layers': P2}, f)
    print(json.dumps(P2))


if __name__ == '__main__':
    main()
