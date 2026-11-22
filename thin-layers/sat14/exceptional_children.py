"""Which root children of an SS(n, d, a, 3) case are exceptional (no sentinel track good through
layers 2-3, README §4.1), and how many of them are hard (left open by the lookup sweep)?
usage: N A CASE [HARDFILE]"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
import ss_cases
import sentinel_prover as sp


def tracks_good(n, a, L1, L2, L3):
    """True if some +inf (on hi) or -inf (on lo) track of an L1 comparator meets every full layer."""
    full = [len(L2) == a, len(L3) == a]
    for lo, hi in L1:
        for start, sg in ((hi, '+'), (lo, '-')):
            pos, ok = start, True
            for L, f in zip((L2, L3), full):
                met = False
                for i, j in L:
                    if pos in (i, j):
                        met = True
                        pos = j if sg == '+' else i
                        break
                if f and not met:
                    ok = False
                    break
            if ok:
                return True
    return False


if __name__ == "__main__":
    n, a, case = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    hard = set(int(l) for l in open(sys.argv[4])) if len(sys.argv) > 4 else set()
    L1, cs = ss_cases.cases(n, a)
    L2, X = cs[case]
    nonred = sp._fc.nonredundant(n, X)
    auts = [g for g in sp._fc.automorphisms(X, n, maxg=500)[0] if g != (tuple(range(n)), False)]
    allL = sp._fc.canonical_layers(n, nonred, a, auts)
    exc = [k for k, L3 in enumerate(allL) if not tracks_good(n, a, L1, L2, L3)]
    print(f'SS({n},9,{a},3) case {case}: |L2|={len(L2)}, {len(allL)} canonical children, {len(exc)} exceptional; '
          f'{len(set(exc) & hard)} of them hard (of {len(hard)} hard children)')
