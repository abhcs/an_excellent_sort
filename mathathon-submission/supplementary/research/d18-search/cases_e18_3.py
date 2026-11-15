#!/usr/bin/env python3
"""cases_e18_3.py -- split "depth-10 extension of e18_3" into symmetry-reduced cases.

Prefix e18_3: Green filter (3 layers) on cube A = channels 1..8 and cube B = channels 9..16
(channel c+b has binary index b), plus the comparator (0,17) in layer 1.  The first free layer
(layer 4) either leaves channel 0 idle or uses (0, c), and leaves channel 17 idle or uses (c', 17).
Every network falls into exactly one such (p0, p17) case.

Symmetries of the prefix output set: permuting the 3 coordinates inside each cube (S3 x S3),
swapping the cubes, and duality (reverse-complement: 0 <-> 17, A_b <-> B_(7-b)), which maps the
case (p0, p17) to (dual(p17), dual(p0)).  Equivalent cases have extensions of the same depth
(Bundala-Zavodny subsumption: outputs related by a channel permutation, or by negation and
reflection), so one representative per orbit suffices.
"""
import itertools
import json
import sys

sys.path.insert(0, __import__('os').path.dirname(__file__))
from netsat import named_prefix  # noqa: E402

PERMS = list(itertools.permutations(range(3)))


def chan(cube, b):
    return (1 if cube == 0 else 9) + b


def permute_bits(b, p):
    return sum(((b >> k) & 1) << p[k] for k in range(3))


def act(elem, pa, pb, swap):
    if elem is None:
        return None
    cube, b = elem
    b = permute_bits(b, pa if cube == 0 else pb)
    if swap:
        cube = 1 - cube
    return (cube, b)


def dual(elem):
    if elem is None:
        return None
    cube, b = elem
    return (1 - cube, 7 - b)


def key(e):
    return (-1, -1) if e is None else e


def canon(p0, p17):
    best = None
    for (q0, q17) in [(p0, p17), (dual(p17), dual(p0))]:
        for pa in PERMS:
            for pb in PERMS:
                for swap in (False, True):
                    img = (key(act(q0, pa, pb, swap)), key(act(q17, pa, pb, swap)))
                    if best is None or img < best:
                        best = img
    return best


def main():
    elems = [None] + [(c, b) for c in (0, 1) for b in range(8)]
    orbits = {}
    for p0 in elems:
        for p17 in elems:
            if p0 is not None and p0 == p17:
                continue
            orbits.setdefault(canon(p0, p17), []).append((p0, p17))
    n, P = named_prefix('e18_3')
    out = []
    for k, (rep, members) in enumerate(sorted(orbits.items())):
        p0, p17 = members[0]
        fix = []
        if p0 is None:
            fix.append({'idle': [0, 0]})
        else:
            fix.append({'g': [0, 0, chan(*p0)], 'value': True})
        if p17 is None:
            fix.append({'idle': [0, 17]})
        else:
            fix.append({'g': [0, chan(*p17), 17], 'value': True})
        out.append({'n': n, 'layers': P, 'fix': fix, 'case': [p0, p17], 'orbit_size': len(members)})
    with open('prefixes/e18_3_cases.jsonl', 'w') as f:
        for o in out:
            f.write(json.dumps(o) + '\n')
    total = sum(o['orbit_size'] for o in out)
    print(f'{len(out)} cases covering {total} (p0,p17) choices')
    for o in out:
        print(o['case'], 'orbit', o['orbit_size'], o['fix'])


if __name__ == '__main__':
    main()
