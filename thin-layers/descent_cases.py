#!/usr/bin/env python3
"""descent_cases.py -- prove SS(n, d, a, 3) case by case, the descent way (README §8.15).

  descent_cases.py SS:n,d,a,3 STORE W w [options]     prove the cases (worker w of W)
  descent_cases.py SS:n,d,a,3 STORE --assemble         prove the statement from its proved cases
  descent_cases.py SS:n,d,a,3 STORE --status           count proved cases

Cases are the second-layer classes of results/l2classes_{n}_{a}.json (ss_cases.py): node (L1, L2)
with d - 2 layers left, the third capped at a.  Workers claim cases with files in
STORE/claims/<statement>/, so any number of workers share a store; facts are shared through it.
For each case:
  1. try the case root with the ordinary prover for --root-seconds (cases whose second layer is
     sparse usually close here by one sentinel step);
  2. otherwise split it on the third layer.  The sentinel covers close every third layer that leaves
     a first-layer sentinel a good track, by the lemma rule with SS(n-1, d, a-1, 3) if that statement
     is recorded in the store (the descent, README §4); what stays open are the exceptional
     third layers and any others the covers miss;
  3. each open child, and the child with an empty third layer, gets --child-seconds of ordinary
     proving, then a SAT certificate of the child itself (satcert.py: CaDiCaL with a DRAT proof that
     drat-trim checks; CaDiCaL limit --sat-seconds);
  4. the case root is assembled: a split whose children are all stored facts now.
A child that SAT completes to a sorting network refutes the statement: it is written to
STORE/COUNTEREXAMPLES.jsonl and the worker stops.  A case with an undecided child is left
unclaimed for a later run (with more --sat-seconds).

Options: --root-seconds S (60; negative: skip the root attempt), --child-seconds S (20; 0: no limit; negative: SAT at once),
--sat-seconds S (CaDiCaL limit; 0: none), --only I,J,...
"""
import json, os, signal, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sprove, ss_cases
import sentinel_prover as sp
from sprove import inv_hash, SatUndecided


class Out(BaseException):              # a time limit: no handler inside the prover may swallow it
    pass


def _alarm(*_):
    raise Out()


def limited(seconds, fn, *a):
    """fn(*a), or 'OPEN' after `seconds` (0 or None: no limit)."""
    if not seconds:
        return fn(*a)
    signal.signal(signal.SIGALRM, _alarm)
    try:
        signal.alarm(int(seconds))
        try:
            return fn(*a)
        finally:
            signal.alarm(0)
    except Out:
        return 'OPEN', None


def opt(args, name, default, conv=float):
    if name in args:
        k = args.index(name)
        v = conv(args[k + 1])
        del args[k:k + 2]
        return v
    return default


def prover(S, **kw):
    base = dict(oracle=True, guide=True, wide_sub=True, share_seconds=60, oracle_max_n=12, guide_big_n=12,
                guide_big_seconds=2.0, absorb_max_n=12, store_first_n=12, store_first_big=10 ** 6,
                guide_skip_n=13, guide_conflicts=10000, sat_certs=True)
    base.update(kw)
    return sprove.Prover(S, **base)


def stored_no(S, n, X, t, caps):
    cls = S.find_class(n, X, inv_hash(X, n))
    hit = S.lookup(cls, n, t, sp.norm_caps(n, t, caps)) if cls is not None else None
    return hit is not None and hit[0] == 'NO'


