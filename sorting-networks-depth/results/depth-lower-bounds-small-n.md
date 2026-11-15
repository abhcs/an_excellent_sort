# Depth lower bounds for sorting networks, $d\le 8$: several proofs each, and the general properties behind them

Everything here is about **depth**; "optimal" means fewest layers. Companion to
`sorting-network-lemma-compendium.md` (cited by its item IDs: A1, C4, C6′, D1, D2, G1–G3).

**Scope.** This document does one thing: it proves the depth lower bounds $d\le8$ by several independent
arguments each — with one exception, $D(11)\ge8$, which no tool in it reaches and which §5 hands to three
separate documents — and sets out the general properties of sorting networks and of depth-optimal networks
that those arguments use. The collections run $D(1..17)=0,1,3,3,5,5,6,6,7,7,8,8,9,9,9,9,10$.

**What is in it.**

1. A reduction of "the lower bounds of depth $1,\dots,8$" to **five frontier statements** — $n=3,5,7,9,11$
   (§2) — so that monotonicity of $D$ supplies every other $n$.
2. A **toolbox of eleven general properties** (T1–T11) with proofs (§3): the dominance lattice and the
   maximal-layer normal form, capacity, van Voorhis's recursion, the sentinel/deletion lemma and the
   interval restriction it yields, the cone bound, the block lemma *with its non-redundance hypothesis*,
   degrees and irredundancy, why single-input potentials saturate, back-end normal forms, and Lemma H.
3. The **five frontier bounds, each with several proofs** (§4), and a table of exactly what the two
   inequalities give at every $n\le12$ and where they first fail (§4.8).
4. **$D(11)\ge8$ is named as the hard case** (§5): both inequalities give $7$ there, and every general
   tool in §3 fails. It is *not* proved here. **`d11-handoff.md` is the entry point** — it explains why the
   case is hard and records every strategy that has failed. Three further documents carry the three
   strategies in detail, each self-contained:
   * `d11-block-lemma-route.md` — the block lemma, Lemma H, and the reduction to a single residual
     statement (R);
   * `d11-image-size-route.md` — image compression as a lower-bound method (Lemma S), with the exact
     minima and the four no-go results;
   * `d11-compression-structure.md` — the component factorization theorems, the local ratios, the tiling
     formula for the two-layer minimum, and the two-lemma split.
5. A **trust ledger** (§6) separating hand proofs, finite checks and solver answers, and reproducibility
   notes (§7).
6. The **five viewpoints** the properties give on depth-optimal networks (§8), machine-checked witnesses
   for the upper bounds (§9), and an honest accounting of what is new and what is not (§10) — including the
   finding that no numerical bound is improved anywhere in this document.


## 1. Notation

$n$ channels; a comparator $(i,j)$, $i<j$, sends $\min$ to $i$ and $\max$ to $j$; a **layer** is a
matching of comparators (no two share a channel); a **network** is a sequence of $d$ layers, $d$ its
**depth**, the total number of comparators its **size**. $D(n)$ = least depth of an $n$-channel
sorting network, $S(n)$ = least size. $\sigma_k = 0^{n-k}1^k$ is the sorted vector of weight $k$;
$B^n=\{0,1\}^n$; a network **sorts** if it maps every $x\in B^n$ to $\sigma_{|x|}$ (sufficient by the
zero-one principle, A1). $\mathrm{image}(N)=\{N(x):x\in B^n\}$; a **near-perfect** matching on an odd
number of channels is a matching leaving exactly one channel idle. Channels are numbered
$1,\dots,n$ throughout (scripts use $0,\dots,n-1$).

Known values: $S(1..12)=0,1,3,5,9,12,16,19,25,29,35,39$ ($n=9..12$ computer-assisted; $n=11,12$ by
Harder, arXiv:2012.04400);
$D(1..17)=0,1,3,3,5,5,6,6,7,7,8,8,9,9,9,9,10$ (provenance: compendium D5).

---

## 2. The lower bounds $d=1,\dots,8$ reduce to five statements

Write $n_d=\min\{n: D(n)\ge d\}$. The table of $D$ gives

| $d$ | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| $n_d$ | 2 | 3 | 3 | 5 | 5 | 7 | 9 | 11 | 13 | 17 |

and $D(n)\ge d$ for all $n\ge n_d$ **iff** $D(n_d)\ge d$, because $D$ is nondecreasing (T4). Note
$n_2=n_3=3$ and $n_4=n_5=5$: the bounds "$d=2$" and "$d=4$" are not tight anywhere, and are implied by
$D(3)\ge3$ and $D(5)\ge5$ respectively.

**So the whole content of "$d\le8$" is five statements:**

$$D(3)\ge3,\quad D(5)\ge5,\quad D(7)\ge6,\quad D(9)\ge7,\quad D(11)\ge8 .$$

Two further true bounds are implied rather than needed: $D(2)\ge1$ (immediate, and $D(3)\ge3$ already
gives $D(n)\ge3$ for all $n\ge3$), and $D(4)\ge3$ (from $D(3)\ge3$ by monotonicity, since $D(4)\ge D(3)$).
The five above have distinct frontiers $n=3,5,7,9,11$.

---

## 3. The toolbox

### T1. Zero-one principle
A network sorts iff it sorts every $x\in B^n$. *Proof*: comparators commute with thresholding
$\theta_t(y)_i=[y_i\ge t]$, because $\theta_t$ distributes over $\min$ and $\max$; if $N$ fails on
some input $y$ there are $i<j$ with $y_i>y_j$, and $\theta_t$ at $t=y_j+1$ gives a failing 0-1 input.
(A1.)

### T2. Capacity (a layer is a matching)
$\mathrm{size}(N)\le \mathrm{depth}(N)\cdot\lfloor n/2\rfloor$, hence

$$D(n)\ \ge\ \Big\lceil \frac{S(n)}{\lfloor n/2\rfloor}\Big\rceil .$$

*A second form, used below:* for an **odd** $n=2m+1$ this is $D(n)\ge \lceil 2S(n)/(n-1)\rceil$.
(G1.)

