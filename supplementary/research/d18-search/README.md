# d18-search: looking for a depth-10 sorting network on 18 channels

**Question.** Is D(18) = 10? It is known that 10 ≤ D(18) ≤ 11. The lower bound comes from
D(17) = 10 (Ehlers & Müller 2015; Codish et al. 2019) and monotonicity. The upper bound is
Al-Haj Baddar & Batcher's 11-layer network (2009). A depth-10 network on 18 channels would prove
D(18) = 10. C. Wang ([arXiv 2511.04107](https://arxiv.org/abs/2511.04107), Nov 2025) reports
trying the same and failing.

**Status.** D(18) remains unresolved. Work continues on branch `codex/d18-structural`
in an isolated worktree. The latest [rank-profile results](two-layer-capacity-proofs.md)
give the sharp normalized-ending capacity bound floor(7n/2)-3 for n>=17
and an exact O(n |U|) test for two-layer completion once the prefix image U
is known. Six-run and ten-run hand certificates exclude example prefixes.
A verified eight-layer prefix with 50 outputs passes degree and parity,
disproving the proposed universal obstruction from those two tests alone.
The [two-value hand proofs](two-real-hand-proofs.md) give
an exact collision criterion, a parity obstruction, and a path structure for
two-layer completions. The latter forces planarity and bounds every radius-two
neighborhood of required interactions by ten wires, at every width. Explicit
18-channel prefix certificates require only 20 binary runs each. The topology
implementation was checked on all 2,559 normal-form suffixes of widths two
through eight, with an 18-channel sorting network as a positive control.
The [context-sensitive continuation](two-layer-context-proofs.md) gives an
exact two-layer completion test without SAT, an inversion-graph characterization,
and further hand obstructions. It agrees with unrestricted enumeration on
1,872 small prefixes and reconstructs two known 18-wire completions. A new
18-wire prefix disproves the conjecture that every eight-layer prefix has
three freely varying output wires; it is still excluded by the degree test.
The preceding [structural results](structural-frontier.md)
give an exact family formula for signed-infinity restrictions, constraints coupling their
later layers, and a limit on extending pure layer-blinding arguments for every even n >= 18.
The complete two-layer cover has **411** cases. One exact depth-10 completion test reached
its 600-second limit (301,635 variables; 6,121,145 clauses) and has terminated; zero cases
in this cover are resolved. See the [audit](results/complete18-d10/audit.json).
The new `capacity_sat.py` adds the proved rank-profile restrictions to the exact
encoding. Its [calibration](results/capacity-sat-checks.json) passed 904 fixed
normal-ending positive controls, all 22 complete n=9 depth-6 negative cases,
and a depth-7 positive network checked on all 512 inputs. A
[45-second retry of n18-r0000](results/capacity18-r0000-attempt1.json) with these
constraints also timed out (303,172 variables; 6,203,577 clauses). This attempt
has terminated and closes no case; no full-cover verification is running.
The subsequent [fourteen-state lemma](two-layer-capacity-proofs.md) gives a
one-run hand obstruction and allows the final two layers to be encoded once
per possible intermediate state. This exact shared encoding passed the small
controls and two full 18-wire positive controls. Its
[45-second retry](results/shared18-r0000-attempt1.json) also timed out, with
261,370 variables and 5,664,501 clauses. No complete-cover case is closed.
A verified seven-wire construction shows that the five-state level capacity
is attainable; a universal reduction of that bound to four is false.

The narrower prefix results below are historical results from earlier searches. Their
recorded pause times are not evidence that those processes still exist; resuming requires
checking the current process state.

## The solver (`netsat.py`)

The search fixes a prefix P and asks a SAT solver for the remaining layers. It encodes only the
images of the 2^18 binary inputs under P. Every restriction below is without loss of generality
unless marked as a heuristic.

| technique | source | what it does |
|---|---|---|
| standard comparators | untangling, Knuth 5.3.4 ex. 16 | only (i,j) with min to i |
| no redundant comparators in the free layers | deleting a never-swapping comparator changes nothing | justifies the rows below |
| last layer = adjacent comparators, absorbed | Codish, Cruz-Filipe, Schneider-Kamp, [arXiv 1411.6408](https://arxiv.org/abs/1411.6408), Lemma 3 | the last layer gets no value variables; an input with z zeros must reach 0^(z-1) ab 1^(n-z-1) |
| penultimate layer φ2–φ4 | same paper, Cor. 2 | length ≤ 3; (i,i+3) forces (i,i+1),(i+2,i+3) in the last layer; (i,i+2) forces (i,i+1) or (i+1,i+2) |
| unit clauses before the penultimate layer | derived from φ2, φ3 | channels ≤ z-4 hold 0, channels ≥ z+3 hold 1 |
| co-saturation ψ (`--cosat`) | same paper, Thm 4.2 | last-layer normal form; the paper combines it with φ |
| windows + one-up/one-down encoding | Ehlers & Müller, [arXiv 1501.06946](https://arxiv.org/abs/1501.06946) | value variables only between the first 1 and the last 0 of each input |
| prefix relabeling (`relabel.py`) | same paper, §3.1 | permute and untangle the prefix to shrink windows (about 2x fewer clauses) |
| iterative inputs (CEGAR) | same paper, §3.2 | add the smallest-window counterexamples first |
| non-redundant first free layer | prefix outputs are known | drops comparators that never swap |
| redundancy tracking | new here | if x_i ≤ x_j is guaranteed after a layer, (i,j) is forbidden in the next one |
| duality lex-leader (`--lex`) | network and its reflection are both solutions | first free layer ≤ its mirror |
| self-dual networks (`--sym`, **heuristic**) | Bundala-Závodný; Wang 2025 | halves variables and inputs; can lose solutions |
| solvers | Kissat 4.0.4, CaDiCaL 1.9.5 (via python-sat) | Kissat on the full instance was fastest for finding |

Every network found is re-checked on all 2^n inputs (bit-parallel 0-1 principle, `verify_all`).

## Validation

* n = 4..12, Parberry first layer: finds the optimal depth and proves one layer less impossible,
  for every combination of the options above (45 checks).
* n = 16, depth 9: found from the 4-layer Green filter (0.5 s) and the 3-layer one (224 s).
* n = 17, depth 10: found from Ehlers & Müller's prefix (Green filter on 16 channels, 3 layers,
  one idle channel) in 175 s (Kissat).
* New along the way: the **4-layer** Green filter on 16 channels plus one idle channel also extends
  to depth 10 on 17 channels (15 s, 74 comparators after pruning).
* Case-split calibration: the 17-channel analogue of `cases_e18_3.py` (5 cases by the layer-4
  partner of the idle channel) found a depth-10 network in the case (0,1) after 26 min on a
  heavily loaded machine (75 comparators after pruning, verified). So forcing layer-4 choices
  doesn't block solutions. The idle case hit its 30-min limit; that is not an UNSAT.

## Results for n = 18, depth 10

| prefix | free layers | result |
|---|---|---|
| `e18_4`: 4-layer Green filter on 16 channels + comparator on the other two | 6 | **UNSAT**: with only the provably valid constraints, CaDiCaL 423 s and Kissat 764 s; with ψ and lex, CaDiCaL 426 s and Kissat 680 s; bare encoding (no φ, no redundancy rules, only the adjacent last layer), Kissat 2137 s; independent encoder `depth-hand-proofs/verify/satnet.py` (exact full-equivalence encoding, last layer adjacent), Kissat 1843 s (`crosscheck_e18_4.py`) |
| 79 random self-dual labelings of `e18_4` | 6 | UNSAT (also implied by the row above) |
| 3-layer Green filter + pair, 10 self-dual 4th layers from simulated annealing | 6 | UNSAT, 10 to 15 s each |
| same, 11 non-symmetric 4th layers with 506 outputs | 6 | 3 tested, 3 UNSAT (426–927 s each); the rest were stopped to free cores |
| Wang-style self-dual beam prefixes, Parberry first layer, 4 layers, 503–520 outputs | 6 | 32 / 32 UNSAT |
| same, BZ first layer (512+ outputs) | 6 | 34 tested, 34 UNSAT; stopped |
| same, 5 layers, 254–272 outputs | 5 | 48 / 48 UNSAT |
| two mirrored 9-channel 4-layer halves (729–841 outputs) | 6 | 13 tested, 13 UNSAT (self-dual); stopped |
| `e18_3`: 3-layer Green filter + pair, whole problem | 7 | paused, no answer after 2.9 h and 2.7 h of solver time (Kissat, 2 labelings) |
| `e18_3`, self-dual: pair (0,17) at the ends, Green filter on 1..16 | 7 | paused, no answer after 2.4 h (CaDiCaL) |
| `m18_3`, self-dual: pair (8,9) in the middle, Green filter on 0..7 and 10..17 | 7 | **UNSAT** after 1.5 h of solver time (CaDiCaL, 600 inputs; the log says 3.4 h because the Mac slept for 1.9 h of it). Self-dual only, so evidence, not a proof |
| `e18_3` split into 26 symmetry-reduced cases on how layer 4 treats the extra pair | 7 | paused, 0/26 finished. Cases 0–2 had used 2.6 h and cases 24–25 1.9 h of their 4-hour limit. Pool A works up from case 0 (3 workers), pool B down from case 25 (2 workers, `--reverse --claim-dir`); each case runs once, the other pool logs it as SKIPPED/ERROR3 |

The historical `status.sh` and `pause.sh` scripts apply to the earlier search processes.
Log files alone do not establish that a process is live or paused. Logged times are
wall-clock, so they may include time the Mac slept. The new `cover_solve.py` runner
records explicit terminal outcomes and does not infer UNSAT from a timeout.

**Consequence of the first row.** No 18-channel sorting network of depth 10 has a 4-dimensional
Green filter on 16 of its channels as its first four layers. In those four layers the other two
channels may be compared with each other or left idle (the comparator can always be added to the
first layer). This is the 18-channel analogue of the prefix that gave the depth-11 network on 20
channels (Codish, Cruz-Filipe, Ehlers, Müller, Schneider-Kamp, JCSS 2019, §5): the Green filter on
the outer 16 channels with the middle channels sorted. That paper does not mention 18 channels.
*Positive control:* the same prefix extends to **depth 11** in 58 s (86 comparators, verified on
all 2^18 inputs), so the encoding is not over-constrained here.

**Calibration caveats.**

* The greedy beam is a weak prefix generator. At n = 16 it finds 4-layer prefixes with 190
  outputs, and all of them fail at depth 9, while the Green filter has 168 and works.
* Self-dual searches depend on the channel labeling. The Green filter in the labeling (i, i+8)
  has no self-dual depth-9 completion at n = 16, and 40 random self-dual labelings also failed.
  Yet a self-dual 61-comparator completion exists with the cube-matching (0,8),(1,12),(2,10),…
  (found from the 3-layer prefix in 5 s).
* So the self-dual and beam rows are evidence, not proofs. The `e18_4` row is unrestricted and
  covers every labeling.

## Is there a computational proof of D(18) = 11?

No, neither here nor in the literature. Dobbelaere's table still lists 10 as the lower bound. The
UNSAT results above rule out particular prefixes, which is what an upper-bound search does. A
lower-bound proof has to rule out **every** prefix. The standard route (Bundala & Závodný 2014;
Ehlers & Müller 2015) is:

1. Take the first layer maximal (Parberry).
2. Enumerate all 2-layer prefixes up to channel permutation, reflection and output-set
   subsumption.
3. Prove by SAT that none of them has an 8-layer completion.

The last data point shows the scale. D(17) ≥ 10 needed 609 two-layer classes with **7** free
layers each, about 27.6 million CPU-seconds (≈ 320 CPU-days) in 2015, the hardest single class
taking 27 hours. The saturated D(18) cover actually has **fewer** classes, 411, but larger
output sets (at least 3,888) and **8** free layers. The single new complete-cover test
timed out after ten minutes. That is insufficient to estimate the time for a complete
proof; stronger structural reductions remain the main research target.

## Files

* `two-real-hand-proofs.md`, `two_real_graph.py`, `two_layer_topology.py`: exact
  collision criterion, pair graphs, degree/parity and path-structure obstructions,
  plus small independently replayable prefix certificates.
* `two-layer-context-proofs.md`, `two_layer_context.py`: inversion graph,
  rectangle exclusions, and exact two-layer completion by matching propagation.
* `two-layer-capacity-proofs.md`, `two_layer_profiles.py`: exact rank blocks,
  sharp ending capacities, short count certificates, and an exact path algorithm
  for two-layer completion.
* `structural-frontier.md`: hand proofs for restriction families, their coupling, and the
  obstruction to universal third-layer blinding at even widths >= 18.
* `two_layer_cover.py`, `verify_two_layer_cover.py`: complete cover generation and independent
  enumeration checks. `prefixes/complete18.jsonl` contains the 411 representatives.
* `verify_restriction_structure.py`: validates transport lemmas and replays explicit third-layer
  obstruction witnesses; it uses no SAT solver.
* `cover_solve.py`: bounded exact completion tests and an auditable per-case ledger. A full
  UNSAT ledger would still need independent proof checking.
* `netsat.py`: encoder and CEGAR driver (`--prefix`, `--depth`, `--sym`, `--cosat`, `--lex`,
  `--full`, `--solver kissat404|cadical195`); prefix JSON files may carry case constraints (`fix`).
* `relabel.py`: window-minimizing relabeling. `symlabel.py`: random self-dual labelings.
* `layer4.py`: annealing for good next layers. `symbeam.py`: Wang-style self-dual beam.
* `cases_e18_3.py`: the 26-case split. `conquer.py`: runs many prefixes in parallel with timeouts.
* `status.sh`: one-screen summary of the runs. `pause.sh`: freezes them; `./pause.sh resume` continues.
* `logs/`, `results/`, `prefixes/`: run logs, outcomes (JSON lines), generated prefixes.

Run with the python-sat venv of `depth-hand-proofs/verify`:

```bash
../depth-hand-proofs/verify/.venv/bin/python netsat.py --prefix e18_4 --depth 10 --full --solver kissat404
```
