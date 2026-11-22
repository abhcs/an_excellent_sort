#!/usr/bin/env python3
"""thinsat.py -- is there an n-channel sorting network of depth d whose first two layers have at most
a comparators each?  ("T(n,a) <= d?")

One signed infinity turns a (2p+1)-channel network of depth d into a 2p-channel one of depth <= d with
at most p-1 comparators in each of its first two layers (depth-hand-proofs/rank-cut-reductions.md,
extension.md).  So "T(2p, p-1) > d" implies D(2p+1) > d.

Normal form (each step keeps the layer sizes, or lowers them, and keeps sorting):
  * L1 = a disjoint pairs in the middle, (s,s+1),(s+2,s+3),..., s = (n-2a)/2: relabel, untangle.
  * remove redundant comparators; then netsat.Model's constraints hold: last layer adjacent [phi1],
    penultimate layer j-i <= 3 with phi3/phi4, first free layer swaps on some prefix output, plus
    redundancy tracking.  A cardinality constraint caps free layer 0 (= L2) at a.
Optional case splits: --l2 fixes the second layer exactly (JSON list of pairs, applied as part of the
prefix), --last fixes the set of last-layer comparators (JSON list of adjacent pairs).

CEGAR as in netsat.search; every network found is checked on all 2^n inputs.
"""
import argparse
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'd18-search'))
from netsat import Model, apply_layers, is_sorted, prefix_images, verify_all, window  # noqa: E402
from pysat.card import CardEnc, EncType  # noqa: E402


class RecModel(Model):
    """netsat.Model that also records every clause it adds, so the final formula can be dumped
    and re-solved by an external proof-producing solver."""

    def __init__(self, *args, **kw):
        self.rec = []
        super().__init__(*args, **kw)

    def add(self, cl):
        out = []
        for l in cl:
            if l is True:
                return
            if l is False:
                continue
            out.append(l)
        if not out:
            v = self.new_var()
            for c in ([v], [-v]):
                self.rec.append(c)
                self.S.add_clause(c)
            self.ncl += 2
            return
        self.rec.append(out)
        self.S.add_clause(out)
        self.ncl += 1

    def dump(self, path, comments=()):
        with open(path, 'w') as f:
            for c in comments:
                f.write(f'c {c}\n')
            f.write(f'p cnf {self.nv} {len(self.rec)}\n')
            for cl in self.rec:
                f.write(' '.join(map(str, cl)) + ' 0\n')


def middle_layer(n, a):
    """The normalized first layer: a disjoint adjacent pairs, the n-2a idle channels split evenly
    between the two ends (one in the middle when n-2a is odd), so that L1 is invariant under the
    duality i -> n-1-i (which also swaps min and max ends).  Any first layer of a comparators can be
    brought to this form by relabeling and untangling, keeping all layer sizes."""
    k = n - 2 * a
    left = k // 2
    pairs, pos = [], left
    for i in range(a):
        if k % 2 == 1 and i == a // 2 and a % 2 == 0:
            pos += 1                       # the middle idle channel
        pairs.append((pos, pos + 1))
        pos += 2
    used = {c for p in pairs for c in p}
    assert len(used) == 2 * a and max(used) < n
    return pairs


