# The H9 case `03 12 46`

This note excludes a seven-layer nine-wire sorter starting with

```
L1 = 01 23 45,
L2 = 03 12 46.
```

It uses the hand H6/H7 profiles, the five-wire thin lemma, and the
[four-three-two merging theorem](h9_feedback_round2_merge432.md).
The classification below is a matching argument; no enumeration is
a premise. The independent checker audits its finite conclusions.

Write

```
A={0,1}, B={2,3}, F={5,6}, I={7,8}, C=F union I, h=4.
```

The prefix image consists exactly of the real vectors with every
A value at most every B value and with `x4<=x5,x6`; I is unrestricted.
The prefix produces these inequalities. Conversely, given desired
outputs y0,y1,y2,y3 with both lower values at most both upper values,
feed `(y0,y2,y1,y3)` into its four-wire part. Its first layer does
nothing and gate 12 puts the outputs in their requested positions.
The fork on 4,5,6 fixes every vector with its root minimal. This
proves the claimed image exactly, for arbitrary real values.

Consequently the image is invariant under interchanging the two
members of any of A,B,F,I. We may conjugate the suffix by any such
permutation and untangle through the entire suffix. This preserves
the unordered third-layer matching. The untangled network sorts
up to a fixed output permutation; sorted distinct inputs belong to
the image and are fixed by the ascending network, so this final
permutation is the identity.

Let M be L3, with every comparator that never fires removed. It has
no A--B edge and no h--F edge, because those endpoint pairs are
already ordered.

## 1. Necessary contact rules for M

For R a set of positions, call a vertex *active in R* if M pairs
it with another vertex of R. Let q(R) be the number of such edges.

**(B) Two blind six-real restrictions.** The placements
`+0,+2,-4` and `-0,-2,-4` blind both initial layers. Their real
sets are respectively A+C and B+C. Hence

```
q(A+C)>=2,  q(B+C)>=2.
```

This uses the H6 first-layer bound: a six-wire depth-five sorter
with at most one initial comparator would, after one more sentinel,
give a five-wire depth-four sorter.

**(F) Delete A or B.** If `q(V\A)<=2`, then either h is active in
V\A or both vertices of F are active there. The same holds with B
deleted.

For example `-0,-2` leaves only the two consecutive fork gates
45,46 through L2, with sentinels on A. Their depth-two tracks are
h and 6. If at most two RR gates of M avoid both tracks, the first
three retained layers have height at most two and at most four
gates. Rescheduling them to two layers would produce a seven-wire
depth-six sorter with at most four gates in its first two layers,
contrary to H7. Swapping F gives the same rule with 5 replacing 6.
Combining them gives (F). The placement `+0,+2` handles deletion of B.

**(K) Delete h and one K2,2 vertex.** For s in A, if
`q(V\{h,s})<=2`, then either the other A vertex is active or both
B vertices are active. For s in B, interchange A and B.

For `-0,-4`, the only retained prefix gates are 23 followed by 12;
the depth-two tracks are 1,2, and the sentinel positions are 0,4.
The preceding rescheduling argument requires contact with 1 or 2.
Swapping B also requires contact with 1 or 3. This proves the rule
for s=0, and swapping A proves it for s=1. Similarly `+0,-4`
leaves sentinel positions 2,4 and retained gates 13 followed by 03,
with depth-two tracks 0,3. Swapping A and B within their pairs
gives the two rules for s in B. All gates here are identified by
their real tracks at the boundary after L2.

## 2. The matching classification

Put c equal to the number of M edges internal to C. Since C has
four vertices, c is 0,1 or 2. Contributions to q(A+C) are those c
edges plus the A-internal and A--C edges; analogously for B.
There are at most four edges altogether.

**h cannot meet A or B.** Suppose h meets A. Rule (B) and the
four-edge limit force c>=1. If c=1, each side contributes exactly
one further edge: the unused A vertex meets C, while B has either
its internal edge or one B--C edge. Choose s in B on that edge.
After deleting h,s, at most two edges remain. The other B vertex
is inactive, as is the A vertex paired with h, contradicting (K).
If c=2, C is fully used, the unused A vertex is idle, and the only
possible extra B edge is internal. Deleting h and either B vertex
again contradicts (K). The argument with A,B interchanged is the
same.

**If h meets I, both A and B pair internally.** Here c>=1 by (B)
and the edge limit, and c<=1 since one C vertex meets h. Each side
must contribute exactly one edge. Only one C vertex remains for
these contributions, so at least one contribution is an internal
pair. If the other is a cross edge, delete h and one vertex of
the internal pair: only two RR edges remain, the other vertex of
the pair is inactive, and one vertex of the cross side is idle.
This violates (K). Thus

