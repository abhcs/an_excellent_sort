#!/usr/bin/env python3
"""ss_cases.py SS:n,d,a,3 FACTS_DIR W K [flags]: prove the second-layer cases of a sparse-start
statement SS(n, d, a, 3) into the fact store, as s11_cases.py does for S11, for any statement whose
second-layer classes are listed in results/l2classes_{n}_{a}.json (l2classes.py; the cover is
checked by verify_cover.py).

A case is the node (L1, L2) with L1 the middle layer of that file and L2 one class representative:
d - 2 layers left, the third layer capped at a. Every legal second layer is the image of one
representative under a symmetry of L1 (and duality when L1 is self-dual), so its node has the same
answer up to relabeling and complement, which is how the prover's store identifies nodes. Cases
run from the smallest output set up. With W = 1, K = 'list' it only prints the cases.

Flags as in s11_cases.py: --oracle, --guide, --share, --wide-sub, --progress, --only A-B or I,J,...,
--help I,J,... (prove these cases without claiming them, largest split child first), and
--opt k=v,... for the prover's cost options (fast_n, symmetry, aut_max, qcover_max_n, oracle_max_n,
guide_big_n, guide_big_seconds, guide_seconds, guide_max, absorb_max_n; README §8.11; store_first_n,
store_first_big, guide_skip_n, guide_conflicts; README §8.13).
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sentinel_prover as sp
import sprove


def cases(n, a):
    d = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results',
                                    f'l2classes_{n}_{a}.json')))
    assert d['n'] == n and d['a'] == a
    L1 = tuple(tuple(p) for p in d['L1'])
    X1 = sp.outputs(n, (L1,))
    out = []
    for r in d['reps']:
        L2 = tuple(tuple(p) for p in r)
        Y = frozenset(sp.apply_layer(L2, x) for x in X1)
        out.append((L2, Y))
    out.sort(key=lambda c: (len(c[1]), c[0]))
    return L1, out


def main():
    flags = ('--oracle', '--progress', '--guide', '--share', '--wide-sub')
    helpcases = only = None
    opts = {}
    if '--opt' in sys.argv:
        k = sys.argv.index('--opt')
        for kv in sys.argv[k + 1].split(','):
            key, val = kv.split('=')
            assert key in ('fast_n', 'symmetry', 'aut_max', 'qcover_max_n', 'oracle_max_n', 'guide_big_n',
                           'guide_big_seconds', 'guide_seconds', 'guide_max', 'absorb_max_n', 'store_first_n',
                           'store_first_big', 'guide_skip_n', 'guide_conflicts'), key
            opts[key] = float(val) if '.' in val else int(val)
        del sys.argv[k:k + 2]
    if '--help' in sys.argv:
        k = sys.argv.index('--help')
        helpcases = [int(v) for v in sys.argv[k + 1].split(',')]
        del sys.argv[k:k + 2]
    if '--only' in sys.argv:
        k = sys.argv.index('--only')
        spec = sys.argv[k + 1]
        only = set(range(int(spec.split('-')[0]), int(spec.split('-')[1]) + 1)) if '-' in spec \
            else {int(v) for v in spec.split(',')}
        del sys.argv[k:k + 2]
    sys.argv = [x for x in sys.argv if x not in flags] + [x for x in sys.argv if x in flags]
    statement, path, W = sys.argv[1], sys.argv[2], int(sys.argv[3])
    kind, args = statement.split(':')
    n, dd, a, m = map(int, args.split(','))
    assert kind == 'SS' and m == 3, 'only SS(n, d, a, 3)'
    t = dd - 2
    L1, cs = cases(n, a)
    if sys.argv[4] == 'list':
        print(len(cs), 'cases; output-set sizes', [len(Y) for _, Y in cs[:5]], '...', [len(Y) for _, Y in cs[-3:]])
        return
    K = int(sys.argv[4])
    log = lambda s: print(time.strftime('%H:%M:%S'), s, flush=True)
    share = '--share' in sys.argv
    store = sprove.Store(path, compact=share, x_cap=40000 if share else 0)
    P = sprove.Prover(store, log=log if '--progress' in sys.argv else None, oracle='--oracle' in sys.argv,
                      guide='--guide' in sys.argv, share_seconds=60 if share else 0,
                      reverse=helpcases is not None, wide_sub='--wide-sub' in sys.argv, **opts)
    mine = helpcases if helpcases is not None else range(len(cs)) if share else range(K, len(cs), W)
    log(f'{statement} worker {K}/{W}: loaded {store.loaded} facts; {len(cs)} cases, mine: '
        f'{"the next unclaimed" if share else len(mine)}')
    if share:
        os.makedirs(os.path.join(path, 'claims'), exist_ok=True)
    caps = sp.norm_caps(n, t, (a,))
    for i in mine:
        if only is not None and i not in only:
            continue
        if share and helpcases is None:
            try:
                os.close(os.open(os.path.join(path, 'claims', f'case-{i}'), os.O_CREAT | os.O_EXCL | os.O_WRONLY))
            except FileExistsError:
                continue
        L2, Y = cs[i]
        t0 = time.time()
        res, fid = P.ext(n, (L1, L2), t, Y, caps)
        log(f'case {i}: {res} ({time.time() - t0:.0f}s) |X|={len(Y)} layer {list(L2)} fact {fid} '
            f'nodes {P.stats["nodes"]}')


if __name__ == '__main__':
    main()
