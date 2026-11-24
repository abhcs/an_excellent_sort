"""Token profile of a whole network: probes for output k taken after layer P (h9.md Lemma 13),
followed through the later layers.  Prints, per output, |T_t(k)| for t = P..depth, and per layer the
number of comparators that are one-sided for k with both channels holding tokens (the only way the
token set shrinks).  usage: N P 'NETWORK_JSON'  (or N P @file.json)"""
import json, sys


def apply(L, x):
    for i, j in L:
        if (x >> i) & 1 and not (x >> j) & 1:
            x ^= (1 << i) | (1 << j)
    return x


def states_after(n, layers):
    X = set(range(1 << n))
    for L in layers:
        X = {apply(L, x) for x in X}
    return X


def profile(n, net, p):
    X = states_after(n, net[:p])
    rows = {}
    for k in range(n):
        w = n - 1 - k
        probes = [(s, j) for s in X if bin(s).count('1') == w for j in range(n)
                  if not (s >> j) & 1 and (s | (1 << j)) in X]
        if not probes:
            continue
        sizes, merges = [len({j for _, j in probes})], []
        cur = probes
        for L in net[p:]:
            T = {j for _, j in cur}
            m = 0
            for i, j in L:
                if i in T and j in T:
                    bits = {(s >> (j if t == i else i)) & 1 for s, t in cur if t in (i, j)}
                    if len(bits) == 1:
                        m += 1
            nxt = []
            for s, t in cur:
                s2 = apply(L, s)
                t2 = t
                for i, j in L:
                    if t in (i, j):
                        other = j if t == i else i
                        t2 = j if not (s >> other) & 1 else i
                        break
                nxt.append((s2, t2))
            cur = nxt
            sizes.append(len({t for _, t in cur}))
            merges.append(m)
        rows[k] = (len(probes), sizes, merges)
    return rows


if __name__ == '__main__':
    n, p = int(sys.argv[1]), int(sys.argv[2])
    arg = sys.argv[3]
    net = json.load(open(arg[1:])) if arg.startswith('@') else json.loads(arg)
    net = [[tuple(c) for c in L] for L in net]
    for k, (np_, sizes, merges) in profile(n, net, p).items():
        print(f'output {k:2d}: {np_:4d} probes; token channels after layers {p}..{len(net)}: {sizes}; '
              f'one-sided merges per layer: {merges}')