def prove_case(S, n, a, L1, L2, X, t, caps, args, log):
    """'NO' (case root proved), 'OPEN' (undecided children left), or ('YES', network)."""
    if stored_no(S, n, X, t, caps):
        return 'NO', 'stored'
    t0 = time.time()
    P = prover(S)
    if args['root'] >= 0:                    # a negative --root-seconds goes straight to the split
        res, fid = limited(args['root'], P.ext, n, (L1, L2), t, X, caps)
        if res == 'NO':
            return 'NO', f'root closes ({time.time() - t0:.0f}s, nodes {P.stats["nodes"]})'
    # split on the third layer: the covers close the good-track layers in bulk
    nonred = sp._fc.nonredundant(n, X)
    auts = [g for g in sp._fc.automorphisms(X, n, maxg=P.aut_max)[0] if g != (tuple(range(n)), False)]
    allL = sp._fc.canonical_layers(n, nonred, caps[0], auts)
    R = prover(S, max_rec=0, guide=False, oracle=False, wide_sub=False, absorb=False)
    qc, opn = R._qcover(n, (L1, L2), t, caps, allL)
    rest = sp.norm_caps(n, t - 1, tuple(caps[1:]))
    kids = [(L3, sp._fc.apply_layer(n, X, L3)) for L3 in opn] + [((), X)]
    log(f'  split: {len(allL)} third layers, {len(qc)} covers close {len(allL) - len(opn)}, '
        f'{len(opn)} open (+ the empty layer)')
    nsat = nprov = 0
    for L3, Y in kids:
        layers = (L1, L2, L3) if L3 else (L1, L2)
        if stored_no(S, n, Y, t - 1, rest):
            continue
        if args['child'] >= 0:                # a negative --child-seconds sends every open child to SAT
            Pc = prover(S)
            res, fid = limited(args['child'], Pc.ext, n, layers, t - 1, Y, rest)
        else:
            res = 'OPEN'
        if res == 'NO':
            nprov += 1
            continue
        if res == 'YES':
            return 'YES', layers
        Ps = prover(S, sat_run_n=n, sat_seconds=args['sat'] or None)
        t1 = time.time()
        try:
            res, fid = Ps.ext(n, layers, t - 1, Y, rest)
        except SatUndecided as e:
            log(f'  child {[list(c) for c in L3]}: SAT undecided ({e.rec.get("result")}, {time.time() - t1:.0f}s)')
            return 'OPEN', 'undecided child'
        if res == 'YES':
            return 'YES', layers
        if res != 'NO':
            return 'OPEN', f'child {L3}: {res}'
        nsat += 1
        rec = S.certs.get(__import__('satcert').node_key(n, layers, t - 1, rest), {})
        log(f'  child {[list(c) for c in L3]}: {res} by {"SAT" if Ps.stats["sat"] else "prover"} '
            f'({time.time() - t1:.0f}s; solve {rec.get("solve_s")}s, check {rec.get("check_s")}s)')
    res, fid = R.ext(n, (L1, L2), t, X, caps)
    if res != 'NO':
        return 'OPEN', f'root assembly gave {res}'
    return 'NO', f'split: {nprov} children by the prover, {nsat} by SAT ({time.time() - t0:.0f}s)'


def main():
    args = sys.argv[1:]
    a_root = opt(args, '--root-seconds', 60)
    a_child = opt(args, '--child-seconds', 20)
    a_sat = opt(args, '--sat-seconds', 0)
    only = opt(args, '--only', None, str)
    assemble, status = '--assemble' in args, '--status' in args
    args = [x for x in args if x not in ('--assemble', '--status')]
    statement, path = args[0], args[1]
    kind, spec = statement.split(':')
    n, d, a, m = map(int, spec.split(','))
    assert kind == 'SS' and m == 3, 'only SS(n, d, a, 3)'
    t = d - 2
    caps = sp.norm_caps(n, t, (a,))
    L1, cs = ss_cases.cases(n, a)
    log = lambda s: print(time.strftime('%m-%d %H:%M:%S'), s, flush=True)
    S = sprove.Store(path, compact=True, x_cap=40000)
    log(f'{statement}: {len(cs)} cases; store {S.loaded} facts, {len(S.certs)} SAT records; lemmas '
        f'{sorted(st for st in S.statements if st.startswith("SS"))}')
    if status or assemble:
        done = [i for i, (L2, X) in enumerate(cs) if stored_no(S, n, X, t, caps)]
        log(f'{len(done)} of {len(cs)} cases proved; open: {[i for i in range(len(cs)) if i not in set(done)][:40]}')
        if assemble:
            if len(done) < len(cs):
                log('not all cases are proved: nothing assembled')
                sys.exit(1)
            P = prover(S, max_rec=0, guide=False, oracle=False, wide_sub=False, absorb=False, subsume=False)
            res, fid = P.prove(statement)
            log(f'{statement}: {"PROVED" if res == "NO" else res} fact {fid}')
            sys.exit(0 if res == 'NO' else 1)
        return
    W, w = int(args[2]), int(args[3])
    cdir = os.path.join(path, 'claims', statement.replace(':', '_').replace(',', '_'))
    os.makedirs(cdir, exist_ok=True)
    mine = range(w, len(cs), W) if only is None else [int(i) for i in only.split(',')]
    for i in mine:
        L2, X = cs[i]
        claim = os.path.join(cdir, f'case-{i}')
        try:
            os.close(os.open(claim, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
        except FileExistsError:
            continue
        S.refresh()
        t0 = time.time()
        log(f'case {i}: |L2|={len(L2)} |X|={len(X)}')
        res, why = prove_case(S, n, a, L1, tuple(L2), X, t, caps,
                              {'root': a_root, 'child': a_child, 'sat': a_sat}, log)
        log(f'case {i}: {res} -- {why} ({time.time() - t0:.0f}s)')
        if res == 'YES':
            with open(os.path.join(path, 'COUNTEREXAMPLES.jsonl'), 'a') as f:
                f.write(json.dumps({'statement': statement, 'case': i, 'prefix': [[list(c) for c in L] for L in why]}) + '\n')
            log('!!! a child completes to a sorting network: the statement is FALSE; stopping')
            sys.exit(3)
        if res != 'NO':
            os.remove(claim)                 # leave it for a later run
    log('worker done')


if __name__ == '__main__':
    main()
