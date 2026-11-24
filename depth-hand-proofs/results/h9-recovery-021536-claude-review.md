# Independent review: H9 class `L2 = 02 15 36`

Reviewed notes: `h9_recovery_021536_reduction.md`, `h9_recovery_021536_case2.md`,
`h9_recovery_021536_fourths.md`, `h9_recovery_021536_fourths_tables.md`,
`h9_recovery_021536_endings.md`, and the four checkers in `verify/`.
Review date 2026-11-18. Nothing in the repository was modified except this file.

## Verdict: ACCEPT WITH FIXES

I found no mathematical error and no coverage gap. The chain
"all L3 → 18 forms → case 2 excluded + 17 forms → 11 empty, 6 forms → 31 (L3,L4) pairs →
31 endings excluded" closes. I re-derived every link with my own code, written from scratch,
which brute-forces every nine-wire matching at L3 and at L4, of any size. Where the notes rely
on hand lemmas, I checked the lemma proofs by hand. The fixes below are documentation and
checker-coverage items. None of them changes a claim or a table entry.

## Issues

| # | Severity | Location | Issue | Suggested fix |
|---|---|---|---|---|
| 1 | fixable (verification only) | `verify/h9_recovery_021536_endings_check.py:51,56,102` | No checker links the 31 ending prefixes to the fourths survivors. The endings checker checks only the per-case counts `{1:6,5:18,8:2,9:2,14:1,16:2}` and that its certificate matches its own table. It never compares the (M,N) pairs with `fourths-certificate.json`, and never checks that the third layer of case k equals `FORMS[k-1]`. So the coverage link stated at `fourths.md:6-8` and `endings.md:9-11` is asserted in prose only. I checked it independently: the two sets of 31 (case, M, N) triples are identical. | Import the fourths certificate (or `FORMS`) in the endings checker and assert set equality. |
| 2 | fixable (documentation) | `reduction.md:16,66`; `fourths.md:25` | The "five-wire thin lemma" is never stated or linked. The repo statement is README §4 **Lemma 3** (`README.md:273`): no network of at most 5 layers on 5 channels whose first two layers contain **at most one comparator each** sorts. Every use here states that hypothesis correctly ("at most one gate in each of its first two layers"). But the common paraphrase "a 5-wire depth-5 sorter has at least two comparators in each of its first two layers", which also appears in this review's brief, is **false**. Counterexample: `34 / 13 24 / 02 34 / 01 23 / 12 34` sorts all 120 permutations and has a one-comparator first layer. | Link README Lemma 3 and quote its exact hypothesis at first use. |
| 3 | cosmetic | `reduction.md:22-24` | The sentence "The listed orientations are allowed to be generalized" is unclear. It means that boundary gate `41` has its minimum on wire 4 and its maximum on wire 1, so it is reversed at the cut, and that untangling preserves layer sizes. | Say that directly. |
| 4 | cosmetic | `reduction.md:50` | Only `02` and `06` are named as impossible in the idle-5 alternative. `36` is also redundant after L2 (x3≤x6, listed at line 47). The argument never needs this, so nothing breaks. | Add `36`, or say "any of the six ordered pairs". |
| 5 | cosmetic | `reduction.md:58-62` | "Otherwise both have two" compresses a case split: first layer = 2 and second ≤ 2; second ≤ 1 is excluded by D(5); so second = 2. | Spell out the three-way split. |
| 6 | cosmetic | `reduction.md:76-81` vs `verify/h9_recovery_021536_reduction_verify.py:20` | The note's restriction **C** (`-0,-1,+2`) is named `D` in the checker, because `C` already names the prefix there. | Rename one of them. |
| 7 | cosmetic | `fourths.md:206` | "Choose any edge in a smallest unmet clause" reads as one arbitrary choice. The rule as applied (checker `local_proof`, and the tables) **branches on every edge** of that clause, which is what exhaustiveness needs. | Reword to "branch on each edge of a smallest unmet clause". |
| 8 | cosmetic | `endings.md:34-36` | "These reciprocal guards are necessary even when j itself is not mandatory" is true but vacuous. A lo/hi guard from j's side needs a run with y_j ≤ h_j−4 (or ≥ l_j+4), which forces span(j) ≥ 4, so j is mandatory. All 12 printed reciprocal partners have span ≥ 4. | Delete the sentence or rephrase it. |
| 9 | cosmetic | `endings.md:4,9,59-62,76`; `case2.md:15,66-67,155`; `fourths_tables.md:412` | The generated text drops spaces before numbers: "the31", "edge24 in form1.4", "pivots1 and4", "partner3", "other26", "parity24", "ranks0 through8", "at least4", "partner2 or5", "are9 ... and9*8*8", "all585", "the140", "demand17 exceeds capacity16". | Fix the generators (`*_build.py`) and regenerate the notes. |
| 10 | cosmetic (process) | `verify/h9_recovery_021536_case2_check.py:68`, `verify/h9_recovery_021536_endings_check.py:113` | These two checkers always overwrite tracked `results/*.json`, whose timing field changes on every run, so rerunning them dirties the tree. The other two checkers use `--out`. I restored both files after rerunning. | Add an `--out` flag, as in the other two checkers. |
| 11 | optional | `endings.md:59-60,76` | In 1.4, parity is not needed. With all six mandatory wires {1,2,3,4,7,8} and edge 24 kept, 1–3 is forced, then 4–2 and 7–5, and wire 8 (partner 5 only) is stranded. 9.1 and 14.1 also admit an unused parity exclusion on 38. | None required. |
| 12 | informational | `fourths_tables.md` forbidden lists | The forbidden lists are sound but incomplete. Unlisted pairs that also never fire: case 1 `26 46`, case 4 `26`, case 5 `36 46`, case 8 `26 36`, case 9 `36`, case 12 `26`, case 14 `36`, case 16 `46`, case 18 `26 46`. This is harmless because no survivor contains any of them. The checker validates forbidden lists against its own propagation rules (`fourths_check.py:14,193`), not by the 0-1 principle. The propagation rules are sound; I also confirmed every listed pair on all 512 binary inputs. | None required. |

