#!/usr/bin/env python3
"""Independent graph, packing, exhaustive-type, and value controls."""
import hashlib
import itertools
import json
from pathlib import Path
import random
import subprocess
import tempfile
import time

from netsat import verify_all

HERE = Path(__file__).parent


def pack(sizes, caps):
    if not sizes:
        return True
    a, *rest = sizes
    return any(pack(rest, caps[:i]+(c-a,)+caps[i+1:])
               for i,c in enumerate(caps) if c >= a)


def analyze(n, layers, initial):
    types = list(initial)
    labels = [i if v == 0 else -1 for i,v in enumerate(types)]
    adjacency = {i:set() for i in labels if i >= 0}
    gates = []
    for layer in layers:
        for a,b in layer:
            if types[a] == types[b] == 0:
                u,v = labels[a],labels[b]
                adjacency[u].add(v); adjacency[v].add(u)
                gates.append((u,v))
            elif types[a] > types[b]:
                types[a],types[b] = types[b],types[a]
                labels[a],labels[b] = labels[b],labels[a]
    unseen = set(adjacency)
    components = []
    while unseen:
        component = {min(unseen)}
        todo = list(component)
        while todo:
            for v in adjacency[todo.pop()] - component:
                component.add(v); todo.append(v)
        unseen -= component
        components.append(component)
    masks = sorted(sum(1<<wire for wire,label in enumerate(labels) if label in comp)
                   for comp in components)
    return masks, labels, gates, types


def call(binary, path, n, layers, mode, all_states=True):
    rows = [f'{n} {len(layers)}']
    for layer in layers:
        mates = [-1]*n
        for a,b in layer:
            assert 0 <= a < b < n and mates[a] == mates[b] == -1
            mates[a],mates[b] = b,a
        rows.append(' '.join(map(str,mates)))
    path.write_text('\n'.join(rows)+'\n')
    command = [str(binary),str(path),mode]+(['all'] if all_states else [])
    run = subprocess.run(command,capture_output=True,text=True,check=True,timeout=20)
    return json.loads(run.stdout)


def value_check(n,layers,witness):
    initial = witness['initial']
    masks,labels,gates,types = analyze(n,layers,initial)
    assert masks == witness['cut_component_masks'] and labels == witness['final_labels']
    positions = [v for v,t in enumerate(initial) if t == 0]
    count = 0
    for bits in itertools.product((0,1),repeat=9):
        registers = dict(zip(positions,bits))
        values = [-2 if t<0 else 2 if t>0 else registers[i] for i,t in enumerate(initial)]
        for layer in layers:
            for a,b in layer:
                values[a],values[b] = min(values[a],values[b]),max(values[a],values[b])
        for a,b in gates:
            registers[a],registers[b] = min(registers[a],registers[b]),max(registers[a],registers[b])
        predicted = [registers[label] if label>=0 else -2 if t<0 else 2 for label,t in zip(labels,types)]
        assert values == predicted
        count += 1
    return count


def main():
    started=time.monotonic();rng=random.Random(432333)
    tests=0;type_assignments=0;value_runs=0
    def random_layer(n):
        vertices=list(range(n));rng.shuffle(vertices)
        return sorted(tuple(sorted(vertices[i:i+2])) for i in range(0,2*rng.randrange(n//2+1),2))
    def partitions(total,maximum):
        if total==0:
            yield ()
        for first in range(min(total,maximum),0,-1):
            for tail in partitions(total-first,first):yield (first,)+tail
    all_parts=list(partitions(9,9))
    for sizes in all_parts:
        assert pack(sizes,(4,3,2)) == (max(sizes)<=4 and sizes not in ((4,4,1),(3,3,3)))
        assert (pack(sizes,(4,3,2)) or pack(sizes,(3,3,3))) == (max(sizes)<=4 and sizes!=(4,4,1))
        assert (pack(sizes,(4,3,2)) or pack(sizes,(3,3,3)) or pack(sizes,(4,4,1))) == (max(sizes)<=4)
    with tempfile.TemporaryDirectory(prefix='merge-component-check-') as temporary:
        temp=Path(temporary);binary=temp/'collect';path=temp/'prefix.txt'
        subprocess.run(['c++','-O3','-std=c++17',str(HERE/'merge_component_states.cpp'),'-o',str(binary)],check=True,capture_output=True,timeout=20)
        for n in (9,10,11):
            for _ in range(12):
                layers=[random_layer(n) for _ in range(rng.randrange(1,6))]
                for mode in ('432','both','max4'):
                    expected=set()
                    for sentinels in itertools.combinations(range(n),n-9):
                        for signs in itertools.product((-1,1),repeat=n-9):
                            initial=[0]*n
                            for v,s in zip(sentinels,signs):initial[v]=s
                            masks,labels,gates,types=analyze(n,layers,initial)
                            sizes=sorted((m.bit_count() for m in masks),reverse=True)
                            if (pack(sizes,(4,3,2)) or mode in ('both','max4') and pack(sizes,(3,3,3))
                                    or mode=='max4' and pack(sizes,(4,4,1))):
                                expected.add(tuple(masks))
                            type_assignments+=1
                    got=call(binary,path,n,layers,mode)
                    assert {tuple(w['cut_component_masks']) for w in got['witnesses']} == expected
                    value_runs += sum(value_check(n,layers,w) for w in got['witnesses'][:2])
                    tests+=1
        blocks=[[(0,1),(2,3),(4,5)],[(0,3),(1,2),(4,6)],[(0,1),(2,3),(5,6),(7,8)]]
        planted=blocks+[[],[],[]]
        plant=call(binary,path,18,planted,'max4',False)
        assert plant['accepted_placements']>0
        value_runs += sum(value_check(18,planted,w) for w in plant['witnesses'])
        positive=json.loads((HERE/'results/dobbelaere18-78-11.json').read_text())
        assert verify_all(18,positive['layers'])
        # Four layers remain after cut7 in this genuine depth11 sorter.
        control=call(binary,path,18,positive['layers'][:7],'max4',False)
        assert control['accepted_placements']==0
    report=dict(status='VERIFIED',small_prefix_tests=tests,all_type_assignments=type_assignments,
                integer_partitions=len(all_parts),binary_functional_replays=value_runs,
                planted_obstruction_placements=plant['accepted_placements'],
                positive_sorter_binary_inputs=1<<18,positive_sorter_cut7_accepted=control['accepted_placements'],
                seconds=time.monotonic()-started,
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                collector_sha256=hashlib.sha256((HERE/'merge_component_states.cpp').read_bytes()).hexdigest(),
                scope='Small exhaustive-type and direct value controls, plus planted obstruction and known sorter; not a complete D18 cover')
    (HERE/'results/merge-component-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)


if __name__=='__main__':main()
