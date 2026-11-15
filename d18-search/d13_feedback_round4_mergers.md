# Two further hand obstructions for nine-real mergers

**Results.** Neither independently sorted blocks `5+3+1` nor independently
sorted blocks `5+2+2` can be merged in four comparator layers. The arguments
below use the cone bound, the hand `3+1+1` merger lemma, and the hand six-wire
first-two-layer profile. SAT is not a premise.

All blocks are in fixed known orders. Relabel and untangle to give them
consecutive positions. Delete first-merger-layer comparisons internal to a
sorted block, since they never swap. This preserves the whole input family.
The first matching need not be perfect.

## 1. A singleton with two blocks of size at least three

Let the two blocks have lengths `p,q>=3`, with `p+q=8`, and let `c` be the
singleton. This covers both `4+4+1` and `5+3+1`.

Suppose four merger layers exist, with first matching `N`. The singleton
must be used in `N`; otherwise only three layers remain to route its nine
possible ranks to nine output positions, contradicting the forward-cone
bound of eight. Suppose its partner is in the p-block, at position `a_j`.

For each other p-block position `a_i`, keep real exactly `a_i`, `c`, and
any consecutive triple of the q-block. Replace lower entries of either
block by negative infinities and higher entries by positive infinities.
These are valid sorted-block restrictions. The real inputs are a sorted
triple and two arbitrary singletons. If `N` were blind, the three remaining
layers would merge `3+1+1`, contrary to the
[hand lemma](d13_feedback_round3_merger441.md).

The singleton's own N-edge is blind because `a_j` is a sentinel. There are
no N-edges internal to a block. Thus `a_i` must have its partner inside
**every** consecutive triple of the q-block. Those triples have intersection
size `6-q`, for q=3,4,5. But there are

```
p-1 = 7-q > 6-q
```

distinct positions `a_i`, which cannot all have distinct matching partners
in that intersection. This contradiction works whichever block contains
the singleton's partner. Hence both mergers need at least five layers. □

For `5+3+1`, the two cases are simply four vertices demanding partners in
three positions, or two vertices demanding partners in one position.

## 2. A five-block and two pairs

Write the sorted blocks as

```
A = a0<a1<a2<a3<a4,  B = b0<b1,  C = c0<c1.
```

Let `t` be the number of first-matching N-edges between B and C. It is0,1,
or2. All other possible N-edges join A to B or C.

Keep any adjacent pair `a_i,a_(i+1)` and all four B,C positions real. These
six reals arrive as three sorted pairs. Prepending one layer that sorts
those pairs creates a six-wire depth-five sorter. The hand
[six-wire early profile](../depth-hand-proofs/h9_feedback_reschedule.md)
requires N to retain at least two real-real gates in each of these four
restrictions.

* **t=0.** Each adjacent A-pair must have both its vertices matched outward
  into B or C. Their union is all five A-vertices, but B and C have only
  four available partners. Contradiction.
* **t=1.** The B--C edge always contributes one retained gate. Its endpoints
  leave only two B,C vertices for A-edges. The A-partners of those two edges
  must hit all four adjacent pairs of the five-block. The only hitting set
  of size at most two is `{a1,a3}`: pair01 needs a0 or a1, pair34 needs a3
  or a4; choosing a0 misses pair12, and then pair23 forces a3.

  Let `x` be the B/C vertex matched to `a3`, and let `y` be the B--C edge's
  endpoint in the **other** two-block. Keep real `a0,a1,a2,x,y`. The first
  matching N is blind: the partner of x is the omitted a3; the partner of
  a1 is the omitted vertex in y's block; and y's B--C partner is omitted
  from x's block. These five inputs form a sorted triple and two arbitrary
  singletons, so three remaining merger layers contradict the hand311
  lemma.
* **t=2.** All B,C vertices are used by the two B--C edges, so N has no edge
  incident with A. Restrict the input family further by requiring B and C
  together to be a sorted four-block, with B before C. N fixes every such
  input. The remaining three layers would have to merge sorted blocks of
  lengths5 and4. Their median, rank4, can be at each of the nine input
  positions: the rank interval at A-position i is `[i,i+4]`, and at
  four-block position j it is `[j,j+5]`; all contain4. Its backward cone
  through three layers has at most eight positions, a contradiction.

All three cases fail, proving that a `5+2+2` merger needs at least five
layers. □

## 3. Scope and local verification

These theorems rule out additional interaction-component partitions at a
cut with four layers left. Any prefix whose independent components can be
packed into `5+3+1` or `5+2+2` fixes the corresponding sorted-block input
family after relabelling and untangling. Its suffix therefore cannot sort.
The prefix does not have to sort its individual components.

The remaining three-block shapes are separate arguments; a hand proof of
`6+2+1` is now in the [companion note](d13_feedback_round4_merger621.md).
No new D13 complete-cover case is claimed here.

[d13_feedback_round4_mergers_verify.py](d13_feedback_round4_mergers_verify.py)
checks the triple-intersection counts, the unique two-vertex cover of the
five-block path, all eight possible t=1 first-matchings and their blind311
restrictions, and explicit median-position witnesses in the5+4 family.
It performs no SAT solving and does not enumerate all nine-wire matchings.
