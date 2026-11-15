"""Greedy/hill-climbing search for the SMALLEST image of a t-layer maximal-layer network.
Gives an upper bound on g(t,n); if it beats |A'| the size method is dead."""
import random, sys
def perfect(items):
    items=list(items); random.shuffle(items)
    return tuple((min(items[i],items[i+1]),max(items[i],items[i+1])) for i in range(0,len(items),2))
def rand_max(n):
    z=random.randrange(n) if n%2 else None
    return perfect([i for i in range(n) if i!=z])
def image_size(net,n,states):
    cur=set(states)
    for L in net:
        nxt=set()
        for x in cur:
            v=x
            for (a,b) in L:
                if ((v>>a)&1)==1 and ((v>>b)&1)==0: v=(v&~(1<<a))|(1<<b)
            nxt.add(v)
        cur=nxt
    return len(cur)
def search(n,t,iters=4000,restarts=6):
    states=list(range(1<<n))
    best=(1<<n)+1; bestnet=None
    for r in range(restarts):
        net=[rand_max(n) for _ in range(t)]
        cur=image_size(net,n,states)
        for it in range(iters):
            i=random.randrange(t)
            old=net[i]; net[i]=rand_max(n)
            s=image_size(net,n,states)
            if s<=cur: cur=s
            else: net[i]=old
            if cur<best: best=cur; bestnet=[l for l in net]
        if best<=n+2: break
    return best,bestnet
if __name__=="__main__":
    n=int(sys.argv[1]); t=int(sys.argv[2])
    b,net=search(n,t)
    print(f"n={n} t={t}: best image size found = {b}   (n+2 = {n+2}, (3n+1)/2 = {(3*n+1)//2})")
