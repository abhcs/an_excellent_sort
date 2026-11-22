#!/usr/bin/env python3
"""check_sentinel_proof.py PROOF.jsonl DLOW_JSON: independent check of a sentinel-prover proof DAG.

Each node claims NO(n, P, t, caps): the prefix P cannot be extended by t layers (the next ones
capped by caps) into a sorting network.  The checker re-derives every step from definitions:
  quick  simulate P with the sentinel inputs set to +-infinity (real values in {0,1}); the
         comparators that meet two real values form a DAG on the real slots; its height h
         satisfies h + t < D(r), where D(r) >= DLOW[r] must itself be a checked root in the file.
  sent   the residual output set (simulated directly) equals the child's output set up to a
         relabelling of channels and complement, which the checker confirms by an explicit search;
         the child has r channels, the same t and the caps truncated for r.
  split  every non-redundant matching (within the cap) and the empty layer give a child whose
         output set is equivalent to that of a listed NO child, or that is trivially NO (t-1 = 0).
Exit status 0 iff every node checks.
"""
import itertools, json, sys


def popcount(x):
    return bin(x).count('1')


def is_sorted(x, n):
    w = popcount(x)
    return x == ((1 << n) - 1) ^ ((1 << (n - w)) - 1)


def run(layers, vals):
    v = list(vals)
    for L in layers:
        for i, j in L:
            if v[i] > v[j]:
                v[i], v[j] = v[j], v[i]
    return v


def out01(n, layers):
    res = set()
    for x in range(1 << n):
        v = run(layers, [(x >> i) & 1 for i in range(n)])
        res.add(sum(b << i for i, b in enumerate(v)))
    return frozenset(res)


def equivalent(A, B, n):
    """Is B = sigma(A) or B = sigma(complement A) for some channel permutation sigma? (explicit search)"""
    mask = (1 << n) - 1
    if len(A) != len(B):
        return False
    for A2 in (A, frozenset(a ^ mask for a in A)):
        def sig(X, i):
            c = [0] * (n + 1)
            for x in X:
                if (x >> i) & 1:
                    c[popcount(x)] += 1
            return tuple(c)
        sA = [sig(A2, i) for i in range(n)]
        sB = [sig(B, j) for j in range(n)]
        if sorted(sA) != sorted(sB):
            continue
        cand = [[j for j in range(n) if sB[j] == sA[i]] for i in range(n)]
        order = sorted(range(n), key=lambda i: len(cand[i]))
        perm = [None] * n
        used = set()
        def proj(X, chans):
            return {tuple((x >> c) & 1 for c in chans) for x in X}
        def rec(t):
            if t == n:
                img = frozenset(sum(((a >> i) & 1) << perm[i] for i in range(n)) for a in A2)
                return img == B
            i = order[t]
            for j in cand[i]:
                if j in used:
                    continue
                perm[i] = j
                used.add(j)
                done = [order[k] for k in range(t + 1)]
                if proj(A2, done) == proj(B, [perm[c] for c in done]) and rec(t + 1):
                    return True
                used.discard(j)
                perm[i] = None
            return False
        if rec(0):
            return True
    return False


def sentinel_run(n, layers, S, with_Z=True):
    """Simulate with sentinels; return (r, real output set Z in channel order, height h).
    with_Z=False skips the output set (returned as None) when only r, h and the schedules are used."""
    BIG = 10 ** 6
    real = [c for c in range(n) if c not in S]
    r = len(real)
    # real-real comparisons and slot movement do not depend on the real values
    slot = {c: k for k, c in enumerate(real)}           # channel -> slot id (reals only)
    level = {}
    h = 0
    seq = []
    cont = {c: (S[c] if c in S else 'r') for c in range(n)}
    for L in layers:
        for i, j in L:
            a, b = cont[i], cont[j]
            if a == 'r' and b == 'r':
                v = max(level.get(slot[i], 0), level.get(slot[j], 0)) + 1
                level[slot[i]] = level[slot[j]] = v
                h = max(h, v)
                seq.append((slot[i], slot[j], v))
            elif a == '+' and b == 'r':
                cont[i], cont[j] = 'r', '+'
                slot[i] = slot.pop(j)
            elif a == 'r' and b == '-':
                cont[i], cont[j] = '-', 'r'
                slot[j] = slot.pop(i)
            elif a == '+' and b == '-':
                cont[i], cont[j] = '-', '+'
    Z = set()
    for x in range(1 << r) if with_Z else ():
        vals = [0] * n
        for c in range(n):
            vals[c] = (BIG if S[c] == '+' else -BIG) if c in S else None
        for k, c in enumerate(real):
            vals[c] = (x >> k) & 1
        out = run(layers, vals)
        q = [c for c in range(n) if abs(out[c]) < BIG]
        Z.add(sum(out[c] << k for k, c in enumerate(q)))
    asap = [0] * h
    for a, b, v in seq:
        asap[v - 1] += 1
    tail, alap = {}, [0] * h
    for a, b, v in reversed(seq):
        u = max(tail.get(a, 0), tail.get(b, 0)) + 1
        tail[a] = tail[b] = u
        alap[h - u] += 1
    return r, (frozenset(Z) if with_Z else None), h, asap, alap


