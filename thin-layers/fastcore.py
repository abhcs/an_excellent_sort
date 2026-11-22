"""fastcore.py -- ctypes wrapper for fastcore.c (README §8.11). Builds fastcore.dylib (macOS) or
fastcore.so with $CC (default cc) when it is missing or older than the source. Every function has a
pure-Python counterpart that it must agree with (test_fastcore.py); the prover only uses them to
search, and check_facts.py re-checks every proof step without them. Set SP_PURE=1 to keep everything
in Python, SP_FC_VERBOSE=1 to see why the core did not load."""
import ctypes, os, subprocess, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(_HERE, 'fastcore.c')
_LIB = os.path.join(_HERE, 'fastcore.dylib' if sys.platform == 'darwin' else 'fastcore.so')


def _load():
    if os.environ.get('SP_PURE'):
        return None
    try:
        if not os.path.exists(_LIB) or os.path.getmtime(_LIB) < os.path.getmtime(_SRC):
            cc = os.environ.get('CC', 'cc')
            subprocess.run([cc, '-O3', '-shared', '-fPIC', '-o', _LIB, _SRC], check=True,
                           capture_output=True)
        lib = ctypes.CDLL(_LIB)
    except Exception as e:
        if os.environ.get('SP_FC_VERBOSE'):
            print('fastcore not loaded:', e, file=sys.stderr)
        return None
    u32p, intp, u64p = ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_uint64)
    lib.fc_outputs.argtypes = [ctypes.c_int, ctypes.c_int, intp, intp, u32p]
    lib.fc_apply_layer.argtypes = [ctypes.c_int, u32p, ctypes.c_int, ctypes.c_int, intp, u32p]
    lib.fc_chan_sigs.argtypes = [ctypes.c_int, u32p, ctypes.c_int, intp]
    lib.fc_nonredundant.argtypes = [ctypes.c_int, u32p, ctypes.c_int, intp]
    lib.fc_equivalent.argtypes = [ctypes.c_int, u32p, ctypes.c_int, u32p, ctypes.c_int, ctypes.c_long, intp, intp]
    lib.fc_automorphisms.argtypes = [ctypes.c_int, u32p, ctypes.c_int, ctypes.c_int, ctypes.c_long, intp, intp]
    lib.fc_canonical_layers.argtypes = [ctypes.c_int, ctypes.c_int, intp, ctypes.c_int, ctypes.c_int, intp,
                                        ctypes.c_long, intp]
    lib.fc_canonical_layers.restype = ctypes.c_long
    lib.fc_qcover.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, intp, u64p, u32p, intp, intp, intp, intp,
                              intp, intp, intp, intp, intp, intp, ctypes.c_int, intp, ctypes.c_long, ctypes.c_int,
                              intp, intp, intp, ctypes.c_char_p]
    lib.fc_qcover.restype = ctypes.c_long
    lib.fc_child_keys.argtypes = [ctypes.c_int, u32p, ctypes.c_int, ctypes.c_int, intp, ctypes.c_int,
                                  ctypes.c_long, intp, u64p]
    return lib


LIB = _load()
available = LIB is not None


def _u32(X):
    xs = sorted(X)
    return (ctypes.c_uint32 * max(1, len(xs)))(*xs), len(xs)


def _ints(v):
    v = list(v)
    return (ctypes.c_int * max(1, len(v)))(*v)


def outputs(n, layers):
    sizes = [len(L) for L in layers]
    flat = [v for L in layers for c in L for v in c]
    out = (ctypes.c_uint32 * (1 << n))()
    k = LIB.fc_outputs(n, len(layers), _ints(sizes), _ints(flat), out)
    return frozenset(out[:k])


def apply_layer(n, X, L):
    arr, m = _u32(X)
    out = (ctypes.c_uint32 * max(1, m))()
    k = LIB.fc_apply_layer(n, arr, m, len(L), _ints([v for c in L for v in c]), out)
    return frozenset(out[:k])


def chan_sigs(X, n):
    arr, m = _u32(X)
    sig = (ctypes.c_int * (n * (n + 1)))()
    LIB.fc_chan_sigs(n, arr, m, sig)
    return [tuple(sig[i * (n + 1):(i + 1) * (n + 1)]) for i in range(n)]


def nonredundant(n, X):
    arr, m = _u32(X)
    out = (ctypes.c_int * (n * n))()
    k = LIB.fc_nonredundant(n, arr, m, out)
    return [(out[2 * i], out[2 * i + 1]) for i in range(k)]


def equivalent(A, B, n, budget=50000):
    """(perm, comp) with B = perm(A) or perm(complement A), else None (also when the budget runs out)."""
    if len(A) != len(B):
        return None
    a, na = _u32(A)
    b, nb = _u32(B)
    perm = (ctypes.c_int * n)()
    comp = ctypes.c_int(0)
    r = LIB.fc_equivalent(n, a, na, b, nb, budget, perm, ctypes.byref(comp))
    return (tuple(perm[:n]), bool(comp.value)) if r == 1 else None


