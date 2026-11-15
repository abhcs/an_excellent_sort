#!/usr/bin/env python3
"""Check the explicit rank witnesses in the 711 hand proof; no SAT."""
import hashlib
import itertools
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent

def after(i,u,v):
    values=[x for x in range(9) if x not in (u,v)]+[u,v]
    for a,b in ((i,7),(4,8)):
        values[a],values[b]=min(values[a],values[b]),max(values[a],values[b])
    return values


def main():
    starts=[(i,j) for i,j in itertools.combinations(range(7),2)
            if all(set((i,j))&set(range(k,k+3)) for k in range(5))]
    assert starts==[(1,4),(2,4),(2,5)]
    # i,pivot,partners,output,low input,low bound,high input,high bound
    rows=[
        (1,7,[0,1,2],'max',(3,8),3,(8,7),8),
        (1,7,[3],'max',(0,8),4,(8,7),8),
        (1,7,[4],'max',(0,1),3,(8,7),8),
        (1,7,[5,6],'min',(0,8),2,(8,0),6),
        (1,7,[8],'min',(0,8),2,(7,6),6),
        (2,7,[0,1,2],'max',(3,8),3,(8,7),8),
        (2,7,[3],'max',(0,8),4,(8,7),8),
        (2,7,[4],'max',(0,1),4,(8,7),8),
        (2,7,[6],'min',(0,8),3,(8,0),7),
        (2,7,[8],'min',(0,8),3,(8,7),7),
        (2,4,[0],'max',(8,0),1,(0,8),5),
        (2,4,[2],'max',(0,1),1,(0,8),5),
        (2,4,[3],'min',(8,0),0,(0,8),4),
        (2,4,[6,8],'min',(8,0),0,(0,8),5)]
    checks=0
    for i,pivot,partners,kind,low,l,high,h in rows:
        function=min if kind=='min' else max
        x,y=after(i,*low),after(i,*high)
        assert h-l>=4
        for p in partners:
            assert function(x[pivot],x[p])<=l and function(y[pivot],y[p])>=h
            checks+=1
    intervals=[]
    for i in (1,2):
        outputs=[after(i,u,v) for u,v in itertools.permutations(range(9),2)]
        for wire in range(9):
            ranks={x[wire] for x in outputs}
            assert ranks==set(range(min(ranks),max(ranks)+1))
        intervals.append([sorted({x[w] for x in outputs}) for w in range(9)])
    forced=[]
    for u,v in itertools.permutations(range(9),2):
        x=after(2,u,v)
        for a,b in ((1,4),(5,7)):
            x[a],x[b]=min(x[a],x[b]),max(x[a],x[b])
        forced.append(x)
    assert {x[4] for x in forced}=={2,3,4,5}
    assert {x[5] for x in forced}=={3,4,5,6}
    report=dict(status='VERIFIED',uses_sat=False,first_partner_pairs=starts,
        displayed_rows=len(rows),excluded_partner_checks=checks,
        interleavings_per_start=72,rank_intervals=intervals,
        forced_final_intervals=[[2,3,4,5],[3,4,5,6]],intersection_size=3,
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        proof_sha256=hashlib.sha256((HERE/'merger711-hand-reduction.md').read_bytes()).hexdigest())
    (HERE/'results/merger711-hand-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='rank_intervals'}))

if __name__=='__main__':main()
