#!/usr/bin/env python3
"""Independent truth-table controls for the substituted two-layer clauses."""
import hashlib,itertools,json,time
from pathlib import Path
from two_layer_data_ending import add_data_ending

HERE=Path(__file__).resolve().parent
def matchings(vertices):
    if not vertices:yield ();return
    a,*rest=vertices
    yield from matchings(rest)
    for b in rest:
        for m in matchings([c for c in rest if c!=b]):yield ((a,b),)+m
class Recorder:
    def __init__(self,n):
        self.n=n;self.ncl=0;self.clauses=[];v=n;self.g=[]
        for adjacent in (False,True):
            layer={}
            for i,j in itertools.combinations(range(n),2):
                if not adjacent or j==i+1:v+=1;layer[i,j]=v
            self.g.append(layer)
        self.nv=v
    def add(self,c):self.clauses.append(c);self.ncl+=1
def actual(n,x,p,s):
    a=[(x>>i)&1 for i in range(n)]
    for layer in (p,s):
        for i,j in layer:a[i],a[j]=min(a[i],a[j]),max(a[i],a[j])
    return a==sorted(a)
def main():
    start=time.monotonic();counts={};positive=negative=0
    for n in range(2,7):
        ms=list(matchings(list(range(n))));last=[m for m in ms if all(j==i+1 for i,j in m)]
        count=0
        for k in range(n+1):
            # The clauses depend on x only through its weight; all data bits
            # below remain separate symbolic variables, then fixed by each run.
            representative=(1<<(n-k))-1
            model=Recorder(n);add_data_ending(model,{representative:{i:i+1 for i in range(n)}})
            for p,s in itertools.product(ms,last):
                gates={model.g[t][e] for t,layer in enumerate((p,s)) for e in layer}
                reduced=[]
                for clause in model.clauses:
                    if any(abs(v)>n and ((v>0)==(abs(v) in gates)) for v in clause):continue
                    reduced.append([v for v in clause if abs(v)<=n])
                for ones in itertools.combinations(range(n),n-k):
                    x=sum(1<<c for c in ones);bits={c+1 for c in ones}
                    accepted=all(any((v>0)==(abs(v) in bits) for v in clause) for clause in reduced)
                    expected=actual(n,x,p,s)
                    assert accepted==expected,(n,x,p,s,accepted,expected)
                    positive+=accepted;negative+=not accepted;count+=1
        counts[n]=count
    result=dict(status='VERIFIED',uses_sat=False,all_binary_states_and_matchings=True,
                counts=counts,accepted=positive,rejected=negative,seconds=time.monotonic()-start,
                source_sha256=hashlib.sha256((HERE/'two_layer_data_ending.py').read_bytes()).hexdigest(),
                checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (HERE/'results/two-layer-data-ending-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