### T3. Adding comparators preserves sorting; maximal-layer normal form
If $N$ sorts and $N'$ is obtained from $N$ by adding comparators to its layers, then $N'$ sorts.

*Proof.* On $B^n$ of fixed weight $k$ use the **prefix-dominance** order
$x\succeq y \iff \sum_{i\le p}x_i\ge\sum_{i\le p}y_i$ for every $p$. A comparator $C_{ij}$ with $i<j$
satisfies $C_{ij}(x)\succeq x$ (a $1$ moves from $j$ to $i$), and every $C_{ij}$ is
$\succeq$-monotone. The sorted vector $\sigma_k$ is the unique $\preceq$-minimum of its weight class.
If $N'$ has the same layers as $N$ plus extra comparators, then by induction on layers
$\mathrm{state}'_t\succeq \mathrm{state}_t$ for all $t$; at the end
$\mathrm{state}'_d\succeq\sigma_{|x|}$, and $\sigma_{|x|}$ is minimal, so equality holds. $\square$

**Consequence (normal form).** If a depth-$d$ network sorts then so does one in which **every layer
is a maximal matching**: for $n$ even, $\tfrac n2$ comparators per layer; for $n$ odd,
$\tfrac{n-1}2$ comparators and exactly one idle channel per layer. For $n=11$, $d=7$ this forces
**exactly $35$ comparators, five per layer** — the counting bound becomes an equality.

### T4. Sentinel deletion: monotonicity, interval restriction, and a size–depth inequality

**Lemma (sentinel).** Let $N$ sort $n$ channels and let $T$ be a set of channels that is a union of an
initial segment $\{1,\dots,t\}$ and a final segment $\{u,\dots,n\}$. Delete $T$ and every comparator
with an endpoint in $T$. The result sorts the remaining $n-|T|$ channels.

*Proof.* Give the deleted initial segment the value $-\infty$ and the deleted final segment
$+\infty$, where $-\infty<0<1<+\infty$. For a comparator $(i,j)$, $i<j$: if $i$ is in the deleted
initial segment then $\min(v_i,v_j)=-\infty$ stays on $i$ and $\max(v_i,v_j)=v_j$ stays on $j$; if
$j$ is in the deleted final segment the dual holds; if both are deleted the comparator is a no-op. So
the deleted channels keep their sentinel values and every remaining channel evolves exactly as in the
induced network. A sorting network sorts every input over every finite total order (T1 applied to
$0<1<\infty$), so the output on the remaining channels is their sorted order. $\square$

**Corollary 1 (monotonicity).** $D(n)\ge D(n-1)$: delete channel $n$.

**Corollary 2 (interval restriction).** For an interval $I\subseteq[n]$, the comparators with both
ends in $I$ form a sorting network on $|I|$ channels: delete the prefix $[1,a-1]$ and the suffix
$[b+1,n]$. Hence $S(|I|)\le \#\{\text{comparators inside } I\}$ and $D(|I|)\le \mathrm{depth}(N)$.

**Corollary 3 (size–depth inequality).** Let $N$ sort $n\ge3$ channels with $C$ comparators in $d$
layers, and let $c_i$ be the number of comparators on channel $i$. Since a layer is a matching,
$c_i\le d$, so $\sum_i c_i=2C\le (n-2)d+c_1+c_n$. Deleting channel $1$ (resp. $n$) leaves a sorting
network on $n-1$ channels with $C-c_1$ (resp. $C-c_n$) comparators, so $c_1,c_n\le C-S(n-1)$.
Hence

$$2S(n-1)\ \le\ 2C-(c_1+c_n)\ \le\ (n-2)\,d, \qquad\text{i.e.}\qquad
D(n)\ \ge\ \Big\lceil \frac{2S(n-1)}{n-2}\Big\rceil .$$

For even $n$ this is the sharp companion of T2 (see the table in §4.8).

### T5. Van Voorhis's recursion
$S(n)\ge S(n-1)+\lceil\lg n\rceil$: prune channel $i$ along the trajectory of the value $1$ of the
one-hot input $\langle i:n\rangle$ (every comparator on that path passes its other input through);
the pruned networks form a binary tree with $n$ leaves, so some channel lies on $\ge\lceil\lg
n\rceil$ comparators. (G2, G3.) Iterating from a base gives, with $\lceil\lg n\rceil=3$ for
$5\le n\le8$ and $=4$ for $9\le n\le16$:

| base | $S(11)\ge$ |
|---|---|
| $S(4)=5$ (elementary, hand) | $29$ |
| $S(5)=9$ (hand) | $30$ |
| $S(7)=16$ (computational) | $31$ |
| $S(10)=29$ (computational) | $\mathbf{33}$ |

**Correction recorded.** An earlier draft of this document quoted $S(11)\ge31$ from $S(5)=9$; that is
wrong, the chain from $S(5)=9$ gives $30$. The value $31$ needs $S(7)=16$, and $33$ — the number in
the literature — needs $S(10)=29$, i.e. a computation. Members m4 and m2 of the swarm caught this
independently. The distinction matters because it is the difference between a computation-free size
bound ($29$ or $30$) and one that inherits a machine result ($31$ or $33$).

### T6. Cone bound
$D(n)\ge\lceil\lg n\rceil$: after $k$ layers a channel depends on at most $2^k$ inputs, and every
output of a sorting network depends on all $n$ inputs. (D1.) Only $d\le2$ is in range here
($\lceil\lg3\rceil=2$, $\lceil\lg4\rceil=2$).

### T7. Block lemma and interval blocks (Codish–Cruz-Filipe–Ehlers–Müller–Schneider-Kamp)
For $k<d$ and a network $C$ **without redundant comparators** (no comparator can be deleted without
changing the function), the **$k$-blocks** of $C$ are the connected components of the graph on
channels whose edges are the comparators of layers $k+1,\dots,d$.

* (i) Values never cross blocks after layer $k$; each block sorts its own set of values.
* (ii) Blocks are **intervals** of channels (C6′).
* (iii) For **every** input at most **one** block receives both a $0$ and a $1$ (C4).