def automorphisms(X, n, maxg=2000, budget=200000):
    """Relabelings (perm, comp) with perm(X) = X (comp: perm(complement X) = X), identity included;
    (list, complete?)."""
    arr, m = _u32(X)
    perms = (ctypes.c_int * (maxg * n))()
    comps = (ctypes.c_int * maxg)()
    r = LIB.fc_automorphisms(n, arr, m, maxg, budget, perms, comps)
    k = abs(r)
    return [(tuple(perms[g * n:(g + 1) * n]), bool(comps[g])) for g in range(k)], r >= 0


def canonical_layers(n, pairs, cap, auts):
    """Non-empty layers over pairs with at most cap comparators, in the order of the prover's
    enumeration, keeping only those that no relabeling in auts maps to a smaller layer."""
    pairs = sorted(pairs, key=lambda p: p[0] * 32 + p[1])
    flat = _ints([v for p in pairs for v in p])
    perms = _ints([v for p, _ in auts for v in p])
    room = 1 << 16
    while True:
        out = (ctypes.c_int * (room * (cap + 1)))()
        cnt = LIB.fc_canonical_layers(n, len(pairs), flat, cap, len(auts), perms, room, out)
        if cnt <= room:
            break
        room = cnt
    res = []
    w = cap + 1
    for l in range(cnt):
        m = out[l * w]
        res.append(tuple(pairs[out[l * w + 1 + c]] for c in range(m)))
    return res


def child_keys(n, X, layers):
    """Per layer: (|Y|, hash, hash, invariant) for its child Y = layer(X); equal children give
    equal keys, equivalent children equal sizes and invariants."""
    arr, m = _u32(X)
    pairs = sorted({c for L in layers for c in L})
    idx = {p: k for k, p in enumerate(pairs)}
    cap = max((len(L) for L in layers), default=1)
    lay = []
    for L in layers:
        lay.append(len(L))
        lay.extend(idx[c] for c in L)
        lay.extend([0] * (cap - len(L)))
    keys = (ctypes.c_uint64 * (4 * max(1, len(layers))))()
    LIB.fc_child_keys(n, arr, m, len(pairs), _ints([v for p in pairs for v in p]), cap, len(layers),
                      _ints(lay), keys)
    return [tuple(keys[4 * l:4 * l + 4]) for l in range(len(layers))]


def qcover(n, t2, states, layers, lp=0):
    """The greedy choice of sprove.Prover._qcover: states are its (S, r, (content, chlvl, asap, h), bad,
    lemmas, residual caps, real comparisons per prefix layer) entries, lp the prefix length.
    Returns (indices of the chosen states, indices of open layers)."""
    assert n <= 16
    QMAXH = 64
    hasbad, bad, real, chlvl, asap, hh, rr = [], [], [], [], [], [], []
    lemoff, lemcnt, lem, capoff, caplen, caps = [], [], [], [], [], []
    lemat, capat = {}, {}
    asis = []
    for S, r, st, b, lems, capsr, ai in states:
        assert len(ai) == lp
        asis += list(ai)
        content, cl, asp, h = st
        assert h < QMAXH - 1 and len(asp) == h
        hasbad.append(0 if b is None else 1)
        b = b or 0
        bad += [b & 0xFFFFFFFFFFFFFFFF, b >> 64]
        real.append(sum(1 << c for c in range(n) if content[c] == 'r'))
        chlvl += cl
        asap += list(asp) + [0] * (QMAXH - h)
        hh.append(h)
        rr.append(r)
        lk = tuple((d2, a2, m2) for d2, a2, m2, _ in lems)
        if lk not in lemat:
            lemat[lk] = len(lem) // 3
            lem += [v for e in lk for v in e]
        lemoff.append(lemat[lk])
        lemcnt.append(len(lk))
        ck = tuple(capsr)
        if ck not in capat:
            capat[ck] = len(caps)
            caps += list(ck)
        capoff.append(capat[ck])
        caplen.append(len(ck))
    ns = len(states)
    cap = max((len(L) for L in layers), default=1)
    flat = []
    for L in layers:
        flat.append(len(L))
        for i, j in L:
            flat += [i, j]
        flat += [0] * (2 * (cap - len(L)))
    chosen = (ctypes.c_int * max(1, ns))()
    nch = ctypes.c_int(0)
    opn = ctypes.create_string_buffer(max(1, len(layers)))
    LIB.fc_qcover(n, t2, ns, _ints(hasbad), (ctypes.c_uint64 * max(1, len(bad)))(*bad),
                  (ctypes.c_uint32 * max(1, ns))(*real), _ints(chlvl), _ints(asap), _ints(hh), _ints(rr),
                  _ints(lemoff), _ints(lemcnt), _ints(lem), _ints(capoff), _ints(caplen), _ints(caps),
                  lp, _ints(asis), len(layers), cap, _ints(flat), chosen, ctypes.byref(nch), opn)
    raw = opn.raw
    return list(chosen[:nch.value]), [i for i in range(len(layers)) if raw[i]]
