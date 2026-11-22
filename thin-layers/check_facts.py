#!/usr/bin/env python3
"""check_facts.py FACTS_DIR [STATEMENT...]: check, from definitions, the NO facts of a fact store
that the given statements (default: all recorded statements) depend on.

The checker trusts nothing in the store but the prefixes: every output set is recomputed, every
sentinel residual is simulated with real +-infinity values, every identification of two output
sets is confirmed by an explicit permutation search (check_sentinel_proof.equivalent), and every
split / absorb step re-enumerates all next layers (except those that an automorphism listed in
the step, verified here, maps to a smaller layer).  A child may be a fact with MORE remaining
layers and LOOSER caps than needed (no completion with more room implies none with less).
D(r) used by quick steps and SS(r,d,a,m) used by lemma steps must be recorded statements whose
facts have the right root and are themselves checked.  A lemma step may schedule the residual as
soon as possible, as late as possible, or in its own prefix layers ('asis', README §8.15).
A 'sat' step (satcert.py) is checked by regenerating the node's CNF from its prefix and comparing
its sha256 with the step; the refutation itself is accepted from a drat-trim verdict recorded in
FACTS_DIR/sat_certs.jsonl, or, with --resat, re-solved by CaDiCaL and re-checked by drat-trim (as
costly as the original run).  Verified facts are cached in
FACTS_DIR/verified.txt (id and sha256 of the fact line) so later runs check only new facts.
--jobs N checks with N forked processes (each fact is checked on its own).
"""
import hashlib, json, multiprocessing, os, sys
import check_sentinel_proof as C


def dup():
    return {1: 0, 2: 1, 3: 3, 4: 3, 5: 5, 6: 5, 7: 6, 8: 6, 9: 7, 10: 7, 11: 8, 12: 8}