*Proof of (iii).* A block's values stay inside it, so a block that receives both values outputs both.
Since blocks are intervals, "above" and "below" are well defined; if block $B$ outputs a $0$ at some
position, every position above $B$ outputs $0$ (sortedness), and every block above $B$ receives only
$0$s; dually below. $\square$

**The non-redundance hypothesis is essential** and is stated in the source ([1507.01428] Def. 2) even
though our compendium's C4/C6′ suppressed it. Without it both (ii) and (iii) fail: the depth-optimal
4-channel network $(1,3)(2,4);(1,2)(3,4);(1,4)(2,3)$ sorts, but on input $1100$ the two $2$-blocks
$\{1,4\}$ and $\{2,3\}$ are both mixed — and $(1,4)$ is redundant. Since deleting redundant
comparators preserves sorting and depth, **non-redundance is available whenever we reason about a
depth-optimal network**; but it is *not* compatible with the maximal-layer normal form of T3 (adding
comparators can create redundancy), so the two normal forms must be used separately.

This is the only tool in the corpus that constrains the **middle** of a depth-optimal network: (i)–(iii)
say that after layer $k$ the state is "sorted blockwise, with at most one block still undecided".

**There is no free dual block lemma** (m3, verified here). The natural hope is to get a back-end
statement by reflection. Three things must be kept apart:

* *Channel reversal, layer order kept* ($(i,j)\mapsto(n{-}j{+}1,n{-}i{+}1)$ in the same layer) **is** a
  symmetry: $\mathrm{outputs}(C^R)=\{\bar x^R:\bar x\in\mathrm{outputs}(C)\}$. But it keeps the layer
  order, so the last layer of $C$ stays the last layer of $C^R$ — it does **not** become the first layer.
  (An earlier draft of this document, and one of my verdicts to the swarm, asserted the latter; it is
  wrong.)
* *Time reversal* ($(1,3),(2,3),(1,2)$ reversed to $(1,2),(2,3),(1,3)$ on 3 channels) is **not** a
  symmetry: the original sorts, the reversal sends $110\mapsto101$.
* The *mirror* (time **and** channel reversal) is not one either: it sends $100\mapsto010$.

So the block lemma cannot be transported to the last layer by any symmetry — a prefix does not trap
values the way a suffix does, and the only dual state set available is
$\mathrm{image}(L_1\cdots L_{d-1})\cap\mathrm{image}(L_d)$, which is just the sorted states. This is why
the corpus's back-end results (C1, C7, C8: last layer adjacent, last-layer normal form) are genuine
*proofs* about the last layer rather than dualisations of front-end lemmas.

### T8. Degrees, connectivity, irredundancy
* Every channel is compared at least once (an untouched channel passes a wrong value through).
* The comparator graph of a sorting network is **connected**: with $\ge2$ components, either two
  components have size $\ge2$ and an input with a $0$ and a $1$ inside each gives two "mixed"
  $0$-blocks, contradicting T7(iii) at $k=0$; or all but one component are singletons, i.e. some
  channel is never compared.
* In a size-minimal network every comparator is essential (else delete it); in a depth-minimal
  network no layer can be deleted.

### T9. Why single-input potentials cannot reach $8$: the capacities saturate

For a $0$-$1$ state $x$ of weight $k$ and a cut $j$ between channels $j$ and $j+1$ put
$D_j(x)=P_j(x)-\max(0,j-(n-k))$, where $P_j$ is the number of $1$s among the first $j$ channels.
Then $D_j\ge0$, $x$ is sorted iff all $D_j=0$, and $\sum_j D_j=\mathrm{inv}(x)$, the inversion
number. A comparator $(a,b)$, $a<b$, that fires at a $10$ moves one $1$ from $a$ to $b$, decreasing
$D_j$ by exactly $1$ for each $j\in[a,b-1]$, i.e. by $b-a$ in total. In one layer a matching crosses
cut $j$ at most $\min(j,n-j)$ times, so the total work per layer is at most
$$\sum_{j=1}^{n-1}\min(j,n-j)=\Big\lfloor \frac{n^2}{4}\Big\rfloor .$$
For $n=11$ that capacity is $30$, and the block input $1^5 0^6$ has $\mathrm{inv}=5\cdot6=30$: **one
layer could in principle discharge it completely**. The reverse input has $55$ inversions, giving
only $\lceil55/30\rceil=2$. Per cut the same computation gives the trivial bound $d\ge1$. So no
argument of the form "this input needs this much work, one layer does at most that much" can prove
anything beyond $d\ge2$ — the truth at $n=11$ requires *simultaneous* reasoning about all inputs with
one set of matchings. T7 is precisely such a statement.

### T10. Back-end normal forms (Codish et al.; compendium C1, C2, C7, C8)
In a non-redundant sorting network every comparator of the last layer is **adjacent**, $(i,i+1)$
(C1), and there is a normal form in which additionally no two adjacent channels are unused in the
last layer (C7). With the normal form the number of possible last layers drops from the Fibonacci
number $F_{n+1}-1$ to the Padovan number $P_{n+5}$ — for $n=17$, from 2583 to 86 (C8). These are
*search* reductions rather than bounds: they constrain the endgame of an optimal network and are what
makes SAT searches feasible, but by themselves they say nothing about how many layers are needed.
They are included because they are genuine structural properties of optimal networks, and because
they locate exactly where the corpus's theory is strong (the two ends, T7's blocks and T10's last
layer) and where it is empty (the middle).

### T11. The first layer is forgotten (Lemma H)
Let $N$ sort $n\ge3$ channels with every layer a maximal matching. Then the comparators of layers
$2,\dots,d$ form a **connected** graph on $[n]$, for every $n$, odd or even. (For odd $n$ no
maximality is needed at all; for even $n$ it is.) Equivalently: every value is forced by sortedness to
end somewhere specific, so the component it occupies after layer 1 must contain that place, and
one-hot, one-cold and their subset variants force every channel into a single component. Proved in
§2 of `d11-block-lemma-route.md`, in four ways — the odd case by m7, the even case by m1, a counting argument of mine, and a parity
argument of m6 — and verified exhaustively at $n=3,4,5,6$. Consequence: the reachable set after layer 1 is the only thing the rest
of the network sees, so "depth is too small" becomes a statement about one connected block of
comparators acting on one reachable set, rather than about a network. This is the sharpest structural
statement in this document and it is uniform in $n$.

