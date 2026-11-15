#!/usr/bin/env python3
"""Check the 26-probe hand certificate for the seven/eight-wire profiles.

The proof reduces the only difficult prefix to seven third-layer forms.
Median probes force a fourth-layer matching in a small listed graph;
probes for outputs 2 and 4 then exceed the two-layer cone bound.
No SAT dependency. Discovery is not needed to verify this certificate.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

from netlib import matchings, run

FIRST = (((0, 1), (2, 3), (4, 5)), ((0, 2),))
THIRDS = [((1,2),(3,4),(5,6)), ((1,2),(3,5),(4,6)),
          ((1,3),(2,4),(5,6)), ((1,3),(2,5),(4,6)),
          ((1,4),(2,5),(3,6)), ((1,4),(2,6),(3,5)),
          ((1,5),(2,4),(3,6))]
PROBES = [(4,'01100*0'), (4,'01*1000'), (4,'00110*0'),
          (3,'*111000'), (3,'011100*'), (2,'111100*'),
          (4,'0100*10'), (3,'01*1010'), (3,'0011*10'),
          (2,'*111010'), (4,'000011*'), (3,'010011*'),
          (2,'01*1110'), (4,'010*001'), (3,'01100*1'),
          (4,'00*1001'), (3,'01010*1'), (3,'00110*1'),
          (4,'0*00011'), (3,'010*011'), (2,'011*011'),
          (2,'01*1011'), (2,'0011*11'), (3,'0*00111'),
          (2,'01*0111'), (2,'0*01111')]
CORE = ['0000','0001','0011','0100','0101','0110','0111','1111']


def corners(probe):
    return [tuple(int(c) for c in probe.replace('*', str(bit))) for bit in (0,1)]


def source(state):
    # All listed core states are fixed except 0110, obtained from 1100.
    text = ''.join(map(str, state))
    assert text[:4] in CORE and text[4:6] in ('00','01','11')
    if text[:4] == '0110':
        text = '1100' + text[4:]
    return tuple(map(int, text))


def support(probes, layers, output):
    result = set()
    for k, text in probes:
        if k != output:
            continue
        x, y = (run(layers, state) for state in corners(text))
        changed = [i for i in range(7) if x[i] != y[i]]
        assert len(changed) == 1
        result.add(changed[0])
    return result


def transform(prefix, permutation, dual=False):
    labels, result = list(permutation), []
    for layer in prefix:
        row = []
        for a,b in layer:
            low,high = (labels[b],labels[a]) if dual else (labels[a],labels[b])
            row.append(tuple(sorted((low,high))))
            if low > high:
                labels[a],labels[b] = labels[b],labels[a]
        result.append(tuple(sorted(row)))
    return tuple(result)


def check_front_reductions():
    first = FIRST[0]
    cross_cases = 0
    for gate in itertools.combinations(range(6),2):
        if gate in first:
            continue
        covered = False
        for order in itertools.permutations(range(3)):
            labels = [2*order[i//2]+i%2 for i in range(6)]+[6]
            for dual in (False,True):
                prefix = transform((first,(gate,)),labels,dual)
                assert prefix[0] == first
                covered |= prefix[1] in (((0,2),),((0,3),))
        assert covered
        cross_cases += 1
    all_layers = matchings(7)
    for gate in ((0,2),(0,3)):
        states = []
        for pairs in itertools.combinations(range(3),2):
            for bits in itertools.product((0,1),repeat=2):
                state = [0]*7
                for i,b in zip(pairs,bits):
                    state[2*i+b] = 1 if b else -1
                if state[gate[0]] == state[gate[1]] == 0:
                    continue
                states.append(run([(gate,)],state))
        positions = {tuple(i for i,v in enumerate(s) if v) for s in states}
        expected = {(0,i) for i in range(1,6)} if gate==(0,2) else {
            (0,2),(0,3),(1,3),(0,4),(0,5),(3,4),(3,5)}
        assert positions == expected
        survivors = [m for m in all_layers if all(sum(s[a]==s[b]==0 for a,b in m)>=2 for s in states)]
        if gate==(0,2):
            assert len(survivors)==15 and all(len(m)==3 and all(0 not in e for e in m) for m in survivors)
        else:
            assert not survivors
    first2 = ((0,1),(2,3))
    coverage = 0
    for second in all_layers:
        if len(second)>2:
            continue
        coverage += 1
        used = {v for edge in second for v in edge}
        if any(not set(edge)&used for edge in first2):
            continue
        idle_edges = [edge for edge in second if min(edge)>=4]
        if idle_edges:
            other = [edge for edge in second if edge not in idle_edges]
            assert len(other)==1 and all(set(other[0])&set(edge) for edge in first2)
        else:
            assert any(all(a in picked or b in picked for a,b in second)
                       for picked in itertools.product(*first2))
    assert cross_cases==12 and coverage==127
    return dict(cross_role_cases=cross_cases, thin_second_layers=coverage,
                sentinel_position_lists=2)


def check():
    front = check_front_reductions()
    certificates = []
    for k,text in PROBES:
        assert text.count('*') == 1 and text.count('1') == 6-k
        states = corners(text)
        inputs = [source(s) for s in states]
        assert all(tuple(run(FIRST,x)) == s for x,s in zip(inputs,states))
        certificates.append(dict(output=k, probe=text, inputs=inputs, states=states))
    expected = {tuple(map(int, a+b+c)) for a in CORE
                for b in ('00','01','11') for c in ('0','1')}
    actual = {tuple(run(FIRST,x)) for x in itertools.product((0,1), repeat=7)}
    assert expected == actual and len(expected) == 48

    all_layers = matchings(7)
    thirds = [m for m in all_layers if len(m)==3 and all(0 not in e for e in m) and (4,5) not in m]
    canonical = set(THIRDS)
    assert len(thirds) == 12
    for third in thirds:
        changed = transform((*FIRST,third), (2,3,0,1,4,5,6))
        assert changed[:2] == FIRST
        assert third in canonical or changed[2] in canonical
    cases = []
    for third in THIRDS:
        assert support(PROBES,[third],3) == set(range(7))
        base2 = support(PROBES,[third],2)
        edges = [e for e in itertools.combinations(range(7),2)
                 if len(support(PROBES,[third,[e]],3)) == 6]
        weights = {e: len(support(PROBES,[third,[e]],2))-len(base2) for e in edges}
        candidates = [m for m in all_layers if len(m)==3 and set(m)<=set(edges)]
        survivors = []
        for fourth in candidates:
            p2 = support(PROBES,[third,fourth],2)
            assert len(p2) == len(base2)+sum(weights[e] for e in fourth)
            if len(p2) <= 4:
                p4 = support(PROBES,[third,fourth],4)
                assert len(p4) >= 5
                survivors.append(dict(fourth=fourth, output4_positions=sorted(p4)))
        # Independent complete matching check, not used as a proof premise.
        for fourth in all_layers:
            assert max(len(support(PROBES,[third,fourth],k)) for k in (2,3,4)) >= 5
        cases.append(dict(third=third, output2_positions=sorted(base2),
                          median_edges=[dict(edge=e, weight2=weights[e]) for e in edges],
                          three_edge_matchings=len(candidates), survivors=survivors))
    return dict(probes=certificates, cases=cases, third_forms=12, representatives=7,
                fourth_matchings_per_form=len(all_layers), probe_count=len(PROBES),
                front_reductions=front,
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


def short(layer):
    return ' '.join(f'{a}{b}' for a,b in layer)


def render(result):
    lines = ['| Case | Third layer | $p_2$ | Median edges, with $w_2$ |',
             '|---|---|---:|---|']
    for i,c in enumerate(result['cases'],1):
        edges = ', '.join(f"{e['edge'][0]}{e['edge'][1]}:{e['weight2']:+d}" for e in c['median_edges'])
        lines.append(f"| {i} | `{short(c['third'])}` | {len(c['output2_positions'])} | `{edges}` |")
    lines += ['', '| Case | Remaining fourth layer | Output-4 probe positions |', '|---|---|---|']
    for i,c in enumerate(result['cases'],1):
        for s in c['survivors']:
            lines.append(f"| {i} | `{short(s['fourth'])}` | `{''.join(map(str,s['output4_positions']))}` |")
    return '\n'.join(lines)+'\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--tables', type=Path)
    args = parser.parse_args()
    result = check()
    document = Path(__file__).resolve().parents[1] / 'h7-early-profiles.md'
    text = document.read_text()
    assert render(result) in text, 'The printed proof tables disagree with the checker.'
    probe_text = '\n'.join(f'{k} {p}' for k,p in PROBES)
    assert probe_text in text, 'The printed probes disagree with the checker.'
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    if args.tables:
        args.tables.write_text(render(result))
    print(json.dumps({k:v for k,v in result.items() if k not in ('probes','cases')} |
                     {'remaining_fourth_layers':sum(len(c['survivors']) for c in result['cases'])}))
