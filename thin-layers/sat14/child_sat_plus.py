"""SAT for one S14 root child with sentinel-height clauses (README §8.14).

Sentinel-height lemma: if a network sorts, then for any sentinel set S (channels holding +-inf at
the input) the real comparisons left form a sorting network on r = n - |S| channels, so their longest
chain has at least D(r) comparisons.  After the fixed prefix that chain has length h(S).  If
h(S) + t = dlow(r) (t free layers, dlow a proved lower bound), every free layer must lengthen a
longest chain.  For the first free layer that is a clause: it contains a comparator between two real
channels, one of them at level h(S).  These clauses follow from proved facts, so adding them keeps
the claim; they cut the first free layer to the next layers the prover's quick rule leaves open.

usage: CASE K [--kmax K] [--solver S] [--full] [--init N] [--no-clauses]"""
import argparse, itertools, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, '..'), os.path.join(HERE, '..', '..', 'd18-search')]
import ss_cases
import sentinel_prover as sp
from sprove import sentinel_state
import netsat

DLOW = {1: 0, 2: 1, 3: 3, 4: 3, 5: 5, 6: 5, 7: 6, 8: 6, 9: 7, 10: 7, 11: 8, 12: 8}   # proved (D:3..11; D(12) >= D(11))


def height_clauses(n, prefix, t, kmax, pairs):
    """Clauses (lists of free-layer-0 pairs) from tight sentinel sets with at most kmax sentinels."""
    out, seen = [], set()
    for k in range(0, kmax + 1):
        r = n - k
        if r not in DLOW:
            continue
        for ch in itertools.combinations(range(n), k):
            for sg in itertools.product('+-', repeat=k):
                content, chlvl, asap, h = sentinel_state(n, prefix, dict(zip(ch, sg)))
                if h + t > DLOW[r]:
                    continue
                if h + t < DLOW[r]:
                    return None                     # the quick rule closes the node outright
                cl = tuple(sorted(p for p in pairs if content[p[0]] == 'r' and content[p[1]] == 'r'
                                  and max(chlvl[p[0]], chlvl[p[1]]) == h))
                if cl not in seen:
                    seen.add(cl)
                    out.append(cl)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('case', type=int); ap.add_argument('k', type=int)
    ap.add_argument('--kmax', type=int, default=4); ap.add_argument('--solver', default='cadical195')
    ap.add_argument('--full', action='store_true'); ap.add_argument('--init', type=int, default=300)
    ap.add_argument('--no-clauses', action='store_true')
    ap.add_argument('--d13', type=int, default=8, help='lower bound used for D(13) and D(14): 8 follows from '
                    'D(11) by sentinels; 9 is the descent from S11 (README §5.15)')
    ap.add_argument('--count-only', action='store_true')
    a = ap.parse_args()
    DLOW[13] = DLOW[14] = a.d13
    n, t = 14, 6
    L1, cs = ss_cases.cases(n, 5)
    L2, X = cs[a.case]
    nonred = sp._fc.nonredundant(n, X)
    auts = [g for g in sp._fc.automorphisms(X, n, maxg=500)[0] if g != (tuple(range(n)), False)]
    allL = sp._fc.canonical_layers(n, nonred, 5, auts)
    L3 = allL[a.k]
    prefix = [list(L1), list(L2), list(L3)]
    t0 = time.time()
    U = sorted(x for x in netsat.prefix_images(n, prefix) if not netsat.is_sorted(x, n))
    M = netsat.Model(n, t, U, solver=a.solver)
    ncl = 0
    if not a.no_clauses:
        cls = height_clauses(n, prefix, t, a.kmax, list(M.g[0]))
        if cls is None:
            print(f'RESULT case {a.case} child {a.k} closed by the quick rule', flush=True)
            return
        for cl in cls:
            M.add([M.g[0][p] for p in cl])
        ncl = len(cls)
        if a.count_only:
            print(f'child {a.k}: {ncl} height clauses, lengths {sorted(len(c) for c in cls)[:12]} ({time.time() - t0:.1f}s)')
            return
    t1 = time.time()
    import random
    rng = random.Random(0)
    added = set(U if (a.full or a.init >= len(U)) else rng.sample(U, a.init))
    for x in added:
        M.add_input(x)
    wsize = {x: (lambda ae: ae[1] - ae[0] + 1)(netsat.window(x, n)) for x in U}
    it = 0
    while True:
        it += 1
        if not M.S.solve():
            verdict = 'UNSAT'
            break
        net = M.network(M.S.get_model())
        fails = [x for x in U if x not in added and not netsat.is_sorted(netsat.apply_layers(net, x), n)]
        if not fails:
            verdict = 'SAT'
            break
        fails.sort(key=lambda x: (wsize[x], rng.random()))
        for x in fails[:30]:
            M.add_input(x)
            added.add(x)
    print(f'RESULT case {a.case} child {a.k} {verdict} {time.time() - t0:.1f}s ({ncl} height clauses, '
          f'{t1 - t0:.1f}s to build them; {it} iterations, {len(added)} inputs; kmax {a.kmax}, solver {a.solver})',
          flush=True)


if __name__ == '__main__':
    main()
