# Proving $D(11)\ge8$, strategy C: how fast an image can shrink

Companion to `depth-lower-bounds-small-n.md` (toolbox T1–T11 numbered there). **See `d11-handoff.md`
first** for the overview. This document is one of three attempts; the others are
`d11-block-lemma-route.md` and `d11-image-size-route.md`.

**Status: the first step is a theorem, the general step is not, and the reason is identified.** The
two-layer minimum is proved for every $n\le12$; beyond the first step the product structure that makes the
proof work is destroyed after $\lceil\lg n\rceil$ layers, and that is exactly where the frontier sits.

---

## 1. The factorization theorems

Write $L_M$ for the map "sort each pair of $M$" and $\mathrm{Fix}(M)=\{v: v_a\le v_b\ \forall(a,b)\in M\}$
for its image. Then $\mathrm{image}(L_1)=V(M_1)=\mathrm{Fix}(M_1)$, of size $3^{e}2$ on $n$ channels
($e=\lfloor n/2\rfloor$).

### 1.1 Theorem F: the first step factors over components

> **Theorem F.** Let $M_*,M$ be matchings and $C_1,\dots,C_p$ the connected components of $M_*\cup M$. Then
> $$\bigl|L_M(\mathrm{Fix}(M_*))\bigr|=\prod_{i=1}^p\bigl|L_{M|_{C_i}}(\mathrm{Fix}(M_*|_{C_i}))\bigr|.$$

*Proof.* $\mathrm{Fix}(M_*)=\prod_i\mathrm{Fix}(M_*|_{C_i})$: the constraints are per pair of $M_*$, and each
pair lies inside one component. Each comparator of $M$ has both ends in one component, so $L_M$ acts
componentwise. The image of a product under a product map is the product of the images. $\square$

Verified on 3 000 random pairs at $n=9$, 0 mismatches.

Two component shapes occur: an alternating **cycle** with $k$ edges of each matching, or — for odd $n$ when
the two idle channels differ — a single alternating **path** with $j$ edges of each, whose endpoints are the
idle channels. So the two-layer minimum is a **minimum over tilings of $[n]$ by local patterns**.

### 1.2 Theorem F′, one level up: it survives every layer, by coarsening

> **Theorem F′.** Let $F=\prod_iA_i$ be a product over a partition $P$ of $[n]$, and $M$ a matching. Join two
> blocks of $P$ when some pair of $M$ has one end in each; call the result the *cluster partition*. Then
> $$\bigl|L_M(F)\bigr|=\prod_{\text{clusters }\kappa}\Bigl|L_{M|_\kappa}\Bigl(\prod_{i\in\kappa}A_i\Bigr)\Bigr|.$$

*Proof.* $L_M$'s image is determined by the sorted content of each pair of $M$: pairs inside a block depend
on that block alone, straddling pairs on those two blocks. Since $M$ is a matching its pairs are disjoint, so
the coordinate map factors over the clusters. $\square$

Verified on 400 random three-layer chains at $n=9$: 0 mismatches. (A first version of that check reported
211 mismatches; the harness built a union where the product needs all combinations. Worth recording because
the same slip would make anyone think the theorem false.)

So the image after every layer is a product over the cluster partition, and the compression is a product of
local ratios. The chain is a DP whose state is (a partition of $[n]$; for each block a set of states).

### 1.3 The coarsening rate, which is the real limit

Blocks at most double per layer — each can merge with one other through a matching — so a block has size
$\le2^t$ after $t$ layers and the partition is **trivial after $\lceil\lg n\rceil$ layers**. Measured on the
brick chain at $n=11$:

| after layer | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| blocks | 11×1 | 2,2,2,2,2,1 | 4,4,3 | 8,3 | **11** | 11 | 11 |

The product structure is live for exactly the first four of the six steps. The last three must be bounded
with a single block — no structure at all. That is the precise form of the obstruction, and it replaces the
vague claim (made and corrected during this work) that the partitions "do not nest".

---

## 2. The local ratios, and the closed form for the two-layer minimum

### 2.1 The local ratios, exactly

Minimum local ratio over all connected patterns of each size, by complete enumeration of connected
matching-pairs (`rho5.c`, verified against the smaller cases; `rho6.c` for the sampled value):

