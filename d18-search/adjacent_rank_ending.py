#!/usr/bin/env python3
"""Linear block DP for rank-interval reachability through two matchings.

The final matching is adjacent. A returned pair is a reachability witness,
not a sorting completion. See fixed-ending-block-capacity.md for the proof.
"""


def ending(intervals):
    n=len(intervals)
    assert n and all(0<=lo<=c<=hi<n for c,(lo,hi) in enumerate(intervals))
    stats={'states':0,'transitions':0}
    def counts(block):
        if block is None:return 0,0,0
        a,b=block
        return (sum(intervals[c][0]<a for c in range(a,b+1)),
                sum(intervals[c][1]>b for c in range(a,b+1)),
                sum(a<=intervals[c][0]<=intervals[c][1]<=b for c in range(a,b+1)))
    def local(a,b,c):
        lo,hi=b
        for wire in range(lo,hi+1):
            l,h=intervals[wire]
            if l<lo and h>hi:return False
            if l<lo and (a is None or l<a[0]):return False
            if h>hi and (c is None or h>c[1]):return False
        lb,rb,fb=counts(b)
        return max(0,counts(a)[1]-lb)+max(0,counts(c)[0]-rb)<=fb
    # Store one predecessor per state; suffix copies would cost O(n^2).
    buckets=[[] for _ in range(n)]
    parent={}
    for length in (1,2):
        if length<=n:
            state=(None,(0,length-1));parent[state]=None
            buckets[length-1].append(state)
    accepted=None
    for end in range(n):
        for state in buckets[end]:
            a,b=state;stats['states']+=1
            if end==n-1:
                if local(a,b,None):
                    accepted=state;break
                continue
            start=end+1
            for length in (1,2):
                if start+length>n:continue
                c=(start,start+length-1);stats['transitions']+=1
                if not local(a,b,c):continue
                nxt=(b,c)
                if nxt not in parent:
                    parent[nxt]=state;buckets[c[1]].append(nxt)
        if accepted is not None:break
    if accepted is None:return None,stats
    blocks=[]
    while accepted is not None:
        blocks.append(accepted[1]);accepted=parent[accepted]
    blocks.reverse()
    owner={v:i for i,(a,b) in enumerate(blocks) for v in range(a,b+1)}
    demands={};free={i:[] for i in range(len(blocks))}
    for v,(lo,hi) in enumerate(intervals):
        targets={owner[r] for r in range(lo,hi+1)}-{owner[v]}
        assert len(targets)<=1
        if targets:demands.setdefault((owner[v],targets.pop()),[]).append(v)
        else:free[owner[v]].append(v)
    pen=[]
    assert all(abs(a-b)==1 for a,b in demands)
    for a in range(len(blocks)-1):
        b=a+1
        left=demands.get((a,b),[]);right=demands.get((b,a),[])
        while left and right:pen.append(tuple(sorted((left.pop(),right.pop()))))
    for (_,target),vertices in demands.items():
        while vertices:
            assert free[target]
            pen.append(tuple(sorted((vertices.pop(),free[target].pop()))))
    last=[b for b in blocks if b[0]!=b[1]]
    by_lower=[None]*n
    for edge in pen:
        assert by_lower[edge[0]] is None
        by_lower[edge[0]]=edge
    return [[edge for edge in by_lower if edge is not None],last],stats
