# Lemmas and theorems characterising sorting networks and depth-optimal sorting networks

A compendium drawn from the ten papers of the Reading project's list
(`optimal-sorting-networks-reading-list.md` in the Reading project, 15 entries), with proofs.

**Scope: minimal depth only.** "Optimal" below always means *fewest layers* $D(n)$, never fewest
comparators. The size material (the Bose–Nelson problem, van Voorhis's recursion in full, Harder's
Huffman bound) has been split off into `sorting-networks-size.md` and is cited here as S1–S12; the
three size facts that genuinely feed *depth* bounds are kept as G1–G3 in the appendix.

**What "characterise" covers here.** Four kinds of statement get conflated in this literature, and
keeping them apart is most of the value of the list:

| Kind | What it pins down | Items |
|---|---|---|
| **A. Predicate** | when a comparator network *is* a sorting network | A1–A9 |
| **B. Front normal forms** | what a depth-optimal network may be assumed to look like at its input end | B1–B9 |
| **C. Back normal forms** | ditto at its output end | C1–C12 |
| **D. Depth** | the function $D(n)$, exactly | D1–D6 |
| **E. Gap** | what none of the ten papers characterises | E1–E3 |
| **G. Size facts kept** | the three size results that bear on depth | G1–G3 |

**Status markers.** Every item is one of:

- **proved** — a hand proof, reproduced or compressed below;
- **proved (sketch)** — the paper's argument is a long case analysis; the reduction is given and
  the enumeration is attributed;
- **⚙ computed** — the proof *is* a finite computation (SAT refutation, exhaustive search, or a
  certificate check). The mathematical content is the reduction that makes the computation finite.

**Notation.** $n$ channels; a network $C = L_1;\dots;L_d$ is a sequence of *layers*, each a set of
comparators $(i,j)$, $i<j$, no two sharing a channel; $d$ is the **depth**, $\sum_k|L_k|$ the
**size**; $C(\bar x)$ is the output on $\bar x$; $\mathrm{outputs}(C) = \{C(\bar x) : \bar x\in
B^n\}$ with $B=\{0,1\}$; $B^n_s$ is the set of sorted Boolean vectors, $|B^n_s| = n+1$;
$\bar x\le \bar y$ is pointwise; $\bar x^{\mathrm b}$ is bitwise negation; $\bar x^{R}$ is reversal;
$C^{R}$ is the reflection (replace $(i,j)$ by $(n{-}j{+}1,n{-}i{+}1)$); $\pi(C)$ is $C$ with channels
permuted; a **generalised** network allows max-min comparators $\langle i,j\rangle$, $i>j$;
$D(n)$ is the minimum depth of an $n$-channel sorting network, $S(n)$ the minimum size;
$\langle i\!:\!n\rangle$ is the one-hot vector with a single $1$ on channel $i$.

Two naming cautions before starting, both of which bite readers of the primary sources:

1. **"Saturated" means two different things.** In Bundala–Závodný (B6 below) a *saturated layer* is a
   syntactic condition on the second layer relative to a fixed first layer; in the journal version
   (B8, [1412.5302] Def. 7) a *saturated network* is an output-minimality condition, and the six
   forbidden patterns characterise it. Same word, different notions.
2. **$D(9)=7$, not $9$.** Parberry's title speaks of "nine-input" networks and the optimal depth there
   is $7$; $D(17)=10$ is the current frontier. $D$ is known exactly only for $n\le17$; the tabulated
   bounds for $n\le32$ are in [1310.6271] and [2511.04107] Table 1.

---

# Part A. What makes a comparator network a sorting network

### A1. The zero-one principle — proved
**Source:** [1310.6271] Lemma 1 (attributed to Knuth); restated as [2511.04107] Lemma 1, [2012.04400] §2, [1501.06946] §2.
**Statement.** A comparator network $C$ on $n$ channels is a sorting network iff $C$ sorts every
$\bar x\in B^n$.
**Proof.** ($\Leftarrow$) trivial. ($\Rightarrow$) It suffices to show that every network *commutes
with thresholding*: for $t\in\mathbb Z$ and $\bar x\in\mathbb Z^n$,
$$ \theta_t\big(C(\bar x)\big) = C\big(\theta_t(\bar x)\big), \qquad \theta_t(y)_i = [y_i \ge t]. $$
A comparator acts by $(\min,\max)$, and $\theta_t$ distributes over both:
$[\min(a,b)\ge t]=\min([a\ge t],[b\ge t])$ and $[\max(a,b)\ge t]=\max([a\ge t],[b\ge t])$. Hence the
identity holds layer by layer. Now suppose $C$ fails on some $\bar x\in\mathbb Z^n$: there are
$p<q$ with $C(\bar x)_p > C(\bar x)_q$. Take $t = C(\bar x)_p$. Then
$\theta_t(C(\bar x))_p = 1 > 0 = \theta_t(C(\bar x))_q$, so by the identity $C(\theta_t(\bar x))$ is
unsorted, and $\theta_t(\bar x)\in B^n$. $\square$

*Remark.* The proof shows more: $\theta_t$ is an endomorphism of the network, which is why the
"threshold set" machinery of [2012.04400] (S9–S10 of the size companion) is available as a lift from Boolean to
permutation inputs.

### A2. Monotonicity — proved
**Source:** [1507.01428] Lemma 2 (quoted from Al-Haj Baddar, Thm. 4.1).
**Statement.** If $\bar x\le\bar y$ then $C(\bar x)\le C(\bar y)$ for every network $C$.
**Proof.** A comparator is monotone in each argument: $a\le a'$, $b\le b'$ gives
$\min(a,b)\le\min(a',b')$ and $\max(a,b)\le\max(a',b')$. Induct over the layers. $\square$

This is the workhorse of Part C: every "case (a) forces case (b)" step in the end-game lemmas is an
application of A2.

### A3. Leading zeros and trailing ones are preserved — proved
**Source:** [1507.01428] Lemma 1; used implicitly by [1310.6271] and [1501.06946].
**Statement.** If $\bar x^0$ has $r$ leading zeros and $s$ trailing ones ($r+s\le n$) then so does
every $\bar x^k$, $0\le k\le d$. In particular a sorted input is a fixed point of every network.
**Proof.** Induction on $k$. Suppose channels $1..r$ carry $0$ and $n{-}s{+}1..n$ carry $1$ at layer
$k$. A comparator with both channels in $1..r$ outputs $0$'s there; a comparator $(i,j)$ with
$i\le r<j$ has value $0$ on channel $i$ and outputs $\min=0$ on $i$; a comparator $(j,i)$ with
$j<i\le r$ outputs $\max=0$ on $i$. Channels in $1..r$ not touched keep their value. So the prefix of
zeros is preserved; the suffix of ones is symmetric. $\square$