---

## 4. The five frontier bounds, with their proofs

Summary of what is available (details below; "finite" means a small exhaustive check, "solver" a SAT
answer):

| bound | frontier $n$ | proofs |
|---|---|---|
| $D\ge1$ | 2 | trivial; cone; capacity |
| $D\ge2$ | 3 | capacity; cone (subsumed by $D(3)\ge3$) |
| $D\ge3$ | 3, 4 | capacity ($n=3,4$); direct $3\times3$ table ($n=3$); sentinel ($n=4$); monotonicity ($n=4$) |
| $D\ge4$ | 5 | subsumed by $D(5)\ge5$ |
| $D\ge5$ | 5 | capacity; finite check on the suffix image (no network found); **capacity-free exhaustive search** over maximal-layer networks |
| $D\ge6$ | 7 | capacity; the same two finite checks (105 matchings $\times$ 4 layers, no hits; and an 87 s exhaustive search) |
| $D\ge7$ | 9 | capacity; SAT (independently re-verified, §7) |
| $D\ge8$ | 11 | **none in this document**: every tool fails (§4.7, §5). Three strategies in the companion documents, none complete |

The pattern, stated plainly: **capacity settles every odd $n\le9$; monotonicity carries each to the
next even $n$; and at $n=11$ capacity gives $7$ against a true $8$.** Nothing else in the toolbox
improves on that (§4.8).

Two of these rows have a second proof that uses **no capacity, no size values and no $S(n)$ at all** —
an exact exhaustive search over maximal-layer networks with the sound prune $\mathrm{im}_t\subseteq
A_{d-t}$ (m5 of the swarm): $D(3)\ge3$, $D(4)\ge3$, $D(5)\ge5$, $D(6)\ge5$, $D(7)\ge6$ independently
of the counting bound, with $D(4)\le3$ and $D(6)\le5$ as built-in sanity checks. That search did not
reach $n=8,9$ (the frontier exceeds $4\cdot10^5$ image sets), so $D(9)\ge7$ still has only the capacity
proof (a hand argument, but from the computed $S(9)=25$) and the SAT proof by machine.

The one route that does not depend on the size values at all is Lemma H (`d11-block-lemma-route.md` §2), which reduces
$D(n)\ge d+1$ to a statement about one connected block of $d-1$ layers — uniform in $n$, at the price
of a finite residual case; we ran it for $n=5$ and $n=7$ (no hits) and it *is* (R) at $n=11$.

### 4.1 $D(2)\ge1$
(a) A network with no layers maps $10\mapsto10$. (b) Cone: $2^0=1<2$. (c) Capacity:
$S(2)=1>0$. Two of the three are trivial, but they are genuinely different arguments.

### 4.2 $D(3)\ge3$
(a) **Capacity**: $S(3)=3>2\cdot\lfloor3/2\rfloor=2$, so $d\ge\lceil3/1\rceil=3$.
(b) **Direct** (a $3\times3$ table): a 2-layer network on 3 channels is $(a,b);(c,d)$ with
$a<b$, $c<d$, $(a,b),(c,d)\in\{(1,2),(1,3),(2,3)\}$, and each of the nine pairs fails on one of the
0-1 inputs $100,110,010,101$. E.g. $(1,2);(2,3)$ fails on $110$ (output $101$), $(1,3);(2,3)$ fails
on $101$, $(2,3);(1,3)$ fails on $110$, and the three constant pairs fail trivially.
(c) **Cone** gives $d\ge2$ only, so it does not suffice.
*Remark.* Here T4 is exactly tight — $2S(2)=2=(3-2)\cdot2$ — so the sentinel inequality cannot see
$D(3)\ge3$, while capacity can; and at even $n$ the roles reverse but the two coincide (§4.8). So the
two bounds are not independent mechanisms: capacity is the substantive one, and the sentinel
inequality's job is to make the *deletion* lemma available (T4 Cor. 2), not to add a second column to
the table.

### 4.3 $D(4)\ge3$
(a) **Capacity**: $S(4)=5>2\cdot2=4$.
(b) **Sentinel (T4)**: $2S(3)=6>(4-2)\cdot2=4$ — but see §4.8: at even $n$ this is the capacity
bound at $n-1$, so it is really (a) applied one step down plus monotonicity.
(c) **Monotonicity** from $D(3)\ge3$.
(d) **Direct**: two layers hold at most $4$ comparators and $S(4)=5$ (classical; a four-line case
analysis on the first comparator).
Four proofs, using three different mechanisms.

### 4.4 $D(5)\ge5$
(a) **Capacity**: $S(5)=9>4\cdot2=8$, so $d\ge\lceil9/2\rceil=5$.
(b) **Block-lemma route** (the technique of `d11-block-lemma-route.md` §2, in miniature). Recall Lemma F
(`d11-block-lemma-route.md` §3): for odd $n$, every near-perfect matching $M$ and every partition of $[n]$
into $b\ge2$ intervals admit a state with no $10$ on an edge of $M$ that is non-constant on two blocks of
size $\ge2$; verified exhaustively for $n\le11$. Now let $N$ be a 4-layer network on 5
channels, WLOG with maximal layers (T3), so $8$ comparators. Its 1-blocks are the components of the
3-layer suffix ($\le6$ comparators). If there are $\ge2$ blocks, Lemma F ($n=5$) produces a state
$u\in\mathrm{image}(L_1)$ that is non-constant on two blocks, contradicting T7(iii); if the unique
block is a singleton, that channel is never touched by the suffix and must already carry $\min$ or
$\max$ after layer 1, which $L_1$ cannot arrange. So the suffix is a connected 3-layer network on 5
channels. Enumerating all $15^3=3375$ triples of maximal layers against all $15$ near-perfect
matchings $M$ (an $18$-element set $\mathrm{image}(M)$ each) gives **no** network sorting
$\mathrm{image}(M)$ — checked exhaustively.
(c) **Nothing else works**: the sentinel inequality gives only $\lceil2S(4)/3\rceil=4$, and the cone
bound gives $3$.

