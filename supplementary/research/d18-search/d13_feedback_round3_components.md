# D13 applications of the nine-real component theorem

The hand [311/441 merger proof](d13_feedback_round3_merger441.md), together
with the hand432 and333 proofs, gives this necessary condition: every
nine-real restriction of a sorter with four layers remaining already has
an interaction component containing at least five real tracks.

This round proves the merger lemma and tests its application to D13. It
does **not** close another complete-cover case or explain the six-wire
case115 interval obstruction by hand.

## Saved four-layer witnesses

The independent scalar [collector](d13_feedback_round3_components.py)
checks all `C(13,4)*16 = 11,440` signed four-sentinel placements on each of
the 117 saved first-two-profile witnesses. Its
[report](results/d13_feedback_round3-components-all.json) records:

- 34 saved four-layer witnesses have an obstructing restriction;
- 83 saved witnesses satisfy the component condition;
- 15 witnesses are rejected only by the newly proved441 partition: cover
  indices7,25,26,27,36,38,43,47,55,63,84,88,100,103,109.

The saved case116 witness has104 obstructions,90 of shape441 and14 of
shape432. The saved case114 witness has16 of shape432. The saved witnesses
for cases0,1,58,115 have no obstruction of this type. In particular, failure
of some saved witnesses must not be counted as closure of their whole
two-layer prefix cases.

For one obstruction per rejected witness, the checker directly constructs
every binary sorted-chain output on its interaction components:1,878
functional replays pass. The known depth-nine D13 sorter is checked on all
8,192 binary inputs, and its cut after layer5 passes all11,440 component
tests, as required with four sorting layers remaining.

## A common case116 survivor after learning component cuts

The [bounded synthesis trial](d13_feedback_round3_component_cegar.py)
searches common layers L3,L4 while retaining these old necessary conditions:

* every seven-real restriction blind in L1,L2 has counts `(2,3)`, `(3,2)`
  or `(3,3)` in L3,L4;
* every five-real restriction blind in L1,L2 has a nonempty L3 or L4.

It additionally tests **every** signed nine-real placement against the new
component theorem. For each violating candidate it learns a guarded
partition-crossing clause, described below.

Case116 survives this combined condition. On the original cover labels,
one common choice is

```
L1 = (0,1)(2,3)(4,5)(7,8)(9,10)(11,12)
L2 = (0,3)(1,2)(4,6)(7,9)(10,11)
L3 = (0,1)(2,3)(4,10)(5,6)(8,9)(11,12)
L4 = (0,10)(1,12)(2,6)(5,9)(8,11).
```

The solver added eight component cuts and exited normally in0.28 seconds
including process overhead, under a hard60-second external cap. This is a
relaxation survivor, not a sorting network. It does not include every
stronger, nonblind rescheduling condition previously studied.

The separate [replay checker](d13_feedback_round3_component_cegar_verify.py)
enumerates the raw signed placements, independently of the synthesis
family normalization:

| Real count | Raw placements checked | Blind in first two layers | Violations |
|---:|---:|---:|---:|
|5|329,472|44,032|0|
|7|109,824|512|0|
|9|11,440|not required|0|

It also reconstructs and audits all eight learned component cuts. The
[verification report](results/d13_feedback_round3-component-cegar-r0116-verification.json)
binds the survivor input and checker source by hash. The
[terminal record](results/d13_feedback_round3-component-cegar-r0116-terminal.json)
records a normal exit. No job remains running.

## Why the guarded partition cut is sound

Fix a violating signed placement and the candidate third matching `M`.
The real track positions after L3 are fixed. Partition those positions
according to the candidate's final interaction components after L4;
every block has size at most four, and every L1--L3 interaction is internal
to a block. Every permissible L4 must therefore compare two reals from
different blocks. Otherwise the components remain of size at most four,
contrary to the hand theorem.

The clause is

```
OR(not g3(e) for e in M)
OR(g3(e) for e joining two vertices idle in M)
OR(g4(e) for e joining two different real blocks).
```

Under the matching constraints, the first two disjunctions are exactly the
negation of `L3=M`: if every chosen M edge is present, the only possible
additional edges join M-idle vertices. Thus the crossing obligation is
activated only for that exact third matching. It excludes all fourth
matchings missing the crossing, rather than just the one candidate L4.

Sentinel comparisons in L4 only permute the track positions. The blocks
here are fixed **logical-track** blocks mapped to physical positions
immediately after L3, so those routes cannot create an interaction between
blocks. The independent cut audit checks this mapping and the literal
translation explicitly.
