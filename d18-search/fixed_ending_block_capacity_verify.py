#!/usr/bin/env python3
"""Direct matching enumeration controls for the hand block-capacity theorem."""
import hashlib
import itertools
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent

def matchings(vertices):
    if not vertices:
        yield ()
        return
    a,*rest=vertices
    yield from matchings(rest)
    for b in rest:
        for tail in matchings([v for v in rest if v!=b]):
            yield ((a,b),)+tail

def cones(n,p,s):
    result=[]
    for c in range(n):
        reached={c}
        for layer in (p,s):
            reached |= {v for a,b in layer if a in reached or b in reached for v in (a,b)}
        result.append(sum(1<<v for v in reached))
    return result

def criterion(n,required,s):
    blocks=[set(e) for e in s]
    used=set().union(*blocks) if blocks else set()
    blocks += [{c} for c in range(n) if c not in used]
    owner={c:i for i,b in enumerate(blocks) for c in b}
    k=[[0]*len(blocks) for _ in blocks];free=[0]*len(blocks)
    for c,bits in enumerate(required):
        assert bits&(1<<c)
        touched={owner[r] for r in range(n) if bits&(1<<r)}
        if len(touched)>2:return False
        touched.discard(owner[c])
        if touched:k[owner[c]][touched.pop()]+=1
        else:free[owner[c]]+=1
    return all(sum(max(0,k[b][c]-k[c][b]) for b in range(len(blocks)))<=free[c]
               for c in range(len(blocks)))

def options(n,c):
    return [sum(1<<i for i in range(a,b+1)) for a in range(c+1) for b in range(c,n)]

def main():
    counts={}
    for n in (4,6):
        ms=list(matchings(list(range(n))));count=0
        rng=random.Random(20261115)
        for s in ms:
            candidates=[cones(n,p,s) for p in ms]
            choices=[options(n,c) for c in range(n)]
            families=(itertools.product(*choices) if n==4 else
                      (tuple(rng.choice(x) for x in choices) for _ in range(100)))
            for family in families:
                direct=any(all(r & ~cone ==0 for r,cone in zip(family,cs)) for cs in candidates)
                assert criterion(n,family,s)==direct,(n,s,family)
                count+=1
        counts[n]=count
    example=[(0,3),(0,3),(0,2),(3,4),(2,5),(4,5)]
    assert not criterion(6,[sum(1<<v for v in range(a,b+1)) for a,b in example],((0,1),(2,3),(4,5)))
    result=dict(status='VERIFIED',uses_sat=False,interval_families_by_width=counts,
                four_wire_exhaustive=True,six_wire_samples_per_last_matching=100,
                proof_sha256=hashlib.sha256((HERE/'fixed-ending-block-capacity.md').read_bytes()).hexdigest(),
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (HERE/'results/fixed-ending-block-capacity-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
