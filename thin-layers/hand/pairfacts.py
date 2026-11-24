"""How many pair facts does a 'pair'-rule certificate need?  A pair fact is the exact value J(p, q) (or K) of
an incomparable pair of prefix channels below the overlap-free sum a_p + a_q.  Greedily relax facts to the
overlap-free sum while sum(pi) > 12 stays.  usage: EXC.json KEY FIRST:LAST"""
import json, sys, os, random
os.environ.setdefault('KEEPRED', '1')
sys.path[:0] = ['.']
import gainrules as gr
d = json.load(open(sys.argv[1])); P = d[sys.argv[2]]
lo, hi = map(int, sys.argv[3].split(':'))
for idx in range(lo, min(hi, len(P))):
    pre = P[idx]; tabs = gr.channel_tables(pre)
    top = gr.Side(tabs); bot = gr.Side([gr.dual(t) for t in tabs])
    facts = []
    for side, S in (('J', top), ('K', bot)):
        for p in range(gr.N):
            for q in range(p + 1, gr.N):
                if gr.leq(S.t[p], S.t[q]) or gr.leq(S.t[q], S.t[p]):
                    continue
                e = S.exact((p, q))
                if e < S.a[p] + S.a[q]:
                    facts.append((side, p, q, e))
    def val(relaxed):
        top.override = {(p, q): top.a[p] + top.a[q] for (sd, p, q, e) in relaxed if sd == 'J'}
        bot.override = {(p, q): bot.a[p] + bot.a[q] for (sd, p, q, e) in relaxed if sd == 'K'}
        top.bound.cache_clear(); bot.bound.cache_clear()
        return gr.lp_value(pre, 'pair', sides=(top, bot))[0]
    v0 = val([])
    keep = list(facts); relaxed = []
    if v0 > 12 + 1e-6:
        random.seed(idx); order = facts[:]; random.shuffle(order)
        for f in order:
            if val(relaxed + [f]) > 12 + 1e-6:
                relaxed.append(f); keep.remove(f)
    print(idx, f'pair={v0:.3f} facts={len(facts)} needed={len(keep)}', ' '.join(f'{s}{p}{q}={e}' for s, p, q, e in keep), flush=True)
