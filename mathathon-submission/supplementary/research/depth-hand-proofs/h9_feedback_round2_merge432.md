# Four sorted, three sorted, two sorted: four merger layers are impossible

**Theorem.** A comparator network merging three independently sorted
blocks of lengths 4,3,2 needs at least five layers. The positions of
the blocks may be fixed arbitrarily; relabel and untangle to use
blocks A=0123, B=456 and C=78.

The proof is by hand. Its only small-sorter inputs are D(5)>=5 and
the five-wire thin lemma, including their consequence that the
first-two profiles of a six-wire depth-five sorter are
(2,3),(3,2),(3,3). No earlier H9 case or exhaustive search is used.

Suppose a four-layer merger exists. Call its first two matchings
N and Q. Remove every comparator which never fires on the input
image reaching it. In particular, N has no edge internal to a block,
and Q repeats no N edge.

## 1. Six restrictions force eight first layers

Keep any two consecutive ranks of A, any two consecutive ranks of
B, and both ranks of C, replacing all other inputs by appropriate
negative or positive infinities. The six reals arrive as three
sorted pairs. A single layer of three comparisons creates every
such real input, so prefixing that layer to the restricted merger
gives a six-wire depth-five sorter. H6 requires N to retain at
least two RR edges in each of the six sets

```
{i,i+1,j,j+1,7,8},  i=0,1,2 and j=4,5.                 (1)
```

The following argument classifies all matchings meeting (1).

Both C vertices must be used. If neither is used, the disjoint A
intervals 01 and 23 require at least four A--B edges, exceeding B's
size. If just one C vertex meets A, choose an A interval avoiding
its partner. Two A--B edges must then lie in both B intervals 45
and 56, forcing both to use vertex 5. If just one C vertex meets a
B endpoint 4 or 6, choose the B interval avoiding it; the two
disjoint A intervals again require four A--B edges. If its partner
is 5, each B endpoint 4 and 6 would have to meet every A interval,
whose common intersection is empty.

The two C vertices cannot both meet B. Some B interval contains
exactly one of their partners, so the sole remaining B vertex
would need an A partner in all three A intervals. Nor can both
meet A. If their partners lie in the same extreme interval 01
or 23, the other interval needs two A--B edges lying in both B
intervals. Otherwise each extreme A interval contains one C
partner, and its other vertex must meet B's common vertex 5.
Both alternatives violate the matching property.

Thus one C vertex meets A at a and the other meets B at b. If b
is an endpoint 4 or 6, choose the B interval excluding b. Across
the two disjoint A intervals, the demands total four; the A--C
edge contributes only one and the at most two A--B edges contribute
at most two. Therefore b=5.

Each B endpoint 4,6 must now have an A partner x4,x6: without that
edge, the A--C partner a would have to lie in every A interval.
For each endpoint b=4,6, the pair {a,xb} must hit all three
intervals 01,12,23. The only hitting pairs are 02,12,13.
Since x4 and x6 are distinct, either

```
a=1 and {x4,x6}={2,3},  or  a=2 and {x4,x6}={0,1}.
```

There are exactly eight forms: two choices of a, two assignments
of its opposite pair to 4,6, and two assignments of C to a,5.

Global value negation followed by reversal within each sorted
block preserves the merger input family. Conjugating a merger by
this operation and untangling through its entire suffix preserves
depth and maps its first unordered matching by
`(0 3)(1 2)(4 6)(7 8)`. As usual, the final fixed permutation is
the identity because sorted distinct inputs are fixed by the
ascending network. This pairs the a=2 forms with the a=1 forms.
It therefore suffices to exclude

| Case | N |
|---|---|
| 1 | `17 24 36 58` |
| 2 | `17 26 34 58` |
| 3 | `18 24 36 57` |
| 4 | `18 26 34 57` |

## 2. A three-gate restriction forces contact with every sink

Prepend the following three-layer block sorter to the alleged merger:

```
01 23 45 | 03 12 46 | 01 23 56 78.
```

Its image is exactly the three sorted blocks. For each placement
in the tables below, four sentinels leave exactly three RR gates
through this prefix and N. A *sink* is a retained gate with no
later retained comparison on either of its real tracks.

Every sink must share a real track with an RR gate of Q. Otherwise,
append Q's RR gates and move all sinks to the third rescheduled
layer. The untouched old sink, in addition to all Q gates, leaves
at most two earlier gates, which can occupy one gate each in the
first two layers. The retained network has height at most three:
if the original three gates formed a chain of height three, its
last gate was precisely the untouched sink; otherwise its height
was at most two before Q. Appending the two final merger layers
would give a five-wire depth-five sorter with two thin first
layers, a contradiction.

Each contact row `(R,e)` thus requires an edge of Q contained in
the real set R and incident with an endpoint of sink e. Track
identities move through sentinel comparisons. All R and e labels
refer to physical positions **after N**, and the verifier checks
these traces on every ordering of the five remaining real inputs.

## 3. Cases 2 and 4 share a six-row contradiction

Let c be the C vertex paired with 5 by N, and d the other C vertex.
Thus (c,d)=(8,7) in case 2 and (7,8) in case 4. The following
placements have the indicated contact requirements in both cases:

| Row | Input sentinels | R after N | Sink e |
|---:|---|---|---|
| 1 | `+0 +1 +2 +4` | {0,1,3,5,c} | 5c |
| 2 | `+0 +1 +2 -4` | {0,1,2,5,c} | 5c |
| 3 | `+0 -1 -2 +4` | {2,3,5,c,d} | 5c |
| 4 | `-0 -1 -2 -4` | {4,5,6,c,d} | 5c |
| 5 | `-0 -2 +4 +5` | {2,3,4,5,d} | 5d |
| 6 | `-0 -2 -4 -5` | {2,4,6,c,d} | cd |

