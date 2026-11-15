#!/usr/bin/env python3
"""Existential path through the 30-state exact two-layer ending automaton.

Requires correctly weighted cut states. Completeness for arbitrary sorting
endings uses the nonredundant span-three normal form for actual full prefix
images. Guard implications need only the positive direction: a chosen path
can use a guard only when every relevant cut state satisfies that mode.
"""

def neg(x):return not x if isinstance(x,bool) else -x

def add_mode_path_ending(model,states):
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
    frontier={((),0):True};boundary_states=[];transition_count=0
    for i in range(n):
        incoming_transitions={};nxt={}
        for state,reach in frontier.items():
            crossing,previous=state
            incoming=[a for a,b in crossing if b==0]
            assert len(incoming)<=1
            reserved={b for a,b in crossing}
            choices=[i+incoming[0]] if incoming else [i]+[i+d for d in (1,2,3) if i+d<n and d not in reserved]
            shifted=tuple((a-1,b-1) for a,b in crossing if b)
            for j in choices:
                future=shifted+(((-1,j-i-1),) if j>i else ())
                for following in ((0,) if previous or i==n-1 else (0,1)):
                    target=(future,following)
                    if target not in nxt:nxt[target]=model.new_var();incoming_transitions[target]=[]
                    transition=model.new_var();transition_count+=1
                    incoming_transitions[target].append(transition)
                    base,left,right=guards[i,j]
                    emit([-transition,reach]);emit([-transition,base])
                    if not previous:emit([-transition,left])
                    if not following:emit([-transition,right])
        for state,reach in nxt.items():emit([-reach]+incoming_transitions[state])
        assert len(nxt)<=30
        frontier=nxt;boundary_states.append(len(nxt))
    emit([frontier.get(((),0),False)])
    return dict(added_variables=model.nv-before_v,clauses=model.ncl-before_c,
                mode_count=len(guards),guard_clauses=guard_clauses,
                path_clauses=model.ncl-before_c-guard_clauses,
                boundary_states=boundary_states,transitions=transition_count,
                max_boundary_states=max(boundary_states,default=1))
