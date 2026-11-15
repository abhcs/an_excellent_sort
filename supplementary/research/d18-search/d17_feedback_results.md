# Three D17 prefix cases excluded by their first two retained layers

**Status, 2026-11-15.** This audit excludes complete-cover cases
`n17-r0606`, `n17-r0607`, and `n17-r0608` from a hypothetical depth-nine
seventeen-wire sorter. All three UNSAT certificates were independently
checked with DRAT-trim. The screen uses only sentinel transport through
layer 3 and retained-comparator counts in layers 3 and 4. It does not
encode a sorting suffix. It relies on the established, computer-assisted
H9 theorem; it is not a new hand proof of H9 or of D(17) >= 10.

The complete cover has 609 cases, SHA-256
`711b620bb298deee98e5520595cfb341a13cf3600f4297dd35f3b38cb11d2100`.
This audit leaves 606 cases unexcluded. Case 0 explicitly survives the
screen, so this condition does not settle the complete cover by itself.

## 1. The one-unpaired-real identity

For a matching M and a real-position set R, let e_M(R) be the number of
matching edges with both endpoints in R. Let q_M(R) count the real wires
that are idle or paired with a sentinel. Every real wire is in exactly
one of these categories, so

\[
|R|=2e_M(R)+q_M(R).
\]

For nine reals, four retained comparators are therefore equivalent to
exactly one such unpaired real. Equivalently, it suffices to impose
q_M(R) <= 1: its odd parity supplies equality.

Every half-blind restriction in these cases leaves nine reals and blinds
the first two layers. A depth-nine sorter would leave a depth-seven
nine-wire sorter. D(9) >= 7 requires both of its first two layers to be
nonempty; H9 requires at least one of them to have four comparators.

The previous encoder expressed the H9 choice through guarded cardinality
predicates on retained gates. The new encoder, `d17_feedback_defects.py`,
uses the identity above. This is the same necessary mathematical
condition, with a smaller encoding, not a stronger premise about H9.

## 2. Encoding and normal forms

The fixed first two layers come directly from the named cover case.
Layers 3 and 4 are arbitrary matchings. They are not filled or required to
be self-dual. A gate repeated immediately from the preceding layer is
excluded: removing such a redundant comparator preserves every sorter.

Each restriction has two threshold bits for every wire:
-infinity=(0,0), real=(1,0), +infinity=(1,1). Both threshold bits propagate
through layer 3 using exact AND/OR comparator equations. Matching and
idle-wire equations determine every output type exactly.

A restriction chooses layer 3 or layer 4 as its four-gate layer. In that
layer, at most one wire may be a real that is idle or paired with a
sentinel. The first retained layer is required to be nonempty. The second
nonemptiness condition is added only if a SAT candidate violates it.
All three refutations finish before that refinement: they are UNSAT even
with second-layer nonemptiness omitted. This omission strengthens the
scope of the obstruction; it does not introduce a premise.

The translation is mathematically justified but not formally verified.
A DRAT check establishes unsatisfiability of the exported CNF; it does
not independently establish the correctness of its sorting-network
interpretation.

## 3. Checked results

| Case | Component sentence | SAT including build/export | DRAT check |
|---|---|---:|---:|
| 606 | H012, S211212, S21121212 | 14.17 s | 10.93 s |
| 607 | H012, S211212, S21122112 | 10.76 s | 7.48 s |
| 608 | H012, S211212, S21211212 | 6.83 s | 4.94 s |

Each case has 20 restrictions and 2,666 variables. The respective clause
counts are 28,764, 28,708, and 28,772. The result directories are
`results/d17-feedback-defects-r0606/`, `...r0607/`, and `...r0608/`.
Each contains a result, a terminal wall-limit record, and a certificate
directory with the CNF, DRAT proof, core, and checker log. The manifest
`results/d17-feedback-audit.json` binds the relevant source and artifacts.

The checker executable has SHA-256
`86a8209e667de72bc68ba43575faff85ecdfc2afa45d14d04cfd57df0d701e1d`.
Each solve and certificate operation had a 120-second external wall
limit. Every process in this audit is terminal.

The positive control `results/d17-feedback-defects-r0000/result.json`
contains a directly replayed matching pair with retained profile (1,4)
for its sole half-blind restriction. It is a relaxation witness, not a
sorting network.

## 4. A smaller, independently checked case-608 core

Selector assumptions grouped the clauses by restriction. Greedy deletion
removed restriction indices 0, 1, and 3. The remaining set is

