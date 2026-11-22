#!/usr/bin/env python3
"""irreducible.py -- can a NO node EXT(n, P, t) be reduced, and to what?

All checks are answered by SAT (netsat CEGAR model, glucose4; run with the venv python, which has
pysat). Every NO answer below is a proof that the node has no t-layer completion.

  0. the node itself: is there a t-layer completion at all?  A node that has one is reported as
     'extends' and not examined further.
  1. residual sentinels: every set S of 1..kmax channels fixed to +-inf at the inputs, with the
     sentinels' paths removed and the rest untangled (Knuth 5.3.4-16). This drops to n - |S|
     channels, but it is a relaxation: the residual forgets that each sentinel must still travel
     through the t remaining layers to its final channel. Sets with t >= D(n - |S|) are skipped.
  2. tracked sentinels: the same inputs, but all n channels kept. This is an exact restriction:
     the sentinel's value is still in the network and must reach channel n-1 (+inf) or 0 (-inf).
     A tracked set without a sorter whose residual has one means the obstruction is the
     sentinel's travel. Single sentinels suffice: more sentinels only shrink the set.
  3. a value fixed after the prefix: the outputs of P with x_c = v, all n channels kept. Again
     exact; it contains the tracked set of every sentinel that ends the prefix on channel c.
  4. (--core) a deletion-minimal core: a subset of P's unsorted outputs that t layers still cannot
     sort, from which no single vector can be removed.

Verdicts for a node without a completion: 'reducible' (some residual has none: fewer channels),
'reducible when tracked' (no residual, but a tracked sentinel or a fixed value leaves a set
without a sorter), 'IRREDUCIBLE' (none of these restrictions lacks a sorter), 'undecided' (timeouts).

(A first version deleted channel c in check 3 and asked whether a standard network on n - 1
channels sorts the rest. That question has no bearing on the node: P1 passed it although fixing
x_3 = 1 with channel 3 kept leaves a set that 5 layers cannot sort.)

usage: irreducible.py N T 'PREFIX_JSON' [--kmax K] [--core]
"""
import itertools, json, os, random, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'd18-search'))
import sentinel_prover as sp
import sprove
from netsat import Model, apply_layers
from netsat import is_sorted as ns_sorted


def sortable(r, Y, t, seconds=60, init=200, batch=30):
    """'YES' if some standard t-layer network on r channels sorts every vector of Y, 'NO' if none
    does, 'UNKNOWN' on timeout."""
    U = sorted(y for y in Y if not ns_sorted(y, r))
    if not U:
        return 'YES'
    M = Model(r, t, U, solver='glucose4')
    rng = random.Random(0)
    added = set(U if len(U) <= init else rng.sample(U, init))
    for x in added:
        M.add_input(x)
    deadline = time.time() + seconds
    while time.time() < deadline:
        M.S.conf_budget(50000)
        ok = M.S.solve_limited()
        if ok is None:
            continue
        if not ok:
            return 'NO'
        net = M.network(M.S.get_model())
        fails = [x for x in U if x not in added and not ns_sorted(apply_layers(net, x), r)]
        if not fails:
            return 'YES'
        rng.shuffle(fails)
        for x in fails[:batch]:
            M.add_input(x)
            added.add(x)
    return 'UNKNOWN'


def apply_prefix(P, x):
    for L in P:
        x = sp.apply_layer(L, x)
    return x


def tracked_outputs(n, P, S):
    """0/1 outputs of P on the inputs where each channel of S holds +inf ('+') or -inf ('-')."""
    fixed = [(c, 1 if s == '+' else 0) for c, s in S.items()]
    return frozenset(apply_prefix(P, x) for x in range(1 << n)
                     if all(((x >> c) & 1) == v for c, v in fixed))


def sentinel_end(P, c, s):
    """Channel holding the sentinel after P (a +inf moves up a comparator, a -inf moves down)."""
    for L in P:
        for i, j in L:
            if s == '+' and c == i:
                c = j
                break
            if s == '-' and c == j:
                c = i
                break
    return c


def residual_sentinels(n, P, t, kmax):
    seen, no, unknown, extend, trivial = {}, [], [], 0, 0
    for k in range(1, kmax + 1):
        r = n - k
        for ch in itertools.combinations(range(n), k):
            for sg in itertools.product('+-', repeat=k):
                S = dict(zip(ch, sg))
                if t >= sp.DUP[r]:
                    trivial += 1
                    continue
                _, R, h, _, _ = sp.residual2(n, P, S)
                X = sp.outputs(r, R)
                key = (r, sprove.inv_hash(X, r))
                res = next((a for X2, a in seen.get(key, []) if sp.equivalent(X2, X, r)), None)
                if res is None:
                    res = sortable(r, X, t)
                    seen.setdefault(key, []).append((X, res))
                if res == 'YES':
                    extend += 1
                elif res == 'NO':
                    no.append((S, r, h))
                else:
                    unknown.append((S, r, h))
    return no, unknown, extend, trivial