### 4.5 $D(7)\ge6$
(a) **Capacity**: $S(7)=16>5\cdot3=15$, so $d\ge\lceil16/3\rceil=6$.
(b) **Block-lemma route**, same shape as §4.4(b): a 5-layer 7-channel network has maximal layers and
$\le15$ comparators; no block of the 4-layer suffix can be a singleton
(`d11-block-lemma-route.md` §2.2 applies verbatim at any $n$); so if there are $\ge2$ blocks, Lemma F
($n=7$) contradicts T7(iii); hence the suffix is connected and must sort $\mathrm{image}(M)$ for the first
layer's near-perfect matching $M$. Running
the search over all $105$ near-perfect matchings and $4$ layers of maximal layers gives **no** hit
(4 min): no 4-layer network sorts any such $\mathrm{image}(M)$. So $D(7)\ge6$ again.
(c) The sentinel inequality gives only $\lceil2S(6)/5\rceil=5$, and monotonicity only $D(6)=5$.

### 4.6 $D(9)\ge7$
(a) **Capacity**: $S(9)=25>6\cdot4=24$, so $d\ge\lceil25/4\rceil=7$. This is the last time the
counting bound is sharp.
(b) Sentinel gives $\lceil2S(8)/7\rceil=6$; cone gives $4$.

### 4.7 $D(11)\ge8$: the hard case, not proved here
(a) Capacity: $35=7\cdot5$, no information. (b) Sentinel: $\lceil2S(10)/9\rceil=\lceil58/9\rceil=7$.
(c) Interval lemma: it gives $S(L)\le d\lfloor L/2\rfloor$ for every interval, and at $L=10$ that is
$29\le35$ — no information. (d) Cone: $4$. So all four general tools stall. **This is the one bound in
this document that is not established by the machinery in §3**, and it is treated separately in §5 and in
the three companion documents named there.

### 4.8 What the inequalities actually give, and where they first fail

| $n$ | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|
| capacity $\lceil S(n)/\lfloor n/2\rfloor\rceil$ | **3** | 3 | **5** | 4 | **6** | 5 | **7** | 6 | 7 | 7 |
| sentinel $\lceil 2S(n-1)/(n-2)\rceil$ | 2 | **3** | 4 | **5** | 5 | **6** | 6 | **7** | 7 | 7 |
| monotonicity from $n-1$ | – | 3 | – | 5 | – | 6 | – | 7 | – | 8 (from $n=11$) |
| truth $D(n)$ | 3 | 3 | 5 | 5 | 6 | 6 | 7 | 7 | 8 | 8 |

**Read this table with one caution, because an earlier draft of this document misread it.** For
**even** $n$ the sentinel inequality *is* the capacity bound at $n-1$:
$$\Big\lceil \frac{2S(n-1)}{n-2}\Big\rceil=\Big\lceil \frac{S(n-1)}{\lfloor (n-1)/2\rfloor}\Big\rceil
\qquad (n \text{ even}),$$
so by monotonicity $D(n)\ge D(n-1)\ge$ that same number. The equality holds in every even column
above; member m4 of the swarm pointed this out and it is correct. Consequently:

* **capacity alone, plus monotonicity, already gives the whole table up to $n=10$** — capacity is
  sharp at $n=3,5,7,9$ and monotonicity carries those values to $n=4,6,8,10$. There is no second
  mechanism at even $n$, and the parity split advertised in an earlier draft was an artefact.
* The sentinel inequality is nevertheless **not** redundant: for **odd** $n$ it is strictly stronger
  than capacity at $n-1$ (at $n=11$: $7$ against $6$), because the deleted set has size $n-2$ rather
  than $\lfloor (n-1)/2\rfloor$ channels' worth of comparators. Its real content is the *deletion
  lemma* behind it (T4), which is what yields the interval restriction (T4 Corollary 2) — a statement
  about sub-networks that capacity cannot make at all.
* Either way, **both give $7$ at $n=11$** against a true value of $8$: this is the precise sense in
  which $n=11$ is the first case needing a new idea, and it explains the shape of the literature —
  $D(11),\dots,D(16)$ were settled by SAT (Bundala–Závodný, arXiv:1310.6271) rather than by an
  inequality.

---

### 4.9 The tail of the table
The same counting that fails at $n=11$ fails one layer short at every later frontier: at $n=13$ the
inequalities give $8$ against a true $9$, and at $n=17$ they give $9$ against $10$; at $n=12,14,15,16$
monotonicity already suffices. So the whole tail rests on two statements, $D(13)\ge9$ and $D(17)\ge10$,
both known only computationally. For how far the machinery reaches, and why, see §1 of
`d11-image-size-route.md`.


## 5. $D(11)\ge8$: the hard case

This section states why $n=11$ is where the machinery of §3 stops, and directs to the three attempts at
proving it. **None of them succeeds**; the value $D(11)=8$ is known computationally
(arXiv:1310.6271 and 1412.5302, SAT), with no published hand proof.

### 5.1 What fails, exactly

| tool | what it gives at $n=11$, $d=7$ |
|---|---|
| capacity (T2) | $35=7\cdot5$ — no information |
| sentinel (T4) | $\lceil2S(10)/9\rceil=7$ |
| interval restriction (T4.2) | $29\le35$ — no information |
| van Voorhis (T5) | $S(11)\ge33$, so capacity gives $\lceil33/5\rceil=7$ |
| cone (T6) | $4$ |
| block lemma (T7) | nothing at $b=1$, which Lemma H forces |

Capacity is *exactly* tight at $n=11$: a 7-layer network would have $7\cdot5=35$ comparators, and
$S(11)\le35$. There is no numerical slack anywhere, which is the structural reason this case needs an
argument of a different kind rather than a sharper inequality.

