"""Token-cone penalty of a network after its first t layers (efficient-prefixes.md section 9): for a depth-D
sorter, after layer D-2 every rank k lies on at most 4 channels, all within k +- 4.  Penalty = sum over k of
the excess count plus the channels out of position.  usage: cone_check.py LOGFILE_WITH_FOUND_LINE D T"""
import json, re, sys
line = [l for l in open(sys.argv[1]) if 'FOUND' in l][-1]
net = json.loads(line.split('network=')[1])
D, t = int(sys.argv[2]), int(sys.argv[3])
n = 1 + max(max(i, j) for L in net for i, j in L)


def interval_tokens(layers):
    lo = [n] * n; hi = [-1] * n
    ones_min = [n + 1] * n; zeros_max = [-1] * n
    for x in range(1 << n):
        s = x
        for L in layers:
            for i, j in L:
                if (s >> i) & 1 and not (s >> j) & 1:
                    s ^= (1 << i) | (1 << j)
        w = bin(x).count('1')
        for c in range(n):
            if (s >> c) & 1:
                ones_min[c] = min(ones_min[c], w)
            else:
                zeros_max[c] = max(zeros_max[c], w)
    # rank interval of channel c: [n-1-zeros_max, n-ones_min]
    T = [[c for c in range(n) if n - 1 - zeros_max[c] <= k <= n - ones_min[c]] for k in range(n)]
    return T


T = interval_tokens(net[:t])
r = D - t; cap = 2 ** r; w = {0: 0, 1: 1, 2: 4}.get(r, n)
pen = sum(max(0, len(T[k]) - cap) + sum(1 for c in T[k] if abs(c - k) > w) for k in range(n))
print(f'n={n} depth={len(net)}; after layer {t}: |T(k)| = {[len(T[k]) for k in range(n)]}, cap {cap}, penalty {pen}')
print('first three layers:', json.dumps(net[:3]))
