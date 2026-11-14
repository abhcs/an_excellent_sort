"""Small helpers shared by the checks.  Channels are 0..n-1; a comparator (a, b) with a < b sends
the minimum to a; a layer is a list of comparators on disjoint channels."""
import itertools


def matchings(n, maximal=False):
    """All matchings (any size) on channels 0..n-1; with maximal=True only floor(n/2)-edge ones."""
    out = []

    def rec(free, cur):
        if not free:
            out.append(tuple(cur))
            return
        a, rest = free[0], free[1:]
        rec(rest, cur)
        for k, b in enumerate(rest):
            rec(rest[:k] + rest[k + 1:], cur + [(a, b)])

    rec(list(range(n)), [])
    if maximal:
        out = [m for m in out if len(m) == n // 2]
    return out


def run(layers, x):
    x = list(x)
    for layer in layers:
        for (a, b) in layer:
            if x[a] > x[b]:
                x[a], x[b] = x[b], x[a]
    return x


def sorts(layers, n):
    """0-1 principle: a network sorts iff it sorts all 2^n binary inputs."""
    return all(run(layers, v) == sorted(v) for v in itertools.product((0, 1), repeat=n))


def sentinel_step(cfg, layer):
    """cfg maps channel -> +1 (+inf) or -1 (-inf); every other channel holds a real value.
    Apply one layer.  Return None if some comparator meets two reals, else the new cfg."""
    c = dict(cfg)
    for (a, b) in layer:
        ia, ib = a in c, b in c
        if not ia and not ib:
            return None
        va, vb = c.get(a, 0), c.get(b, 0)      # -1 < 0 (a real) < +1
        if va > vb:                            # min goes to a
            if ia and ib:
                c[a], c[b] = c[b], c[a]
            elif ia:
                c[b] = c.pop(a)
            else:
                c[a] = c.pop(b)
    return c


def blinds(layers, cfg):
    """Does this placement of infinities keep the reals apart in all the given layers?"""
    for layer in layers:
        cfg = sentinel_step(cfg, layer)
        if cfg is None:
            return False
    return True


def placements(n, k):
    """All ways to put k infinities (with signs) on n input channels."""
    for pos in itertools.combinations(range(n), k):
        for sg in itertools.product((1, -1), repeat=k):
            yield dict(zip(pos, sg))
