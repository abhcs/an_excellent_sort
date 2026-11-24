"""A small exact LP solver (dense simplex, Bland's rule, Fractions) for
    maximize c.x  subject to  A x <= b,  x >= 0,  with b >= 0.
Returns (value, x, y) with y the optimal dual (y >= 0, A^T y >= c, b.y = value).  Meant for the small
fractional-matching / vertex-cover problems of efficient-prefixes.md section 7.3, not for speed."""
from fractions import Fraction as F


def simplex(c, A, b):
    m, n = len(A), len(c)
    # tableau rows: [A | I | b]; objective row: [-c | 0 | 0]
    T = [[F(v) for v in A[i]] + [F(1 if j == i else 0) for j in range(m)] + [F(b[i])] for i in range(m)]
    z = [F(-v) for v in c] + [F(0)] * m + [F(0)]
    basis = [n + i for i in range(m)]
    while True:
        col = next((j for j in range(n + m) if z[j] < 0), None)      # Bland: lowest index entering
        if col is None:
            break
        best, row = None, None
        for i in range(m):
            if T[i][col] > 0:
                r = T[i][-1] / T[i][col]
                if best is None or r < best or (r == best and basis[i] < basis[row]):
                    best, row = r, i
        if row is None:
            raise ValueError('unbounded')
        piv = T[row][col]
        T[row] = [v / piv for v in T[row]]
        for i in range(m):
            if i != row and T[i][col] != 0:
                f = T[i][col]
                T[i] = [a - f * b_ for a, b_ in zip(T[i], T[row])]
        f = z[col]
        z = [a - f * b_ for a, b_ in zip(z, T[row])]
        basis[row] = col
    x = [F(0)] * n
    for i, bv in enumerate(basis):
        if bv < n:
            x[bv] = T[i][-1]
    y = [z[n + i] for i in range(m)]          # duals = reduced costs of the slacks
    return z[-1], x, y


def fractional_cover(nv, w):
    """least fractional vertex cover of edge weights w {(u,v): weight}: min sum c, c_u + c_v >= w_uv.
    Solved as its dual, the largest fractional matching.  Returns (value, cover list)."""
    edges = [e for e, wt in w.items() if wt > 0]
    if not edges:
        return F(0), [F(0)] * nv
    c = [w[e] for e in edges]
    A = [[1 if v in e else 0 for e in edges] for v in range(nv)]
    val, x, y = simplex(c, A, [1] * nv)
    # check duality exactly
    assert all(y[u] + y[v] >= w[(u, v)] for (u, v) in edges) and sum(y) == val
    return val, y


if __name__ == '__main__':
    # triangle with unit weights: matching 1, fractional cover 3/2
    print(fractional_cover(3, {(0, 1): 1, (1, 2): 1, (0, 2): 1}))
    print(fractional_cover(4, {(0, 1): 3, (2, 3): 2, (1, 2): 1}))
