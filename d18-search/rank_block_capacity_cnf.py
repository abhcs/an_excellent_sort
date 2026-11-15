#!/usr/bin/env python3
"""Exact adjacent-last-layer rank reachability, expressed by local clauses.

Uses existing endpoint and adjacent last-edge variables; adds no variables.
Assumes rank intervals contain their wire and the last edges form a matching.
L[c,k]=(lo_c>=k), U[c,k]=(hi_c<k), with strict U.
"""
from itertools import combinations


def negate(lit):
    return not lit if isinstance(lit,bool) else -lit


def add_block_capacity(model,lower,upper):
    n=model.n;last=model.g[-1];seen=set();counts={}
    def edge(k):return last.get((k,k+1),False)
    def condition(block):
        if block is None:return []
        a,b=block
        return [edge(a)] if a!=b else [negate(edge(a-1)),negate(edge(a))]
    def emit(kind,blocks,body):
        literals=[negate(v) for block in blocks for v in condition(block)]+list(body)
        if any(v is True for v in literals):return
        clause=set(v for v in literals if v is not False)
        if any(-v in clause for v in clause):return
        key=tuple(sorted(clause))
        if key in seen:return
        seen.add(key);model.add(list(key));counts[kind]=counts.get(kind,0)+1
    def atmost(kind,blocks,demands,bound):
        for subset in combinations(demands,bound+1):
            emit(kind,blocks,[negate(v) for v in subset])
    def left(block):
        if block is None:return []
        a,b=block;return [negate(lower[c][a]) for c in range(a,b+1)]
    def right(block):
        if block is None:return []
        a,b=block;return [negate(upper[c][b+1]) for c in range(a,b+1)]
    for start in range(n):
        for size in (1,2):
            end=start+size-1
            if end>=n:continue
            b=(start,end)
            previous=[None] if start==0 else [(start-k,start-1) for k in (1,2) if start>=k]
            following=[None] if end==n-1 else [(end+1,end+k) for k in (1,2) if end+k<n]
            for c in range(start,end+1):
                # A wire cannot demand both neighbors of its own last block.
                emit('one_direction',[b],[lower[c][start],upper[c][end+1]])
            for a in previous:
                if a is not None:
                    for c in range(start,end+1):
                        emit('left_extent',[a,b],[lower[c][a[0]]])
                atmost('right_capacity',[a,b],right(a)+right(b),size)
            for cblock in following:
                if cblock is not None:
                    for c in range(start,end+1):
                        emit('right_extent',[b,cblock],[upper[c][cblock[1]+1]])
                atmost('left_capacity',[b,cblock],left(b)+left(cblock),size)
            for a in previous:
                for cblock in following:
                    atmost('incoming_capacity',[a,b,cblock],right(a)+left(cblock),size)
    return dict(clauses=len(seen),by_kind=counts,added_variables=0)
