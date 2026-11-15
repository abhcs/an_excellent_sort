#!/usr/bin/env python3
"""Direct bounded-ending checks of the symbolic path CNF on fixed families."""
import hashlib,itertools,json,random,time
from pathlib import Path
from pysat.solvers import Solver
from two_layer_matching_ending import add_matching_ending
HERE=Path(__file__).resolve().parent
class Recorder:
    def __init__(self,n):
        self.n=n;self.nv=0;self.ncl=0;self.clauses=[]
        pen={e:self.new_var() for e in itertools.combinations(range(n),2)}
        self.g=[pen,{}]
        for c in range(n):
            incident=[v for e,v in pen.items() if c in e]
            for u,v in itertools.combinations(incident,2):self.add([-u,-v])
    def new_var(self):self.nv+=1;return self.nv
    def add(self,clause):self.clauses.append(clause);self.ncl+=1
def matchings(v):
    if not v:yield ();return
    a,*rest=v
    yield from matchings(rest)
    for b in rest:
        for tail in matchings([c for c in rest if c!=b]):yield ((a,b),)+tail
def run(n,x,layers):
    v=[bool(x>>i&1) for i in range(n)]
    for layer in layers:
        for a,b in layer:v[a],v[b]=min(v[a],v[b]),max(v[a],v[b])
    return sum(int(bit)<<i for i,bit in enumerate(v))
def sorts(n,xs,layers):
    return all(run(n,x,layers)==((1<<x.bit_count())-1)<<(n-x.bit_count()) for x in xs)
def main():
    start=time.monotonic();rng=random.Random(1102026);counts={};yes=no=0
    for n in range(2,7):
        ms=list(matchings(list(range(n))));pm=[m for m in ms if all(b-a<=3 for a,b in m)];sm=[m for m in ms if all(b-a==1 for a,b in m)]
        families=[]
        for _ in range(20):
            prefix=[rng.choice(ms) for _ in range(rng.randrange(7))]
            families.append(sorted({run(n,x,prefix) for x in range(1<<n)}))
        families += [sorted(rng.sample(range(1<<n),rng.randrange(1,1<<n))) for _ in range(10)]
        for xs in families:
            rec=Recorder(n)
            stats=add_matching_ending(rec,{x:{i:bool(x>>i&1) for i in range(n)} for x in xs})
            direct=any(sorts(n,xs,[p,s]) for p,s in itertools.product(pm,sm))
            with Solver(name='cadical195',bootstrap_with=rec.clauses) as solver:got=solver.solve()
            assert got==direct,(n,xs,got,direct)
            yes+=got;no+=not got
        counts[n]=len(families)
    # Essential scope control: arbitrary family needs a long penultimate gate.
    n=6;xs=[((1<<(n-k))-1)<<k for k in range(n+1)]+[1]
    assert sorts(n,xs,[[(0,5)],[]])
    rec=Recorder(n);add_matching_ending(rec,{x:{i:bool(x>>i&1) for i in range(n)} for x in xs})
    with Solver(name='cadical195',bootstrap_with=rec.clauses) as solver:assert not solver.solve()
    report=dict(status='VERIFIED',small_sat_controls=True,comparisons=counts,accepted=yes,rejected=no,
                scope_counterexample_passed=True,seconds=time.monotonic()-start,
                source_sha256=hashlib.sha256((HERE/'two_layer_matching_ending.py').read_bytes()).hexdigest(),
                checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (HERE/'results/two-layer-matching-ending-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
