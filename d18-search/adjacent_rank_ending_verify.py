#!/usr/bin/env python3
"""Independent direct-cone controls for the block DP; no SAT."""
import hashlib,itertools,json,random
from pathlib import Path
from adjacent_rank_ending import ending
HERE=Path(__file__).resolve().parent

def matchings(xs):
    if not xs:yield ();return
    a,*rest=xs
    yield from matchings(rest)
    for b in rest:
        for tail in matchings([v for v in rest if v!=b]):yield ((a,b),)+tail

def cones(n,network):
    answer=[]
    for c in range(n):
        reached={c}
        for layer in network:
            used=[v for e in layer for v in e];assert len(set(used))==len(used)
            reached|={v for a,b in layer if a in reached or b in reached for v in (a,b)}
        answer.append(sum(1<<v for v in reached))
    return answer

def main():
    counts={};max_states={};rng=random.Random(123456)
    for n in (4,6):
        ms=list(matchings(list(range(n))));last=[m for m in ms if all(b==a+1 for a,b in m)]
        candidates={tuple(cones(n,[p,s])) for p in ms for s in last}
        choices=[[(a,b) for a in range(c+1) for b in range(c,n)] for c in range(n)]
        families=itertools.product(*choices) if n==4 else (tuple(rng.choice(x) for x in choices) for _ in range(5000))
        count=maximum=0
        for intervals in families:
            required=[sum(1<<v for v in range(a,b+1)) for a,b in intervals]
            expected=any(all(r & ~c ==0 for r,c in zip(required,cs)) for cs in candidates)
            witness,stats=ending(intervals);assert (witness is not None)==expected,(intervals,witness)
            if witness is not None:assert all(r & ~c ==0 for r,c in zip(required,cones(n,witness)))
            assert stats['states']<=4*n and stats['transitions']<=8*n
            maximum=max(maximum,stats['states']);count+=1
        counts[n]=count;max_states[n]=maximum
    middle=[(0,3),(0,3),(0,2),(3,4),(2,5),(4,5)]
    bridge=[(0,3),(0,2),(0,2),(3,5),(2,4),(5,8),(4,6),(6,8),(6,8)]
    assert ending(middle)[0] is None and ending(bridge)[0] is None
    control_path=HERE/'results/prefix-rank-middle-round6-control.json'
    control=json.loads(control_path.read_text())
    intervals=[(r['lo'],r['hi']) for r in control['intervals']]
    witness,stats=ending(intervals);assert witness is not None
    assert all(set(range(a,b+1))<={k for k in range(18) if mask&(1<<k)}
               for (a,b),mask in zip(intervals,cones(18,witness)))
    large=[(i,i) for i in range(10000)]
    large_witness,large_stats=ending(large)
    assert large_witness is not None and large_stats['states']<=40000 and large_stats['transitions']<=80000
    report={'status':'VERIFIED','uses_sat':False,'interval_vectors':counts,'max_dp_states':max_states,
            'four_wire_exhaustive':True,'six_wire_sample_count':5000,
            'middle_pair_and_bridge_rejected':True,'known_eighteen_wire_control_passed':True,
            'large_control_n':10000,'large_control_states':large_stats['states'],
            'control_sha256':hashlib.sha256(control_path.read_bytes()).hexdigest(),
            'algorithm_sha256':hashlib.sha256((HERE/'adjacent_rank_ending.py').read_bytes()).hexdigest(),
            'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE/'results/adjacent-rank-ending-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
