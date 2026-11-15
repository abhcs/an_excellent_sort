# Handoff: $D(11)\ge8$ — why it is hard, and what has failed

**Start here.** This document is the entry point for anyone picking up the last open bound in the $d\le8$
range. It states the claim and its exact status, explains why $n=11$ is hard in a way that is *structural*
rather than a matter of missing estimates, catalogues the strategies that have failed (each failure is a
proved statement, not an opinion), records what is positively established, and lists what a next attempt
must avoid.

Everything that rests on a computation has a script: see `code/README.md` for a per-script table, and run
`code/verify.sh` to re-check every cheap claim in about a minute. Detail lives in four documents,
referred to throughout:

| document | content |
|---|---|
| `depth-lower-bounds-small-n.md` | the toolbox T1–T11, the five frontier bounds that *are* proved, the trust ledger |
| `d11-block-lemma-route.md` | the block lemma, Lemma H, the reduction to (R), provenance |
| `d11-image-size-route.md` | image size as a method (Lemma S), the exact minima, four no-go theorems |
| `d11-compression-structure.md` | the factorization theorems, local ratios, the two-layer minimum, the two-lemma split |

---

## 1. The claim and its status

$$D(11)=8,$$
with the collection $D(1..17)=0,1,3,3,5,5,6,6,7,7,8,8,9,9,9,9,10$.

* **Known**, computationally, in [1310.6271] (SAT over prefix-representative sets, which also settles
  $n=12..16$) and again in [1412.5302].
* **No published hand proof exists.** Both derivations are SAT refutations; neither ships a proof log.
* A hand proof would be a finite argument by which a person can see that no 7-layer 11-channel network
  sorts — not a solver's answer. Nothing in this project reaches that.

## 2. Why $n=11$ is the base of everything above it

$D(n)\ge D(n-1)$ (monotonicity, T4), so $D(11)\ge8$ is exactly the statement that depth 8 begins at 11.
The thresholds $n_d=\min\{n:D(n)\ge d\}$ are $2,3,3,5,5,7,9,11,13,17$ for $d=1..10$. So:

* $D(11)\ge8$ alone gives $D(n)\ge8$ for all $n\ge11$ — it *is* the lower-bound column of the table from
  $n=11$ to $n=12$;
* and the analogous statement at $n=13$ ($D(13)\ge9$) carries $n=13..16$, with $D(17)\ge10$ carrying
  everything above.

So there are exactly three frontier statements left in the whole subject below $n=32$, and $n=11$ is the
smallest. A technique that cannot do 11 will not do 13 or 17.

## 3. Why 11 is numerically special: the inequalities are *closed*, not merely short

At $n=11$, $d=7$ a network would have at most $7\cdot5=35$ comparators, and an 11-channel network with 35
comparators is known. So:

| tool | value at $n=11$, $d=7$ | can it ever give 8? |
|---|---|---|
| capacity (T2): $d\ge\lceil S(11)/5\rceil$ | $\lceil35/5\rceil=7$ | **no**: it needs $S(11)\ge36$, and $S(11)=35$ exactly |
| sentinel (T4): $d\ge\lceil2S(10)/9\rceil$ | $\lceil58/9\rceil=7$ | **no**: it needs $S(10)\ge32$, and $S(10)=29$ exactly |
| interval restriction (T4) | $29\le35$ | no: the bound it yields is capacity at a smaller size |
| cone (T6) | $4$ | no |
| van Voorhis (T5) | $S(11)\ge33$, hence 7 by capacity | no |

**This is the sharpest thing to understand about the case.** It is not that our size bounds are weak:
$S(11)$ is known *exactly* — the 35-comparator network is classical, and Harder (arXiv:2012.04400) proved
that no smaller one exists — and $\lceil35/5\rceil=7$. The counting route is closed by an explicit
construction. The same holds at $n=13$ (capacity would need $S(13)\ge49$, a 45-comparator network is known).

