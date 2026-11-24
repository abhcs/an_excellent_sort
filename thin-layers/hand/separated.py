"""Separated pairs.  After a layer, rank k can leave the min end of a comparator (u, v) only if u and v
never both hold elements of rank >= k (no reachable state of weight n-k has 1 on both), and the max end
only if they never both hold rank <= k (no state of weight n-1-k has 0 on both).  Counts such pairs.
usage: EXC.json KEY IDX 'EXTRA_LAYERS_JSON'"""
import json, sys, itertools
sys.path[:0] = ['.']
from ranks import states, rank_sets


def sep_pairs(n, X, k):
    lo_sep, hi_sep = [], []
    R = rank_sets(n, X)
    for u, v in itertools.combinations(range(n), 2):
        if k not in R[u] or k not in R[v]:
            continue                        # only pairs where both can hold k matter for removal
        if not any(bin(s).count('1') == n - k and (s >> u) & 1 and (s >> v) & 1 for s in X):
            lo_sep.append((u, v))           # k always the larger of the two: leaves the min end
        if not any(bin(s).count('1') == n - 1 - k and not (s >> u) & 1 and not (s >> v) & 1 for s in X):
            hi_sep.append((u, v))           # k always the smaller: leaves the max end
    return lo_sep, hi_sep


if __name__ == '__main__':
    d = json.load(open(sys.argv[1])); pre = d[sys.argv[2]][int(sys.argv[3])]
    extra = json.loads(sys.argv[4]) if len(sys.argv) > 4 else []
    n = d['n']
    for t in range(3, 3 + len(extra) + 1):
        X = states(n, pre + extra[:t - 3])
        print(f'after layer {t}:')
        for k in range(n // 2 - 1, n // 2 + 2):
            a, b = sep_pairs(n, X, k)
            print(f'   rank {k}: {len(a)} pairs where it is always the larger {a}; {len(b)} where always the smaller {b}')
