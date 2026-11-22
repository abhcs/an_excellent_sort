#!/usr/bin/env python3
"""proof_shape.py -- where a stored sentinel proof spends its facts, and how much smaller it could be
(README §8.10).

usage: proof_shape.py FACTS_DIR STATEMENT [--families]

Reads the facts the statement's proof needs (the closure of its recorded fact) and prints
  * the profile: facts by (channels, layers left, rule), and how often each lemma is used;
  * compaction estimates, all with the existing rules (nothing is rewritten):
      merge  -- splits with equivalent output sets (same channels, layers, caps) proved more than
                once count once;
      sub    -- a split whose output set contains a relabeled copy of another needed split's
                (same channels, layers, caps) becomes a one-fact subsumption;
      fold   -- a split child closed by a leaf rule (height bound or lemma), directly or after one
                sentinel step, is listed in its parent's sentinel covers instead of being a fact
                (only for children that no other step uses);
  * with --families: the 'family lemma' test on the splits with at least 5 layers left: their block
    structure (components of the prefix's comparator graph), and for each distinct one any stored
    NO fact (any rule; same channels, at least as many layers left, caps no tighter, not
    equivalent) whose output set or its complement embeds into it after a relabeling. Such a fact
    implies the split by subsumption, the way a lemma proved once for a family would.
Run with the venv python.
"""
import collections, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sentinel_prover as sp
from sprove import caps_le, embeds_py, inv_hash, profiles


def load(path):
    refs, info, pre = {}, {}, {}
    for fn in os.listdir(path):
        if fn.startswith('facts-') and fn.endswith('.jsonl'):
            for line in open(os.path.join(path, fn)):
                if not line.strip():
                    continue
                f = json.loads(line)
                st = f.get('step') or {}
                fid = f['id']
                info[fid] = (f['n'], f['t'], tuple(f['caps']), f['res'], st.get('rule'), st.get('lemma'),
                             frozenset(st.get('children', [])), len(st.get('children', [])) + len(st.get('qcovers', [])))
                r = [st[k] for k in ('child', 'lemma', 'of') if k in st] + st.get('children', []) \
                    + [cv['node'] for cv in st.get('covers', [])] + [q['fact'] for q in st.get('qcovers', []) if 'fact' in q]
                if r:
                    refs[fid] = r
                if f['res'] == 'NO' and (st.get('rule') in ('split', 'absorb') or f['t'] >= 4):
                    pre[fid] = tuple(tuple(tuple(c) for c in L) for L in f['prefix'])
    return refs, info, pre


def closure(root, refs, redirect=None, subbed=None, fold=None):
    redirect, subbed, fold = redirect or {}, subbed or {}, fold or set()
    seen, stack = set(), [root]
    while stack:
        f = stack.pop()
        f = redirect.get(f, f)
        if f in seen or f in fold:
            continue
        seen.add(f)
        stack.extend([subbed[f]] if f in subbed else refs.get(f, ()))
    return seen


