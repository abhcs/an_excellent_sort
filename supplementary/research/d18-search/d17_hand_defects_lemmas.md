# Small hand certificates extracted from the D17 defect screen

**Result.** There are short weighted-counting proofs of the exact shapes of
fully satisfied rows and columns of the case-608 restriction grid. There is
also a four-restriction hand proof rejecting the saved first matching that
satisfies eleven restrictions. These are structural lemmas and a conditional
branch proof. They do not replace the checked SAT proof over **all** first
matchings, and they do not prove the complete D17 lower bound.

The family and checked complete-case result are recorded in
[d17_feedback_results.md](d17_feedback_results.md). A restriction **peaks**
in a matching when it retains four real-real edges. The family is

    R_ij = {1,2} union A_i union B_j,

with row-major index 5i+j:

| i | A_i | j | B_j |
|---:|---|---:|---|
| 0 | 4,7,8 | 0 | 10,12,15,16 |
| 1 | 4,5,8 | 1 | 10,12,13,16 |
| 2 | 4,5,6 | 2 | 10,12,13,14 |
| 3 | 5,7,8 | 3 | 10,13,15,16 |
| | | 4 | 9,13,15,16 |

Every set has nine reals. All statements below allow partial matchings and
repeated comparators; no maximality or nonredundancy assumption is used.

## 1. Weighted counting and equality

For a family F of real sets, put

    w(ab) = number of sets R in F containing both a and b.

Then, for every matching M,

    sum_{R in F} e_M(R) = sum_{ab in M} w(ab).

If nonnegative wire prices p_a obey w(ab)<=p_a+p_b, it follows that

    sum_{R in F} e_M(R) <= sum_a p_a.                 (1)

Matching edges use each wire at most once. If equality holds, every wire
of positive price is matched, and every used edge has equality in its
price bound. These two elementary observations prove the classifications
below. Wires outside the displayed union have price zero; edges to them
cannot evade the argument.

## 2. A full column forces one edge and an eight-wire perfect matching

Fix j and write C={1,2} union B_j, so |C|=6. The four real sets in this
column are

    C+478, C+458, C+456, C+578.

**Column lemma.** A matching peaks in all four sets if and only if it
contains (7,8) and a perfect matching of C union {4,5}. Other edges are
irrelevant to these four retained counts.

*Proof.* Give each C wire price 2, wires 4,5,7,8 price 1, and all others
price 0. The total price is 16. The relevant co-occurrence counts are:

| Endpoint types | Weight |
|---|---:|
| C,C | 4 |
| C with 4,5,6,7,8 respectively | 3,3,1,2,3 |
| 45,46,47,48 | 2,1,1,2 |
| 56,57,58 | 1,1,2 |
| 67,68,78 | 0,0,2 |

They all obey the price bounds. Four peaks require total count 16, so
there is equality in (1). Wire 7 has positive price and its only tight
partner is 8. Thus (7,8) is forced.

After removing that edge, the eight positive-price wires C union {4,5}
are all matched. Their only tight partners outside those eight are wire
6, which may partner 4 or 5. Using it would leave seven positive-price
wires to be paired internally, which is impossible. Therefore the eight
wires are perfectly matched among themselves.

Conversely, take (7,8) and any perfect matching on C union {4,5}. If 4
and 5 are partners, the four counts are each three C-edges plus either
45 or 78. Otherwise 4 and 5 have different C partners; the two sets
containing both retain those two edges and the two remaining C-edges,
while the other two retain one of them, the two C-edges, and 78. Each
count is four. ∎

There are exactly 7!!=105 possible restrictions of such a matching to
the eleven-wire union. Wire 6 is idle in that union; it may have a partner
outside it. This count is a consequence of the classification, not a
computational premise.

## 3. A full row forces two edges and one hub partner

Fix i and write C={1,2} union A_i, so |C|=5.

**Row lemma.** A matching peaks in all five sets of this row if and only
if it contains

    (10,12), (15,16), (13,c) for some c in C,

and a perfect matching of C minus {c}. Other edges are irrelevant to
these retained counts.

*Proof.* Give each C wire price 5/2; give wires 10,12,13,15,16 price
3/2; give every other wire price zero. The total price is 20.
Every C-C edge has weight 5. The C-to-variable weights on wires
9,10,12,13,14,15,16 are respectively 1,4,3,4,1,3,4, all within the
price bounds. Among positive-price variable wires, the weight-three
pairs are

    (10,12), (10,13), (10,16), (13,16), (15,16);

all other such pairs have weight at most two. A zero-price variable
wire, 9 or 14, is real in only one restriction, and the pair 9,14 is
never co-real. Thus every edge obeys its price bound.