It holds at $n=17$ too: $\lceil S(17)/8\rceil\ge10$ would need $S(17)\ge73$, and a 71-comparator
17-channel network is known (Dobbelaere's list, 12 layers; re-checked on all $2^{17}$ inputs). An earlier
version of this section quoted $S(17)\le74$ and concluded that 17 was a *size* problem, but 74 is the
smallest known *10-layer* network, not the smallest network. So none of the three frontiers — 11, 13, 17 —
is a size problem.

## 4. Why 11 is structurally special: the middle is a single block

The corpus's block lemma ([1507.01428]) says that after layer $k$ the channels split into interval
*blocks* that sort independently, with at most one block still mixed. That is the only tool in the
literature that constrains the *middle* of an optimal network, and the natural hope was a case analysis on
the block structure of a 7-layer network.

**Lemma H kills it** (`d11-block-lemma-route.md` §2, four independent proofs):

> In a sorting network on an **odd** number of channels the comparators of layers $2,\dots,d$ always form a
> **connected** graph — for any first layer. With maximal layers the same holds for every $n$.

So $b=1$ unconditionally: there is only one block, "at most one block is mixed" is vacuous, and the
counting invariant that powers the block lemma becomes the identity "the number of ones equals the weight".
The case analysis on $b\ge2$ is not hard — it is *empty*.

Two further cautions found by doing this, both of which cost real time:

* the block lemma is **false** without the non-redundance hypothesis that [1507.01428] Definition 2
  carries and that our own compendium had dropped. Counterexample: $(1,3)(2,4);(1,2)(3,4);(1,4)(2,3)$ on
  4 channels sorts, is depth-optimal with all layers maximal, and has two mixed 2-blocks — because
  $(1,4)$ is redundant;
* the two normal forms ("every layer maximal" and "no redundant comparator") are separately free and
  **jointly not available**, so every argument must choose one. The one place where both are used, in
  order, is Lemma S (`d11-image-size-route.md` §1).

**What remains is genuinely unconstrained.** Once $b=1$, the only fact left is that the 6-layer suffix is
connected and must map $\mathrm{image}(L_1)$ to sorted outputs. In the known depth-optimal networks the
partition into blocks coarsens to a single block after $\lceil\lg n\rceil$ layers — at $n=11$:
$11\to[2,2,2,2,2,1]\to[4,4,3]\to[8,3]\to[11]$ — so the last three of six layers have no block structure left
at all.

## 5. The two objects worth handing over

### 5.1 (R): the case becomes six layers on 486 states

By T3 take every layer maximal; by Lemma H the suffix is connected. $\mathrm{image}(L_1)$ is the set of
states sorted inside every pair of $M=L_1$, of size $3^e2^{11-2e}$ — $486$ when $e=5$. Then

> **(R)** $\exists$ a matching $M$ on 11 channels and a 6-layer network $S$ such that
> $S(u)=\sigma_{\lvert u\rvert}$ for every $u$ with no $10$ on an edge of $M$;

and $D(11)\le7\iff$(R) (`d11-block-lemma-route.md` §3). This is an *equivalence*, so it is a change of
object, not progress: (R) is a smaller SAT instance (32 472 variables, 1 466 562 clauses for the extremal
$M$; UNSAT in 720 s), not a hand proof.

### 5.2 (R″): seventeen explicit states

For an *adjacent* last layer — which one may assume, in a non-redundant network, by C1 — the last layer's
preimage is fully explicit. $\sigma^w$ reads $01$ on the single pair of $M$ straddling its $0/1$ boundary,
so

$$A'(M)=S\cup\{s_w\},\qquad s_w=0^{\,n-w-1}10\,1^{\,w-1},\qquad \lvert A'(M)\rvert=\tfrac{3n+1}{2}=17 .$$

Of those 17 states, 12 are the sorted ones (which every image contains) and 5 are those concrete vectors.
So the frontier is: **can the image of six layers be a subset of those 17 states?** That is the smallest
form the question has taken, and it is the right object to attack. Note that $A'(M)$ is *always* a
sublattice of the Boolean lattice, so $S\cup\{s_w\}$ is a sublattice for every single flip — which is why
closure arguments fail (§6).

### 5.3 Lemma S and the exact minima

> **Lemma S.** If every $(d-1)$-layer maximal-layer network on $n$ channels has
> $\lvert F_{d-1}\rvert>c_n=(3n+1)/2$ (odd $n$; $3n/2+1$ even), then $D(n)>d$.

At $n=11$: $D(11)\ge8$ follows from $\min\lvert F_6\rvert>17$. The exact values of $\min\lvert F_2\rvert$ are
**proved** for every $n\le12$ — $12,18,30,36,72,108,180,216$ for $n=5..12$ — and the greedy descent gives
$486,180,80,50,33,\mathbf{23}$ at $n=11$, where only the two-layer value 180 has been checked exhaustively.
So $\min\lvert F_6\rvert\le23$, and Lemma S needs $\min\lvert F_6\rvert\ge18$. **Whether that holds is open**:
the hypothesis of Lemma S implies $D(11)\ge8$ but is not implied by it, since a 6-layer image with at most 17
states need not fit inside any $A'(M)$. And if it does hold, no size certificate can prove it (§6, row 5).

## 6. The strategies that failed, and what each failure establishes

None of these failed for want of effort; each was pushed to a definite obstruction, and each obstruction is
a proved statement worth having.

| # | strategy | why it cannot work |
|---|---|---|
| 1 | sharper inequalities (capacity, sentinel, interval, cone, van Voorhis) | **closed by construction** at $n=11$: $S(11)=35$ is known exactly and gives only 7 (§3) |
| 2 | case analysis on the block structure ($b\ge2$) | **vacuous**: Lemma H forces $b=1$ for every odd $n$ (§4) |
| 3 | routing / cut counting / free-choice flow | **satisfiable**: cut counting gives $d\ge1$, cone 4, per-weight routability holds for all 2048 inputs |
| 4 | order-theoretic / potential / monotone image | **vacuous for every $n,d$**: the sorted map $x\mapsto\sigma_{\lvert x\rvert}$ is monotone, weight-preserving, fixes sorted states, and has its image inside $A'(M_d)$ |
| 5 | image-size and max-fiber certificates | **provably too lossy**: max fiber 13 against achieved average 2.086 at the first step, and the loss compounds ($13^5$ vs $21$); per-weight form gives 5.6 against a need of 18; no uniform constant survives (worst case $2^{-\lfloor n/2\rfloor}$) |
| 6 | lattice closure ($\wedge,\vee$) | **satisfiable**: network images are not sublattices in general, but $S\cup\{s_w\}$ is one for every adjacent last layer and every single flip |
| 7 | front/back canonical forms as search speedups | **don't touch the middle**: they buy $4\times10^5$ on the last layer and $5.7\times10^4$ on the first two at $n=17$, and nothing at all on layers $2..d-1$ |
| 8 | brute force / monolithic SAT | **out of reach**: $(11,7)$ at 158 004 variables and 7 285 333 clauses did not terminate in 25 min here, nor under four other solvers independently; the literature's answer is 609 *prefix-restricted* instances, i.e. the same method scaled by hand |

### 6.1 Reading guide: which result rules out which strategy

Each row of the table above is closed by one named result. They are collected here so that a reader
can go straight to the obstruction; "kind" says whether the obstruction is a proof, a computation, or an
empirical fact.

| strategy | ruling result | the statement | where | kind |
|---|---|---|---|---|
| 1. sharper inequalities | **closure of the inequalities** | an explicit 11-channel network has 35 comparators, and capacity would need $S(11)\ge36$; the sentinel inequality would need $S(10)\ge32$ against $S(10)=29$ | §3 above; `closed.py` | arithmetic + explicit construction |
| 2. block-structure case analysis ($b\ge2$) | **Lemma H** | in a sorting network on an odd number of channels, layers $2..d$ form a connected graph — so $b=1$ always | `d11-block-lemma-route.md` §2 | lemma, four proofs |
| 3. routing / cut counting / free-choice flow | **the routing no-go** | cut counting gives $d\ge1$; per-weight routability holds for all 2048 inputs; cone gives 4 | `d11-block-lemma-route.md` §5 | lemma + computation |
| 4. monotone / potential / monotone-image | **the vacuity lemma** | the sorted map $x\mapsto\sigma_{\lvert x\rvert}$ is monotone, weight-preserving, fixes sorted states, and has its image in $A'(M_d)$ — so the relaxation is satisfiable for every $n,d$ | `d11-block-lemma-route.md` §5 | lemma, one line |
| 5. image size / max-fiber | **the fiber gap** | $\lvert L_M(F)\rvert\ge\lvert F\rvert/\Phi$ with $\Phi$ the largest fiber, and $\Phi=13$ against an achieved average of $2.086$ at the first step — the loss compounds | `d11-image-size-route.md` §3.1 | lemma + measurement |
| 5b. per-weight counts | **weight saturation** | the per-weight certificate gives $5.6$ against a need of $18$, and measured per-weight ratios fall to $0.405$ at $k=6$ | `d11-image-size-route.md` §3.1 | lemma + measurement |
| 6. lattice closure ($\wedge,\vee$) | **the sublattice lemma** | $A'(M)=L_M^{-1}(S)$ is a sublattice, and $S\cup\{s_w\}$ is one for every adjacent last layer and every single flip state — so closure cannot rule out the minimal case | `d11-image-size-route.md` §3.3 | lemma + enumeration |
| 7. front/back canonical forms as speedups | **the coarsening theorem** | blocks at most double per layer, so the product structure is trivial after $\lceil\lg n\rceil$ layers; and Lemma H prunes $0.00\%$ of the search | `d11-compression-structure.md` §1.3; `d11-image-size-route.md` §5 | lemma + measurement |
| 8. brute force / monolithic SAT | **non-termination** | the $(11,7)$ instance, 158 004 variables and 7 285 333 clauses, did not terminate in 25 min here nor under four solvers independently | `d11-block-lemma-route.md` §4 | empirical |

Three of these deserve a caution. The **vacuity lemma** (row 4) and the **sublattice lemma** (row 6) are
one-line observations, so they are cheap to state and easy to overlook — but they eliminate whole
families, and they are the two that people re-derive most often. The **fiber gap** (row 5) is the only one
that is quantitative: the obstruction is not that the bound fails but that the certificate over-estimates
the compression by a factor $\sim6$, so sharper versions of the same certificate cannot help either.

Two remarks on how to read this table.

* Rows 3, 4, 5, 6 are **no-go theorems**, not failures of execution: they say that whole *families* of
  argument are incapable. Any future attempt must use strictly more than monotonicity, weight, image size,
  per-weight counts, and $\wedge/\vee$-closure.
* Row 1 is the one that most often looks like a gap and is not. At $n=11$, $13$ and $17$ the counting route
  is closed by an explicit construction (networks with 35, 45 and 71 comparators, against the 36, 49 and 73
  that capacity would need), so no counting route can reach any of the three frontiers.

## 7. What is positively established

* **Lemma H** (`d11-block-lemma-route.md` §2): four independent proofs; odd $n$ needs no hypothesis;
  verified exhaustively at $n=3,4,5,6$. Also *measured useless as a search constraint* — 0.00 % pruning at
  the relevant depths — so its value is explanatory, not instrumental.
* **Theorem F and F′** (`d11-compression-structure.md` §1): the image size factors over the components of
  $M_*\cup M$, and the factorization survives every layer by coarsening to clusters. Verified.
* **The exact two-layer minimum for $n\le12$**, with the closed form
  $\lvert F_1\rvert(2/3)^{\lfloor e/2\rfloor}(5/6)^{[e,n\text{ odd}]}$, and the local ratios
  $\rho_2=\rho_3=2/3$, $\rho_4=46/81$, $\rho_5=123/243$; $\rho_6$'s lower bound $8/27$ is rigorous by an
  exhaustive $1.08\times10^8$-pair check.
* **Independent proofs of $D(5),D(6)\ge5$ and $D(7)\ge6$** by exhaustive minimal-image computation, using
  neither capacity nor $S(n)$ nor SAT.
* **One correction to the literature's presentation**: [1507.01428]'s derivation of the interval property
  is apparently circular (Lemma 5's proof uses "above/below", i.e. intervals, which Theorem 2 then derives
  from Lemma 5).

## 8. What a next attempt must avoid, and the one route not excluded

**Must avoid**, because each is a proved satisfiability result: size certificates; per-weight counts;
monotone/potential arguments; lattice closure; routing/cut/flow relaxations; and case analyses on the block
structure. **Must not expect** the front/back canonical forms to help: they are saturated at the ends and
empty in the middle.

**Warning on the one open inequality.** The compression route's remaining gap is the local packing
inequality $\rho_k\ge(2/3)^{\lfloor k/2\rfloor}$ (equivalently $I_k\ge\sqrt6\,I_{k-1}$ per alternating
cell; the truth is $\sim2.6$ against $2.449$). Proving it would give the exact two-layer minimum for all
$n$ — and would **not** give $D(11)\ge8$, because it settles step 1 of six.

**The one route not excluded** is the partition DP that Theorem F′ implies: state = (a partition of $[n]$;
a set per block), transition = apply a matching and coarsen to the cluster partition. It is a correct
decomposition, and it is the only formulation found that carries the product structure past the second
layer. The evidence on feasibility is unpromising: the number of distinct images grows $105\to3\,341\to
76\,867$ by level 3 at $n=7$, and $945\to209\,777$ by level 2 at $n=9$, i.e. roughly an $n^2$-fold increase
per two channels, extrapolating to $\sim10^7$ at level 2 and $\sim10^{11}$ at level 3 for $n=11$. So it is a
correct decomposition without a feasible algorithm as it stands; making it feasible — by exploiting the
symmetry of the local block types, which was never done — is the concrete open engineering question.

## 9. Provenance and trust

* $D(11)=8$: [1310.6271] and [1412.5302], both SAT. **No hand proof.**
* $D(17)=10$: [1507.01428] (not [1310.6271], which leaves $n=17$ open).
* $S(9)=25$ is computer-assisted (arXiv:1405.5754); $S(10)=29$ follows by van Voorhis. $S(11)=35$ and
  $S(12)=39$: the networks are classical (Knuth, TAOCP vol. 3), and arXiv:2012.04400 (Harder) is the
  computer-assisted proof that they are optimal, i.e. of the *lower* bounds.
* **Arithmetic to not get wrong**: van Voorhis with $S(5)=9$ gives $S(11)\ge30$, not 31; 31 needs $S(7)=16$
  and 33 needs $S(10)=29$. An early draft of this project quoted 31.
* Lemma S's hypothesis ordering matters: delete redundant comparators **first** (to force an adjacent last
  layer), then maximalise layers $1..d-1$. Reversing the order invalidates the argument.

## 10. Summary in one paragraph

$n=11$ is hard for two independent reasons, and both are now proved rather than suspected. Numerically,
every inequality in the subject is *closed* there — even exact knowledge of $S(11)$ yields 7 — so the case
cannot be reached by counting. Structurally, the block lemma, the only tool that constrains the middle of
an optimal network, is vacuous there because Lemma H forces the suffix to be a single connected block. The
best available reformulation reduces seven layers on 2046 states to six layers on 486, and further to a
question about 17 explicit states; the best available lower-bound method needs $\min\lvert F_6\rvert>17$
(the smallest image found is 23, and whether the bound holds at all is open) and cannot get there with any
certificate of size, weight, monotonicity or closure.
Four families of argument are eliminated by proof. What a next attempt needs is an invariant that
distinguishes the image of six layers from those 17 states without appealing to any of the four — and no
candidate for one exists in this work.
