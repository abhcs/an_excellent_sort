# Seven supported D17 cover exclusions, with two short residual lemmas

The recovered necessary condition closes complete D17 prefix cases
482 and 603. Together with the retained cases 604 through 608, this
restores **7 of 609** supported complete-cover exclusions. It does not
complete a hand or computer-assisted proof of the whole D17 cover.

For every signed restriction blinding the first two layers and leaving
nine independent real inputs in a hypothetical depth-nine sorter,
the next two retained layer counts must be one of

    (3,4), (4,3), (4,4).

The [first-layer bound](d17_feedback_round10_order.md) uses H9 and an
exact N-shaped four-wire image rescheduling. The reconstructed
[second-layer bound](d17_second_recovery_order.md) reduces by hand to
two four-wire product images, UU and UD, plus a singleton. Their
five-layer completion problems have checked UNSAT certificates:

| Nine-wire residual | Solve process | Independent check |
|---|---:|---:|
| UU | 0.345 s | 0.427 s |
| UD | 0.228 s | 0.163 s |

The universal statement retains **full computer-assisted H9** and the
established ending normal form as explicit premises. The two residuals
do not stand in for a full hand proof of H9. Their fresh CNFs and proofs
reproduce the historical hashes, and the
[replay checker](results/d17-second-recovery-check.json) binds all
sources and artifacts.

## Complete fixed-prefix applications

The new [encoder](d17_both_three_recovery_profile.py) propagates signed
types through an arbitrary common physical third matching. For each
fourth-layer edge it forms the exact conjunction of the selected gate
and its two transported real markers. A cardinality constraint requires
at least three such edges. The existing first-layer-three and H9
peak-four constraints remain in force.

Immediately repeated physical comparators may be deleted while keeping
the cover prefix fixed. This justifies the inherited no-repeat clauses.
No saturation, self-duality, ending adjacency or lexicographic condition
is imposed on these unknown third and fourth layers.

| Complete cover case | Variables | Clauses | Solve process | DRAT check |
|---|---:|---:|---:|---:|
| 482 | 12,338 | 46,034 | 25.71 s | 21.58 s |
| 603 | 12,338 | 46,017 | 12.91 s | 9.87 s |

Every solve and check had its own sixty-second hard limit; all finished.
Both refutations occurred in the first iteration, so the inherited lazy
nonemptiness branch adds no premise. The
[batch record](results/d17-both-three-recovery-batch.json) retains the
terminal process records and exact CNF/proof hashes.

The [independent review](results/d17-both-three-recovery-review.json)
checks the whole-case implication, reconstructs both CNFs byte for byte,
and binds their independently checked certificates. It also checks the
local Boolean/cardinality constraints and 98,304 signed binary transport
runs. The logical claim is that **any** sorting continuation of either
fixed cover prefix would supply a satisfying assignment. Checked UNSAT
therefore excludes all its continuations, rather than one chosen model.

## The count bounds are sharp

Actual seven-layer nine-wire sorters exist with both (3,4) and (4,3)
first-two counts. The [positive controls](results/nine-profile-sharpness-recovery.json)
were found in 0.36 and 0.55 seconds including process startup. Each
complete network was independently simulated on all 512 binary inputs.
Thus neither layer can universally be required to have four gates, and
a proposed first-two sum bound of eight is false. Further progress needs
structural information beyond these two counts.

## Scope for larger widths

The nine-wire statement applies to genuine nine-real restrictions inside
any ambient network when seven layers remain. It does not automatically
give the same constraint after two blind layers on eighteen wires:
a hypothetical depth-ten eighteen-wire sorter has **eight** layers
remaining there. Deleting an additional empty retained layer can make
the theorem applicable, but that emptiness must be proved for the
particular restriction.

D18 remains at zero complete two-layer cover exclusions. No full D18
SAT verification was run as part of this reconstruction.
