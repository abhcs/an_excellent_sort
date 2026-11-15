# The size side: lemmas characterising minimal-size sorting networks (Bose–Nelson)

Companion to `sorting-network-lemma-compendium.md`, which is restricted to **minimal depth**. This
file is the material on minimal **size** $S(n)$ that was split off from it, otherwise unchanged;
items are **S1–S12** here. References of the form A*, B*, C* point into the depth compendium, where
those items are stated and proved.

The material comes from two papers of the Reading project's top-10 list: Harder, *An Answer to the
Bose–Nelson Sorting Problem for 11 and 12 Channels* (arXiv:2012.04400) for S1–S10, and
Codish–Cruz-Filipe–Frank–Schneider-Kamp, *Twenty-five comparators is optimal when sorting nine
inputs* (arXiv:1405.5754) for S11. S12 is Fonollosa's joint size–depth prefix theorem, kept here
because it is the only place the two optima are compared. This file contains the corpus's only
genuine lower-bound *theorem* (S7, van Voorhis) as opposed to a SAT refutation.

---

The size side has the only *theorem-level* lower bound in the corpus. [2012.04400] (Harder) is where
it is done properly: the van Voorhis argument is recast as a recursion on *partial* sorting networks,
which is what makes it usable inside a search.

### S1. Partial sorting networks and monotonicity — proved
**Source:** [2012.04400] Definition 1, Lemma 2.
**Definitions.** For $X\subseteq B^n$, a network $c$ is a *partial sorting network on* $X$ if
$c(X)\subseteq B^n_s$; $s(X)$ is the minimum size of one. $s(B^n) = S(n)$ by A1.
**Statement.** $0\le s(X)\le s(Y)\le S(n)$ for $X\subseteq Y\subseteq B^n$.
**Proof.** $s(B^n) = S(n)$ by A1; every sorting network is a partial one on $Y$; every partial one on
$Y$ is a partial one on $X$. $\square$

### S2. Invariance and subsumption — proved
**Source:** [2012.04400] Lemmas 4, 5, Corollaries 6, 8.
**Statement.** $s$ is invariant under channel permutation ($X\sim_{S_n}Y$) and under bitwise negation
($X\sim_{\langle \mathrm b\rangle}Y$), hence under the generated relation $\sim$; and $s(X)\le s(Y)$
whenever $X\subseteq_\sim Y$.
**Proof.** *Permutation:* from a partial sorting network $c$ on $Y$, $\sigma c$ sorts $X=\sigma Y$ with
the same size, giving $s(X)\le s(Y)$ and, by symmetry, equality. *Negation:* from $c$ on $Y$ build $d$
by exchanging the two outputs of every comparator (max-min instead of min-max); then
$\bar z = \bar y^{c}$ iff $\bar z^{\mathrm b} = \bar y^{d}$, and $\bar z$ is sorted iff $\bar z^{\mathrm b}$
reversed is, so appending the reversal permutation gives a partial sorting network on
$Y^{\mathrm b}$ of the same size. *Subsumption:* combine. $\square$
This is the exact analogue of B1/B2 on the size side, and it is what the `Prune` step of the search of
[1405.5754] implements.

### S3. The pigeonhole bound — proved
**Source:** [2012.04400] Lemma 9.
**Statement.** If $|X|>n+1$ then $s(X)\ge1$.
**Proof.** A network with no comparators is a fixed permutation, hence preserves $|X|$; a sorted output
set has at most $|B^n_s| = n+1$ elements. $\square$

### S4. The initial-comparator recurrence — proved
**Source:** [2012.04400] Lemma 10.
**Statement.** For $s(X)\ge1$: $s(X) = 1 + \min\{s(X^{[i,j]}) : [i,j]\in D_n\}$, where $X^{[i,j]}$ is
the image of $X$ under the comparator $[i,j]$.
**Proof.** ($\le$) prepend $[i,j]$ to a minimal network for $X^{[i,j]}$.
($\ge$) Let $d=[k,l]r$ be a minimal network for $X$ in standard form. Then $r$ is a partial sorting
network on $X^{[k,l]}$, and it is minimal for that set, since a shorter one could be prefixed by
$[k,l]$ to sort $X$. Hence $s(X) = 1+s(X^{[k,l]}) \ge 1+\min$. $\square$

