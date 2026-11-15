# Proving $D(11)\ge8$, strategy B: image size and what would have to shrink

Companion to `depth-lower-bounds-small-n.md` (toolbox items T1–T11 are numbered there). **See
`d11-handoff.md` first** for the overview. This document is one of three attempts; the others are
`d11-block-lemma-route.md` and `d11-compression-structure.md`.

**Status: no proof of $D(11)\ge8$, but three of the small bounds are proved by this route, and four
relaxations of the frontier are shown to be vacuous.** The document is organised as: the lemma (§1), what
it proves exactly (§2), what it cannot do and why (§3), how far the machinery reaches at all (§4), and which
properties actually shrink an instance (§5).

---

## 1. Lemma S: ruling out a depth by a minimal image

Let $F_t=L_t\cdots L_1(B^n)$ be the image of the first $t$ layers. For an adjacent last layer $M$ the flip
states are explicit: $\sigma^w$ reads $01$ on a pair of $M$ iff the pair straddles the boundary between its
$0$s and its $1$s, so

$$A'(M)=S\cup\{s_w:\ w\ \text{a weight whose boundary pair is in }M\},\qquad s_w=0^{\,n-w-1}10\,1^{\,w-1},$$

and $\bigl|A'(M)\bigr|=\sum_w2^{c_w}\le c_n$, where $c_n=(3n+1)/2$ for odd $n$ and $3n/2+1$ for even.

> **Lemma S.** Let $n\ge3$, $d\ge2$. Suppose every $(d-1)$-layer maximal-layer network on $n$ channels has
> $|F_{d-1}|>c_n$. Then $D(n)>d$.

*Proof.* Suppose $N$ sorts in $d$ layers. Delete redundant comparators: by [1507.01428] Lemma 3 the result
still sorts in $d$ layers and is non-redundant, so by C1 every comparator of its last layer $M_d$ is
adjacent. Now **add** comparators to layers $1..d-1$ until each is a maximal matching: by T3 this preserves
sorting and does not touch $M_d$, so $M_d$ stays adjacent. The first $d-1$ layers are now a maximal-layer
network, so $|F_{d-1}|>c_n$; but $F_{d-1}\subseteq A'(M_d)$ and $|A'(M_d)|\le c_n$. Contradiction. $\square$

The two normal forms — non-redundance (to force adjacency) and maximality (for the image bound) — are used
**sequentially**, on different layers. That is the one place where the compatibility problem of
`d11-block-lemma-route.md` §1 resolves in favour of both.

**Read Lemma S as a tiling statement.** A $d$-layer sorter needs the image of $d-1$ layers to fit into $A'$,
a set of about $1.5n$ states. So the size route asks: *how small can the image of a $t$-layer network be?*
That is the quantity studied in `d11-compression-structure.md`; this document records what it buys and where
it stops.

---

## 2. What it proves exactly

### 2.1 The exact two-layer minima

$\min|F_2|$ over all pairs of maximal layers, computed exhaustively (`twolayer.c`), with rigorous lower
bounds for $n\le12$ (`k6verify.c`, which for each $n$ checks that no pair falls below the stated bound, with
an early exit so only genuine failures are fully counted):

| $n$ | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|
| $\lvert F_1\rvert=3^{e}2^{[n\text{ odd}]}$ | 18 | 27 | 54 | 81 | 162 | 243 | 486 | 729 |
| $\min\lvert F_2\rvert$ | 12 | 18 | 30 | 36 | 72 | 108 | 180 | 216 |
| ratio | $2/3$ | $2/3$ | $5/9$ | $4/9$ | $4/9$ | $4/9$ | $10/27$ | $8/27$ |

The structure behind these values — which component patterns attain them, and why — is
`d11-compression-structure.md` §§1–2. For the present document the point is that the first step of the
chain is **settled**, and that $486\cdot10/27=180$ is the exact value at the frontier.

