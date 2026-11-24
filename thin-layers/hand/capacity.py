"""The most token spread (Phi, hand/phi.py) that ANY next layer can remove after a prefix: for each
pair (i, j), the outputs k for which a comparator (i, j) would be a one-sided merge (tokens of k on
both channels, every one of them seeing the same bit on the other channel); a maximum-weight
matching of these weights bounds the drop of Phi in the next layer.  usage: N 'PREFIX_JSON'"""
import json, sys, os
sys.path[:0] = [os.path.dirname(os.path.abspath(__file__))]
from token_profile import states_after


def weights(n, prefix):
    X = states_after(n, prefix)
    w = {}
    for k in range(n):
        wt = n - 1 - k
        P = [(s, j) for s in X if bin(s).count('1') == wt for j in range(n) if not (s >> j) & 1 and (s | (1 << j)) in X]
        T = {j for _, j in P}
        bits = {}
        for s, j in P:
            for o in T:
                if o != j:
                    bits.setdefault((min(j, o), max(j, o)), set()).add((s >> o) & 1)
        for p, b in bits.items():
            if len(b) == 1 and p[0] in T and p[1] in T:
                w[p] = w.get(p, 0) + 1
    return w


def max_matching(n, w):
    best = {0: 0}
    full = (1 << n) - 1
    import functools

    @functools.lru_cache(None)
    def f(mask):                       # mask: channels still free to use
        if mask == 0:
            return 0
        i = (mask & -mask).bit_length() - 1
        rest = mask & ~(1 << i)
        v = f(rest)                    # i idle
        m = rest
        while m:
            j = (m & -m).bit_length() - 1
            m &= m - 1
            c = w.get((i, j), 0)
            if c:
                v = max(v, c + f(rest & ~(1 << j)))
        return v
    return f(full)


if __name__ == '__main__':
    n = int(sys.argv[1])
    prefix = [[tuple(c) for c in L] for L in json.loads(sys.argv[2])]
    w = weights(n, prefix)
    print(f'pairs with some one-sided merge: {len(w)}; max drop of Phi in the next layer: {max_matching(n, w)}')
