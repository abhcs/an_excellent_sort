"""UNSAT cores over inputs for S14 root children: every input's clauses are guarded by a selector,
the solver refutes under all selectors, and its core of selectors is refuted again until it stops
shrinking.  Prints the core size and weights, and saves cores to OUT (JSON lines).
usage: CASE OUT K [K ...] [--rounds R] [--no-phi]"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, '..'), os.path.join(HERE, '..', '..', 'd18-search')]
import ss_cases
import sentinel_prover as sp
import netsat
from netsat import neg


class CoreModel(netsat.Model):
    def add_input_guarded(self, x, s):
        n, r = self.n, self.r
        a, e = netsat.window(x, n)
        z = n - bin(x).count('1')
        cur = {k: bool((x >> k) & 1) for k in range(a, e + 1)}
        G = lambda cl: self.add(list(cl) + [-s])

        def pen(cur):
            for k in range(a, e + 1):
                if k <= z - 4:
                    G([neg(cur[k])])
                elif k >= z + 3:
                    G([cur[k]])
        if r == 2 and self.phi:
            pen(cur)
        for t in range(r - 1):
            new = {k: self.new_var() for k in range(a, e + 1)}
            for k in range(a, e + 1):
                d, u = self.Down(t, k, e), self.Up(t, a, k)
                G([neg(cur[k]), new[k], d])
                G([cur[k], -new[k], u])
            gt = self.g[t]
            for i in range(a, e + 1):
                for j in range(i + 1, e + 1):
                    gl = gt.get((i, j))
                    if gl is None:
                        continue
                    oi, oj, ni, nj = cur[i], cur[j], new[i], new[j]
                    G([-gl, neg(oi), nj]); G([-gl, oi, oj, -nj]); G([-gl, neg(oi), neg(oj), ni]); G([-gl, oj, -ni])
            cur = new
            if t == r - 3 and self.phi:
                pen(cur)
        for k in range(a, e + 1):
            if k <= z - 2:
                G([neg(cur[k])])
            elif k >= z + 1:
                G([cur[k]])
        p, q = cur[z - 1], cur[z]
        G([p, q]); G([neg(p), neg(q)]); G([neg(p), self.L(z - 1)])


def core(n, prefix, t, rounds, phi=True, log=print):
    U = sorted(x for x in netsat.prefix_images(n, prefix) if not netsat.is_sorted(x, n))
    M = CoreModel(n, t, U, solver='cadical195', phi=phi)
    sel = {}
    for x in U:
        s = M.new_var()
        sel[s] = x
        M.add_input_guarded(x, s)
    assume = list(sel)
    sizes = []
    for rnd in range(rounds):
        t0 = time.time()
        if M.S.solve(assumptions=assume):
            return 'SAT', None, sizes
        c = [l for l in M.S.get_core() if l in sel]
        sizes.append((len(c), round(time.time() - t0, 1)))
        log(f'   round {rnd + 1}: core {len(c)} of {len(assume)} ({time.time() - t0:.1f}s)')
        if len(c) >= len(assume):
            break
        assume = c
    return 'UNSAT', sorted(sel[l] for l in assume), sizes


def main():
    args = sys.argv[1:]
    rounds = 4
    phi = '--no-phi' not in args
    args = [a for a in args if a != '--no-phi']
    if '--rounds' in args:
        i = args.index('--rounds'); rounds = int(args[i + 1]); del args[i:i + 2]
    case, out, ks = int(args[0]), args[1], [int(k) for k in args[2:]]
    n = 14
    L1, cs = ss_cases.cases(n, 5)
    L2, X = cs[case]
    nonred = sp._fc.nonredundant(n, X)
    auts = [g for g in sp._fc.automorphisms(X, n, maxg=500)[0] if g != (tuple(range(n)), False)]
    allL = sp._fc.canonical_layers(n, nonred, 5, auts)
    for k in ks:
        prefix = [list(L1), list(L2), list(allL[k])]
        t0 = time.time()
        print(f'child {k}:', flush=True)
        res, U, sizes = core(n, prefix, 6, rounds, phi=phi, log=lambda s: print(s, flush=True))
        if res != 'UNSAT':
            print(f'child {k}: {res}', flush=True)
            continue
        w = sorted(bin(x).count('1') for x in U)
        print(f'child {k}: core {len(U)} inputs, weights {dict((v, w.count(v)) for v in sorted(set(w)))} '
              f'({time.time() - t0:.0f}s) phi {phi}', flush=True)
        with open(out, 'a') as f:
            f.write(json.dumps({'case': case, 'k': k, 'L3': [list(c) for c in allL[k]], 'phi': phi,
                                'core': U, 'rounds': sizes}) + '\n')


if __name__ == '__main__':
    main()