### 5.2 What has been ruled out

Four relaxations of the problem are now known to be *satisfiable*, so no argument confined to them can
prove $D(11)\ge8$. Each was a natural first attempt and each is a proved statement:

| approach | why it cannot work | where |
|---|---|---|
| routing / cut counting / free-choice flow | cut counting gives $d\ge1$, cone $4$, per-weight routability is satisfiable for all $2048$ inputs | `d11-block-lemma-route.md` §5 |
| order-theoretic: monotone, weight-preserving, fixes sorted states | the sorted map $x\mapsto\sigma_{\lvert x\rvert}$ satisfies all of it, so the relaxation is vacuous for every $n,d$ | `d11-block-lemma-route.md` §5 |
| image *size*: "the image is small enough to fit $A'$" | satisfiable at every small frontier, and the size certificate is the largest fiber, which over-estimates the achieved average by a factor $\sim6$ at the first step | `d11-image-size-route.md` §3.1 |
| lattice closure: image closed under $\wedge,\vee$ | $S\cup\{s_w\}$ *is* a sublattice for every adjacent last layer and every single flip state | `d11-image-size-route.md` §3.3 |

### 5.3 The three strategies, and what each achieves

**A. Block lemma and the first layer** (`d11-block-lemma-route.md`). The corpus's block lemma constrains
what a suffix can see. Proved here: the block lemma is false without the non-redundance hypothesis of
[1507.01428] Definition 2, and the two normal forms (maximal layers, no redundant comparator) are
separately free but jointly not available. With that repaired, **Lemma H** — in a sorting network with
maximal layers the suffix of layers $2..d$ is always connected, for every $n$ — follows, with four
independent proofs. It reduces $D(11)\ge8$ to a single residual statement (R) about one connected 6-layer
block sorting an image of $486$ states, and (R) is *equivalent* to $D(11)\le7$. What is gained is a change
of object (seven layers with a free first layer becomes six layers on a fixed small set); what is not
gained is a proof, because (R) is settled only by SAT.

**B. Image size** (`d11-image-size-route.md`). Let $F_t$ be the image of the first $t$ layers. Lemma S:
if every $(d-1)$-layer maximal-layer network has $\lvert F_{d-1}\rvert>c_n=(3n+1)/2$, then $D(n)>d$. The
exact minima $\lvert F_2\rvert$ are computed and *proved* for all $n\le12$, giving an independent proof of
$D(5),D(6),D(7)\ge\cdot$ and, evaluated at $d=D(n)-1$, a contradiction at every $n$ from 5 to 13. At
$n=11$ the method needs $\lvert F_6\rvert>17$; four independent constructions all reach exactly $23$ and
none goes lower. So the gap is a factor $1.35$ in a pure compression quantity — but proving
$\lvert F_6\rvert>17$ needs a lower bound that the document shows cannot come from any size or
max-fiber certificate.

**C. Compression structure** (`d11-compression-structure.md`). The step map factors over the components
of $M_*\cup M$ (Theorem F), and the factorization survives every further layer by *coarsening* to
clusters (Theorem F′). That reduces the two-layer minimum to a minimum over tilings by local patterns, with
exact local ratios, and gives the closed form
$\min\lvert F_2\rvert=\lvert F_1\rvert(2/3)^{\lfloor e/2\rfloor}(5/6)^{[e,n\text{ odd}]}$, proved for
$n\le12$. The product structure is trivial after $\lceil\lg n\rceil$ layers, which is exactly why the last
three steps resist; the route ends as a two-lemma split with the first lemma holding and the second
unavailable.

### 5.4 What an argument would need to look like

Every route above dies at the same place: the last few layers, where the image has full support and no
product structure. In all three the obstruction reduces to a statement about *which* states the image
occupies rather than how many — and in the size route that statement is (R) itself, since
$D(11)\le7$ is equivalent to it. So a hand proof of $D(11)\ge8$ must either

* find a structural invariant that separates the image of a 6-layer network from $A'(M_7)$ without
  appealing to size, monotonicity, weight, or $\wedge/\vee$-closure (all four are ruled out above), or
* close the compression route by proving a *lower bound on per-cell growth* for the connected patterns of
  `d11-compression-structure.md` §3.2 — where the truth is a factor $\sim2.6$ per alternating cell
  against a requirement of $\sqrt6=2.449$, and where neither splitting nor integrality reaches.


## 6. Trust ledger

| Item | Status |
|---|---|
| T1, T2, T3, T4, T8 | hand proofs above (elementary) |
| T5 | hand proof, compendium G2/G3; exact bases $S(4)=5$, $S(5)=9$ classical |
| T6, T7 | hand proofs, compendium D1, C4, C6′ (T7 after Codish et al., arXiv:1507.01428, **with the non-redundance hypothesis that C4/C6′ had dropped**; see T7 and the corrected compendium entry) |
| $S(n)$ for $n\le10$ | literature; $n\le8$ classical (Floyd–Knuth used a computer for $n=7$), $n=9,10$ computational |
| $D(n)\ge$ tabulated, $n\le9$ | proved here from hand inequalities (T2 at odd $n$, T4 at even $n$); $D(2),\dots,D(8)$ additionally re-verified by exhaustive search over maximal-layer networks, and $(3,2),(4,2),(5,4),(6,4),(7,5)$ by an independent SAT encoding |
| $D(10)\ge7$ | sentinel inequality from $S(9)=25$ (computational input) |
| $D(11)\ge8$ | **not proved here**: no general tool in §3 reaches it (§5). Companion documents carry the three attempts and what each achieves |
| Lemma H, Lemma F, Lemma G, (R), the block-lemma correction, the no-free-dual remark | all belong to the $D(11)$ route; see `d11-block-lemma-route.md` §§2, 3, 5 |

**What is *not* claimed.** The bounds $D(3)\ge3$, $D(5)\ge5$, $D(7)\ge6$, $D(9)\ge7$ and
$D(10)\ge7$ are proved by hand in §4 from the inequalities of §3, with the computational inputs named
above. $D(11)\ge8$ is *not* among them; the value is the literature's computation, and the three companion
documents record how far each attempt at a hand proof gets.