The $n=12$ case was settled by a $1.08\times10^8$-pair exhaustive check that no pair of perfect matchings on
12 channels has image below $216=729\cdot(2/3)^3$: **zero failures**. Beyond $n=12$ the enumeration is
$4\times10^{12}$ pairs at $n=14$, out of reach.

### 2.2 Small bounds from the route

Exhaustive minimal-image computations give $D(5)\ge5$, $D(6)\ge5$, $D(7)\ge6$ with no use of capacity, of
$S(n)$, or of any SAT solver (`exact3.c`, `exact4.c`). The exact values, with the chain values they match
(the chains are in `d11-compression-structure.md` §3.1):

| $n$ | $d=D(n)-1$ | needed: $\min\lvert F_{d-1}\rvert>c_n$ | smallest found | margin |
|---|---|---|---|---|
| 5 | 4 | $>8$ | 9 | +1 |
| 6 | 4 | $>10$ | 11 | +1 |
| 7 | 5 | $>11$ | 13 | +2 |
| 9 | 6 | $>14$ | 20 | +6 |
| 11 | 7 | $>17$ | 23 | +6 |
| 13 | 8 | $>20$ | 26 | +6 |
| 15 | 8 | $>23$ | 60 | +37 |
| 17 | 9 | $>26$ | 90 | +64 |

The first three rows are exact (full enumeration over $15^3$, $15^3$ and $105^4$ layer sequences). The rest
come from the greedy descending chain, whose optimality is **not** proved; it was checked to be exact at
every step where an exhaustive check was possible ($t=2$ for $n=5,7,9,11$; $t=3$ for $n=5,6,7,9$; $t=4$ for
$n=5,7$ — twelve independent exact values, all matching). So every row from $n=9$ on is an upper bound on the
minimum, not a proved value; rows $n=15,17$ come from a *sampled* descent.

**The margins grow** — $1,1,2,6,6,6,37,64$ — because $|F_{d-1}|$ is a constant fraction of
$3^{\lfloor n/2\rfloor}2$, exponential, while $c_n$ is linear. So the small cases are the hard ones and the
large ones would follow from any crude bound. For $n=11$ the requirement is $\min|F_6|>17$ and four
independent constructions all reach exactly $23$ and none goes lower: 11_d8's own prefix, two hill climbs,
and the brick descent.

---

## 3. The four relaxations that cannot work

Each was a natural first attempt; each is now a proved *satisfiability* result, so no argument confined to
it can prove the bound.

### 3.1 The size certificate is the largest fiber, and the largest fiber is not the average

$L_M$ preserves weight and its fibers are indexed by pair-contents, so the only certificate depending on the
pair of matchings alone is

$$\Phi(M_*,M)=\max_{u}\#\{v\in\mathrm{Fix}(M_*):L_M(v)=u\},$$

giving $|L_M(F)|\ge|F|/\Phi$. At $n=11$, for the pair the optimal chain uses:

| | value |
|---|---|
| $\lvert\mathrm{Fix}(M_*)\rvert$ | 486 |
| $\lvert L_M(\mathrm{Fix}(M_*))\rvert$ | 233 |
| achieved average fiber | **2.086** |
| $\Phi$ (largest fiber) | **13** |

The factor-6 gap compounds: the true product of averages over five layers is
$2.70\cdot2.25\cdot1.60\cdot1.52\cdot1.44\approx21$, while the product of certificates is $\ge13^5$. The
bound $|F_6|\ge486/13^5<1$ is worthless.

* **No uniform constant exists either**: taking $F$ to be a single full fiber gives ratio $2^{-c}$, down to
  $2^{-\lfloor n/2\rfloor}$.
* **Per-weight decomposition fails too**: $L_M$ preserves weight, but the actual weight profile of $F_6$ at
  $n=11$ is $[1,1,2,3,4,4,6,5,3,2,1,1]$, and the per-weight certificate then gives
  $$\sum_w \frac{|F\cap\mathrm{wt}_w|}{2^{\min(w,n-w,e)}}\approx5.6\qquad\text{against a need of } \ge18.$$
  It is *saturated*: the measured per-weight ratios fall to $0.405$ at $k=6$, so no per-weight constant of
  the shape $1/2$ survives either.
