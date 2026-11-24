"""partition.py MEMBERS.txt DUMP.txt: compare the class partition of cls.c (explicit permutations) with the
partition by 128-bit canonical-form hashes (classcount.c DUMP file: hash, second-layer class, third layer).
They agree iff the map hash -> class is a bijection on the prefixes."""
import sys, collections
mine = {}
for line in open(sys.argv[1]):
    r, l3, rest = line.split('|')
    mine[(int(r), tuple(map(int, l3.split())))] = int(rest.split()[0])
h2c, c2h, missing, n = collections.defaultdict(set), collections.defaultdict(set), 0, 0
for line in open(sys.argv[2]):
    f = line.split(); key = (int(f[1]), tuple(map(int, f[2:])))
    n += 1
    if key not in mine:
        missing += 1; continue
    c = mine.pop(key); h2c[f[0]].add(c); c2h[c].add(f[0])
split = sum(1 for s in h2c.values() if len(s) > 1); merged = sum(1 for s in c2h.values() if len(s) > 1)
print(f'{n} prefixes in the hash dump, {missing} not in MEMBERS, {len(mine)} in MEMBERS only')
print(f'{len(h2c)} hash classes, {len(c2h)} permutation classes; hashes spanning several classes: {split}; '
      f'classes spanning several hashes: {merged}')
print('the partitions agree' if not (missing or mine or split or merged) else 'THE PARTITIONS DIFFER')
