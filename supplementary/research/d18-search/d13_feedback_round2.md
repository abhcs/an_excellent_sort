# Two new whole-prefix D13 obstructions

**Result.** The complete-cover cases `n13-r0058` and `n13-r0115` are excluded
by cut-six wire-interval bounds alone, with independently checked DRAT
certificates. The strongest checked reduction for case115 uses just **six
wires, 4 through 9**, in its explicitly relabelled prefix below. No
rank-position cardinality bounds, common ending routing, or data comparisons
in the ending are premises. The applications remain SAT-based; these are
new whole-case closures and a smaller hand-proof target, not hand proofs of
those targets or of the full D13 lower bound.

The original cover case has component sentence `H012, S2121121212` and
720 binary prefix outputs:

```
L1 = (0,1)(3,4)(5,6)(7,8)(9,10)(11,12)
L2 = (0,2)(3,6)(5,7)(8,9)(10,11)
```

The deterministic relabelling and untangling used by the encoder gives:

```
L1 = (0,12)(1,5)(2,7)(3,11)(4,8)(9,10)
L2 = (0,9)(1,6)(2,10)(3,12)(4,11)
```

The input and output permutations are recorded in every result file. Their
image-set identity is checked directly before encoding, and the complete
cover is bound by SHA-256
`2e3dec7b0d501a15ed9871a024d647c89526945f3ad263d3360ce983279f8406`.

## Exact statement and a two-run formulation

For **every** four further matching layers on this relabelled prefix, some
wire `c` in `{4,5,6,7,8,9}` has at least five attainable ranks after layer six:

```
there exists c in {4,5,6,7,8,9} with |Q6(c)| >= 5.
```

Any two remaining matching layers can carry one wire to at most four final
positions. Hence the displayed statement excludes every depth-eight
completion of this whole cover case.

Using the already established attainable-rank interval lemma, define
`tau0(c)` as the minimum number of input zeros on a binary run whose output
at wire `c` is zero, and `tau1(c)` as the minimum number of input ones on a
run whose output there is one. The established endpoint identity is

```
|Q6(c)| = 15 - tau0(c) - tau1(c).
```

The hand-proof target therefore has this small semantic witness form:
after every four-layer continuation, one of those six wires has a zero
output on an input with `a` zeros and a one output on another input with
`b` ones, where `a+b <= 10`. Equivalently, the zero-output run has at least
three more input ones than the one-output run. This is a restatement using
the existing interval lemma, not a novelty claim for the endpoint identity.

## Checked reductions

| Bounded wires in the relabelled prefix | Result | Build, solve and export | Independent check |
|---|---|---:|---:|
| all thirteen wires | UNSAT | 22.86 s | 15.23 s |
| 2 through 11 | UNSAT, unused bound units removed | proof reused | 15.26 s |
| 3 through 10 | UNSAT | 29.50 s | 17.08 s |
| **4 through 9** | **UNSAT** | **32.50 s** | **20.40 s** |

The six-wire formula has 23,459 variables and 341,305 clauses. All six
bound-unit clauses occur in its trimmed proof. **Deletion-minimality is not
claimed**: no further bound-deletion tests were performed after this result.

The [encoder](d13_feedback_round2.py) simulates all 720 fixed-prefix binary
states through four arbitrary further matching layers. It constrains an
interval overapproximation for each cut wire and bounds the widths of only
the selected wires. The interval variables are linked to all simulated
binary states; they cannot be chosen independently of one common network.
The known sorted-input condition is included. Safe redundant-comparator
deletion is the only prefix simplification; it leaves the cut function and
rank intervals unchanged. Middle layers are not filled and self-duality is
not assumed. Unused ending-layer variables can all be false in wire-only
mode and impose no ending-routing requirement.

The original all-wire certificate was trimmed and explicitly weakened by
removing the unused bound units for wires0,1,12. The weakened CNF was checked
again against the trimmed proof by
[d13_feedback_round2_trim.py](d13_feedback_round2_trim.py), rather than
inferring satisfiability status from a list of unused proof clauses. The
eight- and six-wire formulas were rebuilt and solved independently.

The strongest [result manifest](results/d13_feedback_round2-r0115-wire-central6.json)
binds the source, dependencies, cover, CNF, proof, and checker executable.
Its [checker log](results/d13_feedback_round2-r0115-wire-central6/check.log)
contains `s VERIFIED`. The companion
[terminal record](results/d13_feedback_round2-r0115-wire-central6-terminal.json)
and checker terminal record show normal exits under hard sixty-second caps.

## Representative coverage batch

After the case115 reductions, a separate
[bounded driver](d13_feedback_round2_batch.py) tests the previously unclosed
cover cases1,58,114 using all thirteen wire bounds and no rank or ending
constraints. Each solver subprocess has a hard thirty-second cap. Its
[audit](results/d13_feedback_round2-batch-audit.json) records explicit
terminal statuses:

| Cover case | Wire-only result | Worker time / cap | Independent check |
|---|---|---:|---:|
| `n13-r0001` | TIMEOUT, killed; inconclusive | 30 s / 30 s | none |
| **`n13-r0058`** | **UNSAT** | **23.83 s / 30 s** | **17.77 s, VERIFIED** |
| `n13-r0114` | TIMEOUT, killed; inconclusive | 30 s / 30 s | none |

Case58 has component sentence `C12121221, H01221` and 611 binary prefix
outputs, so this new closure is from a different component family than
case115. Its encoded relabelled prefix is

```
L1 = (0,9)(1,6)(2,10)(3,4)(5,12)(8,11)
L2 = (0,8)(1,7)(2,9)(3,10)(4,11)(6,12)
```

Every four-layer continuation leaves some wire with at least five attainable
ranks. The checked formula uses all thirteen width-four bounds and has
18,745 variables and 255,708 clauses. Its
[result manifest](results/d13_feedback_round2-r0058-wire.json) records the
original cover member, both relabelling permutations, dependency hashes,
CNF/proof hashes and the successful checker result. The
[checker log](results/d13_feedback_round2-r0058-wire/check.log) supplies the
independent verification. No semantic bound-deletion rerun was performed
for this case.

A timeout is inconclusive and is never an UNSAT result. The batch is a
small sample and cannot establish a property of all 117 cases. All solver
and checker processes in the round have terminated; the two capped workers
were killed by their external timeout controls.

No aggregate cover audit was modified by these files. This round adds
cases58 and115 to the previously checked cases0 and116, subject to the exact
case-specific scope and statuses above. The wire-only condition now has
checked examples in several component families; whether it refutes every
complete-cover case remains unanswered.
