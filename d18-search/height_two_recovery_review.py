#!/usr/bin/env python3
"""Finite audit of exact images under extremal-compatible matchings.

The universal proof is separate. These controls exhaust labelled height-two
posets through n=5 and arbitrary labelled posets through n=4. No SAT is used.
"""
import hashlib
import itertools
import json
import time
from pathlib import Path


def matchings(vertices):
    if not vertices:
        yield ()
        return
    a, rest = vertices[0], vertices[1:]
    yield from matchings(rest)
    for i, b in enumerate(rest):
        for tail in matchings(rest[:i] + rest[i+1:]):
            yield ((a,b),) + tail


def height_two_posets(n):
    for roles in itertools.product((-1,0,1), repeat=n):
        lower = [i for i in range(n) if roles[i] == -1]
        upper = [i for i in range(n) if roles[i] == 1]
        possible = list(itertools.product(lower,upper))
        required = set(lower + upper)
        for mask in range(1 << len(possible)):
            edges = tuple(e for k,e in enumerate(possible) if mask >> k & 1)
            if {v for e in edges for v in e} == required:
                yield edges


def all_posets(n):
    seen = set()
    for order in itertools.permutations(range(n)):
        pairs = [(order[i],order[j]) for i in range(n) for j in range(i+1,n)]
        for mask in range(1 << len(pairs)):
            edges = {e for i,e in enumerate(pairs) if mask >> i & 1}
            while True:
                more = {(a,d) for a,b in edges for c,d in edges if b == c}
                if more <= edges:
                    break
                edges |= more
            seen.add(tuple(sorted(edges)))
    return sorted(seen)


def image(n,edges):
    return {x for x in range(1<<n)
            if all(((x>>a)&1) <= ((x>>b)&1) for a,b in edges)}


def apply_layer(x,matching):
    y=x
    for a,b in matching:
        if ((x>>a)&1) > ((x>>b)&1):
            y ^= (1<<a) | (1<<b)
    return y


def transform(n,edges,matching):
    incoming = {b for a,b in edges}
    outgoing = {a for a,b in edges}
    t = list(range(n))
    for a,b in matching:
        # a is the comparator's min output, b its max output.
        # Minimal elements have no incoming edges; maximal no outgoing.
        if a not in incoming and b not in outgoing:
            pass
        elif b not in incoming and a not in outgoing:
            t[a],t[b] = b,a
        else:
            return None
    q = {(t[a],t[b]) for a,b in edges} | set(matching)
    return t,q


def max_chain(n,edges):
    predecessors = [{a for a,b in edges if b == v} for v in range(n)]
    lengths = [0]*n
    for _ in range(n):
        for v in range(n):
            if not lengths[v] and all(lengths[u] for u in predecessors[v]):
                lengths[v] = 1 + max((lengths[u] for u in predecessors[v]),default=0)
    assert all(lengths), 'cycle in claimed output poset'
    return max(lengths,default=0)


def audit(n, posets):
    count = {'n':n, 'posets':0, 'compatible_pairs':0,
             'input_image_vectors':0, 'fixed_preimage_checks':0,
             'reversed_pairs':0, 'repeated_comparators':0}
    layers = list(matchings(tuple(range(n))))
    for edges in posets:
        count['posets'] += 1
        old = image(n,edges)
        old_height = max_chain(n,edges)
        for layer in layers:
            transformed = transform(n,edges,layer)
            if transformed is None:
                continue
            t,q = transformed
            expected = image(n,q)
            actual = {apply_layer(x,layer) for x in old}
            assert actual == expected, (n,edges,layer,actual,expected)
            assert max_chain(n,q) <= max(old_height,2)
            count['compatible_pairs'] += 1
            count['input_image_vectors'] += len(old)
            count['reversed_pairs'] += sum(t[a] == b for a,b in layer)
            count['repeated_comparators'] += sum((a,b) in edges or (b,a) in edges for a,b in layer)
            for y in expected:
                x = sum(((y>>t[v])&1)<<v for v in range(n))
                assert x in old and apply_layer(x,layer) == y
                count['fixed_preimage_checks'] += 1
    return count


def incompatible_control():
    edges = ((0,1),(2,3))
    layer = ((0,2),)
    actual = {apply_layer(x,layer) for x in image(4,edges)}
    hull = {(a,b) for a in range(4) for b in range(4) if a != b
            and all(((x>>a)&1) <= ((x>>b)&1) for x in actual)}
    witness = 1 << 2
    assert witness in image(4,hull) and witness not in actual
    return {'input_poset':edges, 'layer':layer, 'pairwise_order_hull':sorted(hull),
            'unreachable_hull_vector':[0,0,1,0], 'image_size':len(actual),
            'hull_size':len(image(4,hull)), 'conclusion':'same-role comparison may have non-poset image'}


