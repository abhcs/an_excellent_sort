#!/usr/bin/env python3
"""Check the short case3 contact proof, without enumerating9-wire matchings."""
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    case = json.loads((ROOT / 'results/h9-feedback-round2-contacts.json').read_text())[2]
    forbidden = {tuple(edge) for edge in case['fourth']}
    assert forbidden == {(1,8), (2,4), (3,6), (5,7)}
    contacts = []
    for row in case['core']:
        contacts.append({edge for edge in itertools.combinations(row['real'],2)
                         if set(edge) & set(row['sink']) and edge not in forbidden})

    def edge(a,b):
        return tuple(sorted((a,b)))

    def residual(row, selected):
        clause = contacts[row-1]
        if clause & selected:
            return None
        occupied = {v for e in selected for v in e}
        return {e for e in clause if not set(e)&occupied}

    options = [(a,b) for a in (3,4,7) for b in (0,2,5) if a != 4 or b == 0]
    assert len(options) == 7
    # Independently derive the partner possibilities from rows3,5,6.
    derived = []
    for a in [None,0,2,3,4,5,6,7]:
        for b in [None,0,2,3,4,5,6,7]:
            if a is not None and a == b:
                continue
            selected = ({edge(1,a)} if a is not None else set()) | ({edge(8,b)} if b is not None else set())
            if all(contacts[r-1]&selected for r in (3,5,6)):
                derived.append((a,b))
    assert set(derived) == {(x,y) for a,b in options for x,y in ((a,b),(b,a))}

    # (partners of1,8): successive forced rows, final empty row.
    direct = {
        (3,0): ([],1), (0,3): ([],1),
        (2,3): ([(9,(4,7))],10),
        (3,5): ([(1,(0,7))],7), (5,3): ([(2,(4,7))],10),
        (0,4): ([],4),
        (7,0): ([],7), (0,7): ([(1,(3,5))],4),
        (7,2): ([],7), (2,7): ([(9,(3,4))],10),
        (7,5): ([],7),
    }
    for (a,b),(forced,empty) in direct.items():
        selected = {edge(1,a),edge(8,b)}
        for row,e in forced:
            assert residual(row,selected) == {e}
            selected.add(e)
        assert residual(empty,selected) == set()

    leaves = {
        (3,2): [(1,{(0,5),(0,7)}),(2,{(4,5),(4,7)}),
                (7,{(4,7),(6,7)}),(8,{(4,6),(6,7)})],
        (4,0): [(1,{(3,5),(3,7)}),(7,{(3,7),(6,7)}),(9,{(2,3),(2,7)})],
        (5,7): [(8,{(3,4),(4,6)}),(9,{(2,3),(3,4)}),(10,{(0,3),(0,4)})],
    }
    choice_checks = 0
    for (a,b),requirements in leaves.items():
        selected = {edge(1,a),edge(8,b)}
        for row,clause in requirements:
            assert residual(row,selected) == clause
        for choices in itertools.product(*(clause for _,clause in requirements)):
            pairs = set(choices)
            endpoints = [v for pair in pairs for v in pair]
            assert len(endpoints) != len(set(endpoints))
            choice_checks += 1
    assert set(direct)|set(leaves) == set(derived)
    print(json.dumps(dict(status='VERIFIED', partner_orientations=len(derived),
                          immediate_or_forced_branches=len(direct), small_leaves=len(leaves),
                          leaf_choice_checks=choice_checks, full_matching_enumeration=False)))


if __name__ == '__main__':
    main()
