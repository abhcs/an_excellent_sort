# Structural lower-bound research checkpoint — 2026-11-15

## Current checkpoint: structural research through round ten

This checkpoint saves the research since `9b489a9` on the isolated
`codex/d18-structural` branch, including proof notes, encoders, finite
certificates, CNF/DRAT artifacts, and terminal records for bounded trials.
All agents have stopped editing and all known research jobs are terminal.
The original shared working folder has not been edited.

* **H9: 30/50 reviewed hand cases.** The round-six and round-seven
  cases are integrated. The new
  [fence-six proof package](depth-hand-proofs/h9_feedback_round9_fence6.md)
  addresses two more classes (`03 14 67`, `03 16 27`). Its fixed checker
  passes, including all 33 fourth-layer forms and 23,040 restriction
  replays. Final integrated review remains pending, so these two cases
  are saved without increasing the accepted count.
* **D13: 15/117 complete cover cases have checked structural exclusions:**
  0,1,2,3,4,55,56,57,58,111,112,113,114,115,116. The three new round-nine
  cases have checked DRAT proofs and an
  [independent encoder review](d18-search/results/d13-feedback-round9-review.json).
  This does not complete a hand proof of D(13).
* New general results include
  [rank-separated block constraints](d18-search/rank-separated-blocks.md),
  [exact two-layer data completion](d18-search/d13_feedback_round9_data_ending.md),
  and its reduction to a
  [matching covering mandatory wires](d18-search/d13_feedback_round10_matching.md).
  The new path and matching encoders have an
  [independent review](d18-search/results/d13-feedback-round10-review.json),
  including 14 complete CNF reconstructions. All eight larger round-ten
  trials reached their 30-second limits; they add no cover exclusions.
* **D17: 3/609 accepted complete cover exclusions**, cases 606,607,608.
  The new [first-layer-three package](d18-search/d17_feedback_round10_order.md)
  saves checked UNSAT certificates for cases 604 and 605, obtained in
  about four seconds each. Its checker reconstructs both CNFs and verifies
  stronger-screen witnesses for all cases 0 through 603. Final integrated
  mathematical review remains pending; accepting it would raise coverage
  to 5/609. The theorem explicitly uses the established computer-assisted
  H9 result and is not presented as a pure hand proof of D(17).
* **D18: 0/411 complete two-layer cover cases are closed.**
  **The lower bound D(18)>=11 remains unresolved.** All new larger trials
  were bounded, and no full D18 SAT verification is running.

The [round-nine scope record](d18-search/results/structural-cover-progress-round9.json)
is the latest integrated coverage record. New round-ten packages and their
review status are described above; exploratory artifacts and timeouts are
retained without treating them as proofs. Some manifests contain absolute
local paths and require the external dependencies described below.
Historical sections retain their original counts and open issues.

## Earlier checkpoint: structural research through round eight (`9b489a9`)

This checkpoint saves all current research sources, proof drafts, finite
certificates, CNF/DRAT artifacts, and bounded-run records on the isolated
`codex/d18-structural` branch. Its parent checkpoint is `4d1e95b`.
All agents have stopped editing and all known research jobs are terminal.
The original shared working folder has not been edited.

* **H9: 28/50 reviewed hand cases.** The `02 14 56` proof and
  [threshold-partner lemma](depth-hand-proofs/h9_feedback_round5_rank_partner.md)
  are integrated. The next
  [`03 16 47` draft](depth-hand-proofs/h9_feedback_round6_031647.md)
  is explicitly unfinished: its six third-layer forms and tables are saved,
  but final section 3 and an independent fixed-certificate checker remain.
  Its 51 fourth-layer forms do not add a reviewed case yet.
* **D13: 12/117 complete cover cases have checked structural exclusions:**
  0,1,2,3,56,57,58,112,113,114,115,116. Cases 3,56,112 have new
  block-capacity CNFs, checked DRAT proofs, and an
  [independent encoder/artifact review](d18-search/results/d13_feedback_round8-capacity-review.json).
  Solves took 6.90,7.04,7.46 seconds; checks took 4.89,4.39,4.58 seconds.
  Fresh parity baselines also close these cases (7.77,7.31,9.25 seconds),
  so this is a modest single-run timing improvement, not evidence that
  capacity is essential to closing them or a completed D(13) hand proof.
* New general structural results include exact
  [fixed-ending block capacity](d18-search/fixed-ending-block-capacity.md),
  a linear adjacent-ending decision procedure, and a
  [full-three-rank obstruction](d18-search/d13_feedback_round8_triples.md)
  for two-layer sorting completions at any width. The new exact-endpoint
  and triple-clause encoder has passed mathematical review and finite
  controls, but its synthesis workers have not yet been run. These
  statements do not assert that rank reachability suffices for sorting.
* **D17: 3/609 complete cover cases remain closed.** The entire signed
  case606 family now has a reviewed, finite-assisted obstruction valid
  at arbitrary width. The new
  [round-eight cut-budget proof](d18-search/d17_feedback_round8_cut_lemma.md)
  compresses the 2,728 partial forms to a 29 KB inequality certificate
  and gives a nine-row hand branch. Its checker passes; independent
  mathematical review of that latest package remains pending. No new
  complete D17 cover case is claimed.
* **D18: 0/411 complete two-layer cover cases are closed.** New hand
  [partial-sixth-layer exclusions](d18-search/d18_rank_partner_round7_partial.md)
  rule out conditional families of 140,152, 9,496, and 142 labelled
  matchings after three specified five-layer prefixes. They do not
  exhaust those prefixes or the complete cover. The new capacity tests
  on two four-layer prefixes both reached their 30-second caps; the
  known depth-eleven positive control passed.
  **The lower bound D(18)>=11 remains unresolved.**

