"""Which (10,3) classes must still be refuted (efficient-prefixes.md section 9)?  Greedy cover of the 11-channel
classes not yet settled by an already refuted residual class, using only classes not yet searched.
usage: needed10.py RESID.txt reps_10_3.json DONE.jsonl OUT.txt  (OUT: indices in greedy order)"""
import json, sys, collections
reps = json.load(open(sys.argv[2])); idx10 = {h: i for i, h in enumerate(reps['hash'])}
ref, done = set(), set()
for line in open(sys.argv[3]):
    r = json.loads(line); done.add(r['idx'])
    if r['outcome'] == 'none':
        ref.add(r['idx'])
left = []
for line in open(sys.argv[1]):
    f = line.split(); s = {idx10[h] for h in f[1:] if h in idx10}
    if s and not (s & ref):
        left.append(s - done)
print(f'{len(ref)} refuted so far; {len(left)} coverable 11-channel classes still unsettled')
order = []; alive = [k for k in range(len(left)) if left[k]]
stuck = sum(1 for s in left if not s)
while alive:
    cnt = collections.Counter(i for k in alive for i in left[k])
    best, c = cnt.most_common(1)[0]; order.append(best)
    alive = [k for k in alive if best not in left[k]]
print(f'{len(order)} more 10-channel classes cover them ({stuck} have only searched, unrefuted residuals)')
open(sys.argv[4], 'w').write(' '.join(map(str, order)))
