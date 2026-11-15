#!/usr/bin/env python3
"""Bounded, non-SAT discovery of small rank-capacity counterexamples."""
import itertools
import json
from pathlib import Path
import random
import time

from adjacent_rank_ending import ending
from fixed_ending_block_capacity_verify import matchings, criterion

HERE = Path(__file__).resolve().parent


def intervals(fs, masks, n):
    allbits = (1 << (1 << n))-1
    return tuple((n-1-max(k for k in range(n+1) if (allbits ^ f) & masks[k]),
                  n-min(k for k in range(n+1) if f & masks[k])) for f in fs)


def old_pass(iv):
    n = len(iv)
    if max(b-a+1 for a, b in iv) > 4:
        return False
    if max(sum(a <= r <= b for a,b in iv) for r in range(n)) > 4:
        return False
    full = [(c,a) for c,(a,b) in enumerate(iv) if b-a == 3]
    if any(abs(a-b) in (1,3) for (_,a),(_,b) in itertools.combinations(full, 2)):
        return False
    for a in range(n-5):
        if sum(iv[c] == ((a,a+3) if c < a+2 else (a+2,a+5))
               for c in (a,a+1,a+4,a+5)) > 2:
            return False
    for _,a in full:
        if any(b == a+5 for _,b in full):
            if any(lo <= a+3 and hi >= a+5 for lo,hi in iv):
                return False
    return True


def main():
    start = time.monotonic()
    rng = random.Random(83120261115)
    seen = set()
    hits = []
    trials = checks = 0
    cache = {}
    for n in (6,7,8):
        ms = list(matchings(list(range(n))))
        masks = [sum(1 << x for x in range(1<<n) if x.bit_count() == k) for k in range(n+1)]
        initial = tuple(sum(1 << x for x in range(1<<n) if x & (1<<c)) for c in range(n))
        cache[n] = ms, masks, initial
    while time.monotonic()-start < 24:
        n = rng.choice((6,6,7,8))
        ms,masks,fs = cache[n]
        prefix = []
        for depth in range(15):
            layer = rng.choice(ms[1:])
            ff = list(fs)
            for a,b in layer:
                ff[a],ff[b] = fs[a]&fs[b],fs[a]|fs[b]
            fs = tuple(ff)
            prefix.append(layer)
            iv = intervals(fs,masks,n)
            if iv in seen or not old_pass(iv):
                continue
            seen.add(iv)
            checks += 1
            if ending(iv)[0] is not None:
                continue
            required = [sum(1<<r for r in range(a,b+1)) for a,b in iv]
            arbitrary = next((s for s in ms if criterion(n,required,s)),None)
            hits.append(dict(n=n,prefix=prefix[:],intervals=iv,
                             arbitrary_ending_possible=arbitrary is not None,
                             arbitrary_last_witness=arbitrary,
                             full_four_count=sum(b-a == 3 for a,b in iv)))
            if arbitrary is None and all(b-a <= 2 for a,b in iv):
                break
        trials += 1
        if hits and not hits[-1]['arbitrary_ending_possible'] and hits[-1]['full_four_count'] == 0:
            break
    hits.sort(key=lambda x:(x['arbitrary_ending_possible'],x['full_four_count'],x['n'],len(x['prefix'])))
    out = dict(status='TERMINATED_NORMALLY',uses_sat=False,seconds=time.monotonic()-start,
               trials=trials,candidate_vectors=checks,hits=hits)
    (HERE/'results/d13_feedback_round8-discovery.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({**{k:v for k,v in out.items() if k != 'hits'},'hit_count':len(hits),'best':hits[:2]},indent=2))


if __name__ == '__main__':
    main()
