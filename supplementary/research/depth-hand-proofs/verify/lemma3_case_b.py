"""Lemma 3, case (b), exhaustively.  Five channels; layer 1 = {c1}, layer 2 = {c2}, c1 and c2 share
exactly one channel q (c1 = {p,q}, c2 = {q,s}; y, z are idle in layers 1-2); layer 3 = any matching.
Checks:
 1. two infinities can keep three reals apart through layer 3 unless L3 = {{y,z},{p,s'}}, where s' is
    the channel of c2 not holding the infinity A that sits on q after layer 1 (+inf if q > p, -inf
    otherwise) -- and in exactly those cases they cannot;
 2. in those cases c1, c2, {p,s'} sort the triple {p,q,s};
 3. the median of a sorted triple merged with a sorted pair depends on all five positions."""
import itertools
from netlib import matchings, run, blinds, placements

n = 5
pairs = list(itertools.combinations(range(n), 2))
cases = failures = 0
for c1, c2 in itertools.product(pairs, pairs):
    common = set(c1) & set(c2)
    if len(common) != 1:
        continue
    q = common.pop()
    p, s = (set(c1) - {q}).pop(), (set(c2) - {q}).pop()
    y, z = sorted(set(range(n)) - {p, q, s})
    q_after = max(q, s) if q > p else min(q, s)      # where A sits after layer 2
    s_prime = s if q_after == q else q
    predicted = tuple(sorted([(y, z), tuple(sorted((p, s_prime)))]))
    for L3 in matchings(n):
        cases += 1
        fails = not any(blinds([[c1], [c2], list(L3)], cfg) for cfg in placements(n, 2))
        assert fails == (tuple(sorted(L3)) == predicted), (c1, c2, L3)
        if fails:
            failures += 1
            tri = sorted((p, q, s))
            c3 = tuple(sorted((p, s_prime)))
            for perm in itertools.permutations(range(3)):
                x = [0] * n
                for ch, v in zip(tri, perm):
                    x[ch] = v
                out = run([[c1], [c2], [c3]], x)
                assert [out[ch] for ch in tri] == [0, 1, 2]
print(f'Lemma 3(b): {cases} (c1, c2, L3) cases, blinding fails in {failures}, all of the predicted form, '
      f'and in each of them layers 1-3 sort the triple')

depends = set()
for vals in itertools.permutations(range(10), 5):
    tri, pr = sorted(vals[:3]), sorted(vals[3:])
    state = tri + pr
    for k in range(5):
        for v in range(-1, 11):
            w = list(state)
            w[k] = v + 0.5
            if w[:3] == sorted(w[:3]) and w[3:] == sorted(w[3:]) and sorted(w)[2] != sorted(state)[2]:
                depends.add(k)
print(f'median of (sorted triple) + (sorted pair) depends on positions {sorted(depends)}')
assert depends == set(range(5))
