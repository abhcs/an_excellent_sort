# Hand proofs of $D(5)\ge5$, $D(7)\ge6$ and $D(9)\ge7$

**Continuation:** [extension.md](extension.md) generalizes the two-layer
restriction to any number of sentinels, proves why its first-two-layer cap
consequences cannot distinguish $D(18)$ from $D(17)$, and records a validated
simultaneous-restriction SAT experiment. It does **not** settle $D(18)$.

The [rank-cut continuation](rank-cut-reductions.md) gives an exact reduction
of the input weights needed for a fixed ending, and reduces two proposed
auxiliary routes for $D(13)$ and $D(17)$ to 13 and 37 ending cases. These
auxiliary cases remain open. The [H9 update](h9.md#41-the-43-remaining-leaves-have-six-run-hand-certificates)
replaces all 43 former ending searches by six-run hand certificates.
The [six-cycle proof](h9-cycle-case.md) adds a joint sentinel invariant
and a nine-row hand proof. Three [commuting-restriction cases](h9_feedback_commute.md)
and two [rescheduled-prefix cases](h9_feedback_reschedule.md) raise H9's
hand coverage to 23 classes. The [six-real reduction](h9_feedback_next_case.md)
and [fork-and-pairs proof](h9_feedback_next_078.md) raise it to 25 classes.
The [K2,2-and-fork case](h9_feedback_round2_031246.md) raises coverage to
26 classes, using a standalone hand proof that
[three sorted blocks of lengths 4,3,2 need at least five merger layers](h9_feedback_round2_merge432.md).
The [deletion-triangle and rank-endpoint proof](h9_feedback_round4_021637.md)
raises coverage to 27 classes. Its final finite tables use fourteen
explicit real inputs, with no SAT premise. The
[five-real demands and rank-pivot proof](h9_feedback_round5_021456.md)
raises coverage to **28 of 50 classes**. Nine hand matching arguments
reduce it to 47 prefixes, excluded by fifteen explicit real inputs.
The companion [three-triple theorem](h9_feedback_round3_merge333.md)
and [four-four-one theorem](../d18-search/d13_feedback_round3_merger441.md)
prove the same merger lower bound for (3,3,3) and (4,4,1). Together they imply
a [nine-real interaction-component obstruction](../d18-search/merge-component-obstruction.md)
four layers before the end, at arbitrary ambient width: some component
must contain at least five real tracks.
The stronger [three-component theorem](../d18-search/three-component-obstruction.md)
now proves entirely by hand that there are at most two components in
every such restriction. It excludes two additional saved D18 six-layer
prefixes; it does not yet close any complete two-layer D18 case.
The [early-profile proof](h7-early-profiles.md) proves the seven-wire
two-thin-layer lemma by hand and the corresponding first-two-layer
profiles on eight wires. Its direct two-layer application to the D(13)
cover leaves all 117 cases open.
The subsequent [rank-position tests](../d18-search/certificate-guided-frontier.md),
[wire-only reductions](../d18-search/d13_feedback_round2.md),
and [saturated-cone parity](../d18-search/rank-parity-feedback.md)
exclude nine of the 117 D(13) prefix cases with independently checked
structural SAT certificates. Case115 needs only six central wire bounds;
parity closes cases1 and114 in bounded runs that previously timed out,
and the [round-six batch](../d18-search/d13_feedback_round6.md) adds cases2,57,113.
The full D(13), D(17) and D(18) goals remain unfinished.
The [D(17) defect screen](../d18-search/d17_feedback_results.md) now excludes
three of its 609 prefix cases. A [twelve-wire signed pattern](../d18-search/fixed-sentinel-obstruction.md)
now has a complete hand proof of its two-layer obstruction, including
the final [five-gate case](../d18-search/d17_hand_defects_twelve_five.md),
and lifts by hand to arbitrary larger widths with fixed auxiliary
sentinels. A three-second finite enumeration with [four short hand
inequalities](../d18-search/d12_triangle_lemmas.md) independently corroborates it. An
[exact four-triple criterion](../d18-search/d12_triangle_lemmas_complete.md)
provides a reusable structural test independent of that enumeration.
The [signed-fork width theorem](../d18-search/d12_triangle_lemmas_width.md)
extends the obstruction to every number of reals R>=7, with arbitrary
common real and fixed-sentinel auxiliaries. For D(18), its seven/eight-real
versions give a hand obstruction after four blinded layers; forcing such
a family remains open.
The [case606 normalization and incident-row lemmas](../d18-search/d17_feedback_round2_normalization.md)
add reductions valid at arbitrary even width, including the exceptional
B-edge branch. The [complete signed case606 family](../d18-search/d17_feedback_round7_reduction.md)
now has a width-independent finite-assisted proof: hand normalization
reduces the final noncritical branch to 86,370 configurations checked
in seconds without SAT. The finite classifications remain explicit
premises; a fully symbolic case606 proof is still unfinished.
The [common-real padding transfer](../d18-search/d17_feedback_round2_normalization.md#6-padding-gives-seveneight-real-obstructions-without-h9)
also gives seven/eight-real versions of both fourteen-wire obstructions.
These add conditional D18 targets using hand H7/H8. The case606 target
now has the finite arithmetic proof above; the separate case608 target
still uses its checked SAT certificate.
For D18, [compression and four restriction prices](../d18-search/commuting-prefix-hand-proof.md)
now exclude a specified five-layer prefix by hand, and
[two further certificates](../d18-search/commuting-prefix-additional-proofs.md)
exclude specified six-layer prefixes. These do not close complete
two-layer cover cases. The newer [partial-sixth-layer theorem](../d18-search/d18_rank_partner_round7_partial.md)
excludes entire families of L6 matchings after three specified five-layer
prefixes using rank witnesses alone. The [last-pairing projection](../d18-search/d13_feedback_round7_pairing.md)
and [block-capacity criterion](../d18-search/fixed-ending-block-capacity.md)
give further reusable rank-structure results at arbitrary width.
For D13, the [reduced wire-only certificate](../d18-search/d13_hand_next_wire_core.md)
sharpens the whole-case-116 structural target to ten wire intervals.

**Result.** Every optimal-depth lower bound for $n\le10$ follows by hand from $D(3)\ge3$:

$$D(5)\ge5,\qquad D(7)\ge6,\qquad D(9)\ge7,$$

and $D(4)\ge3$, $D(6)\ge5$, $D(8)\ge6$, $D(10)\ge7$ with them. The proofs use no size values ($S(n)$),
no computer search, and no normal form beyond "the first layer may be taken maximal". Until now the
hand arguments for $D(7)\ge6$ and $D(9)\ge7$ went through the computer-found sizes $S(7)=16$ and
$S(9)=25$ (see `../sorting-networks-depth/results/depth-lower-bounds-small-n.md` §4), and Parberry's
1991 proof of $D(9)=7$ was a computer search. The finite lemmas below are also checked exhaustively
by computer, and the constructions are tested on actual sorting networks (§9).

**The idea in one sentence.** Put $+\infty$ or $-\infty$ on one input of every first-layer comparator,
choosing which end of each comparator holds it (the sign then follows from the comparator's
orientation) so that every second-layer comparator also meets an infinity. Then the other
$\lceil n/2\rceil$ inputs are never compared with each other in the first two layers, and the rest of
the network has to sort them on its own. This gives

$$D(n)\ \ge\ D(\lceil n/2\rceil)+2\qquad(n\ge3),$$

so $D(9)\ge D(5)+2\ge D(3)+4=7$; the proof for nine channels never touches seven. $D(7)\ge6$ needs
one more idea (§4).

Channels are numbered $0,\dots,n-1$ (as in the code). A comparator $(a,b)$, $a<b$, sends the minimum to
$a$. A *layer* is a set of comparators on disjoint channels. $D(n)$ is the least depth of a sorting
network on $n$ channels.

---

## 1. Four elementary tools

**Tool A (zero-one principle, with infinities).** A network that sorts all $2^n$ binary inputs sorts
every input from any totally ordered set, ties allowed. *Proof:* if some output has $y_i>y_{i+1}$,
apply the monotone map $v\mapsto[v\ge y_i]$ to the input. Comparators commute with monotone maps, so
on the resulting binary input the output is the image of $y$, which has a 1 above a 0 and is not
sorted. $\square$ In particular a sorting network sorts inputs containing some $+\infty$'s and
$-\infty$'s.

**Tool B (filling the first layer).** If $N$ sorts, so does the network obtained by adding comparators
between channels that are idle in its first layer. Such comparators act on the raw input, so the new
network is $N$ applied after them, and $N$ sorts whatever it receives. Hence the first layer may be
taken to be a maximal matching. *This is the only normal form used.* Adding comparators to a later
layer is not safe in general; see §8.

**Tool C (infinities prune a network).** Let $N$ sort $n$ channels in $d$ layers. Put $+\infty$ or
$-\infty$ on some inputs and arbitrary distinct reals on the other $r$ inputs.

1. Every comparator that meets an infinity has a predetermined outcome: $-\infty$ goes to the min side
   and $+\infty$ to the max side, and two equal infinities are interchangeable. So the channels holding
   infinities after each layer do not depend on the reals.
2. The reals are sorted by a standard network on $r$ channels whose layer $t$ has one comparator for
   each comparator of $N$'s layer $t$ that meets two reals. **In particular, if the comparators of $N$
   that join two reals lie in at most $d'$ layers, then $D(r)\le d'$.**

*Proof of 2.* By 1, before and after each layer the reals occupy a fixed set of $r$ channels. Number
the channels holding reals before layer $t$ as $0,\dots,r-1$ in increasing order. In layer $t$, a
comparator between two reals is a standard comparator in this numbering, and a comparator between a
real and an infinity moves that real to a predetermined channel. So the reals pass through layers of
comparators interleaved with fixed renumberings. Pushing the renumberings to the end conjugates the
later layers. Each stays a matching of the same size, so the result is a generalized network
(comparators may point either way) followed by a fixed permutation. Untangling (Knuth, TAOCP vol. 3,
§5.3.4, exercise 16) makes it a standard network. Each untangling step reverses one comparator and
swaps two channel labels in the later comparators only. The other comparators of the same layer avoid
those two channels, so every layer keeps its size, and the result is again followed by a fixed
permutation. By Tool A the reals leave $N$ sorted, so this standard network followed by the fixed
permutation sorts every input of distinct values. A standard network leaves sorted inputs unchanged,
so the permutation fixes an increasing sequence of distinct values and is the identity. The standard
network therefore sorts all inputs of distinct values, hence all binary inputs (each is a monotone
image of one) and, by Tool A, everything. $\square$

**Tool D (cone bound).** After $t$ layers the value on a channel depends on at most $2^t$ inputs.

---

## 2. Two layers hide half of the inputs

**Lemma 1.** Let $L_1$ be a maximal matching and $L_2$ any matching on $\{0,\dots,n-1\}$. Some set $X$
of channels contains exactly one endpoint of every comparator of $L_1$, at least one endpoint of every
comparator of $L_2$, and only channels used by $L_1$.

*Proof.* The multigraph $G=L_1\cup L_2$ has maximum degree 2, so its components are paths and cycles.
Along each component the edges alternate between $L_1$ and $L_2$, so every cycle is even and $G$ is
bipartite. Choose one colour class of a proper 2-colouring in each component and let $X$ be their
union. Then every edge of $G$, in particular every comparator of $L_1$ and of $L_2$, has exactly one
endpoint in $X$. Because $L_1$ is maximal, at most one channel $u$ is unused by $L_1$ (when $n$ is odd);
in $u$'s component take the class that does not contain $u$. $\square$

**Theorem 2.** For every $n\ge3$, $\;D(n)\ge D(\lceil n/2\rceil)+2$.

*Proof.* Let $N$ sort $n$ channels in $d=D(n)$ layers. Since $n\ge3$, Tool D gives $2^d\ge n>2$, so
$d\ge2$ and $N$ has a second layer (possibly empty). This is where $n\ge3$ is needed: the statement is
false for $n=2$. By Tool B the first layer $L_1$ of $N$ is maximal; let $L_2$ be its second layer and
take $X$ from Lemma 1. Exactly one endpoint of each $(a,b)\in L_1$ lies
in $X$. Put $+\infty$ on input $b$ if $b\in X$, and $-\infty$ on input $a$ if $a\in X$. Each infinity
stays put in layer 1 ($+\infty$ is the maximum of its comparator, $-\infty$ the minimum), so after
layer 1 the infinities occupy exactly $X$. The remaining $n-\lfloor n/2\rfloor=\lceil n/2\rceil$ inputs
are reals.

* In layer 1 every comparator of $L_1$ contains exactly one infinity.
* In layer 2 every comparator of $L_2$ has an endpoint in $X$, which holds an infinity.

So two reals meet only in layers $3,\dots,d$, and Tool C gives $D(\lceil n/2\rceil)\le d-2$. $\square$

*Example.* On 9 channels, take the first two layers of Batcher's 8-sorter with channel 8 idle:
$L_1=(0,1)(2,3)(4,5)(6,7)$ and $L_2=(0,2)(1,3)(4,6)(5,7)$. $G$ is two 4-cycles, $0\!-\!1\!-\!3\!-\!2$ and $4\!-\!5\!-\!7\!-\!6$, plus
the isolated channel 8. Take $X=\{0,3,4,7\}$: $-\infty$ on 0 and 4, $+\infty$ on 3 and 7. The reals on
1, 2, 5, 6, 8 meet only infinities in layers 1 and 2.

**Corollary.** $D(3)\ge3$, and hence $D(4)\ge3$, $D(5)\ge5$, $D(6)\ge5$, $D(9)\ge7$, $D(10)\ge7$.

*Proof.* A network applies to each input a permutation determined by which of its comparators swap, so
$c$ comparators produce at most $2^c$ permutations. Sorting the $3!$ orderings of three distinct values
needs 6, while a 2-layer network on 3 channels has at most 2 comparators. So $D(3)\ge3$. Theorem 2
then gives $D(4)\ge D(2)+2=3$, $D(5)\ge D(3)+2=5$, $D(6)\ge D(3)+2=5$, $D(9)\ge D(5)+2=7$ and
$D(10)\ge D(5)+2=7$. $\square$

The depth-optimal 9-sorter on Dobbelaere's list shows the bound is tight. Its graph $L_1\cup L_2$ is a
single path ending at the idle channel 6, so the placement of Lemma 1 is forced: $X=\{3,4,5,7\}$. Its
five reals then meet in exactly layers 3 to 7, five layers, as $D(5)=5$ requires.

---

## 3. Why seven is different

Theorem 2 gives only $D(7)\ge D(4)+2=5$. Blinding more inputs for longer does not close the gap.
With $L_1=(0,1)(2,3)(4,5)$, four infinities keep three reals apart through three layers for all but
24 of the 24 360 prefixes with a maximal third layer (`verify/blinding.c`). If the third layer may be
any matching, 30 of 53 824 fail. In every exception the second layer joins two
first-layer pairs into a block of four and compares the free channel with one side of the third pair;
Batcher's merge is among them. The proof below gets around them with two infinities and a 5-channel
lemma.

## 4. $D(7)\ge6$

**Lemma 3.** No network of at most 5 layers (some possibly empty) on 5 channels whose first two layers
contain at most one comparator each is a sorting network.

*Proof.* Suppose $N$ is one, with layers $L_1,\dots,L_5$.

*(a)* Suppose $L_1$ or $L_2$ is empty, or $L_1=\{c_1\}$, $L_2=\{c_2\}$ with $c_1,c_2$ disjoint or equal. Then
$N$ does the same as a depth-4 network: disjoint comparators commute, and a comparator repeated
immediately never fires. This contradicts $D(5)\ge5$.

*(b)* Otherwise $c_1=\{p,q\}$ and $c_2=\{q,s\}$ share exactly the channel $q$, and the other two
channels $y,z$ are idle in layers 1 and 2. Let $A$ be $+\infty$ if $q>p$ and $-\infty$ if $q<p$, placed
on $q$, so that it stays on $q$ in layer 1. In layer 2 it moves to $q'=\max(q,s)$ or $\min(q,s)$
respectively; let $s'$ be the other channel of $c_2$. Each of the following placements of two
infinities keeps the reals apart in layers 1–2, leaving three reals on the channels shown:

| placement | reals after layer 2 |
|---|---|
| $A$ on $q$, another infinity on $y$ | $\{p,s',z\}$ |
| $A$ on $q$, another infinity on $z$ | $\{p,s',y\}$ |
| $A$ on $q$, another infinity on $s$ | $\{p,y,z\}$ |
| $+\infty$ on both $p,q$ | $\{\min(q,s),y,z\}$ |
| $-\infty$ on both $p,q$ | $\{\max(q,s),y,z\}$ |

The last two rows give $\{q,y,z\}$ and $\{s,y,z\}$ in some order. If $L_3$ has no comparator inside one
of these five triples, those three reals meet only in layers 4 and 5, and Tool C gives $D(3)\le2$,
which is false. So $L_3$ has a comparator inside each triple.

* The triples $\{p,y,z\},\{q,y,z\},\{s,y,z\}$ need three comparators through $y$ or $z$ unless
  $(y,z)\in L_3$, and a matching has at most two of those. So $(y,z)\in L_3$.
* $\{p,s',z\}$ and $\{p,s',y\}$ then need a further comparator of $L_3$ inside both and disjoint from
  $\{y,z\}$, that is, $\{p,s'\}\in L_3$.

Now $c_1$, $c_2$, $\{p,s'\}$ sort the triple $\{p,q,s\}$. If $q>p$, then after $c_1$ and $c_2$ the
channel $q'=\max(q,s)$ holds the largest of the three values and is the largest of the three channels,
and $\{p,s'\}$ sorts the other two; the case $q<p$ is symmetric with minima. Also $(y,z)$ sorts the
pair. So after layer 3 every input has become a sorted triple on $p,q,s$ beside a sorted pair on $y,z$,
and every such state occurs: fed in directly, it passes through layers 1–3 unchanged. Layers 4 and 5
must therefore merge a sorted triple with a sorted pair. The middle output is the median of the five
values, and that median depends on all five positions. With triple $(a_0,a_1,a_2)$ and pair
$(b_0,b_1)$, each of $(x,8,9|0,1)$, $(0,x,9|1,8)$, $(0,1,x|8,9)$, $(0,1,9|x,8)$, $(0,8,9|1,x)$ has
median $x$ for $1<x<8$. But after two layers a channel depends on at most four of the five positions
(Tool D). Contradiction. $\square$

**Lemma 4.** If some network of $d$ layers sorts 7 channels, then some network of $d$ layers (some
possibly empty) sorts 5 channels with at most one comparator in each of its first two layers.

*Proof.* By Tool B the first layer is $\{c_0,c_1,c_2\}$ plus one idle channel. Write $lo_i<hi_i$ for the
channels of $c_i$. For $i\ne j$ put $+\infty$ on $hi_i$ and $-\infty$ on $lo_j$. Both stay put in
layer 1, where exactly one comparator, $c_k$ with $k\notin\{i,j\}$, meets two reals. Choose $i\ne j$ so
that layer 2 also has at most one comparator between reals; Tool C then gives the claim.

* If $L_2$ has at most one comparator, any $i\ne j$ works.
* If $L_2$ has two comparators, they cover four channels. Only one channel (the idle one of layer 1)
  is not some $lo_b$ or $hi_a$, so pick one covered channel of that form. If it is $hi_a$, take $i=a$
  and any $j\ne a$; if it is $lo_b$, take $j=b$ and any $i\ne b$. Then one of the two comparators
  meets an infinity.
* If $L_2$ has three comparators and idle channel $v$, the ordered pair $(i,j)$ fails only if
  $v\in\{hi_i,lo_j\}$ (at most two pairs) or $\{hi_i,lo_j\}\in L_2$ (at most three pairs, one per
  comparator). Since $2+3<6$, some $(i,j)$ puts the two infinities on different comparators of $L_2$,
  leaving one comparator between reals. $\square$

**Theorem 5.** $D(7)\ge6$, hence $D(8)\ge6$.

*Proof.* A depth-5 sorting network on 7 channels would give, by Lemma 4, a depth-5 sorting network on
5 channels forbidden by Lemma 3. $D(8)\ge D(7)$ by Tool C with a single infinity. $\square$

---

## 5. What the proofs rest on

| bound | uses |
|---|---|
| $D(3)\ge3$ | $2^2<3!$ |
| $D(5)\ge5$, $D(6)\ge5$ | Theorem 2 (Tools A–C, Lemma 1) and $D(3)\ge3$ |
| $D(9)\ge7$, $D(10)\ge7$ | Theorem 2 and $D(5)\ge5$ |
| $D(7)\ge6$, $D(8)\ge6$ | Lemma 4, plus Lemma 3 (which uses $D(5)\ge5$, $D(3)\ge3$ and Tool D) |

Nothing else: no $S(n)$, no exhaustive search, no SAT, no maximal middle layers.

On $S(5)=9$: Floyd and Knuth settled $S(n)$ for $n\le8$ and needed a computer only for $n=7$ (as
summarized in Harder, arXiv:2012.04400), so $S(5)\ge9$ is classically a hand result. Together with
Lemma 4 it would also give $D(7)\ge6$, since the 5-channel network has at most $1+1+2+2+2=8$
comparators. Lemma 3 is the weaker statement actually needed, and it is proved above directly.

---

## 6. Where the method stops: $D(11)\ge8$

Theorem 2 gives $D(11)\ge D(6)+2=7$, one short. Two natural extensions both fail:

* **Three blind layers.** Six infinities on 11 channels keep five reals apart through three layers for
  most prefixes, but not for 4 072 260 of the 371 059 920 (`blinding 11 3 6`, about 1%).
* **The route of §4.** The argument of Lemma 4 works on 11 channels with the same counting: at most
  $4+5=9$ of the 20 ordered pairs fail. It reduces $D(11)\ge8$ to
  **(H9): no depth-7 sorting network on 9 channels has at most three comparators in each of its first
  two layers.** Four infinities keep five reals apart through three layers for only 72% of the
  prefixes of that shape (451 008 of 1 582 875 fail, `blinding 9 3 4 3 3`). So a proof of (H9) would
  need a replacement for the merge step of Lemma 3(b) covering far more cases.

  **Update: (H9) is true** ([`h9.md`](h9.md)). It is settled by computer twice: a SAT instance refuted
  by four solvers, and a case tree without SAT. The case tree's leaves are
  certificates built from $D(5)\ge5$, Lemma 3 and the cone bound; the final
  43 exceptions now have six-run hand certificates from the rank-profile
  lemma (`h9.md` §4.1), with no search over the final two layers. A pair-index
  bug in the tree was corrected and the enumeration rerun; the current
  counts and validation are recorded in `h9.md` §4. Hence $D(11)\ge8$ and
  $D(12)\ge8$, computer-assisted. (H9) is proved by hand for 25
  of its 50 cases, one per class of second layers (`h9.md` §7). Nine use three lemmas about
  infinities, and the [six-cycle case](h9-cycle-case.md) uses a joint sentinel invariant and a
  nine-row table. Three more follow by [commuting retained gates](h9_feedback_commute.md),
  applying the seven/eight-wire early profiles, and a deletion-graph argument.
  Two further cases use [three-layer rescheduling](h9_feedback_reschedule.md)
  and incompatible six-real pairings.
  Two more use a [six-real first-layer bound](h9_feedback_next_case.md) and
  [price, parity and sink-contact arguments](h9_feedback_next_078.md).
  Eight follow from a 7-channel statement, (P7): no sorter on 7 channels with at most 6
  layers has at most one comparator in its first layer. (P7) is tight, and `h9.md` §7.5 proves it by
  hand: infinities fix the first three layers up to six cases, and pairs of inputs that differ in one
  bit, followed through two more layers, rule out every fourth layer. The last step uses six tables of
  71 rows in all, each row one layer applied to a 7-bit string. `h9.md` §§5–6 records where blinding
  fails on the rest and why the merge step does not extend.

The pattern behind §4: for odd $n$, $D(n+2)\ge D(n)+1$ follows from "no depth-$D(n)$ sorter on $n$
channels has two thin first layers" (thin = one comparator short of maximal). It holds at $n=5$
(Lemma 3), and at $n=7$ by the [early-profile hand proof](h7-early-profiles.md).
At $n=9$ the proof remains computer-assisted ([`h9.md`](h9.md), (H9)). It already fails at
$n=11$: an 8-layer sorter on 11 channels with four comparators in each of its first two layers exists
(`h9.md` §9). So this route stops at $D(11)\ge8$. `h9.md` §9 also finds that the route through (P7),
three layers of blinding with one leak allowed, fails on 12% of the 13-channel prefixes. By hand these
methods give only $D(13)\ge8$.

---

## 7. Beyond $n=10$: what the recursion gives

Theorem 2 holds for every $n\ge3$. Fed with the computer-proved values $D(13..16)=9$ (Bundala–Závodný,
2014) and $D(17)=10$ (Codish, Cruz-Filipe, Ehlers, Müller, Schneider-Kamp, 2016), it gives:

| $n$ | from | Theorem 2 gives | lower bound on Dobbelaere's list (Nov 2026) |
|---|---|---|---|
| 25–32 | $D(13..16)=9$ | **11** | 10 |
| 33–38 | $D(17..19)\ge10$ | **12** | 10 |
| 39–48 | $D(20..24)\ge10$ | **12** | 11 |
| 49–64 | $D(25..32)\ge11$ (row 1) | **13** | 11 (49–54), 12 (55–64) |

Rows 2 and 3 also use monotonicity, $D(m)\ge D(17)=10$ for $m\ge17$. For $n\le24$ the recursion gives
nothing new: monotonicity from $D(17)=10$ is already at least as strong (Theorem 2 alone gives only 9
for $n=18..20$).

**Caution on novelty.** Iterating Theorem 2 gives $D(n)\ge2\log_2n-O(1)$, which is the folklore
"$(2-o(1))\log_2n$" depth bound mentioned in recent papers (arXiv:2208.08394, arXiv:2310.12270).
Yao (1980) raised the asymptotic constant to about 2.41 and Kahale et al. (1995) to about 3.27, but
those bounds are asymptotic and say nothing at these sizes. I did not find the exact recursion
$D(n)\ge D(\lceil n/2\rceil)+2$ in the sources I checked, and Dobbelaere's table does not use it. The
2022 paper's general-depth argument is different and loses constants (for $n=9$ it gives only 5). So
either this exact form is new, or it is folklore that never reached the tables. My search was not
exhaustive. Either way, the improved values in the table above should be checked against the
literature, and by someone else, before they are announced. The proof in §2 is short enough to check
line by line.

---

## 8. A correction to the bundle: "adding comparators preserves sorting" is false

`../sorting-networks-depth/results/depth-lower-bounds-small-n.md` T3 states: *if $N$ sorts and $N'$ is
obtained from $N$ by adding comparators to its layers, then $N'$ sorts.* This is false.

* $(1,2)\mid\varnothing\mid(0,2)\mid(0,1)$ sorts 3 inputs. Put $(0,1)$ into the empty second layer and
  input $100$ comes out $010$.
* A depth-optimal example: $(0,2)(1,3)\mid(1,4)\mid(0,1)(3,4)\mid(1,4)(2,3)\mid(1,2)(3,4)$ sorts
  5 inputs. Add $(2,3)$ to its second layer and input $10100$ comes out $00101$.
* It is not rare. `verify/t3_counterexample.py` inserts one random comparator into a middle layer of
  relabelled Batcher networks ($n=3..10$, fixed seed): 188 of 1 121 insertions break the network.

The proof's monotonicity step fails: with prefix sums, $010\preceq100$ ($0,1,1\le1,1,1$), but after
the comparator $(0,2)$ these become $010$ and $001$, with prefix sums $0,1,1\not\le0,0,1$.

Adding comparators *is* safe in the first layer (Tool B) and in or after the last layer, because the
output is already sorted. The bundle uses T3 in middle layers in several places, so the following are
not lower-bound proofs as written:

* the maximal-layer normal form (T3's consequence);
* the proof of Lemma S in `d11-image-size-route.md` §1, which adds comparators to layers $1..d-1$;
* every search restricted to maximal layers: `depth_search.py` ("WLOG by the add-comparators lemma"),
  `exact3.c`/`exact4.c`, `residual_n7.py`, the block-route checks in §4.4–4.5 of that document, and
  `sat_encode.py`,
  which allows at most one idle channel per layer. That includes the SAT "independent confirmation"
  of $D(9)\ge7$.

The values themselves are not in doubt: they are established in the literature, and for $n\le10$ now
by §§2–4. Whether every depth is attained by a network with all layers maximal is a separate question,
and T3's proof does not settle it.

---

## 9. Verification

`verify/verify.sh` re-runs everything in about 35 seconds (needs `cc` and `python3`). If
`verify/.venv` has python-sat installed, it also runs the SAT-based checks of [`h9.md`](h9.md), about 45
seconds more.

| script | checks |
|---|---|
| `small_facts.c` | brute force over **all** networks with given per-layer caps (no maximality): $D(3)\ge3$; $D(5)\ge5$; Lemma 3 (caps 1,1,2,2,2: no sorter); and for contrast caps 1,2,2,2,2 (360 sorters) |
| `blinding.c` | Lemma 1 for every second layer, $n=3..11$; the three-layer data of §§3 and 6 |
| `lemma3_case_b.py` | Lemma 3(b): over all 1 560 cases, blinding fails exactly when $L_3=\{\{y,z\},\{p,s'\}\}$ (60 cases), layers 1–3 then sort the triple, and the median of a 3+2 merge depends on all five positions |
| `lemma4_two_sentinels.py` | Lemma 4's choice of $(i,j)$ exists for all 232 second layers on 7 channels |
| `mechanism.py` | Theorem 2 and Lemma 4 run on 300 relabelled Batcher networks ($n=3..12$), 201 networks on 7 channels and Dobbelaere's depth-optimal networks for $n=5..9$. Brute force over the reals confirms each network still sorts with the infinities in place, the reals never meet where the proofs say they don't, and they meet in at most $d-2$ layers |
| `t3_counterexample.py` | both counterexamples of §8, the failed monotonicity, and the random-insertion count |
| `h9_tree.c`, `h9_blind.c`, `h9_hand.c`, `h9_p7.c`, `h9_*.py`, `h7_profiles_proof.py`, `satnet.py` | (H9), the early-profile lemmas and the data of §6: see [`h9.md`](h9.md) §10; only the SAT scripts need python-sat |
| `leak_blinding.c`, `d13_networks.py`, `h11_sat.py` | $D(13)$: where these methods stop ([`h9.md`](h9.md) §9) |

The heavier run `./blinding 9 4 6` (about 2 minutes) shows that six infinities keep three reals apart
through four layers on 9 channels for every prefix. That is a second, computer-checked route to
$D(9)\ge4+D(3)=7$; the hand proof does not need it.

## References

* D. E. Knuth, *The Art of Computer Programming*, vol. 3, §5.3.4 (zero-one principle; untangling,
  exercise 16).
* I. Parberry, "A computer-assisted optimal depth lower bound for nine-input sorting networks",
  *Math. Systems Theory* 24 (1991).
* D. Bundala, J. Závodný, "Optimal sorting networks", LATA 2014, arXiv:1310.6271.
* M. Codish, L. Cruz-Filipe, T. Ehlers, M. Müller, P. Schneider-Kamp, "Sorting networks: to the end
  and back again", *JCSS* (2016), arXiv:1507.01428.
* J. Harder, "An answer to the Bose–Nelson sorting problem for 11 and 12 channels", arXiv:2012.04400.
* N. Dobokhotova-Maikova, A. Kozachinskiy, V. Podolskii, "Constant-depth sorting networks",
  arXiv:2208.08394.
* "Towards simpler sorting networks and monotone circuits for majority", arXiv:2310.12270.
* B. Dobbelaere, *Smallest and fastest sorting networks*,
  https://bertdobbelaere.github.io/sorting_networks_extended.html (consulted 2026-11-14).
