# Toward a hand proof for the efficient prefixes

The goal is a hand proof of $D(17)\ge10$. The descent of README §4 does most of it by hand: it
reduces the theorem to sparse-start statements, with one obstruction left at every level, the
**exceptional configurations** of §4.1. These are the efficient, merge-like prefixes. The same
obstruction appears at the $D(11)$ level, at (9, 3), (8, 2) and (7, 1), and at the $D(17)$ level,
at (14, 5), (13, 4) and (12, 3). At the $D(17)$ level they have been settled only by SAT (README
§5, §8.14–§8.15). At the $D(11)$ level probe tokens now settle all of them without SAT (§4).

This note records what is known about them, what provably cannot settle them, and the
measurements that point to an argument that might. Proved statements are marked as such;
everything else is a measurement or a conjecture.

Scripts are in `hand/`, data in `hand/*.json`, and logs in `logs/hand_*`.

## 1. The structure of exceptional configurations (proved)

Fix $(n,a)$ with $k=n-2a$ idle channels in a full layer. $L_1$ has exactly $a$ comparators
$(lo_j,hi_j)$, and $|L_2|,|L_3|\le a$. A $+\infty$ track starts on $hi_j$ and a $-\infty$ track
on $lo_j$. A track is good if it meets a comparator in every full layer among $L_2,L_3$. The
configuration is exceptional if none of the $2a$ tracks is good.

**Normal form.** We may assume no comparator of $L_2$ or $L_3$ is redundant (never swaps on the
states it sees). Deleting one keeps the network sorting and only lowers layer sizes. After the
deletion either some track is good, and the descent goes on, or the configuration is still
exceptional. A first-layer comparator always fires, so $L_1$ is unaffected, and Fact A refills
$L_1$ if needed. This normalization cuts the exceptional prefixes:
* at (9, 3), depth 7: from 1,200 to 1,010;
* at (8, 2): from 764 to 663 (`hand/exc_small.py`).

The S14 census of §8.14 was already in normal form.

**Theorem 1 (structure).** Suppose $k<2a$ and $2\lceil a/2\rceil>k$. This holds at (9, 3) and
(14, 5), but not at (13, 4) or (12, 3). Then an exceptional configuration has:
1. $|L_2|=|L_3|=a$;
2. every track that meets $L_2$ ends layer 2 on a channel idle in $L_3$.

So the landing set $\Lambda$ of those tracks lies in the $k$ idle channels of $L_3$.

*Proof.*
* **$L_3$ not full.** Then a track is good as soon as it meets $L_2$ (or always, if $L_2$ is not
  full either). If $L_2$ is full, at most $k<2a$ of the $2a$ start channels are idle in it, so some
  track meets it.
* **$L_2$ not full, $L_3$ full.** After $L_2$ the $+$ tracks sit on max ends of $L_2$ or on
  $L_2$-idle $hi_j$, and the $-$ tracks on min ends or $L_2$-idle $lo_j$. The two kinds of channel
  are disjoint, and each holds at least $\lceil a/2\rceil$ of them, since one comparator merges at
  most two tracks. That is $2\lceil a/2\rceil>k$ channels, so one of them is used in $L_3$ and its
  track is good.
* **Both full.** A track that meets $L_2$ is good exactly when its landing channel is used in
  $L_3$. $\square$

**Corollary (at (14, 5)).** Let $v$ be the number of first-layer channels idle in $L_2$. The
$10-v$ tracks that meet $L_2$ land on at most 4 channels, and each channel receives at most 2. So
$v\ge2$, and $L_2$ contains at least two *merges*: comparators joining two $hi$ channels or two
$lo$ channels.
* **$v=2$:** exactly four merges, two $hi$–$hi$ and two $lo$–$lo$.
* **Diamond type:** when the merges join the same two pairs twice, the post-$L_2$ poset is always
  two diamonds, two 2-chains and two singletons, as in S14's case 0. $L_3$ is then a perfect
  matching of the ten channels outside the four diamond extremes, with no redundant comparator.
  S14's case 0 has 36 such third layers up to symmetry (`hand/case0_exceptional.json`).

## 2. What cannot settle them

**Sentinel reductions, measured.**
* **(14, 5).** For a hard child, every residual of 4 or 5 sentinels has a completion, and those of
  1–3 sentinels are undecided by short SAT runs (§8.14).
* **(9, 3).** After normalization, 1,003 of the 1,010 exceptional prefixes have no hand
  certificate. Over every set of up to four infinities and three schedules (as soon as possible,
  as late as possible, as is), only three small tight-depth statements would close any of them
  (`hand/lemma_hunt.py`):

  | statement | prefixes it would close | true? |
  |---|---|---|
  | SS(5, 5, 1, 1) | 1,003 | false: 360 depth-5 5-sorters start with one comparator |
  | SS(7, 6, 2, 1) | 995 | false |
  | SS(8, 6, 3, 1) | 256 | not yet tested |

**One-layer sparse starts are not forbidden at optimal depth.** SAT finds sorters violating each
of these (`sat14/first_layer.py`, `logs/sat14_first_layer.log`):
* SS(9, 7, 3, 1): a depth-7 9-sorter with 3 comparators in layer 1;
* SS(10, 7, 4, 1);
* SS(11, 8, 4, 1);
* SS(11, 8, 3, 1): even 3 comparators in layer 1 of a depth-8 11-sorter;
* SS(6, 5, 2, 1).

**Splitting construction (proved).** A depth-$d$ sorter with layer sizes $(t_1,t_2,\dots)$ gives a
depth-$(d+1)$ sorter whose first three layers are $(t_1, x, t_2-x)$: split the second layer.
* It refutes SS(11, 9, 2, 2) and SS(11, 9, 3, 3), from the depth-8 11-sorter with layers
  $(3,5,\dots)$.
* So any alternative reduction of the exceptional configurations to sparse statements at depth
  $D(r)+1$ must survive this construction.
* T3(11, 2) survives it, and it is true (proved in §8.15).

**Static (linear-extension) arguments.** The merge rule of §5.1 sorts only the inputs the prefix
leaves alone. After an efficient prefix the comparator poset has small width: 5 for S14's case 0
with $L_3=(3,4)(7,8)(0,10)(1,11)(12,13)$. Cone bounds there give at most 4 layers, against 6 free
ones. The obstruction must use inputs the prefix does change.

## 3. Probe tokens: a dynamic invariant (measured)

Probes (h9.md, Lemma 13) work at full size. A probe for output $k$ is a pair of reachable states
one bit apart. The differing bit is a token, which must end on channel $k$. Let $T_t(k)$ be the
channels holding some probe's token after layer $t$.

**Two facts (proved in h9.md §7.5).**
* **Cone bound:** with the end-game normal form, $|T_{d-2}(k)|\le4$.
* **Merge bound:** a comparator of layer $t+1$ joins two channels. If it is two-sided for $k$ (some
  token on it sees 0 on the other channel and some sees 1), both channels stay in $T_{t+1}(k)$.
  Hence $|T_{t+1}|\ge|T_t|-m_{t+1}$, where $m_{t+1}$ counts one-sided comparators with both channels
  in $T_t$. A two-sided pair on two channels that the layer leaves idle stays two-sided: the tokens
  there and the bits they see do not change.

**Measurements** (`hand/tokens.py`, `hand/token_profile.py`, `hand/phi.py`):
* **After an exceptional S14 prefix** (case 0, $L_3=(0,3)(1,4)(7,8)(10,12)(11,13)$), the median's
  tokens (outputs 6 and 7) are on all 14 channels. 98% of the 91 possible comparators are
  two-sided for them, so layer 4 can merge at most about 2 token channels for the median. Layers
  4–7 must merge 10 to reach the cone bound.
* **A real sorter does this.** SAT finds a depth-9 16-sorter with the 3-layer Green filter
  (`hand/g16_d9_network.json`, 15 s). Its median tokens start on all 16 channels and shrink
  16, 14, 10, 8, 4, 2, 1, with 2, 4, 2, 4, 2, 1 one-sided merges per layer. So layer 4 alone does
  not separate feasible prefixes from infeasible ones.