### S5. Eliminating redundant first comparators — proved
**Source:** [2012.04400] Definition 11, Lemma 12.
**Statement.** With $U(X) = \{X^{[i,j]} : X^{[i,j]}\not\sim_{S_n}X\}$ the set of *successors*,
$s(X) = 1+\min\{s(Y) : Y\in U(X)\}$ for $s(X)\ge1$.
**Proof.** If $X^{[k,l]}\sim_{S_n}X$ then $s(X^{[k,l]}) = s(X)$ by S2, so such a $[k,l]$ cannot be the
first comparator of a minimal network (that would give $s(X) = 1+s(X)$); the remaining candidates are
exactly $U(X)$. $\square$
**Reading.** S3–S5 are a complete recursion for $s$: memoise on similarity classes, and the search is
finite. That is the whole content of "compute $S(n)$ by search" — everything else is engineering.

### S6. Pruning a channel — proved
**Source:** [2012.04400] Definition 13, Lemma 16.
**Definition.** For a channel $i$, $c/i$ is obtained by deleting the wire that starts at input $i$,
follows the **max** output of every comparator it meets, and ends at output $n$; each comparator on
that path loses one input and one output and is short-circuited. $\delta(c,i)$ is the number of
comparators so removed.
**Statement.** If $c$ is a sorting network on $n$ channels then $c/i$ is a sorting network on $n-1$
channels, for every $i$.
**Proof.** The deleted path is the trajectory of the value $1$ when $c$ is applied to the one-hot input
$\langle i\!:\!n\rangle$; since $c$ sorts, that trajectory ends at output $n$. By monotonicity (A2) the
path carries $1$ for every input $\bar x$ with $\bar x_i = 1$; each comparator on the path therefore
passes its other input to its other output, which is exactly what the short-circuit does. Hence for
$\bar x$ with $\bar x_i=1$, $\;(c(\bar x))/i = (c/i)(\bar x/i)$. Every $\bar y\in B^{n-1}$ arises as
$\bar x/i$ with $\bar x_i=1$, and $(c/i)(\bar y)$ is a subsequence of the sorted $c(\bar x)$, hence
sorted. $\square$

### S7. Van Voorhis's bound — proved
**Source:** [2012.04400] Lemma 17, attributing van Voorhis 1972; the statement appears in
[1405.5754] Lemma 1 in the shifted form $S(n+1)\ge S(n)+\lceil\lg n\rceil$.
**Statement.** $S(n) \ge S(n-1) + \lceil \lg n\rceil$ for all $n\ge1$.
**Proof.** Let $c$ be a minimal $n$-channel network. For each $i$, $c/i$ is a sorting network on $n-1$
channels (S6), so $S(n) - \delta(c,i) = s(c/i) \ge S(n-1)$, i.e.
$S(n)\ge S(n-1)+\delta(c,i)$, and hence $S(n)\ge S(n-1)+\max_i\delta(c,i)$. It remains to bound
$\max_i\delta(c,i)$ independently of $c$. Take the union of the pruned paths for all $i$ and delete the
common output $n$: what remains is a binary tree whose root is the comparator feeding output $n$,
whose leaves are the $n$ inputs, and whose internal vertices are comparators; the depth of leaf $i$ is
exactly $\delta(c,i)$. A binary tree with $n$ leaves has height $\ge\lceil\lg n\rceil$, so
$\max_i\delta(c,i)\ge\lceil\lg n\rceil$. $\square$
**Why this matters.** Iterating gives $S(n)\ge S(10) + \sum_{k=11}^{n}\lceil\lg k\rceil = n\lg n - O(n)$:
the *order* $S(n)=\Theta(n\lg n)$ is a hand theorem (with AKS for the upper bound). Every published
size lower bound for $n\ge11$ is S7 applied to the computed bases $S(9)=25$, $S(10)=29$: it yields
$33,37,41,45,49,53,58,63,68,73$ for $n=11,\dots,20$.

