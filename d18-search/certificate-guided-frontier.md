# Structural conditions that actually eliminate D(13) prefix cases

**Status, 2026-11-15:** six of117 complete-cover D13 cases are excluded
by structural conditions with independently checked DRAT certificates:
0,1,58,114,115,116. The latest [rank-parity clauses](rank-parity-feedback.md)
close cases1 and114 in20.03 and13.15 seconds. Their necessary conditions
have hand proofs; the whole-prefix applications still use SAT. The other
111 cases are not closed by this audit. D(18) remains open here.

Subsequent work supplies [small hand certificates for a specified D13
continuation](d13_hand_obstructions.md), three checked
[D17 defect exclusions](d17_feedback_results.md), and a
[twelve-wire obstruction that lifts to larger widths](fixed-sentinel-obstruction.md).
The later [D18 rank-interval trials](interval-frontier.md) remain inconclusive.

The [latest whole-cover audit](results/structural-cover-progress-round4.json) binds the results to the
complete thirteen-wire cover, whose SHA-256 is
`2e3dec7b0d501a15ed9871a024d647c89526945f3ad263d3360ce983279f8406`.
Everything in this note was done in the private `codex/d18-structural`
worktree; the shared main folder was not edited.

## 1. What the earlier 117 results meant

The earlier [profile audit](results/profile-frontier13/audit.json) contains
117 SAT relaxation witnesses, not 117 UNSAT certificates. Each witness gives
layers 3 and 4 compatible with the seven-real first-two-layer profile lemma
for every half-blind restriction of that prefix. Hence that screen eliminates
zero cases.

Adding every five-real placement that blinds layers 1 and 2 gives another
necessary condition: it cannot also blind both layers 3 and 4, since then
five wires would have only four layers left, contradicting D(5) >= 5.
This invalidates some of the saved witnesses, but a
[complete rerun](results/mixed-profile13-audit.json) again finds 117 survivors.
Thus rejecting a saved witness must not be counted as closing its prefix.
Including seven-real placements that do not blind the first two layers also
leaves cases 0 and 116 alive; see `results/all-profile13-r0000.json` and
`results/all-profile13-r0116.json`.

## 2. A hand-proved necessary condition: the rank-position relation

All indices below are zero-based. After a prefix of depth t, let

* P_t(k) be the set of wires that can hold rank k, over all permutations of
  the distinct ranks 0,...,n-1;
* Q_t(c) be the set of ranks that can be on wire c. Thus k is in Q_t(c)
  exactly when c is in P_t(k).

If a sorting completion has s layers, then

\[
|P_t(k)|\le 2^s\quad\hbox{and}\quad |Q_t(c)|\le 2^s.
\]

Indeed, every possible position of rank k must reach output k. Tracing that
output backward through s matching layers reaches at most 2^s wires.
Conversely, tracing a fixed wire forward reaches at most 2^s outputs, which
must include every rank that can be on that wire. These are simultaneous
bounds on the columns and rows of one incidence relation, not unrelated
one-rank optimization problems.

The relation can be computed exactly from binary probes. For each input x
and each zero coordinate i, compare the runs on x and x+e_i. Through a
comparator their states continue to differ on exactly one wire. If x has
n-1-k ones, the differing wire holds rank k in a permutation that assigns
rank k to i, the larger ranks to the ones of x, and the smaller ranks to
the other zeros. Conversely every permutation supplies such a threshold
pair for each rank. Thus the probe positions are exactly P_t(k).

The encoder enumerates all adjacent binary INPUT pairs, applies the fixed
two-layer prefix, and deduplicates the resulting pairs. It then simulates
four further arbitrary matching layers. It does not merely choose arbitrary
rank-position sets: their simultaneous realizability by a common prefix is
encoded exactly.

## 3. A stronger hand-proved condition: common ending matchings

Separate cardinality bounds discard which pairs of ranks must share a cone.
Let M and N be the penultimate and last matchings. For a set S, write
B_M(S) for S together with the partners under M of wires in S. Then

