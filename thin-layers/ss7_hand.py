#!/usr/bin/env python3
"""ss7_hand.py -- the case split behind the hand proof of SS(7,7,1,3).

A 7-channel network whose layers 1-3 have at most one comparator each (c1, c2, c3) cannot sort in
depth 7.  Every configuration (c_t a pair or absent) is shown to fall under one of:
  (E) some c_t is absent, or two consecutive comparators can be made adjacent and disjoint by
      commuting disjoint neighbours, so they merge into one layer: the result has depth 6 and a
      first layer with one comparator, contrary to (P7) (h9.md, Theorem 14);
  (S) two infinities (signs and input channels given) meet c1, c2, c3 between them, so the other
      five inputs are compared only in layers 4-7: four layers cannot sort five (D(5) >= 5).
Infinities are ordered (+inf_1 > +inf_2 and -inf_1 < -inf_2) so ties are resolved consistently.
The script enumerates all configurations up to relabeling and prints a witness for each."""
import itertools, json

N = 7
pairs = list(itertools.combinations(range(N), 2))


def blinds(cs, sents):
    """cs = [c1, c2, c3] (pairs or None); sents = [(channel, value)], value in {+2,+1,-1,-2}
    (larger absolute = more extreme).  Returns the set of t with c_t real-real."""
    val = {}
    for ch, v in sents:
        val[ch] = v
    leaks = set()
    for t, c in enumerate(cs):
        if c is None:
            continue
        i, j = c
        a, b = val.get(i), val.get(j)
        if a is None and b is None:
            leaks.add(t)
            continue
        # comparator puts the smaller on i; reals count as 0
        x, y = (a if a is not None else 0), (b if b is not None else 0)
        if x > y:
            val.pop(i, None); val.pop(j, None)
            if a is not None: val[j] = a
            if b is not None: val[i] = b
    return leaks


def merge_ok(cs):
    if any(c is None for c in cs):
        return 'absent layer'
    c1, c2, c3 = map(set, cs)
    if not (c2 & c3):
        return 'merge c2,c3'
    if not (c1 & c2) and not (c1 & c3):
        return 'commute c1 past c2, merge c1,c3'
    return None


stats, witnesses = {'E': 0, 'S': 0, 'none': 0}, []
opts = pairs + [None]
for cs in itertools.product(opts, repeat=3):
    if cs[0] is None and cs[1] is None and cs[2] is None:
        continue
    why = merge_ok(cs)
    if why:
        stats['E'] += 1
        continue
    found = None
    for (p, q) in itertools.combinations(range(N), 2):
        for vp, vq in itertools.product((2, -2), (1, -1)):
            if not blinds(cs, [(p, vp), (q, vq)]):
                found = [(p, vp), (q, vq)]
                break
        if found:
            break
    if found:
        stats['S'] += 1
    else:
        stats['none'] += 1
        witnesses.append(cs)
print(json.dumps({'configurations': sum(stats.values()), 'by_rule': stats, 'unresolved_examples': witnesses[:5]}))