Five peaks require total count 20, giving equality in (1). Wire 12 has
positive price and its only tight partner is 10. Likewise, wire 15's
only tight partner is 16. After these two edges are removed, the positive
wires are C and 13. The only remaining tight partners of 13 are in C,
and the other four C wires must pair internally. This proves necessity.
Directly count the two fixed edges, the hub edge when present, and the
two C-edges to obtain four in each restriction, proving sufficiency. ∎

There are 5 times 3=15 choices of the five forced retained edges. Within
the twelve-wire union, the unused wires 9 and 14 may be left idle or
paired together, giving 30 matching restrictions. Again the count follows
from the proof.

These are static classifications. Applying them to layer 4 requires the
**transported** family to have the specified real sets. Applying the
initial grid shapes directly after arbitrary layer 3 would be invalid.

## 4. A reusable four-set obstruction

Let C contain six wires, and let a,b,c,x,y,z be six further distinct
wires. Consider

    C+{a,b,x}, C+{b,c,y}, C+{a,b,c}, C+{a,c,z}.       (2)

**Four-set lemma.** No matching peaks in all four sets (2).

*Proof.* Give each C wire price 2, wires a,b,c price 1, and all other
wires price zero. The price sum is 15.

A C-C edge has weight 4. A C-to-a/b/c edge has weight 3; a C-to-x/y/z
edge has weight 1. Each pair among a,b,c has weight 2. A pair with one
endpoint in x,y,z and one in a,b,c has weight at most 1. Distinct members
of x,y,z are never co-real. Thus all edges obey their price bound, and
(1) gives a total retained count at most 15. Four peaks require 16. ∎

This is a four-state obstruction, independent of width, sentinel signs,
and how the real sets were obtained. It can be applied after any exact
transport computation. The six common wires need not be paired together.

## 5. Four transported restrictions reject the saved eleven-peak matching

The saved first matching is

    M=(1,2)(4,16)(5,13)(6,14)(7,8)(9,15)(10,12).

It has eleven peaks in the original twenty-state family. The four
restrictions with indices 2,5,15,18 each retain **three** M-edges, so each
would require a peak in the following matching N.

Their transported real sets have common part

    C={1,2,4,7,10,13},

and remaining triples

| Original index | After transport by M, outside C |
|---:|---|
| 2 | 8,12,14 |
| 5 | 12,15,16 |
| 15 | 8,12,15 |
| 18 | 5,8,15 |

They have form (2) with

    (a,b,c)=(8,12,15), (x,y,z)=(14,16,5).

The four-set lemma rules out every following matching N. This replaces
the earlier SAT-based rejection of this **one specified first matching**
with a four-restriction hand proof. It does not rule out all first
matchings of the complete case.

The four restrictions are indispensable to this particular obstruction:
after deleting any one, a matching peaks in all three remaining sets.
Explicit matching controls are in
[the certificate](results/d17-hand-defects-four-set.json). Thus the proof
is not hiding a simpler one-, two-, or three-state pairing impossibility.

## 6. Another local classification from the shared-gate bound

Suppose a collection of restrictions has pairwise real-set distance at
most two and all peak in one matching. Their retained four-edge sets
have pairwise intersection at least three, by the shared-gate lemma in
`d17_feedback_results.md`.

Such a collection has one of two forms: all retained edge sets contain
a fixed triple, or all lie inside a fixed five-edge set.

*Proof.* Choose two distinct retained sets T+{a},T+{b}, where |T|=3.
A further four-set intersecting both in at least three elements either
contains T, or is {a,b} together with two elements of T. If the latter
occurs, a set T+{c} with c outside T+{a,b} would intersect it in only two.
Hence either every set contains T, or every set lies in T+{a,b}. ∎

This reduces a close cluster of peak restrictions to a triple shared by
all or a five-edge union. It remains a local classification; it does not
supply the missing global transport argument by itself.

## 7. Verification and exact remaining scope

Run

```sh
python d18-search/d17_hand_defects_verify.py
```

The verifier uses no SAT. It checks all 1,360 edge-price inequalities
for the five columns, four rows, and transported four-set certificate;
replays the signed transport from the original twenty states; checks
that the four chosen restrictions each retain three first-layer edges;
and checks explicit positive matching controls. Its
[result](results/d17-hand-defects-verification.json) is `VERIFIED`.

The earlier small static enumeration in
[the static audit](results/d17-hand-defects-static.json) agrees with the
105-column and 30-row counts. That enumeration discovered the shapes;
the proofs above establish them independently.

The universal pure two-matching case-608 result is independently checked
SAT, as documented by the other agent. The unresolved hand-proof target
is to show that every first matching either leaves a contradiction among
whole rows/columns or creates a forced second-layer subfamily admitting
one of these weighted obstructions. The present note establishes neither
that dichotomy nor a complete cover of first matchings. No solver was
invoked for this note or its verifier.
