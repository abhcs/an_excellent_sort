# Three further D13 cover cases closed by interval parity

The unchanged, reviewed `d13_rank_parity_probe.py` worker excludes complete
two-layer cases2,57,113. Each result is UNSAT with an independently verified
DRAT certificate. These are three new whole-case exclusions, rather than
rejections of particular third/fourth layers.

The encoded necessary conditions concern all four-layer continuations to
cut6: every wire's attainable rank interval has width at most four, and
two full four-rank intervals cannot intersect in an odd number of ranks.
The two layers after the cut contain no simulated data comparisons. The
applications remain computational; no hand proof of an entire D13 case
is claimed.

| Case | Two-layer prefix image size | Worker wall seconds | DRAT seconds |
|---:|---:|---:|---:|
| 2 | 468 | 20.11 | 19.06 |
| 57 | 611 | 10.74 | 8.18 |
| 113 | 720 | 13.73 | 9.82 |

Every solver worker and checker had a separate30-second external cap.
All six subprocesses exited0. No timeout is classified as UNSAT.

Cases2,57,113 were selected as close structural neighbors of the earlier
closed cases1,58,114, respectively; this was a three-case study, not a scan
of the complete117-case cover.

## What the proof traces reveal

The DRAT tracer retained the following semantic clauses:

| Case | Retained wire-bound units | Used parity clauses, out of222 |
|---:|---|---:|
| 2 | 1 through12 | 155 |
| 57 | 2 through11 | 150 |
| 113 | 0 and2 through11 | 144 |

The translated cores still contain tens of thousands of CNF clauses.
These numbers are proof-use data, not deletion-minimal semantic cores, and
do not yet expose a short hand explanation of any complete cover case.
All parity literals are translated back to their two named wires and
four-rank windows in the core-analysis JSON.

The analysis did produce a separate hand strengthening:
[the shared-middle-pair capacity lemma](d13_feedback_round6_middle_pair.md).
It gives32 additional endpoint clauses at width13 and has an actual
six-wire comparator-prefix control showing that it adds information beyond
both rank-relation degree bounds and pairwise parity. The new lemma was
**not** used in the three certificates above and was not SAT-tested here.

## Reproducible artifacts

* Bounded driver: [d13_feedback_round6_batch.py](d13_feedback_round6_batch.py).
* Semantic translation: [d13_feedback_round6_core.py](d13_feedback_round6_core.py).
* [Terminal audit](results/d13_feedback_round6-audit.json).
* [Case2 result](results/d13_feedback_round6-r0002.json),
  [case57 result](results/d13_feedback_round6-r0057.json),
  [case113 result](results/d13_feedback_round6-r0113.json).
* [Proof-core translation](results/d13_feedback_round6-core-analysis.json).

Each result names its certificate directory containing `problem.cnf`,
`proof.drat`, `core.cnf`, `core-proof.drat`, and the independent checker
log/terminal record. The result manifests mark
`independently_proof_checked:true` and retain the worker/dependency and
certificate hashes.
