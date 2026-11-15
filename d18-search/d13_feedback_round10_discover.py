#!/usr/bin/env python3
"""One bounded non-SAT search for a nonisolated mandatory Hall obstruction."""
import itertools,json,random,time
from pathlib import Path
from adjacent_rank_ending import ending
from d13_feedback_round8_discover import old_pass
from d13_feedback_round10_matching_verify import profiles,run,matchings,IMP
HERE=Path(__file__).resolve().parent


def main():
    start=time.monotonic();rng=random.Random(1020261115)
    ms={n:list(matchings(list(range(n)))) for n in (6,7,8)}
    trials=checks=0;seen=set();hit=None
    while time.monotonic()-start<24:
        n=rng.choice((6,7,8));xs=list(range(1<<n));prefix=[]
        for depth in range(15):
            layer=rng.choice(ms[n][1:]);prefix.append(layer)
            xs=sorted({run(n,x,[layer]) for x in xs})
            key=n,tuple(xs)
            if key in seen:continue
            seen.add(key)
            iv=tuple((min(n-x.bit_count()-1 for x in xs if not x&(1<<c)),
                      max(n-x.bit_count() for x in xs if x&(1<<c))) for c in range(n))
            if not old_pass(iv) or any(all(iv[c]==(a,a+2) for c in range(a,a+3)) for a in range(n-2)):continue
            if ending(iv)[0] is None:continue
            mode=profiles(n,xs);mandatory={c for c in range(n) if mode[c][c]==IMP}
            if len(mandatory)<2:continue
            edges={e for e in itertools.combinations(range(n),2) if mode[e[0]][e[1]]!=IMP and mode[e[1]][e[0]]!=IMP}
            neighbors={c:{b if a==c else a for a,b in edges if c in (a,b)} for c in range(n)}
            if any(not neighbors[c] for c in mandatory):continue
            checks+=1
            witness=None
            for size in range(2,len(mandatory)+1):
                for vertices in itertools.combinations(sorted(mandatory),size):
                    u=set(vertices)
                    if any(a in u and b in u for a,b in edges):continue
                    hood=set().union(*(neighbors[c] for c in vertices))
                    if len(hood)<len(u):witness=dict(mandatory_set=vertices,neighbors=sorted(hood));break
                if witness:break
            if witness:
                hit=dict(n=n,prefix=prefix[:],intervals=iv,cut_states=xs,allowed_edges=sorted(edges),
                         mandatory=sorted(mandatory),hall=witness)
                break
        trials+=1
        if hit:break
    report=dict(status='TERMINATED_NORMALLY',uses_sat=False,wall_budget_seconds=24,
                seconds=time.monotonic()-start,trials=trials,nonisolated_graphs_checked=checks,hit=hit)
    (HERE/'results/d13-feedback-round10-discovery.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