### S8. Pruning partial networks — proved
**Source:** [2012.04400] Definitions 18–19, Lemma 20.
**Statement.** If $c$ is a partial sorting network on $X$ and $\langle i\!:\!n\rangle\in X$, then $c/i$
is a partial sorting network on $X/i := \{\bar x/i : \bar x\in X,\ \bar x_i = 1\}$.
**Proof.** As S6, restricted to the inputs in $X/i$; the hypothesis $\langle i\!:\!n\rangle\in X$ is what
guarantees the pruned path is the one ending at output $n$. $\square$

### S9. The Huffman bound — proved
**Source:** [2012.04400] Definitions 21–22, Algorithm 23, Lemmas 24, 25, Theorem 26.
**Setup.** A *$\star$-tree* on a multiset $L$ is a full binary tree with leaf labels $L$ and inner node
labels $a\star b$. A *Huffman algebra* $(A,\le,\star)$ satisfies $a\le a\star b$, commutativity,
$(a\star b)\star(c\star d) = (a\star c)\star(b\star d)$, monotonicity, and
$(a\star b)\star c\le a\star(b\star c)$ when $a\le c$; Huffman's algorithm (repeatedly combine the two
smallest labels) returns the minimal root value (Lemma 24).
**Statement (Huffman bound).** For $X\subseteq B^n$ with prunable channels $p(X)\neq\emptyset$,
$$ s(X) \;\ge\; H_{1+\max}\bigl\{\,s(X/i) : i\in p(X)\,\bigr\}, $$
the Huffman value computed in the algebra $(\mathbb N_0,\le,1{+}\max)$.
**Proof.** By S8, $s(X)\ge s(X/i)+\delta(c,i)$ for every $i\in p(X)$, so $s(X)$ is at least the root
value of *some* $1{+}\max$-tree with leaves $\{s(X/i)\}$, namely the tree of pruned paths. Huffman
returns the minimum root value over all such trees, hence a lower bound. $(\mathbb N_0,\le,1{+}\max)$ is
a Huffman algebra since $+$ distributes over $\max$. $\square$
**Corollary S9′** (monotonicity in the leaves). Replacing leaf values by lower bounds preserves the
bound. $\square$
Van Voorhis is the special case where all leaves are bounded by the height: S9 with all
$s(X/i)\ge S(n-1)$ gives the binary-tree-height bound of S7.