* **The total spread separates them in the sample.** Let $\Phi_p=\sum_k(|T_p(k)|-1)$. The sorter
  must bring $\Phi$ to 0, and $\Phi$ only falls through one-sided merges.

  | 3-layer prefix on 14 channels | $\Phi_3$ |
  |---|---|
  | feasible: 124 two-infinity restrictions of the depth-9 16-sorter (layers 6–7) | 126–134 |
  | S14 case 0, the 36 exceptional prefixes (layers 5, 5, 5) | 142–148 |
  | S14, 30 random cases: 180 exceptional children | 142–151 |
  | S14, the same cases: 180 other children | 144–155 |

  So in this sample every sparse prefix, exceptional or not, leaves more spread than every feasible
  one (`hand/phi_census.py`).
* **And the next layer can remove less after a sparse prefix.** For each pair of channels, count the
  outputs for which a comparator on it would be a one-sided merge. A maximum-weight matching of these
  counts bounds the drop of $\Phi$ in the next layer, whatever that layer is (`hand/capacity.py`):

  | prefix | $\Phi_3$ | most any layer 4 can remove |
  |---|---|---|
  | S14 case 0, four exceptional prefixes | 144–146 | 28–31 |
  | feasible 14-channel prefixes (layers 7, 6, 6) | 126 | 32–33 |
  | feasible 16-channel 3-layer Green filter | 164 | 54 (the sorter's own layer 4 removes 48) |

  The real sorter removes 48, 38, 32, 17, 19 and 10 in its last six layers.

**Conjecture (token spread), as first stated.** Every sparse prefix with layers (5, 5, 5) leaves
more token spread than six layers can remove.
* The cone bound alone is far too weak. It caps $\Phi$ at about 98 after layer 6, which asks only
  for a drop of about 47 in layers 4–6.
* The measured per-layer capacity is the quantity that matters. After a sparse prefix it is already
  lower at layer 4 (28–31 against 32–33) while there is more to remove (144–146 against 126).

§4 shows that the sum over *all* outputs is the wrong potential: at the $D(11)$ level it never
suffices, while a sum over the three middle outputs always does. §6 restates the conjecture for a
middle window.

## 4. Tokens settle the exceptional prefixes at the $D(11)$ level (computed, no SAT)

**Method** (`hand/tokcore.c`). A complete search over all later layers below a prefix, pruned only
by tokens:
* After each layer, the token sets $T_t(k)$ are read directly from the reachable set: every pair of
  reachable states one bit apart is a probe.
* A depth-$D$ sorter has $|T_t(k)|\le2^{D-t}$. With the end-game normal form also
  $T_{D-2}(k)\subseteq[k-4,k+4]$, $T_{D-1}(k)\subseteq[k-1,k+1]$ and $T_D(k)=\{k\}$.
* Each layer is built channel by channel, and the images of the current tokens must already meet
  these bounds. Comparators that never fire are skipped, which we may assume.
* Validation: it finds sorters of the optimal depth for 4 to 8 channels and none one layer
  shallower. For 7 and 8 channels it refutes depth 5 already at layer 3.

**Result.** Every normalized exceptional prefix of the $D(11)$ descent fails at layer $5=D-2$. For
every fourth layer and every fifth layer, some output's tokens lie on at least 5 channels.

| level (depth 7) | prefixes | refuted at layer 5 | time |
|---|---|---|---|
| E3(9, 3) | 1,010 | 1,010 | 1.6 s |
| E3(8, 2) | 663 | 663 | 0.6 s |
| E3(7, 1) | 59 | 59 | < 0.1 s |

* The positional part of the cone is not needed; the size bound $|T_5(k)|\le4$ suffices.
* Cross-checks:
  * `hand/tokfull.c` recomputes everything without pruning, over every fifth layer, redundant
    comparators included. It confirms all 59 prefixes of E3(7, 1) (2.2 million pairs of layers) and
    all 663 of E3(8, 2) (200.7 million pairs), and all 1,010 of E3(9, 3) (2.84 billion pairs;
    `logs/hand_tokfull_9_3.log`). For every prefix the least value of $\max_k|T_5(k)|$ is exactly 5.
  * `hand/tokwin.c` independently proves the window bound below for all of E3(9, 3), which implies
    the result.
  * `hand/tokcheck.py` (numpy) repeats samples of both levels (`logs/hand_tokcheck.log`).

**Consequence.** The descent of README §4 is by hand. It takes $D(11)$ to $T_3(9,3)$ through
$(11,5)\to(10,4)\to(9,3)$, and then $T_3(n,a)\ge\min(T_3(n-1,a-1),E_3(n,a))$ down to
$T_3(6,0)=3+D(6)=8$. So $D(11)\ge8$ follows from these three token computations alone: no SAT and
no sentinel prover. Each prefix takes an enumeration of about 600 fourth layers, each refuted by a
short search over fifth layers. This is a much smaller and more transparent computer proof, but not
yet a hand proof.

**Which outputs carry it.** The median alone is not enough; a few neighbouring outputs together
are. Each entry counts the prefixes refuted when the bounds are applied to those outputs only.

| outputs (E3(9, 3)) | refuted of 1,010 | outputs (E3(8, 2)) | refuted of 663 |
|---|---|---|---|
| {4} (median) | 0 | {3, 4} (medians) | 15 |
| {3, 4} or {4, 5} | 41 | {2, 5} | 0 |
| {3, 5} | 957 | {2, 3, 4} | 659 |
| {3, 4, 5} | 1,010 | {2, 3, 4, 5} | 663 |

**At (9, 3) a sum already suffices** (`hand/tokwin.c`). For every prefix and every fourth and fifth
layer, $\sum_{k=3}^{5}|T_5(k)|\ge13$, while the cone allows 12. The least value is 13 for 233
prefixes, 14 for 730 and 15 for 47.
* At (8, 2), the sum over outputs 2–5 reaches the cone allowance of 16 for 151 prefixes, so there the
  maximum is needed.
* The sum over all outputs, the $\Phi$ of §3, never suffices. At (9, 3) some fourth and fifth layer
  bring it to 31–35, under the allowance of 36.

So **the obstruction is local to the middle outputs**: neighbouring outputs compete for the same
comparators.

## 5. Tokens are rank intervals (proved)

**Lemma 2.** After layer $t$, channel $c$ holds a token of output $k$ if and only if some input
permutation puts the element of rank $k$ on channel $c$. These ranks form an interval
$[lo_t(c),hi_t(c)]$, so
$$T_t(k)=\{c:\ lo_t(c)\le k\le hi_t(c)\}.$$
If $f_c$ is the monotone Boolean function on channel $c$, then $lo=\tau(f_c)-1$ and
$hi=n-\mu(f_c)$. Here $\mu$ is the least size of a minimal set of inputs whose 1s force $f_c=1$ (a
term), and $\tau$ the least size of one whose 0s force $f_c=0$ (a clause).

*Proof.*
* If a permutation puts rank $k$ on $c$, its 0-1 images at thresholds $k$ and $k+1$ form a probe with
  its token on $c$.
* Conversely, take a probe $(s,s+e_c)$ with $|s|=n-1-k$. Its state $s+e_c$ is the image of a 0-1 input
  with $n-k$ ones and a 1 on $c$. A permutation whose top $n-k$ elements sit on those ones puts rank
  $\ge k$ on $c$. Likewise $s$ gives rank $\le k$.
* Swapping two inputs of adjacent rank changes the rank on $c$ by at most one, so the achievable
  ranks form an interval.
* The formulas for $lo$ and $hi$ restate the 0-1 principle. $\square$

The token method is therefore a statement about rank intervals: after layer $D-2$, each rank lies in
the intervals of at most 4 channels.

**Calculus.** For a comparator $(i,j)$ with the minimum to $i$:
* min end: $lo'=\min(lo_i,lo_j)$ and $hi'\ge hi_i+hi_j-n$, since the terms of $\min(f_i,f_j)$ are
  unions of a term of each;
* max end: $hi'=\max(hi_i,hi_j)$ and $lo'\le lo_i+lo_j+1$, since its clauses are unions.

The inequalities are equalities when the minimal terms (clauses) can be chosen disjoint. Taking
equality everywhere narrows every interval, so it bounds every $|T(k)|$ from below using the
comparators alone, without reachable sets.

**Measured: overlaps cannot be dropped** (`hand/tokrelax.c`).
* Starting from the exact intervals after the prefix, the overlap-free calculus refutes only 205 of
  the 1,010 (9, 3) prefixes and 100 of the 663 (8, 2) prefixes. The rest have "interval sorters".
* With exact intervals through layer 4 and the calculus only for layer 5, it refutes 31,307 of the
  31,440 pairs of a prefix and a fourth layer, over 12 sample prefixes.

So what keeps the intervals wide is overlap: minimal terms and clauses shared by the two channels
of a comparator. Overlaps accumulate over layers, and a hand argument has to track them.

## 6. Fourteen channels (measured)

* **Spread.** After the exceptional S14 prefixes of case 0, outputs 3–10 each have tokens on all 14
  channels: $|T_3(k)|=5,8,11,14,\dots,14,11,8,5$. After feasible prefixes (two-infinity
  restrictions of the depth-9 16-sorter), no output has more than 13.
* **One-layer capacity.** One more layer lowers $\sum_{k=5}^{8}|T(k)|$ by at most 4–8 after a
  sparse prefix, against 8–13 after a feasible one. This is exact for token images
  (`hand/tokpot.c`, a dynamic program over matchings).
* **Real sorters have no slack.** In the 14-channel depth-9 sorters above, every middle output has
  exactly 4 token channels after layer 7 and exactly 2 after layer 8.
* **Beam search** for continuations that pass the cone at layer 7 (`hand/tokbeam.c`):
  * It passes 6 of 12 feasible prefixes, and the others miss by 1–2 channels in total.
  * For all 36 exceptional prefixes of case 0, the best continuations miss by 7–11 channels and
    leave outputs 3–10 at 5–6 channels each.

  This is a heuristic, not a proof.
* **No sparse feasible sorter found.** Four SAT searches looked for depth-9 14-sorters with first
  three layers of sizes (5, ≤5, ≤6), (5, ≤6, ≤5), (6, ≤5, ≤5) and (5, ≤6, ≤6). All four ran out of
  their 20 minutes without an answer.

**Conjecture (middle window).** For every exceptional S14 prefix and any layers 4–7, some output
$k\in\{3,\dots,10\}$ has $|T_7(k)|\ge5$. The stronger sum form is $\sum_{k=3}^{10}|T_7(k)|>32$.
Either form implies that the prefix has no completion of depth 9.

## 7. The window lemma at the $D(11)$ level

**Every sparse prefix fails, not only the exceptional ones** (`hand/all_prefixes.py`,
`hand/tokcore.c`). The prefixes are listed as before: $L_1$ is $a$ middle pairs, $L_2$ runs over
its symmetry classes, and $L_3$ over every non-redundant layer of at most $a$ comparators. The token
search refutes all of them at layer 5:

| statement | prefixes | refuted at layer 5 | time |
|---|---|---|---|
| $T_3(9,3)\ge8$ | 87,075 | 87,075 | 109 s |
| $T_3(8,2)\ge8$ | 2,926 | 2,926 | 2.5 s |
| $T_3(7,1)\ge8$ | 81 | 81 | < 0.1 s |

So $T_3(9,3)\ge8$ follows directly. With the descent $(11,5)\to(10,4)\to(9,3)$ (by hand), this
gives $D(11)\ge8$ without the exceptional analysis of §4: tokens alone settle the last step.

**The statement to prove by hand.**

> **(W)** Let a network on 9 channels have at most 3 comparators in each of its first three layers,
> in the normal form of README §4. After any two more layers, ranks 3, 4 and 5 lie in at least 13
> channel intervals in total.

Any 9-channel depth-7 sorter has at most 4 channels per rank after layer 5, so at most 12 in
total. (W) therefore gives $T_3(9,3)\ge8$, and with it $D(11)\ge8$.
* **(W) holds for all 87,075 prefixes** (`hand/tokwin.c`, `logs/hand_tokwin_all_9_3.log`). The
  least window sum after two layers is 13 for 935 prefixes, 14 for 17,196, and 15–21 for the
  rest.
* The tight prefixes fall into 96 of the 6,652 reachable-set classes; 76 of those are minimal.
* With fewer layers or channels the sum is not always enough. At (8, 2), 151 prefixes need the
  maximum form, "some rank in at least 5 channels". (8, 2) and (7, 1) are not needed for this
  route, though.

**No small set of cases.**
* Token sets only grow with the reachable set. So a prefix whose reachable set contains a
  relabelled copy of another's (complements included) needs no argument of its own.
* The 87,075 prefixes have 6,652 distinct reachable sets. Of these, 1,471 are minimal under
  containment (`hand/subsetperm.c`).
* For the exceptional prefixes alone: 1,010 prefixes, 138 reachable sets, 103 minimal. For (8, 2):
  663, 60, 46. For (7, 1): 59, 6, 5.

A hand proof of (W) needs an argument that covers all sparse prefixes at once.

Through the descent with exceptions (§4), only the exceptional prefixes need (W), and fewer of
them are hard. Of the 103 minimal exceptional classes at (9, 3), only 29 are tight, with least
window sum 13 after two layers. Each has one to fourteen optimal fourth layers. The other 74 keep
at least 14. The tight classes and their optimal layers are in `hand/window_tight_9_3.json`.

**Removal needs separated pairs (proved).** Let $w(c)$ be the number of window ranks in the
interval of channel $c$, and $S_t=\sum_c w(c)$ after layer $t$. Take a comparator $(u,v)$.
* A rank in the interval of $u$ or $v$ stays in the interval of one of the two outputs, since its
  tokens stay on the comparator. So a comparator removes a rank from at most one output, and only
  if the rank is in both input intervals.
* Rank $k$ leaves the min end if and only if $u$ and $v$ never both hold elements of rank $\ge k$:
  no reachable state of weight $n-k$ has 1 on both.
* Rank $k$ leaves the max end if and only if they never both hold elements of rank $\le k$: no
  state of weight $n-1-k$ has 0 on both.

Call such a pair *$k$-separated*. Weight each pair by the number of window ranks, present in both
intervals, for which it is separated. Let $\nu_5$ be the largest matching of these weights after
layer 4. Then
$$S_5\ \ge\ S_4-\nu_5 .$$
New incidences, when a rank in one input interval reaches both outputs, only increase $S_5$.

* **Measured: the bound is exact.** For one prefix, $S_4-\nu_5$ equals the true least $S_5$ for
  all 994 fourth layers. For 40 exceptional and 40 non-exceptional sample prefixes, its least value
  over fourth layers is the true minimum, at least 13 in every case (`hand/sepbound.py`).
* So (W) is a counting statement: removal in layer 4, plus the largest separation matching after
  it, is at most $S_3-13$.

**Separated pairs are 2-element hitting sets.** $u$ and $v$ never both hold rank $\ge k$ exactly
when, for every input, one of them holds one of the $k$ smallest elements. So the pairs separated
for the min end are the 2-element hitting sets of the family $\mathcal B_k$ of position sets of the
$k$ smallest elements. The pairs separated for the max end are the hitting sets of the family of
position sets of the $n-1-k$ largest elements.
* A layer acts on these families by a routing rule. A comparator holding one of the $k$ smallest
  elements sends it to its min end; one holding two keeps both.
* Rich families have few disjoint hitting pairs. For example, if the 3 smallest elements can sit on
  three pairwise disjoint triples, no pair is separated for rank 3 at the min end.
* Sub-families give valid bounds: positions realized by a few explicit inputs have at least as many
  hitting pairs as the full family. So a hand proof can work with explicit inputs, like the probe
  tables of (P7).

**Measured facts about the trade-off.**
* A comparator of layer 4 keeps at least 3 of its 6 window incidences, by the first point above.
  One of layer 5 can keep only 1, when its inputs are already narrow (`hand/tokpair.c`).
* For one prefix, every fourth layer that removes 9 leaves at most 3 for layer 5. The best pairs
  remove 5, then 9.
* The total mass after the prefix (minimal term and clause sizes, less one each) is 18–23. It is
  only loosely tied to the largest removal (12–14), so it is not the invariant.

### 7.1 The exceptional route, measured

README §5 proves $D(11)\ge8$ through the descent with exceptions. $T_3(7,1)\ge8$ is SS(7, 7, 1, 3),
proved by hand there. The exceptional sets have hand certificates (infinities plus $D(r)$, (P7) or
SS(7, 7, 1, 3)) for 582 of the 663 prefixes of E3(8, 2) and 7 of the 1,010 of E3(9, 3). So a hand
proof by this route needs arguments for exactly these leftovers:

| set | leftovers | second layers | reachable-set classes | settled by a window sum |
|---|---|---|---|---|
| E3(8, 2) | 81 | 7 | 11 | all: ranks {2, 3, 4} or {3, 4, 5} (a complement swaps them) |
| E3(9, 3) | 1,003 | 32 | 135 | all: ranks {3, 4, 5} |

Shortcuts tried, all insufficient on their own:
* **Inputs the prefix never swaps.** Their 0-1 images are the up-sets of the poset of prefix
  comparisons, so the problem would become static. They settle only 32 of 81 and 230 of 1,003.
* **An additive per-channel bound** for layer 5 (each channel's separation potential counted
  separately). It gives −7 to 2 against the 13 needed.
* **Exact intervals through layer 4, overlap-free calculus for layer 5.** It fails for 8.6% of the
  (prefix, layer 4) pairs at (8, 2), in all 81 prefixes, and for 1.84% at (9, 3), in 808 of 1,003
  prefixes (`hand/hybrid_fail.py`). Overlaps at layer 5 matter for a few fourth layers of almost
  every prefix.
* **Splitting on layer 4, then the hand certificates** (`hand/split4_cert.py`). On three sample
  prefixes they settle 80–90% of the fourth layers, leaving 110–223 per prefix.

So by this route each of the 146 classes needs an analysis over about a hundred fourth layers,
some with exact overlaps in layer 5. That is not a hand proof unless a uniform lemma replaces the
case analysis.

### 7.2 Searching for a uniform lemma: what its shape must be

**Exact bookkeeping (proved).** For a channel $c$ let $a_c$ be its least term size and $b_c$ its
least clause size (§5), so its interval is $[b_c-1,\,9-a_c]$, and $a_c+b_c\le10$. Then, after any
layer,
$$S\;=\;27-\sum_c\Big(\min\big(3,(a_c-4)^+\big)+\min\big(3,(b_c-4)^+\big)\Big).$$
The first term counts the window ranks above the interval, the second those below it. A comparator
raises $a$ only at its min end, to the least size of a union of a term of each input. It raises $b$
only at its max end.

**Reaches.** Let $R^+_j$ count the channels that can hold one of the $j$ largest elements, and
$R^-_j$ those that can hold one of the $j$ smallest. Then
$$S_5=\sum_{j=4}^{6}\big(R^+_j+R^-_j\big)-27,$$
so (W) says the six reaches total at least 40. A comparator lowers $R^+_j$ by one exactly when its two
channels can each hold top-$j$ elements but never both at once, and only at its min end. Bottom
reaches mirror this at max ends.

**What the lemma cannot be** (all 1,003 leftovers at (9, 3), `hand/tophalf.c`,
`hand/perrank.c`, `hand/toksingle.c`):
* **Not one-sided.** The top half $R^+_4+R^+_5+R^+_6$ can drop to 19 (329 prefixes), and so can
  the bottom half, but their sum never drops below 40. The two sides trade off.
* **Not per rank.** With a separate best layer-5 matching for each rank, layers 4 and 5 could remove
  15–16 units for every prefix. One common matching removes at most 12–14. Each rank alone can be
  confined: the contradiction is the competition of ranks 3, 4 and 5 for one layer 5.
* **Not additive over channels**, and not overlap-free (§7.1).

**What does hold.**
* For 96% of the pairs of a prefix and a layer 4, a single window rank fails whatever layer 5 is
  (209,365 of 217,905 on 200 prefixes). In 55% all three fail separately. Only 4% need the
  competition.
* The calculus over-narrows only where the two inputs of a layer-5 comparator share inputs through
  the prefix. Their minimal terms overlap, and the union is 1–2 smaller than the sum of sizes.

So a uniform lemma has to bound **one** matching's total separation across adjacent ranks, while
keeping track of overlapping minimal terms. Two forms look worth testing next.
* **A fractional vertex cover** of the joint separation weights after layer 4, with per-channel
  values given by a uniform formula in the channel's terms and clauses. It would replace the
  matching by a sum over channels, exactly where the crude additive bound failed.
* **A term calculus with explicit witnesses**: a few short terms and clauses per prefix channel,
  propagated by unions, as a hand-checkable stand-in for the reachable set.

### 7.3 Vertex covers

Replace the best layer-5 matching by a fractional vertex cover of the joint separation weights
after layer 4. That is, give values $c(x)$ with $c(x)+c(y)\ge w(x,y)$ for every pair. Then
$S_5\ge S_4-\sum_x c(x)$, a sum over channels.

* **Per case, the cover is strong enough** (`hand/lp.py`, an exact simplex; `hand/coverdump.c`).
  On all 23,673 tight pairs of a leftover prefix and a layer 4 ($S_4-\nu\le14$), the least cover
  $\tau^*$ gives $S_4-\tau^*\ge13$.
  * Where $S_4-\nu=13$ there is no gap (642 cases).
  * Where $S_4-\nu=14$ the gap from odd cycles is 0, ½ or 1 (21,581, 1,300 and 150 cases).
  * **Over all 1,075,674 pairs** the cover bound never drops below 13
    (`logs/hand_coverall_9_3.log`). Per prefix its least value is 13 (266 prefixes), 13.5 (167),
    14 (527) or 14.5 (43). The gap over the matching is at most 2, reached only where the slack
    is 5.
* **But there is no uniform cover formula in local data** (`hand/featagg.c`,
  `hand/coverfit.py`). Suppose $c(x)$ is a fixed table over a description of the channel, valid in
  every case. The best worst-case margin $\min(S_4-\sum c)$ is then:
  * about 10 (between 9.5 and 9.96) with the interval after layer 4 as the description;
  * at most 10.0 with the interval and the channel's role in layer 4 (min end, max end, idle).

  13 is needed. A cover must see whether the minimal terms of the two channels overlap, and data
  of one channel cannot.

So covers give short per-case certificates, but a uniform lemma has to bring the term overlaps in.

### 7.4 The witness term calculus

Give each channel a family of **terms**, sets of inputs whose 1s force the channel to 1, and a family
of **clauses**, sets whose 0s force it to 0. The interval is $[b-1,\,n-a]$, with $a$ and $b$ the least
sizes in the two families. Through a comparator:
* the **min end** has as terms the unions of one term of each input, and as clauses both families;
* the **max end** has as terms both families, and as clauses the unions.

With all minimal terms and clauses after the prefix, this is exact through any number of layers.
With fewer witnesses every interval can only narrow, so window counts stay valid lower bounds.
Overlaps are handled automatically, since a union of overlapping sets is small.

**Measured** (`hand/witness.c`, all 1,003 leftovers at (9, 3), layer 5 optimized exactly by a DP
over matchings):

| witnesses kept for each prefix channel | prefixes below 13 | least window sum (count) |
|---|---|---|
| all minimal terms and clauses (exact) | 0 | 13 (230), 14 (730), 15 (43) |
| sizes up to the minimum + 1 | 0 | same as exact |
| **minimum size only** | **0** | 13 (296), 14 (666), 15 (41) |
| one of minimum size | 146 | 11 (5), 12 (141), 13 (625), … |

* The exact version matches the reachable-set search on every prefix tested.
* After a sparse prefix no channel has more than 8 minimal terms or clauses.

So **(W) needs only the shortest terms and clauses of the nine prefix channels**: a small, explicit
set system per prefix.
* Its structure is regular. Each prefix channel computes a nearly read-once formula, and its
  shortest sets are products of choices. For example, $\min(\max(x_5,x_6),\max(x_7,x_8))$ has
  shortest terms {57}, {58}, {67}, {68}.
* Two channels overlap through inputs common to all their shortest sets (the core: input 0 in
  $\min(x_0,x_1,x_2)$ and $\min(\max(x_0,\min(x_1,x_2)),\max(x_3,x_4))$).
* They also overlap through optional choices. A single witness per channel loses these, and fails
  for 146 prefixes.

What is still missing is an argument over all fourth and fifth layers at once. In this language it
must show that two rounds of unions (min ends) and selections (max ends) on these product-structured
families cannot push 15 rank incidences out of the window.

### 7.5 One certificate per prefix, for every fourth and fifth layer

**Block-separable certificates** (`hand/blockcert.py`, exact; `hand/blockcert_fast.py` finds them
with a float simplex and checks them exactly). Fix a prefix.
* A *block* is a possible fourth-layer comparator $(p,q)$ (non-redundant after the prefix) or an idle
  channel.
* Give every block output $x$ a value $c(x)\ge0$, and every prefix channel $p$ a potential
  $\pi(p)$.
* **(cover)** $c(x)+c(y)\ge\mathrm{gain}(x,y)$ for outputs of disjoint blocks, whenever the
  fifth-layer comparator $(x,y)$ is non-redundant. Here the gain is the number of window incidences
  it removes.
* **(block)** $\pi(p)+\pi(q)\le w(\text{min end})+w(\text{max end})-c(\text{min end})-c(\text{max
  end})$ for each comparator block, and $\pi(p)\le w(p)-c(p)$ for each idle one.

Then for any layers 4 and 5,
$$S_5=S_4-\sum_{\text{layer 5}}\mathrm{gain}\ \ge\ S_4-\sum_x c(x)\ \ge\ \sum_p\pi(p).$$
$S_5$ is an integer, so $\sum\pi>12$ proves the prefix. Gains are computed exactly, from truth
tables of the channel functions. No case split over layers 4 and 5 is needed.

**Results.**
* **All 1,003 leftover prefixes at (9, 3) have such a certificate**, each checked exactly
  (`hand/blockcert_left_9_3.jsonl`). The least $\sum\pi$ is 12.17.
* For the family $L_2=(0,1)(2,3)(7,8)$ (ten prefixes) the sums are 12.42–13.5.
* For prefix 0 the optimum is exactly $25/2$, so the integrality of $S_5$ is essential. For prefix
  231 it is $112/9$, with denominators 36.
* A certificate is 9 potentials and about 61–63 cover values.

**How long a written proof of one prefix is.**
* There are 779–877 fifth-layer pairs per prefix. Overlaps only shrink unions, so most pairs can use
  the overlap-free gain bound, which needs only the two outputs' least term and clause sizes.
* A greedy search (`hand/mincrit.py`) still needs exact witness unions for **184** pairs of prefix 0.
* Shortcuts fail: cover values that depend only on the interval reach $\sum\pi=11.25$, and covering
  overlap-free gains everywhere reaches 9.5–10.8.

So a written proof of one prefix is about 70 numbers, about 600 one-line arithmetic checks and about
180 small union computations, all elementary. The family of ten is ten times that. That is a
checkable appendix, not a readable proof. Shortening it needs lemmas that settle whole groups of
pair gains at once, for example by how the shortest terms of prefix channels overlap.

### 7.6 Gain lemmas: the overlaps that matter are between two prefix channels

Every size in a certificate is the least term size $J(S)$ of the AND of a set $S$ of at most four
prefix channels, or the least clause size $K(S)$ of an OR. For example, the min end of a fifth-layer
comparator joining two fourth-layer min ends is the AND of four prefix channels. A max end
contributes an OR, and the least size of an OR of ANDs is the least over its branches. Window counts
only grow when these sizes shrink. So **upper bounds** on the sizes give a bounded window sum that is
at most $S_5$ for every layer 4 and 5, and a certificate for the bounded sums still proves the
prefix.

**Lemma G (pair splitting, proved).** Let $S$ be a set of prefix channels.
1. Drop every member above another member. If $f_q\le f_p$, every term of $q$ is a term of $p$, so
   the AND does not change.
2. Split the remaining members into singletons and pairs.

Then
$$J(S)\ \le\ \sum_{\{p\}}a_p+\sum_{\{p,q\}}\big(a_p+a_q-\mathrm{ov}(p,q)\big),$$
where $\mathrm{ov}(p,q)$ is the largest intersection of a shortest term of $p$ with a shortest term
of $q$. *Proof:* take a shortest term for each singleton and an overlapping pair of shortest terms
for each pair. Their union is a term of the AND, and its size is at most the sum. $K(S)$ is dual:
drop members below another and use shortest clauses.

The bounds hold for the AND and the OR whether or not a comparator ever swaps. So redundant fourth-
and fifth-layer comparators can simply be kept, and no redundancy has to be proved. Only the order
relations used in step 1 are needed.

**Three rules of increasing strength** (`hand/gainrules.py`), each with the best split:
* **meet**: $\mathrm{ov}(p,q)$ is replaced by 1 if some shortest terms of $p$ and $q$ meet, and by 0
  otherwise;
* **ovl**: $\mathrm{ov}(p,q)$ itself;
* **pairw**: each pair contributes one shortest term of the AND of $p$ and $q$, and the bound is the
  size of the union over all parts.

**Results.** All 1,003 leftover prefixes at (9, 3) are certified (`hand/rulecert.py`,
`hand/rulecert_left_9_3.jsonl`).
* Each certificate rounds its cover values up onto a grid, solves for the potentials exactly, and
  re-checks every inequality in exact arithmetic.
* Each prefix uses the weakest rule that certifies it. The class counts are over the 136 meet
  profiles defined below; all prefixes of a class need the same rule.
* The least sum of potentials is $865/72\approx12.01$ (prefixes 76 and 513).

| weakest rule that certifies | prefixes | classes |
|---|---|---|
| meet | 693 | 84 |
| ovl | 277 | 43 |
| pairw | 33 | 9 |
| exact unions at layer 5 | 0 | 0 |

The float LP alone (`logs/hand_gainrules_meet_9_3.log`, with exact pair values in place of ovl)
gives 725, 249 and 29. Rounding the certificates costs a little margin.

* **Step 1 is needed.** Without it, 32 of the first 70 prefixes fail.
* **Cores are not enough.** Count only the inputs common to all shortest terms of a channel. This
  gives 9.9–11.0 on the first ten prefixes, below the 12 needed. The overlaps come from the optional
  choices.
* **pairw needs few unions** (`hand/witcrit.py`). With ovl everywhere else, prefix 13 needs explicit
  unions for 5 of its fifth-layer pairs, and prefix 131 for 1.

So **the overlap information that (W) needs is pairwise, and it is visible in the prefix**: which
shortest terms (and clauses) of two prefix channels meet, and by how much. Apart from 9 classes, a
written proof of a class needs no union at all. It needs the shortest terms and clauses of the nine
channels (at most 8 each), their order relations, and the certificate. Every fifth-layer gain then
follows from one formula.

**Removal is nearly conserved between layers 4 and 5** (`hand/tradeoff.py`,
`logs/hand_tradeoff_9_3.log`). Let $R_4$ be the window incidences that layer 4 removes and $R_5$ the
most that a fifth layer can remove after it. (W) says $R_4+R_5\le14$, since $S_3=27$ for every
leftover.

| $R_4$ | 0 | 1 | 2 | 3 | 4–8 | 9–10 |
|---|---|---|---|---|---|---|
| $R_4+\max R_5$ over all prefixes | 9–12 | 10–12 | 11–13 | 11–13 | 12–14 | 12–13 |

* Whatever layer 4 removes, layer 5 loses almost one for one. Whenever a fourth layer removes
  between 4 and 8, the best one at that level leaves $R_4+\max R_5$ between 12 and 14, in every
  prefix.
* So no case split on $R_4$ helps, and bounding $R_4$ and $R_5$ separately gives only $9+12$.
* As a cross-check, the largest $R_4+R_5$ per prefix reproduces the exact least window sums of §7.4:
  13 for 230 prefixes, 14 for 730, 15 for 43.

**What does not shrink.**
* **The classes.** The data that the meet rule reads, namely $a$, $b$, the order relations and the two
  meet graphs, take 136 distinct values up to relabelling and complement. That is as many as there
  are reachable-set classes (`hand/meetprofiles.py`).
  * Suppose profile $Q$ has all sizes at most those of $P$, and all of $P$'s order relations and
    meets. Then a certificate for $P$ also proves $Q$.
  * This removes only one profile. Richer prefixes have smaller sizes but fewer order relations, so
    profiles are almost never comparable.
* **The checks.** For prefix 0 with all blocks kept:
  * 1,164 fifth-layer pairs have positive bounded gain;
  * 307 of them need the meet information, because $c(x)+c(y)$ is below the overlap-free gain;
  * the cover values have denominators up to 72, and the potentials up to 144.

The gain lemmas remove the explicit unions but not the case structure. A proof of (W) this way is
136 certificates of about a thousand formula checks each. A readable proof needs an argument about
the fifth layer that does not list its pairs. Two candidates:
* classify the pairs that can gain 2 or 3 window incidences, and turn the matching bound into a
  packing argument;
* find a potential on the states after layer 4 that explains the near-conservation of removal, with
  pairwise overlap terms. Per-output covers cannot be uniform (§7.3), so it needs pairwise terms.

### 7.7 A trade-off potential: the fifth layer can be dropped

**Certificates as capacities.** Write $\kappa(p)=3-\pi(p)$. The block condition of §7.5 then says:
the window incidences that a fourth-layer comparator removes, plus the cover values of its two outputs,
fit in $\kappa(p)+\kappa(q)$. Summing over any fourth and fifth layer gives
$$R_4+R_5\ \le\ \sum_p\kappa(p),$$
and (W) is $\sum_p\kappa(p)<15$. So the question is whether the capacities follow a law.

**No capacity law with few parameters** (`hand/captype.py`, `hand/capsearch.py`,
`hand/capsearch2.py`, `logs/hand_capsearch*.log`). The cover values stay free in every class; only
the capacities are uniform. A cutting-plane search over the 136 classes finds the best uniform table:
* The master LP picks a table.
* For each class, a separation LP over fractional fourth and fifth layers (the Farkas dual of the
  certificate LP) returns a violated inequality, if there is one.

| capacity depends on | parameters | worst $\sum_p\kappa(p)$ (must be $<15$) |
|---|---|---|
| the channel's $(a,b)$, complement-symmetric | 6 | 16.02 |
| $(a,b)$ | 10 | 15.92 |
| $(a,b)$ and the numbers of shortest terms and clauses, symmetric | 28 | 15.41 |
| the same, not symmetric | 49 | 15.31 |
| type, plus one term per related channel (order, meeting terms, meeting clauses, shared inputs) | 12–31 | 15.15–15.66 |
| type, plus a relation term that depends on the type | 33–41 | 15.07–15.32 |
| the same, with full relations | 53 | 14.97 (a fit, margin 0.03) |

* Inside a single prefix, capacities that depend only on $(a,b)$ are nearly optimal: 12.35 against
  12.5 for prefix 0. With the term and clause counts they are optimal on the first twelve prefixes.
  Across classes they are not.
* Minimizing the total excess instead of the worst one, a 31-parameter formula still leaves 7 of the
  136 classes above 15.

So the capacities of §7.5 carry per-class information and are not a local law.

**A potential on the state after layer 4.** Take a fourth layer and its 9 outputs. Let $g^*(x)$ be
the largest fifth-layer gain of output $x$ with any other output present, and let
$N_t=\#\{x: g^*(x)\ge t\}$ for $t=1,2,3$.

> **Lemma Q (proved).** Every fifth layer removes at most
> $$Q\;=\;\lfloor N_1/2\rfloor+\lfloor N_2/2\rfloor+\lfloor N_3/2\rfloor\;=\;g^*_{(2)}+g^*_{(4)}+g^*_{(6)}+g^*_{(8)}$$
> window incidences, where $g^*_{(i)}$ is the $i$-th largest best gain.
>
> *Proof.* $R_5=\sum_{t=1}^{3}\#\{\text{fifth-layer comparators with gain}\ge t\}$, and each such
> comparator joins two outputs with $g^*\ge t$.

**Result (exact integers, `hand/qpot.py`, `logs/hand_qpot_left_9_3.log`).** For all 1,003 leftover
prefixes and all 1,075,674 of their fourth layers,
$$R_4+Q\ \le\ 14 .$$
* 899 prefixes reach 14 and 104 stay at or below 13.
* So (W) for the leftovers no longer mentions a fifth layer.
* Since $Q\le\tfrac12\sum_x g^*(x)$, each output pays at most half its best gain. That half-sum
  alone reaches $R_4+\tfrac12\sum g^*=15$ on 98 fourth layers (`hand/localhalf.py`). The rounding in $Q$, which pairs outputs
  level by level, is what closes them. The fractional vertex cover of §7.3 gives 12.5–13.5 there.

**How far it reaches.**
* **It needs the actual fourth layer.** Replace $g^*(x)$ by the best gain with any output of any block
  disjoint from $x$'s block. The bound then depends only on the blocks, but it fails for 863 of the
  1,003 prefixes, by 1 or 2 (11,915 fourth layers; `hand/pairpot.py`). An output's best partner often
  sits in a block that cannot coexist with the rest of the fourth layer.
* **It is not universal.** Over all sparse prefixes, $Q$ fails by 1 on 18 of 1,935 tested (all 935
  with least window sum 13, plus 1,000 at random; `logs/hand_qpot_sample_9_3.log`). All 18 have
  $S_3=25$, and none is exceptional, so the exceptional route of §7.1 is unaffected.

**What it explains.** Let $M_t$ be the number of outputs whose interval holds at least $t$ window ranks.
Then $S_4-Q=\sum_t\big(M_t-\lfloor N_t/2\rfloor\big)$, and (W) reads $\sum_t(M_t-\lfloor
N_t/2\rfloor)\ge13$. At each gain level, a fifth layer can use at most half of the outputs that are
still active at that level. Removal in layer 4 lowers $M_t$, but it also deactivates outputs, which
lowers $N_t$. This is the near one-for-one trade of §7.6.

The statement is now about fourth layers alone and uses only best-partner gains, with no matching. A
hand proof still ranges over about a thousand fourth layers per class, because whether an output is
active depends on the other blocks present.

## 8. Program

1. **$D(11)$ by hand needs a uniform lemma.** Case analysis does not scale (§7.1): 146 classes
   with about a hundred fourth layers each.
   * The candidate is the hitting-set form of §7. Show that the position families of the 3–5
     smallest and largest elements, after a sparse prefix and any fourth layer, are rich enough.
     Removal in layer 4 plus the largest separation matching after it must stay at most
     $S_3-13$, which is 14 when $S_3=27$.
   * Explicit inputs can witness the richness.
   * Per-class certificates exist for all 1,003 leftovers (§7.5–§7.6). They use only pairwise
     overlaps of the prefix channels' shortest terms and clauses, and form a checkable appendix of
     136 certificates. A uniform lemma must explain why removal in layers 4 and 5 trades almost one
     for one (§7.6).
   * The fifth layer can be dropped (§7.7). It removes at most
     $Q=\sum_{t=1}^{3}\lfloor N_t/2\rfloor$, where $N_t$ counts the fourth-layer outputs that can
     still gain $t$ with some other output. $R_4+Q\le14$ holds for every fourth layer of every
     leftover. The certificates' capacities follow no law with few parameters.
   * Until such a lemma is found, $D(11)\ge8$ stands as the hand descent plus a two-minute token
     enumeration, with no SAT.
   * For all 87,075 prefixes it is cross-checked by a second search (window sums, `tokwin.c`). For
     the exceptional prefixes it is also cross-checked by an unpruned recount (`tokfull.c`).
2. **$D(17)$.** The same method needs four layers before the cone.
   * Exhaustive search is out of reach: there are about 2.4 million choices for each of layers 4
     and 5 per prefix.
   * The overlap-free calculus fails over several layers (§5).

   What is needed is a bound on how fast middle rank intervals can narrow that accounts for
   overlap, for instance through the inputs that the minimal terms and clauses of two channels
   share.
   * The $D(13)$ strategy applied here (§10) cuts the SAT route's exceptional children about 4.5
     times through class sharing, to 787 classes at (12, 3) and 6,238 at (13, 4).
   * But its other two steps do not carry over. Exceptional prefixes have no good track for a
     residual, and with four free layers tokens need roughly 200 CPU-hours per class.
3. **$D(13)\ge9$ without SAT** (§9). Tokens settle $T_3(11,4)$ at layer 6, three layers after the
   prefix, again with the obstruction in the middle ranks.
   * A descent prefix by prefix brings the work down to about 15 CPU-hours: 4,561 ten-channel
     residual classes and 216 eleven-channel classes.
   * Direct search would take 530 CPU-hours; the SAT proof of S11 took 17.

## 9. The $D(13)$ level: tokens at (11, 4) (probe)

**The statement.** The hand descent $(13,6)\to(12,5)\to(11,4)$ reduces $D(13)\ge9$ to
$T_3(11,4)\ge9$ (README §5.15). It cannot descend further, because SS(10, 8, 3, 3) is false.
* In token terms, every sparse 11-channel prefix (at most 4 comparators in each of layers 1–3) must
  fail the depth-8 cone.
* The cone is at layer 6, so three layers are free: two at $D(11)$, four at $D(17)$.

**Size.** $T_3(11,4)$ has 2,647,384 prefixes, against 87,075 at (9, 3).
* They come from 177 second-layer classes, and 1,714,809 of them have a full third layer.
* They form 315,835 classes of reachable sets up to relabelling and complement (`hand/classcount.c`).
  The same tool gives 6,641 classes at (9, 3).

**Tokens refute every sampled prefix exactly at layer 6** (`hand/tokcore.c`,
`logs/probe13_tokcore_sample.jsonl`).
* **The sample** (`hand/sample_prefixes.py`, seed 1): 708 prefixes, three random full third layers
  and one smaller one per second-layer class.
* **The result:** no sixth layer survives for any of the 708.
* **The work:** per prefix, about 14,000 fourth layers and 1.1 million fifth layers (up to 6.3
  million), in 3.5–57 s. The median was 8.9 s with ten jobs sharing the machine, about 6 s with fewer.
* **Soundness check:** the search must not refute a feasible sparse prefix. `thinsat.py 10 8 3
  --capped 3` finds a depth-8 10-sorter with layer sizes 3,3,3,5,5,4,4,5. On its first three layers
  the same search finds the 2 surviving sixth layers and a complete sorter, in 7 s.

**The obstruction is in the middle ranks again.** A beam search (`hand/tokbeam.c`) finds the
closest continuations. For the two closest prefixes it reaches $|T_6(k)|$ =
[2,3,4,4,4,5,5,4,4,2,1] and [2,4,4,4,5,5,4,4,4,2,1]. These miss the cone only at two middle ranks, as
at $D(11)$: ranks 4–6 hold 14 tokens where 12 are allowed.
* Only the exact search counts. The beam search misses the feasible 10-channel continuation, ending
  at penalty 1.

**Naive cost.** Searching all 315,835 classes directly would take about 315,835 × 6 s ≈ 530
CPU-hours. Caching states after layer 4 helps little: the sample's 9.9 million fourth-layer states fall
into 7.3 million distinct classes (`hand/x4count.c`).

### 9.1 The proof, by a descent prefix by prefix (about 15 CPU-hours)

**The idea.** Theorem 1's sentinel step works for each prefix on its own.
* Put $+\infty$ on the high end of a first-layer comparator, or $-\infty$ on the low end, and suppose
  its track meets every full layer. Removing the track leaves a 10-channel prefix with at most 3
  comparators per layer: the *residual*.
* If the residual has no depth-8 completion, neither has the prefix, because a completion of the
  prefix restricts to one of the residual.
* The statement $T_3(10,3)\ge9$ is false as a whole, but tokens refute almost every residual class.

**Two facts make this cheap.**
* **Subsumption** (Bundala–Závodný; Codish, Cruz-Filipe, Frank, Schneider-Kamp). Prefixes whose
  reachable sets agree up to a relabelling and complement extend together or fail together.
  * So one search settles a class.
  * A residual is settled when its class is refuted, whatever its own layers look like.
* **No untangling is needed.** The residual's reachable set is the image of the inputs with the
  sentinel's value, with the sentinel's channel deleted.
  * On 264 sentinel choices it agrees with the untangled residual of `sentinel_prover.residual2`.
  * End to end: for 40 random class representatives, the untangled residual itself, searched without
    any canonical form, is refuted (`hand/resid_check.py`, `logs/hand_d13_resid_check.log`).

**The computation.**

| step | tool | result |
|---|---|---|
| classes of $T_3(10,3)$ | `hand/classcount.c` | 147,776 prefixes, 9,897 classes |
| residuals of all 2,647,384 prefixes, good tracks only | `hand/resid.c`, 32 CPU-min | 29,960,072 residuals; 315,654 of the 315,835 classes have one in a (10, 3) class |
| greedy choice of residual classes | `hand/needed10.py` | 4,203 classes would cover all 315,654 |
| token search, (10, 3) classes | `hand/tokcore2.c`, 12.5 CPU-h | 4,571 searched: 4,561 refuted, 10 completed to depth-8 sorters |
| token search, (11, 4) classes directly | 1.9 CPU-h | 216 searched (181 with no family residual, 35 whose residual classes all completed): all refuted |
| assembly | `hand/assemble13.py` | **all 315,835 classes settled**: 315,619 through a refuted residual class, 216 directly |

* The witness of every class is in `logs/hand_d13_token_witness.tsv.gz`: the residual class used, or
  "direct".
* The 10-channel searches are in `logs/hand_tok10_d13.jsonl` and the direct ones in
  `logs/hand_tok11_d13_direct.jsonl`.
* `hand/tokcore2.c` adds a sound filter to `tokcore.c`. At rank $k$, one layer lowers $|T(k)|$ by at
  most the largest matching of the pairs of token channels that can merge. It saves 14–26% and changes
  no outcome: the feasible control is still completed.
* Canonical forms skip orders of interchangeable channels (the set is invariant under their
  transposition). That leaves every hash unchanged, as checked at (10, 3) and (11, 2), and is 11
  times faster on sparse prefixes.

**Result.** **$D(13)\ge9$ without SAT**, in the same form as $D(11)\ge8$:
* the hand descent to $T_3(11,4)$;
* token searches on 4,561 ten-channel classes and 216 eleven-channel classes;
* class and residual bookkeeping.

That is about 15 CPU-hours in all, two and a half hours on this laptop, against 530 for direct
search and 17 for the SAT proof of S11.
* Each search uses only the token cone, from rank intervals (§5), the cone bounds and the normal
  form.
* The two caveats of the first run are settled in §9.2. Class identity rested on 128-bit hashes of
  canonical forms, and there was no second implementation. An independent hash-free check now
  agrees on every count.

### 9.2 An independent check (hash-free, fewer facts)

**What is rechecked.** Every computational step of §9.1, by new code written from the definitions
(`hand/indep13/`). It shares no code with `classcount.c`, `resid.c`, `tokcore*.c` or `assemble13.py`.
`run_all.sh` runs it end to end.

| step | tool | result |
|---|---|---|
| second-layer cover | `verify_cover.py` (the repository's checker) | 19,320 legal second layers in 177 disjoint orbits: the cover is complete |
| family | `cls.c` | 2,647,384 prefixes |
| classes | `cls.c` | 315,835 classes; the partition agrees prefix by prefix with the hash partition (`partition.py`) |
| residuals | `cls.c` | 315,619 classes settled through a refuted 10-channel prefix (1.0 million residuals tried) |
| direct | `cls.c` | the other 216 classes map onto the 216 refuted 11-channel prefixes |
| token searches, 11 channels | `tok.c`, 1.1 CPU-h | all 216 refuted |
| token searches, 10 channels | `tok.c`, 8.1 CPU-h | 4,561 refuted; the other 10 give depth-8 sorters |
| spot check | `wcheck.py` (plain Python) | 3,000 random prefixes and all 581 prefixes of the direct classes |

In all about 9 CPU-hours, an hour on this laptop, against 14.4 for the token searches of §9.1; the
class and residual check takes a minute.
* The prefixes `tok.c` refutes are exactly the lemmas of §9.1.
* With them, `cls.c` settles every class (`logs/ind13_tok10.txt`, `logs/ind13_tok11.txt`).

**No hashes decide identity.** `cls.c` relabels a set onto a stored one by an explicit channel
permutation, with or without complement. It finds the permutation by search and checks it state by
state. Hashes only choose which stored sets to try.
* The class count is exact: two prefixes are put in different classes only after an exhaustive
  search finds no permutation.
* Every class, residual and direct link is written out with its permutation
  (`logs/ind13_class_witness.tsv.gz`). `wcheck.py` rereads samples of it and recomputes every set from
  the comparators.
* **The 128-bit hashes of §9.1 were right.** Over all 2,647,384 prefixes, the map from hash to
  permutation class is a bijection: no class is split and no two classes collide.

**Residuals need no track condition.** Any sentinel works, not only a track that meets every full
layer.
* Removing a sentinel's track from a depth-8 completion leaves a depth-8 sorter on the other ten
  channels. Its first three layers reach a relabelling of the residual set.
* The condition only served to land residuals in the enumerated (10, 3) classes. `cls.c` tries all
  14 sentinels of a prefix and checks that the track end holds the sentinel's value on every image.
* With the same lemmas it settles exactly the same classes: 315,619 through residuals and 216 directly.

**Fewer facts in the token search.** `tok.c` uses only three facts:
* **Rank intervals** (Lemma 2), computed from per-channel extreme weights rather than from probe pairs.
* **The cone size bound** $|T_t(k)|\le2^{D-t}$, which every depth-$D$ sorter satisfies.
* **Deleting comparators that never swap.**

It does not use the end-game normal form (the positional cone $T_6(k)\subseteq[k-4,k+4]$) or the
merge-matching filter. It still refutes the same prefixes, almost all at layer 6:
* At layer 6, 4,484 of the 4,561 ten-channel prefixes and 202 of the 216 eleven-channel ones have no
  layer within the bound.
* The other 91 have a few layer-6 survivors but no layer 7.
* **Node counts agree with `tokcore2.c` at every layer for all 4,787 prefixes.** For a refuted prefix
  these are exact counts of the layers within the bounds, so this is a strong test of both programs.
  It also shows that here the positional cone removes no layer that the size bound keeps.
* The 10 feasible 10-channel classes give depth-8 sorters, each verified on all 1,024 inputs
  (`checksorter.py`).
* The program also finds optimal-depth sorters for 4–8 channels, and refutes one layer less.

**What is still taken on trust.** The mathematics:
* the hand descent to $T_3(11,4)$ (README §5.15);
* the sentinel step and subsumption, with complement as reflection;
* Lemma 2 and the cone bound.

## 10. $D(17)$: the same strategy (probe)

**Where the work is.** The descent with exceptions (README §8.14) reduces $D(17)\ge10$ to the
exceptional children at three levels:

| level | exceptional children (census) |
|---|---|
| (14, 5) | 11,402 |
| (13, 4) | 27,582 |
| (12, 3) | 3,748 |

* The bottom of the descent, $T_3(11,2)\ge10$ (SS(11, 9, 2, 3)), is proved.
* Today every exceptional child needs SAT, 1–6 minutes each.

**What carries over from $D(13)$: classes.** By subsumption, one refutation settles a whole
reachable-set class. A class that also contains a non-exceptional prefix needs no refutation at all:
the descent lemma settles that prefix, and the class with it (`hand/excres.c`, the whole normal-form
family enumerated per level).

| level | prefixes | exceptional | classes | classes with only exceptional prefixes |
|---|---|---|---|---|
| (12, 3) | 690,806 | 68,079 | 12,226 | **787** (3,748 children in the census) |
| (13, 4) | 24,332,564 | 225,719 | 742,163 | **6,238** (27,582 children) |
| (14, 5) | not enumerated (107 million canonical children) | | | (11,402 children) |

So the measured levels need about 4.5 times fewer refutations.
* Most of the saving is that exceptional prefixes share reachable sets. At (13, 4), only 12% of the
  225,719 exceptional prefixes lie in a class with a non-exceptional prefix; the other 198,498 fall
  into 6,238 classes.
* Each level relies on the level below being settled first, as the descent does anyway.

**What does not carry over.** `hand/d17_probe.sh` reruns both measurements.
* **Residuals.** An exceptional prefix has no good track, so every sentinel residual keeps a full
  layer. Its class is then never the class of a sparser prefix (`logs/hand_d17_resid_12_3.log`).
  * Take every member of the 787 exceptional-only (12, 3) classes and all 24 sentinels, on any track.
  * None of these residuals lies in one of the 253 classes of the proved (11, 2) family.
* **Tokens.** At depth 9 the cone is four layers after the prefix (`hand/d17_tokrate.py`,
  `logs/hand_d17_tok_12_3.log`).
  * The first exceptional-only (12, 3) class has 72,948 fourth layers, each with tens of thousands
    of fifth layers.
  * A capped run covers the first 32 fourth layers in about 65 s. Those are cheap ones, and the
    16 CPU-hours per class first quoted here was extrapolated from them.
  * 100 random fourth layers, each searched to the end, take 13 s each on average (3–26 s). That
    gives 264 CPU-hours for the class as measured.
  * The same capped run took 87 s during the measurement instead of about 65 s, because other work
    was running. So on an idle performance core the class needs roughly 200 CPU-hours, against minutes
    for SAT.

**What it means.** The strategy cuts the SAT work but does not remove SAT.
* The count drops to about 787 + 6,238 + an estimated 2,500 at (14, 5), about 9,500 refutations
  instead of 43,000.
* At the measured 2–4 minutes each, that is roughly 300–650 CPU-hours instead of 1,200–1,600.
* The class representatives for (12, 3) and (13, 4) are in `hand/exconly_12_3.json` and
  `hand/exconly_13_4.json`, ready for the SAT pipeline of README §8.15.
* (14, 5) needs its family enumerated: about 100 times (13, 4), so hundreds of CPU-hours with this
  tool.
* A $D(17)$ proof without SAT needs an argument across four layers, which tokens do not give.