def norm_caps(n, t, caps):
    caps = tuple(caps[:t])
    while caps and caps[-1] >= n // 2:
        caps = caps[:-1]
    return caps


def main():
    nodes = [json.loads(l) for l in open(sys.argv[1])]
    dlow = {int(k): v for k, v in json.loads(sys.argv[2]).items()}
    by_id = {d['id']: d for d in nodes}
    outs = {d['id']: out01(d['n'], [[tuple(c) for c in L] for L in d['prefix']]) for d in nodes}
    bad = 0
    for d in nodes:
        n, t, caps = d['n'], d['t'], tuple(d['caps'])
        P = [[tuple(c) for c in L] for L in d['prefix']]
        X = outs[d['id']]
        st = d['step']
        ok = True
        if all(is_sorted(x, n) for x in X) or t < 1:
            ok = False
        elif st['rule'] in ('quick', 'sent', 'lemma'):
            S = {int(c): v for c, v in st['S'].items()}
            r, Z, h, asap, alap = sentinel_run(n, P, S)
            if st['rule'] == 'quick':
                ok = r == st['r'] and h == st['h'] and r in dlow and h + t < dlow[r]
            elif st['rule'] == 'lemma':
                d2, a2, m2 = st['ss']
                prof = asap if st['sched'] == 'asap' else alap
                capsr = norm_caps(r, t, caps)
                sizes = [prof[i] if i < h else (capsr[i - h] if i - h < len(capsr) else r // 2) for i in range(m2)]
                L1 = [[2 * k, 2 * k + 1] for k in range(a2)]
                lem = by_id.get(st['lemma_root'])
                ok = (r == st['r'] and h == st['h'] and h + t <= d2 and all(x <= a2 for x in sizes)
                      and lem is not None and lem['n'] == r and lem['t'] == d2 - 1 and lem['prefix'] == [L1]
                      and tuple(lem['caps']) == norm_caps(r, d2 - 1, (a2,) * (m2 - 1)))
            else:
                c = by_id.get(st['child'])
                ok = (c is not None and c['n'] == r and c['t'] == t and
                      tuple(c['caps']) == norm_caps(r, t, caps) and equivalent(Z, outs[c['id']], r))
        else:
            kids = [by_id[c] for c in st['children'] if c is not None]
            cap0 = caps[0] if caps else n // 2
            rest = norm_caps(n, t - 1, caps[1:])
            nonred = [(i, j) for i in range(n) for j in range(i + 1, n)
                      if any((x >> i) & 1 and not (x >> j) & 1 for x in X)]
            pool = [k for k in kids if k['n'] == n and k['t'] == t - 1 and tuple(k['caps']) == rest]
            def child_ok(Y):
                if t - 1 == 0:
                    return not all(is_sorted(y, n) for y in Y)
                return any(len(outs[k['id']]) == len(Y) and equivalent(Y, outs[k['id']], n) for k in pool)
            layers = [()]
            def gen(start, used, cur):
                if cur:
                    layers.append(tuple(cur))
                if len(cur) == cap0:
                    return
                for idx in range(start, len(nonred)):
                    i, j = nonred[idx]
                    if used >> i & 1 or used >> j & 1:
                        continue
                    cur.append((i, j))
                    gen(idx + 1, used | (1 << i) | (1 << j), cur)
                    cur.pop()
            gen(0, 0, [])
            seen = {}
            for L in layers:
                Y = frozenset(sum(b << i for i, b in enumerate(run([L], [(x >> i) & 1 for i in range(n)]))) for x in X)
                if Y in seen:
                    continue
                seen[Y] = child_ok(Y)
                if not seen[Y]:
                    ok = False
                    break
        if not ok:
            bad += 1
            print('FAILED node', d['id'], st['rule'], flush=True)
    # every D(r) >= DLOW[r] used by a quick step must be a node of this file: NO for the maximal
    # normal-form first layer (Fact A) and DLOW[r] - 2 further layers, i.e. no depth DLOW[r] - 1 sorter
    for r, dv in sorted(dlow.items()):
        if dv <= 1:
            continue                                  # D(2) >= 1: the empty network does not sort
        L1 = [[2 * k, 2 * k + 1] for k in range(r // 2)]
        if not any(d['n'] == r and d['t'] == dv - 2 and not d['caps'] and d['prefix'] == [L1] for d in nodes):
            bad += 1
            print('MISSING root for D(%d) >= %d' % (r, dv))
    print(f'{len(nodes)} nodes checked, {bad} failed')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
