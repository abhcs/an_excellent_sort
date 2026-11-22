#!/usr/bin/env python3
"""sentinel_prover.py -- decide "is there an n-channel sorting network of depth d?" with infinities.

EXT(P, t): can the prefix P (a standard comparator network on n channels) be extended by t more
layers into a sorting network?  D(n) <= d  iff  EXT(L1, d - 1) for the maximal normal-form first
layer L1 (Fact A).  The procedure applies five rules:

  sorted    every output of P is sorted                          -> yes
  zero      t = 0 and some output is unsorted                    -> no
  known     t >= D(n) (append a known optimal sorter)            -> yes   (pruning only)
  sentinel  fix the inputs in S to +inf / -inf.  The real inputs pass through a residual prefix R
            on n - |S| channels (comparators met by a sentinel track are routings).  If P;N sorts,
            the residual of P;N is a sorter on n - |S| channels (Fact B), so EXT(P, t) implies
            EXT(R, t).  Hence NO(R, t) -> NO(P, t).  Shortcut: R's real comparisons reschedule into
            h layers, so h + t < D(n - |S|) already gives NO(R, t).
  split     EXT(P, t) = OR over next layers L of EXT(P;L, t - 1)        (complete by itself)

EXT(P, t) depends only on the output set of P up to channel permutation and complement
(Bundala-Zavodny 2014), which is the memo key.  The procedure is sound (each rule is a theorem)
and complete (split alone is exhaustive search).  A NO answer comes with a proof DAG whose nodes
are "sentinels S reduce this to node k" or "every next layer leads to a NO node".

usage: sentinel_prover.py N [DEPTH] [--kmax K]
"""
import itertools, sys, time
from functools import lru_cache

DUP = {1: 0, 2: 1, 3: 3, 4: 3, 5: 5, 6: 5, 7: 6, 8: 6, 9: 7, 10: 7, 11: 8, 12: 8}   # known upper bounds
DLOW = {1: 0, 2: 1}            # lower bounds proved by this procedure, filled bottom-up


def popcount(x):
    return x.bit_count()


def is_sorted(x, n):
    # sorted (non-decreasing in channel index) <=> the ones form a suffix
    w = popcount(x)
    return x == ((1 << n) - 1) ^ ((1 << (n - w)) - 1)


def apply_layer(L, x):
    for i, j in L:
        if (x >> i) & 1 and not (x >> j) & 1:
            x ^= (1 << i) | (1 << j)
    return x


def outputs(n, layers):
    if _fc is not None and n >= 8:
        return _fc.outputs(n, layers)
    return _py_outputs(n, layers)


def _py_outputs(n, layers):
    out = set(range(1 << n))
    for L in layers:
        out = {apply_layer(L, x) for x in out}
    return frozenset(out)


def canon(X, n, cap=1500):
    """Canonical form of X under channel permutations and complement (exact when ties are few)."""
    mask = (1 << n) - 1
    best = None
    for Y in (X, frozenset(x ^ mask for x in X)):
        pcs = {y: popcount(y) for y in Y}
        sig = []
        for i in range(n):
            c = [0] * (n + 1)
            for y in Y:
                if (y >> i) & 1:
                    c[pcs[y]] += 1
            sig.append(tuple(c))
        order = sorted(range(n), key=lambda i: sig[i])
        groups = [list(g) for _, g in itertools.groupby(order, key=lambda i: sig[i])]
        total = 1
        for g in groups:
            for k in range(2, len(g) + 1):
                total *= k
        choices = itertools.product(*[itertools.permutations(g) for g in groups]) if total <= cap \
            else [tuple(tuple(g) for g in groups)]
        for ch in choices:
            perm = [c for g in ch for c in g]          # new position k <- old channel perm[k]
            key = tuple(sorted(sum(((y >> perm[k]) & 1) << k for k in range(n)) for y in Y))
            if best is None or key < best:
                best = key
    return best


class _Budget(Exception):
    pass


_BITS = [tuple(i for i in range(16) if (x >> i) & 1) for x in range(1 << 14)]

try:                                    # compiled core (fastcore.c); SP_PURE=1 keeps pure Python
    import fastcore as _fcmod
    _fc = _fcmod if _fcmod.available else None
