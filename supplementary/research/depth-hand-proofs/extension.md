# Extending the infinity method: a transfer theorem, a barrier, and a SAT experiment

**Status (2026-11-14, America/Los_Angeles).** This continuation does **not**
resolve whether $D(18)=10$ or $11$. The current [Dobbelaere
table](https://bertdobbelaere.github.io/sorting_networks.html) still lists
$10\le D(18)\le11$. No new exact value of $D(n)$ is claimed here.

What is established below:

* A hand proof generalizes both the two-layer blinding recurrence and the
  two-sentinel reduction to **any number of sentinels**.
* A hand proof shows that using only the resulting two first-layer size caps
  can never improve the even-size bound $D(2p)\ge D(2p-1)$. In particular,
  that entire family of reductions cannot prove $D(18)\ge11$.
* A new SAT relaxation combines the constraints from different infinity
  placements on the **same** proposed network. It reproduces the bounds at
  $5,7,9,11$, but bounded runs at $13$ and $18$ are inconclusive.
* The existing recurrence is propagated with explicit proof dependencies,
  separating hand proofs, the local H9 computation, and published base cases.
  These numerical consequences were already implicit in README §7; they
  are not new lower bounds discovered by the SAT experiment.

The constructions use Tools A–C of [README.md](README.md), including
untangling. No middle-layer maximality is assumed.

The subsequent [coupled restriction theorems](../d18-search/structural-frontier.md)
retain information discarded by the cap barrier: an exact path/cycle
factorization, a distinction for widths congruent to two modulo four, and
constraints linking the retained comparator counts in every suffix layer.
They also prove a limit on universal third-layer blinding for every even
width at least 18. They do not yet settle D(18).

## 1. A general two-layer transfer theorem

Write $p=\lfloor n/2\rfloor$. Suppose an $n$-channel sorting network has
$d\ge2$ layers. For every integer $0\le k\le p$, there is an $(n-k)$-channel
sorting network of the same depth, allowing empty layers, whose first two
layers each contain at most $p-k$ comparators.

More precisely, after making the original first layer maximal, the two
retained layer sizes can be chosen to be

$$p-k,\qquad \max(0,|L_2|-k).$$

**Proof.** Apply the bipartite-coloring construction of README Lemma 1 to
$L_1\cup L_2$. It gives a set $X$ of exactly $p$ vertices, containing exactly
one endpoint of every edge of either layer, and excluding the possibly idle
vertex of $L_1$.

Exactly $|L_2|$ vertices of $X$ are used by $L_2$, one per comparator. Choose
$k$ vertices of $X$, taking used vertices first. Thus the chosen vertices
meet exactly $\min(k,|L_2|)$ distinct second-layer comparators and exactly
$k$ distinct first-layer comparators.

On a chosen vertex put $-\infty$ if it is the lower endpoint of its
first-layer comparator, and $+\infty$ if it is the upper endpoint. Every
sentinel stays in place in the first layer. Every other input is an
arbitrary real. Hence the numbers of real-real comparators in the first
two layers are exactly the two displayed quantities. Prune the sentinels
and untangle by Tool C. This preserves the layer sizes and gives the
claimed smaller sorter. $\square$

The signs need not include both $+\infty$ and $-\infty$: Tool C permits
any fixed mixture, including only one sign. This is why no counting of
ordered opposite-sign pairs is needed here.

Let $T(r,a)$ be the minimum depth of an $r$-channel sorter whose first two
layers have at most $a$ comparators each. Layers may be empty; depth is at
least two in this definition. For $r\ge3$ this convention causes no issue.
The theorem gives, for $n\ge3$ and nontrivial retained sizes,

$$D(n)\ge T\bigl(n-k,\lfloor n/2\rfloor-k\bigr).$$

Three useful specializations:

* $k=p$: remove the first two empty layers and obtain
  $D(n)\ge D(\lceil n/2\rceil)+2$.
* $n=7,k=2$: obtain a 5-channel network with caps $(1,1)$, so README
  Lemma 3 gives $D(7)\ge6$.
* $n=11,k=2$: obtain a 9-channel network with caps $(3,3)$, so H9 gives
  $D(11)\ge8$. H9 remains computer-assisted; this shorter reduction does
  not make its proof a hand proof.

`verify/profile_transfer.py` constructs the placements and checks the
exact two layer counts for **289,420** pairs of a second-layer matching
and a sentinel count, over all matchings for $3\le n\le11$. This is a
check of the proof, not a substitute for it.

## 2. Why these cap reductions cannot settle D(18)

**Even-size barrier.** For $p\ge3$, consider every nontrivial bound obtained
from §1 on $2p$ channels, keeping only the retained channel count and the
two first-layer caps. Their maximum is exactly $D(2p-1)$:

$$\max_{p\le r\le 2p-1}T(r,r-p)=D(2p-1).$$

**Proof.** At even width $2p$, putting $r=2p-k$ makes the cap $r-p$.
For every $p\le r\le2p-2$, apply the same transfer theorem instead to an
optimal sorter on $2p-1$ channels, with $k'=2p-1-r$. Its first-layer
matching has $p-1$ edges, and its retained cap is

$$(p-1)-k'=r-p.$$

Consequently an actual depth-$D(2p-1)$ sorter exists for **each** of these
retained shapes, so $T(r,r-p)\le D(2p-1)$. The remaining case $r=2p-1$
has cap $p-1$, the maximum possible matching size. It imposes no restriction
and has $T(2p-1,p-1)=D(2p-1)$. This proves the equality. $\square$

For 18 channels, the retained shapes are $(r,a)=(9,0),(10,1),\ldots,(17,8)$.
Every one is realized at depth at most 10 because $D(17)=10$. Thus proving
more impossibility lemmas about **these two caps alone** cannot yield 11.
This is a limitation of the specified reduction family, not of all sentinel
arguments, all hand proofs, or all SAT methods.

In particular, one must retain more information: later layers, the identity
and interaction of the retained subnetworks, or output dependence. The
simultaneous experiment in §4 retains the common large network and all its
layers, so the barrier does not apply to it.

## 3. Larger-n bounds, with their dependencies exposed

Iteration of the proved recurrence gives the exact integer implication

$$D(m)\ge b\quad\Longrightarrow\quad
  D\bigl(2^k(m-1)+1\bigr)\ge b+2k\qquad(m\ge3,\ k\ge0).$$

**Proof.** The case $k=0$ is the hypothesis. For $k\ge1$,
$\lceil(2^k(m-1)+1)/2\rceil=2^{k-1}(m-1)+1$. Apply the recurrence and
induction. Monotonicity extends the bound to every larger $n$. $\square$

For example, the hand proofs of $D(7)\ge6$ and $D(9)\ge7$ give two infinite
families without SAT:

$$D(6\cdot2^k+1)\ge6+2k,\qquad
  D(8\cdot2^k+1)\ge7+2k.$$

The following are lower bounds, not claims of optimality:

| channels | hand bases through 9 | also local H9 / D(11)≥8 | also published D(13)≥9, D(17)≥10 |
|---|---:|---:|---:|
| 18–20 | 9 | 9 | 10 |
| 21–24 | 9 | 10 | 10 |
| 25–32 | 10 | 10 | 11 |
| 33–40 | 11 | 11 | 12 |
| 41–48 | 11 | 12 | 12 |
| 49–64 | 12 | 12 | 13 |
| 65–80 | 13 | 13 | 14 |
| 81–96 | 13 | 14 | 14 |
| 97–128 | 14 | 14 | 15 |

`verify/bound_closure.py` computes the exact closure of these seed facts
under monotonicity and the recurrence. `results/bound-closure.json` records
the rule and parent for every entry. Published seeds are clearly separate
from the hand-only and local-computation seeds.

For the published depth seeds see [Bundala et al., Optimal-Depth Sorting
Networks](https://arxiv.org/abs/1412.5302) and [Codish et al., Sorting
Networks: To the End and Back Again](https://arxiv.org/abs/1507.01428).
No novelty claim relative to the wider literature is made for this closure.

## 4. A simultaneous restriction SAT relaxation

`verify/sentinel_cegar.py` has two roles:

1. A **master** chooses a candidate $n$-channel, $d$-layer comparator network.
   It fixes a maximal first layer and allows arbitrary matchings thereafter.
   The last layer may be restricted to adjacent comparators, by h9.md Lemma 6.
2. An **adversary** searches symbolically over every assignment of signed
   infinities with a specified number $r$ of reals. It finds a placement whose
   retained network violates a known small-network fact. The master then
   receives the necessary condition for that particular placement.

The conditions are:

* at least $D(r)$ nonempty retained layers;
* for five reals in exactly five nonempty layers, the first two cannot both
  have one comparator (README Lemma 3);
* for seven reals in exactly six nonempty layers, the first must have at least
  two comparators (P7, h9.md §7.5);
* optionally H9: for nine reals in exactly seven nonempty layers, the first
  two cannot both have at most three comparators;
* optionally the published size bounds $S(r)$, counted across all retained
  comparators.

The master uses two threshold bits per wire to encode the ordered types
$-\infty<\mathrm{real}<+\infty$. Conditional AND/OR equivalences propagate
both thresholds, and idle channels copy their values. A comparator is
counted exactly when both incoming types are real. The actual values and
ordering of the reals are unnecessary for these counts.

With `--no-repeat`, an immediately repeated comparator is excluded: its
second occurrence never swaps and can be deleted. No other middle-layer
completion or maximality is assumed. `--sizes` uses literature inputs,
including computer-assisted size bounds; it is not a hand-only option.

**Why an UNSAT answer is sound.** Every sorter has the selected normal form.
For every fixed sentinel placement, Tool C makes its retained comparators
into a smaller sorting network with the same layer counts. Thus it satisfies
every added condition, regardless of how the placements were discovered.
If the finite conjunction is UNSAT, no original sorter exists. Adversary
search affects which conditions are added, not their validity.

**Why other answers are weaker.** A `SURVIVOR` passes only the selected
necessary conditions. It is checked separately on binary inputs before any
sorting claim. `TIME_LIMIT`, `INTERRUPTED`, and `ITERATION_LIMIT` prove
nothing about the requested bound. A saved `last_candidate` need not satisfy
the newest restrictions. The transcripts contain no depth-10 sorter on 18
channels and no refutation of that full problem.

### Completed experiments

Discovery times below refer to the original runs; the JSON records the
restriction list, so discovery need not be repeated. The later version
groups leak indicators by lower endpoint to reduce cardinality-encoding size.

| target excluded | restrictions | result | discovery time | dependencies |
|---|---:|---|---:|---|
| 5 channels, depth 4 | 4 | UNSAT | 0.014 s | hand facts |
| 7 channels, depth 5 | 12 | UNSAT | 0.091 s | hand facts including Lemma 3 |
| 9 channels, depth 6 | 42 | UNSAT | 11.879 s | hand facts |
| 11 channels, depth 7 | 17 | UNSAT | 1.065 s | hand facts plus H9 |

The saved 9- and 11-channel conjunctions were independently refuted with
Glucose 4.1 as well as CaDiCaL 1.9.5. These are solver-based computations,
not independently checked DRAT/LRAT certificates. The JSON transcripts
are reproducibility artifacts, not a claim of formal proof checking.

| larger attempt | result |
|---|---|
| 13 channels, depth 8, depth/profile facts | interrupted during master solving; inconclusive |
| 18 channels, depth 10, depth/profile facts | interrupted during master solving; inconclusive |
| 13 channels, depth 8, also size facts and no immediate repetitions | TIME_LIMIT after about 301 s; 45 restrictions |
| 18 channels, depth 10, also size facts and no immediate repetitions | TIME_LIMIT after about 301 s; 35 restrictions |

The last two limits include elapsed time between conflict-budget chunks.
They do not suggest that a proof is close, or that the relaxation is strong
enough: either an eventual refutation or a nonsorting survivor is possible.

### Validation

`verify/sentinel_validate.py` checks:

* 8,712 profile-property cases, including empty layers and optional size facts;
* 7,560 fixed-network/placement cases, comparing master satisfiability with
  direct ternary simulation;
* 300 network/retained-size/option cases, comparing the adversary against
  exhaustive signed-placement enumeration;
* a positive control: a verified 9-channel sorter survives every adversary
  for $r=3,5,7$, with and without size facts, and satisfies 20 master rows.

The positive control is an independently found 8-layer sorter with first
two layer sizes $(2,2)$, recorded in `results/profile-9-2-8.json` and checked
on all 512 binary inputs. Its existence also follows without search: split
the four disjoint first-layer comparators of any depth-7 9-sorter into two
layers of two comparators each.

### Reproduction

Run from the repository root:

```bash
sh depth-hand-proofs/verify/verify_extension.sh
# Or run the individual components:
python3 depth-hand-proofs/verify/profile_transfer.py
python3 depth-hand-proofs/verify/bound_closure.py --limit 128
depth-hand-proofs/verify/.venv/bin/python depth-hand-proofs/verify/sentinel_validate.py
depth-hand-proofs/verify/.venv/bin/python depth-hand-proofs/verify/sentinel_cegar.py \
  --replay depth-hand-proofs/results/sentinel-d11-d7.json \
  --out /tmp/sentinel-replay.json --seconds 120
depth-hand-proofs/verify/.venv/bin/python depth-hand-proofs/verify/sentinel_cegar.py \
  18 10 --bases known --h9 --sizes --no-repeat --seconds 300 \
  --out /tmp/sentinel-18.json
```

`--first a` changes the scope to a sparse-first-layer lemma, rather than a
full $D(n)$ claim. `--dimacs PATH` exports the exact master conjunction and
records its SHA-256. Replay may use another budget-capable PySAT solver,
for example `--solver glucose41`. No run continues in the background after
the bounded experiments have been collected.

## 5. The remaining two-cap target for D(13)

The general theorem also identifies a case missed by testing H11 alone:

> **H12:** No 8-layer sorter on 12 channels has at most five comparators
> in each of its first two layers.

If H12 holds, the transfer with $n=13,k=1$ proves $D(13)\ge9$.
In fact H12 is the **only** remaining way to get 9 from the individual
two-cap reductions of §1 at $n=13$:

| sentinels k | retained shape (r,a) | an 8-layer sorter exists? |
|---:|---|---|
| 1 | (12,5) | unresolved in these runs |
| 2 | (11,4) | yes: the H11 counterexample in h9.md §9 |
| 3 | (10,3) | yes: split the first layer of a depth-7 10-sorter into parts of size at most 3 |
| 4 | (9,2) | yes: split the first layer of a depth-7 9-sorter into parts of size at most 2 |
| 5 | (8,1) | yes: prepend two empty layers to a depth-6 8-sorter |
| 6 | (7,0) | yes: prepend two empty layers to a depth-6 7-sorter |

Splitting a layer is safe here because its comparators are disjoint; the
composition does not change. Empty layers are allowed in $T$.
Also $8\le T(12,5)\le9$: the lower bound is $D(12)=8$, and splitting the
first layer of an 8-layer 12-sorter gives the upper bound.

`verify/profile_sat.py` encodes these capped problems exactly, independently
of the sentinel relaxation. Its default `exact` encoder is `satnet.py`.
Its `windows` option reuses the validated encoder in `../d18-search/netsat.py`,
including its stated last/penultimate-layer normal forms, while adding only
the second-layer cardinality cap. Immediately repeated or other redundant
comparators can be deleted without increasing either cap.

Calibration: $(r,a,d)=(6,2,5)$ and $(8,3,6)$ are UNSAT; $(9,2,8)$ is SAT
with a witness verified on all 512 inputs. The two encoders agree on the
8- and 9-channel cases. All three unrestricted H12 attempts were inconclusive:

| encoder / solver | result | elapsed |
|---|---|---:|
| exact / CaDiCaL 1.9.5 | TIME_LIMIT | 303.833 s |
| windows / CaDiCaL 1.9.5 | TIME_LIMIT | 321.644 s |
| windows / Kissat 4.0.4, single call | TIME_LIMIT | 180.027 s |

The first two used the original conflict-budget timing; the current capped
runner enforces its limit in a parent process. None of these runs refutes
H12 or gives a counterexample to it. Records are in
`results/profile-12-5-8*.json`.

Example command:

```bash
depth-hand-proofs/verify/.venv/bin/python depth-hand-proofs/verify/profile_sat.py \
  12 5 8 --encoder windows --seconds 300 --out /tmp/h12.json
```

The capped-profile script uses a single solver call in a subprocess with a
wall-clock timeout, including preprocessing. This also works with Kissat,
which cannot resume a solve. The simultaneous CEGAR master instead uses
conflict-budget checkpoints and rejects Kissat because it needs incremental
solving.

## 6. What remains

To resolve $D(18)$ one still needs either a depth-10 construction or an
exclusion of every depth-10 network. The earlier Green-prefix exclusions
in `../d18-search/` do not provide that coverage. The simultaneous master
does cover every network under its valid normal forms, but has not been
refuted. A complete two-layer prefix cover followed by SAT is another
valid route; none is asserted to have been completed here.

For further hand work, the useful distinction is between a single smaller
network's layer counts and how **several** restrictions must coexist inside
the original network. Section 2 rules out the former for the desired even
case. Any successful continuation must go beyond that specific information.