**Corollary (used by every SAT encoding).** Sorted inputs never need to be constrained, and — more
importantly — after a prefix $P$ the output $\bar x = 0^a\bar x' 1^b$ constrains only the *window* of
channels $a+1,\dots,n-b$: every comparator acting outside it is determined. [1501.06946] §3.1 turns
this into the count, for a prefix $P$,
$$ W(P) = \sum_{\bar x\in \mathrm{outputs}(P)} \Bigl(n - \max\{a : \bar x = 0^a\bar x'\} - \max\{b : \bar x = \bar x'1^b\}\Bigr), $$
the number of channel-instances that must appear in the residual formula. For $n=16$ this is
$85{,}296$ for Parberry's first layer versus $79{,}246$ for the $F_n$ layer — a factor that is pure
A3.

### A4. The minimum test set has exactly $2^n-n-1$ elements — proved
**Source:** stated in [1310.6271] §5 (`|B^n_{un}| = 2^n-n-1`, credited to Chung–Ravikumar); proof
assembled here from A3.
**Statement.** Let $T\subseteq B^n$ be a test set: every network sorting all of $T$ is a sorting
network. Then $|T| \ge 2^n-n-1$, with equality for $T = B^n\setminus B^n_s$.
**Proof.** ($\ge$) If $\bar x\notin B^n_s$ then the empty network is a network that sorts all of
$B^n\setminus\{\bar x\}$ but not $\bar x$; so $\bar x$ must belong to every test set.
($\le$) If $T\supseteq B^n\setminus B^n_s$ and $C$ sorts $T$, then $C$ sorts $B^n$ (A3 gives the
sorted vectors for free), so $C$ is a sorting network by A1. $\square$

### A5. The output-set size criterion — proved
**Source:** the "sortedness test" in this exact form is [2012.04400] Lemma 31 (restricted to
well-behaved sets); the general statement below is immediate from A3 and is the natural form for
SAT/CP search.
**Statement.** For every $n$-channel network $C$, $|{\rm outputs}(C)|\ge n+1$, with equality iff $C$
is a sorting network.
**Proof.** $B^n_s\subseteq {\rm outputs}(C)$ by A3, giving $\ge n+1$. If equality holds then
${\rm outputs}(C) = B^n_s$, i.e. every output is sorted; conversely if $C$ sorts then
${\rm outputs}(C)=B^n_s$. $\square$

This is the cheapest *complete* optimality test for a fixed network, and it is what makes
output-set-based search (as opposed to input enumeration) possible: the state of a prefix is the
*set* $\mathrm{outputs}(P)$, of size at most $2^n$ but usually far smaller.

### A6. Reflection — proved
**Source:** [1412.5302] Lemma 8; [2511.04107] Lemma 4 (with negation); [1310.6271] §3.5.
**Statement.** $\bar x\in{\rm outputs}(C) \iff \bar x^{R}\in{\rm outputs}(C^{R})$.
**Proof.** Induction on the size of $C$. For $C$ empty, clear. Let $C' = C;(i,j)$ and
$\bar y = C(\bar x)$; by induction $\bar y^{R}\in{\rm outputs}(C^{R})$. The comparator $(i,j)$ changes
$\bar y$ iff $(n{-}j{+}1,\,n{-}i{+}1)$ changes $\bar y^{R}$, and the two exchanges are mirror images.
$\square$
**Corollary A6′ (reflection + negation).** If $C$ sorts $\bar x$ then $C$ sorts $\rho_n(\lnot \bar x)$,
$\rho_n(i)=n{+}1{-}i$. [2511.04107] Lemma 4 gives the one-line proof: flip every comparator to
max-min, getting $\lnot C$ which sorts $\lnot\bar x$ into reverse order; then reflect.
**Consequence.** The symmetry group acting on prefixes is generated by channel permutations that fix
the first layer, reflection, and negation — this is what turns $46{,}206{,}736$ second layers into
$211$ candidates at $n=16$ ([1412.5302] Table 2).

### A7. Untangling: generalised networks add no power — proved
**Source:** [1310.6271] Lemma 3 (citing Knuth, ex. 5.3.4.16); proof of the step lemma in
[1507.01428] Lemma 11; Parberry cites the result as Theorem 5.1 (Floyd–Knuth).
**Statement.** If $G$ is a generalised sorting network of depth $d$ then there is a sorting network
$C$ of depth $d$; and if $G = P;H$ with $P$ standard then $C = P;I$, i.e. a standard prefix survives.
**Proof.** Let $k$ be the last layer of $G$ containing a max-min comparator $\langle i,j\rangle$
($i>j$). Interchange channels $i$ and $j$ in layers $1..k$; this is a relabelling, so the resulting
network computes the same function up to that transposition and has one fewer inverted comparator.
Iterate. Max-min comparators never disappear from layers after $k$, but each step strictly decreases
the number of inversions in the lexicographic order on layers, so the process terminates. $\square$

### A8. Redundant comparators can be deleted — proved
**Source:** [1507.01428] Lemma 3 (crediting Knuth ex. 5.3.4.51, in turn credited to R. L. Graham);
[2012.04400] §3 (as "a redundant comparator can be replaced by an exchange").
**Statement.** Call $(i,j)$ in $C;(i,j);C'$ *redundant* if $\bar x_i\le\bar x_j$ for all
$\bar x\in{\rm outputs}(C)$. Deleting all redundant comparators yields $C''$ which is a sorting
network iff $C$ is.
**Proof.** For every $\bar x\in B^n$ a redundant comparator is a no-op on the trajectory of $\bar x$
through $C$; removing no-ops leaves trajectories unchanged, so all of them may be removed
simultaneously and $C(\bar x)=C''(\bar x)$ for every $\bar x$. $\square$
**Consequence.** One may restrict to *non-redundant* networks; this is the hypothesis of every
structural theorem in Part C.

