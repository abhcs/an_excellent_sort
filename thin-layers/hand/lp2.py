"""Dense two-phase simplex (numpy, Bland's rule): max c.x  s.t.  A x <= b (any signs), x >= 0.
Returns (status, value, x) with status 'optimal', 'infeasible' or 'unbounded'.  Used only to SEARCH;
anything claimed is re-checked in exact arithmetic."""
import numpy as np


def _pivot(T, basis, row, col):
    T[row] /= T[row, col]
    f = T[:, col].copy(); f[row] = 0
    T -= np.outer(f, T[row])
    basis[row] = col


def _run(T, basis, obj_row, ncols, tol, maxit, allowed):
    m = len(basis)                                   # constraint rows are 0 .. m-1
    for _ in range(maxit):
        z = T[obj_row, :ncols]
        cols = [j for j in np.where(z < -tol)[0] if allowed[j]]
        if not cols:
            return 'optimal'
        col = cols[0]
        colv = T[:m, col]
        mask = colv > tol
        if not mask.any():
            return 'unbounded'
        ratios = np.full(m, np.inf); ratios[mask] = T[:m, -1][mask] / colv[mask]
        rmin = ratios.min()
        cand = np.where(ratios <= rmin + 1e-12)[0]
        row = min(cand, key=lambda i: basis[i])
        _pivot(T, basis, row, col)
    raise RuntimeError('iteration limit')


def solve(c, A, b, tol=1e-9, maxit=100000):
    A = np.asarray(A, float); b = np.asarray(b, float); c = np.asarray(c, float)
    m, n = A.shape
    neg = b < 0
    A = A.copy(); b = b.copy()
    A[neg] *= -1; b[neg] *= -1                       # rows now: A x + s = b (s >= 0) or A x - s = b (s >= 0)
    nart = int(neg.sum())
    ncols = n + m + nart
    T = np.zeros((m + 2, ncols + 1))
    T[:m, :n] = A
    for i in range(m):
        T[i, n + i] = -1.0 if neg[i] else 1.0
    basis = []
    k = 0
    for i in range(m):
        if neg[i]:
            T[i, n + m + k] = 1.0; basis.append(n + m + k); k += 1
        else:
            basis.append(n + i)
    T[:m, -1] = b
    # phase II objective row (index m), phase I row (index m+1): minimize sum of artificials
    T[m, :n] = -c
    if nart:
        T[m + 1, n + m:n + m + nart] = 1.0
        for i in range(m):
            if neg[i]:
                T[m + 1] -= T[i]
        allowed = [True] * ncols
        st = _run(T, basis, m + 1, ncols, tol, maxit, allowed)
        if T[m + 1, -1] < -1e-7:
            return 'infeasible', None, None
        # drive artificials out of the basis where possible
        for i in range(m):
            if basis[i] >= n + m:
                for j in range(n + m):
                    if abs(T[i, j]) > 1e-9:
                        _pivot(T, basis, i, j); break
    allowed = [j < n + m for j in range(ncols)]
    st = _run(T, basis, m, ncols, tol, maxit, allowed)
    if st != 'optimal':
        return st, None, None
    x = np.zeros(ncols)
    for i, bv in enumerate(basis):
        x[bv] = T[i, -1]
    return 'optimal', float(T[m, -1]), x[:n]


if __name__ == '__main__':
    # tiny tests: max x+y s.t. x+y<=4, x>=1 (-x<=-1), y>=2 (-y<=-2)  -> 4
    print(solve([1, 1], [[1, 1], [-1, 0], [0, -1]], [4, -1, -2]))
    # infeasible: x<=1, x>=2
    print(solve([1], [[1], [-1]], [1, -2]))
    # min x+2y s.t. x+y>=3, x<=2 -> x=2,y=1 -> 4 (max -x-2y = -4)
    print(solve([-1, -2], [[-1, -1], [1, 0]], [-3, 2]))
