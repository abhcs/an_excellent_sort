"""Lemma H predicts: for a sorting network with maximal layers,
  n odd  -> suffix graph connected;
  n even -> every suffix component has >= n/2 channels (so 1 or 2 components).
Check exhaustively for n=4 (d=3), n=6 (d=5), n=7 (d=6) with maximal layers."""
import itertools, sys
def perfect_matchings(items):
    if not items: yield (); return
    a=items[0]
    for k in range(1,len(items)):
        b=items[k]
        for m in perfect_matchings(tuple(x for x in items[1:] if x!=b)):
            yield ((a,b),)+m
def maximal_layers(n):
    if n%2==0: return list(perfect_matchings(tuple(range(n))))
    out=[]
    for z in range(n):
        for m in perfect_matchings(tuple(x for x in range(n) if x!=z)): out.append(m)
    return out
def apply(net,x,n):
    for L in net:
        for (a,b) in L:
            va,vb=(x>>a)&1,(x>>b)&1
            if va>vb: x=(x&~(1<<a))|(1<<b)
    return x
def sorts(net,n):
    return all(apply(net,x,n)==(((1<<bin(x).count('1'))-1)<<(n-bin(x).count('1'))) for x in range(1<<n))
def compsizes(n, layers):
    par=list(range(n))
    def f(a):
        while par[a]!=a: par[a]=par[par[a]]; a=par[a]
        return a
    for L in layers:
        for (a,b) in L:
            ra,rb=f(a),f(b)
            if ra!=rb: par[ra]=rb
    d={}
    for i in range(n): d[f(i)]=d.get(f(i),0)+1
    return sorted(d.values())
for n,d in [(4,3),(6,5),(7,6)]:
    Ls=maximal_layers(n)
    print(f"n={n} d={d}: {len(Ls)} maximal layers, {len(Ls)**d} sequences", flush=True)
    viol=[]
    for seq in itertools.product(range(len(Ls)),repeat=d):
        net=[Ls[i] for i in seq]
        touched=set()
        for L in net:
            for (a,b) in L: touched|={a,b}
        if len(touched)<n: continue
        if not sorts(net,n): continue
        cs=compsizes(n,net[1:])
        ok = (len(cs)==1) if n%2==1 else all(c>=n//2 for c in cs)
        if not ok: viol.append((net,cs))
        if len(viol)>2: break
    print(f"   violations: {len(viol)}", viol[:1], flush=True)
