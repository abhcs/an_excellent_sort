#!/usr/bin/env python3
"""Search using necessary conditions on ALL infinity restrictions.

This is a relaxation, not an exact sorting-network encoding. A master UNSAT
proves the requested lower bound; a survivor is NOT necessarily a sorter.
The adversary searches every signed placement symbolically, without sampling.
Only the first layer is filled; intermediate layers are arbitrary matchings.

Run with verify/.venv/bin/python. JSON output records every restriction, so an
UNSAT instance can be reconstructed with --replay (no discovery run required).
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import time

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver, SolverNames

# The first table has hand proofs in README.md; P7 is in h9.md, section 7.5.
HAND_DEPTH = {2: 1, 3: 3, 4: 3, 5: 5, 6: 5, 7: 6, 8: 6, 9: 7, 10: 7}
KNOWN_DEPTH = HAND_DEPTH | {11: 8, 12: 8, 13: 9, 14: 9, 15: 9, 16: 9, 17: 10}
# Optional literature inputs, not claimed as hand proofs by this program.
KNOWN_SIZE = {2: 1, 3: 3, 4: 5, 5: 9, 6: 12, 7: 16, 8: 19, 9: 25,
              10: 29, 11: 35, 12: 39, 13: 44, 14: 48, 15: 53, 16: 57, 17: 63}


def neg(x):
    return not x if isinstance(x, bool) else -x


class CNF:
    def __init__(self):
        self.pool = IDPool()
        self.clauses = []

    def var(self):
        return self.pool.id()

    def add(self, *xs):
        if any(x is True for x in xs):
            return
        ys = list(dict.fromkeys(x for x in xs if x is not False))
        if any(-x in ys for x in ys):
            return
        self.clauses.append(ys)

    def conj(self, xs):
        xs = list(xs)
        if any(x is False for x in xs):
            return False
        xs = list(dict.fromkeys(x for x in xs if x is not True))
        if not xs:
            return True
        if len(xs) == 1:
            return xs[0]
        v = self.var()
        for x in xs:
            self.add(-v, x)
        self.add(v, *(neg(x) for x in xs))
        return v

    def disj(self, xs):
        return neg(self.conj(neg(x) for x in xs))

    def ge(self, xs, k):
        xs = list(xs)
        k -= sum(x is True for x in xs)
        xs = [x for x in xs if not isinstance(x, bool)]
        if k <= 0:
            return True
        if k > len(xs):
            return False
        if k == 1:
            return self.disj(xs)
        if k == len(xs):
            return self.conj(xs)
        v = self.var()
        yes = CardEnc.atleast(xs, k, vpool=self.pool, encoding=EncType.seqcounter)
        no = CardEnc.atmost(xs, k - 1, vpool=self.pool, encoding=EncType.seqcounter)
        for clause in yes.clauses:
            self.add(-v, *clause)
        for clause in no.clauses:
            self.add(v, *clause)
        return v

    def eq(self, a, b, guard=True):
        self.add(neg(guard), neg(a), b)
        self.add(neg(guard), a, neg(b))

    def gate(self, a, b, low, high, guard=True):
        """guard -> (low = a AND b, high = a OR b)."""
        z = neg(guard)
        self.add(z, neg(low), a)
        self.add(z, neg(low), b)
        self.add(z, low, neg(a), neg(b))
        self.add(z, high, neg(a))
        self.add(z, high, neg(b))
        self.add(z, neg(high), a, b)


def profile_condition(cnf, leaks, r, depth, strong=True, h9=False, sizes=False):
    """True exactly when the retained network passes the selected necessary facts.

    leaks[t] is a list of literals, one for each real-real comparator at t.
    Empty layers can be removed before applying a fact about first layers.
    """
    active = [cnf.disj(row) for row in leaks]
    conditions = [cnf.ge(active, depth[r])]
    if sizes:
        conditions.append(cnf.ge([x for row in leaks for x in row], KNOWN_SIZE[r]))
    # At minimum depth, an early nonempty layer must exceed the given cap.
    rules = {5: (5, 2, 1), 7: (6, 1, 1)} if strong else {}
    if h9:
        rules[9] = (7, 2, 3)
    if r in rules:
        d, early, cap = rules[r]
        large_early = []
        for t, row in enumerate(leaks):
            large_early.append(cnf.conj([
                cnf.ge(row, cap + 1), neg(cnf.ge(active[:t], early))]))
        conditions.append(cnf.disj([cnf.ge(active, d + 1), *large_early]))
    return cnf.conj(conditions)


def fixed_step(cnf, values, layer):
    """Two threshold bits encode -infinity=(0,0), real=(1,0), +inf=(1,1)."""
    reals = [cnf.conj([lo, neg(hi)]) for lo, hi in values]
    leaks = [cnf.conj([reals[a], reals[b]]) for a, b in layer]
    nxt = list(values)
    for a, b in layer:
        nxt[a] = tuple(cnf.conj([values[a][q], values[b][q]]) for q in (0, 1))
        nxt[b] = tuple(cnf.disj([values[a][q], values[b][q]]) for q in (0, 1))
    return nxt, leaks


def simulate(net, placement):
    xs = list(placement)
    profile = []
    for layer in net:
        profile.append(sum(xs[a] == xs[b] == 0 for a, b in layer))
        for a, b in layer:
            xs[a], xs[b] = min(xs[a], xs[b]), max(xs[a], xs[b])
    return profile


def passes(profile, r, depth, strong=True, h9=False, sizes=False):
    p = [x for x in profile if x]
    if len(p) < depth[r]:
        return False
    if sizes and sum(p) < KNOWN_SIZE[r]:
        return False
    if strong and r == 5 and len(p) == 5 and p[:2] == [1, 1]:
        return False
    if strong and r == 7 and len(p) == 6 and p[0] == 1:
        return False
    if h9 and r == 9 and len(p) == 7 and max(p[:2]) <= 3:
        return False
    return True


def adversary(net, n, r, depth, strong, h9, solver, sizes=False):
    cnf = CNF()
    xs = [(cnf.var(), cnf.var()) for _ in range(n)]
    for lo, hi in xs:
        cnf.add(-hi, lo)
    real = [cnf.conj([lo, -hi]) for lo, hi in xs]
    cnf.add(cnf.ge(real, r))
    cnf.add(neg(cnf.ge(real, r + 1)))
    # Sorting the types inside a first-layer pair changes no leak count or
    # subsequent type state. This removes duplicate adversarial placements.
    for a, b in net[0]:
        for q in (0, 1):
            cnf.add(-xs[a][q], xs[b][q])
    cur, leaks = xs, []
    for layer in net:
        cur, row = fixed_step(cnf, cur, layer)
        leaks.append(row)
    cnf.add(neg(profile_condition(cnf, leaks, r, depth, strong, h9, sizes)))
    with Solver(name=solver, bootstrap_with=cnf.clauses) as s:
        if not s.solve():
            return None
        model = set(s.get_model())
    placement = [(int(lo in model) + int(hi in model)) - 1 for lo, hi in xs]
    assert placement.count(0) == r
    assert not passes(simulate(net, placement), r, depth, strong, h9, sizes)
    return placement


class Master(CNF):
    def __init__(self, n, d, first=None, adjacent=True, no_repeat=False):
        super().__init__()
        self.n, self.d = n, d
        self.first = n // 2 if first is None else first
        self.prefix = [(2 * i, 2 * i + 1) for i in range(self.first)]
        self.pairs = list(itertools.combinations(range(n), 2))
        self.g = {}
        self.used = {}
        for t in range(1, d):
            for a, b in self.pairs:
                self.g[t, a, b] = self.var()
                if adjacent and t == d - 1 and b != a + 1:
                    self.add(-self.g[t, a, b])
            for a in range(n):
                inc = [self.g[t, min(a, b), max(a, b)] for b in range(n) if a != b]
                for x, y in itertools.combinations(inc, 2):
                    self.add(-x, -y)
                self.used[t, a] = self.disj(inc)
        if no_repeat:
            for t in range(1, d):
                for a, b in self.pairs:
                    previous = (a, b) in self.prefix if t == 1 else self.g[t - 1, a, b]
                    self.add(neg(previous), -self.g[t, a, b])

    def restriction(self, placement, depth, strong, h9, sizes=False):
        r = placement.count(0)
        cur = [(x >= 0, x >= 1) for x in placement]
        cur, first_leaks = fixed_step(self, cur, self.prefix)
        leaks = [first_leaks]
        for t in range(1, self.d):
            real = [self.conj([lo, neg(hi)]) for lo, hi in cur]
            # A matching has at most one edge with a given lower endpoint.
            # Counting these ORs counts each real-real comparator once, and
            # greatly reduces the cardinality encodings for size bounds.
            row = [self.disj(self.conj([self.g[t, a, b], real[a], real[b]])
                             for b in range(a + 1, self.n)) for a in range(self.n - 1)]
            leaks.append(row)
            nxt = [(self.var(), self.var()) for _ in range(self.n)]
            for a, b in self.pairs:
                for q in (0, 1):
                    self.gate(cur[a][q], cur[b][q], nxt[a][q], nxt[b][q], self.g[t, a, b])
            for a in range(self.n):
                for q in (0, 1):
                    self.eq(cur[a][q], nxt[a][q], neg(self.used[t, a]))
            cur = nxt
        self.add(profile_condition(self, leaks, r, depth, strong, h9, sizes))

    def network(self, model):
        pos = set(model)
        return [self.prefix] + [[(a, b) for a, b in self.pairs if self.g[t, a, b] in pos]
                                for t in range(1, self.d)]


def binary_failure(net, n):
    for x in itertools.product((0, 1), repeat=n):
        y = list(x)
        for layer in net:
            for a, b in layer:
                y[a], y[b] = min(y[a], y[b]), max(y[a], y[b])
        if y != sorted(y):
            return list(x)
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('n', type=int, nargs='?')
    ap.add_argument('d', type=int, nargs='?')
    ap.add_argument('--retained', default='3,5,7,9,11,13,17')
    ap.add_argument('--bases', choices=['hand', 'known'], default='hand')
    ap.add_argument('--plain', action='store_true', help='omit Lemma 3 and P7')
    ap.add_argument('--h9', action='store_true', help='also use computer-assisted H9')
    ap.add_argument('--sizes', action='store_true', help='also use literature size lower bounds')
    ap.add_argument('--first', type=int, help='test a sparse first layer instead of the full problem')
    ap.add_argument('--free-last', action='store_true')
    ap.add_argument('--no-repeat', action='store_true', help='delete immediately repeated comparators, a valid normal form')
    ap.add_argument('--solver', default='cadical195')
    ap.add_argument('--iterations', type=int, default=1000)
    ap.add_argument('--seconds', type=float, default=300, help='checked between 10000-conflict master chunks and between adversary calls')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--replay', type=Path)
    ap.add_argument('--dimacs', type=Path)
    args = ap.parse_args()
    if args.solver in SolverNames.kissat404:
        ap.error('the incremental master requires CaDiCaL, Glucose, or another incremental solver; Kissat is not supported')
    if args.replay:
        old = json.loads(args.replay.read_text())
        cfg = old['config']
    else:
        if args.n is None or args.n < 3 or args.d is None or args.d < 2:
            ap.error('n >= 3 and d >= 2 are required without --replay')
        if args.first is not None and not 0 <= args.first <= args.n // 2:
            ap.error('first must lie between 0 and floor(n/2)')
        cfg = dict(n=args.n, d=args.d, bases=args.bases, strong=not args.plain,
                   h9=args.h9, sizes=args.sizes, first=args.first, adjacent=not args.free_last,
                   no_repeat=args.no_repeat,
                   retained=[int(r) for r in args.retained.split(',')])
    depth = HAND_DEPTH if cfg['bases'] == 'hand' else KNOWN_DEPTH
    sizes = cfg.get('sizes', False)  # compatibility with the first transcripts
    rs = [r for r in cfg['retained'] if r < cfg['n'] and r in depth]
    if not rs:
        ap.error('no retained size is available in the selected base facts')
    master = Master(cfg['n'], cfg['d'], cfg['first'], cfg['adjacent'], cfg.get('no_repeat', False))
    data = dict(config=cfg, status='INCOMPLETE', restrictions=[], iterations=0, encoding_version=2,
                solver=args.solver,
                proof_scope='full lower bound' if cfg['first'] is None else 'sparse-first-layer lemma')
    start = time.monotonic()

    def save():
        data['seconds'] = round(time.monotonic() - start, 3)
        data['variables'] = master.pool.top
        data['clauses'] = len(master.clauses)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(data, indent=2) + '\n')

    try:
        with Solver(name=args.solver, bootstrap_with=master.clauses) as solver:
            sent = len(master.clauses)
            if args.replay:
                for placement in old['restrictions']:
                    master.restriction(placement, depth, cfg['strong'], cfg['h9'], sizes)
                data['restrictions'] = old['restrictions']
            for iteration in range(args.iterations):
                solver.append_formula(master.clauses[sent:])
                sent = len(master.clauses)
                data['iterations'] = iteration + 1
                save()
                ok = None
                while time.monotonic() - start < args.seconds:
                    solver.conf_budget(10000)
                    ok = solver.solve_limited()
                    if ok is not None:
                        break
                if ok is None:
                    data['status'] = 'TIME_LIMIT'
                    break
                if ok is False:
                    data['status'] = 'UNSAT'
                    break
                net = master.network(solver.get_model())
                data['last_candidate'] = net
                if args.replay:
                    data['status'] = 'REPLAY_SAT'
                    break
                bad = []
                for r in rs:
                    if time.monotonic() - start >= args.seconds:
                        data['status'] = 'TIME_LIMIT'
                        break
                    placement = adversary(net, cfg['n'], r, depth, cfg['strong'], cfg['h9'], args.solver, sizes)
                    if placement is not None:
                        bad.append(placement)
                if data['status'] == 'TIME_LIMIT':
                    break
                if not bad:
                    data['status'] = 'SURVIVOR'
                    data['candidate'] = net
                    data['binary_failure'] = binary_failure(net, cfg['n'])
                    break
                for placement in bad:
                    assert placement not in data['restrictions']
                    data['restrictions'].append(placement)
                    master.restriction(placement, depth, cfg['strong'], cfg['h9'], sizes)
                if iteration % 10 == 0:
                    print(f"iteration={iteration + 1} restrictions={len(data['restrictions'])} "
                          f"vars={master.pool.top} elapsed={time.monotonic() - start:.1f}s", flush=True)
                if time.monotonic() - start >= args.seconds:
                    data['status'] = 'TIME_LIMIT'
                    break
            else:
                data['status'] = 'ITERATION_LIMIT'
    except KeyboardInterrupt:
        data['status'] = 'INTERRUPTED'
    except Exception as exc:
        # PySAT reports SIGINT from its C solvers as its own exception type.
        if 'keyboard interrupt' not in str(exc).lower():
            raise
        data['status'] = 'INTERRUPTED'
    if args.dimacs:
        with args.dimacs.open('w') as f:
            f.write(f'p cnf {master.pool.top} {len(master.clauses)}\n')
            for clause in master.clauses:
                f.write(' '.join(map(str, clause)) + ' 0\n')
        data['dimacs_sha256'] = hashlib.sha256(args.dimacs.read_bytes()).hexdigest()
    save()
    print(json.dumps({k: data[k] for k in ['status', 'seconds', 'iterations', 'variables', 'clauses']}), flush=True)


if __name__ == '__main__':
    main()