def signed_next_layer_control():
    n=4
    count={'n':n,'poset_matching_pairs':0,'independent_sets':0,'binary_family_replays':0}
    layers=list(matchings(tuple(range(n))))
    for edges in all_posets(n):
        for layer in layers:
            count['poset_matching_pairs'] += 1
            for mask in range(1<<n):
                free=[v for v in range(n) if mask>>v&1]
                if any(a in free and b in free for a,b in tuple(edges)+tuple(layer)):
                    continue
                predecessors={a for a,b in edges if b in free}
                count['independent_sets'] += 1
                output_positions=None
                outputs=set()
                for values in itertools.product((0,1), repeat=len(free)):
                    x=[-1 if v in predecessors else 2 for v in range(n)]
                    for v,value in zip(free,values):
                        x[v]=value
                    assert all(x[a] <= x[b] for a,b in edges)
                    y=x[:]
                    for a,b in layer:
                        assert not (a in free and b in free)
                        y[a],y[b]=min(x[a],x[b]),max(x[a],x[b])
                    positions=tuple(v for v in range(n) if y[v] in (0,1))
                    if output_positions is None:
                        output_positions=positions
                    assert positions == output_positions
                    outputs.add(tuple(y[v] for v in positions))
                    count['binary_family_replays'] += 1
                assert len(outputs) == 1 << len(free)
    return count


def eighteen_circulant_control():
    n=18
    layers=[tuple((i,9+(i+s)%9) for i in range(9)) for s in range(4)]
    edges=()
    inverse_maps=[]
    for layer in layers:
        t,q=transform(n,edges,layer)
        assert max_chain(n,q) == 2
        inverse_maps.append(t)
        edges=tuple(sorted(q))
    replays=0
    for mask in range(1<<9):
        target=[(mask>>i)&1 for i in range(9)]+[2]*9
        x=target[:]
        for t in reversed(inverse_maps):
            x=[x[t[v]] for v in range(n)]
        for layer in layers:
            y=x[:]
            for a,b in layer:
                y[a],y[b]=min(x[a],x[b]),max(x[a],x[b])
            x=y
        assert x == target
        replays += 1
    return {'n':18,'layers':layers,'relations':len(edges),'free_antichain':list(range(9)),
            'fixed_sentinels':list(range(9,18)),'sentinel_value':2,
            'binary_preimage_replays':replays,
            'scope':'This four-layer family needs at least seven further layers, conditional on D(9)=7; not a complete D(18) proof.'}


def main():
    start=time.monotonic()
    rows = [audit(n,height_two_posets(n)) for n in range(1,6)]
    arbitrary = [audit(n,all_posets(n)) for n in range(1,5)]
    result = {'status':'VERIFIED_FINITE_CONTROLS',
              'scope':'Universal result requires the separate hand proof; finite controls alone are not a proof.',
              'height_two':rows,'arbitrary_posets':arbitrary,
              'mathematical_review':{
                  'status':'ACCEPTED_WITH_STATED_SCOPE',
                  'reviewed_note':'height-two-image-closure.md',
                  'note_sha256':hashlib.sha256((Path(__file__).parent/'height-two-image-closure.md').read_bytes()).hexdigest(),
                  'accepted_claims':[
                      'Exact fixed-permutation preimage for arbitrary-degree height-two posets and compatible matchings.',
                      'Generalization to minimal/maximal comparisons in arbitrary posets with other vertices idle.',
                      'Propagation of a contained full poset family, including ties and arbitrary physical comparator orientation.',
                      'Antichain freezing with fixed signed sentinels and standard untangling gives D(width(P)) remaining layers.',
                      'Independence in the full comparability graph union the next matching gives one additional blind layer.',
                      'At the stated18-wire cut, alpha<=8, odd cycle necessity, and per-bipartition internal-edge counts.',
                      'Four-layer18-wire circulant is excluded from depth ten, conditional on established D(9)=7.'
                  ],
                  'scope_limits':[
                      'Known inequalities alone put the image inside a poset family and do not imply the required containment.',
                      'For general posets use all comparable pairs, not only Hasse edges, in the independent-set statement.',
                      'Every bipartition includes component flips and arbitrary placement of isolated vertices.',
                      'No whole D18 two-layer cover case or global lower bound is claimed.'
                  ]
              },
              'incompatible_control':incompatible_control(),
              'signed_next_layer_control':signed_next_layer_control(),
              'eighteen_circulant_control':eighteen_circulant_control(),
              'elapsed_seconds':time.monotonic()-start,
              'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    out=Path(__file__).parent/'results'/'height-two-recovery-review.json'
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