def first_layer(n):
    return [[2 * k, 2 * k + 1] for k in range(n // 2)]


def root_of(st):
    kind, args = st.split(':')
    if kind == 'D':
        n = int(args)
        return n, [first_layer(n)], dup()[n] - 2, (), dup()[n]
    n, d, a, m = map(int, args.split(','))
    return n, [[[2 * k, 2 * k + 1] for k in range(a)]], d - 1, C.norm_caps(n, d - 1, (a,) * (m - 1)), (d, a, m)


def caps_le(n, t, small, big):
    for i in range(t):
        s = small[i] if i < len(small) else n // 2
        b = big[i] if i < len(big) else n // 2
        if s > b:
            return False
    return True


def asis_counts(n, layers, S):
    """Real-real comparisons per layer with the sentinels S simulated (+inf to max ends, -inf to
    min ends); the residual kept in its own layers.  Independent of sprove.asis_sizes."""
    cont = {c: (S[c] if c in S else 'r') for c in range(n)}
    out = []
    for L in layers:
        k = 0
        for i, j in L:
            a, b = cont[i], cont[j]
            if a == 'r' and b == 'r':
                k += 1
            elif a == '+' and b == 'r':
                cont[i], cont[j] = 'r', '+'
            elif a == 'r' and b == '-':
                cont[i], cont[j] = '-', 'r'
            elif a == '+' and b == '-':
                cont[i], cont[j] = '-', '+'
        out.append(k)
    return out


def sig(X, n):
    mask = (1 << n) - 1
    best = None
    for Y in (X, frozenset(x ^ mask for x in X)):
        prof = []
        for i in range(n):
            c = [0] * (n + 1)
            for y in Y:
                if (y >> i) & 1:
                    c[bin(y).count('1')] += 1
            prof.append(tuple(c))
        k = (len(Y), tuple(sorted(prof)))
        best = k if best is None or k < best else best
    return best


_CHECK = None


def _check_chunk(fids):
    return [(fid, _CHECK(fid)) for fid in fids]


def main():
    jobs = 1
    if '--jobs' in sys.argv:               # --jobs N: check with N forked processes
        k = sys.argv.index('--jobs')
        jobs = int(sys.argv[k + 1])
        del sys.argv[k:k + 2]
    resat = '--resat' in sys.argv
    sys.argv = [a for a in sys.argv if a != '--resat']
    path = sys.argv[1]
    import satcert
    certified = {r['cnf_sha256'] for r in satcert.load_records(path).values()
                 if r.get('result') == 'UNSAT' and r.get('drat') == 'VERIFIED'}
    facts, lines = {}, {}
    for fn in sorted(os.listdir(path)):
        if fn.startswith('facts-') and fn.endswith('.jsonl'):
            for line in open(os.path.join(path, fn)):
                if line.strip():
                    f = json.loads(line)
                    facts[f['id']] = f
                    lines[f['id']] = hashlib.sha256(line.strip().encode()).hexdigest()
    stmts = {}
    for line in open(os.path.join(path, 'statements.jsonl')):
        if line.strip():
            s = json.loads(line)
            stmts[s['statement']] = s['fact']
    want = [a for a in sys.argv[2:]] or list(stmts)
    verified = {}
    vpath = os.path.join(path, 'verified.txt')
    if os.path.exists(vpath):
        for line in open(vpath):
            fid, h = line.split()
            verified[fid] = h
    bad = []
    # statements: right root, NO
    dlow, lem = {1: 0, 2: 1}, {}
    for st, fid in stmts.items():
        f = facts.get(fid)
        n, pre, t, caps, extra = root_of(st)
        # the statement's fact may be any NO fact at least as strong: equivalent outputs, at least
        # as many remaining layers, caps at least as loose
        ok = (f is not None and f['res'] == 'NO' and f['n'] == n and f['t'] >= t
              and caps_le(n, t, tuple(caps), tuple(f['caps']))
              and C.equivalent(C.out01(n, [[tuple(c) for c in L] for L in pre]),
                               C.out01(n, [[tuple(c) for c in L] for L in f['prefix']]), n))
        if not ok:
            bad.append(('statement', st))
            print('FAILED statement', st, flush=True)
            continue
        if st.startswith('D:'):
            dlow[n] = max(dlow.get(n, 0), extra)
        else:
            lem[fid] = (n,) + extra
    # facts needed
    need, stack = set(), [stmts[s] for s in want if s in stmts]
    # FACT:<id> checks one fact (e.g. a single node proved with sprove.py --node) and what it uses
    for a in want:
        if a.startswith('FACT:'):
            f = facts.get(a[5:])
            if f is None or f['res'] != 'NO':
                bad.append(('fact', a[5:], None))
                print('FAILED: no NO fact', a[5:], flush=True)
                continue
            print(f'{a}: claims no {f["t"]}-layer completion of n={f["n"]} prefix={json.dumps(f["prefix"])} '
                  f'caps={f["caps"]}', flush=True)
            stack.append(a[5:])
    def walk(stack):
        while stack:
            fid = stack.pop()
            if fid in need:
                continue
            need.add(fid)
            st = facts[fid].get('step', {})
            for key in ('child', 'lemma', 'of'):
                if key in st:
                    stack.append(st[key])
            stack.extend(st.get('children', []))
            stack.extend(tr['node'] for tr in st.get('tracks', []))
            stack.extend(cv['node'] for cv in st.get('covers', []))
            stack.extend(q['fact'] for q in st.get('qcovers', []) if 'fact' in q)
    walk(stack)
    # quick steps (D(r)) and the sentinel covers of splits (D(r) and every recorded SS lemma) rest on
    # recorded statements without naming their facts: then every recorded statement is checked too
    if any(facts[fid].get('step', {}).get('rule') == 'quick'
           or any('fact' not in q for q in facts[fid].get('step', {}).get('qcovers', [])) for fid in need):
        walk(list(stmts.values()))
    outs = {}

    def out(fid):
        if fid not in outs:
            if len(outs) > 30000:              # bounded: output sets are recomputed when needed
                outs.clear()
            f = facts[fid]
            outs[fid] = C.out01(f['n'], [[tuple(c) for c in L] for L in f['prefix']])
        return outs[fid]

    todo = [fid for fid in need if verified.get(fid) != lines[fid]
            or (resat and facts[fid].get('step', {}).get('rule') == 'sat')]
    nsat = sum(1 for fid in need if facts[fid].get('step', {}).get('rule') == 'sat')
    if nsat:
        print(f'{nsat} needed facts rest on SAT certificates ({"re-solved and re-checked" if resat else "drat-trim verdicts recorded in sat_certs.jsonl"})', flush=True)
    print(f'{len(facts)} facts, {len(need)} needed by {len(want)} statements, {len(todo)} to check', flush=True)
    newly = []

    def check_one(fid):
        f = facts[fid]
        n, t, caps = f['n'], f['t'], tuple(f['caps'])
        P = [[tuple(c) for c in L] for L in f['prefix']]
        X = out(fid)
        st = f.get('step')
        ok = f['res'] == 'NO' and st is not None and t >= 1 and not all(C.is_sorted(x, n) for x in X)
        if ok and st['rule'] in ('quick', 'lemma', 'sent'):
            S = {int(c): v for c, v in st['S'].items()}
            r, Z, h, asap, alap = C.sentinel_run(n, P, S, with_Z=st['rule'] == 'sent')
            if st['rule'] == 'quick':
                ok = r == st['r'] and h == st['h'] and r in dlow and h + t < dlow[r]
            elif st['rule'] == 'lemma' and st['sched'] == 'asis':
                d2, a2, m2 = st['ss']
                L = lem.get(st['lemma'])
                Lp = len(P)
                A = asis_counts(n, P, S)
                capsr = C.norm_caps(r, t, caps)
                sizes = [A[i] if i < Lp else (capsr[i - Lp] if i - Lp < len(capsr) else r // 2) for i in range(m2)]
                ok = (L == (r, d2, a2, m2) and r == st['r'] and st['h'] == Lp and Lp + t <= d2
                      and all(x <= a2 for x in sizes))
            elif st['rule'] == 'lemma':
                d2, a2, m2 = st['ss']
                L = lem.get(st['lemma'])
                prof = asap if st['sched'] == 'asap' else alap
                capsr = C.norm_caps(r, t, caps)
                sizes = [prof[i] if i < h else (capsr[i - h] if i - h < len(capsr) else r // 2) for i in range(m2)]
                ok = (L == (r, d2, a2, m2) and r == st['r'] and h == st['h'] and h + t <= d2
                      and all(x <= a2 for x in sizes))
            else:
                c = facts.get(st['child'])
                ok = (c is not None and c['res'] == 'NO' and c['n'] == r and c['t'] >= t
                      and caps_le(r, t, C.norm_caps(r, t, caps), tuple(c['caps']))
                      and C.equivalent(Z, out(c['id']), r))
        elif ok and st['rule'] == 'sat':
            text, sha, _ = satcert.node_cnf(n, P, t, caps)
            ok = st.get('enc') == satcert.ENC and sha == st.get('cnf_sha256')
            if ok and resat:
                rec = satcert.certify(n, P, t, caps)
                ok = rec['cnf_sha256'] == sha and rec['result'] == 'UNSAT' and rec.get('drat') == 'VERIFIED'
            elif ok:
                ok = sha in certified
        elif ok and st['rule'] == 'sub':
            F = facts.get(st['of'])
            ok = (F is not None and F['res'] == 'NO' and F['n'] == n and F['t'] >= t
                  and caps_le(n, t, caps, tuple(F['caps'])))
            if ok:
                mask = (1 << n) - 1
                A = out(F['id'])
                if st['comp']:
                    A = frozenset(a ^ mask for a in A)
                sigma = st['sigma']
                ok = sorted(sigma) == list(range(n)) and all(
                    sum(((a >> i) & 1) << sigma[i] for i in range(n)) in X for a in A)
        elif ok and st['rule'] in ('split', 'absorb'):
            cap0 = caps[0] if caps else n // 2
            rest = C.norm_caps(n, t - 1, caps[1:])
            covs = []                                  # (positions, a) of verified cover facts
            legacy = [dict(tr, pos=[tr['pos']], a=1) for tr in st.get('tracks', [])]
            for cv in st.get('covers', []) + legacy:
                S = {int(c): v for c, v in cv['S'].items()}
                BIG = 10 ** 6
                vals = [(BIG if S[c] == '+' else -BIG) if c in S else 0 for c in range(n)]
                occ = sorted(c for c, v in enumerate(C.run(P, vals)) if abs(v) >= BIG)
                r, Z, h, _, _ = C.sentinel_run(n, P, S)
                nd = facts.get(cv['node'])
                a = cv['a']
                capr = C.norm_caps(r, t, (cap0 - a,) + tuple(caps[1:]))
                if not (occ == sorted(cv['pos']) and a >= 1 and nd is not None and nd['res'] == 'NO'
                        and nd['n'] == r and nd['t'] >= t and caps_le(r, t, capr, tuple(nd['caps']))
                        and C.equivalent(Z, out(nd['id']), r)):
                    ok = False
                    break
                covs.append((set(occ), a))
            qsets = [{int(c): v for c, v in q['S'].items()} for q in st.get('qcovers', []) if 'fact' not in q]
            ssets = [({int(c): v for c, v in q['S'].items()}, q['fact']) for q in st.get('qcovers', []) if 'fact' in q]

            def sent_ok(n2, P2, t2, caps2, S2, fid2):
                F2 = facts.get(fid2)
                r2, Z2, h2, _, _ = C.sentinel_run(n2, P2, S2)
                return (F2 is not None and F2['res'] == 'NO' and F2['n'] == r2 and F2['t'] >= t2
                        and caps_le(r2, t2, C.norm_caps(r2, t2, caps2), tuple(F2['caps']))
                        and len(Z2) == len(out(fid2)) and sig(Z2, r2) == sig(out(fid2), r2)
                        and C.equivalent(Z2, out(fid2), r2))

            def leaf_ok(n2, P2, t2, caps2, S2):
                r2, Z2, h2, asap2, alap2 = C.sentinel_run(n2, P2, S2, with_Z=False)   # Z unused here
                if r2 in dlow and h2 + t2 < dlow[r2]:
                    return True
                capsr2 = C.norm_caps(r2, t2, caps2)
                A2, Lp2 = None, len(P2)
                for (rl, d2, a2, m2) in lem.values():
                    if rl != r2 or h2 + t2 > d2:
                        continue
                    for prof in (asap2, alap2):
                        sizes = [prof[i] if i < h2 else (capsr2[i - h2] if i - h2 < len(capsr2) else r2 // 2) for i in range(m2)]
                        if all(x <= a2 for x in sizes):
                            return True
                    if Lp2 + t2 <= d2:                 # the residual in its own layers
                        if A2 is None:
                            A2 = asis_counts(n2, P2, S2)
                        sizes = [A2[i] if i < Lp2 else (capsr2[i - Lp2] if i - Lp2 < len(capsr2) else r2 // 2)
                                 for i in range(m2)]
                        if all(x <= a2 for x in sizes):
                            return True
                return False
            pool = {}
            for cid in st['children']:
                c = facts.get(cid)
                if c is None or c['res'] != 'NO' or c['n'] != n or c['t'] < t - 1 \
                        or not caps_le(n, t - 1, rest, tuple(c['caps'])):
                    continue
                pool.setdefault(sig(out(cid), n), []).append(cid)
            nonred = [(i, j) for i in range(n) for j in range(i + 1, n)
                      if any((x >> i) & 1 and not (x >> j) & 1 for x in X)]
            layers = [()]
            def gen(start, used, cur):
                if cur:
                    layers.append(tuple(cur))
                if len(cur) == cap0:
                    return
                for idx in range(start, len(nonred)):
                    i, j = nonred[idx]
                    if used >> i & 1 or used >> j & 1:
                        continue
                    cur.append((i, j))
                    gen(idx + 1, used | (1 << i) | (1 << j), cur)
                    cur.pop()
            if ok:
                gen(0, 0, [])
            # A next layer L is closed if a cover fact covers it, or its child (outputs Y) is a listed
            # child, or a listed sentinel set closes the child, or reduces it to a listed fact. Any
            # one suffices, so the order of the tests only affects speed: the cheap ones first, and
            # a sentinel set that worked moves to the front of its list. The child depends only on
            # Y, so a layer whose Y was already closed is closed too.
            seen = set()
            capsq = C.norm_caps(n, t - 1, caps[1:])
            # Symmetry ('aut'): relabelings g (a channel permutation, applied after complementing if
            # flagged) with g(X) = X. For a next layer L, g(L) standardized (each comparator (i, j)
            # becomes (min, max) of (g(i), g(j))) is a layer whose child is a relabeling (and, for a
            # complementing g, the complement) of L's child, so both children have the same answer.
            # A layer that some listed g maps to a lexicographically smaller layer is therefore
            # skipped. Each g must also map the non-redundant pairs onto themselves (true whenever X
            # holds the sorted vectors, as every prefix output set does), so the images of the
            # enumerated layers are enumerated layers; the least layer of each orbit under the
            # listed g's is then enumerated and not skipped, and it is checked.
            auts = []
            mask = (1 << n) - 1
            nonred_set = set(nonred)
            for g in (st.get('aut') or []) if ok else []:
                perm, comp = g
                if sorted(perm) != list(range(n)) or len(perm) != n:
                    ok = False
                    break
                img = frozenset(sum(((x ^ (mask if comp else 0)) >> i & 1) << perm[i] for i in range(n)) for x in X)
                if img != X or {tuple(sorted((perm[i], perm[j]))) for i, j in nonred} != nonred_set:
                    ok = False
                    break
                auts.append(perm)

            def smaller_image(L):
                key = tuple(sorted(tuple(sorted(c)) for c in L))
                return any(tuple(sorted(tuple(sorted((p[i], p[j]))) for i, j in L)) < key for p in auts)

            def first(lst, test):
                for k, e in enumerate(lst):
                    if test(e):
                        if k:
                            lst.insert(0, lst.pop(k))
                        return True
                return False
            for L in layers if ok else []:
                if auts and L and smaller_image(L):
                    continue                          # a listed automorphism maps L to a smaller layer
                if any(sum(1 for i, j in L if i in ps or j in ps) >= a for ps, a in covs):
                    continue                          # covered by a cover fact
                Y = frozenset(sum(b << i for i, b in enumerate(C.run([L], [(x >> i) & 1 for i in range(n)]))) for x in X)
                if Y in seen:
                    continue
                if t - 1 == 0:
                    good = not all(C.is_sorted(y, n) for y in Y)
                else:
                    good = any(C.equivalent(Y, out(cid), n) for cid in pool.get(sig(Y, n), ()))
                if not good and qsets:                # closed by a listed sentinel set
                    good = first(qsets, lambda S2: leaf_ok(n, P + [list(L)], t - 1, capsq, S2))
                if not good and ssets:                # reduced by listed sentinels to a listed fact
                    good = first(ssets, lambda e: sent_ok(n, P + [list(L)], t - 1, caps[1:], e[0], e[1]))
                if not good:
                    ok = False
                    break
                seen.add(Y)
        elif ok:
            ok = False
        return ok

    order = sorted(todo, key=lambda i: (facts[i]['n'], facts[i]['t']), reverse=jobs > 1)
    if jobs > 1:                           # facts are checked independently: fork workers,
                                           # the largest nodes first so that the slow ones overlap
        global _CHECK
        _CHECK = check_one
        for fid in [f for f in facts if f not in need]:
            del facts[fid]                 # every fact a check reads is in `need`; keep forks small
        import gc
        gc.collect()
        gc.freeze()
        pool = multiprocessing.get_context('fork').Pool(jobs)
        chunks = [order[i:i + 100] for i in range(0, len(order), 100)]
        results = (r for part in pool.imap_unordered(_check_chunk, chunks) for r in part)
    else:
        results = ((fid, check_one(fid)) for fid in order)
    vf = open(vpath, 'a')                  # verified facts are recorded as they come: a stopped
    for k, (fid, ok) in enumerate(results):  # check resumes where it was
        if ok:
            newly.append(fid)
            vf.write(f'{fid} {lines[fid]}\n')
            if len(newly) % 1000 == 0:
                vf.flush()
        else:
            st = facts[fid].get('step')
            bad.append(('fact', fid, st['rule'] if st else None))
            print('FAILED', fid, st['rule'] if st else None, flush=True)
        if (k + 1) % 5000 == 0:
            print(f'  {k + 1}/{len(todo)} checked, {len(bad)} failed', flush=True)
    vf.close()
    print(f'{len(need)} facts needed, {len(newly)} newly verified, {len(bad)} failed')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
