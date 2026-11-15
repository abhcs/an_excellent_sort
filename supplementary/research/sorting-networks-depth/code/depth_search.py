"""Exhaustive depth search over maximal-layer networks (WLOG by the add-comparators lemma).

State = image set of the prefix, as a bitmask over 2^n vectors.
Pruning = subsumption: keep only subset-minimal image sets at each depth.
Returns: max depth at which no sorting network exists, and a witness network.
"""
import sys, itertools
from functools import lru_cache

def perfect_matchings(items):
    if not items:
        yield ()
        return
    a = items[0]
    for k in range(1, len(items)):
        b = items[k]
        rest = tuple(x for x in items[1:] if x != b)
        for m in perfect_matchings(rest):
            yield ((a, b),) + m

def maximal_layers(n):
    if n % 2 == 0:
        return list(perfect_matchings(tuple(range(n))))
    out = []
    for z in range(n):
        rest = tuple(x for x in range(n) if x != z)
        for m in perfect_matchings(rest):
            out.append(m)
    return out

def apply_layer(v, m):
    # v bits: bit i = value on channel i ; min to lower channel
    for (a, b) in m:
        va, vb = (v >> a) & 1, (v >> b) & 1
        if va > vb:                      # (1,0) -> swap
            v = (v & ~(1 << a)) | (1 << b)
    return v

def sorted_mask(n):
    mk = 0
    for k in range(n + 1):
        v = ((1 << k) - 1) << (n - k)    # 0^{n-k} 1^k
        mk |= 1 << v
    return mk

def reverse_bits(v, n):
    r = 0
    for i in range(n):
        if (v >> i) & 1: r |= 1 << (n - 1 - i)
    return r

def canon(mask, n):
    best = mask
    # reversal of image set
    for neg in (False, True):
        m2 = 0
        mm = mask
        while mm:
            low = mm & -mm; v = low.bit_length() - 1; mm ^= low
            w = reverse_bits(v, n)
            if neg: w = (1 << n) - 1 - w
            m2 |= 1 << w
        best = min(best, m2)
    return best

def search(n, maxdepth, want_witness=True):
    layers = maximal_layers(n)
    # precompute images of each layer
    acts = []
    for m in layers:
        acts.append([apply_layer(v, m) for v in range(1 << n)])
    full = (1 << (1 << n)) - 1
    target = sorted_mask(n)
    # BFS with subsumption pruning
    frontier = {canon(full, n): ()}
    found = None
    for d in range(maxdepth + 1):
        # check target in frontier
        for st, path in frontier.items():
            if st & ~target == 0:
                found = (d, path); break
        if found: break
        if d == maxdepth: break
        new = {}
        for st, path in frontier.items():
            # enumerate members
            members = []
            mm = st
            while mm:
                low = mm & -mm; members.append(low.bit_length() - 1); mm ^= low
            for li, act in enumerate(acts):
                ns = 0
                for v in members:
                    ns |= 1 << act[v]
                if ns & ~target == 0:
                    new[ns] = path + (li,); break
                if ns in new: continue
                # smaller image set dominates (any continuation sorting a
                # superset also sorts the subset), so keep subset-minimal sets
                if any((ns | s) == ns for s in new):
                    continue
                for s in [s for s in new if (s | ns) == s]:
                    del new[s]
                new[ns] = path + (li,)
            if any((s & ~target) == 0 for s in new):
                break
        frontier = new
        sys.stderr.write(f"n={n} depth {d+1}: {len(frontier)} states\n"); sys.stderr.flush()
        if not frontier: break
    return found, layers

if __name__ == "__main__":
    n = int(sys.argv[1]); D = int(sys.argv[2])
    found, layers = search(n, D)
    if found:
        d, path = found
        print(f"n={n}: sorting network at depth {d}")
        for li in path:
            print("  ", layers[li])
    else:
        print(f"n={n}: NO sorting network of depth <= {D}")
