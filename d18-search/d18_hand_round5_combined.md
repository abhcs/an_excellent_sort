# The combined rescheduling and component tests still admit L6

For each sampled five-layer prefix `beam00`, `beam16`, and `beam32`, one
common sixth matching satisfies both of the following necessary conditions:

* Every seven/eight-real restriction whose normalized retained DAG through
  L5 has height at most two and fewer than5/7 gates must acquire either a
  third dependency level or enough additional gates in L6.
* Every nine-real restriction must have at most two interaction components
  after L6, since all three-block partitions of nine require five merger
  layers and only four layers would remain in a depth-ten sorter.

These are directly replayed necessary-condition survivors. None is claimed
to have a four-layer sorting completion, and none of the five-layer
prefixes is excluded by this combined test.

## Common sixth layers

| Prefix | R7/R8 demand groups | R9 cut states | Three-block clauses | L6 |
|---|---:|---:|---:|---|
| beam00 | 40 | 76 | 78 | `14 (2,11) (3,10) 56 79 (12,13) (14,15) (16,17)` |
| beam16 | 23 | 84 | 110 | `12 38 46 (5,15) (7,14) (10,11) (12,13) (16,17)` |
| beam32 | 108 | 84 | 86 | `01 28 37 45 69 (10,14) (11,15) (12,13) (16,17)` |

The three SAT workers exited0 in0.10,0.09,0.14seconds wall time, each with
an explicit30-second external cap. There was no UNSAT result or proof to
check. All solver processes are terminal.

## Encoding and direct verification

The existing R7/R8 encoder supplies the matching clauses and each
rescheduling demand. Its gate variables1 through153 correspond to the
lexicographically ordered unordered pairs of eighteen wires.

For each R9 cut5 state, enumerate every unordered partition of its
interaction components into three nonempty groups. Require L6 to contain
at least one RR edge crossing the resulting three blocks. Deduplicate
identical clauses across states. Requiring all these clauses is equivalent
to leaving at most two components: if three or more survived, they could
be grouped into three unions with no crossing L6 edge.

Before solving, independent adjacency-graph traces verify every component
representative and its physical cut labels. After solving, direct replay
checks all R7/R8 retained profiles and all R9 component states. The fixed
routing in the repeated-gate normalization is also checked on25,344 binary
real-input assignments across the three cases.

A fresh collector pass then checks the entire normalized placement family
at cut6 for each survivor, not just the stored representatives:

| Reals | Placements per prefix | Violating placements, all three prefixes |
|---:|---:|---:|
| 7 | 1,538,352 | 0 |
| 8 | 1,135,242 | 0 |
| 9 | 710,828 | 0 |

That is10,153,266 placement replays in total. The local R7/R8 collector is
an exact copy of the earlier collector except that its input guard accepts
cut6 as well as cut5; its normalization and enumeration logic is unchanged.
The R9 collector is compiled from the reviewed root source. All nine
collector jobs exited0, each under an explicit20-second cap.

## Artifacts

* Combined search and replay: [d18_hand_round5_combined.py](d18_hand_round5_combined.py).
* Whole-family verifier: [d18_hand_round5_verify.py](d18_hand_round5_verify.py).
* Local cut6 collector: [d18_hand_round5_reschedule_states.cpp](d18_hand_round5_reschedule_states.cpp).
* [Terminal audit](results/d18_hand_round5_combined-audit.json).
* [Whole-family verification](results/d18_hand_round5_combined-verification.json).
* Per-prefix input, result, and terminal files use
  `results/d18_hand_round5_combined-beam{00,16,32}*`.
