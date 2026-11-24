"""checksorter.py PREFIXES.txt RESULTS.txt: brute-force check of every SORTER line printed by tok.c
(prefix layers from the input line, later layers from the output line; all 2^n 0-1 inputs)."""
import sys
pre = {}
for line in open(sys.argv[1]):
    f = list(map(int, line.split()))
    if not f:
        continue
    idx, n, D, p = f[:4]; k = 4; layers = []
    for _ in range(p):
        m = f[k]; layers.append([(f[k + 1 + 2 * c], f[k + 2 + 2 * c]) for c in range(m)]); k += 1 + 2 * m
    pre[idx] = (n, D, layers)
ok = bad = 0
for line in open(sys.argv[2]):
    if 'SORTER' not in line:
        continue
    head, tail = line.split('SORTER')
    idx = int(head.split()[0]); n, D, layers = pre[idx]
    parts = tail.split('|')[1:]
    parts[-1] = ' '.join(parts[-1].split()[:-1])          # drop the seconds field
    later = []
    for s in parts:
        v = list(map(int, s.split())); later.append([(v[2 * c], v[2 * c + 1]) for c in range(len(v) // 2)])
    net = layers + later
    assert len(net) == D, (idx, len(net), D)
    for L in net:
        used = [c for P in L for c in P]
        assert len(used) == len(set(used)) and all(a < b for a, b in L)
    good = True
    for x in range(1 << n):
        v = [(x >> c) & 1 for c in range(n)]
        for L in net:
            for a, b in L:
                if v[a] > v[b]:
                    v[a], v[b] = v[b], v[a]
        if any(v[c] > v[c + 1] for c in range(n - 1)):
            good = False; break
    ok += good; bad += not good
    print(idx, 'sorts' if good else 'DOES NOT SORT', f'depth {D}')
print(f'{ok} sorters verified, {bad} failures')
