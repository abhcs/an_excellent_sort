"""Subsumption among the hard S14 root children of a case: for which pairs does one child's output
set (or its complement, reversed) embed into another's after relabeling?  Then a child whose set
embeds into another's settles it: no completion for the smaller one means none for the larger
(Bundala-Zavodny).  Reports the minimal children (embedding into no other sampled child... i.e. the
ones that would still need their own proof) for a sample.  usage: CASE SAMPLE [SEED] [BUDGET]"""
import os, random, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, '..')]
import ss_cases
import sentinel_prover as sp
from sprove import profiles, embeds_py

case, SAMPLE = int(sys.argv[1]), int(sys.argv[2])
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
BUDGET = int(sys.argv[4]) if len(sys.argv) > 4 else 20000
n = 14
L1, cs = ss_cases.cases(n, 5)
L2, X = cs[case]
nonred = sp._fc.nonredundant(n, X)
auts = [g for g in sp._fc.automorphisms(X, n, maxg=500)[0] if g != (tuple(range(n)), False)]
allL = sp._fc.canonical_layers(n, nonred, 5, auts)
hard = [int(l) for l in open(os.path.join(HERE, '..', 'logs', f's14_case{case}_hard.txt'))]
random.Random(seed).shuffle(hard)
hard = hard[:SAMPLE]
mask = (1 << n) - 1


def rc(x):                                  # reverse and complement: the dual network's view
    y = 0
    for k in range(n):
        if not (x >> (n - 1 - k)) & 1:
            y |= 1 << k
    return y


Y = {k: frozenset(sp._fc.apply_layer(n, X, allL[k])) for k in hard}
P = {k: profiles(Y[k], n) for k in hard}
Yd = {k: frozenset(rc(x) for x in Y[k]) for k in hard}
Pd = {k: profiles(Yd[k], n) for k in hard}
order = sorted(hard, key=lambda k: len(Y[k]))
covered_by = {}
t0 = time.time()
tests = 0
for ib, b in enumerate(order):
    for a in order[:ib]:                    # smaller first; ties by order, so no cycles
        for A, pa in ((Y[a], P[a]), (Yd[a], Pd[a])):
            tests += 1
            if embeds_py(A, Y[b], n, pa, P[b], budget=BUDGET) is not None:
                covered_by[b] = a
                break
        if b in covered_by:
            break
print(f'case {case}: {len(hard)} hard children, sizes {len(Y[order[0]])}..{len(Y[order[-1]])}; '
      f'{len(covered_by)} settled by a smaller sampled child; {len(hard) - len(covered_by)} minimal '
      f'({tests} embedding tests, {time.time() - t0:.0f}s)', flush=True)
mins = [k for k in order if k not in covered_by]
print('minimal:', [(k, len(Y[k])) for k in mins[:40]])