Edge 5c is forbidden as a repetition of N. Therefore the partners
of 5 and c must hit each of the four triples

```
{0,1,3}, {0,1,2}, {2,3,d}, {4,6,d}.
```

No vertex hits three triples. The first two intersect in {0,1},
the last two in {d}, and the other possible partitions into two
intersecting pairs each have an empty intersection. Hence both
vertices are matched and their partner set is {a,d}, a in {0,1}.
If Q uses `5a,cd`, row 5 is untouched: both partners lie outside
its R. If Q uses `5d,ca`, row 6 is untouched. Contradiction.

## 4. Case 1: six partner pairs

For N=`17 24 36 58`, the ten contacts are:

| Row | Input sentinels | R | e |
|---:|---|---|---|
| 1 | `+0 +1 +2 -4` | 01358 | 58 |
| 2 | `+0 -1 -2 -4` | 34578 | 58 |
| 3 | `+0 +1 +2 +7` | 01235 | 35 |
| 4 | `+0 -1 -4 +7` | 13457 | 35 |
| 5 | `+0 +2 +4 +5` | 01257 | 17 |
| 6 | `-0 -2 +4 +5` | 23457 | 57 |
| 7 | `-0 -2 +4 +5` | 23457 | 24 |
| 8 | `-0 -2 -4 -5` | 34678 | 78 |
| 9 | `-0 -2 -4 -5` | 34678 | 36 |
| 10 | `+0 +2 +4 -7` | 02578 | 58 |

Since 58 is forbidden, rows 1,2,10 force the two partners of 5,8
to hit the triples 013,347,027. Their intersection is empty, so
both partners exist. The possible unordered partner pairs are
03,04,07,17,23,37. This follows by choosing a vertex from 013:
0 needs 3,4 or7; 1 needs 7; 3 needs 0,2 or7. Vertex pairs which
repeat this list are counted only once.

In the table, `r=>uv` means contact row r forces edge uv after the
displayed partners have been fixed, and `r=empty` means no legal
edge can satisfy that row. All four N edges remain forbidden.

| Unordered pair (a,b) | Q has `5a,8b` | Q has `5b,8a` |
|---|---|---|
| (0,3) | row 4 empty | Leaf D |
| (0,4) | Leaf C | Leaf B |
| (0,7) | row 6 empty | row 8 empty |
| (1,7) | row 6 empty | row 8 empty |
| (2,3) | row 4 empty | row 7=>47; row 9 empty |
| (3,7) | row 7 empty | row 3 empty |

The three leaves require only one binary split each:

* **B: Q has 45,08.** Row 3 requires 13 or23. If 13, row 5
  forces 27 and row 8 is empty. If 23, row 5 is already empty.
* **C: Q has 05,48.** Row 6 requires 27 or37. If 37, row 5
  forces 12 and row 7 is empty. If 27, row 4 forces 13 and
  row 9 is empty.
* **D: Q has 35,08.** Row 5 requires 12 or27. If 27, row 8
  is empty. If 12, row 7 forces 47 and row 9 is empty.

This rules out case 1 without enumerating the other Q edges.
The [branch checker](verify/h9_round2_case1_branch_check.py)
independently checks all twelve orientations and their fifteen
contradiction leaves.

## 5. Case 3: seven partner pairs

For N=`18 24 36 57`, the ten contacts are:

| Row | Input sentinels | R | e |
|---:|---|---|---|
| 1 | `+0 +1 +2 -4` | 01357 | 57 |
| 2 | `+0 -1 -2 -4` | 34578 | 57 |
| 3 | `+0 -1 -4 -5` | 13478 | 18 |
| 4 | `+0 -1 -4 +7` | 13457 | 14 |
| 5 | `+0 +2 +4 +5` | 01258 | 18 |
| 6 | `+0 +2 -4 -5` | 01378 | 18 |
| 7 | `-0 -2 -4 -5` | 34678 | 78 |
| 8 | `-0 -2 -4 -5` | 34678 | 36 |
| 9 | `-0 -2 +4 -7` | 23478 | 24 |
| 10 | `+0 -4 -5 +7` | 01347 | 01 |

Because 18 is forbidden, rows 3 and 5 force the partners of 1,8
to consist of one a in {3,4,7} and one b in {0,2,5}. Row 6
requires b=0 if a=4. The resulting seven pairs and fourteen
orientations are contradicted by the explicit partner table in
the [companion hand proof](h9_root_helper_case3.md). Eleven
orientations fail immediately or after one forced edge. The other
three reduce to these clauses:

* Q has `13,28`: rows 7,8 require `47 or67`, `46 or67`.
  Thus 67 is forced; rows 1,2 then force the incompatible 05,45.
* Q has `14,08`: rows 1,7 require `35 or37`, `37 or67`.
  They use both 3 and 7, leaving row 9's `23 or27` impossible.
* Q has `15,78`: rows 8,9 require `34 or46`, `23 or34`.
  They use both 3 and 4, leaving row 10's `03 or04` impossible.

Thus case 3 also fails. All four normalized first merger layers
are impossible, proving the theorem. □

## Verification and scope

The proof classifies N by the six interval restrictions, then Q
by small partner tables. It does not depend on a SAT refutation
or on testing all merger layers. The companion checkers audit
the two partner tables; the integrated checker traces the signed
restrictions, checks every stated sink and the two uniform
six-row cases, and cross-checks the classification with finite
matching enumeration.

The theorem applies to any suffix required to merge independently
sorted blocks of lengths 4,3,2. In particular it closes the final
branch of the [H9 case `03 12 46`](h9_feedback_round2_031246.md).
It does not assert that these blocks must arise in every remaining
H9 case.
