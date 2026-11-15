# A twenty-fifth H9 hand case: the fork and three pairs

No seven-layer sorting network on nine wires has

```
L1 = 01 23 45,
L2 = 06 78.
```

This is a new second-layer class beyond the previous 23 and the
[twenty-fourth case](h9_feedback_next_case.md). The proof uses the
[H7/H8 early profiles](h7-early-profiles.md), the five-wire thin lemma
(README Lemma 3), and elementary matching arguments. No SAT result
or exhaustive search is a premise. The finite verifier below audits
the displayed traces and the hand classifications.

We write `+i` and `-i` for infinities placed on input i. An RR gate
compares two remaining real tracks. Whenever sentinel comparisons
move a real track, its identity moves with it; RR gates keep the
track identities and compare their values. All boundary sets and
gate endpoints below refer to physical positions **after L3**.
This convention permits the stated disjoint commutations, followed
by the usual untangling without changing gate counts.

## 1. Three small matching tools

**Five-real demand.** If four sentinels leave exactly one RR gate
through L3, L4 must have two RR gates on the resulting real set R.
Otherwise the first four layers contain at most two retained gates.
Schedule them in two layers with at most one gate each, then append
the remaining three layers. This gives a five-wire sorter of depth
at most five with both first layers thin, forbidden by Lemma 3.

**An untouched sink is forbidden.** Suppose one or two sentinels
leave respectively seven or five RR gates through L3, and their
real-track dependency order has height at most two. Each sink gate
of this retained prefix must share a track with an RR gate of L4.

Indeed, append L4's RR gates. The resulting dependency order has
height at most three. Its sinks are pairwise disjoint, so move all
of them to the third rescheduled layer. If an old sink was untouched,
at most six or four gates remain in the first two layers. The four
original layers have become three; appending L5--L7 yields an
eight- or seven-wire sorter of depth at most six. H8 requires at
least seven gates in its first two layers, and H7 requires at least
five. Both possibilities are contradictions.

Here the dependency order is defined on real **tracks**, including
the deterministic routing through sentinel comparisons. Gates on
disjoint tracks commute. There is no assumption that a real value
stays on its original physical wire.

**Three extensions force an internal pairing.** Let T have four
vertices and let u,v,w be distinct vertices outside T. If a matching
has two edges within each of T+u, T+v and T+w, it pairs T internally.
With no internal T edge, each extension has at most one edge. With
exactly one internal T edge, each of u,v,w must be matched to one
of the two unused vertices of T, which is impossible.

## 2. Eight third-layer forms

The image of L1,L2 is precisely the set of real vectors satisfying

```
x0 <= x1, x0 <= x6, x2 <= x3, x4 <= x5, x7 <= x8.
```

The prefix produces these inequalities, and fixes every vector
satisfying them. Consequently its image is invariant under swapping
1 with 6, and under permuting the ordered pairs 23,45,78.
These are genuine symmetries for arbitrary real inputs.

Place `-0`. The retained gates through L2 are the disjoint gates
23,45,78, and the sentinel stays at 0. Collapse the first two layers
to one. H8 says that L3 must then have four RR gates: it pairs
1 through 8 perfectly and leaves 0 idle. None of 23,45,78 can be
an L3 gate, because it is already ordered and would never fire;
deleting it would violate the same four-gate requirement.

We may act on L3 by the image symmetries. Formally, conjugate the
suffix by an image-preserving coordinate permutation, and untangle
any reversed comparisons of its first layer. Swapping the two
outgoing labels of each reversed comparison affects only the later
suffix. Thus the resulting L3 has the image-permuted **unordered**
matching, with ordinary ascending comparisons, and an arbitrary
later suffix of the same depth. Untangling continues through the later
suffix layers and initially gives a sorter
up to a fixed output permutation. Every sorted real vector belongs
to the prefix image and is fixed by the now-ascending network, so
that final permutation must be the identity. This argument does not require
the coordinate permutation to preserve L1 and L2 individually.

Superpose L3 on the three pair edges P={23,45,78}. There is one
alternating path from 1 to 6, and alternating cycles elsewhere.
The path uses either three, one, or zero P edges. Two is impossible:
the remaining P edge would have to be repeated by L3.

* Three P edges: their low-to-high orientations along the path are
  a three-bit string, modulo the single involution which reverses
  the string and complements every bit.
  There are four forms, represented by cases 1,2,3,6 below.
* One P edge: the other two form an alternating four-cycle, with
  either the low endpoints paired together or cross-paired.
  These give cases 4,5.
* Zero P edges: L3 contains 16. The other three P edges form a
  six-cycle. Its L3 gates either all join opposite endpoint types,
  or consist of one low-low, one high-high and one mixed gate.
  These give cases 8,7.

