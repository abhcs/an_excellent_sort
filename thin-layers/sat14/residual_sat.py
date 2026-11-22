"""For hard S14 root children: which sentinel residual does the prover's SAT guidance pick, and what
does a checkable SAT refutation of that residual cost?

For each child: run the prover's candidate generation and guidance on an empty store (so no stored
residual helps, as for the hard children), stop before it recurses, take the first candidate whose
guide verdict is NO, then refute that residual with netsat's model by CEGAR (pysat CaDiCaL), dump
the final CNF, re-solve it with the standalone CaDiCaL writing a DRAT proof, and check the proof with
drat-trim.  usage: CASE K [K ...]   (prints one JSON line per child)"""
import json, os, shutil, subprocess, sys, tempfile, time
HERE = os.path.dirname(os.path.abspath(__file__))
TL = os.path.join(HERE, '..')
sys.path[:0] = [TL, os.path.join(TL, '..', 'd18-search')]
import sprove, ss_cases
import sentinel_prover as sp
from netsat import apply_layers, is_sorted, prefix_images, window
from thinsat import RecModel

from satcert import CADICAL, DRATTRIM


class Stop(Exception):
    pass


def refute(r, R, t, init=200, batch=30, solver='cadical195', limit=600):
    """CEGAR on netsat's model; ('UNSAT', model, inputs) or ('SAT', net) or ('LIMIT',)."""
    U = sorted(x for x in prefix_images(r, [list(L) for L in R]) if not is_sorted(x, r))
    M = RecModel(r, t, U, solver=solver)
    import random
    rng = random.Random(0)
    added = set(U if len(U) <= init else rng.sample(U, init))
    for x in sorted(added):
        M.add_input(x)
    wsize = {x: (lambda ae: ae[1] - ae[0] + 1)(window(x, r)) for x in U}
    t0 = time.time()
    while time.time() - t0 < limit:
        if not M.S.solve():
            return 'UNSAT', M, sorted(added), len(U)
        net = M.network(M.S.get_model())
        fails = [x for x in U if x not in added and not is_sorted(apply_layers(net, x), r)]
        if not fails:
            return 'SAT', net, None, len(U)
        fails.sort(key=lambda x: (wsize[x], rng.random()))
        for x in fails[:batch]:
            M.add_input(x)
            added.add(x)
    return 'LIMIT', None, None, len(U)


def drat(M, tag):
    d = tempfile.mkdtemp()
    cnf, proof = os.path.join(d, f'{tag}.cnf'), os.path.join(d, f'{tag}.drat')
    M.dump(cnf, [tag])
    t0 = time.time()
    p = subprocess.run([CADICAL, '-q', '--binary=false', cnf, proof], capture_output=True, text=True)
    t_solve = time.time() - t0
    t0 = time.time()
    q = subprocess.run([DRATTRIM, cnf, proof, '-t', '100000'], capture_output=True, text=True)
    t_check = time.time() - t0
    out = q.stdout.replace('\r', '\n')
    res = {'cadical_rc': p.returncode, 'solve_s': round(t_solve, 2), 'check_s': round(t_check, 2),
           'drat_bytes': os.path.getsize(proof) if os.path.exists(proof) else 0,
           'cnf_bytes': os.path.getsize(cnf), 'verified': '\ns VERIFIED' in '\n' + out}
    shutil.rmtree(d)
    return res


def main():
    case = int(sys.argv[1])
    ks = [int(k) for k in sys.argv[2:]]
    n = 14
    L1, cs = ss_cases.cases(n, 5)
    L2, X = cs[case]
    nonred = sp._fc.nonredundant(n, X)
    auts = [g for g in sp._fc.automorphisms(X, n, maxg=500)[0] if g != (tuple(range(n)), False)]
    allL = sp._fc.canonical_layers(n, nonred, 5, auts)
    tmp = tempfile.mkdtemp()
    shutil.copy(os.path.join(TL, 'facts_s14', 'statements.jsonl'), tmp)
    S = sprove.Store(tmp, compact=True)
    for k in ks:
        L3 = allL[k]
        Y = sp._fc.apply_layer(n, X, L3)
        P = sprove.Prover(S, oracle=False, guide=True, guide_big_n=12, guide_big_seconds=2.0,
                          guide_skip_n=13, guide_conflicts=10000, absorb_max_n=12)
        cap = {}
        orig = P._guided

        def grab(n_, t_, caps_, cands, resid):
            t0 = time.time()
            order = orig(n_, t_, caps_, cands, resid)
            cap.update(order=order, resid=resid, secs=time.time() - t0, ncands=len(cands))
            raise Stop()
        P._guided = grab
        t0 = time.time()
        try:
            P.ext(n, (L1, L2, L3), 6, Y, ())
            out = {'k': k, 'closed_before_guidance': True}
            print(json.dumps(out), flush=True)
            continue
        except Stop:
            pass
        rec = {'k': k, 'L3': [list(c) for c in L3], 'cands': cap['ncands'], 'guide_s': round(cap['secs'], 1),
               'guide_calls': P.stats['guide']}
        chosen = None
        for h, kk, Sx, i in cap['order'][:3]:
            R = cap['resid'](i)
            XR = sp.outputs(n - kk, R)
            v = P.gcache.get((n - kk, 6, (), len(XR), hash(XR)))
            if v == 'NO':
                chosen = (h, kk, Sx, R)
                break
        if chosen is None:
            rec['chosen'] = None
            print(json.dumps(rec), flush=True)
            continue
        h, kk, Sx, R = chosen
        r = n - kk
        rec.update(r=r, h=h, sentinels={str(c): v for c, v in Sx.items()},
                   R=[[list(c) for c in L] for L in R], R_sizes=[len(L) for L in R])
        t0 = time.time()
        verdict, M, inputs, nU = refute(r, R, 6)
        rec.update(cegar=verdict, cegar_s=round(time.time() - t0, 1), U=nU,
                   inputs=len(inputs) if inputs else None)
        if verdict == 'UNSAT':
            rec.update(M.nv and {'vars': M.nv, 'clauses': len(M.rec)})
            rec['drat'] = drat(M, f'c{case}_k{k}')
        print(json.dumps(rec), flush=True)
    shutil.rmtree(tmp)


if __name__ == '__main__':
    main()
