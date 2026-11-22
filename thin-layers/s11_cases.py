#!/usr/bin/env python3
"""s11_cases.py FACTS_DIR W K [LIMIT_SECONDS]: prove the second-layer cases of S11 = SS(11,8,4,3)
numbered K, K+W, K+2W, ... into the fact store (W workers in parallel, each its own facts file).
The cases are the next layers of the S11 root (first layer (0,1),(2,3),(4,5),(6,7), at most four
comparators, non-redundant), deduplicated up to relabelling and complement exactly as the prover's
split does, in a fixed order.  `sprove.py FACTS_DIR SS:11,8,4,3` then finds every case in the
store.  With W = 1, K = 'list' it only prints the cases.  Flags: --oracle (skip extendable branches
by SAT), --guide (let SAT pick a residual without completion first; see sprove.py), --progress,
--share (workers read each other's new facts every minute, take the next unclaimed case from
FACTS_DIR/claims instead of every W-th one, and keep memory bounded: compact loaded facts, at most
40,000 cached output sets). --help I,J,...: prove only these cases, without claiming them, working
through every split from the largest child down (a helper for the workers on hard cases).
--wide-sub: the subsumption step looks at every stored NO fact, not only split facts.
--only A-B (or I,J,...): work on these cases only."""
import os
import sys, time
import sentinel_prover as sp
import sprove


def cases():
    n = 11
    L1 = ((0, 1), (2, 3), (4, 5), (6, 7))
    X = sp.outputs(n, (L1,))
    nonred = [(i, j) for i in range(n) for j in range(i + 1, n)
              if any((x >> i) & 1 and not (x >> j) & 1 for x in X)]
    out, buckets = [], {}

    def gen(start, used, cur):
        if cur:
            L = tuple(cur)
            Y = frozenset(sp.apply_layer(L, x) for x in X)
            k = (sprove.inv_hash(Y, n), len(Y))
            b = buckets.setdefault(k, [])
            if not any(sp.equivalent(Y2, Y, n) for Y2 in b):
                b.append(Y)
                out.append((L, Y))
        if len(cur) == 4:
            return
        for idx in range(start, len(nonred)):
            i, j = nonred[idx]
            if used >> i & 1 or used >> j & 1:
                continue
            cur.append((i, j))
            gen(idx + 1, used | (1 << i) | (1 << j), cur)
            cur.pop()
    gen(0, 0, [])
    out.sort(key=lambda c: len(c[1]))
    return L1, out


def main():
    flags = ('--oracle', '--progress', '--guide', '--share', '--wide-sub')
    helpcases = None
    if '--help' in sys.argv:
        k = sys.argv.index('--help')
        helpcases = [int(v) for v in sys.argv[k + 1].split(',')]
        del sys.argv[k:k + 2]
    only = None
    if '--only' in sys.argv:                 # --only A-B or I,J,...: work on these cases only
        k = sys.argv.index('--only')
        spec = sys.argv[k + 1]
        only = set(range(int(spec.split('-')[0]), int(spec.split('-')[1]) + 1)) if '-' in spec \
            else {int(v) for v in spec.split(',')}
        del sys.argv[k:k + 2]
    sys.argv = [a for a in sys.argv if a not in flags] + [a for a in sys.argv if a in flags]
    path, W = sys.argv[1], int(sys.argv[2])
    L1, cs = cases()
    if sys.argv[3] == 'list':
        print(len(cs), 'cases')
        return
    K = int(sys.argv[3])
    log = lambda s: print(time.strftime('%H:%M:%S'), s, flush=True)
    share = '--share' in sys.argv
    store = sprove.Store(path, compact=share, x_cap=40000 if share else 0)
    P = sprove.Prover(store, log=log if '--progress' in sys.argv else None, oracle='--oracle' in sys.argv,
                      guide='--guide' in sys.argv, share_seconds=60 if share else 0,
                      reverse=helpcases is not None, wide_sub='--wide-sub' in sys.argv)
    mine = helpcases if helpcases is not None else range(len(cs)) if share else range(K, len(cs), W)
    log(f'worker {K}/{W}: loaded {store.loaded} facts; {len(cs)} cases, mine: '
        f'{"the next unclaimed" if share else len(mine)}')
    if share:
        os.makedirs(os.path.join(path, 'claims'), exist_ok=True)
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
        res, fid = P.ext(11, (L1, L2), 6, Y, (4,))
        log(f'case {i}: {res} ({time.time() - t0:.0f}s) layer {list(L2)} fact {fid} nodes {P.stats["nodes"]}')


if __name__ == '__main__':
    main()
