#!/usr/bin/env python3
"""Exact binary-threshold endpoints and the full-three-rank sorting obstruction.

states MUST contain the complete fixed-prefix binary image, then symbolically
propagated through every free layer up to the cut. Samples are insufficient.
"""

def neg(v):return not v if isinstance(v,bool) else -v


def add_exact_endpoints(model,states,lower,upper):
    n=model.n;by_zeros={k:[] for k in range(n+1)}
    for x,state in states.items():
        assert 0<=x<(1<<n)
        by_zeros[n-x.bit_count()].append(state)
    assert all(by_zeros.values()),'Every input weight must be represented.'
    count=0
    for k in range(1,n):
        for c in range(n):
            model.add([lower[c][k]]+[neg(s[c]) for s in by_zeros[k]])
            model.add([upper[c][k]]+[s[c] for s in by_zeros[k]])
            count+=2
    return dict(reverse_threshold_clauses=count,complete_image_required=True)


def add_no_full_triples(model,lower,upper):
    for a in range(model.n-2):
        clause=[]
        for c in range(a,a+3):
            # Negate: lo(c)=a AND hi(c)=a+2, for all three wires.
            clause += [neg(lower[c][a]),lower[c][a+1],neg(upper[c][a+3]),upper[c][a+2]]
        model.add(clause)
    return model.n-2
