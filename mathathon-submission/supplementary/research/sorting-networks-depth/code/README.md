# Code for the sorting-network depth project

Every claim in the four documents that rests on a computation has a script here. Run
`./verify.sh` to rebuild and re-check everything cheap (about a minute); the heavy runs are named
below with their cost.

Conventions: channels are numbered `0..n-1` in the C programs and in most of the Python, `1..n` in
prose inside the documents. A **layer** is a matching of comparators `(i,j)`, `i<j`, min to `i`.
`Fix(M) = {v : v_a <= v_b on every edge of M}` is the image of one layer; `F_t` is the image of the
first `t` layers. "Maximal layer" means `floor(n/2)` comparators.

## The checks behind the handoff (`d11-handoff.md`)

| script | establishes | cost |
|---|---|---|
| `closed.py` | §3: at `n=11`, `n=13` and `n=17` **both** general inequalities are closed — an explicit network has fewer comparators than the inequality would need, so no better size bound can help (at `n=17` capacity needs `S(17)>=73`, and a 71-comparator network is known) | instant |
| `conn_test.py`, `conn_even.py` | §4: Lemma H (in a sorting network on an odd number of channels, layers `2..d` form a connected graph). Exhaustive over all layer sequences: `n=3` (64 sequences, 6 sorting networks), `n=5` (11 881 376 sequences, 4320 sorting networks), `n=4`, `n=6` | 1 min |
| `sat_encode.py` + any CDCL solver | §5.1: the SAT encoding of "a `d`-layer maximal-layer network sorting a state set". `python3 sat_encode.py full 9 6 out.cnf` then run a solver on `out.cnf`: UNSAT (195 s with CaDiCaL here), an independent confirmation of `D(9)>=7`. The `(11,7)` instance is `sat_encode.py full 11 7` — 158 004 variables, 7 285 333 clauses — and did **not** terminate here or under four other solvers | 3 min + solver |
| `residual_n7.py` | §6 row 2 in miniature: the block-lemma residual for `D(7)>=6` — no 4-layer network sorts `image(M)` for any of the 105 near-perfect `M` on 7 channels | 4 min |

## The checks behind the size route (`d11-image-size-route.md`)

| script | establishes | cost |
|---|---|---|
| `twolayer.c` | the exact two-layer minimum `min_M |L_M(Fix(M1))|`: 12, 30, 72, 180 at `n=5,7,9,11`; also a histogram of all values and the third-step minimum | fast to `n=9`; `n=11` about 3 min |
| `exact3.c`, `exact4.c` | the exact `t`-layer minima by full enumeration with pruning (`exact4 n LIMIT` answers "does any 4-layer network have `|F_4| <= LIMIT`?"). Gives `min|F_3| = 9, 11, 19, 40` and `min|F_4| = 8, 13` | seconds |
| `phibound.c` | §3.1: the largest fiber `Phi` against the achieved average fiber (13 versus 2.086 at `n=11`) — the quantitative reason the size certificate is too lossy | instant |
| `greedy_min.py`, `minimage.py`, `minimage11.py` | hill-climbing searches for small images (upper bounds only) — used to show that nothing goes below 23 at `n=11, t=6` | minutes |
| `ratio.py`, `target_search.py` | the per-step shrinkage ratios, and a search for a 6-layer image inside `A'(M_7)` | minutes |
| `dedup.c` | breadth-first search over **distinct** image sets: counts 105 / 3 341 / 76 867 at `n=7`, 945 / 209 777 at `n=9`; the reason brute force stops at `t=3` | 25 min for `n=9` level 3 |

## The checks behind the structure route (`d11-compression-structure.md`)

| script | establishes | cost |
|---|---|---|
| `cycletype.py` | the ratio for **one** pattern per size (the shifted alternation), not the minimum — for `k=2` it gives `7/9` while the minimum is `6/9` from the crossing pattern. Its content is the path profile counts `5, 13, 34 = F_5, F_7, F_9`, i.e. `rho'_j = F_{2j+3}/(2*3^j)`. Take the minima from `rho5.c` | instant |
| `rho5.c` | §2.1: the exact minimum local ratio over all connected patterns — `rho_2 = 6/9`, `rho_3 = 18/27`, `rho_4 = 46/81`, `rho_5 = 123/243` (exhaustive; verified against the smaller cases) | `n=4,6,8` instant; `n=10` about 3 min |
| `rho6.c` | a sampled `rho_6 <= 321/729` — an **upper** bound, which is why it proves nothing on its own | seconds |
| `k6verify.c` | the rigorous lower bound at `k=6`: `k6verify 12 216` walks all `10 395^2 = 1.08e8` pairs of perfect matchings on 12 channels and checks that none has an image below 216, with early exit so only failures are fully counted. **Zero failures** — this is what turned the `k=6` statement from sampled to proved | 3 min |
| `chain.c`, `chain2.c`, `chain3.c` | the greedy descents: `chain` (exact two-layer start, exhaustive), `chain2` (brick start, exhaustive), `chain3` (sampled, for `n=15,17`). Values in `d11-compression-structure.md` §3.1 | `n<=9` seconds; `n=11` 3 min; `n=13` 20 min |
| `cluster.py` | Theorem F' verified on 400 random three-layer chains (0 mismatches). Note the comment about the harness bug that first reported 211 mismatches | instant |
| `frontend_lemma.py`, `frontend_lemma_any.py` | Lemma F (superseded by Lemma H, kept for the block route): for odd `n`, every near-perfect `M` and every interval partition into `b>=2` blocks admit a `10`-free state non-constant on two blocks of size `>=2`. Exhaustive to `n=11` (10 395 matchings x 1 023 partitions) | 1 s to `n=9`, 20 s for `n=11` |
| `depth_search.py` | exhaustive search over maximal-layer networks with subsumption pruning: verifies `D(2..8) = 1,3,3,5,5,6,6` in both directions and prints witness networks | seconds to `n=7` |

## What is *not* here

The SAT instances themselves (up to 154 MB) and the solver runs are not stored; `sat_encode.py`
regenerates them. The `(11,7)` run never finished, so there is no outcome to record beyond that.

## Two lessons worth carrying

* In the SAT encoding the pass-through condition must be keyed on the channel being **idle**, not on
  the comparator being **absent**; with the latter the encoding is satisfiable at depths where no
  sorting network exists, and the error is invisible for `n <= 2`.
* In `cluster.py` the product over a cluster needs *all combinations* of the block states. Building a
  union instead makes Theorem F' look false (211 mismatches in 400 trials), which is how the bug was
  found.

## Runtime

`./verify.sh` takes **1 min 10 s** end to end (measured, compilation included): most steps are instant,
`conn_test.py` (all 11 881 376 five-layer sequences on 5 channels) is about 50 s and `exact4 7 12` about
11 s. Every value it prints matches the documents.
