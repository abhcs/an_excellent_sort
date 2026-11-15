#!/usr/bin/env python3
"""Independent small exhaustive and planted-family checks for recognition."""
import hashlib
from itertools import product
import json
from pathlib import Path
import random
from signed_fork_prefix import blind_states, encode, recognize

ROOT=Path(__file__).parent


def main():
    rng=random.Random(20261115)
    tiny=0
    for n in (3,4,5):
        for trial in range(8):
            layers=[]
            for _ in range(3):
                vertices=list(range(n));rng.shuffle(vertices)
                layers.append(sorted(tuple(sorted(vertices[i:i+2])) for i in range(0,n-1,2)
                                     if rng.randrange(3)))
            for r in range(1,n+1):
                direct=set()
                for initial in product((-1,0,1),repeat=n):
                    if initial.count(0)!=r:continue
                    state=list(initial);valid=True
                    for layer in layers:
                        for a,b in layer:
                            if state[a]==state[b]==0:valid=False
                            state[a],state[b]=sorted((state[a],state[b]))
                    if valid:direct.add(encode(state))
                normalized,_=blind_states(n,layers,r)
                assert set(normalized)==direct
                tiny+=1
    planted=0
    for index,Bsigns in enumerate(product((-1,1),repeat=5)):
        r=7+index%3;n=18
        positions=list(range(n));rng.shuffle(positions)
        A=positions[:5];B=positions[5:10];common=positions[10:10+r-7]
        fixed=positions[10+r-7:]
        signs={A[i]:s for i,s in enumerate((-1,-1,1,1,1))}
        signs.update(zip(B,Bsigns))
        base=[0]*n
        for v in fixed:base[v]=rng.choice((-1,1))
        rows=((0,1),(1,2),(2,4),(1,3))
        states={}
        for i,j in rows:
            for w in B:
                state=base.copy()
                for v in (A[i],A[j],w):state[v]=signs[v]
                states[encode(state)]=tuple(state)
        found,_=recognize(n,r,states)
        assert found is not None
        smaller=dict(list(states.items())[:-1])
        assert recognize(n,r,smaller)[0] is None
        planted+=1
    # Twenty states varying only nine positions cannot contain the template's
    # ten distinct variable positions, regardless of their signs.
    negative={}
    for i,j in ((0,1),(1,2),(2,3),(3,0)):
        for w in range(4,9):
            state=[0]*10
            for v in (i,j,w):state[v]=-1 if v%2 else 1
            negative[encode(state)]=tuple(state)
    assert len(negative)==20 and recognize(10,7,negative)[0] is None
    record=dict(status='VERIFIED',tiny_exhaustive_prefix_cases=tiny,
                planted_arbitrarily_embedded_families=planted,
                planted_families_cover_all_B_sign_assignments=True,
                nineteen_state_negative_controls=planted,
                twenty_state_nine_variable_negative_control=True,
                sat_used=False,
                sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in (Path(__file__),ROOT/'signed_fork_prefix.py')})
    (ROOT/'results/signed-fork-prefix-recognizer-checks.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2))


if __name__=='__main__':main()
