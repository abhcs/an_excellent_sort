"""Float simplex (numpy, Bland's rule) for  max c.x  s.t.  A x <= b, x >= 0, b >= 0; returns x.
Used only to FIND certificates; blockcert.check verifies them exactly afterwards."""
import numpy as np


def simplex(c, A, b, tol=1e-9, maxit=200000):
    A = np.asarray(A, float); b = np.asarray(b, float); c = np.asarray(c, float)
    m, n = A.shape
    T = np.hstack([A, np.eye(m), b.reshape(-1, 1)])
    z = np.concatenate([-c, np.zeros(m + 1)])
    basis = list(range(n, n + m))
    for _ in range(maxit):
        cols = np.where(z[:-1] < -tol)[0]
        if len(cols) == 0:
            break
        col = cols[0]
        colv = T[:, col]
        mask = colv > tol
        if not mask.any():
            raise ValueError('unbounded')
        ratios = np.full(m, np.inf); ratios[mask] = T[mask, -1] / colv[mask]
        rmin = ratios.min()
        cand = np.where(ratios <= rmin + 1e-12)[0]
        row = min(cand, key=lambda i: basis[i])
        T[row] /= T[row, col]
        f = T[:, col].copy(); f[row] = 0
        T -= np.outer(f, T[row])
        z -= z[col] * T[row]
        basis[row] = col
    x = np.zeros(n + m)
    for i, bv in enumerate(basis):
        x[bv] = T[i, -1]
    return z[-1], x[:n]