* **The hybrid using $S\subseteq F$ adds nothing**: bounding the excess in the $n+1$ sorted fibers returns
  exactly $|F|/\Phi$ again.

The conclusion is the sharpest statement in this project's work on $n=11$: **the image is not merely small,
it is spread** — the useful datum is which fibers $F$ occupies, not how many states it has.

### 3.2 Where the image could in principle be squeezed

For the record, the ceiling really is small: $A'$ has $\sum_w2^{c_w}$ states, equal to $(3n+1)/2$ for an
adjacent maximal last layer — $17$ at $n=11$, of which $12$ are sorted and $5$ are the explicit vectors
$s_w$. So the frontier asks whether a 6-layer network's image can be a subset of those $17$ states. §3.1
says no size argument can answer that.

### 3.3 Lattice closure is satisfiable

Comparators are **not** lattice homomorphisms: network images are not sublattices in general (375 of 3000
random networks fail closure under $\wedge$ or $\vee$). But the target sets are: $S\cup\{s_w\}$ **is** a
sublattice of the Boolean lattice for every adjacent last layer and every single flip state. So "the image
is a sublattice containing $S$ and inside $A'$" is satisfiable at the frontier, and closure arguments cannot
rule out the minimal case $|F_{d-1}|=n+2$.

### 3.4 The two that come from the other strategy

Routing/counting and order-theoretic relaxations are ruled out in `d11-block-lemma-route.md` §5. With §3.1
and §3.3 that makes **four** families of argument eliminated: routing, monotone/potential, size, and
lattice closure.

---

## 4. How far the machinery reaches at all

**The gap is exactly one layer, at exactly two places.** With the size bounds $S(9..17)$ from van Voorhis
above the computed bases $S(9)=25$, $S(10)=29$:

| $n$ | truth | capacity | sentinel | monotonicity | gap |
|---|---|---|---|---|---|
| 11 | 8 | 7 | 7 | 7 | 1 |
| 12 | 8 | 7 | 7 | 8 | **0** |
| 13 | 9 | 7 | 7 | 8 | **1** |
| 14 | 9 | 7 | 7 | 9 | **0** |
| 15 | 9 | 7 | 7 | 9 | **0** |
| 16 | 9 | 7 | 7 | 9 | **0** |
| 17 | 10 | 8 | 8 | 9 | **1** |

So the entire tail of the table rests on **two** statements, $D(13)\ge9$ and $D(17)\ge10$; everything else
at depths 9 and 10 is monotonicity. Both are known only computationally.

**Lemma H applies but the residual grows.** The statement to refute at a frontier is: *no connected
$(d-1)$-layer network sorts $\mathrm{image}(M)$ for any matching $M$*.

| $n$ | $d$ | suffix | $\lvert\mathrm{image}(M)\rvert$ | near-perfect $M$ |
|---|---|---|---|---|
| 11 | 7 | 6 layers | 486 | $1.0\times10^{4}$ |
| 13 | 9 | 8 layers | 1 458 | $1.4\times10^{5}$ |
| 15 | 9 | 8 layers | 4 374 | $2.0\times10^{6}$ |
| 17 | 10 | 9 layers | 13 122 | $3.4\times10^{7}$ |

For calibration: at $n=11$ the one-matching instance (486 states, 6 layers) is 32 472 variables and 1.47M
clauses and takes 720 s; the monolithic all-inputs $(11,7)$ instance (7.3M clauses) does not terminate. A
single-$M$ instance at $n=13$ is about the size of that failed monolithic one, and there are $1.35\times10^5$
of them. So the route is a computation with a factor $\sim10^3$ over what was already out of reach.

