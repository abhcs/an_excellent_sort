#!/usr/bin/env python3
"""sprove.py -- the sentinel prover with a persistent fact store: no fact is derived twice.

A node is a question EXT(n, P, t, caps): can prefix P be completed by t layers (the next ones
capped by caps) into a sorting network?  Every decided node becomes a FACT, appended to
FACTS_DIR/facts-<run>.jsonl as soon as it is decided:
  NO  facts carry the step proving them, which refers to other facts by id;
  YES facts are hints (a completion exists); they only let the search skip a branch and are
      never used in a proof.
Facts live in classes: output sets equal up to relabelling channels and complementing.  A query
is answered from the store when an equivalent class holds
  a NO  fact with t' >= t and caps' >= caps   (no completion even with more room), or
  a YES fact with t' <= t and caps' <= caps   (a completion within less room; pad with empty
        layers at the end).
Every run loads all facts first, so work is shared within a run and across runs.

Steps of NO facts (all checked from definitions by check_facts.py):
  quick   sentinels S leave r reals whose real comparisons reschedule into h layers, h + t < D(r)
  lemma   ... into h layers whose first m (continued by the capped suffix) have <= a
          comparators and h + t <= d, where SS(r, d, a, m) is a proved statement
  sent    sentinels S leave a residual equivalent to a NO fact (r channels, >= t, caps >=)
  absorb  cover facts (S, a): the sentinels S sit on positions pos(S) after P, and the residual
          of P under S with the next cap lowered by a has no completion.  A next layer with at
          least a comparators touching pos(S) loses them to the sentinels, so it is covered by
          that ONE fact; only the next layers covered by no cover fact are enumerated
  split   absorb with no tracks: every next layer (and the empty one) leads to a NO fact
          (absorb and split steps may also list sentinel sets, 'qcovers': a next layer closed
          by one of them through a quick or lemma step needs no fact of its own; and
          automorphisms of the output set, 'aut': a next layer that one of them maps to a smaller
          layer is left out, since its child is a relabeling of that layer's child, README §8.11)
  sub     the outputs of a NO fact F (proved by absorb/split) embed in ours after relabelling,
          possibly complemented, and F has as many remaining layers and caps at least as
          loose: we have no completion either (Bundala-Zavodny)

usage: sprove.py FACTS_DIR STATEMENT...    (STATEMENT = D:n | SS:n,d,a,m)
"""
import collections, hashlib, itertools, json, os, sys, time
import sentinel_prover as sp


def inv_hash(X, n):
    return hashlib.sha1(repr(sp.invariant(X, n)).encode()).hexdigest()[:20]


def caps_le(n, t, small, big):
    """Every layer i < t allowed by `small` is allowed by `big` (missing caps = n // 2)."""
    for i in range(t):
        s = small[i] if i < len(small) else n // 2
        b = big[i] if i < len(big) else n // 2
        if s > b:
            return False
    return True


def track_pos(layers, c, sg):
    pos = c
    for L in layers:
        for i, j in L:
            if pos == i or pos == j:
                pos = j if sg == '+' else i
                break
    return pos


def occupancy(n, layers, S):
    """Channels holding the sentinels S (input channel -> '+'/'-') after the layers."""
    content = ['r'] * n
    for c, v in S.items():
        content[c] = v
    for L in layers:
        for i, j in L:
            a, b = content[i], content[j]
            if (a == '+' and b != '+') or (b == '-' and a != '-'):
                content[i], content[j] = b, a
    return frozenset(c for c in range(n) if content[c] != 'r')


def profiles(X, n):
    """Weight counts and, per channel, counts of ones and zeros by weight."""
    wc = [0] * (n + 1)
    ones = [[0] * (n + 1) for _ in range(n)]
    zeros = [[0] * (n + 1) for _ in range(n)]
    for x in X:
        w = x.bit_count()
        wc[w] += 1
        for i in range(n):
            if (x >> i) & 1:
                ones[i][w] += 1
            else:
                zeros[i][w] += 1
    return wc, ones, zeros


def embeds_py(A, B, n, pa=None, pb=None, budget=20000):
    """A permutation sigma with sigma(A) inside B (A, B sets of n-bit ints), or None.  Backtracking
    over channels; partial keys (weight, then assigned bits) must embed as multisets."""
    from collections import Counter
    if len(A) > len(B):
        return None
    wa, oa, za = pa or profiles(A, n)
    wb, ob, zb = pb or profiles(B, n)
    if any(wa[k] > wb[k] for k in range(n + 1)):
        return None
    cand = [[j for j in range(n) if all(oa[i][k] <= ob[j][k] and za[i][k] <= zb[j][k] for k in range(n + 1))]
            for i in range(n)]
    if any(not c for c in cand):
        return None
    order = sorted(range(n), key=lambda i: len(cand[i]))
    Al, Bl = list(A), list(B)
    used, sigma, nodes = [False] * n, [-1] * n, [0]

    def fits(kA, kB):
        cB = Counter(kB)
        for k, c in Counter(kA).items():
            if cB.get(k, 0) < c:
                return False
        return True

    def rec(t, kA, kB):
        if t == n:
            return True
        nodes[0] += 1
        if nodes[0] > budget:
            raise TimeoutError
        i = order[t]
        for j in cand[i]:
            if used[j]:
                continue
            nA = [ka * 2 + ((a >> i) & 1) for ka, a in zip(kA, Al)]
            nB = [kb * 2 + ((b >> j) & 1) for kb, b in zip(kB, Bl)]
            if not fits(nA, nB):
                continue
            used[j], sigma[i] = True, j
            if rec(t + 1, nA, nB):
                return True
            used[j], sigma[i] = False, -1
        return False
    try:
        if rec(0, [a.bit_count() for a in Al], [b.bit_count() for b in Bl]):
            return list(sigma)
    except TimeoutError:
        pass
    return None


def sentinel_state(n, layers, S):
    """The prefix with the sentinels S: content of each channel afterwards ('+', '-' or 'r'), the
    level of the real line on each channel (as-soon-as-possible height of the real comparisons that
    touched it), the as-soon-as-possible layer sizes, and the height h.  Computed once per S; a next
    layer is then judged from it in a few lookups."""
    content = ['r'] * n
    for c, v in S.items():
        content[c] = v
    line_at = list(range(n))
    lvl = [0] * n
    asap = []
    h = 0
    for L in layers:
        for i, j in L:
            a, b = content[i], content[j]
            if a == 'r' and b == 'r':
                la, lb = line_at[i], line_at[j]
                v = (lvl[la] if lvl[la] > lvl[lb] else lvl[lb]) + 1
                lvl[la] = lvl[lb] = v
                if v > h:
                    h = v
                    asap.append(0)
                asap[v - 1] += 1
            elif (a == '+' and b != '+') or (b == '-' and a != '-'):
                content[i], content[j] = b, a
                line_at[i], line_at[j] = line_at[j], line_at[i]
    chlvl = [lvl[line_at[c]] if content[c] == 'r' else -1 for c in range(n)]
    return content, chlvl, asap, h


