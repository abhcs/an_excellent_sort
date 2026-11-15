#!/usr/bin/env python3
"""Independent fixed-assignment validation of the local capacity CNF."""
import hashlib,itertools,json,random
from pathlib import Path
from rank_block_capacity_cnf import add_block_capacity
HERE=Path(__file__).resolve().parent

class Formula:
    def __init__(self,n):
        self.n=n;self.nv=0;self.clauses=[]
        self.g=[{(i,i+1):self.var() for i in range(n-1)}]
        self.lower=[[True]+[self.var() for _ in range(n-1)]+[False] for _ in range(n)]
        self.upper=[[False]+[self.var() for _ in range(n-1)]+[True] for _ in range(n)]
    def var(self):self.nv+=1;return self.nv
    def add(self,c):self.clauses.append(c)
    def accepts(self,intervals,last):
        values={v:edge in last for edge,v in self.g[0].items()}
        for c,(lo,hi) in enumerate(intervals):
            for k in range(1,self.n):
                values[self.lower[c][k]]=lo>=k
                values[self.upper[c][k]]=hi<k
        return all(any(values[abs(v)]==(v>0) for v in clause) for clause in self.clauses)

def matchings(xs):
    if not xs:yield ();return
    a,*rest=xs
    yield from matchings(rest)
    for b in rest:
        for tail in matchings([v for v in rest if v!=b]):yield ((a,b),)+tail

def cones(n,p,s):
    result=[]
    for c in range(n):
        reached={c}
        for layer in (p,s):
            reached|={v for a,b in layer if a in reached or b in reached for v in (a,b)}
        result.append(sum(1<<v for v in reached))
    return result

def main():
    counts={};clause_counts={};rng=random.Random(20261116)
    for n in (3,4,5,6):
        formula=Formula(n);before=formula.nv;stats=add_block_capacity(formula,formula.lower,formula.upper)
        assert formula.nv==before
        clause_counts[n]=stats
        ms=list(matchings(list(range(n))));lasts=[s for s in ms if all(b==a+1 for a,b in s)]
        choices=[[(a,b) for a in range(c+1) for b in range(c,n)] for c in range(n)]
        count=0
        for s in lasts:
            candidates=[cones(n,p,s) for p in ms]
            families=itertools.product(*choices) if n<=4 else (tuple(rng.choice(x) for x in choices) for _ in range(500))
            for intervals in families:
                masks=[sum(1<<v for v in range(a,b+1)) for a,b in intervals]
                direct=any(all(r&~c==0 for r,c in zip(masks,cs)) for cs in candidates)
                assert formula.accepts(intervals,s)==direct,(n,intervals,s)
                count+=1
        counts[n]=count
    for n in (13,18):
        f=Formula(n);clause_counts[n]=add_block_capacity(f,f.lower,f.upper)
    report=dict(status='VERIFIED',uses_sat=False,comparisons=counts,clause_counts=clause_counts,
        source_sha256=hashlib.sha256((HERE/'rank_block_capacity_cnf.py').read_bytes()).hexdigest(),
        checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (HERE/'results/rank-block-capacity-cnf-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