## 7. Reproducibility

All scripts are in `code/`, beside `results/`, with a per-script table in `code/README.md`; `code/verify.sh`
re-runs every cheap check in about a minute. The companion documents list the scripts specific to their own
routes.

* `depth_search.py n d` — exhaustive search over **maximal-layer** networks (WLOG by T3) with subsumption
  pruning on image sets: if $\mathrm{image}(N')\subseteq\mathrm{image}(N)$ then every continuation that
  sorts $N$ also sorts $N'$, so $N'$ dominates. Verifies both directions: no network at depth $d-1$, and a
  witness at depth $d$. Runs: $D(2)=1$, $D(3)=3$, $D(4)=3$, $D(5)=5$, $D(6)=5$, $D(7)=6$, $D(8)=6$
  (each pair of runs; witness networks are printed).
* `sat_encode.py full n d` + `cadical` — CNF for "does a $d$-layer maximal-layer network sort a given
  state set?". Variables: $g_{\ell,p}$ (comparator $p$ in layer $\ell$), $\mathrm{idle}_{\ell,i}$,
  $v_{\ell,i,x}$ (value on channel $i$ after layer $\ell$ on input $x$). Clauses: matching constraints;
  idleness bookkeeping; value propagation ($g\Rightarrow v_{\ell,i}=\min$, $v_{\ell,j}=\max$;
  $\mathrm{idle}_i\Rightarrow$ channel $i$ unchanged — *not* $\lnot g\Rightarrow$ unchanged, which is
  unsound when two pairs share a channel, as an early version was); sortedness units at layer $d$; sorted
  inputs omitted (they are fixed points). Validated against the known values: $(3,2),(4,2),(5,4),(6,4)$,
  $(7,5)$ UNSAT and $(3,3),(4,3),(5,5),(6,5),(7,6)$ SAT. Then $(9,6)$: UNSAT in 195 s (27 810 variables,
  1 007 388 clauses) — an independent confirmation of $D(9)\ge7$.
* Postscript, worth recording: the pass-through condition must be keyed on the channel being *idle*, not on
  the comparator being absent. With the latter the encoding is satisfiable at depths where no sorting
  network exists, and the mistake is invisible for $n\le2$.

---


## 8. What the general properties say about depth-optimal networks

Five viewpoints, each with its own lower-bound mechanism; the first three are classical, the fourth
is the corpus's, and the fifth is what this document adds.

1. **Dominance lattice (T1, T3).** Fix the weight $k$. Comparators are monotone maps that move a state
   *up* in prefix dominance, and $\sigma_k$ is the bottom. A network sorts iff it pushes every state
   to the bottom. Two consequences are used constantly: adding comparators is safe, and every layer
   may be taken maximal. This is the cleanest proof of both.
2. **Token flow (T2, T9).** Ones only move right, along matched edges, at most one step per token per
   layer; sorting means the $k$ ones end on the last $k$ channels. Depth bounds become *routing*
   bounds: cut $j$ can be crossed $\min(j,n-j)$ times per layer. This viewpoint also explains why the
   naive bounds saturate (§T9).
3. **Restriction (T4).** Deleting a prefix and a suffix of channels, with sentinels, yields smaller
   sorting networks of no greater depth. This is the only general source of *size–depth* inequalities
   ($2S(n-1)\le(n-2)d$), and it is what makes the even cases go.
4. **Block decomposition (T7).** Cutting a non-redundant depth-optimal network after layer $k$ splits
   the channels into intervals that are sorted independently, at most one of which is still undecided.
   This is the corpus's statement about the *middle* of an optimal network; its hypothesis
   (non-redundance) is essential and is easy to lose.
5. **Forgetting the front (T11, Lemma H).** On an odd number of channels, whatever the first layer
   does, the remaining layers form one connected block. So a depth bound is a statement about a single
   block of comparators acting on one reachable set — the viewpoint under which $d=7$ versus $d=8$ at
   $n=11$ is a question about six layers and 486 states (§5), with no reference to $n$ anywhere.

**A remark on why $n=11$, $d=7$ is the natural frontier.** By §4.8 the counting and sentinel
inequalities are sharp for every $n\le10$ and both miss $n=11$ by exactly one layer. The
maximal-layer normal form makes the case look extremal — $35=7\cdot5$ comparators, every layer a
perfect matching on ten of eleven channels — but that is a *description*, not the mechanism: the
n=11 argument uses the other normal form, non-redundance, because maximalisation can create redundant
comparators and the block lemma needs non-redundance. Both normal forms are free; they cannot be
used simultaneously, and that tension is itself informative about what "depth-optimal" costs.

---

## 9. Appendix: witnesses for the upper bounds (machine-checked)

Depth-optimal networks found by the search of §7 (channels $1..n$; a layer is a set of comparators).
Each was checked against all $2^n$ inputs.

| $n$ | depth | layers |
|---|---|---|
| 2 | 1 | (1,2) |
| 3 | 3 | (2,3) \| (1,3) \| (1,2) |
| 4 | 3 | (1,2)(3,4) \| (1,3)(2,4) \| (1,4)(2,3) |
| 5 | 5 | (2,3)(4,5) \| (1,4)(3,5) \| (1,2)(3,4) \| (2,3)(4,5) \| (2,5)(3,4) |
| 6 | 5 | (1,2)(3,4)(5,6) \| (1,2)(3,5)(4,6) \| (1,3)(2,6)(4,5) \| (1,6)(2,4)(3,5) \| (1,6)(2,3)(4,5) |
| 7 | 6 | (2,3)(4,5)(6,7) \| (1,3)(4,6)(5,7) \| (1,2)(3,7)(5,6) \| (1,4)(2,5)(3,6) \| (2,7)(3,4)(5,6) \| (2,3)(4,5)(6,7) |
| 8 | 6 | (1,2)(3,4)(5,6)(7,8) \| (1,3)(2,4)(5,7)(6,8) \| (1,4)(2,3)(5,8)(6,7) \| (1,5)(2,6)(3,7)(4,8) \| (1,2)(3,5)(4,6)(7,8) \| (1,8)(2,3)(4,5)(6,7) |

These are not size-optimal — e.g. the 6-channel witness uses 15 comparators against $S(6)=12$ — and
that is the point of the maximal-layer normal form: for depth questions one may always spend more
comparators. Witnesses for $n=9,\dots,12$ at depths $7,7,8,8$ are in the literature (compendium D5);
they are not reproduced here because only the lower bounds are at issue.

---

---

## 10. What is new here, and what is not

An honest accounting, since the natural question is whether any of this extends the subject.

### 10.1 No numerical bound is improved

Not one value of $D(n)$ or $S(n)$ moves. Every bound proved in §4 was already known; the one bound in
play, $D(11)\ge8$, is not proved here. The toolbox grew in *understanding* and in *negative* results, not in
*power*.

### 10.2 The eleven toolbox items, classified

| item | status |
|---|---|
| T1 zero-one principle | classical (Knuth) |
| T2 capacity | folklore; the inequality $D\ge\lceil S/\lfloor n/2\rfloor\rceil$ is immediate |
| T3 maximal layers | classical (used throughout the corpus) |
| T5 van Voorhis | literature (1972) |
| T6 cone bound | folklore; gives only $d\ge\lceil\lg n\rceil$ |
| T7 block lemma | literature ([1507.01428]) — **and corrected here**, see below |
| T8 degrees, connectivity, irredundancy | folklore |
| T10 back-end normal forms | literature ([1507.01428] C1, C7, C8) |
| **T4 sentinel inequality** $2S(n-1)\le(n-2)d$ | true, and **never raises a bound**: checked for $4\le n\le17$, it is $\le\max(\text{capacity},\text{monotonicity})$ in every case, and at even $n$ it is *identical* to capacity at $n-1$. Its content is the deletion lemma, not a bound |
| **T4 interval restriction** | true and elementary; the bound it yields is capacity at $\lvert I\rvert$, which is $\le$ capacity at $n$, so it yields no bound either. Its use is structural (sub-networks) |
| T9 single-input potentials saturate | a no-go, elementary |
| **T11 Lemma H** | the one item not found in the corpus. Simple; and *measured useless instrumentally*: it prunes $0.00\%$ as a search constraint (§5 of `d11-image-size-route.md`), and it implies no bound. Its value is explanatory — it is what makes the block route terminate at $b=1$ |

So of eleven items, seven are classical or from the corpus, two are true but give no bound, one is a
trivial no-go, and one — Lemma H — is possibly new as a statement but has no instrumental value.

*A caution on "new":* "not in the corpus of fifteen papers" is a statement about fifteen papers, not a
literature claim. A targeted search for Lemma H found nothing usable, which is not the same as a sweep.

### 10.3 What is genuinely new, to the best of our knowledge

1. **Theorem F and F′** (`d11-compression-structure.md` §1): the size of an image factors over the
   connected components of $M_*\cup M$, and the factorization survives every further layer by coarsening to
   clusters. This is the only item I would call an addition to the theory, and it is what makes the next
   entry computable at all.
2. **The exact two-layer minimum for $n\le12$, with proofs** — values $12,18,30,36,72,108,180,216$ — and
   the closed form $\min\lvert F_2\rvert=\lvert F_1\rvert(2/3)^{\lfloor e/2\rfloor}(5/6)^{[e,n\text{
   odd}]}$.
3. **Four no-go theorems** (routing/counting; monotone/potential; size certificates; lattice closure),
   each ruling out a family of arguments rather than a single attempt.
4. **One critical observation about the literature**: [1507.01428]'s derivation of the interval property is
   apparently circular — Lemma 5's proof uses "above/below", i.e. presupposes intervals, while Theorem 2
   derives them from Lemma 5.

### 10.4 What is correction rather than extension

The block lemma's non-redundance hypothesis (the paper has it; our compendium had dropped it, and the
version without it is false); van Voorhis from $S(5)=9$ gives $S(11)\ge30$, not $31$; the sentinel
inequality collapses to capacity at even $n$; an $n_d$ row error; a reflection error in a verdict to the
swarm. These are diligence, not contribution, and they are listed so that they are not mistaken for
progress.

