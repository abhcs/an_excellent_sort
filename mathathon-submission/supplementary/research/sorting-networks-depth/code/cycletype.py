"""Compression of L_M on Fix(M_*) factors over the connected components of M_* u M.
Each component is an alternating CYCLE (k pairs of each type) or a PATH (j of each,
endpoints the two idle channels).  Compute the local ratios exactly."""
import itertools

def cyc_ratio(k):
    """alternating 2k-cycle: M* edges (v1,v2),(v3,v4),... ; M edges (v2,v3),...,(v2k,v1)"""
    V = 2*k
    Ms = [(2*i, 2*i+1) for i in range(k)]
    Me = [((2*i+1) % V, (2*i+2) % V) for i in range(k)]
    states = set()
    for c in itertools.product((0,1,2), repeat=k):        # content per M*-pair
        v = [0]*V
        for i,(a,b) in enumerate(Ms):
            if c[i] == 1: v[a] = 1
            elif c[i] == 2: v[a] = v[b] = 1
        states.add(tuple(v))
    profs = set()
    for v in states:
        profs.add(tuple(v[a]+v[b] for (a,b) in Me))
    return len(states), len(profs)

def path_ratio(j):
    """alternating path: M edges (w1,w2),(w3,w4),...; M* edges (w2,w3),(w4,w5),...
       w1 is M*-idle, w_{2j+1} is M-idle.  M*|_C has j pairs; w1 free."""
    W = 2*j+1
    Ms = [(2*i+1, 2*i+2) for i in range(j)]
    Me = [(2*i, 2*i+1) for i in range(j)]
    states = set()
    for free in (0,1):
        for c in itertools.product((0,1,2), repeat=j):
            v=[0]*W; v[0]=free
            for i,(a,b) in enumerate(Ms):
                if c[i]==1: v[a]=1
                elif c[i]==2: v[a]=v[b]=1
            states.add(tuple(v))
    profs = set()
    for v in states:
        profs.add((v[2*j],)+tuple(v[a]+v[b] for (a,b) in Me))
    return len(states), len(profs)

print(" CYCLE  k : states, profiles, ratio")
CYC={}
for k in range(1,7):
    s,p = cyc_ratio(k); CYC[k]=(s,p); print(f"   {k} : {s:6d} {p:6d}  {p/s:.6f}")
print(" PATH   j : states, profiles, ratio")
PATH={}
for j in range(0,6):
    s,p=path_ratio(j); PATH[j]=(s,p); print(f"   {j} : {s:6d} {p:6d}  {p/s:.6f}")
