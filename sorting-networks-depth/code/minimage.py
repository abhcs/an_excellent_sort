"""g(t,n) = minimum |image(L_1..L_t)| over all t-layer MAXIMAL-layer networks.
BFS over distinct image sets (bitmask over 2^n states)."""
import sys
def perfect(items):
    if not items: yield (); return
    a=items[0]
    for k in range(1,len(items)):
        b=items[k]
        for m in perfect(tuple(x for x in items[1:] if x!=b)):
            yield ((a,b),)+m
def maximal_layers(n):
    if n%2==0: return list(perfect(tuple(range(n))))
    return [m for z in range(n) for m in perfect(tuple(x for x in range(n) if x!=z))]
def apply_m(v,m):
    for (a,b) in m:
        if ((v>>a)&1)==1 and ((v>>b)&1)==0: v=(v&~(1<<a))|(1<<b)
    return v
def run(n, tmax, cap=3_000_000):
    Ls=maximal_layers(n)
    acts=[[apply_m(v,m) for v in range(1<<n)] for m in Ls]
    cur={(1<<(1<<n))-1}
    out=[len(bin(next(iter(cur))).replace('0b','')) ]  # placeholder
    res=[1<<n]
    for t in range(1,tmax+1):
        nxt=set()
        for st in cur:
            members=[v for v in range(1<<n) if (st>>v)&1]
            for act in acts:
                ns=0
                for v in members: ns |= 1<<act[v]
                nxt.add(ns)
            if len(nxt)>cap: 
                print(f"  n={n} t={t}: ABORT (>{cap} images)"); return res
        cur=nxt
        mins=min(bin(s).count('1') for s in cur)
        res.append(mins)
        print(f"  n={n} t={t}: {len(cur)} distinct images, minimum |image| = {mins}", flush=True)
    return res
if __name__=="__main__":
    n=int(sys.argv[1]); t=int(sys.argv[2])
    print(f"g(t,{n}) for t=0..{t}:", run(n,t))
