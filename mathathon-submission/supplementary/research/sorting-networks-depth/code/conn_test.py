"""Test: in a sorting network on an ODD number n of channels, are layers 2..d
always connected?  And layers 1..d-1?  Exhaustive over all networks of depth d."""
import itertools, sys
def all_matchings(n):
    out=[]
    def rec(i, cur, used):
        if i>=n:
            out.append(tuple(cur)); return
        rec(i+1, cur, used)          # channel i idle
        if i not in used:
            for j in range(i+1,n):
                if j not in used:
                    rec(i+1, cur+[(i,j)], used|{i,j})
    rec(0, [], frozenset())
    return out
def apply(net, x, n):
    for L in net:
        for (a,b) in L:
            va,vb=(x>>a)&1,(x>>b)&1
            if va>vb: x=(x&~(1<<a))|(1<<b)
    return x
def sorts(net,n):
    for x in range(1<<n):
        k=bin(x).count('1')
        if apply(net,x,n) != (((1<<k)-1)<<(n-k)): return False
    return True
def connected(n, layers):
    par=list(range(n))
    def f(a):
        while par[a]!=a: par[a]=par[par[a]]; a=par[a]
        return a
    for L in layers:
        for (a,b) in L:
            ra,rb=f(a),f(b)
            if ra!=rb: par[ra]=rb
    return len({f(i) for i in range(n)})==1

for n,d in [(3,3),(5,5)]:
    Ls=all_matchings(n)
    print(f"n={n} d={d}: {len(Ls)} layers, {len(Ls)**d} sequences")
    bad=0; tot=0
    for seq in itertools.product(range(len(Ls)),repeat=d):
        net=[Ls[i] for i in seq]
        # quick prune: every channel must be touched
        touched=set()
        for L in net:
            for (a,b) in L: touched|={a,b}
        if len(touched)<n: continue
        if not sorts(net,n): continue
        tot+=1
        if not connected(n,net[1:]):
            bad+=1
            if bad<=3: print("  suffix-disconnected:", net)
    print(f"  sorting networks: {tot}, suffix-disconnected: {bad}")