### S10. Well-behaved sets: making S9 applicable — proved
**Source:** [2012.04400] Definitions 27–28, Lemma 29, Corollary 30, Lemma 31, Corollary 33.
**Definitions.** For a permutation $\bar x$ of $(1,\dots,n)$, the *threshold set*
$T(\bar x) = \{\theta_k(\bar x) : 1\le k\le n+1\}$ (A1's $\theta$); $T\bigl((1,\dots,n)\bigr) = B^n_s$.
$X$ is *well-behaved* if it is a union of threshold sets; $W_n$ is the family.
**Lemma (preservation).** If $X\in W_n$ and $\bar x\in X$ then some prunable $i$ has $\bar x/i\in X/i$.
**Proof.** $\bar x\in T(\bar y)\subseteq X$; let $i$ be the channel with $\bar y_i = n$; the only member
of $T(\bar y)$ with $t_i=0$ is the all-zero vector, whose prune coincides with $\langle i\!:\!n\rangle/i$,
so $T(\bar y)/i = \{t/i : t\in T(\bar y)\}\ni \bar x/i$. $\square$
**Corollary.** Every nonempty well-behaved $X$ has $p(X)\ne\emptyset$, so S9 always applies.
**Lemma (sortedness test).** For well-behaved $X$: $s(X) = 0 \iff |X|\le n+1$.
**Proof.** ($\Rightarrow$) S3. ($\Leftarrow$) $|X|\le n+1$ with $X$ a union of threshold sets of size
$n+1$ each means $X$ is empty or a single threshold set $T(\bar y)$, which is a permutation of $B^n_s$
and hence sorted by the empty network. $\square$
**Corollary (well-behaved Huffman bound).** $s(X)\ge H_{1+\max}\{s((X/i)^\circ) : i\in p(X)\}$, where
$X^\circ$ is the well-behaved interior. $\square$

### S11. The size-theoretic lemmas of [1405.5754] — proved
**Source:** [1405.5754] Lemmas 1–6.
- **Lemma 1** (= S7 in shifted form): $S(n+1)\ge S(n)+\lceil\lg n\rceil$; with $S(9)=25$ this yields
  $S(10)\ge29$, and iterating yields the $n\ge11$ column.
- **Lemma 2** (= B1 specialised to equal size): if $C_a\preceq C_b$ and $C_b;C$ is a sorting network of
  size $k$, so is $C_a;C'$. Proof: B1 with A7.
- **Lemma 3 (completeness).** For every $n,k$ the sets $N^n_k$ (all networks of size $k$) and $R^n_k$
  (their subsumption-minimal representatives) are complete sets of filters: if any sorting network has
  size $\le k$ then one has a prefix in $R^n_k$. Proof: induction on $k$ using Lemma 2.
- **Lemmas 4 and 5 (numeric subsumption tests).** If for some $k$ the number of outputs with exactly $k$
  ones is larger in $\mathrm{outputs}(C_a)$ than in $\mathrm{outputs}(C_b)$, then
  $C_a\not\preceq C_b$. Proof: a permutation preserves the count for each $k$. Sharper: if
  $|w(C_a,x,k)|>|w(C_b,x,k)|$, where $w(C,x,k)$ is the set of positions that carry the bit $x$ in some
  output with $k$ ones, then $C_a\not\preceq C_b$; same proof. (These two eliminate 27M and 0.6M of the
  33M subsumption tests in the $n=7$ run.)
- **Lemma 6 (permutation filter).** If $\pi(\mathrm{outputs}(C_a))\subseteq\mathrm{outputs}(C_b)$ then
  $\pi(w(C_a,x,k))\subseteq w(C_b,x,k)$ for all $x,k$. Proof: apply $\pi$. This restricts the
  permutations that need testing.
- **Main theorem ⚙ computed.** The generate-and-test over the complete sets $R^n_k$ (Lemma 3) finds no
  sorting network of size 24 on 9 channels, so $S(9)=25$ (Floyd's 1964 network is optimal); by Lemma 1
  then $S(10)=29$ (Waksman's 1969 network is optimal).

### S12. Joint size–depth: the Pareto characterisation — proved
**Source:** [1806.00305] Lemma 1, Theorem 1, Theorems 2–5.
**Statement.** $R(T'_n)$ — representatives of two-layer networks modulo the equivalence of B7 *and*
output subsumption — is a complete set of prefixes for the search of networks that are optimal in size
and depth simultaneously: for every depth budget $d$ and size budget $k$, if an $(n,d,k)$ network
exists, one exists whose first two layers lie in $R(T'_n)$. **Proof.** Combine B1, B2, B7, and the
observation that subsumption never increases size or depth. $\square$
**⚙ computed consequences.** $S_{d=7}(10) = 31$ (Theorem 2); $D_{k=29}(10) = 8$ (Theorem 3);
$S_{d\in\{8,9\}}(11) = 35$ (Theorem 4); $S_{d=8}(12) = 40$ (Theorem 5). Hence for $n\le9$ there are
networks optimal in both metrics, and for $n=10,12$ there are not.

---

