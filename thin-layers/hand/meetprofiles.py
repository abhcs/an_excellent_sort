"""Meet profiles (efficient-prefixes.md section 7.6): least sizes a_p, b_p of the nine prefix channels, the
order relations f_p <= f_q, and the two meet graphs (p ~ q when some shortest terms, resp. shortest clauses,
of p and q intersect).  The 'meet' gain rule reads nothing else.  A profile Q dominates P if a channel
bijection makes a, b of Q at most those of P and every order relation and every meet of P present in Q; then
every rule-based bound of Q is at most that of P, so a certificate for P also proves Q.
usage: meetprofiles.py EXC.json KEY OUT.json"""
import json, sys, itertools
sys.path[:0] = ['.']
import gainrules as gr
N = gr.N


def profile(pre):
    tabs = gr.channel_tables(pre)
    top = gr.Side(tabs); bot = gr.Side([gr.dual(t) for t in tabs])
    le = [[int(p != q and gr.leq(tabs[p], tabs[q])) for q in range(N)] for p in range(N)]
    mt = [[int(p != q and any(T & U for T in top.mins((p,)) for U in top.mins((q,)))) for q in range(N)] for p in range(N)]
    mc = [[int(p != q and any(T & U for T in bot.mins((p,)) for U in bot.mins((q,)))) for q in range(N)] for p in range(N)]
    return top.a, bot.a, le, mt, mc


def complement(pr):
    a, b, le, mt, mc = pr
    return b, a, [[le[q][p] for q in range(N)] for p in range(N)], mc, mt


def key(pr, s):
    a, b, le, mt, mc = pr
    return (tuple(a[p] for p in s), tuple(b[p] for p in s), tuple(le[s[i]][s[j]] for i in range(N) for j in range(N)),
            tuple(mt[s[i]][s[j]] for i in range(N) for j in range(N)), tuple(mc[s[i]][s[j]] for i in range(N) for j in range(N)))


def canon(pr):
    a, b, le, mt, mc = pr
    inv = [(a[p], b[p], tuple(sorted((le[p][q], le[q][p], mt[p][q], mc[p][q], a[q], b[q]) for q in range(N) if q != p))) for p in range(N)]
    order = sorted(range(N), key=lambda p: inv[p])
    groups = [list(g) for _, g in itertools.groupby(order, key=lambda p: inv[p])]
    return min(key(pr, [p for g in perms for p in g]) for perms in itertools.product(*[itertools.permutations(g) for g in groups]))


def unflat(k):
    a, b, le, mt, mc = k
    m = lambda f: [list(f[i * N:(i + 1) * N]) for i in range(N)]
    return list(a), list(b), m(le), m(mt), m(mc)


def dominates(Q, P):
    aQ, bQ, lQ, tQ, cQ = unflat(Q); aP, bP, lP, tP, cP = unflat(P)
    s = [None] * N; used = [False] * N

    def rec(p):
        if p == N:
            return True
        for q in range(N):
            if used[q] or aQ[q] > aP[p] or bQ[q] > bP[p]:
                continue
            if all((not lP[p][r] or lQ[q][s[r]]) and (not lP[r][p] or lQ[s[r]][q]) and (not tP[p][r] or tQ[q][s[r]])
                   and (not cP[p][r] or cQ[q][s[r]]) for r in range(p)):
                s[p] = q; used[q] = True
                if rec(p + 1):
                    return True
                used[q] = False
        return False
    return rec(0)


if __name__ == '__main__':
    d = json.load(open(sys.argv[1])); P = d[sys.argv[2]]
    rep, members = {}, {}
    for i, pre in enumerate(P):
        pr = profile(pre)
        k = min(canon(pr), canon(complement(pr)))
        rep.setdefault(k, i); members.setdefault(k, []).append(i)
    keys = list(rep)
    print(f'{len(P)} prefixes, {len(keys)} distinct meet profiles (up to relabelling and complement)')
    minimal = []
    for k in keys:
        # k is covered if it dominates another profile k2 (k2 at least as hard); ties broken by order
        covered = any(k2 != k and dominates(k, k2) and not (dominates(k2, k) and keys.index(k2) > keys.index(k)) for k2 in keys)
        if not covered:
            minimal.append(k)
    print(f'minimal meet profiles under dominance: {len(minimal)}; their representatives:', sorted(rep[k] for k in minimal))
    json.dump({'profiles': [{'rep': rep[k], 'members': members[k], 'minimal': k in minimal} for k in keys]}, open(sys.argv[3], 'w'))