```
2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19.
```

Removing any further single group makes that relaxation SAT. This is
deletion-minimal, not a proof that 17 is the globally smallest core.
The UNSAT formula was rebuilt with the other three groups absent,
re-solved, and independently checked again. It has 25,134 clauses; solve
and check took 10.92 and 8.55 seconds. See
`results/d17-feedback-core-r0608/reduced-certificate/certificate.json`.

The case-608 real sets factor as a four-by-five family. Each is
{1,2} union A_i union B_j, with row-major index 5i+j:

| i | A_i | j | B_j |
|---:|---|---:|---|
| 0 | {4,7,8} | 0 | {10,12,15,16} |
| 1 | {4,5,8} | 1 | {10,12,13,16} |
| 2 | {4,5,6} | 2 | {10,12,13,14} |
| 3 | {5,7,8} | 3 | {10,13,15,16} |
| | | 4 | {9,13,15,16} |

Wires 0, 3 and 11 are never real at this cut. Full signed states, which
are needed for transport through layer 3, are in
`results/d17-feedback-peaks/result.json`.

## 5. Two hand lemmas suggested by the feedback

**Shared gates.** Let R and S be nine-element real sets, with
d=9-|R intersect S|. If one matching retains four gates in both, their
retained gate sets share at least ceil((7-d)/2) gates.

*Proof.* If h gates are shared, their union consists of 8-h matching
edges, all within R union S, whose size is 9+d. Thus
2(8-h) <= 9+d. In particular, distance one or two forces at least three
shared gates. This bound remains available after common comparator
layers because normalized sentinel real-set distance never increases,
as proved in `sentinel-coupling-proofs.md`.

For distance one there are only two configurations: four common gates
pair the eight common reals, or three common gates pair six common
reals and the two exclusive reals are matched to different remaining
common reals. This gives a concrete local classification for a hand
argument on the four-by-five family.

**Common-pair compression for static counts.** If two wires u,v are real
in every member of a family, a matching can be changed to include (u,v)
without reducing its retained count in any member. If u and v originally
have distinct partners a,b, replace (u,a),(v,b) by (u,v),(a,b). The old
contribution is 1_R(a)+1_R(b); the new is 1+1_R(a)1_R(b), which is at least
as large. The idle cases follow by the same count.

This is a static counting lemma. It cannot be imposed as a normal form
on layer 3 of the two-layer problem, because changing comparators also
changes sentinel transport and which gates layer 4 may repeat.

Applying compression to {1,2}, deleting never-real wires, and filling
unused vertices reduces a static maximum to the 10,395 perfect matchings
on the remaining twelve wires. The exact maximum number of restrictions
with four retained gates is 11. The maxima with respectively one, three,
or five A-B cross edges are 11, 11, and 9. The direct enumeration is
`d17_feedback_static.py`, with data in
`results/d17-feedback-peaks/combinatorial-audit.json`.

Thus at least nine of the twenty restrictions must obtain their H9 peak
from layer 4. The checked two-layer obstruction says that no common
transporting layer 3 and following matching can accomplish that. A short
proof should combine the shared-gate classification with the signed
four-by-five family, rather than repeat the large CNF argument.

## 6. Negative evidence kept separate

The fresh all-rank cut-seven routing probe for case 608 reached its
120-second wall limit without SAT or UNSAT. Its terminal record is
`results/d17-feedback-r0608-cut7-resumed/terminal.json`. The earlier run
in `results/d17-feedback-r0608-cut7/` was stopped on the user's pause;
it is neither a timeout nor an UNSAT result.

The static 11-peak witness alone does not close a prefix. Its particular
first matching cannot serve the remaining nine restrictions in a second
matching, but rejecting that chosen continuation is weaker than the
universal two-layer refutations above.

The 17-restriction core is still too large to call a short hand proof.
The successful result is a reusable encoding of an elementary defect
identity plus three independently checked structural exclusions. The
full D17 lower-bound problem remains open in this audit.

## 7. Stronger case-608 statement: pure two-matching coverage

The original case-608 formula was weakened twice. First, all 136 clauses
forbidding a repeated L3/L4 gate were deleted. This remained UNSAT
(8.08 seconds) and its proof was independently checked (6.34 seconds).
Next, all 20 clauses requiring a nonempty first retained layer and all
six units forbidding L2/L3 gate repeats were deleted. This too remained
UNSAT (7.69 seconds), independently checked in 5.88 seconds.