def asis_sizes(n, layers, S):
    """Real comparisons in each prefix layer under the sentinels S: the residual kept in its own
    layers (empty ones included), a schedule of height len(layers) for the lemma rule.  A good
    sentinel track of the descent (README §4) leaves exactly this residual."""
    content = ['r'] * n
    for c, v in S.items():
        content[c] = v
    out = []
    for L in layers:
        k = 0
        for i, j in L:
            a, b = content[i], content[j]
            if a == 'r' and b == 'r':
                k += 1
            elif (a == '+' and b != '+') or (b == '-' and a != '-'):
                content[i], content[j] = b, a
        out.append(k)
    return out


def statement_root(st):
    """(n, prefix, t, caps) of the node whose NO proves the statement."""
    kind, args = st.split(':')
    if kind == 'D':
        n = int(args)
        return n, (sp.first_layer(n),), sp.DUP[n] - 2, ()
    n, d, a, m = map(int, args.split(','))
    return n, (tuple((2 * k, 2 * k + 1) for k in range(a)),), d - 1, sp.norm_caps(n, d - 1, (a,) * (m - 1))


class Store:
    def __init__(self, path, compact=False, x_cap=0):
        """compact: facts read from files keep only what lookups need (no proof step; the prefix,
        packed into bytes, only for a class representative and for split/absorb facts), and other
        runs' new facts can be read during the run with refresh(). x_cap > 0: keep the output sets
        of at most x_cap classes in memory (least recently used; recomputed from the prefix)."""
        self.path = path
        os.makedirs(path, exist_ok=True)
        self.run = time.strftime('%Y%m%d-%H%M%S') + f'-{os.getpid()}'
        self.own = f'facts-{self.run}.jsonl'
        self.compact, self.x_cap = compact, x_cap
        self.xlru = collections.OrderedDict()
        self.facts, self.classes, self.by_inv = {}, {}, {}
        self.big = {}                       # n -> ids of NO facts proved by absorb/split (worth reusing)
        self.osets = {}
        self.statements = {}
        self.serial = 0
        self.loaded = 0
        self.offsets = {}
        # for the wide subsumption search: classes with a NO fact, by (n, t), newest last, and the
        # weight counts of a class's output set (stored with new facts as 'wc', else computed)
        self.no_by_nt, self.no_seen, self.csig = {}, set(), {}
        for fn in sorted(os.listdir(path)):
            if fn.startswith('facts-') and fn.endswith('.jsonl'):
                self.loaded += self._load_file(fn)
        import gc
        gc.collect()
        gc.freeze()                         # the loaded store is long-lived: keep it out of GC scans
        gc.set_threshold(200000, 50, 100)
        sp_path = os.path.join(path, 'statements.jsonl')
        if os.path.exists(sp_path):
            for line in open(sp_path):
                if line.strip():
                    s = json.loads(line)
                    self.statements[s['statement']] = s['fact']
        self.out = open(os.path.join(path, self.own), 'a')
        self.certs = {}                     # SAT certificates by node key (satcert.py)
        self._cert_pos = 0
        self.refresh_certs()

    def refresh_certs(self):
        """Index the SAT certificate records appended since the last call."""
        fn = os.path.join(self.path, 'sat_certs.jsonl')
        if not os.path.exists(fn):
            return 0
        with open(fn, 'rb') as f:
            f.seek(self._cert_pos)
            data = f.read()
        end = data.rfind(b'\n')
        if end < 0:
            return 0
        k = 0
        for line in data[:end].split(b'\n'):
            if line.strip():
                r = json.loads(line)
                self.certs[r['key']] = r
                k += 1
        self._cert_pos += end + 1
        return k

    def add_cert(self, rec):
        import satcert
        satcert.append_record(self.path, rec)
        self.certs[rec['key']] = rec

    def _load_file(self, fn):
        """Index the complete lines of a facts file past the last offset read (a line that another
        run is still writing is left for later)."""
        full = os.path.join(self.path, fn)
        pos = self.offsets.get(fn, 0)
        try:
            size = os.path.getsize(full)
        except OSError:
            return 0
        if size <= pos:
            return 0
        with open(full, 'rb') as f:
            f.seek(pos)
            data = f.read(size - pos)
        end = data.rfind(b'\n')
        if end < 0:
            return 0
        k = 0
        for line in data[:end].split(b'\n'):
            if line.strip():
                d = json.loads(line)
                if d['id'] not in self.facts:
                    self._index(d, loaded=True)
                    k += 1
        self.offsets[fn] = pos + end + 1
        return k

    def refresh(self):
        """Index the facts that other runs appended to the store since the last call."""
        self.refresh_certs()
        k = 0
        for fn in sorted(os.listdir(self.path)):
            if fn.startswith('facts-') and fn.endswith('.jsonl') and fn != self.own:
                k += self._load_file(fn)
        return k

    @staticmethod
    def _pack(prefix):
        return bytes(v for L in prefix for v in [x for c in L for x in c] + [255])

    @staticmethod
    def _layers(prefix):
        if isinstance(prefix, bytes):
            out, cur = [], []
            for i in range(0, len(prefix)):
                v = prefix[i]
                if v == 255:
                    out.append(tuple(tuple(cur[k:k + 2]) for k in range(0, len(cur), 2)))
                    cur = []
                else:
                    cur.append(v)
            return tuple(out)
        return tuple(tuple(tuple(p) for p in L) for L in prefix)

    def _index(self, f, loaded=False):
        rule = f.get('step', {}).get('rule')
        inv = f['inv']
        prefix = f['prefix']
        big = f['res'] == 'NO' and rule in ('absorb', 'split')
        wc = f.get('wc')
        if loaded and self.compact:
            g = {'id': f['id'], 'cls': f['cls'], 'n': f['n'], 't': f['t'], 'caps': f['caps'], 'res': f['res']}
            if f['res'] == 'NO':
                g['pfx'] = self._pack(prefix)
            f = g
        self.facts[f['id']] = f
        if big:
            self.big.setdefault(f['n'], []).append(f['id'])
        c = self.classes.get(f['cls'])
        if c is None:
            c = {'n': f['n'], 'prefix': self._pack(prefix) if (loaded and self.compact) else prefix,
                 'X': None, 'facts': []}
            self.classes[f['cls']] = c
            self.by_inv.setdefault((f['n'], inv), []).append(f['cls'])
        c['facts'].append(f['id'])
        if wc and f['cls'] not in self.csig:
            self.csig[f['cls']] = tuple(wc)
        if f['res'] == 'NO' and (f['n'], f['t'], f['cls']) not in self.no_seen:
            self.no_seen.add((f['n'], f['t'], f['cls']))
            self.no_by_nt.setdefault((f['n'], f['t']), []).append(f['cls'])

    def _touch(self, cls):
        if self.x_cap:
            self.xlru[cls] = None
            self.xlru.move_to_end(cls)
            while len(self.xlru) > self.x_cap:
                old, _ = self.xlru.popitem(last=False)
                self.classes[old]['X'] = None

    def class_X(self, cls):
        c = self.classes[cls]
        X = c['X']
        if X is None:
            X = sp.outputs(c['n'], self._layers(c['prefix']))
            c['X'] = X
        self._touch(cls)
        return X

    def find_class(self, n, X, ih):
        for cls in self.by_inv.get((n, ih), ()):
            if sp.equivalent(self.class_X(cls), X, n):
                return cls
        return None

    def new_class(self, n, X, ih, layers):
        self.serial += 1
        cls = f'{self.run}-c{self.serial}'
        self.classes[cls] = {'n': n, 'prefix': [[list(p) for p in L] for L in layers], 'X': X, 'facts': []}
        self.by_inv.setdefault((n, ih), []).append(cls)
        self._touch(cls)
        return cls

    def oset(self, fid):
        """(X, profiles(X), complement of X, its profiles) of a stored fact, cached."""
        if fid not in self.osets:
            f = self.facts[fid]
            n = f['n']
            X = sp.outputs(n, self._layers(f['pfx'] if 'pfx' in f else f['prefix']))
            if self.x_cap and len(self.osets) > self.x_cap:
                self.osets.clear()
            mask = (1 << n) - 1
            Xc = frozenset(x ^ mask for x in X)
            self.osets[fid] = (X, profiles(X, n), Xc, profiles(Xc, n))
        return self.osets[fid]

    def class_sig(self, cls):
        """Weight counts of a class's output set (invariant under relabeling; reversed under
        complement)."""
        wc = self.csig.get(cls)
        if wc is None:
            c = self.classes[cls]
            w = [0] * (c['n'] + 1)
            for x in self.class_X(cls):
                w[x.bit_count()] += 1
            wc = self.csig[cls] = tuple(w)
        return wc

    def subsumer_wide(self, n, t, caps, X, limit=200, sig_budget=300, scan_cap=60000):
        """As subsumer, over every stored NO fact (any rule) with t_F >= t and caps no tighter,
        newest first within each t. Weight counts filter the candidates before any embedding is
        tried. Returns (fid, sigma, comp) or None."""
        pq = profiles(X, n)
        wq = pq[0]
        size = len(X)
        tried = new_sigs = scanned = 0
        tmax = max((tt for (nn, tt) in self.no_by_nt if nn == n), default=t - 1)
        for tt in range(t, tmax + 1):
            bucket = self.no_by_nt.get((n, tt), ())
            for i in range(len(bucket) - 1, -1, -1):
                cls = bucket[i]
                scanned += 1
                if scanned > scan_cap:
                    return None
                wc = self.csig.get(cls)
                if wc is None:
                    if new_sigs >= sig_budget:
                        continue
                    new_sigs += 1
                    wc = self.class_sig(cls)
                if sum(wc) > size or not (all(wc[k] <= wq[k] for k in range(n + 1))
                                          or all(wc[n - k] <= wq[k] for k in range(n + 1))):
                    continue
                fid = next((f for f in self.classes[cls]['facts']
                            if self.facts[f]['res'] == 'NO' and self.facts[f]['t'] >= t
                            and ('pfx' in self.facts[f] or 'prefix' in self.facts[f])
                            and caps_le(n, t, caps, tuple(self.facts[f]['caps']))), None)
                if fid is None:
                    continue
                A, pa, Ac, pac = self.oset(fid)
                for comp, P, pp in ((False, A, pa), (True, Ac, pac)):
                    if len(P) > size or any(pp[0][k] > wq[k] for k in range(n + 1)):
                        continue
                    tried += 1
                    sig = embeds_py(P, X, n, pp, pq)
                    if sig is not None:
                        return fid, sig, comp
                if tried >= limit:
                    return None
        return None

    def subsumer(self, n, t, caps, X, limit=60):
        """A NO fact F (absorb/split) with sigma(out F) or sigma(complement of out F) inside X:
        X then has no completion either (Bundala-Zavodny).  Returns (fid, sigma, comp) or None."""
        cands = [fid for fid in self.big.get(n, ())
                 if self.facts[fid]['t'] >= t and caps_le(n, t, caps, tuple(self.facts[fid]['caps']))]
        if not cands:
            return None
        pq = None
        tried = 0
        for fid in cands:
            A, pa, Ac, pac = self.oset(fid)
            if len(A) > len(X):
                continue
            if pq is None:
                pq = profiles(X, n)
            for comp, P, pp in ((False, A, pa), (True, Ac, pac)):
                if any(pp[0][k] > pq[0][k] for k in range(n + 1)):
                    continue
                tried += 1
                sig = embeds_py(P, X, n, pp, pq)
                if sig is not None:
                    return fid, sig, comp
            if tried >= limit:
                break
        return None

    def lookup(self, cls, n, t, caps):
        for fid in self.classes[cls]['facts']:
            f = self.facts[fid]
            fc = tuple(f['caps'])
            if f['res'] == 'NO' and f['t'] >= t and caps_le(n, t, caps, fc):
                return 'NO', fid
            if f['res'] == 'YES' and f['t'] <= t and caps_le(n, f['t'], fc, caps):
                return 'YES', fid
        return None

    def add(self, cls, n, ih, layers, t, caps, res, step=None, X=None):
        self.serial += 1
        fid = f'{self.run}-{self.serial}'
        f = {'id': fid, 'cls': cls, 'inv': ih, 'n': n, 't': t, 'caps': list(caps),
             'prefix': [[list(p) for p in L] for L in layers], 'res': res}
        if step is not None:
            f['step'] = step
        if X is not None:                  # weight counts of the output set: a cheap subsumption filter
            wc = [0] * (n + 1)
            for x in X:
                wc[x.bit_count()] += 1
            f['wc'] = wc
        self.out.write(json.dumps(f) + '\n')
        self.out.flush()
        self._index(f)
        return fid

    def record_statement(self, st, fid):
        self.statements[st] = fid
        with open(os.path.join(self.path, 'statements.jsonl'), 'a') as f:
            f.write(json.dumps({'statement': st, 'fact': fid}) + '\n')


