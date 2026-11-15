# Proving $D(11)\ge8$, strategy A: the block lemma and the first layer

Companion to `depth-lower-bounds-small-n.md`, which carries the toolbox (items T1–T11, C1, C7, C8 and
Lemmas H, F, G are numbered there). **See `d11-handoff.md` first** for why $D(11)\ge8$ is hard and which
strategies have failed. This document is one of three attempts; the other two are
`d11-image-size-route.md` and `d11-compression-structure.md`.

**Status: no proof.** The strategy reduces $D(11)\ge8$ to a single, much smaller statement (R) and shows
that (R) is *equivalent* to $D(11)\le7$ — so nothing is lost, but nothing is gained either: (R) is
settled only by SAT. What the strategy does deliver is Lemma H, which is a genuine theorem about
depth-optimal networks, and two corrections to the corpus.

---

## 1. The block lemma, and the hypothesis the corpus dropped

[1507.01428] proves a *block lemma*: for $k<d$ the $k$-blocks of a network are the connected components
of the graph on channels formed by the comparators of layers $k+1..d$; blocks are intervals, values never
cross them after layer $k$, and for every input at most one block is mixed.

**The non-redundance hypothesis is essential.** [1507.01428] Definition 2 introduces $k$-blocks only for
networks *without redundant comparators*, and the interval property is Corollary 3 under that hypothesis.
Our own compendium (`sorting-network-lemma-compendium.md`, items C4 and C6′) had dropped it, and the
version without it is false. Counterexample (4 channels, depth 3, every layer maximal, so depth-optimal):

$$(1,3)(2,4)\;;\;(1,2)(3,4)\;;\;(1,4)(2,3).$$

It sorts. On the input $1100$ the state after two layers is $0011$, and the two $2$-blocks $\{1,4\}$ and
$\{2,3\}$ both carry a $0$ and a $1$ — blocks are not intervals and two are mixed at once. The culprit is
the redundant comparator $(1,4)$: deleting it still sorts. Six inputs (all six of weight 2) give two mixed
$2$-blocks.

**A second caution.** [1507.01428]'s own derivation is at least apparently circular: Lemma 5's proof uses
"above" and "below", i.e. it presupposes that blocks are intervals, while Theorem 2 derives the interval
property *from* Lemma 5. The statements survive (they are consistent with an exhaustive check over all
non-redundant networks for $n\le6$), but the printed proof does not establish them.

**Consequence for any proof of $D(11)\ge8$.** The two normal forms are separately free and **jointly not
available**: deleting redundant comparators preserves sorting and depth (so non-redundance is free), and
maximalising layers preserves sorting (so maximal layers are free), but maximalising can *create*
redundancy. Any argument must pick one. §1 of the present strategy picks non-redundance and drops
maximality; the size strategy does the reverse, in that order (see `d11-image-size-route.md` §1).

---

## 2. Lemma H: the first layer is forgotten

> **Lemma H.** Let $N$ sort $n\ge3$ channels. If every layer is a **maximal** matching then the comparators
> of layers $2,\dots,d$ form a **connected** graph on $[n]$, for every $n$. For **odd** $n$ no hypothesis
> is needed at all beyond "$L_1$ is a matching".

Equivalently, for odd $n$: after the first layer the network is a single communicating block, so the only
thing the rest of the network sees is the reachable set $\mathrm{image}(L_1)$.

### 2.1 Proof 1 (odd $n$): partition the first layer

Put $L_1$ down and classify the channels: $Z$ = unused by $L_1$, $L$ = smaller endpoints, $H$ = larger
endpoints. These partition $[n]$ and $Z\ne\emptyset$ because $L_1$ is a matching on an odd number of
channels.