def run(n, depth, a, l2=None, last=None, solver='cadical195', init=300, batch=30, seed=0, log=print,
        cap2=True, capped=2, dump=None, cosat=False, exceptional=None, caps=None):
    t_start = time.time()
    prefix = [middle_layer(n, a)]
    if l2 is not None:
        prefix.append([tuple(p) for p in l2])
    r = depth - len(prefix)
    U = sorted(x for x in prefix_images(n, prefix) if not is_sorted(x, n))
    wsize = {x: (lambda ae: ae[1] - ae[0] + 1)(window(x, n)) for x in U}
    M = RecModel(n, r, U, solver=solver, cosat=cosat)
    # cap layers 2..capped (free layers 0..capped-2, or 1..capped-2 when --l2 fixes layer 2)
    first_free_layer = len(prefix) + 1            # 1-based index of free layer 0
    for t in range(r):
        layer = first_free_layer + t
        if caps is not None:                      # per-layer caps for layers 2, 3, ...
            if layer - 2 >= len(caps):
                continue
            bound = caps[layer - 2]
        else:
            if layer > capped or (layer == 2 and not cap2):
                continue
            bound = a
        lits = sorted(M.g[t].values())
        enc = CardEnc.atmost(lits=lits, bound=bound, top_id=M.nv, encoding=EncType.seqcounter)
        for cl in enc.clauses:
            M.add(cl)
        M.nv = max(M.nv, enc.nv)
    if exceptional:
        assert l2 is None, '--exceptional needs the second layer free'
        from exceptional import add_exceptional
        add_exceptional(M, n, a, prefix[0], exceptional)
    if last is not None:
        want = {tuple(p) for p in last}
        for (i, j), v in M.g[r - 1].items():
            M.add([v] if (i, j) in want else [-v])
        for p in want:
            if p not in M.g[r - 1]:
                M.add([])
    log(f'n={n} depth={depth} a={a} capped layers 1..{capped} prefix={prefix} last={last} |U|={len(U)} solver={solver} cosat={cosat} exceptional={exceptional}')
    rng = random.Random(seed)
    added = set()
    first = U if init >= len(U) else rng.sample(U, init)
    for x in first:
        M.add_input(x)
        added.add(x)
    it = 0
    while True:
        it += 1
        t0 = time.time()
        ok = M.S.solve()
        dt = time.time() - t0
        if not ok:
            log(f'UNSAT iter {it} after {dt:.1f}s with {len(added)} inputs; total {time.time() - t_start:.1f}s')
            if dump:
                M.dump(dump, [f'thinsat n={n} depth={depth} a={a} capped={capped} prefix={json.dumps(prefix)}',
                              f'last={json.dumps(last)} inputs={json.dumps(sorted(added))}'])
                log(f'dumped {len(M.rec)} clauses over {M.nv} variables to {dump}')
            return None
        net = M.network(M.S.get_model())
        fails = [x for x in U if x not in added and not is_sorted(apply_layers(net, x), n)]
        log(f'iter {it}: SAT in {dt:.1f}s inputs={len(added)} vars={M.nv} clauses={M.ncl} '
            f'fails={len(fails)} elapsed={time.time() - t_start:.0f}s')
        if not fails:
            full = [list(L) for L in prefix] + net
            assert verify_all(n, full), 'candidate fails full verification: encoding bug'
            if caps is None:
                assert all(len(full[k]) <= a for k in range(min(capped, len(full))))
            else:
                assert len(full[0]) <= a and all(len(full[k + 1]) <= c for k, c in enumerate(caps) if k + 1 < len(full))
            log(f'FOUND depth={len(full)} sizes={[len(L) for L in full]} network={json.dumps(full)}')
            return full
        fails.sort(key=lambda x: (wsize[x], rng.random()))
        for x in fails[:batch]:
            M.add_input(x)
            added.add(x)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('n', type=int)
    ap.add_argument('depth', type=int)
    ap.add_argument('a', type=int)
    ap.add_argument('--l2', default=None)
    ap.add_argument('--last', default=None)
    ap.add_argument('--solver', default='cadical195')
    ap.add_argument('--init', type=int, default=300)
    ap.add_argument('--batch', type=int, default=30)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--no-cap2', action='store_true', help='do not cap the second layer')
    ap.add_argument('--capped', type=int, default=2, help='cap layers 1..CAPPED at a (default 2)')
    ap.add_argument('--caps', default=None, help='JSON list: caps for layers 2, 3, ... (overrides --capped)')
    ap.add_argument('--dump', default=None, help='on UNSAT, write the final CNF (DIMACS) here')
    ap.add_argument('--cosat', action='store_true', help='add the co-saturation end-game constraints psi')
    ap.add_argument('--exceptional', type=int, default=None,
                    help='only networks in which no sentinel track is good through layers 1..M')
    args = ap.parse_args()

    def log(s):
        print(time.strftime('%H:%M:%S'), s, flush=True)

    res = run(args.n, args.depth, args.a,
              l2=json.loads(args.l2) if args.l2 else None,
              last=json.loads(args.last) if args.last else None,
              solver=args.solver, init=args.init, batch=args.batch, seed=args.seed, log=log,
              cap2=not args.no_cap2, capped=args.capped, dump=args.dump, cosat=args.cosat,
              exceptional=args.exceptional, caps=json.loads(args.caps) if args.caps else None)
    sys.exit(0 if res else 1)


if __name__ == '__main__':
    main()
