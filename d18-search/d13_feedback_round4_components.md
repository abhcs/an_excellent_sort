# D13 case116 still passes the stronger component condition

The new hand merger results imply that, with four layers remaining, every
nine-real sentinel restriction must already have **at most two interaction
components**. Any three or more components can be coarsened into exactly
three nonempty blocks. Every three-block partition of nine requires at
least five merger layers: `711,621,531,522,441,432,333`.

This strengthens the round3 condition requiring some component of size at
least five. It rejects the previous round3 common `L3,L4` survivor for
case116, but it does not close that whole two-layer cover case.

## A new common continuation

The exact case116 prefix and the newly found two layers are:

```
L1: 01 23 45 78 (9,10) (11,12)
L2: 03 12 46 79 (10,11)
L3: 01 23 (4,10) 56 89 (11,12)
L4: (0,10) (1,12) 26 37 59 (8,11)
```

Relative to the round3 survivor, only the extra fourth-layer edge37 is
needed. This is a necessary-condition survivor, not a sorting network or
a depth-eight completion.

The bounded search exited successfully in0.40seconds wall time, with an
explicit60-second hard cap. It learned25 component cuts. Its output status
is `SURVIVOR`; there is no UNSAT claim.

## Exact cuts and independent checks

For a candidate third matching M and a violating sentinel placement,
compute the real interaction components through candidate L4. Coarsen
whole components into three nonempty blocks, then represent the original
real tracks of those blocks at the physical cut after M. Any replacement
L4 that preserves all three blocks would leave a forbidden three-block
merger. The learned clause is

```
(some selected M edge is absent)
OR (an edge between two M-idle positions is present)
OR (L4 has a real-real edge crossing the three cut3 blocks).
```

Under the matching constraints, the first two parts are precisely the
negation of the complete M assignment. The clause therefore restricts all
fourth layers associated with that M, not just the current two-layer
candidate. No claim that a single cross edge always suffices is made;
another candidate with three components causes another sound cut.

The independent verifier uses adjacency graphs rather than the encoder's
union-find and checks:

* All11,440 signed nine-real placements have at most two components after
  the displayed four layers.
* All329,472 raw five-real placements: the44,032 placements blind through
  L1,L2 retain at least one gate in L3,L4.
* All109,824 raw seven-real placements: the512 placements blind through
  L1,L2 have L3,L4 retained profiles `(2,3)`, `(3,2)`, or `(3,3)`.
* Every one of the25 learned cuts has three nonempty nine-real blocks,
  preserves all cut3 interaction edges, and has the recorded exact guard
  and crossing-edge clause.
* A known thirteen-wire depth-nine sorter passes all8192 binary inputs;
  all11,440 nine-real restrictions at its cut5 also pass the new criterion.

These checks do not include every stronger nonblind rescheduling condition
studied elsewhere. The result establishes compatibility of the stated
blind profiles and the stronger component condition; it is not a proof
that every previously studied relaxation survives jointly.

## Files

* Search: [d13_feedback_round4_component_cegar.py](d13_feedback_round4_component_cegar.py).
* Replay and translation audit: [d13_feedback_round4_component_cegar_verify.py](d13_feedback_round4_component_cegar_verify.py).
* [Search result](results/d13_feedback_round4-component-cegar-r0116.json).
* [Terminal record](results/d13_feedback_round4-component-cegar-r0116-terminal.json).
* [Independent verification](results/d13_feedback_round4-component-cegar-r0116-verification.json).

The first two-layer case remains covered by earlier independently checked
wire-interval UNSAT certificates. This experiment concerns replacing that
computational obstruction by more compact hand structure.