```
M = 01 23 (h,i) e,  i in I,  e a pair in C\{i}.             (X)
```

**Suppose h is idle.**

* If c=0, rule (B) forces two A--C and two B--C edges. By (F),
  deleting A requires both F vertices to meet B, while deleting B
  requires both to meet A. This is impossible in a matching.
* If c=2, C is fully paired. If, say, A is not internally paired,
  delete h and a B vertex. Only the two C edges remain, while
  both A vertices and the other B vertex are inactive, violating
  (K). Thus both A and B pair internally, giving the desired form
  `M=01 23 K`, where K pairs C.
* If c=1, each side needs at least one additional contribution.
  If both pair internally, (F) forces the C edge to be 56:
  `M=01 23 56`. If one side pairs internally and the other has
  just one cross edge, delete h and a vertex of the internal pair;
  (K) fails because one opposite vertex is idle. Thus the cross
  side has two cross edges; (F), deleting that side, forces the
  C edge to be 56, and the two cross edges go to I. If neither
  side pairs internally, only two C vertices remain, so each side
  has exactly one cross edge. Delete h and the used vertex of
  either side; (K) again fails.

The only exceptional forms besides (X) are therefore

```
01 23 56,                                                   (Y)
01 56 + a perfect matching from B to I,                     (Z_A)
23 56 + a perfect matching from A to I.                     (Z_B)
```

## 3. The exceptional forms force incompatible six-real pairings

In every row pair below, the first three original layers retain
exactly two disjoint real-track gates. Collapse them to a single
first layer on six reals. H6 then forces L4 to pair all six real
positions. The two real sets have intersection five, so they
cannot both be unions of edges of one matching.

| Form | First placement | Second placement | Sentinel sets after L3 |
|---|---|---|---|
| (X) | `+0,+2,-4` | `+0,-1,-4` | 234 and 034 |
| (Y) | `+0,+2,+4` | `+0,+2,-4` | 236 and 234 |
| (Z_A) | `+0,+2,+4` | `+0,+2,-4` | 678 and 478 |
| (Z_B) | `-0,-2,+4` | `-0,-2,-4` | 016 and 014 |

For (X), the retained gate pairs are `01,e` and `12,e`, using
boundary positions; the h--I comparison always meets the negative
sentinel at h. For (Y) and (Z_A), they are `01,45` and `01,56`;
for (Z_B), they are `23,45` and `23,56`. The table holds uniformly
for either bijection in (Z_A),(Z_B) and all six choices in (X).

For completeness, H6's first-two profile follows by hand from
D(5)>=5 and the five-wire thin lemma. Each of the first two layers
of an optimal six-wire depth-five sorter has at least two gates:
otherwise one sentinel blinds that layer and leaves a five-wire
depth-four sorter. If both layers have two gates, their four-wire
supports intersect. A sentinel on a common supported wire, with
its sign chosen to remain there in the first layer, leaves at
most one RR gate in each first layer on five reals, contrary to
the thin lemma. Thus the only profiles are (2,3),(3,2),(3,3).

We have proved

```
L3 = 01 23 K,  with K a perfect matching on {5,6,7,8}.
```

## 4. The two possible K shapes

Swapping F or I reduces K to `56 78` or `57 68`.

If K=`57 68`, the placements `+0,+2,+4,+5` and
`-0,-2,+4,+5` retain exactly one gate through L3, leaving real
sets 01456 and 23456. The five-wire thin lemma requires L4 to
have two edges in each set. Gates 01 and 23 never fire after L3,
which has fully sorted wires 0,1,2,3. Price each common vertex
4,5,6 at 1 and every other vertex at 0. Every permitted edge's
membership count in the two sets is at most its endpoint-price
sum: an internal common edge counts twice, and a cross edge
once. A matching has budget 3, while the two demands total 4.
Contradiction.

If K=`56 78`, the first three layers have sorted three independent
blocks of lengths 4,3,2, and their image is exactly all vectors
sorted within those blocks. The four remaining layers would
merge those blocks, contrary to the standalone
[four-three-two merging theorem](h9_feedback_round2_merge432.md).
This finishes this H9 class.

The proof dependencies are D(5)>=5, the five-wire thin lemma,
the hand H7 early profile, and the H6 profile derived above.
The merging theorem itself uses only D(5)>=5 and the thin lemma
(including their H6 consequence).
