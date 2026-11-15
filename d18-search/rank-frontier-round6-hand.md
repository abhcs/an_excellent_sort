# Rank witnesses exclude three concrete six-layer D18 prefixes

The exact prefixes and input permutations are in the
[fixed certificate](results/rank-layer-round6-hand-certificate.json) and
[printed endpoint tables](rank-layer-round6-hand-tables.md). Each prefix
has six layers on eighteen wires. None extends to a ten-layer sorter.
This is a statement about those three prefixes, not the complete D18 cover.

## Two reusable hand lemmas

At a fixed wire after a comparator prefix, attainable ranks over all
permutations form an interval. Swapping adjacent rank values connects the
permutations. Identifying the swapped values commutes with every minimum
and maximum, so each wire changes by at most one at a step. The wire
therefore attains every integer between two witnessed ranks.

With s layers remaining, its forward cone has at most 2^s positions.
Consequently a witnessed gap of at least 2^s is impossible. If the gap
is exactly 2^s-1, its attainable interval and forward cone must both be
that complete interval. For s>=1 this full cone is a union of edges of
the final matching: all positions reached immediately before the last
layer must acquire distinct partners to double to 2^s. Two full cones
therefore have even intersection.

These statements impose a useful matching constraint one layer earlier.
For each proposed comparator, evaluate its two outputs on a finite bank
of real input permutations. Delete any comparator whose minimum or
maximum has a gap of at least 2^s. Any wire with such a gap before the
layer is mandatory: it cannot be idle. Every completion must match all
mandatory wires using the remaining edges. When a surviving edge forces
full output intervals, incompatible odd intersections forbid that edge
or a pair of disjoint edges. All these exclusions are necessary at any
ambient width; a bank need only witness exclusions, not enumerate inputs.

## Applying the lemmas with s=3

For `beam00`, wire12 cannot be idle and every one of its seventeen
possible partners is excluded by a rank gap of at least eight. The
printed table supplies explicit low/high input witnesses for every
choice. Other gates of layer7 are disjoint and cannot alter the displayed
output. There is no possible layer7.

For `beam16`, exactly the same argument applies to wire6. Again the
table excludes the idle choice and all seventeen partners.

For `beam32`, wires5 and12 are mandatory. The width tables leave only
partners2 and8 for either one. If edge(2,12) is used, its outputs force
full rank intervals [2,9] and [9,16]. Their intersection has size one,
which is impossible. Thus (8,12) is forced and wire5 must use (2,5).
These two edges force the full intervals [3,10] at output8 and [4,11]
at output5. Their intersection has size seven, again impossible.

This proves all three exclusions by explicit inputs and the two lemmas.
No SAT result is a premise. The independent
[standard-library checker](rank_layer_hand_check.py) replays 69 input
permutations, 68 width exclusions, and the two odd-cone contradictions.
The [saved replay](results/rank-layer-round6-hand-check.json) identifies
the exact certificate, table, and checker hashes.

## Computational extension and limits

The corresponding three five-layer prefixes also fail the rank-width
and parity test with three unknown layers leading to cut8. Files
`results/prefix-rank-round6-only-beam{00,16,32}.json` identify these runs;
each companion directory contains the CNF, DRAT proof, independent checker
log, and terminal record. All solves and checks finished in under one
second. Raw worker manifests say `UNSAT_UNCHECKED` because the separate
checker runs afterward; the companion checks report `s VERIFIED`.
The combined structural variants are independently reviewed in
[the encoder audit](results/d18_hand_round6-frontier-review.json).

At four fixed layers, both distinct tested prefixes remain unresolved.
The original width/parity models and their middle-pair strengthenings
reached 30-second caps. Round-seven common-ending routing models, with
both arbitrary ending spans and the existing last-two-layer normal form,
also reached their 30-second caps. The known eighteen-wire depth-eleven
sorter passes both routing positive controls. These timeouts are not
refutations and do not increase the complete-cover count.