\[
P_t(k)\subseteq B_M(B_N(\{k\})) \qquad\text{for every }k
\]

when two layers remain. **The same M and N must work for every rank.**
This is just backward reachability through the two layers; it does not
assert how values compare in those layers.

For example, if N contains (k,k+1), both ranks share the same backward cone,
so

\[
|P_t(k)\cup P_t(k+1)|\le4.
\]

An output left idle by N has a cone of at most two wires. The two matching
choices must satisfy all these requirements together. The shared-routing
encoding also uses the established ending normal forms documented in
[netsat.py](netsat.py): adjacent last-layer comparators, penultimate length
at most three, and the corresponding implications for last-layer pairs.
These are necessary normal forms for a full sorter. Self-duality is never
imposed, and middle layers are not filled.

## 4. Cases actually excluded

| Cover case | Structural condition sufficient for refutation | SAT including build/export | Independent DRAT check |
|---|---|---:|---:|
| `n13-r0116` | At depth six, every rank has at most four positions and every wire has at most four possible ranks | 27.4 s | 19.4 s |
| `n13-r0000` | At depth six, all rank positions can route through a common pair of ending matchings in the valid normal form | 10.5 s | 10.3 s |

Case 0 is three four-wire diamond components plus an idle wire. Case 116
has component sentence `C1212, H012, S211212`. The
[cover](prefixes/complete13.jsonl) specifies their exact original layers.
The result JSON files below specify the deterministically relabelled
prefixes actually encoded. Relabelling and untangling preserve the
existence of a sorting completion; their permutations are recorded in the
corresponding exact-completion results.

* [Case 116 structural result](results/probe-frontier13-r0116-both-checked.json),
  [checker log](results/probe-frontier13-r0116-both-checked/check.log).
* [Case 0 structural result](results/probe-frontier13-r0000-route-checked.json),
  [checker log](results/probe-frontier13-r0000-route-checked/check.log).

Both runs encode data comparisons only through layer six. The final two
layers are represented by cone bounds or common reachability, not by a full
sorting simulation. Their UNSAT answers therefore establish actual
structural obstructions, and exclude the complete prefix cases.