def main():
    path, statement = sys.argv[1], sys.argv[2]
    t0 = time.time()
    stmts = {}
    for line in open(os.path.join(path, 'statements.jsonl')):
        if line.strip():
            s = json.loads(line)
            stmts[s['statement']] = s['fact']
    name_of = {v: k for k, v in stmts.items()}
    refs, info, pre = load(path)
    root = stmts[statement]
    need = closure(root, refs)
    print(f'{statement}: proof needs {len(need)} of {len(info)} stored facts ({time.time() - t0:.0f}s)')
    rule = {f: info[f][4] for f in info}
    # profile
    by = collections.Counter((info[f][0], info[f][1], rule[f]) for f in need)
    print('  largest groups (channels, layers left, rule):',
          ', '.join(f'({n},{t},{r}) {c}' for (n, t, r), c in by.most_common(8)))
    lem = collections.Counter(name_of.get(info[f][5], info[f][5]) for f in need if rule[f] == 'lemma')
    print('  lemma uses:', ', '.join(f'{k} {v}' for k, v in lem.most_common()))
    # compaction
    splits = [f for f in need if rule[f] in ('split', 'absorb')]
    X = {f: sp.outputs(info[f][0], pre[f]) for f in splits}
    groups = collections.defaultdict(list)
    for f in splits:
        groups[info[f][:3] + (inv_hash(X[f], info[f][0]),)].append(f)
    redirect, reps = {}, []
    for key, fs in groups.items():
        rs = []
        for f in fs:
            r = next((r for r in rs if sp.equivalent(X[r], X[f], key[0])), None)
            if r is None:
                rs.append(f)
            else:
                redirect[f] = r
        reps += rs
    prof, comp = {}, {}

    def pr(f):
        if f not in prof:
            n = info[f][0]
            Xs = X[f] if f in X else sp.outputs(n, pre[f])
            X[f] = Xs
            Xc = frozenset(x ^ ((1 << n) - 1) for x in Xs)
            prof[f], comp[f] = profiles(Xs, n), (Xc, profiles(Xc, n))
        return prof[f]

    def embeds(a, b):
        """out(a) or its complement embeds into out(b) after a relabeling"""
        n = info[b][0]
        pb = pr(b)
        for A, pa in ((X[a], pr(a)), comp[a]):
            if any(pa[0][k] > pb[0][k] for k in range(n + 1)):
                continue
            if embeds_py(A, X[b], n, pa, pb) is not None:
                return True
        return False
    subbed = {}
    byk = collections.defaultdict(list)
    for f in reps:
        byk[info[f][:3]].append(f)
    for key, fs in byk.items():
        order = sorted(fs, key=lambda f: len(X[f]))
        for b in order:
            for a in order:
                if a == b or a in subbed or len(X[a]) > len(X[b]) or (len(X[a]) == len(X[b]) and a > b):
                    continue
                if embeds(a, b):
                    subbed[b] = a
                    break
    parents = collections.defaultdict(set)
    for p in need:
        for c in refs.get(p, ()):
            parents[c].add(p)
    leaf = lambda f: rule.get(f) in ('quick', 'lemma')
    fold = {f for f in need if (leaf(f) or (rule[f] == 'sent' and refs.get(f) and leaf(refs[f][0])))
            and parents.get(f) and all(f in info[p][6] for p in parents[f])}

    def report(label, **kw):
        s = closure(root, refs, **kw)
        sub = kw.get('subbed') or {}
        nsplit = sum(1 for f in s if rule[f] in ('split', 'absorb') and f not in sub)
        print(f'  {label}: {len(s)} facts, {nsplit} splits')
    print(f'compaction with the existing rules ({time.time() - t0:.0f}s):')
    report('as stored')
    report('merge', redirect=redirect)
    report('merge + sub', redirect=redirect, subbed=subbed)
    report('merge + sub + fold', redirect=redirect, subbed=subbed, fold=fold)
    if '--families' not in sys.argv:
        return
    # family test on the splits with >= 5 layers left
    big = [f for f in reps if info[f][1] >= 5]

    def blocks(n, P):
        par = list(range(n))

        def find(a):
            while par[a] != a:
                par[a] = par[par[a]]
                a = par[a]
            return a
        for L in P:
            for i, j in L:
                par[find(i)] = find(j)
        g = collections.defaultdict(list)
        for c in range(n):
            g[find(c)].append(c)
        return list(g.values())

    def block_key(G, Xs):
        pats = {tuple((x >> c) & 1 for c in G) for x in Xs}
        rel = {(a, b) for a in G for b in G if a != b and all(((x >> a) & 1) <= ((x >> b) & 1) for x in Xs)}
        hasse = {(a, b) for a, b in rel if not any((a, c) in rel and (c, b) in rel for c in G if c not in (a, b))}
        deg = sorted((sum(1 for a, b in hasse if b == c), sum(1 for a, b in hasse if a == c)) for c in G)
        return (len(G), len(pats), min(tuple(deg), tuple(sorted((o, i) for i, o in deg))))
    fam = {}
    for f in big:
        n = info[f][0]
        Gs = blocks(n, pre[f])
        fam[f] = (info[f][:2], tuple(sorted(block_key(G, X[f]) for G in Gs if len(G) > 1)),
                  sum(1 for G in Gs if len(G) == 1))
    fc = collections.Counter(fam.values())
    multi = sum(1 for v in fam.values() if len(v[1]) > 1)
    print(f'families of the {len(big)} distinct splits with >= 5 layers left: {len(fc)} '
          f'(largest {fc.most_common(1)[0][1]}); {multi} are products of two or more blocks of size > 1')
    cand = collections.defaultdict(list)
    for f, v in info.items():
        if v[3] == 'NO' and f in pre and v[1] >= 5:
            cand[v[0]].append(f)
    covers = {}
    for b in sorted(big, key=lambda f: -info[f][7]):
        n, t, caps = info[b][:3]
        found = None
        for c in cand[n]:
            cn, ct, ccaps = info[c][:3]
            if c == b or ct < t or not caps_le(n, t, caps, ccaps):
                continue
            if c not in X:
                X[c] = sp.outputs(cn, pre[c])
            if len(X[c]) > len(X[b]) or (len(X[c]) == len(X[b]) and sp.equivalent(X[c], X[b], n)):
                continue
            if embeds(c, b):
                if found is None or (rule[found] in ('split', 'absorb') and rule[c] not in ('split', 'absorb')):
                    found = c
                if rule[c] not in ('split', 'absorb'):
                    break
        if found:
            covers[b] = found
    tot, hit = collections.Counter(), collections.Counter()
    for b in big:
        tot[info[b][:2]] += 1
        hit[info[b][:2]] += b in covers
    print(f'implied by another stored NO fact: {len(covers)} of {len(big)} ({time.time() - t0:.0f}s); '
          f'{sum(1 for c in covers.values() if rule[c] not in ("split", "absorb"))} by facts without a split')
    print('  by (channels, layers left):', ', '.join(f'{k} {hit[k]}/{tot[k]}' for k in sorted(tot)))
    sub2 = dict(subbed)
    for b, c in covers.items():
        sub2.setdefault(b, c)
    report('merge + sub + family cores', redirect=redirect, subbed=sub2)
    report('merge + sub + family cores + fold', redirect=redirect, subbed=sub2, fold=fold)


if __name__ == '__main__':
    main()
