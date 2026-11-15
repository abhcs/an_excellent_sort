# Extracted verbatim from collaborator snapshot 53034fa080e0b1014dc796281a515ce357765868, Appendix A (following this provenance line).
import json,sys
B16=[[(0,1),(2,3),(4,5),(6,7),(8,9),(10,11),(12,13),(14,15)],
[(0,2),(1,3),(4,6),(5,7),(8,10),(9,11),(12,14),(13,15)],
[(0,4),(1,5),(2,6),(3,7),(8,12),(9,13),(10,14),(11,15)],
[(0,8),(1,9),(2,10),(3,11),(4,12),(5,13),(6,14),(7,15)],
[(1,2),(3,12),(4,8),(5,10),(6,9),(7,11),(13,14)],
[(1,4),(2,8),(3,10),(5,9),(6,12),(7,13),(11,14)],
[(2,4),(3,8),(5,6),(7,9),(10,12),(11,13)],
[(3,5),(6,8),(7,10),(9,12)],
[(3,4),(5,6),(7,8),(9,10),(11,12)]]
def par(*nets):
    d=max(len(x) for x in nets); return [sum((x[i] for x in nets if i<len(x)),[]) for i in range(d)]
def kmerge(lists):
    L=len(lists[0]); k=len(lists)
    if L==2:
        w=[x for l in lists for x in l]
        return [[(w[a],w[b]) for a,b in lay] for lay in B16[1:]], w
    El,Eo=kmerge([l[0::2] for l in lists]); Ol,Oo=kmerge([l[1::2] for l in lists])
    out=[None]*(2*len(Eo)); out[0::2]=Eo; out[1::2]=Oo
    lays=par(El,Ol); s=1
    while s<k: s*=2
    s//=2
    while s>=1:
        lays.append([(out[2*i+1],out[2*i+2*s]) for i in range(len(out)//2) if 2*i+2*s<len(out)]); s//=2
    return lays,out
def sort16(w): return [[(w[a],w[b]) for a,b in lay] for lay in B16], list(w)
def sorter(w):
    n=len(w)
    if n==16: return sort16(w)
    sub=[sorter(w[i*n//8:(i+1)*n//8]) for i in range(8)]
    ml,out=kmerge([o for _,o in sub])
    return par(*[l for l,_ in sub])+ml,out
for n in (128,1024):
    lays,out=sorter(list(range(n)))
    pos={w:i for i,w in enumerate(out)}
    std=[[ (pos[a],pos[b]) for a,b in lay] for lay in lays]
    assert all(a<b for lay in std for a,b in lay)
    for lay in std:
        u=[x for c in lay for x in c]; assert len(u)==len(set(u))
    print(n,"depth",len(std),"size",sum(map(len,std)))
    json.dump({"n":n,"depth":len(std),"layers":std},open(f"net_{n}.json","w"))
