"""satnet.py -- an exact SAT encoding of "some comparator network of this shape sorts".

Channels are 0..n-1; a comparator (a, b), a < b, sends the minimum to a.  The network is a fixed
`prefix` (a list of layers, applied to the inputs directly) followed by d FREE layers.  Free layer t
(0-based) is ANY matching subject only to
    caps[t]     at most that many comparators (None: no cap),
    allowed[t]  the set of pairs it may use (None: every pair).
No maximality and no other normal form is built in (README section 8: adding comparators to a middle
layer can break a sorting network, so middle layers must range over all matchings).

Exactness.  Variables g[t,a,b] choose the comparators.  For every input and free layer there is one
value variable per channel, tied to the previous values by full equivalences: max-end of (a,b) gets
OR, min-end gets AND, an unused channel copies.  So for each choice of the free layers there is
exactly one assignment of the value variables, and it meets the output clauses iff the network sorts
every input.  Hence SAT <=> such a network exists, and the models projected onto the g variables are
in bijection with the sorting networks of the given shape (checked against brute force in
h9_validate.py).  The inputs are the images of all 2^n binary vectors under the prefix, minus the
sorted ones (a standard network fixes every sorted vector).
"""
import itertools

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool


def apply(layers, x):
    x = list(x)
    for layer in layers:
        for (a, b) in layer:
            if x[a] > x[b]:
                x[a], x[b] = x[b], x[a]
    return x


def sorts(layers, n):
    return all(apply(layers, v) == sorted(v) for v in itertools.product((0, 1), repeat=n))


def _neg(l):
    return (not l) if isinstance(l, bool) else -l


class Encoding:
    def __init__(self, n, d, caps=None, prefix=(), allowed=None):
        self.n, self.d, self.prefix = n, d, [list(L) for L in prefix]
        self.pool = pool = IDPool()
        self.clauses = []
        self.pairs = pairs = list(itertools.combinations(range(n), 2))
        g = self.g = {(t, a, b): pool.id(('g', t, a, b)) for t in range(d) for (a, b) in pairs}
        add = self._add
        for t in range(d):
            if allowed is not None and allowed[t] is not None:
                for (a, b) in pairs:
                    if (a, b) not in allowed[t]:
                        add([-g[t, a, b]])
        used = {}
        for t in range(d):                       # each layer is a matching
            for k in range(n):
                inc = [g[t, min(k, m), max(k, m)] for m in range(n) if m != k]
                for x, y in itertools.combinations(inc, 2):
                    add([-x, -y])
                u = used[t, k] = pool.id(('u', t, k))
                add([-u] + inc)
                for x in inc:
                    add([-x, u])
        for t in range(d):                       # per-layer caps
            if caps is not None and caps[t] is not None:
                lits = [g[t, a, b] for (a, b) in pairs]
                enc = CardEnc.atmost(lits=lits, bound=caps[t], vpool=pool, encoding=EncType.seqcounter)
                for cl in enc.clauses:
                    add(cl)
        imgs = sorted({tuple(apply(self.prefix, x)) for x in itertools.product((0, 1), repeat=n)})
        self.inputs = [x for x in imgs if list(x) != sorted(x)]
        for xi, x in enumerate(self.inputs):
            cur = [bool(b) for b in x]           # Python booleans are constants
            for t in range(d):
                nxt = [pool.id(('v', xi, t, k)) for k in range(n)]
                for k in range(n):
                    vk, nk = cur[k], nxt[k]
                    for m in range(n):
                        if m == k:
                            continue
                        gl, vm = g[t, min(k, m), max(k, m)], cur[m]
                        if k > m:                # k is the max end: nk <-> vk OR vm
                            add([-gl, _neg(vk), nk]); add([-gl, _neg(vm), nk]); add([-gl, vk, vm, -nk])
                        else:                    # k is the min end: nk <-> vk AND vm
                            add([-gl, vk, -nk]); add([-gl, vm, -nk]); add([-gl, _neg(vk), _neg(vm), nk])
                    u = used[t, k]
                    add([u, _neg(vk), nk]); add([u, vk, -nk])
                cur = nxt
            w = sum(x)
            for k in range(n):                   # output sorted: ones exactly on channels n-w..n-1
                add([cur[k]] if k >= n - w else [_neg(cur[k])])

    def _add(self, cl):
        out = []
        for l in cl:
            if l is True:
                return
            if l is False:
                continue
            out.append(l)
        if not out:                              # an empty clause: make the formula UNSAT explicitly
            z = self.pool.id(('empty', len(self.clauses)))
            self.clauses += [[z], [-z]]
            return
        self.clauses.append(out)

    @property
    def nvars(self):
        return self.pool.top

    def network(self, model):
        """The free layers chosen by a model (prefix not included)."""
        pos = {l for l in model if l > 0}
        return [[(a, b) for (a, b) in self.pairs if self.g[t, a, b] in pos] for t in range(self.d)]

    def gvars(self):
        return [self.g[t, a, b] for t in range(self.d) for (a, b) in self.pairs]

    def write_dimacs(self, path):
        with open(path, 'w') as f:
            f.write(f'p cnf {self.nvars} {len(self.clauses)}\n')
            for cl in self.clauses:
                f.write(' '.join(map(str, cl)) + ' 0\n')


def solve(enc, name='cadical195'):
    from pysat.solvers import Solver
    with Solver(name=name, bootstrap_with=enc.clauses) as s:
        ok = s.solve()
        return ok, (s.get_model() if ok else None)


def count(enc, name='cadical195', limit=None):
    """Number of models projected onto the comparator variables = number of sorting networks."""
    from pysat.solvers import Solver
    gv = enc.gvars()
    c = 0
    with Solver(name=name, bootstrap_with=enc.clauses) as s:
        while s.solve():
            val = {abs(l): l > 0 for l in s.get_model()}
            c += 1
            if limit is not None and c >= limit:
                break
            s.add_clause([-v if val[v] else v for v in gv])
    return c


def adjacent_pairs(n):
    return {(i, i + 1) for i in range(n - 1)}
