# Structural lower-bound research checkpoint — 2026-11-15

This checkpoint is on branch `codex/d18-structural`, in the isolated worktree
`/private/tmp/an_excellent_sort-d18-structural-20261115`. It includes the
research sources, notes, complete-prefix covers, result records, and saved
CNF/DRAT certificates. Local Python environments, caches, and compiled
executables are excluded. The original working folder was not modified.

The requested complete hand proofs for D(11), D(13), and D(17), and the
D(18) lower bound, are **not all resolved**.

## Verified status

* H9's strengthened early-profile proof has hand coverage of **25/50**
  classes. The next `03 12 46` class and its proposed (4,3,2)-merging theorem
  are work in progress at this checkpoint; their integrated proof/checker
  review is not yet complete. The case1 and case3 local matching arguments
  have been checked, but do not alone finish the class.
* D(13): **4/117** complete two-layer cover cases have checked structural
  exclusions: 0,58,115,116. Case115 needs only six central wire-interval
  bounds. These are SAT-assisted whole-case statements, not a complete
  hand proof of D(13).
* D(17): **3/609** complete two-layer cover cases have checked structural
  exclusions: 606,607,608. The reduced twelve-wire signed-fork obstruction
  has a complete hand proof and generalizes to larger widths. The new
  case606 normalization and incident-row lemmas close additional hand
  branches, but mixed branches remain.
* D(18): **0/411** complete two-layer cover cases are closed. Hand proofs
  exclude one specified five-layer prefix and two six-layer prefixes.
  Additional seven/eight-real obstruction families are obtained by padding
  from small checked SAT certificates; forcing their occurrence remains
  open. There is no completed proof of D(18)>=11.

The [curated artifact audit](d18-search/results/structural-cover-progress-round2.json)
records the complete-cover counts and checks saved certificate hashes and
independent checker logs. Its scope does not include formal verification
of the encoders or of the prefix-cover theorem.

## Main entry points

* [Hand-proof overview](depth-hand-proofs/README.md)
* [Structural SAT frontier and current results](d18-search/certificate-guided-frontier.md)
* [New D13 cases58 and115](d18-search/d13_feedback_round2.md)
* [D17 hand reductions and D18 padding transfer](d18-search/d17_feedback_round2_normalization.md)
* [D18 compressed-prefix hand exclusions](d18-search/commuting-prefix-hand-proof.md)
* [Incremental interval experiment and its negative results](d18-search/endpoint-cegar.md)

The latest incremental D13/D18 interval trials reached their explicit
time limits; smaller formulas did not demonstrate a speedup. Timeouts
are not refutations. The completed runs have terminal records; no large
SAT job is required to interpret this checkpoint.

Some historical manifests contain absolute paths to this worktree or the
original Python environment. Sources and mathematical artifacts are
included, but a fresh checkout must supply Python with `python-sat`, a
C/C++ compiler for the corresponding helpers, and `drat-trim` for proof
checking. Existing saved hashes identify the exact checked proof files.
