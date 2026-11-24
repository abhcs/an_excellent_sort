# Independent review scripts for the H9 class `02 15 36`

Written from scratch on 2026-11-18 for the review in
[../../results/h9-recovery-021536-claude-review.md](../../results/h9-recovery-021536-claude-review.md).
They brute-force every nine-wire matching at layers 3 and 4 (any size, no maximality assumed),
recompute the case-2 local modes and guard rows, the signed demand rows, and the ending guards,
and check the small-width facts behind the six-real exchange rule. `common.py` sets `DOC` to the
worktree path used at review time; edit it to rerun elsewhere. Run each `check_*.py` with the
project's python-sat environment (none of them uses SAT).
