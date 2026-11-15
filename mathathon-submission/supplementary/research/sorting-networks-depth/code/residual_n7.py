"""Residual case of the block-lemma route for D(7) >= 6:
is there a 4-layer maximal-layer network on 7 channels sorting image(M)
for some near-perfect matching M?  Expect: no."""
import sys
def perfect_matchings(items):
    if not items: yield (); return
    a=items[0]
    for k in range(1,len(items)):
        b=items[k]
        for m in perfect_matchings(tuple(x for x in items[1:] if x!=b)):
            yield ((a,b),)+m
def near_perfect(n):
    return [m for z in range(n) for m in perfect_matchings(tuple(x for x in range(n) if x!=z))]
def apply_m(v,m):
    for (a,b) in m:
        if ((v>>a)&1)==1 and ((v>>b)&1)==0: v=(v&~(1<<a))|(1<<b)
    return v
n=7; depth=4
layers=near_perfect(n)
acts=[[apply_m(v,m) for v in range(1<<n)] for m in layers]
tgt=0
for k in range(n+1): tgt |= 1<<((((1<<k)-1)<<(n-k)))
hits=[]
for M in near_perfect(n):
    st=0
    for v in range(1<<n):
        if all(not(((v>>a)&1)==1 and ((v>>b)&1)==0) for (a,b) in M): st |= 1<<v
    frontier={st}
    for d in range(depth):
        new={}
        for s in frontier:
            members=[v for v in range(1<<n) if (s>>v)&1]
            for li,act in enumerate(acts):
                ns=0
                for v in members: ns |= 1<<act[v]
                if (ns & ~tgt)==0:
                    hits.append((M,d+1)); break
                if ns in new: continue
                if any((ns|t)==ns for t in new): continue
                for t in [t for t in new if (t|ns)==t]: del new[t]
                new[ns]=1
            if hits and hits[-1][0]==M: break
        if hits and hits[-1][0]==M: break
        frontier=set(new)
        sys.stderr.write(f"M={M} depth {d+1}: {len(frontier)} states\n")
    if hits: break
print("n=7 residual: hits =", hits)
