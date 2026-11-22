#!/usr/bin/env python3
"""exceptional.py -- SAT constraints saying that NO sentinel track is good through layers 1..m.

For the first layer L1 = (lo_j, hi_j) (fixed, exactly a comparators) a +inf sentinel starts on hi_j
and a -inf sentinel on lo_j.  A track is good if it meets a comparator in every FULL layer (exactly
a comparators) among layers 2..m.  `add_exceptional(M, n, a, L1, m)` adds to a netsat/thinsat Model
whose prefix is just L1 (free layer t is layer t+2) clauses that hold exactly when every one of the
2a tracks fails at some full layer among 2..m.  Track positions are encoded exactly (one-hot,
full equivalences), so a model describes the true tracks of the network it encodes.
"""
from pysat.card import CardEnc, EncType


def add_exceptional(M, n, a, L1, m):
    T = m - 1                                    # free layers 0..T-1 are layers 2..m
    nv = lambda: M.new_var()
    g = lambda t, i, j: M.g[t].get((min(i, j), max(i, j)), False)

    def lit_and(*xs):                            # aux <-> AND(xs); xs may contain True/False
        xs = [x for x in xs if x is not True]
        if any(x is False for x in xs):
            return False
        if not xs:
            return True
        if len(xs) == 1:
            return xs[0]
        z = nv()
        for x in xs:
            M.add([-z, x])
        M.add([z] + [-x for x in xs])
        return z

    def lit_or(xs):                              # aux <-> OR(xs)
        xs = [x for x in xs if x is not False]
        if any(x is True for x in xs):
            return True
        if not xs:
            return False
        if len(xs) == 1:
            return xs[0]
        z = nv()
        M.add([-z] + xs)
        for x in xs:
            M.add([z, -x])
        return z

    def neg(x):
        return (not x) if isinstance(x, bool) else -x

    # full-layer indicators: f_t -> |layer t| >= a
    full = []
    for t in range(T):
        f = nv()
        lits = sorted(M.g[t].values())
        if len(lits) < a:
            M.add([-f])
        else:
            enc = CardEnc.atleast(lits=lits, bound=a, top_id=M.nv, encoding=EncType.seqcounter)
            M.nv = max(M.nv, enc.nv)
            for cl in enc.clauses:
                M.add([-f] + cl)
        full.append(f)
    minend = [[lit_or([g(t, c, y) for y in range(c + 1, n)]) for c in range(n)] for t in range(T)]
    maxend = [[lit_or([g(t, x, c) for x in range(c)]) for c in range(n)] for t in range(T)]
    used = [[lit_or([minend[t][c], maxend[t][c]]) for c in range(n)] for t in range(T)]
    for lo, hi in L1:
        for sign, start in ((+1, hi), (-1, lo)):
            pos = [c == start for c in range(n)]          # Python booleans: fixed after L1
            fails = []
            for t in range(T):
                idle_here = lit_or([lit_and(pos[c], neg(used[t][c])) for c in range(n)])
                fails.append(lit_and(full[t], idle_here))
                if t == T - 1:
                    break
                new = []
                for c in range(n):
                    if sign > 0:
                        stay = lit_and(pos[c], neg(minend[t][c]))
                        come = [lit_and(pos[x], g(t, x, c)) for x in range(c)]
                    else:
                        stay = lit_and(pos[c], neg(maxend[t][c]))
                        come = [lit_and(pos[y], g(t, c, y)) for y in range(c + 1, n)]
                    new.append(lit_or([stay] + come))
                pos = new
            M.add([x for x in fails if x is not False] or [])   # some layer defeats this track
    return M