| cycles: $2k$ channels | $\rho_k$ | paths: $2j+1$ channels | $\rho'_j$ |
|---|---|---|---|
| 2 | $1$ | 3 | $5/6$ |
| 4 | $\mathbf{2/3}=6/9$ | 5 | $13/18$ |
| 6 | $2/3=18/27$ | 7 | $17/27$ |
| 8 | $46/81=0.5679$ | | |
| 10 | $123/243=0.5062$ | | |

Three features. The 4-cycle (the *crossing* pattern: $M_*$ pairs $(1,2),(3,4)$, $M$ pairs $(1,3),(2,4)$)
gives $2/3$, and **every** 6-channel pattern — all $120$ — gives the same $2/3$. The path profile counts are
$5,13,34=F_5,F_7,F_9$, so $\rho'_j=F_{2j+3}/(2\cdot3^j)$. And $\rho_k$ **decreases**: $0.667,0.667,0.568,
0.506$ — so "a large component cannot beat a 4-cycle" is false component-wise; what survives is the
comparison against a *packing*.

### 2.2 The tiling formula and the closed form

$$\min_M\bigl|L_M(\mathrm{Fix}(M_*))\bigr|=|F_1|\cdot\min_{\text{tilings}}\prod\rho,\qquad
\boxed{\ \min|F_2|=|F_1|\cdot\Bigl(\tfrac23\Bigr)^{\lfloor e/2\rfloor}\cdot\Bigl(\tfrac56\Bigr)^{[\,e\text{ odd and }n\text{ odd}\,]}\ }$$

the $5/6$ exponent recording that for odd $n$ one pair is best spent on the alternating path rather than on a
2-cycle. Pack crossing 4-cycles; when $n$ is odd pay one path factor. That is the structural content of the
"brick" pattern, and it explains why the brick is optimal at the first step.

### 2.3 What is proved

The closed form is **proved for every $n\le12$**, by exhaustive lower bound plus explicit attaining
construction:

| $n$ | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|
| $\min\lvert F_2\rvert$ | 12 | 18 | 30 | 36 | 72 | 108 | 180 | 216 |

The $n=12$ case needs $\bigl|L_{M_2}(\mathrm{Fix}(M_1))\bigr|\ge216$ for every pair of perfect matchings on
12 channels ($729\cdot(2/3)^3=216$), which is a lower bound and so cannot be sampled: it was settled by
exhaustive verification over all $10\,395^2=1.08\times10^{8}$ pairs (`k6verify.c`), with an early exit the
moment a count reaches 216 so that only genuine failures are fully counted — **zero failures**. The bound is
attained by three crossing 4-cycles. The same program confirms the bounds at $n=8$ (36) and $n=10$ (108). A
first version of the $k=6$ statement was only *sampled*, which gave an upper bound ($\rho_6\le0.440$) and
proved nothing; the exhaustive check supplies the lower bound.

Beyond $n=12$ the enumeration is $4.1\times10^{12}$ pairs at $n=14$, out of reach by this method.

---

## 3. The greedy chains, and the two-lemma split

### 3.1 The descents

Starting from the *brick* pair (layer 1 adjacent, layer 2 the crossing matching) and then at each step
choosing the layer minimising the image size gives a valid $t$-layer network at every stage, so these values
are *upper* bounds on $\min|F_t|$; they are attained by the known optimal networks in several cases and are
believed optimal:

| $n$ | $|F_1|,|F_2|,\dots$ |
|---|---|
| 5 | 18, 12, 9, 8, 6 |
| 7 | 54, 30, 19, 13, 10, 8 |
| 9 | 162, 72, 40, 26, 20, 14 |
| 11 | 486, 180, 80, 50, 33, **23** |
| 13 | 1 458, 432, 180, 102, 63, 38, 26, 20 |
| 15 (sampled) | 4 374, 1 080, 479, 253, 154, 95, 60, 43 |
| 17 (sampled) | 13 122, 3 204, 1 242, 608, 332, 204, 129, 90, 62 |

The chain was verified **exact** at every step where an exhaustive check was possible — twelve independent
exact values: $t=2$ at $n=5,7,9,11$; $t=3$ at $n=5,6,7,9$; $t=4$ at $n=5,7$. Exactness beyond that is out of
reach: the number of *distinct* image sets explodes (105, 3341, 76 867 at $n=7$; 945, 209 777, not completed
at $n=9$), so $t=4$ at $n=9$ needs $\approx10^{10}$ image operations.

### 3.2 Lemma 1 (early steps, local packing): holds, one inequality open