class SatUndecided(BaseException):
    """A node the prover was told to certify by SAT stayed undecided (time limit or failed proof
    check).  Raised, not returned: the caller decides whether to retry with more time."""

    def __init__(self, key, rec):
        super().__init__(key)
        self.key, self.rec = key, rec


class Prover:
    def __init__(self, store, kmax=4, max_rec=40, absorb=True, subsume=True, log=None,
                 cover_k=3, cover_rank=6, cover_budget=12, multi_min=40, qcover=True, oracle=False,
                 guide=False, guide_max=200, guide_seconds=10.0, share_seconds=0, reverse=False,
                 wide_sub=False, fast_n=10, symmetry=True, aut_max=500, qcover_max_n=99, oracle_max_n=99,
                 guide_big_n=99, guide_big_seconds=2.0, absorb_max_n=99, store_first_n=99,
                 store_first_big=300, guide_skip_n=99, guide_conflicts=50000, sat_certs=False,
                 sat_run_n=99, sat_seconds=None):
        self.S = store
        # fast_n: splits of nodes with at least this many channels use the compiled core (fastcore.c);
        # symmetry: such splits only expand next layers that no automorphism of the node's output set
        # maps to a smaller layer, and record those automorphisms (check_facts.py verifies them)
        self.fast_n, self.symmetry, self.aut_max = fast_n, symmetry, aut_max
        # cost limits for big nodes: no listed sentinel covers above qcover_max_n channels, no
        # extension oracle above oracle_max_n, and guide SAT calls on residuals with at least
        # guide_big_n channels get guide_big_seconds
        self.qcover_max_n, self.oracle_max_n = qcover_max_n, oracle_max_n
        self.guide_big_n, self.guide_big_seconds = guide_big_n, guide_big_seconds
        self.absorb_max_n = absorb_max_n        # no cover facts (absorb) above this many channels
        # nodes with at least store_first_n channels look up the residuals of their first store_first_big
        # sentinel candidates in the store (others: the first 300) before any SAT guidance; residuals
        # with at least guide_skip_n channels get no SAT verdict (undecided), and each guide SAT call
        # solves in rounds of guide_conflicts conflicts (its time limit is checked between rounds)
        self.store_first_n, self.store_first_big = store_first_n, store_first_big
        self.guide_skip_n, self.guide_conflicts = guide_skip_n, guide_conflicts
        # SAT certificates (satcert.py, README §8.15): sat_certs uses recorded drat-trim-verified
        # refutations of the exact node; nodes with at least sat_run_n channels that no quick, lemma
        # or stored-residual step closes are certified on the spot (CaDiCaL time limit sat_seconds)
        self.sat_certs, self.sat_run_n, self.sat_seconds = sat_certs, sat_run_n, sat_seconds
        # wide_sub: the subsumption step looks at every stored NO fact, not only split facts
        self.wide_sub = wide_sub
        # reverse: work through the children of a split from the largest down (a helper on the
        # same case as another run meets it in the middle instead of repeating it)
        self.reverse = reverse
        # share_seconds > 0: every so often index the facts other runs appended to the store
        self.share_seconds, self._last_share = share_seconds, time.time()
        # guide: ask SAT which sentinel residuals have no completion and recurse into one of those
        # first (guidance only: the residual is still proved by the rules, and checked later)
        self.guide, self.guide_max, self.guide_seconds = guide, guide_max, guide_seconds
        self.gcache = {}
        self.qcover = qcover
        self.scover_k = 2
        self.cover_k, self.cover_rank, self.cover_budget = cover_k, cover_rank, cover_budget
        self.multi_min = multi_min
        self.kmax, self.max_rec, self.absorb, self.subsume = kmax, max_rec, absorb, subsume
        self.log = log
        self.trace = None
        self.stats = dict(nodes=0, hits=0, quick=0, lemma=0, sent=0, reuse=0, sub=0, absorb=0, split=0, yes=0, oracle=0,
                          guide=0, shared=0, sym=0, sat=0)
        self.oracle, self.oracle_min_n, self.oracle_seconds = oracle, 9, 3.0
        self.dlow = {1: 0, 2: 1}
        self.lemmas = {}
        for st, fid in store.statements.items():
            self._register(st, fid)

    def _register(self, st, fid):
        kind, args = st.split(':')
        if kind == 'D':
            n = int(args)
            self.dlow[n] = max(self.dlow.get(n, 0), sp.DUP[n])
        else:
            n, d, a, m = map(int, args.split(','))
            self.lemmas.setdefault(n, []).append((d, a, m, fid))

    def prove(self, st):
        n, L1, t, caps = statement_root(st)
        if st in self.S.statements:
            return 'NO', self.S.statements[st]
        self.trace = (n, L1)
        res, fid = self.ext(n, L1, t, None, caps)
        if res == 'NO':
            self.S.record_statement(st, fid)
            self._register(st, fid)
        return res, fid

    # ------------------------------------------------------------------
    def ext(self, n, layers, t, X=None, caps=()):
        if self.share_seconds and time.time() - self._last_share > self.share_seconds:
            self.stats['shared'] += self.S.refresh()
            self._last_share = time.time()
        if X is None:
            X = sp.outputs(n, layers)
        caps = sp.norm_caps(n, t, caps)
        if all(sp.is_sorted(x, n) for x in X):
            return 'YES', None
        if t == 0:
            return 'NO', None
        if not caps and t >= sp.DUP.get(n, 99):
            return 'YES', None
        ih = inv_hash(X, n)
        cls = self.S.find_class(n, X, ih)
        if cls is None:
            cls = self.S.new_class(n, X, ih, layers)
        else:
            hit = self.S.lookup(cls, n, t, caps)
            if hit:
                self.stats['hits'] += 1
                return hit
        self.stats['nodes'] += 1
        if self.log and self.stats['nodes'] % 1000 == 0:
            self.log(f'  progress {self.stats} facts={len(self.S.facts)}')
        if self.oracle and self.oracle_min_n <= n <= self.oracle_max_n and t >= 2:
            w = sp.sat_oracle(n, layers, t, caps, seconds=self.oracle_seconds)
            if isinstance(w, list):                # a completion exists: a YES hint, never a proof
                self.stats['oracle'] += 1
                fid = self.S.add(cls, n, ih, layers, t, caps, 'YES', X=X)
                return 'YES', fid
        res, step = self._ext(n, layers, t, X, caps)
        fid = self.S.add(cls, n, ih, layers, t, caps, res, step, X=X)
        return res, fid

    def _verdict(self, n, t, caps, c, resid):
        """'YES' / 'NO' / 'UNKNOWN' for the residual of candidate c: the store first (facts of
        every run sharing it), then the cache, then SAT. A SAT completion is recorded as a YES
        fact so that other runs skip it too (YES facts are hints, never part of a proof)."""
        h, k, S, i = c
        r = n - k
        capsr = sp.norm_caps(r, t, caps)
        R = resid(i)
        XR = sp.outputs(r, R)
        key = (r, t, capsr, len(XR), hash(XR))   # guidance only: a collision costs time, not soundness
        v = self.gcache.get(key)
        if v is not None:
            return v
        ih = inv_hash(XR, r)
        cls = self.S.find_class(r, XR, ih)
        hit = self.S.lookup(cls, r, t, capsr) if cls is not None else None
        if hit:
            v = hit[0]
        else:
            self.stats['guide'] += 1
            secs = self.guide_seconds if r < self.guide_big_n else min(self.guide_seconds, self.guide_big_seconds)
            if r >= self.guide_skip_n:
                w = 'UNKNOWN'
            else:
                w = sp.sat_oracle(r, R, t, capsr, seconds=secs, conflicts=self.guide_conflicts)
            v = 'YES' if isinstance(w, list) else ('NO' if w is None else 'UNKNOWN')
            if v == 'YES':
                if cls is None:
                    cls = self.S.new_class(r, XR, ih, R)
                self.S.add(cls, r, ih, R, t, capsr, 'YES')
        if len(self.gcache) > 400000:
            self.gcache.clear()
        self.gcache[key] = v
        return v

    def _guided(self, n, t, caps, cands, resid):
        """The candidates to recurse into. A residual of several sentinels has a completion if the
        residual of any one of them has one (remove the others from a completed network), so only
        candidates whose single sentinels all lack a completion can lack one. The single-sentinel
        candidates are decided first (store, cache, SAT); if every one completes, nothing is worth
        a recursion. Otherwise the candidates built from the failing singles are tried in the
        prover's order (lowest height, then most sentinels) up to the first without completion;
        undecided ones (SAT timeouts) follow. Guidance only: every step is still proved."""
        singles = [c for c in cands if c[1] == 1]
        if not singles:                        # no single candidates generated: check in order
            out = []
            for c in cands[:self.guide_max]:
                v = self._verdict(n, t, caps, c, resid)
                if v == 'NO':
                    return [c] + out
                if v == 'UNKNOWN':
                    out.append(c)
            return out
        bad, maybe = set(), set()
        for c in singles:
            v = self._verdict(n, t, caps, c, resid)
            (s,) = c[2].items()
            if v == 'NO':
                bad.add(s)
            elif v == 'UNKNOWN':
                maybe.add(s)
        if not bad and not maybe:
            return []
        no, unknown, checks = [], [], 0
        for c in cands:
            items = set(c[2].items())
            if not items <= (bad | maybe):
                continue
            if c[1] == 1:
                v = 'NO' if items <= bad else 'UNKNOWN'
            elif checks >= self.guide_max:
                unknown.append(c)
                continue
            else:
                checks += 1
                v = self._verdict(n, t, caps, c, resid)
            if v == 'NO':
                no.append(c)
                break
            if v == 'UNKNOWN':
                unknown.append(c)
        return no + unknown

    def _ext(self, n, layers, t, X, caps):
        # no sentinels at all: the node itself may already be too shallow for D(n), or violate
        # a proved sparse-start statement on n channels
        z = self._leaf_by({}, n, layers, t, caps)
        if z:
            self.stats[z['rule']] += 1
            return 'NO', z
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
            capsr = sp.norm_caps(r, t, caps)
            rec_ok = bool(capsr) or t < sp.DUP.get(r, 99)
            hmax = self.dlow[r] - t - 1 if r in self.dlow else -1
            quick_ok = hmax >= 0 and total - k * Lp <= hmax * (r // 2)
            lems = [lm for lm in self.lemmas.get(r, ()) if lm[0] - t >= 1]
            full = quick_ok or bool(lems)
            if not (rec_ok or full):
                continue
            combos = ((tuple(zip(ch, sg)) for ch in itertools.combinations(range(n), k)
                       for sg in itertools.product('+-', repeat=k)) if full
                      else itertools.combinations(pool, k))
            for combo in combos:
                if len({c for c, _ in combo}) < k:
                    continue
                S = dict(combo)
                # cheap state first (height and as-soon-as-possible sizes); full residual later
                content, chlvl, asap, h = sentinel_state(n, layers, S)
                Sj = {str(c): v for c, v in S.items()}
                if quick_ok and h <= hmax:
                    self.stats['quick'] += 1
                    return 'NO', {'rule': 'quick', 'S': Sj, 'h': h, 'r': r}
                alap = asis = None
                for d2, a2, m2, lfid in lems:
                    if h + t > d2:
                        continue
                    if Lp + t <= d2:                  # the residual in its own layers (descent)
                        if asis is None:
                            asis = asis_sizes(n, layers, S)
                        sizes = [asis[i] if i < Lp else (capsr[i - Lp] if i - Lp < len(capsr) else r // 2)
                                 for i in range(m2)]
                        if all(x <= a2 for x in sizes):
                            self.stats['lemma'] += 1
                            return 'NO', {'rule': 'lemma', 'S': Sj, 'sched': 'asis', 'h': Lp, 'r': r,
                                          'ss': [d2, a2, m2], 'lemma': lfid}
                    for name in ('asap', 'alap'):
                        if name == 'alap' and alap is None:
                            alap = sp.residual2(n, layers, S)[4]     # only when a lemma could apply
                        prof = asap if name == 'asap' else alap
                        sizes = [prof[i] if i < h else (capsr[i - h] if i - h < len(capsr) else r // 2)
                                 for i in range(m2)]
                        if all(x <= a2 for x in sizes):
                            self.stats['lemma'] += 1
                            return 'NO', {'rule': 'lemma', 'S': Sj, 'sched': name, 'h': h, 'r': r,
                                          'ss': [d2, a2, m2], 'lemma': lfid}
                if rec_ok:
                    cands.append((h, k, S, None))
        cands.sort(key=lambda c: (c[0], -c[1]))
        rcache = {}

        def resid(i):                          # full residual, computed when a candidate is reached
            if i not in rcache:
                rcache[i] = sp.residual2(n, layers, cands[i][2])[1]
            return rcache[i]
        cands = [(h, k, S, i) for i, (h, k, S, _) in enumerate(cands)]
        # store first: a residual that is already a NO fact costs nothing new
        for h, k, S, i in cands[:self.store_first_big if n >= self.store_first_n else 300]:
            R = resid(i)
            r = n - k
            XR = sp.outputs(r, R)
            ih = inv_hash(XR, r)
            cls = self.S.find_class(r, XR, ih)
            if cls is not None:
                hit = self.S.lookup(cls, r, t, sp.norm_caps(r, t, caps))
                if hit and hit[0] == 'NO':
                    self.stats['sent'] += 1
                    self.stats['reuse'] += 1
                    return 'NO', {'rule': 'sent', 'S': {str(c): v for c, v in S.items()}, 'child': hit[1]}
        if self.sat_certs or n >= self.sat_run_n:
            import satcert
            key = satcert.node_key(n, layers, t, caps)
            rec = self.S.certs.get(key)
            more = rec is not None and rec['result'] == 'UNKNOWN' and (
                self.sat_seconds is None or (rec.get('limit') or 0) < self.sat_seconds)
            if (rec is None or more) and n >= self.sat_run_n and t >= 2:
                rec = satcert.certify(n, layers, t, caps, seconds=self.sat_seconds)
                self.S.add_cert(rec)
            if rec is not None:
                if rec['result'] == 'UNSAT' and rec.get('drat') == 'VERIFIED':
                    self.stats['sat'] += 1
                    return 'NO', {'rule': 'sat', 'enc': rec['enc'], 'cnf_sha256': rec['cnf_sha256']}
                if rec['result'] == 'SAT' and rec.get('network_sorts'):
                    return 'YES', None
                if n >= self.sat_run_n:
                    raise SatUndecided(key, rec)
        seen, tried = set(), 0
        order = self._guided(n, t, caps, cands, resid) if self.guide else cands
        for h, k, S, i in order:
            if tried >= self.max_rec:
                break
            R = resid(i)
            r = n - k
            XR = sp.outputs(r, R)
            sig = (r, inv_hash(XR, r), XR)
            if sig[:2] in seen:
                continue
            seen.add(sig[:2])
            tried += 1
            res, fid = self.ext(r, R, t, XR, sp.norm_caps(r, t, caps))
            if res == 'NO':
                self.stats['sent'] += 1
                return 'NO', {'rule': 'sent', 'S': {str(c): v for c, v in S.items()}, 'child': fid}
        # subsumption: an already proved case whose outputs embed in ours
        if self.subsume:
            sub = self.S.subsumer_wide(n, t, caps, X) if self.wide_sub else self.S.subsumer(n, t, caps, X)
            if sub is not None:
                self.stats['sub'] += 1
                return 'NO', {'rule': 'sub', 'of': sub[0], 'sigma': sub[1], 'comp': sub[2]}
        # absorb / split
        cap0 = caps[0] if caps else n // 2
        rest = tuple(caps[1:])
        fast = sp._fc is not None and n >= self.fast_n
        auts = []
        if fast:
            nonred = sp._fc.nonredundant(n, X)
            if self.symmetry:
                ident = tuple(range(n))
                auts = [g for g in sp._fc.automorphisms(X, n, maxg=self.aut_max)[0] if g != (ident, False)]
            allL = sp._fc.canonical_layers(n, nonred, cap0, auts)
            if auts:
                self.stats['sym'] += 1
        else:
            nonred = [(i, j) for i in range(n) for j in range(i + 1, n)
                      if any((x >> i) & 1 and not (x >> j) & 1 for x in X)]
            allL = []

            def gen(start, used, cur):
                if cur:
                    allL.append(tuple(cur))
                if len(cur) == cap0:
                    return
                for idx in range(start, len(nonred)):
                    i, j = nonred[idx]
                    if used >> i & 1 or used >> j & 1:
                        continue
                    cur.append((i, j))
                    gen(idx + 1, used | (1 << i) | (1 << j), cur)
                    cur.pop()
            gen(0, 0, [])
        covers = []
        uncovered = allL
        if self.absorb and allL and n <= self.absorb_max_n:
            uncovered = self._choose_covers(n, layers, t, caps, cap0, rest, allL, covers)
        qcovers = []
        if self.qcover and t - 1 >= 1 and uncovered and n <= self.qcover_max_n:
            qcovers, uncovered = self._qcover(n, layers, t, caps, uncovered)
        children = {}
        mult = {}
        if fast:
            # child keys from the C core: equal hashes = the same child; equivalent children have the
            # same size and invariant, and the C search decides equivalence within such a group
            groups = {}
            for L, k in zip(uncovered, sp._fc.child_keys(n, X, uncovered) if uncovered else []):
                groups.setdefault((k[0], k[3]), []).append((L, (k[1], k[2])))
            for gk, lst in groups.items():
                reps = []                        # [layer, hashes, child or None]
                for L, hk in lst:
                    hit = next((r for r in reps if r[1] == hk), None)
                    if hit is None:
                        Y = sp._fc.apply_layer(n, X, L)
                        for r in reps:
                            if r[2] is None:
                                r[2] = sp._fc.apply_layer(n, X, r[0])
                            if sp._fc.equivalent(r[2], Y, n) is not None:
                                hit = r
                                break
                        if hit is None:
                            reps.append([L, hk, Y])
                            mult[L] = 1
                            continue
                    mult[hit[0]] += 1
                children[gk] = [(r[0], r[2] if r[2] is not None else sp._fc.apply_layer(n, X, r[0])) for r in reps]
        else:
            for L in uncovered:
                Y = frozenset(sp.apply_layer(L, x) for x in X)
                k2 = (inv_hash(Y, n), len(Y))
                bucket = children.setdefault(k2, [])
                for L0, Y2 in bucket:
                    if sp.equivalent(Y2, Y, n):
                        mult[L0] += 1
                        break
                else:
                    bucket.append((L, Y))
                    mult[L] = 1
        kids = sorted((c for b in children.values() for c in b), key=lambda c: len(c[1]), reverse=self.reverse)
        trace = self.trace is not None and (n, layers) == self.trace and self.log
        if trace:
            self.log(f'TRACE {"absorb" if covers else "split"}: {len(covers)} covers, {len(kids)} cases (+ empty layer)')
        ckeys = []
        fold = {}                        # (S, target) -> child facts that are exactly that reduction
        t0 = time.time()
        for idx, (L, Y) in enumerate(kids):
            res, fid = self.ext(n, layers + (L,), t - 1, Y, rest)
            if res == 'YES':
                self.stats['yes'] += 1
                return 'YES', None
            if fid is not None:
                ckeys.append(fid)
                f = self.S.facts[fid]
                st = f.get('step', {})
                if (mult[L] == 1 and st.get('rule') == 'sent'
                        and f.get('prefix') == [[list(c) for c in Lx] for Lx in layers + (L,)]):
                    key = (json.dumps(sorted(st['S'].items())), st['child'])
                    fold.setdefault(key, []).append(fid)
            if trace:
                self.log(f'TRACE case {idx + 1}/{len(kids)} closed ({time.time() - t0:.0f}s, nodes {self.stats["nodes"]}): {list(L)}')
        res, fid = self.ext(n, layers, t - 1, X, rest)
        if res == 'YES':
            return 'YES', None
        if fid is not None:
            ckeys.append(fid)
        # cases closed by the same sentinels reducing to the same fact: one listed entry for all
        for (Sj, target), fids in fold.items():
            if len(fids) >= 2:
                drop = set(fids)
                ckeys = [c for c in ckeys if c not in drop]
                qcovers.append({'S': dict(json.loads(Sj)), 'fact': target})
        self.stats['absorb' if covers else 'split'] += 1
        step = {'rule': 'absorb' if covers else 'split', 'children': ckeys}
        if auts:                                 # next layers that one of these maps lower were skipped
            step['aut'] = [[list(p), int(c)] for p, c in auts]
        if covers:
            step['covers'] = covers
        if qcovers:
            step['qcovers'] = qcovers
        return 'NO', step

    def _leaf_by(self, S, n, layers, t, caps):
        """Does the sentinel set S (possibly empty) close EXT(n, layers, t, caps) by a quick or
        lemma step?  Returns the step, or None."""
        r = n - len(S)
        rr, R, h, asap, alap = sp.residual2(n, layers, S)
        Sj = {str(c): v for c, v in S.items()}
        if r in self.dlow and h + t < self.dlow[r]:
            return {'rule': 'quick', 'S': Sj, 'h': h, 'r': r}
        capsr = sp.norm_caps(r, t, caps)
        Lp = len(layers)
        asis = None
        for d2, a2, m2, lfid in self.lemmas.get(r, ()):
            if h + t > d2:
                continue
            for name, prof in (('asap', asap), ('alap', alap)):
                sizes = [prof[i] if i < h else (capsr[i - h] if i - h < len(capsr) else r // 2) for i in range(m2)]
                if all(x <= a2 for x in sizes):
                    return {'rule': 'lemma', 'S': Sj, 'sched': name, 'h': h, 'r': r, 'ss': [d2, a2, m2], 'lemma': lfid}
            if Lp + t <= d2:
                if asis is None:
                    asis = asis_sizes(n, layers, S)
                sizes = [asis[i] if i < Lp else (capsr[i - Lp] if i - Lp < len(capsr) else r // 2) for i in range(m2)]
                if all(x <= a2 for x in sizes):
                    return {'rule': 'lemma', 'S': Sj, 'sched': 'asis', 'h': Lp, 'r': r, 'ss': [d2, a2, m2], 'lemma': lfid}
        return None

    def _leaf_sets(self, n, layers, t, caps, limit=12):
        """Sentinel sets that close the node by quick or lemma (at most `limit`)."""
        found = []
        Lp = len(layers)
        total = sum(len(L) for L in layers)
        for k in range(1, min(self.kmax, n - 2) + 1):
            r = n - k
            hmax = self.dlow[r] - t - 1 if r in self.dlow else -1
            quick_ok = hmax >= 0 and total - k * Lp <= hmax * (r // 2)
            lems = [lm for lm in self.lemmas.get(r, ()) if lm[0] - t >= 1]
            if not (quick_ok or lems):
                continue
            for ch in itertools.combinations(range(n), k):
                for sg in itertools.product('+-', repeat=k):
                    S = dict(zip(ch, sg))
                    if self._leaf_by(S, n, layers, t, caps):
                        found.append(S)
                        if len(found) >= limit:
                            return found
        return found

    def _sent_hit(self, S, n, layers, t, caps):
        """A stored NO fact equivalent to the residual of (layers) under S, or None (no search)."""
        r = n - len(S)
        rr, R, h, _, _ = sp.residual2(n, layers, S)
        XR = sp.outputs(r, R)
        if all(sp.is_sorted(x, r) for x in XR):
            return None
        cls = self.S.find_class(r, XR, inv_hash(XR, r))
        if cls is None:
            return None
        hit = self.S.lookup(cls, r, t, sp.norm_caps(r, t, caps))
        return hit[1] if hit and hit[0] == 'NO' else None

    def _qcover(self, n, layers, t, caps, layer_list):
        """Close as many next layers as possible by sentinel sets listed once in the step.  Every
        sentinel set's state after the prefix is computed once; a next layer L is closed by a set
        through a quick step iff no comparator of L joins two real lines one of which is already at
        the top allowed level (one AND of bitmasks), or through a lemma step (a few lookups).
        Returns (qcovers, layers still open)."""
        rest = tuple(caps[1:])
        t2 = t - 1
        pidx = {}
        for i in range(n):
            for j in range(i + 1, n):
                pidx[(i, j)] = len(pidx)
        lmask = {L: sum(1 << pidx[p] for p in L) for L in layer_list}
        states = []                      # (S, r, state, quick-bad-mask or None, lemmas)
        for k in range(1, min(self.kmax, n - 2) + 1):
            r = n - k
            hmax = self.dlow[r] - t2 - 1 if r in self.dlow else -1
            lems = [lm for lm in self.lemmas.get(r, ()) if lm[0] - t2 >= 1]
            top = max([hmax] + [d2 - t2 for d2, a2, m2, f in lems])
            if top < 0:
                continue
            capsr = sp.norm_caps(r, t2, rest)
            for ch in itertools.combinations(range(n), k):
                for sg in itertools.product('+-', repeat=k):
                    S = dict(zip(ch, sg))
                    st = sentinel_state(n, layers, S)
                    if st[3] > top:
                        continue
                    content, chlvl = st[0], st[1]
                    bad = None
                    if hmax >= 0 and st[3] <= hmax:
                        bad = 0
                        for (i, j), b in pidx.items():
                            if content[i] == 'r' and content[j] == 'r' and max(chlvl[i], chlvl[j]) + 1 > hmax:
                                bad |= 1 << b
                    states.append((S, r, st, bad, lems, capsr, asis_sizes(n, layers, S)))

        if sp._fc is not None and n <= 16:      # the same greedy choice in the compiled core
            ch, opn = sp._fc.qcover(n, t2, states, layer_list, lp=len(layers))
            return ([{'S': {str(c): v for c, v in states[e][0].items()}} for e in ch],
                    [layer_list[i] for i in opn])

        Lp = len(layers)

        def closes(entry, L):
            S, r, st, bad, lems, capsr, asis = entry
            if bad is not None and not (bad & lmask[L]):
                return {'rule': 'quick'}
            if not lems:
                return None
            content, chlvl, asap, h = st
            h2, prof = h, list(asap)
            for i, j in L:
                if content[i] == 'r' and content[j] == 'r':
                    v = max(chlvl[i], chlvl[j]) + 1
                    while len(prof) < v:
                        prof.append(0)
                    prof[v - 1] += 1
                    h2 = max(h2, v)
            for d2, a2, m2, lfid in lems:
                if h2 + t2 > d2:
                    continue
                sizes = [prof[l] if l < h2 else (capsr[l - h2] if l - h2 < len(capsr) else r // 2) for l in range(m2)]
                if all(x <= a2 for x in sizes):
                    return {'rule': 'lemma'}
            if Lp + 1 + t2 <= max(d2 for d2, a2, m2, lfid in lems):
                ai = list(asis) + [sum(1 for i, j in L if content[i] == 'r' and content[j] == 'r')]
                for d2, a2, m2, lfid in lems:
                    if Lp + 1 + t2 > d2:
                        continue
                    sizes = [ai[l] if l <= Lp else (capsr[l - Lp - 1] if l - Lp - 1 < len(capsr) else r // 2)
                             for l in range(m2)]
                    if all(x <= a2 for x in sizes):
                        return {'rule': 'lemma'}
            return None

        chosen, qcovers, open_ = [], [], []
        pending = list(layer_list)
        while pending:
            L = pending.pop(0)
            if any(closes(e, L) for e in chosen):
                continue
            cands = [e for e in states if closes(e, L)]
            if not cands:
                open_.append(L)
                continue
            if len(cands) > 12:
                cands = cands[:12]
            window = pending[:400]
            best = max(cands, key=lambda e: sum(1 for L2 in window if closes(e, L2)))
            chosen.append(best)
            qcovers.append({'S': {str(c): v for c, v in best[0].items()}})
        return qcovers, open_

    def _choose_covers(self, n, layers, t, caps, cap0, rest, allL, covers):
        """Cover facts (S, a): the residual of P under the sentinels S, with the next cap lowered
        by a, has no completion; it covers every next layer with >= a comparators touching the
        sentinels' positions.  Single sentinels first (every one whose lowered cap is binding);
        then pairs and triples while many layers remain, each kept only if proving it added
        fewer new facts than the layers it removes.  Returns the layers left uncovered."""
        # comparators of L touching the positions pos: with lm = channels L uses and lp = pairs it
        # compares (bit sets), a position set with mask pm and pair mask pp is touched by
        # popcount(lm & pm) comparators, minus one if L compares two positions of the set
        pidx = {(i, j): k for k, (i, j) in enumerate(itertools.combinations(range(n), 2))}
        lmask, lpair = {}, {}
        for L in allL:
            m = q = 0
            for i, j in L:
                m |= (1 << i) | (1 << j)
                q |= 1 << pidx[(i, j)]
            lmask[L], lpair[L] = m, q

        def pmasks(pos):
            pm = sum(1 << p for p in pos)
            pp = sum(1 << pidx[(i, j)] for i, j in itertools.combinations(sorted(pos), 2))
            return pm, pp

        def touching(L, pos, masks=None):
            pm, pp = masks or pmasks(pos)
            return (lmask[L] & pm).bit_count() - (1 if lpair[L] & pp else 0)
        uncovered = list(allL)
        single = {}
        capr1 = sp.norm_caps(n - 1, t, (cap0 - 1,) + rest)
        binding1 = n - 1 >= 2 and cap0 >= 1 and capr1 != sp.norm_caps(n - 1, t, caps)
        for c in range(n):
            for sg in '+-':
                S = {c: sg}
                (p,) = occupancy(n, layers, S)
                rr, R, h, _, _ = sp.residual2(n, layers, S)
                if p not in single or h < single[p][2]:
                    single[p] = (S, R, h)
                if not binding1 or any(p in cv['pos'] and cv['a'] == 1 for cv in covers):
                    continue
                if not any(lmask[L] >> p & 1 for L in uncovered):
                    continue
                res, fid = self.ext(n - 1, R, t, None, capr1)
                if res == 'NO':
                    covers.append({'S': {str(c): sg}, 'pos': [p], 'a': 1, 'node': fid})
                    uncovered = [L for L in uncovered if not lmask[L] >> p & 1]
        if len(uncovered) < self.multi_min or self.cover_k < 2:
            return uncovered
        ranked = sorted(single, key=lambda p: single[p][2])[:self.cover_rank]
        options = []
        for size in range(2, self.cover_k + 1):
            for ps in itertools.combinations(ranked, size):
                S = {}
                for p in ps:
                    S.update(single[p][0])
                if len(S) < size:
                    continue
                occ = occupancy(n, layers, S)
                if occ != frozenset(ps):
                    continue
                rr, R, h, _, _ = sp.residual2(n, layers, S)
                for a in range(size, 0, -1):
                    if a <= cap0:
                        options.append((S, occ, a, R))
        omasks = [pmasks(pos) for _, pos, _, _ in options]
        tried, budget = set(), self.cover_budget
        while len(uncovered) >= self.multi_min and budget > 0:
            best, gain = None, 0
            for k, (S, pos, a, R) in enumerate(options):
                if k in tried:
                    continue
                pm, pp = omasks[k]
                g = sum(1 for L in uncovered if (lmask[L] & pm).bit_count() - (1 if lpair[L] & pp else 0) >= a)
                if g > gain:
                    best, gain = k, g
            if best is None:
                break
            tried.add(best)
            S, pos, a, R = options[best]
            r = n - len(S)
            capr = sp.norm_caps(r, t, (cap0 - a,) + rest)
            if capr == sp.norm_caps(r, t, caps):
                continue
            budget -= 1
            before = len(self.S.facts)
            res, fid = self.ext(r, R, t, None, capr)
            if res == 'NO' and len(self.S.facts) - before < gain:
                covers.append({'S': {str(c): v for c, v in S.items()}, 'pos': sorted(pos), 'a': a, 'node': fid})
                uncovered = [L for L in uncovered if touching(L, pos, omasks[best]) < a]
        return uncovered


def main():
    path = sys.argv[1]
    log = lambda s: print(time.strftime('%H:%M:%S'), s, flush=True)
    store = Store(path)
    log(f'loaded {store.loaded} facts, {len(store.statements)} statements from {path}')
    if '--assemble' in sys.argv:            # prove statements from facts already stored, no new search
        P = Prover(store, absorb=False, subsume=False, qcover=False, max_rec=0, log=log)
    else:
        P = Prover(store, absorb='--no-absorb' not in sys.argv, subsume='--no-sub' not in sys.argv,
                   qcover='--no-qcover' not in sys.argv, oracle='--oracle' in sys.argv,
                   guide='--guide' in sys.argv, wide_sub='--wide-sub' in sys.argv, log=log)
    node = None
    argv = list(sys.argv)
    if '--node' in argv:                    # --node N T 'PREFIX_JSON': prove one node, no statement
        k = argv.index('--node')
        node = (int(argv[k + 1]), int(argv[k + 2]),
                tuple(tuple(tuple(c) for c in L) for L in json.loads(argv[k + 3])))
        del argv[k:k + 4]
    sts = [a for a in argv[2:] if not a.startswith('--')]
    for r in range(3, 11):                  # D(r) bounds are statements too
        if f'D:{r}' not in sts:
            sts.insert(r - 3, f'D:{r}')
    for st in sts:
        t0 = time.time()
        before = dict(P.stats)
        res, fid = P.prove(st)
        delta = {k: P.stats[k] - before[k] for k in P.stats}
        log(f'{st}: {"PROVED" if res == "NO" else "a sorter EXISTS"} ({time.time() - t0:.0f}s) fact {fid}; new work {delta}')
    if node:
        n, layers, t0 = node[0], node[2], time.time()
        before, nfacts = dict(P.stats), len(store.facts)
        res, fid = P.ext(n, layers, node[1])
        delta = {k: P.stats[k] - before[k] for k in P.stats}
        log(f'node n={n} t={node[1]} {json.dumps(layers)}: {"NO completion" if res == "NO" else "EXTENDS"} '
            f'({time.time() - t0:.0f}s) fact {fid}; {len(store.facts) - nfacts} new facts; new work {delta}')


if __name__ == '__main__':
    main()
