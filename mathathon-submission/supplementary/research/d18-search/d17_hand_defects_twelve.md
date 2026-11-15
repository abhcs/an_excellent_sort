# A hand proof of the twelve-wire no-cross-edge branch

**Later completion.** The subsequent [small and cross-edge lemmas](d17_hand_defects_twelve_cross.md),
[four-gate/perfect arguments](d17_feedback_twelve_structure.md), and
[five-gate argument](d17_hand_defects_twelve_five.md) now prove the full
twelve-wire obstruction by hand. This note records the first branch proof.

**Result.** For the twelve-wire restriction family obtained from case 607,
no pair of matchings can cover every restriction if the first matching
has **no edge between A and B**, where

    U={1,2}, A={4,5,6,7,8}, B={10,11,12,15,16}.

Both matchings may be partial. The proof below treats every possible size
of the first matching; it never fills that middle matching without a
separate justification. This closes a structural branch, not the whole
case. The remaining branches have at least one A--B edge.

The full pure twelve-wire obstruction is already independently checked by
SAT; see `results/d17-feedback-twelve-audit.json`. The proof here explains
one part of it without using that UNSAT result.

## 1. The family and two safe normalizations

Every state has nine reals and three sentinels. The A sentinels occupy an
edge of the four-edge tree

    G={56,67,78,46}.

Their signs are fixed by the vertex: 4+,5-,6-,7+,8+. Independently, the
third sentinel occupies one arbitrary B vertex; its sign is 10+,11-,12+,
15-,16+. Wires 1 and 2 are always real. Thus there are four times five
signed states.

Write M for the first matching and N for the last counted matching.
A state **peaks** when its matching retains four real-real comparisons.
The coverage condition asks that each state peak either in M, or in N
after exact sentinel transport through M.

**Fill N.** Adding edges between idle wires of N can only increase its
retained counts. There is no following transport to preserve. Therefore
we may complete N to a perfect matching on the twelve wires.

For a perfect matching on twelve wires, a nine-real state peaks precisely
when two of its three sentinels are paired. Indeed, with one sentinel pair
there is one mixed edge and four real-real edges; without a sentinel pair
there are three mixed edges and only three real-real edges.

**A different safe operation on M.** If an N-edge has both endpoints idle
in M, add that same edge to M, retaining it in N. The first retained
counts cannot decrease. In the second layer the two types entering this
N-edge may have been reordered, but its both-real predicate is unchanged;
all other N-edges are disjoint. Thus every second retained count is
unchanged. This operation is valid even with repeated edges permitted.
It does not justify arbitrary filling of M. The branch proof below does
not need this additional normalization.

## 2. Folding singleton sentinels and forcing an N-edge

Assume M has no A--B edge. If a single sentinel starts at v, let f(v) be
its position after M: it is the smaller endpoint of its M-edge for a
minus sentinel, the larger endpoint for a plus sentinel, and v if idle.

Two distinct singleton positions can have the same image only when they
are the endpoints of one M-edge and have the same sign. Hence every
image has at most two preimages. Images from A and B are disjoint: their
M-edges belong to different blocks when there are no A--B edges.
An M-idle vertex has a unique image, itself.

For an A-edge ab not in M, the two A sentinels end at f(a),f(b), which
are distinct. The third sentinel ends at f(c), c in B. If ab is itself
in M, its two sentinel positions remain the two endpoints; this case
will not be needed for the forcing argument.

**Three-image rule.** If a fixed A pair {u,v} is forced to obtain its peak
in N for at least three distinct transported B positions, then uv must
be an N-edge. Otherwise every sentinel triple {u,v,z} requires an N-edge
from z to u or v, and a matching can accommodate at most two such z.

**Two-image rule.** For two distinct B positions p,q, if N already pairs
u to a vertex outside {v,p,q}, it cannot peak on both {u,v,p} and
{u,v,q}. The only remaining possible sentinel edges would require v to
be paired to both p and q.

## 3. The fork contradiction

Suppose every A-edge outside M forces its folded pair into N. This is
impossible.

If M uses none of 65,67,64, the three N-edges forced at f(6) require
f(5)=f(7)=f(4), contradicting the two-preimage bound. If M uses 67, the
other two neighbors 5- and 4+ cannot coalesce. If M uses 64, the other
neighbors 5- and 7+ likewise cannot coalesce.

Only M-edge 65 remains. The other neighbors 4+ and 7+ must coalesce,
forcing M-edge 47. Therefore f(6)=5 and f(4)=f(7)=7, and N must contain
57. The A-edge 78 is outside M and would also force 7f(8) into N.
But f(8) is neither 5 nor 7, since the M-edges 65 and 47 already use
those vertices. Contradiction.

The same argument still works if one additional A-edge joining two
M-idle vertices is exempted from being forced. At the center 6, this
exception behaves as a possible fourth choice of covered edge. Only
an exception 65 could leave coalescible neighbors 4,7. It again forces
M-edge 47 and the incompatible N-edges 67 and 7f(8); here f(6)=6 is
idle and cannot equal f(8). If the exemption is elsewhere, the preceding
center argument is unchanged. It cannot exempt 78 in the only surviving
center configuration, because M-edge 47 already uses 7.

