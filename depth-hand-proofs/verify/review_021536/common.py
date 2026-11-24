"""Independent helpers for reviewing the 02 15 36 H9 proof (written from scratch)."""
import itertools

L1 = ((0, 1), (2, 3), (4, 5))
L2 = ((0, 2), (1, 5), (3, 6))
DOC = '/Users/abhishek/Documents/an_excellent_sort/.claude/worktrees/depth-bounds-continue/depth-hand-proofs/'


def edges(s):
    s = s.strip().strip('`')
    if s in ('', 'none'):
        return ()
    return tuple(sorted(tuple(sorted(int(c) for c in tok)) for tok in s.split()))


def run(layers, x):
    x = list(x)
    for layer in layers:
        for a, b in layer:
            assert a < b
            if x[a] > x[b]:
                x[a], x[b] = x[b], x[a]
    return x


def matchings(n=9):
    out = []

    def rec(i, used, cur):
        if i == n:
            out.append(tuple(cur))
            return
        if i in used:
            rec(i + 1, used, cur)
            return
        rec(i + 1, used, cur)
        for j in range(i + 1, n):
            if j not in used:
                rec(i + 1, used | {i, j}, cur + [(i, j)])

    rec(0, frozenset(), [])
    return out


BIN = list(itertools.product((0, 1), repeat=9))


def order_info(layers):
    """Return (never_fire, always_swap) pair sets (i<j) using the 0-1 principle."""
    outs = [run(layers, x) for x in BIN]
    nf, sw = set(), set()
    for i, j in itertools.combinations(range(9), 2):
        if all(y[i] <= y[j] for y in outs):
            nf.add((i, j))
        if all(y[i] >= y[j] for y in outs):
            sw.add((i, j))
    return nf, sw


def trace(layers, placement):
    """Symbolic sentinel trace. placement: {input wire: +1/-1}.
    Returns sentinel signs at the end, list of real-real gate events as
    (layer index, track_a, track_b) where tracks are the identities of
    the real values' current 'slots' (a slot keeps its id along the wire
    a real occupies, swapping only when a sentinel moves past it)."""
    sign = [placement.get(w, 0) for w in range(9)]
    slot = list(range(9))
    events = []
    for k, layer in enumerate(layers):
        for a, b in layer:
            if sign[a] == 0 and sign[b] == 0:
                events.append((k, slot[a], slot[b]))
            else:
                # min goes to a: order by sign with real = 0
                if sign[a] > sign[b]:
                    sign[a], sign[b] = sign[b], sign[a]
                    slot[a], slot[b] = slot[b], slot[a]
    real = tuple(w for w in range(9) if sign[w] == 0)
    return dict(sign=sign, slot=slot, events=events, real=real)


def numeric_check(layers, placement, tr, trials=200, seed=1):
    """Check symbolic sentinel positions against numeric runs with random reals."""
    import random
    rng = random.Random(seed)
    for _ in range(trials):
        x = [rng.random() for _ in range(9)]
        for w, s in placement.items():
            x[w] = 1000.0 * s
        y = run(layers, x)
        for w in range(9):
            if tr['sign'][w] == 0:
                assert abs(y[w]) < 10, (placement, w, y)
            else:
                assert y[w] == 1000.0 * tr['sign'][w], (placement, w, y)


def schedulable(events, nlayers, cap):
    """Can the real-real gate events (in order) be put into nlayers layers with at
    most cap gates each, respecting per-slot order? Brute force (few events)."""
    m = len(events)
    if m > nlayers * cap:
        return False
    for assign in itertools.product(range(nlayers), repeat=m):
        ok = True
        last = {}
        for (k, a, b), L in zip(events, assign):
            for t in (a, b):
                if t in last and last[t] >= L:
                    ok = False
                    break
            if not ok:
                break
            last[a] = L
            last[b] = L
        if ok and all(assign.count(L) <= cap for L in range(nlayers)):
            return True
    return False


def partner_map(M):
    p = {}
    for a, b in M:
        p[a] = b
        p[b] = a
    return p


def swap78(M):
    pi = {v: v for v in range(9)}
    pi[7], pi[8] = 8, 7
    return tuple(sorted(tuple(sorted((pi[a], pi[b]))) for a, b in M))
