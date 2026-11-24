"""Plan the D(13) token proof by sentinel residuals (efficient-prefixes.md section 9).
Reads resid output (per 11-channel prefix class: the classes of its residual 10-channel prefixes) and the
(10,3) class representatives; reports how many 11-channel classes have a residual in the (10,3) family and a
greedy cover: which 10-channel classes to refute so that every coverable 11-channel class is settled.
Optional REFUTED.jsonl (tokcore results on reps_10_3.json): only refuted 10-channel classes count.
usage: coverplan.py RESID.txt reps_10_3.json [REFUTED.jsonl] [OUT.json]"""
import json, sys, collections
reps = json.load(open(sys.argv[2])); idx10 = {h: i for i, h in enumerate(reps['hash'])}
refuted = None
if len(sys.argv) > 3 and sys.argv[3] != '-':
    refuted = set(); unrefuted = set()
    for line in open(sys.argv[3]):
        r = json.loads(line)
        (refuted if r['outcome'] == 'none' else unrefuted).add(r['idx'])
cls11 = []                      # list of sets of 10-class indices
for line in open(sys.argv[1]):
    f = line.split()
    s = {idx10[h] for h in f[1:] if h in idx10}
    if refuted is not None:
        s &= refuted
    cls11.append((f[0], s))
n11 = len(cls11); cov = [c for c in cls11 if c[1]]
print(f'{n11} 11-channel classes; {len(cov)} have a residual in the (10,3) family'
      + (' that is refuted' if refuted is not None else '') + f'; {n11 - len(cov)} have none')
freq = collections.Counter(i for _, s in cov for i in s)
print(f'{len(freq)} distinct 10-channel classes occur; most frequent: {freq.most_common(5)}')
# greedy cover
left = [s for _, s in cov]; chosen = []
alive = list(range(len(left)))
while alive:
    cnt = collections.Counter(i for k in alive for i in left[k])
    best, c = cnt.most_common(1)[0]
    chosen.append(best)
    alive = [k for k in alive if best not in left[k]]
print(f'greedy cover: {len(chosen)} 10-channel classes settle all {len(cov)} coverable 11-channel classes')
if len(sys.argv) > 4:
    json.dump({'chosen': chosen, 'uncovered': [h for h, s in cls11 if not s]}, open(sys.argv[4], 'w'))