No issue is fatal.

## Coverage (task item 1)

* **L3, all matchings.** I enumerated all 2620 matchings M on nine wires and deleted every
  pair that never fires after L2. Those pairs are exactly `02 05 06 15 36 45`, the note's list
  at line 47, which is therefore complete. No pair after L2 always swaps. The breakdown:
  * 2497 matchings fail the H7 pair condition (fewer than three gates avoiding `56` or avoiding `05`).
  * 60 reduce to the 18 listed forms; these are exactly the 18 classes of K and K+56 under
    7↔8, each listed once.
  * The remaining 63 are the idle-5 four-gate matchings. Each is excluded by at least one
    argument that I validated separately on its own trace, by its own validity condition:
    * the A/B or A/C exchange: exactly two track-disjoint retained gates and six-sets meeting in five;
    * the all-cross D(5) blind;
    * the `-0,+2` rescheduling into two layers of ≤2 gates.

  The counts by argument are AB+reschedule 18, AC 18, cross 14, AB+AC 7, reschedule only 6.
* **Symmetry.** The 7↔8 relabelling fixes L1 and L2, and untangling preserves the edge set
  of M. The 7↔8 reductions inside fourths cases 1, 9 and 10 use only the symmetry of the
  printed demand rows and forbidden lists. I confirmed that symmetry, and my brute force
  uses no symmetry at all.
* **Case 2.** The argument fixes an idle wire of N, which exists because nine is odd. It
  covers every N and every Q, including non-maximal ones and ones with redundant gates.
* **L4, all matchings, no maximality.** For each of the 17 forms I enumerated all 2620
  matchings N of any size that avoid the printed forbidden edges, and filtered them by the
  printed demand rows. The survivors equal the printed lists exactly: 6/18/2/2/1/2, total 31,
  with 0 for the other 11 forms. The non-maximal survivors `17 25 48` and `18 25 47` are
  present and carried to endings 1.5 and 1.6.
* **Middle layers.** No maximality is assumed anywhere:
  * L3 may have 3 gates (form K).
  * Redundant gates are removed only when they never fire, which changes no value. Every
    such deletion was checked on all binary inputs.
  * Q is never assumed perfect: the isolated-pivot and Hall arguments allow idle wires.
* **Endings.** The 31 (M,N) pairs in `endings.md` equal the fourths survivors (see issue 1).

## Soundness of general lemmas (task item 2)

I re-proved each of the following by hand:
* the six-real exchange rule, including that a six-set intersection of size five cannot be N-closed;
* the even-core, common-pair, odd-core/deletion-graph and shared-triangle matching lemmas,
  the weighted-demand bound, and the local table rule. The odd-core necessity holds in both
  cases h = r−1 and h = r−2.