except Exception:
    _fc = None


def chan_sigs(X, n):
    """Per channel: number of vectors with a 1 there, by weight (a relabelling invariant)."""
    if _fc is not None and len(X) >= 64:
        return _fc.chan_sigs(X, n)
    return _py_chan_sigs(X, n)


def _py_chan_sigs(X, n):
    sig = [[0] * (n + 1) for _ in range(n)]
    for x in X:
        b = _BITS[x]
        w = len(b)
        for i in b:
            sig[i][w] += 1
    return [tuple(c) for c in sig]


def invariant(X, n):
    """Invariant of X under channel permutations and complement (cheap; not a canonical form)."""
    mask = (1 << n) - 1
    best = None
    for Y in (X, frozenset(x ^ mask for x in X)):
        k = (len(Y), tuple(sorted(chan_sigs(Y, n))))
        if best is None or k < best:
            best = k
    return best


def equivalent(A, B, n, budget=50000):
    """True iff B = sigma(A) or B = sigma(complement of A) for a channel permutation sigma
    (explicit backtracking search; on budget exhaustion answers False, which only loses sharing)."""
    if len(A) != len(B):
        return False
    if _fc is not None and len(A) >= 32:
        return _fc.equivalent(A, B, n, budget) is not None
    return _py_equivalent(A, B, n, budget)


def _py_equivalent(A, B, n, budget=50000):
    if len(A) != len(B):
        return False
    mask = (1 << n) - 1
    Bl = list(B)
    sB = chan_sigs(B, n)
    for A2 in (A, frozenset(a ^ mask for a in A)):
        sA = chan_sigs(A2, n)
        if sorted(sA) != sorted(sB):
            continue
        cand = [[j for j in range(n) if sB[j] == sA[i]] for i in range(n)]
        order = sorted(range(n), key=lambda i: len(cand[i]))
        Al = list(A2)
        used = [False] * n
        nodes = [0]

        def rec(t, kA, kB):
            if t == n:
                return True
            nodes[0] += 1
            if nodes[0] > budget:
                raise _Budget
            i = order[t]
            for j in cand[i]:
                if used[j]:
                    continue
                nA = [ka * 2 + ((a >> i) & 1) for ka, a in zip(kA, Al)]
                nB = [kb * 2 + ((b >> j) & 1) for kb, b in zip(kB, Bl)]
                if sorted(nA) != sorted(nB):
                    continue
                used[j] = True
                if rec(t + 1, nA, nB):
                    return True
                used[j] = False
            return False
        try:
            if rec(0, [popcount(a) for a in Al], [popcount(b) for b in Bl]):
                return True
        except _Budget:
            pass
    return False


def residual(n, layers, S):
    """S: dict input channel -> '+' or '-'.  Returns (r, standard residual layers, h)."""
    r, std, h, _, _ = residual2(n, layers, S)
    return r, std, h


def residual2(n, layers, S):
    """As residual, plus the layer sizes of the as-soon-as-possible and as-late-as-possible
    schedules of the real comparisons (both of height h)."""
    content = [None] * n
    real = [c for c in range(n) if c not in S]
    for c in range(n):
        content[c] = S[c] if c in S else real.index(c)
    gen = []
    for L in layers:
        gl = []
        for i, j in L:
            a, b = content[i], content[j]
            sa, sb = isinstance(a, str), isinstance(b, str)
            if sa and sb:
                if a == '+' and b == '-':
                    content[i], content[j] = b, a
            elif sa:
                if a == '+':
                    content[i], content[j] = b, a
            elif sb:
                if b == '-':
                    content[i], content[j] = b, a
            else:
                gl.append((a, b))                       # min to wire a, max to wire b
        if gl:
            gen.append(gl)
    # rescheduled height (longest chain of real comparisons sharing a wire)
    lvl = {}
    h = 0
    seq = []
    for gl in gen:
        for a, b in gl:
            v = max(lvl.get(a, 0), lvl.get(b, 0)) + 1
            lvl[a] = lvl[b] = v
            h = max(h, v)
            seq.append((a, b, v))
    asap = [0] * h
    for a, b, v in seq:
        asap[v - 1] += 1
    tail = {}
    alap = [0] * h
    for a, b, v in reversed(seq):
        u = max(tail.get(a, 0), tail.get(b, 0)) + 1
        tail[a] = tail[b] = u
        alap[h - u] += 1
    # untangle (Knuth 5.3.4-16): wires labelled by initial rank
    r = len(real)
    m = list(range(r))
    std = []
    for gl in gen:
        sl = []
        for a, b in gl:
            a2, b2 = m[a], m[b]
            if a2 < b2:
                sl.append((a2, b2))
            else:
                sl.append((b2, a2))
                m[a], m[b] = b2, a2
        std.append(tuple(sl))
    return r, tuple(std), h, asap, alap


