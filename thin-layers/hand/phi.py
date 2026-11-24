"""Phi_p = sum over outputs k of (|T_p(k)| - 1): the total spread of probe tokens after a prefix of
p layers (hand/token_profile.py).  Compares sparse-start prefixes with prefixes of real sorters."""
import json, sys, os
sys.path[:0] = [os.path.dirname(os.path.abspath(__file__)), os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')]
from token_profile import states_after
import sentinel_prover as sp


def phi(n, prefix):
    X = states_after(n, prefix)
    tot, sizes = 0, []
    for k in range(n):
        w = n - 1 - k
        T = {j for s in X if bin(s).count('1') == w for j in range(n)
             if not (s >> j) & 1 and (s | (1 << j)) in X}
        if T:
            tot += len(T) - 1
            sizes.append(len(T))
    return tot, sizes


def residual_network(n, net, S):
    """Untangled residual of a whole network under sentinels S (input channel -> '+'/'-')."""
    r, R, h, _, _ = sp.residual2(n, tuple(tuple(tuple(c) for c in L) for L in net), S)
    return r, [list(L) for L in R]


if __name__ == '__main__':
    g16 = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'g16_d9_network.json')))
    print('feasible 16-ch (3-layer Green filter):', phi(16, [[tuple(c) for c in L] for L in g16[:3]]))
    # feasible 14-channel sorters: two infinities on the 16-channel sorter, kept in their own layers
    import itertools
    best = []
    for a, b in itertools.combinations(range(16), 2):
        for sa, sb in itertools.product('+-', repeat=2):
            S = {a: sa, b: sb}
            content = ['r'] * 16
            for c, v in S.items():
                content[c] = v
            layers = []
            for L in g16:
                real = []
                for i, j in L:
                    x, y = content[i], content[j]
                    if x == 'r' and y == 'r':
                        real.append((i, j))
                    elif (x == '+' and y != '+') or (y == '-' and x != '-'):
                        content[i], content[j] = y, x
                layers.append(real)
            sizes3 = [len(L) for L in layers[:3]]
            best.append((sizes3, S))
    print('layer sizes of the first three layers over two-infinity restrictions:', sorted({tuple(s) for s, _ in best})[:8])
