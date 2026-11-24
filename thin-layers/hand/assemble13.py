"""Assemble the token proof of T3(11,4) >= 9, hence D(13) >= 9 (efficient-prefixes.md section 9).

Every 3-layer sparse prefix of T3(11,4) lies in one of 315,835 reachable-set classes (classcount.c / resid.c;
prefixes of one class extend to a depth-8 sorter or fail together, by subsumption).  A class is settled
  (a) if some prefix in it has a sentinel residual (good track: the 10-channel prefix left after removing a
      +inf/-inf track, at most 3 comparators per layer) whose class is refuted by the exact token search at depth
      8 (tokcore2 on the (10,3) class representative): a depth-8 completion would restrict to one of the residual;
  (b) or if the exact token search refutes a representative of the class directly at (11, 4).
usage: assemble13.py RESID.txt reps_10_3.json TOK10.jsonl uncovered_11_4.json TOK11.jsonl OUT_witness.tsv.gz"""
import json, sys, gzip, collections
resid, reps10, tok10, unc, tok11, out = sys.argv[1:7]
R10 = json.load(open(reps10)); idx10 = {h: i for i, h in enumerate(R10['hash'])}
ref10 = {}; sec10 = {}; bad10 = []
for line in open(tok10):
    r = json.loads(line); sec10[r['idx']] = r['seconds']
    if r['outcome'] == 'none':
        ref10[r['idx']] = r
    else:
        bad10.append((r['idx'], r['outcome']))
U = json.load(open(unc)); ref11 = {}; sec11 = 0.0; bad11 = []
for line in open(tok11):
    r = json.loads(line); sec11 += r['seconds']
    if r['outcome'] == 'none':
        ref11[U['hash'][r['idx']]] = r
    else:
        bad11.append((r['idx'], r['outcome']))
use = collections.Counter(); settled_a = settled_b = 0; unsettled = []
with gzip.open(out, 'wt') as fo:
    fo.write('# 11-channel class hash\tsettled by\twitness\n')
    for line in open(resid):
        f = line.split(); h = f[0]
        cands = sorted(idx10[x] for x in f[1:] if x in idx10 and idx10[x] in ref10)
        if cands:
            # prefer a residual class that is used most (smaller set of 10-channel searches)
            settled_a += 1; use[cands[0]] += 1
            fo.write(f'{h}\tresidual\t{cands[0]}\n')
        elif h in ref11:
            settled_b += 1
            fo.write(f'{h}\tdirect\t-\n')
        else:
            unsettled.append(h)
n11 = settled_a + settled_b + len(unsettled)
print(f'11-channel classes: {n11}; settled through a refuted residual: {settled_a}; refuted directly: {settled_b}; '
      f'UNSETTLED: {len(unsettled)}')
print(f'10-channel classes searched: {len(sec10)} ({sum(sec10.values()) / 3600:.1f} CPU-h), refuted {len(ref10)}, '
      f'not refuted {len(bad10)} {bad10[:5]}; used as witnesses: {len(use)}')
print(f'11-channel classes searched directly: {len(U["hash"])} ({sec11 / 3600:.2f} CPU-h), refuted {len(ref11)}, '
      f'not refuted {len(bad11)} {bad11[:5]}')
if unsettled:
    print('first unsettled:', unsettled[:5])