**Why the block invariant cannot be iterated for free.** The count invariant (★) does work only when the
suffix has at least two components: with one component, "at most one block is mixed" is vacuous and the
count equals the total weight. Lemma H is therefore also a precise statement of where the tool dies. The
known optimal networks show connectivity reaching only so deep:

| network | components of layers $k+1..d$ for $k=0,1,\dots,d$ | connected for |
|---|---|---|
| 11_d8 | $1,1,1,1,1,3,4,8,11$ | $k\le4$ of 8 |
| 13_d9 | $1,1,1,1,2,3,4,5,9,13$ | $k\le3$ of 9 |
| 17_d10 | $1,1,1,1,1,1,2,2,3,10,17$ | $k\le5$ of 10 |

Components appear only in the last 3–6 layers, exactly where the constraint is on the largest possible
image.

**Beyond $d=10$ the question is not about machinery.** For $18\le n\le32$ the best lower bound is 10
(monotonicity) against upper bounds 11–14; the frontier $n_{11}$ is unknown, so there is nothing to attack.
That range is a construction-and-verification problem.

---

## 5. Which properties actually shrink an instance, measured

The point of a property, for larger instances, is that it multiplies the search reduction. Measured
(`twolayer.c`, enumeration of last layers):

| property | what it removes | $n=11$ | $n=13$ | $n=17$ |
|---|---|---|---|---|
| T3 maximal layers | choice of layer size (all matchings → maximal) | $3.4\times$ | $4.2\times$ | $6.1\times$ |
| $\mathrm{image}(M)=3^{\lfloor n/2\rfloor}2$ | inputs to test at layer 1 | $4.2\times$ | $5.6\times$ | $10\times$ |
| C1 last layer adjacent | non-adjacent last layer | $72\times$ | $358\times$ | $13\,336\times$ |
| C7 last-layer normal form | two adjacent unused channels | $\times9$ | $\times13.5$ | $\times30$ |
| **C1+C7 combined** | the last layer entirely | $650\times$ | $4\,826\times$ | $\mathbf{4.0\times10^{5}}$ |
| **B-series front prefixes** | the first two layers | — | — | $\mathbf{5.7\times10^{4}}$ |
| reflection | channel-reversal orbit | $2\times$ | $2\times$ | $2\times$ |
| **A′** last-layer preimage | states at level $d-1$ | $121\times$ | $410\times$ | $5\,041\times$ |

For an adjacent last layer $|A'(M)|=(3n+1)/2$ exactly, so that reduction is exactly $2^{n+1}/(3n+1)$ —
exponential. At $n=17$ the front and back canonical forms multiply to about $2.3\times10^{10}$: that, not any
counting argument, is why $D(17)=10$ was reachable in 2015 and $n=19$ is at the edge today.

**Lemma H reduces nothing.** Random maximal-layer networks of the relevant depth are already connected
essentially always — 20 000 trials each, 100.00 % at $(11,6)$, $(13,8)$, $(17,9)$ — so imposing connectivity
prunes 0.00 %. It is a theorem, not a reduction.

**The count invariant does prune, in the back half.** If layers $k+1..d$ have $b$ components, the state after
layer $k$ is confined to $\sum_w\prod_i\binom{|C_i|}{|C_i\cap T_w|}$ states, which is $2^{b-1}$ off $2^n$.
Measured, as % of $2^n$:

| network | $k=1,\dots,d$ |
|---|---|
| 11_d8 | 100, 100, 100, 100, **25.1, 12.6, 0.73** |
| 13_d9 | 100, 100, 100, **50.0, 25.0, 12.5, 6.3, 0.22** |
| 17_d10 | 100, 100, 100, 100, 100, **50.0, 50.0, 25.0, 0.02** |

Up to $4096\times$ off, but flat at 100 % across the front half, where $b=1$.

**So the properties worth collecting are not more inequalities.** The ends are saturated; the back half has
the invariant; the front-to-middle stretch is untouched. What is missing is either a bound on how fast a
layer can shrink an image (this document, §3.1) or a canonical form for the middle (`d11-compression-
structure.md`).
