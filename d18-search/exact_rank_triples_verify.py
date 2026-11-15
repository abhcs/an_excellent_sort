#!/usr/bin/env python3
"""Independent complete binary/real-order controls for endpoint exactness."""
import hashlib,itertools,json,random
from pathlib import Path
from exact_rank_triples import add_exact_endpoints,add_no_full_triples
HERE=Path(__file__).resolve().parent

class Formula:
    def __init__(self,n):
        self.n=n;self.nv=0;self.clauses=[]
        self.lower=[[True]+[self.var() for _ in range(n-1)]+[False] for _ in range(n)]
        self.upper=[[False]+[self.var() for _ in range(n-1)]+[True] for _ in range(n)]
    def var(self):self.nv+=1;return self.nv
    def add(self,c):self.clauses.append(c)
    def accepts(self,intervals):
        values={}
        for c,(lo,hi) in enumerate(intervals):
            for k in range(1,self.n):
                values[self.lower[c][k]]=lo>=k;values[self.upper[c][k]]=hi<k
        def truth(v):return v if isinstance(v,bool) else values[abs(v)]==(v>0)
        return all(any(truth(v) for v in clause) for clause in self.clauses)

def run(prefix,x):
    y=list(x)
    for layer in prefix:
        for a,b in layer:y[a],y[b]=min(y[a],y[b]),max(y[a],y[b])
    return y

def matchings(xs):
    if not xs:yield ();return
    a,*rest=xs
    yield from matchings(rest)
    for b in rest:
        for tail in matchings([v for v in rest if v!=b]):yield ((a,b),)+tail

def main():
    layers=list(matchings(list(range(4))))
    examples=[(4,[a,b]) for a in layers for b in layers]
    examples += [(4,[[(0,3)],[(1,3)],[(2,3)]]),(5,[[(1,3)],[(1,2)],[(2,3)],[(0,2),(3,4)],[(1,4),(2,3)]])]
    rng=random.Random(314159);m5=list(matchings(list(range(5))))
    examples += [(5,[rng.choice(m5) for _ in range(5)]) for _ in range(25)]
    vectors=0;real_runs=0;binary_runs=0;forbidden=0
    for n,prefix in examples:
        support=[set() for _ in range(n)]
        for permutation in itertools.permutations(range(n)):
            for c,value in enumerate(run(prefix,permutation)):support[c].add(value)
            real_runs+=1
        actual=[(min(s),max(s)) for s in support]
        states={x:run(prefix,[bool(x&(1<<c)) for c in range(n)]) for x in range(1<<n)}
        binary_runs+=len(states)
        f=Formula(n)
        # Existing forward implications, written independently with fixed bits.
        for x,state in states.items():
            k=n-x.bit_count()
            for c,value in enumerate(state):
                f.add([not f.lower[c][k] if isinstance(f.lower[c][k],bool) else -f.lower[c][k],value])
                f.add([not f.upper[c][k] if isinstance(f.upper[c][k],bool) else -f.upper[c][k],not value])
        add_exact_endpoints(f,states,f.lower,f.upper)
        for c in range(n):
            for lo in range(c+1):
                for hi in range(c,n):
                    trial=actual[:];trial[c]=(lo,hi)
                    assert f.accepts(trial)==(trial==actual),(n,prefix,trial,actual)
                    vectors+=1
        triple=Formula(n);add_no_full_triples(triple,triple.lower,triple.upper)
        bad=any(all(actual[c]==(a,a+2) for c in range(a,a+3)) for a in range(n-2))
        assert triple.accepts(actual)==(not bad)
        forbidden+=bad
    assert forbidden>=2
    report=dict(status='VERIFIED',uses_sat=False,prefixes=len(examples),real_order_runs=real_runs,
        complete_binary_runs=binary_runs,endpoint_vectors_checked=vectors,triple_examples_rejected=forbidden,
        source_sha256=hashlib.sha256((HERE/'exact_rank_triples.py').read_bytes()).hexdigest(),
        checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (HERE/'results/exact-rank-triples-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
