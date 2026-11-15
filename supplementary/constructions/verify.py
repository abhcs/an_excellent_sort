# Extracted verbatim from collaborator snapshot 53034fa080e0b1014dc796281a515ce357765868, Appendix B (following this provenance line).
# Independent certificate checker: works only from the flat layer list, discovers the structure itself.
import json,sys,itertools,numpy as np
def comps_in(layers,a,b,W):
    out=[]
    for t in range(a,b):
        L=[]
        for x,y in layers[t]:
            ix,iy=x in W,y in W
            if ix!=iy: raise SystemExit(f"FAIL: comparator {(x,y)} in layer {t+1} leaves its wire group")
            if ix: L.append((x,y))
        out.append(L)
    return out
def components(cl,W):
    p={w:w for w in W}
    def f(x):
        while p[x]!=x: p[x]=p[p[x]]; x=p[x]
        return x
    for L in cl:
        for x,y in L: p[f(x)]=f(y)
    g={}
    for w in W: g.setdefault(f(w),[]).append(w)
    return [sorted(v) for v in g.values()]
def run(cl,ws,X):   # X: rows=inputs, cols=wires in label order ws
    idx={w:i for i,w in enumerate(ws)}
    for L in cl:
        for x,y in L:
            a,b=X[:,idx[x]].copy(),X[:,idx[y]].copy(); X[:,idx[x]]=a&b; X[:,idx[y]]=a|b
    return bool((X[:,:-1]<=X[:,1:]).all())
stats={"sort16":0,"base":0,"cleanup":0,"comps":0}
def sorter(layers,a,b,ws):
    W=set(ws); n=len(ws)
    if n==16:
        assert b-a==9; cl=comps_in(layers,a,b,W); stats["comps"]+=sum(map(len,cl))
        X=((np.arange(1<<16)[:,None]>>np.arange(16))&1).astype(np.uint8)
        if not run(cl,ws,X): raise SystemExit("FAIL: a 16-wire block does not sort")
        stats["sort16"]+=1; return
    ds={128:26,1024:26+0}[n] if n==128 else None
    dsub={128:9,1024:26}[n]
    groups=components(comps_in(layers,a,a+dsub,W),ws)
    if len(groups)!=8 or any(len(g)!=n//8 for g in groups): raise SystemExit("FAIL: block structure")
    for g in groups: sorter(layers,a,a+dsub,g)
    merger(layers,a+dsub,b,ws,groups)
def merger(layers,a,b,ws,lists):
    W=set(ws); k=len(lists); L=len(lists[0])
    if L==2:
        if b-a!=8: raise SystemExit("FAIL: base depth")
        cl=comps_in(layers,a,b,W); stats["comps"]+=sum(map(len,cl))
        rows=[]
        for z in itertools.product(range(3),repeat=k):
            v={}
            for l,zz in zip(lists,z): v[l[0]]=int(zz<1); v[l[1]]=int(zz<2)
            rows.append([v[w] for w in ws])
        if not run(cl,ws,np.array(rows,dtype=np.uint8)): raise SystemExit("FAIL: base merger of sorted pairs")
        stats["base"]+=1; return
    sub=comps_in(layers,a,b-3,W)
    parts=components(sub,ws)
    if len(parts)!=2: raise SystemExit(f"FAIL: expected 2 sub-mergers, found {len(parts)}")
    E,O=parts if lists[0][0] in parts[0] else parts[::-1]
    Es,Os=set(E),set(O)
    for l in lists:
        if any(w not in Es for w in l[0::2]) or any(w not in Os for w in l[1::2]): raise SystemExit("FAIL: even/odd split")
    merger(layers,a,b-3,E,[l[0::2] for l in lists]); merger(layers,a,b-3,O,[l[1::2] for l in lists])
    cl=comps_in(layers,b-3,b,W); stats["comps"]+=sum(map(len,cl))
    idx={w:i for i,w in enumerate(ws)}; ei=[idx[w] for w in E]; oi=[idx[w] for w in O]; h=len(E)
    rows=[]
    for ze in range(h+1):
        for zo in range(max(0,ze-k),ze+1):
            r=np.ones(len(ws),dtype=np.uint8); r[ei[:ze]]=0; r[oi[:zo]]=0; rows.append(r)
    if not run(cl,ws,np.array(rows)): raise SystemExit("FAIL: cleanup layers")
    stats["cleanup"]+=1
net=json.load(open(sys.argv[1])); layers=[[tuple(c) for c in L] for L in net["layers"]]; n=net["n"]
for L in layers:
    u=[x for c in L for x in c]; assert len(u)==len(set(u)) and all(x<y for x,y in L) and all(0<=x<n for x in u)
if len(sys.argv)>2:   # negative control: drop one comparator
    t,i=map(int,sys.argv[2:4]); print("dropping",layers[t].pop(i),"from layer",t+1)
sorter(layers,0,len(layers),list(range(n)))
tot=sum(map(len,layers))
print(f"n={n} depth={len(layers)} size={tot}: CERTIFIED. 16-sorters {stats['sort16']}, base mergers {stats['base']}, cleanup steps {stats['cleanup']}, comparators accounted {stats['comps']} of {tot}")
assert stats["comps"]==tot
