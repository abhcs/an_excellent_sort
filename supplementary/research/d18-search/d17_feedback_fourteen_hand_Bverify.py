#!/usr/bin/env python3
"""Local checks of the five-column B lemmas; no full fourteen-wire scan."""
from itertools import combinations
import hashlib
import json
from pathlib import Path


def matchings(xs):
    if not xs:
        yield ()
        return
    a,*rest=xs
    yield from matchings(rest)
    for j,b in enumerate(rest):
        for tail in matchings(rest[:j]+rest[j+1:]):
            yield ((a,b),)+tail


def step(state,matching):
    out=list(state)
    for a,b in matching:
        out[a],out[b]=sorted((out[a],out[b]))
    return out


def near_pair(matching,sentinel_sets):
    return all(sum(a in S and b in S for a,b in matching)>=2 for S in sentinel_sets)


def contains_core(matching,cores):
    edges=set(matching)
    return any(set(core)<=edges for core in cores)


def main():
    root=Path(__file__).parent
    path606=root/'results/d17-feedback-fourteen-hand606-states.json'
    path608=root/'results/d17-feedback-fourteen-states.json'
    full606=json.loads(path606.read_text())['states']
    full608=json.loads(path608.read_text())['states']
    B606=[s[7:] for s in full606[:5]]
    B608=[s[7:] for s in full608[:5]]
    incomparable=[]
    for a,b in combinations(range(7),2):
        if not all(s[a]<=s[b] for s in B606) and not all(s[a]>=s[b] for s in B606):
            incomparable.append((a,b))
    assert incomparable==[(0,3),(0,5),(0,6)]
    local=list(matchings(list(range(7))))
    assert len(local)==232
    critical=0
    for M in local:
        exceptional=[edge for edge in M if edge in incomparable]
        assert len(exceptional)<=1
        critical+=(0,3) in M
        swaps=[]
        for a,b in M:
            if (a,b) in exceptional:
                continue
            if not all(s[a]<=s[b] for s in B606):
                assert all(s[a]>=s[b] for s in B606)
                swaps.append((a,b))
        for s in B606:
            predicted=step(s,exceptional)
            for a,b in swaps:
                predicted[a],predicted[b]=predicted[b],predicted[a]
            assert predicted==step(s,M)
    assert critical==26
    allN=list(matchings(list(range(9))))
    assert len(allN)==2620
    ordinary=((2,4),(3,5),(7,8))
    exceptional_cores=[ordinary]
    exceptional_cores += [tuple(sorted(((1,2),(5,6),*p)))
                          for p in matchings([3,4,7,8]) if len(p)==2]
    canonical=[]
    for name,M in [('none',()),('de',((0,5),)),('dr',((0,6),)),('dc',((0,3),))]:
        families=[{i for i,x in enumerate(step(s,M)) if x!=0}|{7,8} for s in B606]
        cores=exceptional_cores if name=='dc' else [ordinary]
        good=[]
        for N in allN:
            actual=near_pair(N,families)
            assert actual==contains_core(N,cores),(name,N)
            if actual:
                good.append(N)
        canonical.append(dict(first_gate=name,solutions=len(good),
                              bypasses=sum((7,8) not in N for N in good),cores=cores))
    bypass=((1,2),(3,7),(4,8),(5,6))
    assert near_pair(bypass,[{i for i,x in enumerate(step(s,[(0,3)])) if x}|{7,8} for s in B606])
    assert (7,8) not in bypass
    cores608=[tuple(sorted(((1,2),(5,6),*p)))
              for p in matchings([0,4,7,8]) if len(p)==2]
    family608=[{i for i,x in enumerate(s) if x}|{7,8} for s in B608]
    good608=0
    for N in allN:
        actual=near_pair(N,family608)
        assert actual==contains_core(N,cores608)
        good608+=actual
    assert good608==3
    controls=[]
    for case,states in [(606,full606),(608,full608)]:
        p=root/f'results/d17-feedback-fourteen-hand-fourbyfour{case}/result.json'
        record=json.loads(p.read_text())
        assert record['status']=='SURVIVOR'
        profiles=[]
        for s in states:
            cur=list(s);counts=[]
            for matching in record['next_layers']:
                endpoints=[v for e in matching for v in e]
                assert len(endpoints)==len(set(endpoints))
                counts.append(sum(cur[a]==cur[b]==0 for a,b in matching))
                cur=step(cur,matching)
            profiles.append(counts)
        assert [profiles[i] for i in record['indices']]==record['profiles']
        assert all(max(profiles[i])==4 for i in record['indices'])
        failing=[i for i,p in enumerate(profiles) if max(p)<4]
        assert failing
        controls.append(dict(case=case,covered_indices=record['indices'],
                             failing_full_family_indices=failing,profiles=profiles))
    result=dict(status='VERIFIED',scope='Local B-family normalization and static matching classifications only',
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                input_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path606,path608]},
                incomparable_B_pairs=incomparable,B_matchings=len(local),
                critical_B_matchings=critical,static_matchings_per_family=len(allN),
                canonical606=canonical,static608_solutions=good608,cores608=cores608,
                critical_bypass=bypass,fourbyfour_controls=controls,
                sat_used_by_verifier=False,complete_fourteen_wire_hand_proof=False)
    out=root/'results/d17-feedback-fourteen-hand-Blemma-verified.json'
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('input_sha256','fourbyfour_controls')},indent=2))


if __name__=='__main__':
    main()
