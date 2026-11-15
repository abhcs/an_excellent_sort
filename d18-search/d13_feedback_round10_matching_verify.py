#!/usr/bin/env python3
"""Direct controls for conservation and exact mandatory matching."""
import hashlib,itertools,json,random,time
from pathlib import Path
from adjacent_rank_ending import ending as cone_ending
from d13_feedback_round8_discover import old_pass

HERE=Path(__file__).resolve().parent
FREE,LEFT,RIGHT,IMP=0,1,2,3


def matchings(xs):
    if not xs:yield ();return
    a,*rest=xs
    yield from matchings(rest)
    for b in rest:
        for tail in matchings([v for v in rest if v!=b]):yield ((a,b),)+tail


def run(n,x,layers):
    for layer in layers:
        for a,b in layer:
            if (x>>a)&1 and not (x>>b)&1:x^=(1<<a)|(1<<b)
    return x


def profiles(n,xs):
    out=[]
    for c in range(n):
        row=[]
        for j in range(n):
            flags=FREE
            for x in xs:
                k=n-x.bit_count();a=bool(x&(1<<c));b=bool(x&(1<<j))
                bit=a if j==c else a and b if c<j else a or b
                if bit==(c>=k):continue
                if c==k-1 and bit:flags|=RIGHT
                elif c==k and not bit:flags|=LEFT
                else:flags=IMP
                if flags==IMP:break
            row.append(flags)
        out.append(row)
    return out


def last_layer(n,mode,p):
    partner=list(range(n))
    for a,b in p:partner[a]=b;partner[b]=a
    if any(mode[c][partner[c]]==IMP for c in range(n)):return None
    s=set()
    for c in range(n):
        flags=mode[c][partner[c]]
        if flags&LEFT:s.add((c-1,c))
        if flags&RIGHT:s.add((c,c+1))
    assert all(0<=a<b<n for a,b in s)
    assert len({v for e in s for v in e})==2*len(s)
    return sorted(s)


def sorts(n,xs,p,s):
    return all(run(n,x,[p,s])==((1<<x.bit_count())-1)<<(n-x.bit_count()) for x in xs)


def main():
    start=time.monotonic();rng=random.Random(10152026);counts={};valid=invalid=0
    for n in range(2,7):
        ms=list(matchings(list(range(n))));ss=[s for s in ms if all(b==a+1 for a,b in s)]
        if n<=3:families=[[x for x in range(1<<n) if mask&(1<<x)] for mask in range(1<<(1<<n))]
        else:families=[rng.sample(range(1<<n),rng.randrange((1<<n)+1)) for _ in range({4:100,5:70,6:35}[n])]
        checked=0
        for xs in families:
            mode=profiles(n,xs)
            mandatory={c for c in range(n) if mode[c][c]==IMP}
            allowed={e for e in itertools.combinations(range(n),2) if mode[e[0]][e[1]]!=IMP and mode[e[1]][e[0]]!=IMP}
            for p in ms:
                condition=set(p)<=allowed and mandatory<={v for e in p for v in e}
                last=last_layer(n,mode,p)
                assert (last is not None)==condition
                direct=any(sorts(n,xs,p,s) for s in ss)
                assert condition==direct,(n,xs,p)
                if last is not None:assert sorts(n,xs,p,last);valid+=1
                else:invalid+=1
                checked+=1
        counts[n]=dict(families=len(families),fixed_P_checks=checked)
    xs=sorted({run(4,x,[[(0,1)]]) for x in range(16)})
    mode=profiles(4,xs)
    assert all(mode[c][c]==IMP for c in range(4))
    assert not any(mode[a][b]!=IMP and mode[b][a]!=IMP for a,b in itertools.combinations(range(4),2))
    intervals=[(0,2),(1,3),(0,3),(0,3)]
    assert old_pass(intervals) and cone_ending(intervals)[0] is not None
    expected={(0,1):[(0,2),(1,3)],(0,2):[(0,1),(1,3)],(0,3):[(0,1),(1,3)],
              (1,2):[(0,2),(2,3)],(1,3):[(0,2),(2,3)],(2,3):[(0,2),(1,3)]}
    table=[]
    for edge,wanted in expected.items():
        supports=[set(),set()];witnesses=[{},{}]
        for perm in itertools.permutations(range(4)):
            v=list(perm)
            for a,b in ((0,1),edge):v[a],v[b]=min(v[a],v[b]),max(v[a],v[b])
            for k,c in enumerate(edge):supports[k].add(v[c]);witnesses[k].setdefault(v[c],perm)
        assert supports==[set(range(a,b+1)) for a,b in wanted]
        table.append(dict(edge=edge,intervals=wanted,rank_witnesses=witnesses))
    # Arbitrary-family theorem is unrestricted; only the span-three reduction needs a prefix.
    xs=[((1<<(6-k))-1)<<k for k in range(7)]+[1];mode=profiles(6,xs)
    assert last_layer(6,mode,[(0,5)]) is not None
    bounded=[p for p in matchings(list(range(6))) if all(b-a<=3 for a,b in p)]
    assert not any(last_layer(6,mode,p) is not None for p in bounded)
    result=dict(status='VERIFIED',uses_sat=False,comparisons=counts,valid_modes=valid,invalid_modes=invalid,
                arbitrary_families_including_empty_checked=True,four_wire_prefix=[[(0,1)]],
                four_wire_intervals=intervals,four_wire_allowed_edges=[],four_wire_mandatory=[0,1,2,3],
                four_wire_partner_table=table,long_edge_scope_counterexample_passed=True,
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                proof_sha256=hashlib.sha256((HERE/'d13_feedback_round10_matching.md').read_bytes()).hexdigest(),seconds=time.monotonic()-start)
    (HERE/'results/d13-feedback-round10-matching-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='four_wire_partner_table'},indent=2))


if __name__=='__main__':main()