def sat_oracle(n, layers, t, caps, seconds=20.0, init=200, batch=30, conflicts=20000):
    """Search for an extension with netsat's CEGAR model (only used to skip branches that DO
    extend; its UNSAT answers are never used as proof).  Returns a verified network, None for
    UNSAT, or 'UNKNOWN' on timeout."""
    import os, random, threading
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'd18-search'))
    from netsat import Model, prefix_images, apply_layers, verify_all
    from netsat import is_sorted as ns_sorted
    from pysat.card import CardEnc, EncType
    prefix = [list(L) for L in layers]
    U = sorted(x for x in prefix_images(n, prefix) if not ns_sorted(x, n))
    M = Model(n, t, U, solver='glucose4')   # CaDiCaL in pysat has no interruptible solve
    for i, c in enumerate(caps):
        lits = sorted(M.g[i].values())
        enc = CardEnc.atmost(lits=lits, bound=c, top_id=M.nv, encoding=EncType.seqcounter)
        for cl in enc.clauses:
            M.add(cl)
        M.nv = max(M.nv, enc.nv)
    rng = random.Random(0)
    added = set(U if len(U) <= init else rng.sample(U, init))
    for x in added:
        M.add_input(x)
    deadline = time.time() + seconds
    while True:
        if time.time() > deadline:
            return 'UNKNOWN'
        M.S.conf_budget(conflicts)               # a conflict budget: no watchdog threads
        ok = M.S.solve_limited()
        if ok is None:
            return 'UNKNOWN'
        if not ok:
            return None
        net = M.network(M.S.get_model())
        fails = [x for x in U if x not in added and not ns_sorted(apply_layers(net, x), n)]
        if not fails:
            full = prefix + [list(L) for L in net]
            assert verify_all(n, full), 'oracle network fails verification'
            assert all(len(net[i]) <= c for i, c in enumerate(caps) if i < len(net))
            return full
        rng.shuffle(fails)
        for x in fails[:batch]:
            M.add_input(x)
            added.add(x)


def norm_caps(n, t, caps):
    """Caps for the next layers; entries >= n//2 at the end bind nothing and are dropped."""
    caps = tuple(caps[:t])
    while caps and caps[-1] >= n // 2:
        caps = caps[:-1]
    return caps


