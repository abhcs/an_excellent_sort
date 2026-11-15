"""How close can a 6-layer network on 11 channels get to image(T) subset of A'(M7)?
Convention: bit i = channel i (0-indexed)."""
import random, itertools
def perfect(items):
    items=list(items); random.shuffle(items)
    return tuple((min(items[i],items[i+1]),max(items[i],items[i+1])) for i in range(0,len(items),2))
def rand_max(n):
    z=random.randrange(n) if n%2 else None
    return perfect([i for i in range(n) if i!=z])
def adj_layers(n):
    return [tuple((i,i+1) for i in range(n-1) if mask>>i & 1)
            for mask in range(1<<(n-1)) if not (mask & (mask<<1))]
def S_set(n): return {((1<<k)-1)<<(n-k) for k in range(n+1)}
def Ap(n,M):
    out=set(S_set(n))
    for v in S_set(n):
        ps=[p for p in M if (((v>>p[0])&1),((v>>p[1])&1))==(0,1)]
        for r in range(1,len(ps)+1):
            for c in itertools.combinations(ps,r):
                w=v
                for (a,b) in c: w=(w|(1<<a))&~(1<<b)
                out.add(w)
    return out
def image(net,n):
    cur=set(range(1<<n))
    for L in net:
        nxt=set()
        for x in cur:
            v=x
            for (a,b) in L:
                if ((v>>a)&1)==1 and ((v>>b)&1)==0: v=(v&~(1<<a))|(1<<b)
            nxt.add(v)
        cur=nxt
    return cur
n=11; t=6; random.seed(7)
M7s=[M for M in adj_layers(n) if len(M)>=3]     # focus on rich last layers
best=(10**9,None,None)
for trial in range(40):
    M7=random.choice(M7s); T=Ap(n,M7)
    net=[rand_max(n) for _ in range(t)]
    cur=len(image(net,n)-T)
    for it in range(120):
        i=random.randrange(t); old=net[i]; net[i]=rand_max(n)
        s=len(image(net,n)-T)
        if s<=cur: cur=s
        else: net[i]=old
        if cur<best[0]: best=(cur,M7,[l for l in net])
print("best |image \\ A'(M7)| =", best[0], "  |A'(M7)| =", len(Ap(n,best[1])), "  M7 =", best[1])
print("best count of image states inside A':", len(Ap(n,best[1]) & image(best[2],n)) if best[2] else None)