def tracked_sentinels(n, P, t):
    seen, no, unknown, extend = {}, [], [], 0
    for c in range(n):
        for s in '+-':
            X = tracked_outputs(n, P, {c: s})
            if X not in seen:
                seen[X] = sortable(n, X, t)
            res = seen[X]
            e = sentinel_end(P, c, s)
            d = (n - 1 - e) if s == '+' else e
            if res == 'YES':
                extend += 1
            elif res == 'NO':
                no.append((c, s, e, d, len(X)))
            else:
                unknown.append((c, s, e, d, len(X)))
    return no, unknown, extend


def fixed_after(n, X, t):
    no, unknown, extend = [], [], 0
    for c in range(n):
        for v in (0, 1):
            Y = frozenset(x for x in X if ((x >> c) & 1) == v)
            a = sortable(n, Y, t)
            if a == 'YES':
                extend += 1
            elif a == 'NO':
                no.append((c, v, len(Y)))
            else:
                unknown.append((c, v, len(Y)))
    return no, unknown, extend


def core(n, X, t):
    keep = [x for x in sorted(X) if not ns_sorted(x, n)]
    assert sortable(n, keep, t, init=10 ** 6) == 'NO'
    i = 0
    while i < len(keep):
        trial = keep[:i] + keep[i + 1:]
        if sortable(n, trial, t, init=10 ** 6) == 'NO':
            keep = trial
        else:
            i += 1
    return keep


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    n, t = int(args[0]), int(args[1])
    P = tuple(tuple(tuple(c) for c in L) for L in json.loads(args[2]))
    kmax = int(sys.argv[sys.argv.index('--kmax') + 1]) if '--kmax' in sys.argv else n - 3
    X = sp.outputs(n, P)
    unsorted = sum(1 for x in X if not ns_sorted(x, n))
    t0 = time.time()
    print(f'node: n={n} t={t} prefix={json.dumps(P)}; {len(X)} outputs, {unsorted} unsorted')
    node = sortable(n, X, t)
    print(f'  node itself: {node} (NO = no {t}-layer completion)')
    if node == 'YES':
        print('  verdict: extends')
        return
    no1, unk1, ext1, triv = residual_sentinels(n, P, t, kmax)
    print(f'  residual sentinels (1..{kmax}): {len(no1)} residuals without completion, {ext1} with, '
          f'{len(unk1)} unknown, {triv} skipped (t >= D(r)) ({time.time() - t0:.0f}s)')
    for S, r, h in no1[:12]:
        print(f'    reduces: S={S} -> {r} channels, height {h}')
    no2, unk2, ext2 = tracked_sentinels(n, P, t)
    print(f'  tracked sentinels (1, all {n} channels kept): {len(no2)} without a sorter, {ext2} with, '
          f'{len(unk2)} unknown ({time.time() - t0:.0f}s)')
    for c, s, e, d, m in no2:
        print(f'    no sorter: {c}{s} ends the prefix on channel {e}, {d} channels from its target '
              f'({m} vectors)')
    no3, unk3, ext3 = fixed_after(n, X, t)
    print(f'  one value fixed after the prefix (channel kept): {len(no3)} without a sorter, {ext3} with, '
          f'{len(unk3)} unknown ({time.time() - t0:.0f}s)')
    for c, v, m in no3:
        print(f'    no sorter: x_{c} = {v} ({m} vectors)')
    if no1:
        verdict = 'reducible'
    elif no2 or no3:
        verdict = 'reducible when tracked'
    elif node == 'NO' and not (unk1 or unk2 or unk3):
        verdict = 'IRREDUCIBLE'
    else:
        verdict = 'undecided'
    print(f'  verdict: {verdict}')
    if '--core' in sys.argv:
        C = core(n, X, t)
        print(f'  deletion-minimal unsortable core: {len(C)} of {unsorted} unsorted outputs ({time.time() - t0:.0f}s)')
        print('    ' + ' '.join(''.join('1' if (x >> k) & 1 else '0' for k in range(n)) for x in C))


if __name__ == '__main__':
    main()