Hence the following eight forms are exhaustive by hand:

| Case | L3 |
|---|---|
| 1 | `12 34 57 68` |
| 2 | `12 34 58 67` |
| 3 | `12 35 47 68` |
| 4 | `12 36 47 58` |
| 5 | `12 36 48 57` |
| 6 | `13 24 57 68` |
| 7 | `16 24 37 58` |
| 8 | `16 25 37 48` |

## 3. Cases 1,2,6: strict price bounds

Each row below leaves exactly one RR gate through L3. By the
five-real demand, L4 must have two edges inside each displayed R.

| Case | Input sentinels | R after L3 |
|---|---|---|
| 1 | `+0 +1 +2 +4` | 01356 |
| 1 | `+0 +1 +2 -7` | 01367 |
| 1 | `-0 +2 +4 +7` | 12356 |
| 1 | `-0 -2 -4 -7` | 24678 |
| 2 | `+0 +1 +2 +4` | 01356 |
| 2 | `+0 +1 -4 +7` | 01456 |
| 2 | `+0 +2 +4 -7` | 01357 |
| 2 | `-0 -2 -4 -7` | 24578 |
| 6 | `+0 +1 -2 +4` | 01456 |
| 6 | `+0 +1 -2 -7` | 01467 |
| 6 | `-0 +2 +4 +7` | 12456 |
| 6 | `-0 +2 -4 -7` | 14678 |
| 6 | `-0 -2 +4 +7` | 13456 |

Let w(ab) count the displayed real sets containing both a and b.
For t rows the required total is at least 2t. The following vectors
give **twice** a price on each wire, in order 0,...,8:

| Case | Twice the wire prices | Total | Required twice-total |
|---|---|---:|---:|
| 1 | `(1,3,1,3,1,1,3,1,1)` | 15 | 16 |
| 2 | `(3,3,1,1,1,3,1,1,1)` | 15 | 16 |
| 6 | `(0,5,0,0,5,2,5,2,0)` | 19 | 20 |

For each pair ab, `2w(ab) <= p(a)+p(b)`; this can be checked directly
from the four or five sets in its column. Summing over a matching
uses each wire price at most once. The displayed totals are strictly
smaller than the demands, so these three cases are impossible.

## 4. Cases 7,8: equality and parity

Again every row retains exactly one gate through L3, so each R
requires two L4 edges.

| Case | Input sentinels | R after L3 |
|---|---|---|
| 7 | `+0 +2 -4 +7` | 01345 |
| 7 | `+0 -2 +4 -7` | 01457 |
| 7 | `-0 +2 -4 +7` | 13456 |
| 7 | `-0 -2 +4 -7` | 14567 |
| 8 | `+0 +2 +4 +7` | 01234 |
| 8 | `+0 -2 -4 -7` | 01578 |
| 8 | `-0 +2 +4 +7` | 12346 |
| 8 | `-0 -2 -4 -7` | 15678 |

For case 7 the sets are `C+a+b`, where C={1,4,5}, a ranges over
A={0,6}, and b ranges over B={3,7}. Give each C vertex price 2,
each A vertex price 1, and all others price 0. For every edge its
row count w is at most its endpoint-price sum; the total price is
8, equal to the demand. Equality therefore requires every positive
price vertex to be matched, and every used edge to be tight.
Each A vertex can be tightly matched only to B. This consumes both
B vertices. No C vertex can then have a tight external partner,
so the odd set C would have to be paired internally. Impossible.

For case 8 the sets are `{h,a}+X` and `{h,a}+Y`, with h=1,
A={0,6}, X={2,3,4}, Y={5,7,8}. Give h price 2, each X or Y vertex
price 1, and A price 0. The total price is again 8 and bounds every
edge's row count. Equality forces h to pair with one A vertex.
The tight partners of an X vertex lie in X or A, and likewise for
Y. Both X and Y are odd, so each needs an external A partner;
only one A vertex remains. Impossible.

These are reusable matching obstructions: an odd common triple
with a two-by-two rectangle of alternatives, and two disjoint odd
triples with a shared hub and two alternatives.

## 5. Cases 3,4: a forced four-set and an untouched sink

The following one-gate restrictions impose two-edge demands on R.

| Case | Input sentinels | R after L3 |
|---|---|---|
| 3 | `+0 +1 +2 -4` | 01367 |
| 3 | `-0 -2 +4 +7` | 23467 |
| 3 | `-0 -2 +4 -7` | 23678 |
| 3 | `-0 -2 -4 +7` | 23567 |
| 4 | `+0 +1 +4 -7` | 01357 |
| 4 | `-0 +2 +4 -7` | 12357 |
| 4 | `-0 -2 +4 -7` | 23567 |
| 4 | `-2 +4 +6 -7` | 02357 |

