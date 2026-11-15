# Case 606: two idle wires suffice, and a critical-edge branch closes

This note adds two hand reductions for the twenty-state case-606 family.
Any hypothetical two-layer peak cover can be normalized so that the first
matching has at most two idle wires. Also, a perfect first matching with
no A--B edges is impossible, including the previously exceptional B edge.
The corresponding two-idle-wire branch is impossible when both idles lie
in the same block and there are no A--B edges.

These results do **not** complete case 606. They hold with any even number
of additional common real wires, and hence give structural statements
independent of the original fourteen-wire embedding. No SAT result or
large matching scan is a premise of the hand proofs in Sections 1--4.
Section 6 separately records a computer-assisted padding consequence.

## 1. The family and safe augmentation

Distinguish A labels by capitals. The A sentinel pairs are

    G = {AB, BC, CE, BD},       A-, B-, C+, D+, E+.

The five B sentinel triples, using lower-case labels, are

    qab, qbc, qce, rce, qbd,
    q-, a-, b-, c+, d+, e+, r+.

Take the product of these four rows and five columns. All other coordinates
are always real. At even width n=2h>=12, each state has five sentinels and
2h-5 reals. A peak is h-3 real-real comparators. The fourteen-wire case
has h=7 and peak four.

For the concrete case-606 indexing, the labels are

| Block | Labels in compact indexing |
|---|---|
| A | A=3, B=4, C=5, D=2, E=6 |
| B | a=8, b=9, c=10, d=7, e=12, q=11, r=13 |
| Common reals | 0,1 |

The B critical comparator dc is compact 7--10, originally 10--13.

Write M for the first matching and N for the last counted matching.
Complete N to a perfect matching. For a sentinel set S, if u sentinels
are idle in M and s M-edges join two sentinels, then

    RR_M = |M|-5+u+s.

A perfect N therefore peaks exactly when it has two edges inside the
transported five-element sentinel set.

