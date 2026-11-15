"""Aggressive minimisation of |image| for 6-layer networks on 11 channels.
If a value <= 17 is reachable, the size relaxation cannot prove D(11)>=8."""
import random, sys
def perfect(items):
    items=list(items); random.shuffle(items)
    return tuple((min(items[i],items[i+1]),max(items[i],items[i+1])) for i in range(0,len(items),2))
def rand_max(n):
    z=random.randrange(n) if n%2 else None
    return perfect([i for i in range(n) if i!=z])
def img(net,n,cur):
    for L in net:
        nxt=set()
        for x in cur:
            v=x
            for (a,b) in L:
                if ((v>>a)&1)==1 and ((v>>b)&1)==0: v=(v&~(1<<a))|(1<<b)
            nxt.add(v)
        cur=nxt
    return cur
n=11; t=6
random.seed(99)
best_global=(10**9,None)
start=[[(0,9),(1,4),(2,6),(3,8),(5,10)],
       [(0,2),(1,5),(3,7),(4,9),(6,10)],
       [(0,1),(2,4),(3,6),(5,8),(7,9)],
       [(0,7),(1,3),(2,5),(4,8),(6,9)],
       [(0,1),(2,3),(4,6),(5,7),(8,10)],
       [(1,2),(3,4),(5,6),(7,8),(9,10)]]
for restart in range(30):
    if restart==0:
        net=[tuple(map(tuple,start[i])) for i in range(t)]
    else:
        net=[rand_max(n) for _ in range(t)]
    cur=len(img(net,n,set(range(1<<n))))
    T=4000; stall=0
    for it in range(T):
        i=random.randrange(t); old=net[i]; net[i]=rand_max(n)
        s=len(img(net,n,set(range(1<<n))))
        if s<=cur: cur=s; stall=0
        else: net[i]=old; stall+=1
        if cur<best_global[0]:
            best_global=(cur,[l for l in net]); print("  new best", cur, flush=True)
        if cur<=13: break
    if best_global[0]<=17: break
print("BEST |F_6| found:", best_global[0], " (need > 17 for the size method to work; n+2 = 13)")
print("network:", best_global[1])