### A9. The window bound for a prefix — proved
**Source:** [1501.06946] §3.1; also [1507.01428] §2.5 (the same, phrased as "fix leading zeros and
trailing ones at encoding time").
**Statement.** Let $P$ be a prefix and $\bar x = 0^a\bar x'1^b\in{\rm outputs}(P)$. Any network $S$
extending $P$ to a sorting network need only be checked on the window $\bar x'$, on channels
$a{+}1,\dots,n{-}b$; comparators of $S$ leaving the window are no-ops on $\bar x$.
**Proof.** Apply A3 to $S$ with input $\bar x$: channel $i\le a$ carries $0$ throughout and channel
$j>n-b$ carries $1$ throughout. A comparator $(i,j)$ with $i\le a$ outputs $\min(0,\cdot)=0$ on $i$ and
$\max(0,\cdot)=\cdot$ on $j$ — a no-op; dually for $j>n-b$. $\square$

---

# Part B. Normal forms at the front of an optimal network

The strategy of [1310.6271], [1412.5302] and everything downstream: show that if *any* depth-$d$
sorting network exists then one exists whose first two layers lie in an explicitly computable small
set, then search that set by SAT. B1–B2 are the engine; B3–B9 are the consequences.

### B1. Subsumption (output containment) — proved
**Source:** [1310.6271] Lemma 2; [1405.5754] Lemma 2; [2511.04107] Lemma 2.
**Statement.** Let $P;S$ be a sorting network of depth $d$ and $Q$ a network with
$\mathrm{depth}(Q)=\mathrm{depth}(P)$ and $\mathrm{outputs}(Q)\subseteq\mathrm{outputs}(P)$. Then
$Q;S$ is a sorting network of depth $d$.
**Proof.** For $\bar x\in B^n$, $Q(\bar x)\in\mathrm{outputs}(Q)\subseteq\mathrm{outputs}(P)$, so
$Q(\bar x) = P(\bar y)$ for some $\bar y$; then $S(Q(\bar x)) = S(P(\bar y))$ is sorted because $P;S$
is a sorting network. Depth is unchanged because the prefixes have equal depth. $\square$
**Reading.** A prefix is only ever used through its output set. Hence "which prefixes must I try" is
a question about a preorder on output sets — this is the single most important structural idea in
the modern literature, and it is a six-line proof.

### B2. Subsumption up to permutation — proved
**Source:** [1310.6271] Lemma 7; [1412.5302] Lemma 7; [2511.04107] Lemma 3.
**Statement.** If $\mathrm{outputs}(Q)\subseteq\pi(\mathrm{outputs}(P))$ for some permutation $\pi$,
and $P;S$ is a sorting network of depth $d$, then there is $S'$ with $Q;S'$ a sorting network of
depth $d$.
**Proof.** $\pi(P;S)$ is a generalised sorting network by A7, and
$\mathrm{outputs}(Q)\subseteq\mathrm{outputs}(\pi(P))$, so B1 gives that $Q;\pi(S)$ is a generalised
sorting network; untangle it by A7, which preserves the standard prefix $Q$. $\square$
Write $Q\preceq P$ for this relation ("$Q$ subsumes $P$"); it is a preorder refining A6's symmetry.

### B3. The first layer may be taken maximal — proved
**Source:** [1310.6271] §3.2 (stated), immediate from B1.
**Statement.** If a depth-$d$ $n$-channel sorting network exists, one exists whose first layer is
maximal (contains $\lfloor n/2\rfloor$ comparators).
**Proof.** Let $C=L_1;N$, and let $L_1^+\supseteq L_1$ be maximal. Adding comparators can only shrink
the output set, so $\mathrm{outputs}(L_1^+)\subseteq \mathrm{outputs}(L_1)$; B1 with $P=L_1$,
$Q=L_1^+$ gives $L_1^+;N$ a sorting network of the same depth. $\square$

### B4. Parberry's lemma: *any* maximal layer can be the first layer — proved
**Source:** [1310.6271] Lemma 5, citing Parberry; proof reproduced there.
**Statement.** Let $L$ be any maximal layer. If a depth-$d$ sorting network exists, one exists whose
first layer is exactly $L$.
**Proof.** Let $C=L_1;N$ be a sorting network; by B3 assume $L_1$ maximal. Both $L_1$ and $L$ are
maximal, so there is a permutation $\pi$ with $\pi(L_1)=L$. Then $\pi(C)$ is a generalised sorting
network (permuting channels turns min-max comparators into max-min ones but preserves sortedness up
to a fixed output permutation), $\pi(C) = L;\pi(N)$, and A7 untangles $\pi(N)$ while keeping the
standard prefix $L$. $\square$
**Consequence.** One layer is free: fix $L = F_n = \{(i,\lceil n/2\rceil+i) : 1\le i\le\lfloor n/2\rfloor\}$
(or Parberry's $L^1_P = \{(2i-1,2i)\}$, related by a permutation).

### B5. Parberry's second-layer lemma — proved
**Source:** [1310.6271] Lemma 6, attributing Parberry, Thm. 5.4.
**Statement.** Let $\pi(F_n)=F_n$ and let $L$ be a layer with $\pi(L)$ a layer. If a depth-$d$
network with first layer $F_n$ and second layer $L$ exists, one with second layer $\pi(L)$ exists.
**Proof.** $\pi$ fixes the first layer, so $\pi(F_n;L) = F_n;\pi(L)$, and $\pi$ of a (generalised)
sorting network is a generalised sorting network; untangle. $\square$
**Consequence.** The second layer lives in the orbit space $G_n/H_n$, where
$H_n=\mathrm{Stab}(F_n)$: $35{,}696$ layers at $n=11$ become $1{,}134$ candidates; $568{,}504$ at
$n=13$ become $4{,}288$ ([1310.6271] Fig. 3).

### B6. Odd $n$: every layer is dominated by a *saturated* layer — proved
**Source:** [1310.6271] Lemma 8 and Lemma 9 (this is the conference paper's own contribution to the
prefix theory; the notion of "saturated" here is the syntactic one — see the caution at the top).
**Definitions.** $L$ is *saturated* if it contains no comparator of $F_n$ and its unused channels are
either all min-channels or all max-channels of comparators of $F_n$; $S_n$ is the set of saturated
layers; $R(S)$ denotes representatives of $S$ modulo $H_n$; $R_{po}(S)$ denotes a minimal set of
$R_{po}$-representatives as in B2.
**Statement.** For odd $n$ and every layer $L$ there is a saturated $S$ with $S\preceq L$; hence
$R_{po}(G_n) = R_{po}(R(S_n))$.
**Proof.** Delete from $L$ all comparators that also occur in $F_n$; this changes nothing, since they
re-compare already-compared pairs, so $\mathrm{outputs}(F_n;L)$ is unchanged. If the result is not
saturated, one of two things holds.
(i) The unused channels are not all of one type: there is an unused min-channel $i\le\lfloor n/2\rfloor$
and an unused max-channel $j\ge\lceil n/2\rceil+1$ with $\langle i,j\rangle\notin F_n$ — for odd $n$,
$F_n$ leaves only the middle channel free, so this is the generic case. Add $c=\langle i,j\rangle$,
getting $L_1$. If $(F_n;L_1)(\bar x)\ne (F_n;L)(\bar x)$ for some $\bar x$, then $(F_n;L)(\bar x)$ has
$1$ on $i$ and $0$ on $j$ and $c$ flips exactly these. Since $i$ is the min-channel of
$\langle i,i+\lceil n/2\rceil\rangle\in F_n$, both $i$ and $i+\lceil n/2\rceil$ are $1$ in $\bar x$;
dually both $j$ and $j-\lceil n/2\rceil$ are $0$. Changing $\bar x$ to $\bar x'$ with $\bar x'_i=0$,
$\bar x'_j=1$ propagates so that $(F_n;L)(\bar x') = (F_n;L_1)(\bar x)$. Hence
$\mathrm{outputs}(F_n;L_1)\subseteq\mathrm{outputs}(F_n;L)$.
(ii) The unused channels are all min- or all max-channels; then the only addable comparator touches the
one channel $\lceil n/2\rceil$ left free by $F_n$, and the same bit-moving exchange argument applies.
Iterating, $\mathrm{outputs}(F_n;S)\subseteq\mathrm{outputs}(F_n;L)$, i.e. $S\preceq L$. $\square$
**Reading.** The proof is a *simulation*: any output reachable with the extra comparator is reachable
without it by moving one bit in the input. That is the same trick as the six-pattern arguments of B8.

### B7. Two-layer networks are words: a complete invariant — proved
**Source:** [1412.5302] Lemma 5, Theorem 1; [1806.00305] Lemma 1.
**Statement.** Two two-layer networks $C,C'$ (with first layer $F_n$) are isomorphic as comparator
graphs iff $\mathrm{word}(C)=\mathrm{word}(C')$; and for $n\ge3$ the set $R(G_n)$ of
representatives is a complete set of filters.
**Proof (of the invariant).** In a two-layer network every comparator has out-degree $\le 2$ and
in-degree $\le 2$, so the graph is a disjoint union of paths and cycles; the word of a maximal path
records, channel by channel, whether the channel is free ($0$), a min-channel ($1$) or a max-channel
($2$) of the first layer. Two networks have isomorphic graphs iff their path multisets agree, and a
path is determined by its word up to reversal, which the normal form fixes by taking the
lexicographically smaller of the two directions. $\square$
**Theorem B7′ (counts).** $R(G_n)$ is generated by a context-free grammar (head/stick/cycle words) and
for odd $n$ satisfies $|R(G_n)| = |R(G_{n-1})| + 2\,|R(G_{n-2})|$.
**Proof.** For odd $n$ exactly one word starts with $0$ (the free channel); if it is $0^{\mathsf h}$,
deleting it gives a network on $n-1$ channels; otherwise deleting its last two letters, which are
$12$ or $21$, gives a network on $n-2$ channels, with two choices.$\square$

### B8. Saturation in the output-minimality sense: six forbidden patterns — proved
**Source:** [1412.5302] Definitions 7, Theorem 3, Theorem 4, Theorem 5, Corollary 2, Theorem 6.
**Definitions.** $C$ is *redundant* if deleting a comparator yields $C'$ with
$\mathrm{outputs}(C')=\pi(\mathrm{outputs}(C))$; $C$ is *saturated* if it is non-redundant and no
single added comparator yields $C'$ with $\mathrm{outputs}(C')\subseteq\pi(\mathrm{outputs}(C))$.
**Theorem (necessity).** A saturated two-layer network contains none of the six patterns of
[1412.5302] Fig. 6.
**Proof (pattern 1a; the other five are the same simulation).** Let $a,b,c$ be the three channels of
the pattern, $b$ a max-channel and $c$ a min-channel with $(a,b),(b,c)$ in layer 1 and $b$ unused in
layer 2. Add $(c,b)$, getting $C'$. If $C'(\bar x)\neq C(\bar x)$ then $C(\bar x)$ has $1$ on $c$ and
$0$ on $b$ at layer 1, which forces $\bar x_a=\bar x_b=0$ and $\bar x_c=1$; swapping the values of
$\bar x$ at $b$ and $c$ gives $\bar x'$ with $C(\bar x') = C'(\bar x)$. Hence
$\mathrm{outputs}(C')\subseteq\mathrm{outputs}(C)$, contradicting saturation. $\square$
**Theorem (sufficiency, converse).** A non-redundant two-layer network containing none of the six
patterns is saturated. *(Proof: an eight-case analysis on whether the two unused channels are min- or
max-channels, each case producing an explicit input whose output under $C'$ cannot arise under $C$;
[1412.5302] Thm. 5.)*
**Corollary B8′.** The set of saturated two-layer networks — and its set of representatives — is a
complete set of filters, i.e. if a depth-$d$ sorting network exists then one exists whose first two
layers are saturated. **Proof.** By the sufficiency theorem plus B1 (take an arbitrary non-redundant
prefix; if a pattern occurs, add the corresponding comparator; repeat).$\square$
**Conjecture (open, [1412.5302] Conj. 1).** Saturated $\Rightarrow$ subsumption-minimal; verified for
$n\le15$. This is the boundary of what the theory currently proves.

### B9. Reflection, and the final representative sets — proved
**Source:** [1412.5302] Corollary 4, Theorem 7, Corollary 5; [2511.04107] Corollary 2.
**Statement.** If $C\approx C'$ or $C'\approx C^{R}$ then either may be kept; hence the representative
sets $R_n$ of [1412.5302] Def. 8 are complete sets of filters, with
$|R_{16}| = 211$, $|R_{17}| = 609$, $|R_{19}| = 1367$.
**Proof.** A6 gives $\bar x\in\mathrm{outputs}(C)\iff \bar x^{R}\in\mathrm{outputs}(C^{R})$, i.e.
reflection transports output sets; combined with B1 the two prefixes are interchangeable.$\square$
**Reflection-symmetric refinement** ([2511.04107] Cor. 2): if both $P$ and $P'$ are
reflection-symmetric and $\sigma(\mathrm{outputs}(P'))\subseteq\mathrm{outputs}(P)$ for a
reflection-symmetric permutation $\sigma\in C(\rho_n)\cong C_2\wr S_{n/2}$, then the extension $S'$ can
be taken reflection-symmetric. This is what makes a 28-channel search feasible today.

---

# Part C. Normal forms at the back of an optimal network

All of Part C is [1507.01428] (Codish–Cruz-Filipe–Ehlers–Müller–Schneider-Kamp). This is the paper
that made $D(17)=10$ reachable, and the only part of the ten-paper corpus where a *structural*
theory of sorting networks is developed rather than a search heuristic.

### C1. The last layer compares only neighbours — proved
**Statement.** In a non-redundant $n$-channel sorting network, every comparator of the last layer is
of the form $(i,i+1)$.
**Proof.** Suppose the last layer contains $c=(i,i+2)$ (the argument for $(i,i+k)$, $k\ge2$, is the
same). As $c$ is not redundant there is an input whose values on channels $i,i+1,i+2$ just before $c$
are $(1,\cdot,0)$ — case (a) — with $1$ above $0$. Let $\bar y$ be obtained from that input by
changing one $0$ to $1$. By A2 the top input of $c$ stays $1$, and by sortedness of the output the
bottom input of $c$ must still be $0$: case (b). Dually, from case (b) changing one $1$ to $0$ returns
to case (a). So all inputs with the same number of zeros as $\bar x$ or $\bar y$ give case (a) or (b);
in particular some *sorted* input does. But sorted inputs are fixed points (A3), so no comparator can
see $1$ above $0$ there. Contradiction. $\square$

### C2. Non-adjacent comparators must be followed — proved
**Statement** (Corollary 1). If a non-redundant network has $(i,j)$ at layer $d$ with $j>i+1$, then
at least one of $i,j$ is used in a layer after $d$.
**Proof.** Otherwise $(i,j)$ can be moved to the last layer without changing the function, and C1
forbids it there. $\square$

### C3. Counting the possible last layers — proved
**Statement** (Theorem 1). The number of possible last layers of a non-redundant $n$-channel sorting
network is $L_n = F_{n+1}-1$ (Fibonacci, $F_1=F_2=1$). For $n=17$: $L_{17}=2583$.
**Proof.** Let $L^+_n$ count last layers allowing the empty one. Either channel $1$ is unused
($L^+_{n-1}$ ways for the rest) or it is compared with channel $2$ ($L^+_{n-2}$ ways), giving
$L^+_n = L^+_{n-1}+L^+_{n-2}$ with $L^+_1=F_2$, $L^+_2=F_3$; so $L^+_n=F_{n+1}$ and
$L_n=F_{n+1}-1$. $\square$
Compare with the $211{,}799{,}312$ arbitrary layers at $n=17$: the last layer is a factor $10^5$
cheaper than the second.

### C4. The block lemma — proved, but only for **non-redundant** networks
**Definitions.** For $k<d$ and a network $C$ **without redundant comparators**, the *$k$-blocks* of
$C$ are the connected components of the graph on channels whose edges are the comparators in layers
$k+1..d$; they partition the channels, and values cannot cross between blocks after layer $k$.
$C$ is *non-redundant* if no comparator can be deleted without changing the function ([1507.01428]
Def. 1; Lemma 3 there: deleting redundant comparators preserves being a sorting network).
The hypothesis is **not** cosmetic: [1507.01428] Definition 2 introduces $k$-blocks only for networks
without redundant comparators, and both this statement and C6′ fail without it. Counterexample
(4 channels, depth 3, every layer maximal, so depth-optimal):
$$(1,3)(2,4)\;;\;(1,2)(3,4)\;;\;(1,4)(2,3).$$
It sorts; on the input $1100$ the state after two layers is $0011$, and the two $2$-blocks $\{1,4\}$
and $\{2,3\}$ both receive a $0$ and a $1$ — blocks are not intervals and two of them are mixed at
once. The culprit is the redundant comparator $(1,4)$: deleting it still sorts.
(Found by swarm member m3; verified here.)
**Statement** (Lemma 5). For every input, **at most one** $k$-block receives both a $0$ and a $1$.
**Proof.** Values cannot move between blocks. If block $B$ receives both values then every block above
$B$ must output only $0$s and every block below only $1$s, for the output to be sorted; and those
outputs *are* the block's inputs. $\square$
**Two cautions.** (i) The proof uses "above" and "below", i.e. it presupposes that blocks are
intervals (C6′); in [1507.01428] the order of the argument runs the other way (Lemma 5 is used for
Lemma 6 and Theorem 2, whence the interval property), so the paper's derivation is at least
apparently circular. (ii) The statements themselves survive: they are consistent with an exhaustive
check over all non-redundant sorting networks on $n\le6$ channels (m3). The safe form to quote is:
**non-redundance $\Rightarrow$ blocks are intervals and at most one is mixed.**
**Reading.** This is the single most useful lemma in the paper: it says a $k$-block boundary is a
"cut" that is sorted except at one place, and it is what a lower-bound argument would have to exploit.

### C5. The penultimate layer spans at most three channels — proved (sketch)
**Statement** (Lemma 6). In a non-redundant sorting network, every comparator of layer $d-1$ connects
*adjacent blocks*.
**Proof.** Let $c$ connect blocks $X$ (above) and $Z$ (below), with $Y$ the channels in between. $c$
cannot lie inside one block (it would be repeated in the last layer and hence redundant). As $c$ is
not redundant some input gives it $1$ over $0$. Lemma C4 restricts $(X,Y,Z)$ to the five
configurations "all $0$ / mixed / all $1$" with at most one mixed; monotonicity (A2) lets one move
between them changing one bit at a time, which propagates the pattern to all inputs with the same
number of zeros — including sorted ones, which is impossible by A3. $\square$
**Corollary C5′** (Corollary 2). Every comparator $(i,j)$ in layer $d-1$ has $j-i\le3$; if $j=i+2$
then $(i,i+1)$ or $(i+1,i+2)$ occurs in the last layer; if $j=i+3$ then both $(i,i+1)$ and
$(i+2,i+3)$ occur. The bound $3$ is attained (networks in [1507.01428] Fig. 5).

### C6. The same, for every layer — proved
**Statement** (Theorem 2). If $C$ is non-redundant and $(i,j)$ is a comparator at layer $k$, then $i$
and $j$ lie in the same $k$-block or in adjacent $k$-blocks.
**Proof.** Repeat C5 with $k$-blocks in place of blocks. $\square$
**Corollary C6′** (Corollary 3). For $C$ **non-redundant**: all $k$-blocks are intervals of channels,
and a $k$-block containing $m$ comparators spans at most $m+1$ channels.
**Proof.** By induction on $m$, splitting on whether the first comparator at layer $k+1$ lies inside a
$(k+1)$-block or joins two of them; the step uses Theorem 2 of [1507.01428] ("a comparator at layer
$k$ joins channels in the same $k$-block or in adjacent $k$-blocks"), which is where non-redundance
enters. See C4 for the counterexample showing that the hypothesis cannot be dropped. $\square$
**Reading.** C6′ is a quantitative statement about *how much sorting a suffix of given size can do* —
the only such statement in the corpus, and still too weak to give $D(17)>9$.

### C7. Last-layer normal form — proved
**Statement** (Lemma 7). Every sorting network $C$ has a sorting network $N$ of the same depth whose
last layer (i) contains only adjacent comparators and (ii) has no two adjacent unused channels.
**Proof.** Delete redundant comparators (A8) getting $S$; by C1 its last layer is adjacent-only. If
$j,j+1$ are both unused in the last layer, then $(j,j+1)$ is redundant there, so add it; repeat. $\square$

### C8. Counting last layers in normal form — proved
**Statement** (Theorem 3). The number of last layers in last-layer normal form is $K_n = P_{n+5}$,
$P$ the Padovan sequence ($P_0=1$, $P_1=P_2=0$, $P_{n+3}=P_n+P_{n+1}$). For $n=17$: $K_{17}=86$
against $L_{17}=2583$.
**Proof.** Split on whether channel $1$ is used: $K_n = K^+_n+K^-_n$ with $K^+_n = K_{n-2}$ (a
comparator on $1,2$ leaves $n-2$ channels) and $K^-_n = K^+_{n-1}$ (channel $1$ free forces channel
$2$ used), so $K_n = K_{n-2}+K_{n-3}$, with $K_1=P_6$, $K_2=P_7$, $K_3=P_8$. $\square$

### C9. Adding comparators at the back is safe — proved
**Statement** (Lemma 8). If $C$ is in last-layer normal form and $i<j$ are unused in layer $d-1$ and
lie in different blocks, then adding $(i,j)$ to layer $d-1$ still gives a sorting network.
**Proof.** If some input had $1$ on channel $i$ and $0$ on channel $j$ at layer $d-1$, then since both
channels are unused their blocks carry those values to the output, which would then not be sorted
(block of $i$ is above block of $j$). So the comparator is redundant there. $\square$

### C10. Co-saturation — proved
**Definitions** ([1507.01428] Def. 3). $C$ of depth $d$ is *co-saturated* if (i) its last layer is in
last-layer normal form, (ii) no two consecutive $(d-1)$-blocks have unused channels, (iii) if
$(i,i+1)$ is in layer $d$ with $i,i+1$ unused in layer $d-1$, then $i-1$ and $i+2$ are used in layer
$d$.
**Statement** (Theorem 4). Every sorting network $C$ of depth $d$ can be transformed into a
co-saturated sorting network of the same depth.
**Proof.** Put $S$ in last-layer normal form (C7), let $B_1,\dots,B_k$ be the $(d-1)$-blocks, and for
each adjacent pair with a free channel add a comparator between them (C9 makes this safe). Then
correct violations of (iii) by the transformation of Lemma 9: if $(i,i+1)$ is in layer $d$ with
$i,i+1$ unused in $d-1$ and $i+2$ used in $d-1$ but not $d$, move $(i,i+1)$ to layer $d-1$ (possible
because both channels are free there) and add the now-redundant $(i+1,i+2)$ to layer $d$. $\square$
**Counts.** Co-saturated two-layer suffixes: $45{,}664$ at $n=17$, against $211{,}799{,}312$ arbitrary
two-layer networks. This is the "co-saturation" that makes the $17$-channel SAT instances finish.

### C11. Co-subsumption, and the duality front $\leftrightarrow$ back — proved
**Definitions.** $\mathrm{sorts}(C)=\{\bar x : C(\bar x)\text{ sorted}\}$; $C\sqsubseteq C'$ iff
$\pi(\mathrm{sorts}(C))\subseteq\mathrm{sorts}(C')$ for some $\pi$.
**Statement** (Lemma 10). If $C\sqsubseteq C'$ and $N;C$ is a sorting network, then there is a
*generalised* sorting network $N';C'$ of the same depth and size.
**Proof.** Rename channels of $N$ by $\pi$. For any $\bar x$, $N(\bar x)\in\mathrm{sorts}(C)$, so
$\pi(N)(\pi\bar x)\in\mathrm{sorts}(C')$. $\square$
**Corollary C11′** (Corollary 4). There is an optimal-depth generalised sorting network whose last
layer is Parberry's $L^1_P=\{(1,2),(3,4),\dots\}$; by repeated untangling (A7) — here "dual
standardisation", [1507.01428] Def. 4 and Lemma 11 — one that is standard. **Proof of the corollary.**
Given any last layer $C=\{(i_1,j_1),\dots,(i_\ell,j_\ell)\}$, take $\pi$ mapping $i_k\mapsto 2k-1$,
$j_k\mapsto 2k$; then $C\sqsubseteq L^1_P$. $\square$
**Reading.** This is the exact dual of B4: the last layer can be fixed to a maximal layer, just as the
first can. The two cannot be fixed simultaneously in the standard model — fixing the front dictates
what the back may be — which is why the duality is stated for generalised networks.

### C12. The end-game theorems that are actually used
$D(17)=10$ is proved in [1507.01428] §6 as follows: by B9 there are $609$ two-layer prefixes; for each,
add the constraints C1–C10 to the SAT encoding of D4 and refute. Total CPU time
$27.63\cdot10^6$ s, worst instance $97{,}112$ s. The same computation is reported in [1501.06946] §4
with identical timings — the two 2015 papers share authors, so this is one proof, reported twice, not
an independent replication.

---

# Part D. Characterising minimal depth

Depth has **no** theorem of van Voorhis type. Everything below is either trivial, a symmetry reduction,
or a computational statement, and that asymmetry is the honest headline of this compendium.

### D1. The cone bound — proved
**Source:** folklore; the only hand lower bound on depth.
**Statement.** $D(n)\ge\lceil\lg n\rceil$.
**Proof.** Define the *influence set* $I_k(i)\subseteq[n]$ of channel $i$ after $k$ layers: the inputs
on which its value depends. A comparator changes it by $I_{k+1}(i)\subseteq I_k(i)\cup I_k(j)$, so
$|I_k(i)|\le 2^k$. Output $n$ must depend on every input: if input $p$ did not influence it, then the
all-zero input and the input that is $1$ only at $p$ would give the same output $n$, namely $0$ and
$1$. So $2^d\ge n$. $\square$
At $n=17$ this gives $5$ against the true $10$: the bound is useless beyond asymptotics.

### D2. Depth is monotone in $n$ — proved
**Source:** used throughout, e.g. [1310.6271] ("$t_n\ge9$ for $n\ge17$"), [2511.04107] Table 1.
**Statement.** $D(n)\ge D(n-1)$.
**Proof.** Take a depth-$d$ $n$-channel sorting network and prune any channel as in G2. Each layer
contributes at most one comparator to the path, so the pruned network has depth $\le d$ and, by the
argument of G2, sorts $n-1$ channels. $\square$
**Consequence.** $D(17)=10$ alone gives $D(n)\ge10$ for all $n\ge17$ — this is literally how the
lower-bound column of the current tables is filled, out to $n=32$. The depth side has no other
non-computational input.

### D3. Parberry's reach bounds — proved (sketch)
**Source:** Parberry, via [1310.6271] §2 and the statement in Marinov–Gregg (item 8).
**Statement.** Let $C$ be a sorting network of depth $d\ge2$ and $c$ a channel. Define
$\mathrm{To}_C(c,i)$ = $\{c\}$ together with the channels reachable from $(c,i)$ by following
comparators forward through layers $i..d$, $\mathrm{From}_C(c,i)$ the same backwards, and
$\mathrm{Reach}_C(c,i) = \mathrm{To}_C(c,i)\cup\mathrm{From}_C(c,i)$. Then
$|\mathrm{To}_C(c,d-2)|\le4$, $|\mathrm{From}_C(c,d-2)|\le4$, $|\mathrm{Reach}_C(c,d-2)|\le5$.
**Proof.** Two remaining layers give out-degree at most $2$ each, so at most $2^2=4$ channels reachable
forward and, dually, backward. The sharp bound $5$ for $\mathrm{Reach}$ uses that the forward and
backward cones of a channel cannot be disjoint in a network that sorts: if
$(c,d{-}2)$ could reach $5$ distinct channels, two of them would have to be "swapped" by the last two
layers in a way that contradicts sortedness — a short case check over the two-layer patterns.
**Use.** As a necessary condition on a prefix: if some channel's cone already exceeds these bounds, the
prefix cannot be completed. This is the pruning behind Parberry's Cray computation for $D(9)=7$ and,
extended to three and four last layers, behind the independent re-derivation of $D(n)$ for $n\le12$.

### D4. The SAT formula is sound and complete — proved
**Source:** [1310.6271] Lemma 10 and §5; [1501.06946] §3.3; [1507.01428] §2.4–2.5.
**Statement.** With variables $g^k_{i,j}$ ("layer $k$ contains comparator $(i,j)$"), $u^k_i$
("channel $i$ is used in layer $k$") and $v^k_i$ ("value on channel $i$ after layer $k$"), the formula
$$ \Psi(n,d) \;=\; \varphi_{\text{used}}\wedge\varphi_{\text{valid}}\wedge\bigwedge_{\bar x\in B^n}\varphi_{\text{sort}}(\bar x) $$
is satisfiable iff an $n$-channel depth-$d$ sorting network exists; and a satisfying assignment yields
one.
**Proof.** ($\Leftarrow$) read the $g$'s off the network: $\varphi_{\text{valid}}$ holds because layers
are matchings; $\varphi_{\text{sort}}(\bar x)$ holds because the network sorts $\bar x$ and the $v$'s
are forced along the unique propagation. ($\Rightarrow$) conversely, set $v^k$ by propagation; then the
$g$'s define a valid network whose output on each $\bar x$ is sorted. $\square$
**Corollary (the reductions are lossless).** Replacing $B^n$ by $B^n\setminus B^n_s$ (A4), and
restricting the first two layers to a complete set of filters (B8′/B9) or fixing them (B4), preserves
satisfiability. This is what every paper in the list actually runs.

### D5. The exact values, and what their proofs are
Every depth-optimality theorem in the corpus is of the form *"$D(n)=d$"*, proved by: reduction
(Part A–C lemmas) + exhaustiveness of a finite case set + a refutation for each case. The list:

| Statement | Source | Proof |
|---|---|---|
| $D(n)$ optimal for $n\le8$ | Floyd–Knuth 1973 (outside the ten) | no proof in the corpus; see the note below |
| $D(n)$ optimal for $n=9,10$ | Parberry 1991 [item 5] | ⚙ exhaustive search with reach pruning |
| $D(n)$ optimal for $n=11,\dots,16$ | [1310.6271] Thms 12, 13 | ⚙ SAT over $R_{po}(G_n)$, $R_n$ |
| $D(17)=10$ | [1507.01428] Thm 5 (= [1501.06946] Thm 2) | ⚙ 609 UNSAT instances |
| depth upper bounds 17–20 | [1501.06946], [1410.2736] | construction + A1 verification |
| $D(23),D(24)\le12$ | Ehlers 2017 [item 13] | construction |
| $D(27),D(28)\le13$ | [2511.04107] Thm 1, Cor. 3 | construction + SAT for the tail |

**Historical note on $n\le8$** (from outside the ten papers). That row is usually read as the last
conceptual stretch of the subject, and it is not. Harder [2012.04400, §1] records that "the
Bose–Nelson sorting problem was first answered for $n\le8$ by Floyd and Knuth using a computer search
for the $n=7$ case" (Floyd–Knuth, *The Bose–Nelson sorting problem*, 1973). So the first
machine-assisted optimum is $n=7$, not $n=9$. Two qualifiers. (i) Once $n=7$ is known, $n=8$ costs
nothing: $S(8)\ge S(7)+\lceil\lg8\rceil = 16+3 = 19$ by G3, and $D(8)\ge D(7)=6$ by D2 — which is why
"$n\le8$" gets quoted as a single block. (ii) For *depth* specifically I found no statement about
machine use; the attribution to the same paper is Bundala et al.'s, and the depth bounds at $n\le8$
are short enough that a hand case analysis is plausible. The purely hand-settled range is thus
$n\le6$, and even there the arguments are exhaustive case distinctions, not structural explanations
of why the value is what it is.

### D6. Where the ten papers stop
- $D(n)$ is known exactly only for $n\le17$; for $18\le n\le32$ the best lower bound is still $10$
  (D2 applied to $D(17)$) while upper bounds run $11$–$14$.

---

# Part E. What none of the ten papers characterises

### E1. No structural theorem separates $d-1$ from $d$
For $n=17$ the hand-provable bounds are $\max(\lceil\lg17\rceil,\ \lceil S(17)/\lfloor17/2\rfloor\rceil)
= \max(5,\lceil58/8\rceil) = 8$ — using D1 and G1 with van Voorhis's $S(17)\ge58$ from G3 — against the
true value $10$. Nothing in Parts B–C is sensitive enough: the block lemma (C4) and the span-3 bound
(C5′) constrain the *ends*, and no lemma constrains the middle layers of an optimal network at all.

### E2. The one structural conjecture in the corpus is open
[1412.5302] Conjecture 1: saturated two-layer networks are exactly the subsumption-minimal ones
(verified $n\le15$). A proof would unify B1 and B8 into a single canonical form; its absence is the
cleanest measure of how far the theory is from a conceptual lower bound.

### E3. The trust boundary
Every ⚙ item here — D3 (Parberry's Cray search), the SAT refutations behind D5, and the construction
searches — is a *solver or search answer*, not a certificate: none of these papers ships a proof log,
so the reader who wants certainty audits the reduction (A1–A9, B1–B9, C1–C12, D1–D4) and the claim
that the case set is exhaustive. Two concrete caveats. First, $D(17)=10$ is a *single* computation
reported in two 2015 papers with identical timings and overlapping author lists — not an independent
replication; what was independently re-derived is $D(n)$ for $n\le16$ (by a different prefix
generation, and by Marinov–Gregg's non-SAT pruned search, item 8) and $D(9)=D(10)=7$
(Parberry, then by everyone). Second, an end-to-end auditable proof of an exact optimum *does* exist
in this subject, but on the size side: Harder's derivation chains, checked by an Isabelle/HOL-verified
program (S11 of the companion). Nothing comparable exists for any depth-optimality result.

Parberry, whose 1989 search is the first fully exhaustive one in this subject, put the epistemic
point plainly: "There is much contention in the mathematical community over whether such a
computer-assisted 'proof' of nonexistence really constitutes a proof in the formal sense. We prefer
to regard this type of result as experimental computer science rather than mathematics."
---

# Part G. Appendix: the three size facts that bear on depth

Kept out of the split for one reason only: each converts something about comparators into something
about layers. Everything else about minimal size is in `sorting-networks-size.md`.

### G1. A layer holds at most $\lfloor n/2\rfloor$ comparators — proved
**Statement.** $\mathrm{size}(C)\le \mathrm{depth}(C)\cdot\lfloor n/2\rfloor$; hence
$$ D(n)\ \ge\ \Bigl\lceil S(n)/\lfloor n/2\rfloor \Bigr\rceil . $$
**Proof.** A layer is a matching on $n$ channels, so it has at most $\lfloor n/2\rfloor$ comparators.
$\square$
**Use.** Every size lower bound is a depth lower bound, and this is the only route from the size
theory into $D$. At $n=17$: $S(17)\ge58$ from G3 gives $D(17)\ge\lceil58/8\rceil=8$, still two short.

### G2. Pruning a channel — proved
**Source:** [2012.04400] Definition 13, Lemma 16 (stated here because D2's proof uses it).
**Statement.** For a sorting network $c$ on $n$ channels and any channel $i$, delete the wire that
starts at input $i$, follows the **max** output of every comparator it meets and ends at output $n$;
each comparator on that path loses one input and one output and is short-circuited. The result
$c/i$ is a sorting network on $n-1$ channels.
**Proof.** The deleted path is the trajectory of the value $1$ when $c$ is applied to the one-hot
input $\langle i\!:\!n\rangle$, and it ends at output $n$ because $c$ sorts. By monotonicity (A2) the
path carries $1$ for every input with $\bar x_i=1$, so each comparator on it passes its other input
to its other output — exactly what the short-circuit does. Hence
$(c(\bar x))/i = (c/i)(\bar x/i)$ for all $\bar x$ with $\bar x_i=1$; every $\bar y\in B^{n-1}$ is
such a $\bar x/i$, and $(c/i)(\bar y)$ is a subsequence of the sorted $c(\bar x)$, hence sorted.
$\square$

### G3. Van Voorhis's recursion — proved
**Source** van Voorhis 1972; [2012.04400] Lemma 17; [1405.5754] Lemma 1 states the shifted form.
**Statement.** $S(n)\ge S(n-1)+\lceil\lg n\rceil$.
**Proof.** For every channel $i$, $c/i$ is an $(n-1)$-channel sorting network (G2) obtained by deleting
$\delta(c,i)$ comparators, so $S(n)\ge S(n-1)+\delta(c,i)$, hence $S(n)\ge S(n-1)+\max_i\delta(c,i)$.
The union of the pruned paths, with the common output removed, is a binary tree whose leaves are the
$n$ inputs, whose internal nodes are comparators, and in which leaf $i$ has depth $\delta(c,i)$. A
binary tree with $n$ leaves has height $\ge\lceil\lg n\rceil$. $\square$
**Consequences.** Iterating gives $S(n)\ge n\lg n-O(n)$ — with the AKS construction this is the whole
of the asymptotic statement $S(n)=\Theta(n\lg n)$, and it is a hand theorem. Numerically, from the
computed bases $S(9)=25$, $S(10)=29$ it yields $33,37,41,45,49,53,58,63,68,73$ for $n=11,\dots,20$,
which is every published size lower bound above $n=10$.

---

# Coverage by paper

| Paper (rank in the 15-entry reading list) | Items contributed |
|---|---|
| Bundala–Závodný, LATA 2014 (1) | B1, B3–B6, plus the conference-level counts quoted in B5 (A1 imported) |
| Codish et al., JCSS 2019 (2) | A2, A3, A8, C1–C12 (the front/back duality is C11) |
| Codish et al., ICTAI 2014 (3) | size only — see `sorting-networks-size.md`, S11 |
| Harder 2020 (4) | size only — S1–S10 there; his pruning lemma is quoted here as G2 and his van Voorhis proof as G3; his Isabelle-checked certificate is the trust benchmark in E3 |
| Parberry 1991, *depth lower bound* (5) | B4, B5 (origin), D3, D5 ($D(9)=D(10)=7$) |
| Van Voorhis 1972 (6) | G3 here, S7 in the companion — the only theorem-level lower bound |
| Codish–Cruz-Filipe–Schneider-Kamp, SYNASC 2014 (7) | the prefix sets quantified over in B5 and B9: the 211 and 609 figures |
| Marinov–Gregg 2015 (8) | D3 (cone bounds extended to three and four last layers) and the only independent re-derivation of D5's $n\le12$ rows |
| Valsalam–Miikkulainen 2013 (9) | no lemma-level content: an upper-bound heuristic; its symmetry operations are A5/A6 used operationally |
| Ehlers–Müller 2014/15 (10) | A9, D4 (encoding optimisations), D5 (upper bounds; the $D(17)$ lower bound) |
| Fonollosa 2018, *joint size–depth* (11) | no item in scope: its question is size-at-a-given-depth (Pareto), not $D(n)$ |
| Fonollosa 2018, *encodings* (12) | D4 (encoding family) and exact optima outside the plain model |
| Ehlers 2017 (13) | construction only; no characterisation theorem |
| Wang 2025 (14) | A6′ (reflection+negation), B9 (reflection-symmetric subsumption), D5 (upper bounds) |
| Parberry 1991, *verification complexity* (15) | E3 — the reason there is no certificate to audit |
| Bundala et al., JCSS 2017 [1412.5302] | B2, B7, B8, B9 — the full proofs behind item 1 |

Ranks are those of the reading list as extended on 2026-11-14; if it is re-ranked again, the item IDs
above are the stable thing to follow. Five items are not in any of the fifteen papers and are proved
here: A4, A5, D1, D2, plus G1. They are elementary; everything else carries its source.