class Prover:
    """EXT(n, P, t, caps): P extends by t layers, the next len(caps) of them with <= caps[i]
    comparators.  NO answers are recorded in self.proof as
      ('quick', S, h, r)          sentinels S leave r reals with h real layers, h + t < D(r)
      ('sent', S, child)          sentinels S reduce to the NO node `child` (fewer channels)
      ('split', children)         every next layer (up to symmetry) gives a NO node
    """
    def __init__(self, kmax=3, log=None, oracle=False, oracle_min_n=9, max_rec=40):
        self.max_rec = max_rec
        self.trace = None              # key of a node whose split is logged child by child
        self.lemmas = {}               # r -> list of (d, a, m, key): proved SS(r, d, a, m)
        self.memo, self.proof, self.rep, self.table = {}, {}, {}, {}
        self.next_id = 0
        self.oracle, self.oracle_min_n = oracle, oracle_min_n
        self.witness = {}
        self.kmax = kmax
        self.stats = {'nodes': 0, 'memo': 0, 'sent_quick': 0, 'sent_rec': 0, 'split_no': 0, 'yes': 0,
                      'oracle_yes': 0, 'oracle_no': 0, 'oracle_unknown': 0}
        self.log = log

    def key(self, n, X, t, caps):
        """Node id for (n, t, caps, X up to relabelling and complement): registry lookup by an
        invariant, then an explicit equivalence test against the classes with that invariant."""
        inv = (n, t, caps, invariant(X, n))
        lst = self.table.setdefault(inv, [])
        for Xr, kid in lst:
            if equivalent(Xr, X, n):
                return kid
        self.next_id += 1                 # ids must be unique: (n, t, serial number)
        kid = (n, t, self.next_id)
        lst.append((X, kid))
        return kid

    def ext(self, n, layers, t, X=None, caps=()):
        if X is None:
            X = outputs(n, layers)
        caps = norm_caps(n, t, caps)
        if all(is_sorted(x, n) for x in X):
            return True
        if t == 0:
            return False
        if not caps and t >= DUP.get(n, 99):
            return True
        key = self.key(n, X, t, caps)
        if key in self.memo:
            self.stats['memo'] += 1
            return self.memo[key]
        self.stats['nodes'] += 1
        if self.log and self.stats['nodes'] % 500 == 0:
            self.log(f"  progress: {self.stats} memo={len(self.memo)}")
        self.rep[key] = (n, layers, t, caps)
        if self.oracle and n >= self.oracle_min_n and t >= 2:
            w = sat_oracle(n, layers, t, caps)
            if isinstance(w, list):
                self.stats['oracle_yes'] += 1
                self.witness[key] = w
                self.memo[key] = True
                return True
            self.stats['oracle_no' if w is None else 'oracle_unknown'] += 1
        res = self._ext(n, layers, t, X, caps, key)
        self.memo[key] = res
        return res

    def _ext(self, n, layers, t, X, caps, key):
        # sentinel rule.  Candidate sentinels: those whose track (alone) meets a comparator in every
        # prefix layer (all but one if there are too few); sets are drawn from this pool.  Restricting
        # the candidates keeps the procedure sound and complete (the split rule is the fallback).
        Lp = len(layers)
        total = sum(len(L) for L in layers)
        single = []
        for c in range(n):
            for sg in '+-':
                pos, hit = c, 0
                for L in layers:
                    for i, j in L:
                        if pos == i or pos == j:
                            hit += 1
                            pos = j if sg == '+' else i
                            break
                single.append((hit, c, sg))
        pool = [(c, sg) for hit, c, sg in single if hit == Lp]
        if len({c for c, _ in pool}) < self.kmax:
            pool = [(c, sg) for hit, c, sg in single if hit >= Lp - 1]
        cands = []
        for k in range(1, min(self.kmax, n - 2) + 1):
            r = n - k
            rec_ok = bool(norm_caps(r, t, caps)) or t < DUP.get(r, 99)
            hmax = DLOW[r] - t - 1 if r in DLOW else -1
            # a quick closure needs the >= total - k*Lp real comparisons to fit in hmax layers
            quick_ok = hmax >= 0 and total - k * Lp <= hmax * (r // 2)
            lems = [lm for lm in self.lemmas.get(r, ()) if lm[0] - t >= 1]
            capsr = norm_caps(r, t, caps)
            quick_ok = quick_ok or bool(lems)
            if not (rec_ok or quick_ok):
                continue
            if quick_ok:                 # every sentinel set: a quick closure may need idle channels
                combos = (tuple(zip(ch, sg)) for ch in itertools.combinations(range(n), k)
                          for sg in itertools.product('+-', repeat=k))
            else:                        # recursion only: sets from the absorbing pool
                combos = itertools.combinations(pool, k)
            for combo in combos:
                if len({c for c, _ in combo}) < k:
                    continue
                S = dict(combo)
                rr, R, h, asap, alap = residual2(n, layers, S)
                if quick_ok and h <= hmax:
                    self.stats['sent_quick'] += 1
                    self.proof[key] = ('quick', S, h, r)
                    return False
                for d2, a2, m2, lkey in lems:
                    if h + t > d2:
                        continue
                    for name, prof in (('asap', asap), ('alap', alap)):
                        sizes = [prof[i] if i < h else (capsr[i - h] if i - h < len(capsr) else r // 2)
                                 for i in range(m2)]
                        if all(x <= a2 for x in sizes):
                            self.stats['sent_lemma'] = self.stats.get('sent_lemma', 0) + 1
                            self.proof[key] = ('lemma', S, name, h, r, (d2, a2, m2), lkey)
                            return False
                if rec_ok:
                    cands.append((h, k, S, R))
        cands.sort(key=lambda c: (c[0], -c[1]))
        seen = set()
        tried = 0
        for h, k, S, R in cands:
            if tried >= self.max_rec:
                break
            r = n - k
            XR = outputs(r, R)
            rc = norm_caps(r, t, caps)
            ck = self.key(r, XR, t, rc)
            if ck in seen:
                continue
            seen.add(ck)
            tried += 1
            if not self.ext(r, R, t, XR, rc):
                self.stats['sent_rec'] += 1
                self.proof[key] = ('sent', S, ck)
                return False
        # split rule
        cap0 = caps[0] if caps else n // 2
        rest = caps[1:]
        nonred = [(i, j) for i in range(n) for j in range(i + 1, n)
                  if any((x >> i) & 1 and not (x >> j) & 1 for x in X)]
        children = {}
        rest_n = norm_caps(n, t - 1, rest)
        def rec(start, used, cur):
            if cur:
                L = tuple(cur)
                Y = frozenset(apply_layer(L, x) for x in X)
                ck = self.key(n, Y, t - 1, rest_n)
                if ck not in children:
                    children[ck] = (L, Y)
            if len(cur) == cap0:
                return
            for idx in range(start, len(nonred)):
                i, j = nonred[idx]
                if used >> i & 1 or used >> j & 1:
                    continue
                cur.append((i, j))
                rec(idx + 1, used | (1 << i) | (1 << j), cur)
                cur.pop()
        rec(0, 0, [])
        kids = sorted(children.items(), key=lambda c: len(c[1][1]))
        ckeys = []
        tr = self.log if (self.trace is not None and key == self.trace and self.log) else None
        if tr:
            tr(f'TRACE split of the traced node: {len(kids)} cases (+ empty layer)')
        t_split = time.time()
        for idx, (ck, (L, Y)) in enumerate(kids):
            if self.ext(n, layers + (L,), t - 1, Y, rest):
                self.stats['yes'] += 1
                if tr:
                    tr(f'TRACE case {idx + 1}/{len(kids)} EXTENDS: layer {list(L)}')
                return True
            ckeys.append(ck)
            if tr:
                tr(f'TRACE case {idx + 1}/{len(kids)} closed ({time.time() - t_split:.0f}s, nodes {self.stats["nodes"]}): layer {list(L)}')
        if self.ext(n, layers, t - 1, X, rest):     # empty next layer
            return True
        ckeys.append(self.key(n, X, t - 1, norm_caps(n, t - 1, rest)))
        self.stats['split_no'] += 1
        self.proof[key] = ('split', ckeys)
        return False

    def proof_dag(self, root):
        """Nodes reachable from root through recorded NO steps (trivial NO leaves are t = 0)."""
        seen, stack = set(), [root]
        while stack:
            k = stack.pop()
            if k in seen or k not in self.proof:
                continue
            seen.add(k)
            st = self.proof[k]
            if st[0] == 'sent':
                stack.append(st[2])
            elif st[0] == 'split':
                stack.extend(st[1])
            elif st[0] == 'lemma':
                stack.append(st[6])
        kinds = {}
        for k in seen:
            kinds[self.proof[k][0]] = kinds.get(self.proof[k][0], 0) + 1
        return seen, kinds

    def export(self, roots, path):
        """Write the proof DAG reachable from roots as JSON lines (one node per line)."""
        import json
        seen = set()
        for r in roots:
            seen |= self.proof_dag(r)[0]
        ids = {k: i for i, k in enumerate(sorted(seen, key=lambda k: (k[0], k[1])))}
        with open(path, 'w') as f:
            for k, i in sorted(ids.items(), key=lambda kv: kv[1]):
                n, layers, t, caps = self.rep[k]
                st = self.proof[k]
                rec = {'id': i, 'n': n, 't': t, 'caps': list(caps), 'prefix': [[list(c) for c in L] for L in layers]}
                if st[0] == 'quick':
                    rec['step'] = {'rule': 'quick', 'S': {str(c): v for c, v in st[1].items()}, 'h': st[2], 'r': st[3]}
                elif st[0] == 'sent':
                    rec['step'] = {'rule': 'sent', 'S': {str(c): v for c, v in st[1].items()}, 'child': ids.get(st[2])}
                elif st[0] == 'lemma':
                    rec['step'] = {'rule': 'lemma', 'S': {str(c): v for c, v in st[1].items()}, 'sched': st[2],
                                   'h': st[3], 'r': st[4], 'ss': list(st[5]), 'lemma_root': ids.get(st[6])}
                else:
                    rec['step'] = {'rule': 'split', 'children': [ids.get(c) for c in st[1]]}
                f.write(json.dumps(rec) + '\n')
        return ids

    def describe(self, root, limit=60):
        seen, _ = self.proof_dag(root)
        order = sorted(seen, key=lambda k: (-k[0], -k[1]))
        names = {k: f'N{i}' for i, k in enumerate(order)}
        lines = []
        for k in order[:limit]:
            n, layers, t, caps = self.rep[k]
            st = self.proof[k]
            head = f'{names[k]}: n={n}, prefix {[list(L) for L in layers]}, {t} more layers' + (f', caps {list(caps)}' if caps else '')
            S = lambda d: ' '.join(f'{c}:{s}inf' for c, s in sorted(d.items()))
            if st[0] == 'quick':
                lines.append(f'{head}\n    sentinels {S(st[1])}: {st[3]} reals, real comparisons reschedule into {st[2]} layers; {st[2]} + {t} < D({st[3]})')
            elif st[0] == 'sent':
                lines.append(f'{head}\n    sentinels {S(st[1])}: residual is {names.get(st[2], "?")}')
            elif st[0] == 'lemma':
                d2, a2, m2 = st[5]
                lines.append(f'{head}\n    sentinels {S(st[1])}: {st[4]} reals; real comparisons fit {st[3]} layers ({st[2]}), first {m2} with <= {a2}; {st[3]} + {t} <= {d2}: SS({st[4]},{d2},{a2},{m2})')
            else:
                kids = [names.get(c, 't=0') for c in st[1]]
                lines.append(f'{head}\n    split on the next layer: {len(kids)} cases -> {", ".join(kids[:12])}{" ..." if len(kids) > 12 else ""}')
        return '\n'.join(lines)


def first_layer(n):
    return tuple((2 * k, 2 * k + 1) for k in range(n // 2))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    n = int(args[0])
    kmax = 3
    if '--kmax' in sys.argv:
        kmax = int(sys.argv[sys.argv.index('--kmax') + 1])
    P = Prover(kmax=kmax, log=lambda m: print(time.strftime('%H:%M:%S'), m, flush=True), oracle='--oracle' in sys.argv)
    for r in range(3, n + 1):
        d = DUP[r] - 1                        # show no sorter of depth DUP[r] - 1
        t0 = time.time()
        before = dict(P.stats)
        L1 = (first_layer(r),)
        if r == n:
            P.trace = P.key(r, outputs(r, L1), d - 1, ())
        ok = P.ext(r, L1, d - 1)
        dt = time.time() - t0
        delta = {k: P.stats[k] - before[k] for k in P.stats}
        if not ok:
            DLOW[r] = DUP[r]
            root = P.key(r, outputs(r, L1), d - 1, ())
            nodes, kinds = P.proof_dag(root)
            print(f'n={r:2d} depth {d}: NO sorter ({dt:.1f}s); proof DAG {len(nodes)} nodes {kinds}; search {delta}', flush=True)
            if '--show' in sys.argv and r == n:
                print(P.describe(root))
        else:
            print(f'n={r:2d} depth {d}: SORTER EXISTS?! ({dt:.1f}s)', flush=True)


if __name__ == '__main__':
    main()
