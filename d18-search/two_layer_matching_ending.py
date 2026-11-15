#!/usr/bin/env python3
"""Exact adjacent-final sorting via one mandatory-vertex matching.

For each active P mode require correct outputs away from the final boundary,
and forbid needing both incident final edges. Weight conservation makes all
remaining final-edge requests reciprocal and therefore disjoint. Restricting
P span to three is complete for actual full comparator-prefix images only.
"""

def neg(x):return not x if isinstance(x,bool) else -x

def add_matching_ending(model,states):
    n=model.n;before_v=model.nv;before_c=model.ncl;guards={};seen=set()
    def emit(clause):
        if any(v is True for v in clause):return
        literals=set(v for v in clause if v is not False)
        if any(-v in literals for v in literals):return
        key=tuple(sorted(literals))
        if key not in seen:seen.add(key);model.add(list(key))
    def require(guard,c,j,state,want):
        bits=[state[c]] if c==j else [state[c],state[j]]
        if c==j:emit([-guard,bits[0] if want else neg(bits[0])])
        elif (c<j and want) or (c>j and not want):
            for bit in bits:emit([-guard,bit if want else neg(bit)])
        else:emit([-guard]+[bit if want else neg(bit) for bit in bits])
    for c in range(n):
        for j in range(max(0,c-3),min(n,c+4)):
            base,left,right=(model.new_var() for _ in range(3))
            guards[c,j]=(base,left,right)
            for x,state in states.items():
                k=n-x.bit_count()
                guard=left if c==k else right if c==k-1 else base
                require(guard,c,j,state,c>=k)
    guard_clauses=model.ncl-before_c
    pen=model.g[-2]
    for (i,j),g in pen.items():
        if j-i>3:emit([-g])
    for c in range(n):
        incident=[g for edge,g in pen.items() if c in edge]
        for j in range(max(0,c-3),min(n,c+4)):
            if j==c:guard=incident
            else:
                g=pen.get(tuple(sorted((c,j))))
                if g is None:continue
                guard=[-g]
            base,left,right=guards[c,j]
            emit(guard+[base]);emit(guard+[left,right])
    return dict(added_variables=model.nv-before_v,clauses=model.ncl-before_c,
                mode_count=len(guards),guard_clauses=guard_clauses,
                matching_clauses=model.ncl-before_c-guard_clauses,
                scope='Exact sorting using span-three P and the implied adjacent final matching')
