"""Per-layer shrinkage: min over (M1,M) of |L_M(Fix(M1))| / |Fix(M1)|  = |F_2|/|F_1|,
and the analogous ratio for later steps starting from such an F_2."""
import random
def perfect(items):
    items=list(items); random.shuffle(items)
    return tuple((min(items[i],items[i+1]),max(items[i],items[i+1])) for i in range(0,len(items),2))
def rand_max(n):
    z=random.randrange(n) if n%2 else None
    return perfect([i for i in range(n) if i!=z])
def Fix(n,M):
    return [v for v in range(1<<n) if all(not(((v>>a)&1)==1 and ((v>>b)&1)==0) for (a,b) in M)]
def LM(n,M,S):
    out=set()
    for x in S:
        v=x
        for (a,b) in M:
            if ((v>>a)&1)==1 and ((v>>b)&1)==0: v=(v&~(1<<a))|(1<<b)
        out.add(v)
    return out
random.seed(3)
for n in (9,11):
    e=(n-1)//2
    best=(9,None,None)
    for _ in range(4000):
        M1=rand_max(n); F1=Fix(n,M1)
        M=rand_max(n); F2=LM(n,M,F1)
        r=len(F2)/len(F1)
        if r<best[0]: best=(r,M1,M)
    print(f"n={n}: |F_1|={3**e*2}; best |F_2|/|F_1| over 4000 random pairs = {best[0]:.3f}  => |F_2| >= {int(3**e*2*best[0])}")
    # second step from that F_2
    best2=(9,None)
    F2=LM(n,best[2],Fix(n,best[1]))
    for _ in range(4000):
        M=rand_max(n); F3=LM(n,M,F2); r=len(F3)/len(F2)
        if r<best2[0]: best2=(r,M)
    print(f"        best |F_3|/|F_2| = {best2[0]:.3f}  => |F_3| >= {int(len(F2)*best2[0])}")
