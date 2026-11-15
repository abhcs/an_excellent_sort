#!/usr/bin/env python3
"""Check the explicit twelve-branch contact proof, not all nine-wire matchings."""
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
SOURCE = ROOT/'results/h9-feedback-round2-contacts.json'


def main():
    case = json.loads(SOURCE.read_text())[0]
    forbidden = {tuple(e) for e in case['fourth']}
    clauses = []
    for row in case['core']:
        clauses.append({e for e in itertools.combinations(row['real'],2)
                        if set(e)&set(row['sink']) and e not in forbidden})
    def edge(a,b): return tuple(sorted((a,b)))
    def residual(index, chosen):
        clause = clauses[index-1]
        assert not clause & chosen, ('row already satisfied',index,chosen)
        used = {x for e in chosen for x in e}
        return {e for e in clause if not set(e)&used}
    # The common-sink rows force two distinct partners hitting these three triples.
    triples = [{0,1,3},{3,4,7},{0,2,7}]
    assert not set.intersection(*triples)
    hitting = {p for p in itertools.combinations([0,1,2,3,4,6,7],2)
               if all(set(p)&t for t in triples)}
    assert hitting == {(0,3),(0,4),(0,7),(1,7),(2,3),(3,7)}
    # Each branch gives optional clause split, then forced edges, then an empty row.
    proofs = {
        (0,3): [(None,[],4)], (0,7): [(None,[],6)],
        (1,7): [(None,[],6)], (7,0): [(None,[],8)],
        (7,1): [(None,[],8)], (2,3): [(None,[],4)],
        (3,7): [(None,[],7)], (7,3): [(None,[],3)],
        (3,2): [(None,[(7,(4,7))],9)],
        (4,0): [((3,(1,3)),[(5,(2,7))],8), ((3,(2,3)),[],5)],
        (0,4): [((6,(3,7)),[(5,(1,2))],7), ((6,(2,7)),[(4,(1,3))],9)],
        (3,0): [((5,(2,7)),[],8), ((5,(1,2)),[(7,(4,7))],9)],
    }
    assert set(proofs) == {(a,b) for x,y in hitting for a,b in ((x,y),(y,x))}
    leaves = 0
    for (a,b), branches in proofs.items():
        base = {edge(5,a),edge(8,b)}
        assert len({v for e in base for v in e}) == 4
        splits = [(split[0],edge(*split[1])) for split,forces,last in branches if split]
        if splits:
            assert len({i for i,e in splits}) == 1
            assert {e for i,e in splits} == residual(splits[0][0],base)
        else:
            assert len(branches) == 1
        for split, forces, last in branches:
            chosen = set(base)
            if split: chosen.add(edge(*split[1]))
            for index,forced in forces:
                assert residual(index,chosen) == {edge(*forced)}, (a,b,index)
                chosen.add(edge(*forced))
            assert residual(last,chosen) == set(), (a,b,last)
            leaves += 1
    result = dict(status='VERIFIED', partner_pairs=6, oriented_branches=12,
                  contradiction_leaves=leaves, full_matching_enumeration=False,
                  scope='Contact-clause implication for the first normalized merger layer only; trace premises verified separately',
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  contacts_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest())
    (ROOT/'results/h9-round2-case1-branch-check.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__ == '__main__': main()
