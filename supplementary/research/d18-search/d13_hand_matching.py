#!/usr/bin/env python3
"""Exact one-layer multi-rank obstruction, without a SAT solver."""
import json
from pathlib import Path
from itertools import combinations
from functools import lru_cache


def wire_functions(n, layers):
    total = 1 << n
    full = (1 << total) - 1
    fs = []
    levels = [0] * (n + 1)
    for x in range(total):
        levels[x.bit_count()] |= 1 << x
    for k in range(n):
        h = 1 << k
        fs.append((((1 << h) - 1) << h) * (full // ((1 << (2 * h)) - 1)))
    for layer in layers:
        for a, b in layer:
            fs[a], fs[b] = fs[a] & fs[b], fs[a] | fs[b]
    return fs, levels, full


def rank_interval(f, levels, full, n):
    one = next(w for w in range(n+1) if f & levels[w])
    zero = n - next(w for w in range(n, -1, -1) if (~f & full) & levels[w])
    return zero-1, n-one


def analyze(n, layers, bound=4):
    fs, levels, full = wire_functions(n, layers)
    intervals = [rank_interval(f,levels,full,n) for f in fs]
    supports = [[c for c,(lo,hi) in enumerate(intervals) if lo<=k<=hi] for k in range(n)]
    edge_ranks = {}
    edge_intervals = {}
    for a,b in combinations(range(n),2):
        ia = rank_interval(fs[a]&fs[b], levels, full, n)
        ib = rank_interval(fs[a]|fs[b], levels, full, n)
        edge_intervals[a,b] = (ia,ib)
        gains=[]
        for k in range(n):
            before = int(a in supports[k])+int(b in supports[k])
            after = int(ia[0]<=k<=ia[1])+int(ib[0]<=k<=ib[1])
            assert before-after in (0,1)
            if before-after: gains.append(k)
        edge_ranks[a,b]=gains
    return dict(n=n,layers=layers,intervals=intervals,supports=supports,
                demands=[max(0,len(s)-bound) for s in supports],
                edge_ranks={f'{a},{b}':v for (a,b),v in edge_ranks.items()},
                edge_intervals={f'{a},{b}':v for (a,b),v in edge_intervals.items()})


def max_matching(n,weights):
    @lru_cache(None)
    def dp(mask):
        if not mask:return 0,()
        a=(mask&-mask).bit_length()-1
        rem=mask^(1<<a)
        best=dp(rem)
        for b in range(a+1,n):
            if rem>>b&1:
                value,edges=dp(rem^(1<<b))
                cand=value+weights.get((a,b),0)
                if cand>best[0]:best=cand,((a,b),)+edges
        return best
    return dp((1<<n)-1)


def search_subsets(data):
    n=data['n'];dem=data['demands']
    ranks=[k for k in range(n) if dem[k]]
    ed={tuple(map(int,k.split(','))):v for k,v in data['edge_ranks'].items()}
    out=[]
    for size in range(1,len(ranks)+1):
        for subset in combinations(ranks,size):
            weights={e:sum(k in vals for k in subset) for e,vals in ed.items()}
            cap,matching=max_matching(n,weights)
            need=sum(dem[k] for k in subset)
            if cap<need:
                out.append(dict(ranks=subset,demand=need,maximum=cap,matching=matching))
        if out:break
    return out


def main():
    root=Path(__file__).parent
    positive=json.loads((root/'results/probe-frontier13-d9-positive.json').read_text())
    net=positive['prefix']+positive['free_layers']+positive['ending_matchings']
    median=[[(0,1),(2,3),(4,5),(6,7),(8,9),(10,11)],[(0,8),(1,9),(2,6),(3,7),(4,10),(5,11)],[(0,2),(1,5),(3,8),(4,6),(7,9),(10,12)],[(0,9),(1,8),(2,12),(3,4),(5,6),(7,11)],[(0,6),(1,2),(4,10),(5,7),(8,12)],[(1,5),(2,4),(6,10),(7,8)]]
    result={}
    for name,layers in [('case116_d9_first5',net[:5]),('median_first5',median[:5]),('case116_d9_first6_positive',net[:6])]:
        data=analyze(13,layers)
        data['subset_obstructions']=search_subsets(data)
        result[name]=data
        print(name,'sizes',list(map(len,data['supports'])),'obstructions',data['subset_obstructions'][:3],flush=True)
    path=root/'results/d13-hand-matching-analysis.json'
    path.write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
