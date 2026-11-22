#!/usr/bin/env python3
"""subsume.py: subsumption order on the two-layer prefixes L1;L2 of a sparse-start statement.

P subsumes Q when the output set of P embeds in the output set of Q, or of Q's dual, under a
relabeling of channels: sigma(out(P)) <= out(Q).  Then a sorting suffix for Q, relabeled and
untangled, is a sorting suffix for P with the same number of comparators in every layer
(Bundala-Zavodny 2014, Lemma 2).  So "P has no suffix" implies "Q has no suffix", and only the
prefixes that no other prefix subsumes need a SAT run.

usage: subsume.py CLASSES.json [OUT.json] [--times CASES.jsonl]
"""
import json, sys, time
import numpy as np


def apply(layer, x):
    for i, j in layer:
        if (x >> i) & 1 and not (x >> j) & 1:
            x ^= (1 << i) | (1 << j)
    return x


def outputs(n, layers):
    out = set()
    for x in range(1 << n):
        for L in layers:
            x = apply(L, x)
        out.add(x)
    return np.array(sorted(out), dtype=np.int64)


def popcount(a):
    a = a.copy()
    c = np.zeros_like(a)
    while a.any():
        c += a & 1
        a >>= 1
    return c


class OutSet:
    def __init__(self, n, X):
        self.n, self.X = n, X
        self.w = popcount(X)
        self.wcount = np.bincount(self.w, minlength=n + 1)
        bits = np.stack([(X >> i) & 1 for i in range(n)])          # n x |X|
        self.bits = bits
        # ones[i][w] = #vectors of weight w with a 1 on channel i
        self.ones = np.stack([np.bincount(self.w[bits[i] == 1], minlength=n + 1) for i in range(n)])
        self.zeros = np.stack([np.bincount(self.w[bits[i] == 0], minlength=n + 1) for i in range(n)])


def embeds(P, Q, budget=200000):
    """Find sigma with sigma(P.X) <= Q.X (sigma maps P-channel i to Q-channel sigma[i])."""
    n = P.n
    if len(P.X) > len(Q.X) or (P.wcount > Q.wcount).any():
        return None
    cand = [[j for j in range(n) if (P.ones[i] <= Q.ones[j]).all() and (P.zeros[i] <= Q.zeros[j]).all()]
            for i in range(n)]
    if any(not c for c in cand):
        return None
    order = sorted(range(n), key=lambda i: len(cand[i]))
    sigma = [-1] * n
    used = [False] * n
    nodes = [0]

    def ok(kP, kQ):
        uP, cP = np.unique(kP, return_counts=True)
        uQ, cQ = np.unique(kQ, return_counts=True)
        pos = np.searchsorted(uQ, uP)
        if (pos >= len(uQ)).any():
            return False
        if (uQ[pos] != uP).any():
            return False
        return bool((cQ[pos] >= cP).all())

    def rec(t, kP, kQ):
        if t == n:
            return True
        nodes[0] += 1
        if nodes[0] > budget:
            raise TimeoutError
        i = order[t]
        for j in cand[i]:
            if used[j]:
                continue
            nP = kP * 2 + P.bits[i]
            nQ = kQ * 2 + Q.bits[j]
            if not ok(nP, nQ):
                continue
            used[j] = True
            sigma[i] = j
            if rec(t + 1, nP, nQ):
                return True
            used[j] = False
            sigma[i] = -1
        return False

    if rec(0, P.w.copy(), Q.w.copy()):
        return list(sigma)
    return None


def check_embedding(P, Q, sigma):
    img = np.zeros_like(P.X)
    for i in range(P.n):
        img |= ((P.X >> i) & 1) << sigma[i]
    return bool(np.isin(img, Q.X).all())


def main():
    src = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
    times = {}
    if '--times' in sys.argv:
        for line in open(sys.argv[sys.argv.index('--times') + 1]):
            r = json.loads(line)
            times[json.dumps(r['l2'])] = r['seconds']
    d = json.load(open(src))
    n, L1, reps = d['n'], [tuple(p) for p in d['L1']], d['reps']
    mask = (1 << n) - 1
    sets, duals = [], []
    for L2 in reps:
        X = outputs(n, [L1, [tuple(p) for p in L2]])
        sets.append(OutSet(n, X))
        duals.append(OutSet(n, np.array(sorted(int(x) ^ mask for x in X), dtype=np.int64)))
    order = sorted(range(len(reps)), key=lambda k: (len(sets[k].X), -len(reps[k]), k))
    R, cover = [], {}
    t0 = time.time()
    timeouts = 0
    for q in order:
        found = None
        for p in R:
            for tag, target in (('id', sets[q]), ('dual', duals[q])):
                try:
                    s = embeds(sets[p], target)
                except TimeoutError:
                    timeouts += 1
                    s = None
                if s is not None:
                    assert check_embedding(sets[p], target, s)
                    found = (p, tag, s)
                    break
            if found:
                break
        if found:
            cover[q] = found
        else:
            R.append(q)
    el = time.time() - t0
    print(f'{len(reps)} classes -> {len(R)} unsubsumed ({el:.1f}s, {timeouts} search timeouts)')
    from collections import Counter
    print('unsubsumed by |L2|:', dict(sorted(Counter(len(reps[k]) for k in R).items())))
    print('unsubsumed |out| range:', min(len(sets[k].X) for k in R), max(len(sets[k].X) for k in R))
    if times:
        tR = [times.get(json.dumps(reps[k])) for k in R]
        tall = [times.get(json.dumps(r)) for r in reps]
        print(f'SAT seconds: all {sum(t for t in tall if t):.0f}, unsubsumed {sum(t for t in tR if t):.0f}')
    if out_path:
        json.dump({'n': n, 'L1': d['L1'], 'unsubsumed': [{'class': k, 'l2': reps[k], 'out': len(sets[k].X)} for k in R],
                   'cover': {str(q): {'by': p, 'how': tag, 'sigma': s} for q, (p, tag, s) in cover.items()}},
                  open(out_path, 'w'))


if __name__ == '__main__':
    main()