The [round-eight scope record](d18-search/results/structural-cover-progress-round8.json)
records the latest counts and review references. All raw exploratory and
timeout artifacts are retained. Some manifests use absolute local paths;
a fresh checkout must supply the external dependencies described below.
Historical sections retain their original counts and open issues.

## Earlier checkpoint: structural research through round six (`4d1e95b`)

This snapshot includes all current research sources, proof drafts, finite
certificates, CNF/DRAT artifacts, and bounded-run records on the isolated
`codex/d18-structural` branch. The previous checkpoint is `7bcc462`.
All agent edits are stopped for this checkpoint; their jobs are terminal.
The original shared working folder is unchanged.

* **H9: 27/50 reviewed hand cases.** The `02 16 37` proof is integrated.
  The next [`02 14 56` draft](depth-hand-proofs/h9_feedback_round5_021456.md)
  and fixed certificates are saved. Its checker passes 423 rank exclusions,
  94 clause checks, and 223,680 restriction-order runs, but final prose and
  independent review remain; it is not counted as a 28th case.
* **D13: 9/117 complete cover cases have checked structural exclusions:**
  0,1,2,57,58,113,114,115,116. The new
  [round-six cases](d18-search/d13_feedback_round6.md) are 2,57,113.
  Solves took about 20.03,10.64,13.64 seconds and independent checks
  19.06,8.18,9.82 seconds. Saved source/dependency/CNF/proof hashes and
  successful checker logs were rechecked at this checkpoint. These are
  SAT-assisted case exclusions, not a completed hand proof of D(13).
* The [nine-real three-component theorem](d18-search/three-component-obstruction.md)
  is proved by hand: four layers before the end, every signed restriction
  leaving nine arbitrary real inputs has at most two interaction components.
  The new [shared-middle-pair lemma](d18-search/d13_feedback_round6_middle_pair.md)
  strengthens saturated-cone parity and applies at arbitrary ambient width.
* **D17: 3/609 complete cover cases remain closed.** The critical-perfect
  reduction has completed root review. The
  [critical two-idle extension](d18-search/d17_feedback_round6_reduction.md)
  passed [independent review](d18-search/results/d17-hand-round6-review.json)
  with 1,584 finite cases and 9,504 branches. Its finite certificate remains
  a premise. The noncritical mixed branch and full hand proof remain open.
  A nonfatal prose correction remains in section 2: “Every A vertex outside
  C” should read “Every used A vertex outside C”; D changes status but is idle.
* **D18: 0/411 complete two-layer cover cases are closed.** Three specified
  six-layer prefixes now have [explicit rank-endpoint hand certificates](d18-search/rank-layer-round6-hand-tables.md),
  replayed by a SAT-free checker. All continuations of three specified
  five-layer prefixes are excluded by checked SAT certificates, each solve
  and check under one second. This does not cover every five-layer prefix.
  The two distinct four-layer tests, with and without the new middle-pair
  clauses, reached their 30-second limits and prove nothing about those cases.
  **The lower bound D(18)>=11 remains unresolved.**

The five-layer experiments include both combined structural conditions
(`prefix-rank-round6-cut8-*`) and rank-width/parity alone
(`prefix-rank-round6-only-*`). The latter all finished and their companion
`check-terminal.json` and `check.log` files record successful independent
DRAT checks; raw worker manifests still say `UNSAT_UNCHECKED` because they
were written before the separate check. The
[encoder review](d18-search/results/d18_hand_round6-frontier-review.json)
covers the combined and one-next-layer tested calls. Exact earlier worker
sources are preserved as `d18-search/recorded_*.py` alongside dependencies.

Historical sections below retain their counts as of their own snapshots.
Some manifests use absolute local paths; fresh checkouts need the external
Python/SAT/compiler/checker dependencies described below. Exploratory and
timeout artifacts are included without treating them as proofs.


## Follow-up checkpoint

The earlier snapshot below was pushed as `e9b71c4`. This follow-up saves
the subsequent research, including exploratory files, with this status:

* H9 hand coverage is now **26/50**. The `03 12 46` proof and its
  (4,3,2)-merger argument have completed integrated review and replay.
* Hand lower bounds for merging (4,3,2), (3,3,3), and (4,4,1) imply a
  general structural theorem: four layers before the end, every signed
  restriction leaving nine real inputs has an interaction component of
  size at least five. See the
  [component proof and controls](d18-search/merge-component-obstruction.md).
  The collector passed 108 small prefix/mode checks, 8,676 signed
  assignments, and 68,608 binary trace replays. A known eighteen-wire
  depth-eleven sorter passes the condition.
* The component screen rejects 34 of 117 saved D13 four-layer witnesses;
  this does **not** exclude their complete two-layer cover cases. A new
  common third/fourth-layer candidate for case116 passes the screen.
  All six sampled D18 six-layer prefixes also pass it.
* Complete cover exclusions remain **4/117 for D13**, **3/609 for D17**,
  and **0/411 for D18**. The lower bound D(18)>=11 remains unresolved.
* The [new D17 hand draft](d18-search/d17_feedback_round3_hand.md) and
  its SAT-free checker are saved. The checker passed 61,512 relevant
  fourteen-wire first matchings, but the draft still awaits independent
  mathematical review. It addresses the critical-edge branch with at
  most one cross gate, not the full case606.
* The H9 `02 16 37` scan and the D17 probe/classification/two-cross
  experiments are exploratory. They are not additional proved cases.
  The saved (5,4) merger is a small positive control.

The additional merger certificates, bounded-run terminal records, and
component replays are included. Python syntax, JSON parsing, shell
syntax, and source whitespace checks pass; raw checker logs are preserved
verbatim. No new full SAT verification of
D(18)>=11 has been completed.

## Earlier checkpoint snapshot (`e9b71c4`)

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