* **One-hot inputs.** For $c\in Z\cup H$ the input $e_c$ still has its single $1$ at $c$ after layer 1: if
  $c\in Z$ nothing touches it; if $c\in H$ its comparator $(p_c,c)$, $p_c<c$, carries $(\cdot,1)$ and puts
  the max, i.e. $1$, on $c$. Values never leave a component, and the sorted output of a weight-1 input has
  its $1$ at channel $n$. Hence $n\in C(c)$ for every $c\in Z\cup H$.
* **One-cold inputs.** Dually, for $c\in Z\cup L$ the input $\mathbf1-e_c$ still has its single $0$ at $c$
  after layer 1, and the sorted output has its $0$ at channel $1$. Hence $1\in C(c)$ for every
  $c\in Z\cup L$.

Pick $z\in Z$: then $n\in C(z)$ and $1\in C(z)$, so $C(1)=C(n)=:C$. For $c\in H$, $c\in C(n)=C$; for
$c\in L$, $c\in C(1)=C$; and $Z\subseteq C$. Since $Z\cup L\cup H=[n]$, every channel lies in $C$. $\square$

### 2.2 Proof 2 (counting ones on a component)

Take $L_1$ maximal, so exactly one channel $z$ is idle. A component $C$ never exchanges values with its
complement after layer 1, so it only permutes its own values; since the final output is sorted, for every
input the number of $1$s on $C$ after layer 1 equals $c(w)=\#\{i\in C:\ i\ge n-w+1\}$, where $w$ is the
input's weight. If $2|C|-(\text{1 if }z\in C\text{ else }0)<n$ there is a channel $t\notin C$ paired (or
idle) outside $C$, and then

* $x=e_t$ gives $0$ on all of $C$ after layer 1, so $c(1)=0$, i.e. $n\notin C$;
* $x=\mathbf1-e_t$ gives $1$ on all of $C$, so $c(n-1)=|C|$, i.e. $1\notin C$;
* $x=e_a$ for $a\in C$ keeps the $1$ on $a$ iff $a$ is the *larger* end of its pair, so $c(1)=0$ forces
  every $a\in C$ to be a smaller end;
* $x=\mathbf1-e_a$ keeps the $0$ on $a$ iff $a$ is the *smaller* end, so $c(n-1)=|C|$ forces every
  $a\in C$ to be a larger end.

A contradiction, so $|C|>(n-1)/2$; two components would then hold more than $n-1$ channels. $\square$

### 2.3 Proof 3 (the even case, which Proofs 1–2 do not reach)

Proof 1 needs an idle channel, so for even $n$ it gives only "every component contains $1$ or $n$". Let
$m=n/2$, $L=\mathrm{high}(M_1)$, $H=\mathrm{low}(M_1)$, so $L\cup H=[n]$, $L\cap H=\emptyset$,
$|L|=|H|=m\ge2$.

* For $S\subseteq L$ the vector $\mathbf1_S$ lies in $V(M_1)$ (all of $\mathrm{low}(M_1)$ is $0$) and is
  fixed by layer 1, so the invariant gives $|S\cap C|=|C\cap T_{|S|}|$ for every component $C$. With
  $|S|=1$: a component contains $n$ iff it contains all of $L$.
* For $T\subseteq H$ the vector $\mathbf1_{[n]\setminus T}$ lies in $V(M_1)$ and is fixed by layer 1, so
  $|C\cap T|=|C\cap[1,|T|]|$. With $|T|=1$: a component contains $1$ iff it contains all of $H$.

So every component other than the one containing $L$ is contained in $H$, and is either $H$ or empty. The
only non-connected possibility is $b=2$ with components $L$ and $H$. It cannot occur: take $(a,b)\in M_1$
and $b'\in L\setminus\{b\}$ (possible since $m\ge2$). Then $u=e_b+e_{b'}\in V(M_1)$, so the invariant for
the component $H$ gives $0=|H\cap T_2|=|H\cap\{n-1,n\}|$; while $u'=e_a+e_b\in V(M_1)$ gives
$1=|H\cap T_2|$. Contradiction. $\square$