In case 3 the last three rows extend T={2,3,6,7} by 4,8,5;
in case 4 the last three extend T={2,3,5,7} by 1,6,0.
The three-extension lemma forces T to be paired internally.
In each case the first row contains three vertices of T and 0,1.
It already has exactly one T edge, and T cannot pair externally,
so it also forces gate 01. The only possible additional edge is
one edge within the complementary three-set: {4,5,8} in case 3,
or {4,6,8} in case 4.

The following contact restrictions finish all these possibilities.
Their retained prefixes have height two, and seven gates for a
one-sentinel row or five for a two-sentinel row. The listed sink
gates must each meet an RR gate of L4 by Section 1.

| Case | Label | Input sentinels | Sentinel positions after L3 | Retained sinks |
|---|---|---|---|---|
| 3 | A | `+0` | 2 | `35 47 68` |
| 3 | B | `+0 +1` | 28 | `35 47` |
| 3 | C | `+0 +2` | 25 | `47 68` |
| 3 | D | `+0 -4` | 24 | `35 68` |
| 4 | A | `+0` | 2 | `36 47 58` |
| 4 | B | `+0 +1` | 26 | `13 47 58` |
| 4 | C | `+0 +4` | 28 | `36 47` |
| 4 | D | `+0 -4` | 24 | `36 58` |

Each cell in the next two tables names a contact restriction with
an untouched sink. Every candidate also contains 01. The row is
its perfect matching of T; the column is its optional extra edge.
Checking a cell means deleting every L4 edge incident with the
specified sentinel positions and noticing one listed sink has
neither endpoint in a remaining edge.

| Case 3: T pairing | No extra edge | 45 | 48 | 58 |
|---|---|---|---|---|
| `23 67` | A | D | A | B |
| `26 37` | A | A | D | C |
| `27 36` | A | C | B | A |

| Case 4: T pairing | No extra edge | 46 | 48 | 68 |
|---|---|---|---|---|
| `23 57` | A | D | A | C |
| `25 37` | A | A | D | B |
| `27 35` | A | B | C | A |

For example, case 3 with L4=`01 23 45 67` fails row D:
sentinels on 2,4 disable 23,45, leaving sink 35 untouched.
These are only three pairing choices and four optional-edge
choices, derived by the preceding argument, rather than a scan
of arbitrary fourth layers.

## 6. Case 5: one forced fourth layer

The seven one-gate restrictions are:

| Input sentinels | R after L3 |
|---|---|
| `+0 +1 +4 +7` | 01345 |
| `-0 +2 +4 +7` | 12345 |
| `-0 +2 -4 -7` | 12378 |
| `-0 -2 +4 +7` | 23456 |
| `-0 -2 -4 -7` | 23678 |
| `-2 +4 +6 +7` | 02345 |
| `-2 -4 +6 -7` | 02378 |

The sets T={2,3,4,5} and U={2,3,7,8} both have their extensions
by 0,1,6 in this table. Therefore L4 pairs both T and U internally.
Their shared vertices 2,3 must be paired together, forcing also
45 and 78. The first row then forces 01. Thus

```
L4 = 01 23 45 78.
```

Now use `+0,+4`. Its five retained gates through L3 have height
two; the sentinels end on 2,7, and its sinks are 36 and 48.
In the forced L4 only 01 and 45 are RR gates. Sink 36 is untouched,
contradicting Section 1. This finishes the final case. □

Together with the earlier twenty-fourth case, this raises H9 hand
coverage to **25 of 50 second-layer classes**. The remaining classes
still require the existing computer-assisted proof; this does not
claim a full hand proof of D(11)>=8.

## Independent verification

[`verify/h9_feedback_next_078.py`](verify/h9_feedback_next_078.py)
has no solver imports and does not import the exploratory restriction
code. It independently traces moving real identities, checks every
displayed real set, gate count, depth and sink, and validates each
price inequality and contact-table entry.

As cross-checks, it constructs all 2,620 matchings on nine vertices:
68 possible L3 matchings have exactly the eight stated symmetry
orbits, of sizes 12,12,12,6,6,12,6,2. The five-real constraints leave
zero L4 matchings in cases 1,2,6,7,8, exactly twelve in cases 3,4,
and exactly one in case 5, precisely as the proof derives. It also
runs the prefix on every ordering of the real inputs in each listed
restriction to check the identity-routing traces directly.

The [audit](results/h9-feedback-next-078.json) stores all traces,
the 25 fourth-layer refutations, the run count and the checker hash.
The scans corroborate the hand proof; they are not assumptions of it.
