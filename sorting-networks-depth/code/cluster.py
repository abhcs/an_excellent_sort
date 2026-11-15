"""Theorem F, one level up: if F = prod_i A_i over a partition P of the channels,
then |L_M(F)| = prod over the CLUSTERS of the interaction graph (blocks joined by
M-pairs straddling them) of the local image.  Test on real 3-layer chains."""
import random
def near_perfect(n):
    out=[]
    def rec(used,cur):
        i=None
        for k in range(n):
            if not (used>>k)&1: i=k; break
        if i is None: out.append(tuple(cur)); return
        rec(used|(1<<i),cur)
        for j in range(i+1,n):
            if not (used>>j)&1: rec(used|(1<<i)|(1<<j),cur+[(i,j)])
    rec(0,[]); return [m for m in out if len(m)==n//2]
def LM(M,v):
    for (a,b) in M:
        if ((v>>a)&1)==1 and ((v>>b)&1)==0: v=(v&~(1<<a))|(1<<b)
    return v
def parts(n,Ms):
    par=list(range(n))
    def f(a):
        while par[a]!=a: par[a]=par[par[a]]; a=par[a]
        return a
    for a,b in Ms:
        ra,rb=f(a),f(b)
        if ra!=rb: par[ra]=rb
    d={}
    for i in range(n): d.setdefault(f(i),[]).append(i)
    return sorted([tuple(v) for v in d.values()])
def clusters(blocks, M):
    """join blocks that some M-pair straddles"""
    bid={}
    for i,B in enumerate(blocks):
        for c in B: bid[c]=i
    nb=len(blocks); par=list(range(nb))
    def f(a):
        while par[a]!=a: par[a]=par[par[a]]; a=par[a]
        return a
    for a,b in M:
        ra,rb=f(bid[a]),f(bid[b])
        if ra!=rb: par[ra]=rb
    d={}
    for i in range(nb): d.setdefault(f(i),[]).append(i)
    return [sum((list(blocks[i]) for i in idx),[]) for idx in d.values()]

n=9
Ls=near_perfect(n)
random.seed(1)
bad=0; tested=0
for trial in range(400):
    M1,M2,M3 = (random.choice(Ls) for _ in range(3))
    F1=[v for v in range(1<<n) if all(not(((v>>a)&1)==1 and ((v>>b)&1)==0) for (a,b) in M1)]
    F2={LM(M2,v) for v in F1}
    lhs=len({LM(M3,v) for v in F2})
    blocks=parts(n,list(M1)+list(M2))
    # F2 is a product over `blocks`: A_i = states of F2 zero outside C_i
    A={}
    for i,B in enumerate(blocks):
        Cs=set(B); idx={c:j for j,c in enumerate(B)}
        st=set()
        for v in F2:
            if any(((v>>c)&1) and c not in Cs for c in range(n)): continue
            w=0
            for c in B:
                if (v>>c)&1: w|=1<<idx[c]
            st.add(w)
        A[i]=st
    rhs=1
    for cl in clusters(blocks,M3):
        Cs=set(cl); idx={c:j for j,c in enumerate(cl)}
        st={0}
        for i,B in enumerate(blocks):
            if not set(B) <= Cs: continue
            lifted=set()
            for v in A[i]:
                w=0
                for j,c in enumerate(B):
                    if (v>>j)&1: w|=1<<idx[c]
                lifted.add(w)
            st={a|b for a in st for b in lifted}
        M3l=[(idx[a],idx[b]) for (a,b) in M3 if a in Cs and b in Cs]
        pr=set()
        for v in st: pr.add(LM(M3l,v))
        rhs*=len(pr)
        tested+=1
    if lhs!=rhs: bad+=1
print(f"3-layer cluster factorization: {bad} mismatches over 400 chains (n=9)")
