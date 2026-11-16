# Research recovery — 2026-11-16

The earlier worktree at
`/private/tmp/an_excellent_sort-d18-structural-20261115` was absent when
the goal resumed. Its Git registration remained, but its files did not.
No copy of the uncommitted round-eleven through round-fifteen packages
was found in the project, Documents, or managed-worktree locations
checked during recovery. Their results must not be presented as
available, reproducible artifacts until reconstructed.

A durable managed worktree was created from the saved and previously
pushed commit `6ebff9d6ec1a2d1a4249932fca2dd83429fddad5`, on the new
branch `codex/d18-structural-resume`:

    /Users/abhishek/.codex/worktrees/d18-structural-resume/an_excellent_sort

The original shared checkout and its current branch were not edited.
The historical [checkpoint](CHECKPOINT.md) retains the state as saved.

The two saved fence-image H9 cases have now passed independent
mathematical review and a read-only replay of their unchanged fixed
checker. This restores **32/50 accepted hand cases**, leaving 18. See
[the recovery review](depth-hand-proofs/results/recovery-h9-fence6-review.json).
The existing complete computer-assisted H9 proof still implies
D(11)>=8, but a complete hand proof remains unfinished.

The checkpoint contains **15/117 accepted D13 cover exclusions**.
Independent recovery review of the saved D17 theorem, encoder, two
byte-identical CNF reconstructions, and historical proof-check records
restores **5/609 accepted D17 exclusions**, cases 604 through 608. See
[the review](d18-search/results/recovery-d17-first3-review.json); no
fresh SAT or DRAT runs were needed. Full computed H9 remains an explicit
premise. A later historical 7/609 count depended on artifacts absent from
this checkout. D18 remains **0/411 complete
cover exclusions**, with D(18)>=11 unresolved. Partial prefix exclusions
and general matching/merger theorems survive in the checkpoint.

The reconstructed [poset image theorem](d18-search/height-two-image-closure.md)
gives structural conditions for arbitrary widths, including an explicit
family of four-layer 18-wire prefixes requiring at least eleven total
layers. It does not add a whole-cover exclusion.
The [cover census](d18-search/results/height-two-cover-recovery-census.json)
recognizes height-two images after the first two layers in 15/411 D18
and 22/609 D17 cases, all with width nine. Recognition only identifies
where the theorem can constrain subsequent matchings; it does not
refute any of these cases.

At recovery no prior subagents were running, and no full D18 SAT solve
was launched. New work has used proof review and bounded finite checks.