### 10.5 Distance to a non-SAT proof of $D(11)\ge8$

None of the three strategies is close, and the reason is qualitative rather than quantitative.

* **Block route.** (R) is *equivalent* to $D(11)\le7$ (`d11-block-lemma-route.md` §3), so it is a
  reformulation with no logical gain. What it buys is a smaller instance — six layers on $486$ states
  instead of seven layers on $2046$ — which is a better *SAT* target, not a hand proof.
* **Size route.** The requirement is $\min\lvert F_6\rvert>17$; four independent constructions all reach
  exactly $23$. But §3 of `d11-image-size-route.md` shows that no size certificate, no per-weight bound, no
  monotone/potential argument and no lattice-closure argument can establish such a lower bound. The gap is
  not "we have not found the estimate"; it is "the estimates available are provably incapable".
* **Structure route.** The first step is a theorem, and it is exact for $n\le12$. But the product
  structure dies after $\lceil\lg n\rceil=4$ layers, so three of the six steps have no handle at all. In
  particular — worth stating plainly — **a complete proof of the one open inequality (Lemma 1, the local
  packing inequality) would not give $D(11)\ge8$**: it settles step 1 only.

So the honest summary is that $n=11$ is not a case where more effort on the same lines will finish. The
only route that is different *in kind* is the partition DP that Theorem F′ suggests — state = a partition
of $[n]$ together with a set per block — and its feasibility is untested. The evidence is not encouraging:
the number of distinct images grows like $3\,341$ at level 2 for $n=7$ and $209\,777$ for $n=9$, i.e.
roughly $n^2$-fold per two channels, which extrapolates to $\sim10^{7}$-odd at level 2 for $n=11$ and
therefore $\sim10^{11}$ at level 3. A correct decomposition without a feasible algorithm.