### 2.4 Proof 4 (parity — the shortest)

With $L_1$ arbitrary and the blocks *intervals*, suppose $b\ge2$. Then $B_1$ does not contain $n$, so for
the one-hot input $e_a$ with $a\in B_1$ the count lemma forces $0$ ones in $B_1$ after layer 1 although
$B_1$ held one before it: the comparator $(a,\cdot)$ leaves $B_1$. Dually $B_b$ does not contain $1$, so
for the one-cold input the count lemma forces $|B_b|$ ones in $B_b$ although it held $|B_b|-1$, so a
comparator enters $B_b$. Interior blocks satisfy both. Hence **every channel is matched by layer 1 outside
its own block**, layer 1 is a perfect matching, and $n$ is even. For odd $n$ that is a contradiction.
$\square$

This one needs the interval property (hence non-redundance, §1); the other three do not. The missing
hypothesis is one line — delete redundant comparators first — and the mechanism is new: *$b\ge2$ forces the
first layer to be perfect, so an odd channel count forces connectivity.*

### 2.5 Verification

Exhaustive over all sorting networks of the relevant depth: $n=3$ (all $64$ layer sequences, $6$ sorting
networks); $n=4$ (all $9$ depth-3 networks over *all* layers, so including non-maximal first layers —
connected in every case); $n=5$ (all $11\,881\,376$ sequences of $5$ layers, $4320$ sorting networks; with
all layers maximal $2730$); $n=6$ (all maximal-layer networks of depth 5, $1080$ sorting networks).
Zero violations. Scripts: `code/conn_test.py`, `code/conn_even.py`; run `code/verify.sh` for all cheap checks.

---

## 3. The reduction to (R)

Assume $N=L_1;\dots;L_7$ sorts 11 channels. By T3 take every layer maximal. Let $M=L_1$; by Lemma H the
6-layer suffix is connected.

$\mathrm{image}(L_1)=\{u\in B^{11}:\ u\text{ has no }10\text{ on any edge of }M\}$ — a matching's map is
the identity on, and onto, the states sorted inside every pair. For a matching with $e$ comparators this set
has $3^e2^{11-2e}$ elements ($486$ when $e=5$).

> **(R)** There is a matching $M$ on 11 channels and a 6-layer network $S$ (each layer a matching of at most
> five comparators) such that $S(u)=\sigma_{|u|}$ for every $u$ with no $10$ on an edge of $M$.

**Proposition.** $D(11)\le7\iff$(R).

*Proof.* ($\Leftarrow$) $M;S$ is a 7-layer network and it sorts every $x$, since $M(x)\in\mathrm{image}(M)$.
($\Rightarrow$) Given a 7-layer $N$, Lemma H makes its suffix connected, i.e. its suffix sorts
$\mathrm{image}(L_1)$, which is (R). $\square$

So $D(11)\ge8$ is equivalent to a statement with **six layers instead of seven and 486 states (for a
near-perfect first layer) instead of 2046 — but a free choice of the first layer**. That is a genuine
change of object, and it is why the block-lemma route is worth recording even though it does not finish.

