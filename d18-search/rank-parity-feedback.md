# Saturated rank intervals close two more D13 cover cases

**Result.** Complete two-layer cover cases1 and114 have independently
checked structural exclusions. The current curated D13 count is now
**6/117**:0,1,58,114,115,116. These two applications use small SAT solves;
they are not complete hand proofs of D13.

## The hand lemma

If k comparator layers remain, a cut wire can reach at most2^k outputs.
When its attainable rank interval has exactly2^k positions, its structural
forward cone is exactly that interval. Equality requires every stage to
expand fully. In particular, the final cone is a union of disjoint edges
of the final matching. Two such exact cones therefore have an even-sized
intersection.

For two remaining layers, intervals `[a,a+3]` and `[b,b+3]` cannot both
occur if `|a-b|` is1 or3. This is the same short parity argument that
finishes the [711 merger hand proof](merger711-hand-reduction.md).
It is valid at arbitrary ambient width and with any remaining depth k.

## Encoding the lemma

The existing endpoint model uses `L[c,j]` for `lo(c)>=j` and `U[c,j]`
for `hi(c)<j`. The strict upper inequality is the implemented convention;
the older helper's introductory docstring used an imprecise non-strict
notation. A window `[a,a+3]` is contained in the chosen interval exactly
when both `L[c,a+1]` and `U[c,a+3]` are false.

For distinct cut wires c,d and full windows with odd overlap, add

```
L[c,a+1] OR U[c,a+3] OR L[d,b+1] OR U[d,b+3].
```

Only starts whose windows contain the corresponding wire index are
needed. A standard comparison prefix fixes sorted inputs, so its true
rank interval contains that index. There are222 added clauses for n=13
and no extra variables. The endpoint intervals may overapproximate the
actual ones; every genuine completion remains feasible by choosing the
actual intervals. Thus these additional clauses are sound necessary
conditions for every continuation of the fixed prefix.

The [worker](d13_rank_parity_probe.py) otherwise uses the earlier complete
cut6 endpoint model, including every binary output of the fixed two-layer
prefix. It places no data-sorting constraints in the final two layers.
Both workers were externally limited to30 seconds; proof checking had
separate30-second limits.

## Controlled bounded comparison

Fresh baseline runs used the unchanged earlier worker, same solver,
prefix, relabelling, all wire bounds, and proof-recording mode. Direct CNF
comparison confirms that the **only difference is the222 added clauses**.
There is no variable or input-universe difference.

| D13 cover case | Old model, fresh run | With parity | Independent DRAT check |
|---|---|---:|---:|
|1|30-second timeout|20.03 seconds, UNSAT|15.89 seconds, verified|
|114|30-second timeout|13.15 seconds, UNSAT|9.89 seconds, verified|

The solve column includes model construction; full worker wall times
were20.10 and13.22 seconds. Each old worker was killed at its explicit
limit; no timeout is interpreted as UNSAT. These two bounded comparisons
demonstrate an improvement on these instances, not a general claim about
all D13 or D17 solves. The lemma transfers to D18, but no full D18 solve
speedup has been measured here.

The [comparison manifest](results/d13-rank-parity-comparison.json) records
sizes, timings and the exact CNF difference. The
[independent review](results/d13_feedback_round5-parity-review.json)
checks the literal semantics on19,666 endpoint assignments, source and
dependency hashes, CNF/proof hashes, solve termination and successful
checker logs. A separate known depth9 sorter passes the parity conditions
at cut7 and is verified on all8,192 binary inputs.

The reproducible [audit script](rank_parity_verify.py) checks5,554 pairs
of intervals containing their respective wire indices, the known-sorter
control, current dependency hashes, saved proof/checker artifacts, and the
exact222-clause differences. It invokes neither SAT nor a new proof-checker
run; its [report](results/d13-rank-parity-verification.json) states that scope.

The raw worker manifests preserve `independently_proof_checked:false`
because the external checker runs afterward. The companion
[case1 checker record](results/d13-rank-parity-r0001/check-terminal.json)
and [case114 checker record](results/d13-rank-parity-r0114/check-terminal.json)
provide the successful verification outcomes. The updated
[whole-cover audit](results/structural-cover-progress-round4.json)
uses those outcomes and keeps them separate from proof of the encoder
and the complete-cover theorem.
