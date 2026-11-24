"""Probe tokens after a prefix (h9.md Lemma 13): for output k, a probe is a pair of reachable states
s, s + e_j after the prefix, s with n-1-k ones; its token (channel j) must end on channel k.
For each output k: T(k) = channels holding some token, and for every pair (i, j) whether a
comparator (i, j) in the next layer would be two-sided for k (some token on i or j sees 0 on the
other channel and some sees 1), which forces both channels into T(k) after that layer.
usage: N 'PREFIX_JSON'   (prints per output: |T|, two-sided pairs among T, max one-sided matching)"""
import itertools, json, sys


def outputs(n, layers):
    X = set(range(1 << n))
    for L in layers:
        Y = set()
        for x in X:
            for i, j in L:
                if (x >> i) & 1 and not (x >> j) & 1:
                    x ^= (1 << i) | (1 << j)
            Y.add(x)
        X = Y
    return X


def probes(n, X, k):
    """(s, j): s and s | 1<<j both reachable, s has n-1-k ones, bit j of s is 0."""
    w = n - 1 - k
    out = []
    for s in X:
        if bin(s).count('1') != w:
            continue
        for j in range(n):
            if not (s >> j) & 1 and (s | (1 << j)) in X:
                out.append((s, j))
    return out


def analyse(n, layers):
    X = outputs(n, layers)
    res = {}
    for k in range(n):
        P = probes(n, X, k)
        T = sorted({j for _, j in P})
        seen = {}                      # (i, j) -> set of partner bits seen when a token is on i or j
        for s, j in P:
            for o in range(n):
                if o == j:
                    continue
                key = (min(j, o), max(j, o))
                seen.setdefault(key, set()).add((s >> o) & 1)
        two = {p for p, b in seen.items() if len(b) == 2}
        res[k] = (len(P), T, two)
    return res


if __name__ == '__main__':
    n = int(sys.argv[1])
    layers = [[tuple(c) for c in L] for L in json.loads(sys.argv[2])]
    for k, (np_, T, two) in analyse(n, layers).items():
        pairs = [(i, j) for i, j in itertools.combinations(T, 2)]
        frac = sum(1 for p in pairs if p in two) / max(1, len(pairs))
        print(f'output {k}: {np_} probes, tokens on {len(T)} channels {T}; two-sided pairs among them {frac:.0%}')