**Reducing (R) to the near-perfect matchings.** If $M\subseteq M'$ then
$\mathrm{image}(M')\subseteq\mathrm{image}(M)$, so a network sorting $\mathrm{image}(M)$ also sorts
$\mathrm{image}(M')$. Since every matching on 11 channels has at most five comparators and is contained in
a near-perfect one, refuting (R) for all near-perfect $M$ refutes it for every $M$.

Two symmetries that do *not* help: channel relabelling (a comparator $(i,j)$ needs $i<j$), and reflection,
which does carry the sorting predicate ($\mathrm{outputs}(C^R)=\{\bar x^R\}$) but sends an image set to a
**co-image** $\{w: w_c\ge w_d\ \forall (c,d)\in\widetilde M\}$, not the image of the reflected matching.
Relatedly there is **no free dual block lemma**: time reversal and the mirror both destroy sorting
($(1,3)(2,3)(1,2)$ sorts, its time-reverse sends $110\mapsto101$) while channel-reversal-only keeps the
layer order and so cannot move the last layer to the front. That is why the corpus's back-end results are
proofs rather than dualisations.

**A weaker route that is now superseded.** An earlier version reached the same conclusion through the block
lemma plus a combinatorial fact (**Lemma F**: for odd $n$, every near-perfect matching $M$ and every
partition of $[n]$ into $b\ge2$ intervals admit a state with no $10$ on an edge of $M$ that is non-constant
on two blocks of size $\ge2$; verified exhaustively at $n=3,5,7,9,11$ over $10\,395\times1\,023$ cases with
no counterexample). Lemma H makes it unnecessary. It is kept only because it is the statement the block
lemma actually needs if one insists on using the block lemma.

---

## 4. The computations, and what they establish

| instance | size | outcome |
|---|---|---|
| $(9,6)$, all inputs | 27 810 vars, 1 007 388 clauses | **UNSAT**, 195 s — independent confirmation of $D(9)\ge7$ |
| (R) for $M_0=\{(1,2),(3,4),(5,6),(7,8),(9,10)\}$ | 32 472 vars, 1 466 562 clauses | **UNSAT**, 720 s |
| $(11,7)$, all inputs | 158 004 vars, 7 285 333 clauses | **no answer** |

The $(11,7)$ instance ran 25 minutes under CaDiCaL here and was stopped; independently, swarm member m8
built its own encoding (182 436 variables, 5 098 830 clauses) and ran four solvers (CaDiCaL 1.5.3,
CaDiCaL 1.9.5, Glucose 4.2, Kissat 4.0.4); every one read the instance and none returned. So the monolithic
$(11,7)$ instance is out of reach of straightforward CDCL here — which is why [1507.01428] and [1310.6271]
do not solve it either: they split the search into 609 (resp. thousands of) prefix-restricted instances with
the first one or two layers *fixed*.

The honest position: $\lnot$(R) is established for $M\subseteq M_0$; for all $M$ it rests on the
literature's computation, which was not reproduced here.

---

## 5. What has been ruled out from this direction

Two whole families of arguments were eliminated by this strategy and its swarm members. Both are proved
statements, and both are recorded because they tell the next attempt where not to look.

* **Routing / cut counting / free-choice flow** (m7). Cut counting gives $d\ge1$ at $n=11$, the cone bound
  gives $4$, per-weight routability is satisfiable for all $2048$ inputs, and capacity gives $7$. So no
  cut/count/cone/free-choice relaxation can prove $D(11)\ge8$.
* **Order-theoretic / potential** (m5). The conditions "monotone, weight-preserving, fixes every sorted
  state, image inside the last layer's preimage $A'(M_d)$" are satisfied by the sorted map
  $x\mapsto\sigma_{|x|}$ itself. So that relaxation is vacuous for **every** $n$ and $d$, not merely at the
  frontier. In particular no potential-function argument on $0$-$1$ states can work unless it uses strictly
  more than monotonicity and weight.

Also ruled out, in the size strategy: image size and lattice closure (`d11-image-size-route.md` §3).

---

## 6. Provenance, checked against primary sources

* $D(11)=8$: computed by SAT in [1310.6271] (Bundala–Závodný, which settles $n=11..16$) and again in
  [1412.5302]; **no published hand proof**.
* $D(17)=10$: [1507.01428], not [1310.6271], which leaves $n=17$ open.
* $S(9)=25$: computed (arXiv:1405.5754); $S(10)=29$ follows by van Voorhis.
* Van Voorhis's recursion with $S(5)=9$ gives $S(11)\ge30$, **not** $31$; $31$ needs $S(7)=16$ and $33$ —
  the literature figure — needs $S(10)=29$. An early draft of this project quoted $31$ and it was wrong.
