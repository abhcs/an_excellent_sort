#!/usr/bin/env python3
"""test_fastcore.py -- the C core must agree with the Python routines it replaces (README §8.11).
Run with the venv python; exits non-zero on any disagreement."""
import itertools, os, random, sys, time
os.environ.pop('SP_PURE', None)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fastcore as fc
import sentinel_prover as sp

assert fc.available, 'fastcore did not load'
rng = random.Random(7)
fails = 0


def check(cond, what):
    global fails
    if not cond:
        fails += 1
        print('FAIL', what)


def py_outputs(n, layers):                     # the original Python routine
    out = set(range(1 << n))
    for L in layers:
        out = {sp.apply_layer(L, x) for x in out}
    return frozenset(out)


def py_chan_sigs(X, n):
    sig = [[0] * (n + 1) for _ in range(n)]
    for x in X:
        w = bin(x).count('1')
        for i in range(n):
            if (x >> i) & 1:
                sig[i][w] += 1
    return [tuple(c) for c in sig]


def rand_layer(n, k):
    ch = list(range(n))
    rng.shuffle(ch)
    return tuple(sorted(tuple(sorted(ch[2 * i:2 * i + 2])) for i in range(k)))


def rand_prefix(n, d):
    return tuple(rand_layer(n, rng.randint(1, n // 2)) for _ in range(d))


def relabel(X, perm, comp, n):
    mask = (1 << n) - 1
    out = set()
    for x in X:
        if comp:
            x ^= mask
        y = 0
        for i in range(n):
            if (x >> i) & 1:
                y |= 1 << perm[i]
        out.add(y)
    return frozenset(out)


def py_gen(n, X, cap):                          # the prover's enumeration of next layers
    nonred = [(i, j) for i in range(n) for j in range(i + 1, n)
              if any((x >> i) & 1 and not (x >> j) & 1 for x in X)]
    allL = []

    def gen(start, used, cur):
        if cur:
            allL.append(tuple(cur))
        if len(cur) == cap:
            return
        for idx in range(start, len(nonred)):
            i, j = nonred[idx]
            if used >> i & 1 or used >> j & 1:
                continue
            cur.append((i, j))
            gen(idx + 1, used | (1 << i) | (1 << j), cur)
            cur.pop()
    gen(0, 0, [])
    return nonred, allL


def key(L):
    return tuple(sorted(tuple(sorted(c)) for c in L))


def image(L, perm):
    return key((perm[i], perm[j]) for i, j in L)


t0 = time.time()
# 1-4: outputs, layer images, channel signatures, non-redundant pairs
for trial in range(60):
    n = rng.randint(4, 14)
    P = rand_prefix(n, rng.randint(1, 4))
    X = py_outputs(n, P)
    check(fc.outputs(n, P) == X, f'outputs n={n} {P}')
    L = rand_layer(n, rng.randint(1, n // 2))
    check(fc.apply_layer(n, X, L) == frozenset(sp.apply_layer(L, x) for x in X), 'apply_layer')
    check(fc.chan_sigs(X, n) == py_chan_sigs(X, n), 'chan_sigs')
    nonred, _ = py_gen(n, X, 0)
    check(fc.nonredundant(n, X) == nonred, 'nonredundant')
print(f'outputs, layers, signatures, pairs: done ({time.time() - t0:.0f}s)')

# 5: equivalence (positive cases from relabelings, negative from different prefixes)
for trial in range(80):
    n = rng.randint(5, 14)
    X = py_outputs(n, rand_prefix(n, rng.randint(2, 4)))
    perm = list(range(n))
    rng.shuffle(perm)
    comp = rng.random() < 0.5
    Y = relabel(X, perm, comp, n)
    r = fc.equivalent(X, Y, n)
    check(r is not None and relabel(X, r[0], r[1], n) == Y, f'equivalent positive n={n}')
    Z = py_outputs(n, rand_prefix(n, rng.randint(2, 4)))
    if len(Z) == len(X):
        rz = fc.equivalent(X, Z, n)
        if n <= 11:
            check((rz is not None) == sp._py_equivalent(X, Z, n), f'equivalent vs python n={n}')
        if rz is not None:
            check(relabel(X, rz[0], rz[1], n) == Z, 'equivalent witness')
print(f'equivalence: done ({time.time() - t0:.0f}s)')

# 6: automorphisms (each maps X onto X; complete against brute force for small n)
for trial in range(40):
    n = rng.randint(4, 7)
    X = py_outputs(n, rand_prefix(n, rng.randint(1, 3)))
    auts, complete = fc.automorphisms(X, n)
    check(all(relabel(X, p, c, n) == X for p, c in auts), 'automorphism maps X onto X')
    brute = {(p, c) for p in itertools.permutations(range(n)) for c in (False, True) if relabel(X, p, c, n) == X}
    check(complete and set(auts) == brute, f'automorphisms complete n={n}: {len(auts)} vs {len(brute)}')
print(f'automorphisms: done ({time.time() - t0:.0f}s)')

# 7: canonical layers -- without symmetry the prover's own list; with it exactly the canonical ones
cases = []
import ss_cases
for (n, a) in ((11, 4), (14, 5)):
    L1, cs = ss_cases.cases(n, a)
    for i in (0, len(cs) // 3, len(cs) - 1):
        cases.append((n, a, (L1, cs[i][0]), cs[i][1]))
for trial in range(12):
    n = rng.randint(6, 10)
    P = rand_prefix(n, rng.randint(1, 3))
    cases.append((n, n // 2, P, py_outputs(n, P)))
for n, cap, P, X in cases:
    nonred, allL = py_gen(n, X, cap)
    if len(allL) > 300000:
        continue
    check(fc.canonical_layers(n, nonred, cap, []) == allL, f'all layers n={n}')
    auts, _ = fc.automorphisms(X, n)
    can = fc.canonical_layers(n, nonred, cap, auts)
    want = [L for L in allL if all(image(L, p) >= key(L) for p, _ in auts)]
    check(can == want, f'canonical layers n={n}: {len(can)} vs {len(want)}')
    # every layer's child is equivalent to the child of some canonical layer
    sample = rng.sample(allL, min(40, len(allL)))
    cset = {}
    for L in can:
        Y = fc.apply_layer(n, X, L)
        cset.setdefault((len(Y), sp.invariant(Y, n)), []).append(Y)
    for L in sample:
        Y = fc.apply_layer(n, X, L)
        bucket = cset.get((len(Y), sp.invariant(Y, n)), [])
        check(any(fc.equivalent(Y, Z, n) is not None for Z in bucket), f'child of a skipped layer n={n}')
    print(f'  n={n} |X|={len(X)}: {len(allL)} layers, {len(auts)} automorphisms, {len(can)} canonical')
print(f'canonical layers: done ({time.time() - t0:.0f}s)')

# 8: child keys
for n, cap, P, X in cases[:6]:
    nonred, allL = py_gen(n, X, cap)
    sample = rng.sample(allL, min(300, len(allL)))
    keys = fc.child_keys(n, X, sample)
    ch = [fc.apply_layer(n, X, L) for L in sample]
    for a in range(len(sample)):
        check(keys[a][0] == len(ch[a]), 'child size')
        for b in range(a + 1, min(len(sample), a + 25)):
            if ch[a] == ch[b]:
                check(keys[a][1:3] == keys[b][1:3], 'equal children, equal hashes')
            elif keys[a][1:3] == keys[b][1:3]:
                check(False, 'different children, equal hashes')
            if fc.equivalent(ch[a], ch[b], n) is not None:
                check(keys[a][3] == keys[b][3], 'equivalent children, equal invariants')
print(f'child keys: done ({time.time() - t0:.0f}s)')

# 9: quick covers -- the C greedy loop makes the Python loop's choices
import shutil, tempfile, sprove
tmp = tempfile.mkdtemp()
shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'facts', 'statements.jsonl'), tmp)
prover = sprove.Prover(sprove.Store(tmp))
qcases = [(10, ((0, 1), (3, 4), (5, 6)), 5), (11, None, 6), (12, None, 5), (12, None, 6), (13, None, 6)]
for n, first, t in qcases * 2:
    P = [first or rand_layer(n, n // 2)] + [rand_layer(n, rng.randint(2, n // 2)) for _ in range(rng.randint(1, 2))]
    X = py_outputs(n, P)
    nonred, _ = py_gen(n, X, 0)
    allL = fc.canonical_layers(n, nonred, n // 2, [])
    lst = sorted(rng.sample(range(len(allL)), min(3000, len(allL))))
    lst = [allL[i] for i in lst]
    got = prover._qcover(n, P, t, (), lst)
    keep, sp._fc = sp._fc, None
    want = prover._qcover(n, P, t, (), lst)
    sp._fc = keep
    check(got == want, f'qcover n={n} t={t}')
    print(f'  n={n} t={t}: {len(lst)} layers, {len(want[0])} sets chosen, {len(want[1])} open')
print(f'quick covers: done ({time.time() - t0:.0f}s)')

# 10: the descent through the lemma rule's as-is schedule (README §8.15).  At every case root of
# S9 = SS(9, 7, 3, 3), with SS(8, 7, 2, 3) registered, the covers must close every third layer that
# leaves a first-layer sentinel a good track (README §4), and C and Python must agree.
import l2classes
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sat14'))
from exceptional_children import tracks_good
assert any(d == 7 and a == 2 and m == 3 for d, a, m, _ in prover.lemmas.get(8, ())), 'SS(8,7,2,3) not registered'
L1d, reps = l2classes.classes(9, 3)
L1d = tuple(tuple(p) for p in L1d)
X1 = sp.outputs(9, (L1d,))
gaps = closed_exc = total = 0
for L2, _ in reps:
    L2 = tuple(tuple(p) for p in L2)
    Xc = frozenset(sp.apply_layer(L2, x) for x in X1)
    nonred = fc.nonredundant(9, Xc)
    allL = fc.canonical_layers(9, nonred, 3, [])
    got = prover._qcover(9, (L1d, L2), 5, (3,), allL)
    keep, sp._fc = sp._fc, None
    want = prover._qcover(9, (L1d, L2), 5, (3,), allL)
    sp._fc = keep
    check(got == want, f'descent qcover C vs Python, L2={L2}')
    opn = set(got[1])
    for L3 in allL:
        total += 1
        good = tracks_good(9, 3, L1d, L2, L3)
        if good and L3 in opn:
            gaps += 1
        if not good and L3 not in opn:
            closed_exc += 1
check(gaps == 0, f'descent: {gaps} third layers with a good track left open')
print(f'descent: {len(reps)} S9 cases, {total} third layers; good-track layers left open: {gaps}; '
      f'exceptional layers closed anyway: {closed_exc} ({time.time() - t0:.0f}s)')
shutil.rmtree(tmp)
print('ALL PASS' if fails == 0 else f'{fails} FAILURES')
sys.exit(1 if fails else 0)