The single gap in §2's closed form for general $n$ is: *no connected pattern compresses more than the best
packing of the same total size*, i.e. $\rho_k\ge(2/3)^{\lfloor k/2\rfloor}$.

| $k$ | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|
| $\rho_k$ | $2/3$ | $2/3$ | $0.568$ | $0.506$ | $\le0.440$ |
| packing bound | $2/3$ | $2/3$ | $0.444$ | $0.444$ | $0.296$ |
| room | $0$ | $0$ | $0.124$ | $0.062$ | $\ge0.144$ |

Rigorous for $k\le6$; equality at $k=2,3$ (4-cycles and 6-cycles exactly tied), and the room grows because
$\rho_k$ decays like $\sim0.87^k$ against the packing's $0.816^k$. So the inequality is tightest where it is
finite and checked, and easiest in the limit.

**Its sharpest form is a growth statement.** With $I_k$ the image size of a connected pattern on $2k$
channels, the bound is equivalent to $I_k\ge\sqrt6\,I_{k-1}$ (since $I_2=6$ and
$\sqrt6^{\,k-2}\cdot6=6^{k/2}$):

| $k$ | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|
| $I_k$ | 6 | 18 | 46 | 123 | $\le321$ |
| $I_k/I_{k-1}$ | — | 3.000 | 2.556 | 2.674 | 2.610 |
| margin over $\sqrt6=2.449$ | — | 1.22 | 1.04 | 1.09 | 1.07 |

A per-cell factor near $2.6$ against a requirement of $2.45$: real but thin, and thin in a way that defeats
both obvious arguments.

* **Splitting goes the wrong way.** Deleting a comparator only *enlarges* the image, so a connected pattern
  can be compared to a split one only as $I_{\text{connected}}\le I_{\text{split}}$. Any induction on $k$ by
  removing an alternating cell gives an *upper* bound — useless here.
* **Integrality is not enough.** The projection $I_k\to I_{k-1}$ has average fibre $I_k/I_{k-1}$, so the
  needed statement is "average fibre $\ge2.449$"; surjectivity gives $\ge1$ and proving no fibre is a
  singleton gives $\ge2$. Neither reaches $2.449$.

So the missing lemma is a genuine **lower bound on per-cell growth for a 1-dimensional cyclic structure** —
the same "average, not maximum" phenomenon as the size route, but now translation-invariant and
one-dimensional, which is the most tractable form this problem has taken.

### 3.3 Lemma 2 (last steps, single block): unavailable

The last $d-\lceil\lg n\rceil$ steps have no product structure, so they need a bound on $|L_M(F)|$ for a
single-block $F$. The per-weight (max-fiber) certificate fails by a factor of three per step: with the actual
profile at $n=11$ it gives $\approx5.6$ against a need of $\ge18$, and it is saturated (per-weight ratios
down to $0.405$ at $k=6$). No size certificate exists — that is the content of
`d11-image-size-route.md` §3.1.

### 3.4 Net position

| layer range | what is available |
|---|---|
| $1..\lceil\lg n\rceil$ | Lemma 1: exact local ratios, closed-form minimum proved to $n=12$, one finite inequality open |
| $\lceil\lg n\rceil+1..d-1$ | nothing: no product structure, no size certificate, no per-weight bound |

For $n=11$, $d=7$ that is four steps with product structure, of which only the first (the two-layer
minimum) is settled exactly, and three without. Lemma S needs $|F_6|\ge18$ for every network, and the
smallest $|F_6|$ found is 23. The
split halves the problem precisely — six steps to three — and locates the difficulty: it is not the early
mixing, which is now understood, but the final collapse, where the image has full support and the useful
datum is its *position* among the $\binom{2048}{\le33}$ possible sets. That is (R) again, in its smallest
form. The split's contribution is to explain why the computation must be done on the last three layers
rather than on all six.

---

## 4. Reproducibility

Scripts are in `code/`, with a per-script table in `code/README.md`: `cycletype.py` (local ratios on cycles
and paths), `rho5.c`, `rho6.c` (exact and sampled connected minima), `k6verify.c` (the exhaustive $n=12$
lower bound), `cluster.py` (Theorem F′, and the harness bug), `chain.c`, `chain2.c`, `chain3.c` (the
descents — exhaustive, brick-started, sampled), `twolayer.c`, `exact3.c`, `exact4.c`, `minimage.py`,
`dedup.c`. `code/verify.sh` re-runs every cheap check in about a minute.