Consequently the following finite structural theorem has a checked SAT
proof, with no nonemptiness or nonrepetition premises:

> Let F be the twenty signed states of case 608 after layer 2. For every
> pair of arbitrary matching layers M,N on the seventeen wires, there
> exists s in F such that M retains at most three real-real gates on s
> and N retains at most three on the signed state obtained from s by M.

The formula is just exact ternary transport and the negation of this
statement. Repeated gates and empty retained layers are allowed. The
certificate is in `results/d17-feedback-peak-only-r0608/result/`, with
its checker manifest in `result/check/certificate.json`. The script
`d17_feedback_peak_only.py` records exactly which clauses were removed.
This stronger statement has only been checked for case 608; the sister
case results retain their original stated scope.

This is the cleanest hand-proof target produced by the audit. H9 then
converts the resulting thin/thin restriction into exclusion of a
depth-nine completion. The 17-state deletion-minimal core above was
computed for the original formula and is not asserted to remain UNSAT
under this further weakening.

The subsequent [fixed-sentinel pruning argument](fixed-sentinel-obstruction.md)
reduces the pure case-608 pattern to fourteen wires and the pure case-607
pattern to twelve. Both smaller formulas have direct checked certificates.
The hand pruning lemma lifts either obstruction to any larger width with
common fixed auxiliary sentinels.

## 8. Case 607: four-restriction hand certificates

The twelve-wire obstruction now has a complete finite proof without SAT.
For each of the 140,152 possible first matchings, exact transport exposes
four sentinel triples of one of [four forbidden types](d12_triangle_lemmas.md).
Vertex prices with total at most 7/2 prove that no following matching can
hit all four triples. The three-second [audit](results/d12-triangle-proof-audit.json)
checks the exhaustive scan and independent price/isomorphism certificates.

This replaces the two-matching SAT search for this pattern with a small
finite selection of four restrictions and hand proofs at the leaves.
The [no-cross argument](d17_hand_defects_twelve.md) and
[safe-image arguments](d17_hand_defects_twelve_cross.md) additionally prove
large branches by hand. The [general four-triple criterion](d12_triangle_lemmas_complete.md)
does not depend on the scan and applies to arbitrary triple families.

**Subsequent complete hand proof.** The [four-gate and perfect
cases](d17_feedback_twelve_structure.md) and the [five-gate
case](d17_hand_defects_twelve_five.md), together with the small-matching
argument, now eliminate every first-matching size symbolically.
The twelve-wire structural theorem therefore no longer depends on either
the SAT proof or the 140,152-matching enumeration. Those computations
remain independent corroboration. The proof also allows arbitrary fixed
signs on its five B coordinates.

The [general width theorem](d12_triangle_lemmas_width.md) goes further:
the same obstruction holds for every R>=7 real coordinates, with any
number of common reals and common fixed sentinels. Its R=7 and R=8
applications invoke the fully hand-proved early-profile lemmas, giving
a new target after three blinded prefix layers for D(17), or four for
D(18). Existence of the needed family in every relevant prefix is not
established.

Case 607's implication for sorting networks still invokes H9, whose
current proof is computer-assisted. Neither the finite proof nor the
complete hand proof of this pattern closes additional members of the 609-case
cover. The full D(17) hand-proof goal and the D(18) lower bound remain open.

The subsequent [fourteen-wire B-family lemmas](d17_feedback_fourteen_hand_Blemma.md)
classify the five-column demand in cases 606 and 608. In case 606 they
single out the critical original edge (10,13): without it, any A row
requiring second-layer peaks in all five columns forces its A sentinel
pair into that layer. Several branches follow by hand, but the critical
edge and partially covered rows remain. The four-by-four fork-product
subfamilies have directly replayed SAT witnesses, showing why the fifth
column cannot simply be omitted. Full hand closure of 606/608 is not
claimed.

The [second-round hand reductions](d17_feedback_round2_normalization.md)
prove that a hypothetical case606 peak cover can be normalized to a
perfect first matching or one with exactly two idle wires. The proof
uses the width-four order on the signed coordinate types. A new
incident-row lemma handles the previously exceptional B edge by showing
that its ordinary and exceptional matching cores are incompatible on
two incident rows. This excludes every perfect first matching without
A--B gates, and the corresponding two-idle branch when both idles are
in one block. These reductions hold at every even width n>=12 with
additional common reals; mixed and partially required rows remain open.