If two M-idle type coordinates are ordered in one fixed direction across
all twenty states, their comparator can be added safely. On the types it
acts as one fixed identity or transposition; conjugating N by that fixed
permutation preserves every second-layer RR count. The first count only
increases. Repeating this operation leaves an antichain of idle type
coordinates. This is the comparable-coordinate augmentation proved in
[the twelve-wire structural note](d17_feedback_twelve_structure.md#7-comparable-idle-coordinates-reduce-five-gates-to-six).

## 2. The type order closes the four-idle-wire branch

Every negative-only coordinate is below every positive-only coordinate,
and an always-real coordinate is comparable with every coordinate.
Within the negative coordinates, A and B form one chain, while q,b,a
form another. Within the positive coordinates, the orders are

    E <= C, with D incomparable to C,E;
    r <= e <= c, with d incomparable to r,e,c.

Coordinates in the same sign class but in different variable blocks
are incomparable: their choices vary independently. Thus the type order
has width four. Every four-element antichain has exactly the form

    {D, X, d, y},       X in {C,E}, y in {c,e,r}.       (1)

The idle set has even size, so safe augmentation leaves zero, two, or
four idle wires. Suppose four remain. Each A row contains at most one
of D,X, since neither DC nor DE is a G-edge. Each B column contains at
most one of d,y: d occurs only in qbd, together with negative q,b.
Consequently every state has at most two idle sentinels. Its other at
least three sentinels touch at least two different M-edges. Since
|M|=h-2, it has at most h-4 RR edges and cannot peak.

All twenty states must therefore peak in N. The B vertex d is idle,
so M cannot contain critical dc. The corrected five-column row lemma in
[the B-family note](d17_feedback_fourteen_hand_Blemma.md#5-corrected-row-consequence-for-the-full-fourteen-wire-family)
forces N to pair the two transported A sentinels in every G-row outside
M. The folded-fork lemma says these pairs cannot be a matching. This is
a contradiction.

**Normalization theorem.** A hypothetical peak cover of this signed
family can always be transformed into one whose first matching is
perfect or has exactly two idle wires.

This does not say that adding arbitrary comparators preserves a cover;
only comparators between universally comparable idle types were added.
The theorem also does not exclude every unnormalized small M directly:
it eliminates those ending with four idles and sends all others to the
perfect or two-idle problem.

For later use, the possible incomparable idle pairs are exactly two A
pairs DC,DE; three B pairs dc,de,dr; and eighteen same-sign A--B pairs.
There are six negative and twelve positive A--B pairs.

## 3. The critical edge still forbids two incident required rows

The old row lemma had a necessary exception: dc can destroy the requirement
that N pair the two common A sentinels. The weaker property actually needed
for a fork survives when the B coordinate routing is common to the rows.

After dc, the five B sentinel triples become

    qab, qbc, qce, rce, qbc.                          (2)

All other B--B comparators act as fixed type routings, because d and c are
already used and the remaining type coordinates form chains. The exact
static classification from the B-family note says that, for two common
sentinel positions u,v, N must contain one of the following cores:

    ordinary:      uv, qb, ce;
    exceptional:   ab, re, and a perfect matching of {u,v,q,c}.   (3)

All six named B positions a,b,c,e,q,r are distinct and outside u,v.

**Incident-row lemma.** Let u,v,w be three distinct positions outside
these six B positions. No matching satisfies the five-column demands
for both common pairs uv and uw in (2).

*Proof.* If both rows choose the ordinary alternative, N would pair u
with both v and w. If exactly one chooses it, its edge qb conflicts with
the other's edge ab (also ce conflicts with re). If both choose the
exceptional alternative, N must pair both four-sets {u,v,q,c} and
{u,w,q,c} internally. Their intersection {u,q,c} would also have to be
paired internally, which is impossible because it has odd size. These
exhaust the alternatives. ∎

More generally, a graph of common pairs whose rows all need N must be
a matching. This is a reusable extension of pair forcing: the individual
pair need not be forced, but two incident pairs are still incompatible.
The argument uses incompatible fixed cores and an odd intersection; it
does not depend on the wire order, signs, or ambient width after the
sentinel sets have been obtained.

## 4. Closing first matchings with no A--B gates

Assume M has no A--B edge. Comparisons between B and a common real have
fixed routing over the whole family. All B--B gates except possibly one
of dc,de,dr also have fixed routing. The resulting relabelling of the B
coordinates is therefore independent of the A row. For a G-edge UV
outside M, its two A sentinels occupy their singleton destinations
f(U),f(V); these are outside the B positions. Different A singleton
images merge only across a same-sign A--A gate.

If dc is absent, every fully required row forces its folded pair into N,
by the old row lemma. If dc is present, Section 3 instead says the graph
of fully required folded rows must be a matching. Thus in either case
the same folded-fork contradiction applies whenever every G-row outside
M needs N in all five columns.

**Perfect M.** For UV outside M, its A sentinels cannot form an SS edge.
There are no A--B gates, and the three B sentinels give at most one SS
edge. A perfect M needs two SS edges for a peak, so all five columns of
every such row require N. The folded-fork contradiction excludes M.

**Two idles, both in A or both in B.** After normalization, the idle pair
is DC or DE, or one of dc,de,dr. No state contains both idle positions.
For UV outside M there is still at most one SS edge, and at most one idle
sentinel. Thus

    RR_M <= (h-1)-5+1+1 = h-4,

below the peak h-3. Again all the relevant rows require N, and the
folded-fork contradiction excludes M. This includes critical dc when
the two idles lie in A.

The uniform-routing argument also gives a useful conditional extension.
If every A--B gate has opposite sentinel signs, each such gate acts as a
fixed type routing across the whole family. The B positions remain
separate from the A singleton images. Consequently the same incident-row
criterion applies, including in the dc branch, to any collection of
fully required G-rows outside M. Such cross gates can produce first
peaks, so full-row necessity must be checked rather than presumed.

## 5. Verification, feedback, and the remaining gap

`d17_feedback_round2_verify.py` independently checks the type order and
all six maximal idle patterns, all 26 local A matchings for the folded
fork, and all sixteen ordinary/exceptional core combinations for two
incident rows. It also directly checks the no-first-peak and singleton
transport premises for the 5,670 fourteen-wire first matchings with the
six specified four-idle patterns. These checks corroborate the above
hand proof; the proof does not use that scan.

A separate bounded structural screen examines the 10,395 perfect first
matchings containing dc. It conjoins only the four explicitly derived
core choices for each fully required row, excludes 9,643, and leaves
752 undecided. Its survivors are merely
cases left open by that particular criterion; they are not peak covers
and are not sorting networks. This screen uses no SAT and does not
search second matchings. The saved examples explain why full-row
forcing alone is insufficient: some first matchings have no fully
required row at all, though many individual states still need N. One
concrete compact-index example is

    M = {01, 23, 48, 56, 7--10, 9--11, 12--13}.

Here the four A rows have respectively one, one, four, and one first-layer
peaks, so thirteen individual states still require N. This is an undecided
first matching for the full-row screen, not a two-layer cover.

The remaining hand gap is precise. After normalization, a hypothetical
606 cover has either a perfect first matching with at least one A--B
edge, or a two-idle first matching with A--B edges or with one idle in
each block. Some are already excluded by the earlier full-row criterion;
the mixed branches need constraints from partially required rows. The
hand status of case 608 is unchanged. No complete D17 or D18 claim is made.

## 6. Padding gives seven/eight-real obstructions without H9

Both supplied fourteen-wire families have exactly two coordinates that
are real in all twenty states: compact coordinates 0,1, corresponding to
original labels 1,2. Let F12 be the family obtained by deleting both,
and F13 the family obtained by deleting just compact coordinate 0.
Their twenty states have seven and eight reals respectively.

**Padding transfer.** If F14 is a pure two-layer peak-four obstruction,
then F12 is a pure peak-three obstruction and F13 is a pure peak-four
obstruction.

*Proof.* A hypothetical pair of matching layers covering F12 at peak
three extends to F14 by adding the common-real comparator 01 to **both**
layers. That disjoint comparator contributes one RR gate in each layer
for every state, and does not change any other type transport. This would
cover F14 at peak four. For F13, add the missing common-real wire as an
idle wire in both layers; all counts and all other transports are
unchanged. This also contradicts the F14 obstruction. ∎

Repeating 01 is allowed in the pure formula. This is why the older
seventeen-wire case-606 certificate, which includes nonrepetition and
nonemptiness conditions, was not by itself an adequate premise.
A fresh [pure case-606 certificate](results/d17-feedback-round2-pure606/audit.json)
now supplies the needed premise: 2,150 variables, 19,428 clauses, UNSAT
in 6.89 seconds and independently DRAT-verified in 5.08 seconds. The solve
and proof check each had a separate 30-second wall limit and exited zero.
Case 608 uses its existing
[pure fourteen-wire audit](results/d17-feedback-fourteen-audit.json).
These two finite obstructions remain computational premises; the padding
proof does not turn them into full hand proofs.

The ordered retained original labels are:

| Family | Active labels after deleting both common reals |
|---|---|
| 606, F12 | 4,5,6,7,8,10,11,12,13,14,15,16 |
| 608, F12 | 4,5,6,7,8,9,10,12,13,14,15,16 |

For F13, prepend original label 2 to the corresponding row. Deleting
original label 2 instead of 1 gives an equivalent family with label 1
as the remaining common real. The explicit state files and padding checks
are bound in [the transfer audit](results/d17-feedback-round2-padding.json).

By the [fixed-sentinel pruning and permutation lemma](fixed-sentinel-obstruction.md#2-hand-lemma-common-fixed-sentinels-can-be-removed),
either smaller family can be embedded in any order among eighteen wires,
with all extra coordinates fixed signed sentinels across the family.
If a hypothetical depth-ten eighteen-wire sorter has twenty restrictions
that blind its first four layers and realize one of these families at
the cut, its remaining six-layer sorter is impossible. H7 requires a
three-gate layer among its first two layers on seven real wires; H8
requires a four-gate layer on eight. Both profile results have hand
proofs. Thus this application needs no H9 premise, although it still
uses the pure fourteen-wire computational certificate.

No assertion is made that every four-layer prefix, or any newly identified
specific prefix, realizes one of these families. This transfer adds
structural targets for D18; it does not close a D18 cover case.
