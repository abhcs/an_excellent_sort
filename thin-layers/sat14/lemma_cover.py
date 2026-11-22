"""Which sparse-start lemmas would close the hard S14 root children?  For each sampled hard child,
every sentinel set with up to KMAX sentinels gives a residual on r = 14 - k channels with height h
and as-soon/as-late-as-possible layer sizes.  The prover's lemma rule closes the child with
SS(r, d, a, m) when h + 6 <= d and the first m sizes of either schedule (free layers counting r // 2)
are at most a.  Prints, per candidate lemma, how many sampled children it would close.
usage: CASE SAMPLE KMAX [SEED]"""
import collections, itertools, os, random, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, '..')]
import ss_cases
import sentinel_prover as sp

case, SAMPLE, KMAX = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
t = 6
n = 14
L1, cs = ss_cases.cases(n, 5)
L2, X = cs[case]
nonred = sp._fc.nonredundant(n, X)
auts = [g for g in sp._fc.automorphisms(X, n, maxg=500)[0] if g != (tuple(range(n)), False)]
allL = sp._fc.canonical_layers(n, nonred, 5, auts)
hard = [int(l) for l in open(os.path.join(HERE, '..', 'logs', f's14_case{case}_hard.txt'))]
random.Random(seed).shuffle(hard)
hard = hard[:SAMPLE]
# candidate lemmas SS(r, d, a, m): tight or one above D(r), sparse in the first m layers
D = {8: 6, 9: 7, 10: 7, 11: 8, 12: 8, 13: 9}
LEMMAS = []
for r in range(9, 14):
    for d in (D[r], D[r] + 1):
        for m in (1, 2, 3):
            for a in range(1, r // 2):
                if d - m >= t:             # the lemma can only apply when h <= m <= d - t
                    LEMMAS.append((r, d, a, m))


def applies(r, h, asap, alap, lem):
    r2, d, a, m = lem
    if r2 != r or h + t > d:
        return False
    for prof in (asap, alap):
        sizes = [prof[i] if i < h else r // 2 for i in range(m)]
        if all(x <= a for x in sizes):
            return True
    return False


cover = collections.Counter()
t0 = time.time()
for idx, kc in enumerate(hard):
    layers = (L1, L2, allL[kc])
    hit = set()
    for k in range(1, KMAX + 1):
        r = n - k
        lems = [lm for lm in LEMMAS if lm[0] == r]
        for ch in itertools.combinations(range(n), k):
            for sg in itertools.product('+-', repeat=k):
                _, R, h, asap, alap = sp.residual2(n, layers, dict(zip(ch, sg)))
                for lm in lems:
                    if lm not in hit and applies(r, h, asap, alap, lm):
                        hit.add(lm)
    for lm in hit:
        cover[lm] += 1
    if (idx + 1) % 10 == 0:
        print(f'{idx + 1} children ({time.time() - t0:.0f}s)', flush=True)
print(f'{len(hard)} hard children of case {case}; sentinel sets up to {KMAX}')
# report only lemmas that are not implied by a stronger reported one... keep it simple: all, sorted
for lm, c in sorted(cover.items(), key=lambda kv: (-kv[1], kv[0])):
    print(f'  SS{lm}: closes {c} ({100 * c / len(hard):.0f}%)')