* the interval lemma, by the monotone-map argument;
* the threshold-partner rules;
* saturated-cone parity. This includes the degenerate case where P repeats the Q edge, in
  which both cones coincide and meet in 4.

All are correct as stated.

Hidden assumptions:
* Idle wires: "wire 5 idle" in case 6 follows from the common-pair lemma with 78 forbidden.
* Redundancy deletion: deleting a comparator that never fires changes no later value.
* Sentinel signs: every sentinel sits on an original input, so all placements are realizable.
  The six-wire and Lemma 3 placements act on an abstract untangled sorter.

None of these is a problem.

I also checked, by exhaustive search over binary-image sets, the two small facts that the
exchange rule rests on:
* README Lemma 3 holds as stated (5 wires, depth 5, ≤1 and ≤1 gates): no sorter exists.
* A six-wire depth-5 sorter has ≥2 first-layer gates, and exactly 2 forces 3 in the second layer.

H7 (`h7-early-profiles.md` §3) is used exactly in its proved form, "no depth-6 seven-wire
sorter with ≤2 gates in each of the first two layers". I did not re-verify H7 itself.

## Tables, hand spot-checks and checkers (task item 3)

My independent recomputation, via symbolic traces plus numeric replays, covers:
* all 100 signed demand rows: real sets and retained-gate counts 3−d;
* all 11 case-2 runs, all 9 Q-idle modes, all 576 paired local modes (minimum witnessed gap
  exactly 4), and all 81 printed guard rows;
* all 16 ending inputs, 32 guard rows, 12 reciprocal rows, 5 parity rows and the
  "remainder before parity" columns.

I also computed the allowed-edge graph directly: an edge is allowed when the bank spans of
both its minimum and maximum outputs are ≤3 and parity does not exclude it. For all 31
prefixes, no matching covers every mandatory wire.

By hand I recomputed:
* reduction rows `+0,+2`, `+0,-2`, A, B, C, the all-cross `-0,-1,+2,-4` and `-0,+2`;
* fourths case 1 row 2 (`-0 -1 +2 -4` → 24578, one retained gate) and case 14 row 4
  (`+0 +2 +4 -6` → 01348, two retained gates);
* case-2 run H through C (`416075823`);
* ending 5.1 pivot 7 (endpoints G:1, B:7; guards `A hi:568`, `D lo:012`, `N hi:346`, which
  leave no partner);
* ending 9.1 pivot 7 and the parity row 37 (min output G:1, J:4; max output D:4, B:7;
  intersection {4}).

I also re-derived the hand arguments for cases 1, 6, 9, 10 and 14, the case 17 weighted
inequalities, and the even-core and common-pair core counts (12, 10, 10, 10; 16, 22). All agree.

Rerunning the four checkers with the repo venv, all pass. By design, no checker verifies the following:
* the general case split of `reduction.md` §1 over all M (only the 63 idle-5 matchings are enumerated);
* any lemma proof;
* the core lists for fourths cases 1, 9 and 14, which are hard-coded at `fourths_check.py:113-129`;
* the case 6 contradiction: `fourths_check.py:54` checks only that its rows exist;
* the fourths-to-endings link (issue 1).

My scripts cover all of these. They live outside the repo, in a scratchpad that may be
cleared: `/private/tmp/claude-501/-Users-abhishek--claude-spares-spare-8LJXq4/c54486b5-433d-4286-8fa9-f685212181d8/scratchpad/review021536/`
(`check_reduction.py`, `check_case2.py`, `check_fourths.py`, `check_endings.py`,
`check_endings2.py`, `check_small.py`).

## Follow-up (2026-11-18, same day)

Issue 1 is resolved by `verify/h9_recovery_021536_link_check.py`, which asserts that every third
layer in the fourth-layer and ending certificates is `FORMS[case-1]`, that the fourth-layer
certificate covers exactly the cases other than 2, and that the 31 ending prefixes equal the 31
fourth-layer survivors (status LINKED). Issue 2 is resolved: `h9_recovery_021536_reduction.md` and
`h9_recovery_021536_fourths.md` now state README Lemma 3 with its exact hypothesis. All four
original checkers pass again after these edits. Issues 3–12 are cosmetic or informational and
remain open. With the substantive fixes applied, the class counts as accepted (33 of 50).
