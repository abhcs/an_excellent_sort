#!/usr/bin/env python3
"""Substitute min/max directly into exact adjacent-final-layer conditions.

States must be the correctly simulated cut states, each with its original
weight. The penultimate gates may be arbitrary; the final gates must form
an adjacent matching. No data variables or cardinal auxiliaries are added.
"""
from itertools import combinations

def neg(v):return not v if isinstance(v,bool) else -v

def add_data_ending(model,states):
    n=model.n;pen,last=model.g[-2:];seen=set();start=model.ncl
    incidence={c:[g for e,g in pen.items() if c in e] for c in range(n)}
    def emit(literals):
        if any(v is True for v in literals):return
        clause=set(v for v in literals if v is not False)
        if any(-v in clause for v in clause):return
        key=tuple(sorted(clause))
        if key not in seen:seen.add(key);model.add(list(key))
    for x,state in states.items():
        k=n-x.bit_count()
        if k in (0,n):continue
        boundary=last.get((k-1,k),False)
        def require(c,guard,op,inputs):
            # Only the two boundary positions may disagree with the target,
            # and only if the final matching contains their correcting edge.
            base=list(guard)+([boundary] if c in (k-1,k) else [])
            want_one=c>=k
            if op=='idle':emit(base+[inputs[0] if want_one else neg(inputs[0])])
            elif (op=='min' and want_one) or (op=='max' and not want_one):
                for bit in inputs:emit(base+[bit if want_one else neg(bit)])
            else:emit(base+[bit if want_one else neg(bit) for bit in inputs])
        for c in range(n):require(c,incidence[c],'idle',[state[c]])
        for (i,j),g in pen.items():
            require(i,[-g],'min',[state[i],state[j]])
            require(j,[-g],'max',[state[i],state[j]])
    return dict(clauses=model.ncl-start,distinct_templates=len(seen),added_variables=0,
                input_states=len(states),scope='Exact two-layer sorting with adjacent final matching')
