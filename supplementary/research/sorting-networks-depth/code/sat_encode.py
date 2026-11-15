"""SAT encodings for depth lower bounds.

b1        : does a 6-layer maximal-layer network on 11 channels sort image(M0)?
full n d  : does a d-layer maximal-layer network on n channels sort all 0-1 inputs?
"""
import sys

T, F = 'T', 'F'

def neg(x):
    if x == T: return F
    if x == F: return T
    return -x

class CNF:
    def __init__(self): self.nv = 0; self.cl = []
    def new(self): self.nv += 1; return self.nv
    def add(self, *lits):
        out = []
        for L in lits:
            if L == T: return
            if L == F: continue
            out.append(L)
        self.cl.append(out)

def pairs_of(n): return [(i, j) for i in range(n) for j in range(i + 1, n)]

def encode(n, d, states, path):
    cnf = CNF(); P = pairs_of(n)
    g    = {(l, p): cnf.new() for l in range(d) for p in P}
    idle = {(l, i): cnf.new() for l in range(d) for i in range(n)}
    for l in range(d):
        for a in range(len(P)):
            i, j = P[a]
            for b in range(a + 1, len(P)):
                u, v = P[b]
                if i in (u, v) or j in (u, v):
                    cnf.add(-g[(l, P[a])], -g[(l, P[b])])       # matching
                # channel bookkeeping
        for i in range(n):
            cnf.add(idle[(l, i)], *[g[(l, p)] for p in P if i in p])   # idle or matched
            for p in P:
                if i in p: cnf.add(-g[(l, p)], -idle[(l, i)])
            for j in range(i + 1, n):
                cnf.add(-idle[(l, i)], -idle[(l, j)])                  # at most one idle
    val = {(l, i, s): cnf.new() for l in range(1, d + 1) for i in range(n) for s in range(len(states))}
    def lit(l, i, s):
        if l == 0: return T if (states[s] >> i) & 1 else F
        return val[(l, i, s)]
    for l in range(1, d + 1):
        for (i, j) in P:
            G = g[(l - 1, (i, j))]
            I, J = idle[(l - 1, i)], idle[(l - 1, j)]
            for s in range(len(states)):
                a, b = lit(l - 1, i, s), lit(l - 1, j, s)
                c, e = val[(l, i, s)], val[(l, j, s)]
                cnf.add(neg(G), neg(a), neg(b), c)      # G & a & b -> c  (c = a AND b)
                cnf.add(neg(G), a, neg(c))              # G & ~a -> ~c
                cnf.add(neg(G), b, neg(c))              # G & ~b -> ~c
                cnf.add(neg(G), neg(a), e)              # G & a -> e      (e = a OR b)
                cnf.add(neg(G), neg(b), e)              # G & b -> e
                cnf.add(neg(G), a, b, neg(e))           # G & ~a & ~b -> ~e
                cnf.add(neg(I), neg(a), c)              # channel i idle: c = a
                cnf.add(neg(I), a, neg(c))
                cnf.add(neg(J), neg(b), e)              # channel j idle: e = b
                cnf.add(neg(J), b, neg(e))
    for s, x in enumerate(states):
        k = bin(x).count('1')
        for i in range(n):
            L = val[(d, i, s)]
            cnf.add(L if i >= n - k else -L)
    with open(path, 'w') as f:
        f.write(f"p cnf {cnf.nv} {len(cnf.cl)}\n")
        for cl in cnf.cl: f.write(" ".join(map(str, cl)) + " 0\n")
    return cnf.nv, len(cnf.cl)

def image_of_matching(M, n):
    return [v for v in range(1 << n)
            if all(not (((v >> a) & 1) == 1 and ((v >> b) & 1) == 0) for (a, b) in M)]

def halve(states, n):
    keep, seen = [], set()
    for v in states:
        c = ((1 << n) - 1) ^ v
        if c in seen: continue
        seen.add(v); keep.append(v)
    return keep

if __name__ == "__main__":
    what = sys.argv[1]
    if what == "b1":
        n, d = 11, 6
        M0 = ((0,1),(2,3),(4,5),(6,7),(8,9))
        S = image_of_matching(M0, n)   # NO complement-halving: negation is not a network symmetry
        print("states:", len(S))
        print("vars/clauses:", encode(n, d, S, sys.argv[2]))
    else:
        n, d = int(sys.argv[3]), int(sys.argv[4])
        S = [v for v in range(1 << n) if bin(v).count("1") not in (0, n)]  # sorted inputs are fixed points
        print("states:", len(S))
        print("vars/clauses:", encode(n, d, S, sys.argv[2]))