The checker is [DRAT-trim](https://github.com/marijnheule/drat-trim), commit
`2e3b2dc0ecf938addbd779d42877b6ed69d9a985`. Each directory contains its CNF,
DRAT proof, core CNF and check log. The result files bind the CNF, proof,
encoder and checker executable by SHA-256. A checked CNF proof still relies
on the mathematical soundness of the encoding and normal-form reductions;
it is not a formally verified translation of sorting networks.

Separate full sorting encodings also refuted case 0 in 8.1 seconds and
case 116 in 7.0 seconds. Their checked traces are in
`results/complete13-r0000-drat/` and `results/complete13-r0116-drat/`.
These exact results were used as benchmarks, not as premises for the
structural refutations.

## 5. What certificate minimization already tells us

The raw exact case-0 certificate uses clauses from 414 of 418 binary inputs.
It does not directly resemble a short human argument. This is why raw
proof length or an arbitrary learned clause is a poor guide by itself.

The structural case-116 core is more interpretable. Only these degree
bounds are used:

\[
|P_6(k)|\le4\quad(3\le k\le10),\qquad
|Q_6(c)|\le4\quad(2\le c\le11).
\]

All other degree-bound clauses were removed. The trimmed proof was then
checked again against that reduced formula, not merely inspected for
unused variables. See the [reduced-certificate manifest](results/probe-frontier13-r0116-both-checked/central-bounds.json)
and [check log](results/probe-frontier13-r0116-both-checked/central-bounds-check.log).
The wire indices here refer to the relabelled prefix in the case-116 result.

This gives a concrete hand-proof target: for that prefix, after any four
further matching layers, some rank 3 through 10 has at least five possible
positions, or some wire 2 through 11 can hold at least five ranks.
The nonredundancy restrictions do not weaken this statement: a comparator
that never swaps on the full prefix image can be removed without changing
the rank-position relation or adding a layer.
The finite proof of this target is currently SAT-based. No short invariant
proving it by hand has yet been extracted.

## 6. Controls, failed trials, and the next mathematical target

A depth-nine sorter extending case 116 was found and checked on all 8192
binary inputs. Fixing the probe model to that sorter at the cut after layer
seven passes both degree bounds and common-ending routing. The
[positive-control record](results/probe-frontier13-d9-positive.json) includes
the directly replayed probe supports and ending matchings.

Other bounded experiments are terminal and inconclusive:

* Rank bounds alone for case 0: 120-second timeout.
* Full eight-layer sentinel-profile CEGAR for case 0, with hand bounds for
  retained sizes 5, 7 and 9: 120-second timeout after adding 169 restrictions.
  No semantic UNSAT core was obtained. Its profile predicate was separately
  checked on all 72,097 length-eight count profiles for retained sizes 5/7.
* Keeping only the central eight binary weight levels in the exact case-0
  formula is independently UNSAT, but still uses 390 inputs and is not a
  useful small hand certificate.

The productive direction is to constrain the common rank-position relation
and its compatible ending matchings. A prospective lemma should first be
tested as a relaxation over **all** continuations of a named complete-cover
case. Only an UNSAT result closes that case; rejecting selected continuations
does not. Then group the constraints by ranks, wires, probe families or
ending blocks, and minimize those mathematical premises before attempting
a hand proof.

For a hypothetical depth-ten eighteen-wire sorter, use the cut after layer
eight: exactly the same degree-four and common-ending conditions apply.
For other n and candidate depths d, use the cut at d-2. Their general
validity is immediate from the lemmas above; their ability to eliminate
any D(18) or larger complete-cover case is still unproved here. All 411
D(18) complete-cover cases remain unclosed.

## 7. Reproduction

Use the Python environment with `python-sat`, and a compiled DRAT-trim:

```sh
python d18-search/probe_frontier.py \
  --result d18-search/results/complete13-d8-single-structural/n13-r0116/result.json \
  --out /private/tmp/probe116-check.json --both --checker /path/to/drat-trim

python d18-search/probe_frontier.py \
  --result d18-search/results/complete13-d8-single-structural/n13-r0000/result.json \
  --out /private/tmp/probe000-check.json --both --route --checker /path/to/drat-trim
```

The recorded `probe_frontier.py` source digest is
`e07f9183616412db41b7093fbb86efe8a13acf00d413b88084454b73ccdbeef0`.
The checked results are complete artifacts; no background solve is needed
to interpret them.

## 8. Subsequent reductions and D18 transfer tests

The [wire-only case-116 reduction](d13_hand_next_wire_core.md) removes all
rank-position bounds and all ending routing. Only wire intervals of width
at most four on wires 2 through 11 remain. This whole-prefix condition is
independently UNSAT: 19.79 seconds for building/solving/exporting and 13.69
seconds for DRAT checking, versus the earlier 27.41 and 19.36 seconds.
These are recorded runs, not a controlled performance benchmark. The
stronger result is the reduction of the mathematical premises. No new
member of the 117-case cover is closed.

The [D17 defect encoder](d17_feedback_results.md) turns the three earlier
timed-out profile cases into 7--14-second refutations, followed by 5--11
seconds of independent checking. The reduced case-607 obstruction takes
2.11+1.30 seconds by SAT/checking and now has a complete hand proof.
These are specific structural problems; they are not measured speedups
for a full rerun of the complete D13 or D17 sorting searches.

The [signed-fork theorem](d12_triangle_lemmas_width.md) is valid at larger
widths. Its exact pattern, however, appeared in none of 160 sampled D18
four-layer prefixes. Of these, 155 have no seven-real fully blind
restriction at all; the other five have at most two cut states, and none
has an eight-real one. The [recognizer](signed_fork_prefix.py) recovers
the known D17 case-607 family and passes independent small exhaustive,
arbitrary-embedding and all-B-sign controls. This negative D18 audit is
about samples, not a complete cover.

Allowing early retained comparisons and compressing repeated pairs is
more productive. A [four-restriction hand proof](commuting-prefix-hand-proof.md)
excludes every depth-ten completion of one specified five-layer prefix.
Two [additional hand certificates](commuting-prefix-additional-proofs.md)
exclude specified six-layer prefixes. They do not close whole cases of
the two-layer cover.

A [normalized depth-two screen](d18_hand_next_reschedule.md) requires only
one unknown matching after a fixed five-layer prefix. Four bounded tests
finished in about 0.06--0.14 seconds of worker time: the already hand-excluded
combined prefix is UNSAT with checked certificates; three beam prefixes
have directly replayed survivors. This demonstrates that these local
structural checks are fast on D18, while also showing that they are not
yet sufficient. The larger cut-eight interval trials remain inconclusive.

All these runs are terminal. D18 still has zero closed complete two-layer
cover cases. The next encoding question is whether interval bounds can
be imposed incrementally using only two-run witnesses from candidate
wide wires, avoiding the full initial binary-input simulation. That is
a proposed experiment, not an established speedup or proof result.

**Follow-up:** the [incremental two-run experiment](endpoint-cegar.md)
has now been implemented and checked on small positive and negative
controls. The whole-prefix D13 and D18 trials both reached their
60-second caps; the pair-only D13 variant also remained inconclusive.
The smaller initial formulas did not deliver a speedup. These trials
close no additional cover case.

## 9. Two additional whole-case wire obstructions

The [second-round wire-only tests](d13_feedback_round2.md) add complete
D13 cover cases58 and115. Case115 remains independently UNSAT when only
the six cut-six wire bounds on wires4 through9 are kept: 32.50 seconds
for build/solve/export and20.40 seconds for checking. Case58 uses all
thirteen wire bounds and takes23.83+17.77 seconds. Neither statement uses
rank-support cardinalities, shared ending routing, or sorting constraints
in the final two layers. These are SAT-assisted universal statements over
every four-layer continuation of the specified relabelled two-layer prefix.

At the end of round two, structural coverage was **4/117** for D13:
cases0,58,115,116. The later rank-parity update below raises it to6/117.
The [curated artifact audit](results/structural-cover-progress-round2.json)
checks saved CNF/proof hashes and independent checker logs, and records
the unchanged **3/609** D17 and **0/411** D18 complete-cover counts.
It is not a formal verification of the encoders or prefix-cover theorem.
The two other sampled D13 cases,1 and114, reached their30-second caps;
neither is ruled out by this experiment.

## 10. Further seven/eight-real targets for D18

The [common-real padding transfer](d17_feedback_round2_normalization.md#6-padding-gives-seveneight-real-obstructions-without-h9)
turns the twenty-state case606 and608 obstructions into seven- and
eight-real versions. Removing two always-real coordinates yields the
seven-real family: any two-matching peak-three cover could be padded
by one disjoint common-real comparator in both layers, contradicting
the pure fourteen-wire peak-four obstruction. Removing one always-real
coordinate yields the eight-real family by padding with an idle wire.

A fresh unrestricted case606 certificate supplies the required pure
premise, independently checked in6.89+5.08 seconds. The older case606
normal-form certificate alone would not justify padding by a repeated
comparator. Case608 already had a pure checked certificate.

These four projected families give additional conditional obstructions
after four blinded layers of a hypothetical depth-ten eighteen-wire
sorter. They use the hand H7/H8 profile lemmas and retain the small pure
SAT certificate as a premise. No prefix has yet been shown to realize
one of these additional families, and the D18 complete-cover count
remains zero.

## 11. Hand merger theorems and a component condition at every width

Three hand merger lower bounds now apply to block sizes (4,3,2),
(3,3,3), and (4,4,1): each needs at least five layers. They imply the
[nine-real component condition](merge-component-obstruction.md): in
every signed-sentinel restriction leaving nine arbitrary reals, the
interaction graph before the last four layers has a component of size
at least five. No sorting inside the components is assumed, and no SAT
answer is a premise. This gives constraints on cut4 for D13, cut6 for
D18, and the analogous cut at arbitrary larger widths.

The (4,3,2) theorem also completes the `03 12 46` H9 class by hand,
raising H9 coverage to26/50. The initial component tests leave all six
sampled D18 six-layer prefixes possible; no complete D18 cover case is
closed by this test. The mathematical statement and its finite sample
coverage are kept separate in the linked note.

## 12. A stronger component count and two additional six-layer exclusions

The [three-component theorem](three-component-obstruction.md) strengthens
the previous size condition: every nine-real restriction has at most two
interaction components before the final four layers. Five three-block
merger shapes had hand proofs at the start of this round;711 and621 now
also have hand proofs based on rank intervals and saturated-cone parity.
The tiny SAT certificates are corroboration only. The theorem applies at
arbitrary ambient width.

It excludes the saved sixth-layer continuations of beam00 and beam16,
and recovers the already known exclusion of the combined candidate.
Other sixth matchings survive the condition, so no five-layer beam prefix
or complete two-layer D18 case is declared closed. For D13 the screen
rejects83 of117 saved witnesses, not their entire cover cases.

The [D17 critical-edge hand argument](d17_feedback_round3_hand.md) has
also completed [independent review](d17_feedback_round3_review.md). It
excludes every first matching with that edge and at most one cross gate,
at arbitrary even active width. The reviewed [two-cross extension](d17_feedback_round4_hand.md)
also excludes all perfect first matchings with that edge and exactly two
cross gates. The full case606 hand proof remains open.


## 13. Saturated-cone parity yields two whole-case D13 exclusions

Two exact four-position forward cones must intersect in an even number
of ranks: both are unions of edges of the same final matching. Adding222
endpoint clauses expressing this hand lemma closes cases1 and114. Their
independent checks take15.89 and9.89 seconds after solves of20.03 and13.15
seconds; fresh baseline runs both time out at30 seconds. The
[comparison and derivation](rank-parity-feedback.md) records the precise
scope. This raises the curated structural count to6/117; D17 remains
3/609 and D18 remains0/411 complete cover cases.

The same rank-endpoint method also finishes the H9 class `02 16 37`
entirely by hand. Its [proof and tables](../depth-hand-proofs/h9_feedback_round4_021637.md)
have completed root review and fixed-certificate replay, raising H9
hand coverage to27/50. Fourteen explicit real inputs supply the final
160 endpoint exclusions; no solver answer is a premise.

The later [D17 critical-perfect reduction](d17_feedback_round5_reduction.md)
has completed independent root review. Its contraction lemmas and
finite certificate cover all remaining perfect matchings with the
critical edge at arbitrary even width; the finite verification remains
a premise. This is not counted as a new complete-cover exclusion or as a
completed full case606 hand proof.


## 14. Round-six checkpoint

[Cases2,57,113](d13_feedback_round6.md) add three checked D13 exclusions,
raising the current complete-cover count to **9/117**. The new
[shared-middle-pair lemma](d13_feedback_round6_middle_pair.md) is a separate
hand structural result. D17 remains3/609 and D18 remains0/411.

The [critical two-idle D17 extension](d17_feedback_round6_reduction.md)
has passed [independent review](results/d17-hand-round6-review.json).
Its 1,584-case finite certificate remains a premise; the noncritical mixed
branch is still open. The review records one nonfatal prose correction.

For D18, [explicit rank-endpoint certificates](rank-layer-round6-hand-tables.md)
exclude three concrete six-layer prefixes. The saved
`prefix-rank-round6-cut8-*` and `prefix-rank-round6-only-*` results exclude
all continuations of three concrete five-layer prefixes with independently
checked SAT proofs. Each solve and check takes less than one second.
The four-layer tests, including the stronger middle-pair condition, reach
30-second limits. These are partial-prefix results and do not increase
the complete-cover count. The [checkpoint](../CHECKPOINT.md) identifies
current review status, artifact conventions, and unfinished work.