## 4. All partial first matchings are included

Let m=|M| and let r be the number of idle A vertices. For an A-edge not
in M, write h for the number of its endpoints used by M. A state whose
B sentinel is at c retains exactly

    m-h-1_{c is used by M}

M-edges: the sentinel-bearing edges are distinct because there are no
A--B edges. In particular, for m<=4 an A-edge with at least one used
endpoint misses an M-peak for every B choice. For m=5 this holds when
both endpoints are used. All five B positions have at least three
distinct images.

**m<=3.** Every state misses its M-peak. The three-image rule forces
every A-edge outside M, and Section 3 applies.

**m=6.** All vertices are used. Every A-edge outside M misses its M-peak
for all B choices. Again Section 3 applies. More generally, this same
argument works for any m when every A vertex is used.

**m=5.** There are just two idle vertices.

* If no B vertex is idle, its five positions give at least three images.
  Every A-edge outside M with a used endpoint is forced into N. The
  only possible exception joins the two idle A vertices, so the extended
  fork contradiction applies.
* If two B vertices are idle, every A vertex is used, already handled.
* The remaining case has one idle B vertex. If no A vertex is idle it is
  already handled. Otherwise exactly one A vertex v is idle. For an
  A-edge incident to v, all four **used** B choices miss their M-peak;
  these have at least two distinct images p,q. If they have three, the
  ordinary fork contradiction applies, so only two need consideration.

  If v is 4,5, or 7, the used center 6 has two other used neighbors.
  At most one is its M-partner. Another therefore forces an N-edge at
  f(6) to a vertex different from v and from p,q. The two-image rule
  contradicts the requirement for edge 6v.

  If v=6, all three neighbors 4,5,7 are used. If N pairs 6 to p, all
  three neighbor images must be q's single N-partner; if it pairs 6 to q,
  all must be p's single N-partner. Otherwise all three neighbor images
  must be the N-partner of 6.
  Each alternative violates the two-preimage bound.

  If v=8, the three central edges have used endpoints. The argument in
  Section 3 forces M-edges 65 and 47 and N-edge 57. The two-image rule
  now rejects the remaining edge 78.

**m=4.** There are four idle vertices.

* If r<=1, every A-edge has a used endpoint, and all A-edges outside M
  are forced. Section 3 applies.
* If r=4, every B vertex is used, so there are at least three B images.
  Every state with a used B sentinel misses its M-peak, even if both A
  sentinels are idle. Thus all A-edges outside M are forced.
* Suppose r=2. If center 6 is used, at least one of its three neighbors
  is idle. Two idle neighbors would force two different N-partners for
  f(6). With just one idle neighbor, its two used neighbors cannot both
  be M-partners; one forces another, different N-partner. Thus 6 is
  idle. At least two of 4,5,7 are used, and their images must coincide
  as N's partner of 6. The only possible coalescence is M-edge 47, so
  the other idle vertex is 5. Vertex 8 is used. Edge 78 forces an
  N-edge at 7, conflicting with the already forced N-edge 67.
* Suppose r=3. At least four B vertices are used, giving at least two
  distinct B images. If center 6 is used, at least two of its neighbors
  are idle and force two different N-partners. If 6 is idle, it has
  both a used neighbor and an idle neighbor: only two A vertices are
  used, and only one A vertex, 8, is not its neighbor. The used neighbor
  forces an N-edge at 6 to a non-idle A image. The edge to the idle
  neighbor must still peak for the two used B images, contradicting the
  two-image rule.

These cases exhaust m=0,...,6. Therefore every feasible first matching
must contain an A--B cross edge. ∎

## 5. Direct checks and the remaining work

`d17_hand_defects_twelve_verify.py` independently checks the branch using
small exact matching constraints. For each A pair it computes the B
images that still need an N-peak. Three or more images force the A pair;
two images allow that pair or either of the two cross-pairings; one image
allows any edge of its sentinel triple. The four resulting constraints
have at most three alternatives each. Compatibility is checked directly.

The checker covers all **15,712** no-cross first matchings, with counts
by size m=0,...,6 equal to

    1, 41, 560, 3110, 6825, 4725, 450.

It finishes in under a second and uses no SAT. The
[record](results/d17-hand-defects-twelve-no-cross.json) is `VERIFIED`.
The enumeration corroborates the proof; it is not one of its premises.

The remaining hand-proof branches contain at least one A--B cross edge.
Their sizes m=1,2,3 must not be discarded merely because M never peaks:
M still transports the states, so N sees a different family. A lower
bound on m would require a separate argument. Neither arbitrary filling
of M nor the initial family's static peak bound supplies that argument.

The safe operations in Section 1 remain available in those branches.
No analysis here covers every cross-edge branch, so the universal
case-607 statement remains SAT-assisted.
