#!/usr/bin/env python3
"""Exact fixed-cut ending DP for penultimate span<=3 and adjacent final edges."""
FREE,LEFT,RIGHT,IMPOSSIBLE=0,1,2,3


def profiles(states):
    """States are explicit equal-length Boolean sequences, with conserved weight."""
    assert states
    n=len(states[0]);assert all(len(x)==n for x in states)
    weighted=[(n-sum(x),x) for x in states]
    result=[]
    for c in range(n):
        row={}
        for j in range(max(0,c-3),min(n,c+4)):
            needed=FREE
            for k,x in weighted:
                out=x[c] if j==c else (x[c] and x[j]) if c<j else (x[c] or x[j])
                if out==(c>=k):continue
                if c==k-1 and out:needed|=RIGHT
                elif c==k and not out:needed|=LEFT
                else:needed=IMPOSSIBLE
                if needed==IMPOSSIBLE:break
            row[j]=needed
        result.append(row)
    return result


def ending(mode):
    """Return [P,S] or None. The profiles, not this DP, depend on the cut data."""
    n=len(mode);assert n
    frontier={((),0)};parents=[]
    stats={'states':0,'transitions':0,'max_boundary_states':1}
    for i in range(n):
        nxt={}
        for state in frontier:
            crossing,previous=state;stats['states']+=1
            incoming=[a for a,b in crossing if b==0]
            assert len(incoming)<=1
            reserved={b for a,b in crossing}
            choices=[i+incoming[0]] if incoming else [i]+[i+d for d in (1,2,3) if i+d<n and d not in reserved]
            shifted=tuple((a-1,b-1) for a,b in crossing if b)
            for partner in choices:
                required=mode[i].get(partner,IMPOSSIBLE)
                if required==IMPOSSIBLE:continue
                future=shifted+(((-1,partner-i-1),) if partner>i else ())
                for following in ((0,) if previous or i==n-1 else (0,1)):
                    stats['transitions']+=1
                    if required&LEFT and not previous:continue
                    if required&RIGHT and not following:continue
                    out=(future,following)
                    nxt.setdefault(out,(state,partner,following))
        if not nxt:return None,stats
        assert len(nxt)<=30
        parents.append(nxt);frontier=set(nxt)
        stats['max_boundary_states']=max(stats['max_boundary_states'],len(nxt))
    accepted=((),0)
    if accepted not in frontier:return None,stats
    p=[];s=[]
    for i in range(n-1,-1,-1):
        previous,partner,following=parents[i][accepted]
        if partner>i:p.append((i,partner))
        if following:s.append((i,i+1))
        accepted=previous
    p.reverse();s.reverse()
    return [p,s],stats
