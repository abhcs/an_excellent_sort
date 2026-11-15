# Independent review of the critical-edge hand reduction

The root review checked Sections1–5 of
[d17_feedback_round3_hand.md](d17_feedback_round3_hand.md), including its
use of the earlier folded-fork lemma. The argument is valid for every
even active width at least twelve, not just the fourteen-wire sample.

The essential checks were these:

* The one-row path classification allows partial matchings and edges to
  vertices outside the five-set. With no internal edge of the common
  triple, four distinct path vertices would need partners in three
  positions. Once that internal edge is present, the two stated cores
  exhaust the remaining possibilities.
* For a same-sign cross comparator, a row missing its A endpoint moves
  exactly one B path coordinate to the A singleton destination. The
  resulting transfer is one of the four proved local patterns. An
  opposite-sign cross comparator has fixed routing instead.
* The first-layer peak identity is `RR = |M|-5+idle_S+SS`. When the
  matching has one or two missing edges, at most one A row can peak in
  any selected column. Its endpoints have no A--A partners, as required
  by the deleted-row folding argument. Smaller matchings cannot peak.
* The six-entry folding table exhausts the same-sign A pairs disjoint
  from an exceptional row. Opposite-sign pairs do not identify images;
  the only disjoint pair of deleted fork edges is handled explicitly.

The SAT-free checker was independently rerun successfully:232 one-row
matchings, five patterns with764 local matchings each,26 A matchings,
16 deleted-edge configurations, and61,512 relevant fourteen-wire first
matchings. Its source SHA256 is
`4fe644371d4a0506c6153126cf83b57da205746e01c5694d78f8ae77920fab78`.
The replay took1.17 seconds. The arbitrary-width conclusion comes from
the hand argument, not extrapolation from these checks.

This finishes review of this branch. The full case606 hand proof and
D17 hand lower bound remain unfinished; the complete-cover counts do
not increase as a result of this review.


## Follow-up review: perfect matchings with two cross gates

The [round-four extension](d17_feedback_round4_hand.md) also passes root
review. Its exact double-transfer table correctly retains two compatible
cores instead of declaring every local pair impossible. The A-fork case
split leaves only crossed vertices A,D with BC in the first matching;
the additional CE row contradicts each of the two surviving cores.
The argument covers arbitrary even widths and embeddings for **perfect**
first matchings. It does not extend the two-cross conclusion to deficient
first matchings.

The SAT-free checker independently replayed all3,600 corresponding
fourteen-wire first matchings:3,588 are excluded by the local two-row
lemmas, six by the inner-core third row, and six by the outer-core third
row. Its SHA256 is
`8d2a1d513097c77da19dfc667157d23b6be3c7c7ad463e4680dec0f0313fdeab`.
The full case606 hand proof remains open.

## Round-five review: every perfect critical first matching

The root review checked the external-common-real contraction and the
full-row existence argument in [round five](d17_feedback_round5_reduction.md).
The contractions are sound for the selected twelve type states: they
lose at most one first-layer RR comparison while the required peak drops
by one, and delete only always-real output coordinates before transporting
and completing the second matching. Thus no SS edge is lost. This is a
statement about two-layer type-count covers, not about preserving an
entire sorting network.

The width reduction exhausts the noncross vertices at cross counts3,4,5.
It leaves600+120+240+120 canonical cases at widths12 and14; arbitrary
reorientation of the first matching is absorbed by fixed output swaps in
the second. For a fixed A row all comparisons have fixed type routing
across the three selected B columns, so the six path cores apply exactly.

The independent checker was rerun: all1,080 cases and6,480 branches pass;
4,479 contradict immediately and2,001 require one forced edge. Its SHA256
is `5dbf7552627904cdaa1b195e6b416e140df964eacd9a2926bc3ae47452b64773`.
The certificate SHA256 is
`d2858a22247eb034280d6a510e139cc4aa4f68a6f5a367a207160d03343c45be`.

Together with the reviewed hand results for at most two cross gates,
this establishes the full critical-perfect branch at every even active
width. The1,080-case arithmetic verification remains a proof premise.
It is not a pure hand classification of that branch, a full case606
proof, or a new complete-cover exclusion.
