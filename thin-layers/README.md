# A sentinel descent: D(13) and D(17) reduced to one sparse-start statement each

## Names used here

A **sparse-start statement** says that a sorting network cannot begin sparsely:

> **SS(n, d, a, m)**: no sorting network on n channels with depth d has at most a comparators in
> each of its first m layers.

The statements that matter, with short names:

| name | statement | what it gives | status |
|---|---|---|---|
| **H9** (h9.md) | SS(9, 7, 3, **2**): 9 channels, depth 7, first **two** layers ≤ 3 | D(11) ≥ 8 | true, **without SAT**: sentinel proof of 3,172 checked lines in [facts/](facts) (§8.4) |
| **S9** | SS(9, 7, 3, 3): same, first **three** layers ≤ 3 (weaker than H9) | D(11) ≥ 8 | true: SAT, 258 s, DRAT-checked |
| **S11** | SS(11, 8, 4, 3): 11 channels, depth 8, first three layers ≤ 4 | **D(13) ≥ 9** | **true**: all 177 cases UNSAT (median 5.3 min), all 177 DRAT-verified; 87 cases after subsumption (§8.2); and **without SAT in the proof**: sentinel proof of 382,318 checked facts in [facts_s11g/](facts_s11g) (§8.8) |
| **S12** | SS(12, 8, 5, 3) (implied by S11) | D(13) ≥ 9 | 18/387 cases UNSAT (hedge, stopped) |
| **S14** | SS(14, 9, 5, 3): 14 channels, depth 9, first three layers ≤ 5 | **D(17) ≥ 10** | open: 682 cases; one probe case is slow |
| S8, S6 | SS(8, 6, 3, 3), SS(6, 5, 2, 3) | D(9) ≥ 7, D(7) ≥ 6 | true: SAT under a second, DRAT-checked; SS(6, 5, 2, 3) also by hand certificates |

The function $T_3(n,a)$ below is the least depth of an $n$-channel sorter whose first three layers
have at most $a$ comparators, so SS(n, d, a, 3) is the statement $T_3(n,a)>d$; for example
S11 is $T_3(11,4)\ge9$. A false sparse-start statement found on the way: SS(10, 8, 3, 3) fails
(a depth-8 10-sorter with layer sizes 3,3,3,5,5,4,4,5 exists), so the descent for D(13) cannot go
below 11 channels.

**Status (2026-11-20).** $D(11)\ge8$ now has a proof **without SAT**: the sentinel prover of
§8.3–8.4 proves H9 and then $D(11)\ge8$, which takes 5 more lines on top of H9 (the descent
11 → 10 → 9 channels, found by the prover). The proofs live in the fact store [facts/](facts)
(H9: 3,172 lines; all 17 proved statements: 1,178 facts) and pass an independent checker. $D(13)\ge9$ follows from the descent below plus
S11, which is settled twice: by SAT (177 cases, median 5.3 minutes each, all DRAT-verified) and, since
2026-11-20, by the sentinel prover with SAT only as a guide (382,318 facts in [facts_s11g/](facts_s11g),
all checked; §8.8). $D(17)$ is reduced to S14, which is not yet settled. This note proves, by hand, that

$$D(13)\ \ge\ T_3(11,4)\qquad\text{and}\qquad D(17)\ \ge\ T_3(14,5),$$

so $D(13)\ge 9$ follows from **S11** alone and $D(17)\ge10$ from **S14** alone. These replace
the 117 and 609 two-layer prefix cases of the classical computer proofs. Whether S11 and S14 are
true, and how fast a SAT solver settles them, is recorded under "Results" below: S11 is true,
S14 is open.

The method does not reach $D(18)$: see the last section.

## 1. Definitions

Networks are standard (a comparator $(i,j)$, $i<j$, puts the minimum on $i$); layers are matchings.
For $0\le a\le\lfloor n/2\rfloor$ and $m\ge1$ let $T_m(n,a)$ be the least depth of an $n$-channel
sorting network whose layers $1,\dots,m$ have at most $a$ comparators each. Then
$T_m(n,\lfloor n/2\rfloor)=D(n)$, $T_m(n,a)\ge D(n)$, and $T_m$ does not decrease when $m$ grows or
$a$ shrinks. Write $k=n-2a$ for the number of channels a layer with exactly $a$ comparators leaves
idle.

## 2. Two standard facts

**Fact A (first layer).** Adding a comparator between two idle channels of the first layer keeps a
sorting network sorting: the new comparator only permutes the input. Relabeling channels and
untangling (Knuth, TAOCP 5.3.4, Ex. 16) turns any first layer of $a$ comparators into any other
fixed one, keeping every layer size. So a network counted by $T_m(n,a)$ may be assumed to have
**exactly** $a$ comparators in its first layer, placed anywhere we like.

**Fact B (one sentinel).** Let $N$ sort $n$ channels in depth $d$. Put $+\infty$ (or $-\infty$) on
one input and distinct reals on the others. The sentinel's channel after every layer is fixed by
$N$ alone: it goes to the max end (min end) of every comparator it meets. A real that meets the
sentinel goes to the other end, whatever its value. So the comparisons between two reals form a
generalized network $R$ on $n-1$ tracks, of depth at most $d$, whose layer $t$ has
$|L_t|-1$ comparators if the sentinel meets a comparator of $L_t$, and $|L_t|$ otherwise. $N$ puts
the sentinel on the extreme output and the reals in order on the rest, so $R$ sorts; untangling
makes it a standard $(n-1)$-channel sorting network with the same layer sizes.

## 3. The track lemma

Let the first layer be $(lo_1,hi_1),\dots,(lo_a,hi_a)$, exactly $a$ comparators, and let
$|L_2|,|L_3|\le a$. A $+\infty$ placed on an input of comparator $j$ sits on $hi_j$ after $L_1$;
a $-\infty$ sits on $lo_j$. Call the sentinel's track **good** if it meets a comparator of $L_2$
whenever $|L_2|=a$, and a comparator of $L_3$ whenever $|L_3|=a$. (It always meets one of $L_1$.)

**Lemma (track lemma).** If
$$\Big\lceil \tfrac{2a-k}{2}\Big\rceil>k\qquad\text{and}\qquad 2\Big\lceil\tfrac a2\Big\rceil>k,$$
then one of the $2a$ sentinels has a good track.

*Proof.* A layer with exactly $a$ comparators leaves exactly $k$ channels idle; call them $V$ for
$L_2$ and $W$ for $L_3$ when those layers are full.

*Both $L_2$ and $L_3$ full.* Let $H=\{j:hi_j\notin V\}$ and $O=\{j:lo_j\notin V\}$; since
$|V|=k$, $|H|+|O|\ge 2a-k$. For $j\in H$ the $+\infty$ track meets the $L_2$ comparator at $hi_j$
and moves to its **max** end; for $j\in O$ the $-\infty$ track moves to the **min** end of the
$L_2$ comparator at $lo_j$. A comparator holds at most two of the channels $hi_j$, so the
$+\infty$ tracks of $H$ end on at least $\lceil|H|/2\rceil$ distinct max ends; likewise the
$-\infty$ tracks of $O$ end on at least $\lceil|O|/2\rceil$ distinct min ends. No channel is both a
max end and a min end of a matching, so these are at least
$\lceil|H|/2\rceil+\lceil|O|/2\rceil\ge\lceil(2a-k)/2\rceil>k=|W|$ distinct channels. One of them
is not idle in $L_3$, and its track is good.

*$L_2$ not full, $L_3$ full.* All $2a$ tracks qualify at $L_2$. After $L_2$ a $+\infty$ track is on
a max end of $L_2$ or on an $L_2$-idle $hi_j$; a $-\infty$ track is on a min end or an $L_2$-idle
$lo_j$. These two kinds of channel are disjoint, and each kind holds at least $\lceil a/2\rceil$
tracks' positions (one comparator merges at most two tracks). So at least
$2\lceil a/2\rceil>k$ channels carry tracks, and one is not idle in $L_3$.

*$L_3$ not full.* Only $L_2$ may need meeting; at most $k<2a$ of the $2a$ start channels are idle
in a full $L_2$. If neither is full every track is good. ∎

The lemma is sharp in the cases checked: `track_lemma_check.py` enumerates **every** second layer
(no symmetry reduction) for 14 pairs $(n,a)$ with $n\le15$, including all 10,349,536 second layers
at $(15,7)$. Where the condition holds no second layer defeats every track; where it fails,
second layers that defeat every track against a suitable third layer exist
([results/track_lemma_check.json](results/track_lemma_check.json)).

## 4. The descent

**Theorem 1.** If $(n,a)$ satisfies the condition of the track lemma, then
$T_3(n,a)\ge T_3(n-1,a-1)$.

*Proof.* Take a sorting network counted by $T_3(n,a)$; by Fact A its first layer has exactly $a$
comparators. Put the sentinel the lemma provides. By Fact B the residual network sorts $n-1$
channels in the same depth; its first layer has exactly $a-1$ comparators (the other first-layer
comparators involve no sentinel), and its second and third layers have at most $a-1$: a full layer
lost the comparator the sentinel met, and a layer that was not full had at most $a-1$ already. ∎

Starting from $D(2p+1)=T_3(2p+1,p)$ ($k=1$) and descending while the condition holds:

| target | chain (each step by Theorem 1) | stops at ($k$ there) | remaining statement |
|---|---|---|---|
| $D(7)\ge6$ | $(7,3)\to(6,2)$ | $(6,2)$, $k=2$ | $T_3(6,2)\ge6$ |
| $D(9)\ge7$ | $(9,4)\to(8,3)$ | $(8,3)$, $k=2$ | $T_3(8,3)\ge7$ |
| $D(11)\ge8$ | $(11,5)\to(10,4)\to(9,3)$ | $(9,3)$, $k=3$ | $T_3(9,3)\ge8$ — implied by (H9) |
| $D(13)\ge9$ | $(13,6)\to(12,5)\to(11,4)$ | $(11,4)$, $k=3$ | $T_3(11,4)\ge9$ |
| $D(15)$ | $(15,7)\to(14,6)\to(13,5)\to(12,4)$ | $(12,4)$, $k=4$ | (only $T_3(12,4)\le D(15)=9$) |
| $D(17)\ge10$ | $(17,8)\to(16,7)\to(15,6)\to(14,5)$ | $(14,5)$, $k=4$ | $T_3(14,5)\ge10$ |

For $D(11)$ the remaining statement is weaker than (H9) of [h9.md](../depth-hand-proofs/h9.md),
which restricts only two layers; so the descent re-derives the two-sentinel route and shows it
also tolerates a thin third layer.

### 4.1 Descending past the lemma: exceptional networks

Where the counting condition fails, most networks still have a good track. Call a network
**exceptional at $(n,a)$** if none of its $2a$ sentinels has a good track, and let $E_3(n,a)$ be
the least depth of an exceptional sorting network there. The proof of Theorem 1 gives

$$T_3(n,a)\ \ge\ \min\big(T_3(n-1,a-1),\ E_3(n,a)\big).$$

"Exceptional" is a condition on the first three layers only. `exceptional.py` writes it as SAT
clauses: one-hot track positions with full equivalences, and a full-layer indicator per layer. It
agrees with a direct computation on 1,500 random layer stacks per level, and on 600 mutations of a
hand-built exceptional stack (353 exceptional, 247 not) (`test_exceptional.py`). So "no exceptional
sorter of depth $d$" is one small SAT question, separate from the descent.

## 5. D(11) ≥ 8 with two small SAT checks (and now without SAT: §8.3)

Descend $(11,5)\to(10,4)\to(9,3)$ by Theorem 1, then $(9,3)\to(8,2)\to(7,1)$ with exceptions:

1. $E_3(9,3)\ge8$: no exceptional 9-channel sorter of depth 7. SAT, 21 s; DRAT proof checked by
   `drat-trim`.
2. $E_3(8,2)\ge8$: no exceptional 8-channel sorter of depth 7. SAT, 20 s; DRAT checked.
3. **SS(7, 7, 1, 3) by hand.** Let $c_1,c_2,c_3$ be the at most one comparator of layers 1–3.
   If a layer is empty, or $c_2=c_1$ (then $c_2$ never swaps and can be deleted), deleting it
   leaves a depth-6 sorter whose first layer has at most one comparator, contrary to (P7)
   ([h9.md](../depth-hand-proofs/h9.md), Theorem 14). If $c_2\cap c_3=\emptyset$, merge layers 2
   and 3: the same contradiction. Otherwise pick $w\in c_2\cap c_3$ and an input $u$ of $c_2$
   outside $c_1$. Put an infinity on $u$ whose sign sends it to $w$ at $c_2$, and one of the opposite
   sign on an input of $c_1$. They meet $c_1,c_2,c_3$ between them (opposite signs never disturb
   each other's track), so the other five inputs are compared only in layers 4–7, and four layers
   cannot sort five values ($D(5)\ge5$). `ss7_hand.py` confirms the case split on all 10,647
   configurations.

So $D(11)\ge8$ rests on hand arguments, (P7), $D(5)\ge5$, and two SAT instances of about 20 seconds
each. The single statement S9 = SS(9, 7, 3, 3) is also proved directly (258 s, DRAT checked).

## 5.1 Hand certificates: sparse-start statements without SAT

A sparse-start statement only restricts the first $m$ layers, so it can be attacked prefix by
prefix. For a prefix $P$ and a set of infinities, the comparisons between two real inputs inside
$P$ form a comparator DAG on the real tracks; with height $h$ it reschedules into $h$ layers. The
real inputs are then sorted by a network of depth $h+f$, where $f=d-m$ counts the free layers. A
**certificate** is a set of infinities plus one rule that turns this into a contradiction, using only
results proved by hand:

* **D:** $h+f<D(r)$ for the $r$ real inputs ($D(r)$ for $r\le10$, README).
* **P7:** $r=7$, $h+f=6$, and every height-$h$ schedule can put at most one comparator first (P7).
* **SS7:** $r=7$, $f=4$, at most three real comparisons in $P$; as three one-comparator layers they
  contradict SS(7, 7, 1, 3).

`prefix_cert.py` searches up to four infinities; `prefix_cert_all.py` runs it on every prefix (layer
2 over its symmetry classes). It never certifies the prefix of an actual sorter: it refuses the
counterexample to SS(10, 8, 3, 3) and the residual prefix of a real 13-sorter after two descents.

| statement | prefixes | certified by hand | left over |
|---|---|---|---|
| SS(7, 6, 1, 2) | 4 | 4 | 0 |
| SS(8, 8, 1, 4) | 2,523 | **2,523** (no SAT) | 0 |
| **SS(9, 8, 2, 4)** | 2,755,600 | 2,754,931 | 669, each UNSAT with the prefix fixed (≤ 0.04 s; 13.7 s in all); SAT on the whole statement did not finish in 20 minutes |
| SS(6, 5, 2, 3) | 854 | **854** (851 + 3 by the merge rule below; no SAT) | 0 |
| SS(8, 7, 2, 3) | 3,824 | 3,743 | 81, each UNSAT with the prefix fixed (≤ 0.03 s; 1.6 s in all) |
| exceptional prefixes at (8,2), depth 7 | 764 | 683 | 81 |
| exceptional prefixes at (9,3), depth 7 | 1,200 | 17 (merge rule: 12 by (4,3,2), 4 by (3,3,3), 1 by (4,4,1)) | 1,183 |

Random samples: SS(10, 8, 3, 4) 198/200 and SS(11, 8, 4, 4) 98/100 certified; S11 = SS(11, 8, 4, 3)
only 58/100. The pattern: certificates prove statements with slack (four sparse layers, or depth
above $D(n)$). What they cannot reach are the efficient, Green-filter-like prefixes of statements
at depth $D(n)$, whose impossibility depends on the later layers. Those still need SAT on the
fixed prefix, or stronger hand rules.

**Merge rule (`static_cert.py`).** Inputs that no prefix comparator swaps are exactly the linear
extensions of the prefix's comparison poset $Q$; the prefix leaves them alone, so the $f$ free
layers must sort all of them. Send a down-set of $Q$ to $-\infty$ and an up-set to $+\infty$; if
the rest of $Q$ is a disjoint union of chains, the free layers merge those chains. An element in
place $i$ of a chain of size $c$ can be the $k$-th smallest exactly when
$i\le k\le i+N-c$ ($N$ elements in all), so some output depends on that many elements and its
backward cone needs $\lceil\log_2\rceil$ of that many layers. Antichains use $D(r)$, and chain
sizes (4,4,1), (4,3,2), (3,3,3) use the five-layer merger bounds proved by hand in
`h9_feedback_round2_merge432.md`, `h9_feedback_round3_merge333.md` and
`../d18-search/d13_feedback_round3_merger441.md`. (A first version used the size of the whole
union as the cone bound; that is false, e.g. inserting one element into a sorted 4-list has no
output depending on more than 3 elements, and was corrected before use.) The rule finishes
SS(6, 5, 2, 3): its three leftover prefixes are two chains of sizes 3 and 2 that two layers cannot
merge. It does not touch the 81 leftovers at (8, 2), whose natural next lemma is
"no depth-6 7-sorter has at most one comparator in its second layer" (true by an instant SAT
check, and tight: two comparators suffice), a (P7)-type statement still to be proved by hand.

## 5.15 D(13) ≥ 9

By Theorem 1 twice, $D(13)=T_3(13,6)\ge T_3(12,5)\ge T_3(11,4)$, so S11 = SS(11, 8, 4, 3)
suffices. Its first layer is (1,2)(3,4)(6,7)(8,9) (idle 0, 5, 10). Its second layer runs over 177
classes (cover verified: 19,320 legal second layers), and each class is one SAT instance with
layers 3–8 free and layer 3 capped at 4.

* Second layer empty (1 class): the network is a depth-7 11-sorter, contrary to $D(11)\ge8$.
* One second-layer comparator (4 classes): an infinity on it (reachable after layer 1 by choosing
  its start and sign) leaves ten real inputs sorted in seven effective layers whose first two
  have at most four comparators, contrary to SS(10, 7, 4, 2) (SAT, about 2 minutes; it also
  descends by Theorem 1 to H9).
* The other 172 classes: SAT. **All 177 classes are UNSAT** (the run also covers the five above):
  wall time per case 89 s to about 10 minutes, median 317 s, about 17 CPU-hours in all (five
  cases show about an hour because they were in flight during a 50-minute pause). Results:
  [results/T3_11_4_d8_l2cases.jsonl](results/T3_11_4_d8_l2cases.jsonl).

Each case's final CNF was re-solved by the standalone CaDiCaL 2.1.2 with a DRAT proof, and
`drat-trim` **verified all 177 proofs** (`finalize_s11.sh`, [results/S11_drat.jsonl](results/S11_drat.jsonl):
19.3 h of solving and 23.7 h of checking in total, largest proof 365 MB, each CNF's sha256 recorded). Three
classes were re-decided by the independent `satnet.py` encoder (every prefix image, no end-game
constraints, no CEGAR) and agree: second layer of 4 comparators UNSAT in 413 s, second layer of 3 comparators UNSAT in 523 s, second layer of 0 comparators UNSAT in 586 s ([results/S11_crosscheck.jsonl](results/S11_crosscheck.jsonl)).

## 5.2 D(17): where the computation stands

The descent gives $D(17)\ge T_3(14,5)$ by hand, so S14 = SS(14, 9, 5, 3) suffices. It splits into
682 second-layer classes (cover verified). Each is a 14-channel, depth-9 problem with seven free
layers. One probe case (class 681) had not finished its first CEGAR round after 75 CPU-minutes,
whereas S11 cases finish completely in 1.5–10 minutes (median 5.3). Stopping the descent earlier
does not look cheaper per case: one probe case each of S15 = SS(15, 9, 6, 3) and S16 =
SS(16, 9, 7, 3) (tight, since depth 9 is $D(16)$) also had no first-round answer after 27
CPU-minutes, and those statements have more cases. Going deeper by exceptions is not obviously
cheaper. The next level is the tight statement $T_3(13,4)\ge10$ (depth 9 is $D(13)$, so no slack
for certificates). Lower levels have slack but are hard for SAT: SS(10, 9, 1, 3) did not finish in
2 minutes, and certificates there need a richer rule set than D/P7/SS7. §8.11 measures the cost
of S14. With SAT, none of eight cases finished within 3 hours. With the sentinel prover and a
compiled core (§8.11–8.12), 83 of the 682 cases are proved, each root by one sentinel step: the
cases whose second layer has at most 3 comparators, all but 19 of them. The 580 cases with 4 or 5
second-layer comparators need root splits of 10,000–42,000 children each. For case 0
(§8.13), 94.5% of its 17,881 children close by one sentinel step onto a stored residual. The other
980 need deep proofs: some are still open after 20 minutes and 27,000 nodes. That puts this one
case at over 100 worker-hours and millions of facts. Every worker holds the whole store in
memory, so this laptop cannot finish the case. §8.14 finds that S14's cases have 107 million root
children in all, and that the descent with exceptions (§4.1) one and two levels further down
leaves about 39,000 exceptional children plus T3(12, 3) (41,039 children). SAT refutes such
children in 1–6 minutes each, with checked DRAT proofs. §8.15 builds this route, from
SS(11, 9, 2, 3) up, as `descent_run.sh`: about 43,000 exceptional children in all, roughly
2,000–3,000 CPU-hours. The original 609-case proof in 2015 took about 27.6 million
CPU-seconds (roughly 7,700 CPU-hours) ([d18-search/README.md](../d18-search/README.md)).
The open problem is a hand rule strong enough for the efficient (Green-filter-like) prefixes.

## 5.3 Why this cannot reach D(18)

For even $n=2p$ the first layer can be perfect ($k=0$), and one sentinel leaves $2p-1$ reals whose
layers have at most $p-1$ comparators, which is no restriction at all on $2p-1$ channels. Any
descent from $D(18)$ therefore passes through $T_3(17,8)=D(17)=10$ and proves nothing beyond
$D(18)\ge10$. This agrees with the first-two-layer obstruction in
[extension.md](../depth-hand-proofs/extension.md).

Variants do not help either. Two infinities of opposite sign on one first-layer comparator leave
a 16-channel residual of depth 10 whose layers 2 and 3 have at most 7 comparators; but $D(16)=9$
leaves a whole layer of slack. For example, split one comparator of a depth-9 16-sorter's second
layer into its own layer. Every restriction that thins layers leaves at most 16 reals, and depth
10 is then never tight. So D(18) needs either a new kind of argument about 17-channel sorters of
depth 10 (17 would have to be "tight", unlike every odd width up to 15) or the full computation,
estimated at well over 100 times the D(17) proof.

## 6. The computer part

A sparse-start statement SS(n, d, a, 3) is decided by `thinsat.py`, which reuses the encoder of
`d18-search/netsat.py` (reviewed in earlier rounds) and adds cardinality caps. The normal form it
searches is justified as follows; each step keeps sorting and does not increase any layer size.

1. **First layer.** Exactly $a$ comparators, placed as `middle_layer(n, a)`: adjacent pairs with
   the idle channels split between the two ends (one in the middle if their number is odd), so the
   layer is invariant under duality (Fact A).
2. **Second layer, by cases.** The second layer is fixed to one representative per class of the
   group generated by permuting the first-layer pairs (min end to min end, max end to max end),
   permuting the idle channels, and duality $i\mapsto n-1-i$. Each generator is a symmetry of the
   problem: relabeling channels and untangling keeps all layer sizes and maps the first layer to
   itself; the dual of a sorting network sorts. A second-layer comparator equal to a first-layer
   pair never swaps and is excluded. `verify_cover.py` recounts the legal second layers by a
   recursion over vertex sets, regrows every orbit from the generators, and checks that the orbits
   are disjoint and add up to the recount (S11: 177 classes, 19,320 second layers; S12: 387 and
   93,016; S14: 682 and 1,008,414).
3. **Redundancy.** Deleting comparators that never swap leaves a non-redundant sorting network.
   For those, the end-game constraints $\phi_1$–$\phi_4$ of Codish, Cruz-Filipe and
   Schneider-Kamp (arXiv 1411.6408) hold, a first free layer comparator swaps on some prefix output,
   and netsat's redundancy tracking applies. Layer 3 is capped at $a$ by a cardinality constraint.
4. **CEGAR.** Inputs are added until the solver says UNSAT; UNSAT on a subset of the inputs implies
   UNSAT on all. Every network found is checked on all $2^n$ inputs.

Certificates: on UNSAT, `thinsat.py --dump` writes the final CNF; `drat_check.py` re-solves it with
the standalone CaDiCaL 2.1.2, writing a DRAT proof, and checks the proof with `drat-trim`. (The
`lrat-check` program shipped with drat-trim was rejected: it reports "VERIFIED" for an empty clause
whose only hint is a unit clause, which cannot derive it.) `crosscheck.py` re-decides sample cases
with the independent, plain encoder `depth-hand-proofs/verify/satnet.py` (every prefix image,
full value equivalences, no end-game constraints beyond an adjacent last layer, no CEGAR).

Positive controls: `descent.py` runs the descent on real sorters. A depth-9 13-sorter becomes a
depth-9 11-sorter with layer sizes 4,4,4,5,5,5,5,5,5, and a depth-10 17-sorter becomes a depth-10
14-sorter with sizes 5,5,5,6,6,6,6,6,6,7; both residuals are checked to sort by brute force
([results/controls](results/controls)). The same searches at one more layer find networks quickly
(e.g. SS(8, 7, 3, 3) and SS(10, 8, 4, 2) are false), and SS(10, 8, 3, 3) is false.

## 7. Results

| statement | gives | method | result |
|---|---|---|---|
| SS(6, 5, 2, 3) | D(7) ≥ 6 | one CNF, 29 inputs | UNSAT in 0.0 s; DRAT verified |
| SS(8, 6, 3, 3) | D(9) ≥ 7 | one CNF, 99 inputs | UNSAT in 0.3 s; DRAT verified |
| **S9** = SS(9, 7, 3, 3) | D(11) ≥ 8 | one CNF, 206 inputs | UNSAT in 258 s; DRAT proof 145 MB |
| SS(10, 7, 4, 2) | D(11) ≥ 8 (two-layer version) | one CNF | UNSAT in 101–137 s |
| **S11** = SS(11, 8, 4, 3) | **D(13) ≥ 9** | 177 second-layer cases | **all UNSAT** (median 317 s); all 177 DRAT-verified |
| **S11** = SS(11, 8, 4, 3) | **D(13) ≥ 9** | sentinel prover, SAT only as a guide (§8.8) | **proved**: 164 cases in about 3½ hours on up to 10 cores; 382,318 facts, all checked |
| S12 = SS(12, 8, 5, 3) | D(13) ≥ 9 (implied by S11) | 387 cases | 18 UNSAT, then stopped |
| **S14** = SS(14, 9, 5, 3) | **D(17) ≥ 10** | 682 cases | one probe case: no answer after an hour |
| SS(10, 8, 3, 3) | (would extend the D(13) descent) | one search | **false**: sizes 3,3,3,5,5,4,4,5 |

## 8. Fewer cases for S11, and a decision procedure built from sentinels

### 8.1 Where the 177 cases come from

Nothing but symmetry. The first layer of an S11 network is normalized to exactly four comparators
(1,2), (3,4), (6,7), (8,9) with channels 0, 5, 10 idle (adding comparators to layer 1 keeps a
sorter; Fact A places them). The second layer is any matching of at most four comparators, 19,320
in all, and two second layers are one case when a symmetry of the first layer maps one to the
other: permuting the four pairs, permuting the three idle channels, and the flip $i\mapsto10-i$.
That leaves 177 orbits, so the cases are exactly as fine as the symmetry of layer 1 allows.

### 8.2 Coarser splits that were tried

* **Subsumption** (Bundala–Závodný 2014). A prefix $P$ covers $Q$ when the output set of $P$
  embeds in that of $Q$ (or of its dual) after relabeling channels: a suffix for $Q$, relabeled and
  untangled, is a suffix for $P$ with the same layer sizes, so refuting $P$ refutes $Q$.
  `subsume.py` (with explicit permutations, re-checked) reduces the 177 cases to **87**, all with
  four comparators in layer 2. They carry 49,550 of the 84,510 SAT seconds
  ([results/subsume_11_4.json](results/subsume_11_4.json)).
* **Two more sentinels.** Two sentinels whose tracks absorb two different comparators in each of
  the first three layers leave a 9-channel sorter whose first three layers have at most two
  comparators: a violation of SS(9, 8, 2, 3). `exc_pairs.py` finds that this covers every third
  layer for 58 of the 177 cases, but 74,386 three-layer prefixes (44,622 up to symmetry) have no
  such pair. The residual statement is also the only one of its family that might hold: the
  9-channel profiles (2,2,3) and (2,3,2) and the 8-channel profile (1,1,1) are **false** (the
  solver finds sorters within seconds), and SS(9, 8, 2, 3) itself was still undecided when the
  monolithic SAT run hit its 40-minute limit.
* **Four sentinels on 13 channels at once.** Choosing all four sentinels of the D(13) descent
  together (`exc13.py`) still leaves 113 of the 495 second-layer classes with third layers that
  defeat every choice.

So S11 is tight: no single sentinel argument covers its cases uniformly, which is why the cases
stay at SAT level. The procedure below handles each case by recursion instead.

### 8.3 A decision procedure built from sentinels

`sentinel_prover.py` decides $\mathrm{EXT}(P,t,c)$: can the prefix $P$ on $n$ channels be followed
by $t$ layers, the $i$-th with at most $c_i$ comparators, so that the whole network sorts?
($D(n)\le d$ iff $\mathrm{EXT}(L_1, d-1)$ for the maximal first layer.) Its rules:

| rule | statement | justification |
|---|---|---|
| sorted | every output of $P$ is sorted ⇒ yes | — |
| zero | $t=0$ and an output is unsorted ⇒ no | — |
| sentinel | fix inputs $S$ to $\pm\infty$; the real inputs pass through a residual prefix $R$ on $n-\lvert S\rvert$ channels. $\mathrm{EXT}(P,t,c)\Rightarrow\mathrm{EXT}(R,t,c)$ | Fact B (a sorter's residual sorts; layers only thin) |
| quick | the real comparisons of $R$ reschedule into $h$ layers and $h+t<D(r)$ ⇒ no | rescheduling keeps the function |
| lemma | the real comparisons of $R$ schedule into $h$ layers whose first $m$ (continued by the capped suffix) have $\le a$ comparators, and $h+t\le d$, where SS($r,d,a,m$) was proved earlier in the same run ⇒ no | the residual would violate SS($r,d,a,m$) |
| split | $\mathrm{EXT}(P,t,c)$ iff $\mathrm{EXT}(P;L,t-1,c')$ for some next layer $L$ | definition |
| symmetry | $\mathrm{EXT}$ depends only on the output set of $P$ up to relabeling and complement | Bundala–Závodný |

It is **sound** (each rule is a theorem) and **complete** (the split rule alone is exhaustive
search); sentinels only make it fast. Nodes are output sets up to relabeling and complement,
memoized, so a lemma proved once (for example "a 6-channel prefix (3,4);(2,3) has no 4-layer
completion") is reused wherever it appears. A "no" answer is a proof DAG whose nodes are one-line
sentinel arguments or case splits; `check_sentinel_proof.py` re-checks an exported DAG from the
definitions (it simulates the sentinels with real $\pm\infty$ values, finds explicit permutations
for every identification, re-enumerates every split, and requires each $D(r)$ it uses to be a
node of the same file). An optional SAT oracle (`--oracle`) is used only to recognize branches
that *do* extend; its answers never enter a proof.

| statement | proof DAG (nodes: quick / sentinel / split) | time | before |
|---|---|---|---|
| D(3) … D(10) | 119 in all; D(9) ≥ 7: 70 (38 / 31 / **1**) | 3 s | D(9): Parberry's 1991 search; here one split into 67 cases, each closed by ≤ 4 sentinels ([text](results/sentinel_proof_D9.txt)) |
| SS(6, 5, 2, 3) | 32 (25 / 4 / 3) | 0.0 s | 854 hand certificates |
| SS(7, 7, 1, 3) | 52 (42 / 4 / 6) | 0.1 s | hand classification of 10,647 configurations |
| SS(8, 8, 1, 4) | 56 (42 / 6 / 8) | 0.3 s | 2,523 hand certificates |
| SS(8, 7, 2, 3) | 349 (279 / 50 / 20) | 2.3 s | 3,743 certificates + 81 SAT runs |
| SS(9, 8, 2, 4) | 385 (281 / 59 / 23, and 22 lemma steps) | 3 s | 2,754,931 hand certificates + 669 SAT runs |
| **H9** = SS(9, 7, 3, 2) | **129,701** (90,373 / 5,836 / 284, and 33,208 lemma steps) | 31 min | 33 of 50 classes by hand, 17 by SAT |
| **D(11) ≥ 8** | H9 + **180**: one split into 179 cases; 165 close by two sentinels and H9, 8 by $h+5<D(9)$, 6 by one sentinel and $h+5<D(10)$ | 9 min after H9 | descent + two SAT checks. Export ([results/sentinel_proof_D11_final.jsonl](results/sentinel_proof_D11_final.jsonl), 129,925 nodes) **passes the checker** |
| SS(9, 8, 2, 3) | 239,583 (161,925 / 10,177 / 505, and 66,976 lemma steps) | 60 min | undecided by SAT in 40 min. Export ([results/sentinel_proof_SS9823.jsonl](results/sentinel_proof_SS9823.jsonl), 239,627 nodes) **passes the checker** |

`lemma_chain.py` proves a list of statements in one memo, each proved sparse-start statement
becoming a lemma for the later ones. The exported proofs pass the checker: $D(3)$–$D(9)$
([results/sentinel_proof_D3-9.jsonl](results/sentinel_proof_D3-9.jsonl)), and $D(3)$–$D(10)$
with the six sparse-start statements of the table
([results/sentinel_proof_small.jsonl](results/sentinel_proof_small.jsonl), 482 nodes, 0 failures).

**A bug the checker caught.** A first run reported H9 proved (61,050 nodes in 16 minutes; 129,506
nodes in a second run with lemmas). Checking the exported 129,506-node proof failed: some split
nodes missed a child. The cause was the prover's node ids, built from the size of its class table,
which could coincide for two different classes, so one class could inherit another's answer.
Ids are now serial numbers. Proofs that passed the checker are unaffected, because the checker
re-derives every step without the prover's ids. The rerun proves H9 in 31 minutes; its export
([results/sentinel_proof_H9.jsonl](results/sentinel_proof_H9.jsonl), 129,745 nodes including
the D(r) and small lemmas) **passes the checker** (30 minutes, 0 failures).

Everything here is pure Python; the per-node cost at 11 channels is a few hundred sentinel
residuals and equivalence tests.

### 8.4 Smaller proofs: a fact store and covers

`sprove.py` reorganizes the procedure so that no fact is derived twice and one fact can stand for
many cases; `check_facts.py` checks its output from the definitions.

* **Fact store** (`facts/`). Every decided node is written, the moment it is decided, to an
  append-only file `facts/facts-<run>.jsonl`; proved statements go to `facts/statements.jsonl`.
  Every run loads the whole store first. Facts are grouped by output set up to relabelling and
  complement, and a query is answered by a stored NO fact with at least as many remaining layers
  and caps at least as loose (no completion with more room means none with less), or a stored YES
  hint in the other direction. So work is shared within a run and across runs: D(3)–D(10) and the
  small lemmas are never re-proved, and the checker caches verified facts (`facts/verified.txt`)
  and only checks new ones.
* **Cover facts** (step `absorb`). If the sentinels S sit on channels pos(S) after the prefix P,
  any next layer with at least a comparators touching pos(S) loses them to the sentinels. So one
  fact, "the residual of P under S, with the next cap lowered by a, has no completion", covers all
  those layers at once; only the layers no cover fact covers are enumerated. With one sentinel this
  is the track lemma of §3, and the prover finds the descent on its own: $D(11)\ge8$ becomes
  absorb (11 → 10 channels), absorb (10 → 9), then H9.
* **Listed sentinel covers.** A split step may list sentinel sets once; a next layer that one of
  them closes (through a quick or lemma step, or by reducing it to a listed stored fact) needs no
  fact of its own. Siblings share sentinel sets heavily: in the H9 proof, 16,630 leaf closures
  used 4,399 sets.
* **Subsumption** (step `sub`, Bundala–Závodný). Before a node is expanded, a stored NO fact whose
  output set embeds in the node's (after relabelling, possibly complemented) closes it.

Proof sizes (facts plus listed covers; each is one line, each checked):

| statement | §8.3 prover | + store, absorb | + reuse, subsumption | + listed covers |
|---|---|---|---|---|
| D(9) ≥ 7 | 70 | 175 | 174 | 89 |
| SS(8, 7, 2, 3) | 348 | 211 | 194 | 111 |
| SS(9, 8, 2, 4) | 385 | 198 | 186 | 101 |
| **H9** | 129,701 | 22,188 | 17,630 | **3,172** |
| **D(11) ≥ 8** on top of H9 | 180 | 4 | 4 | **5** |
| **SS(9, 8, 2, 3)** | 239,583 | 32,313 | 25,667 | **5,248** |

With all rules, H9 takes 6 minutes, D(11) 5 and SS(9, 8, 2, 3) 6.5 (single core, Python). The
17 statements together depend on 1,178 stored facts, and the checker verifies them in a minute
with no failures. For D(9) the store-and-absorb proof is larger than the flat one (one lemma
about 8-channel networks, reused eight times, costs more than the 67 direct cases), so the
covers help on the hard statements, not the easy ones.

**Speed at 11 channels.** The first S11 attempt with these rules stalled: profiling showed 92% of
the time in the search for listed sentinel covers, which recomputed a full residual for every
(sentinel set, next layer) pair, millions per case split. Now each sentinel set's state after the
prefix is computed once per node, and a next layer is judged from it with one bitmask test (the
quick rule: no comparator of the layer may join two real lines one of which is already at the top
allowed level) or a few lookups (the lemma rule). Two smaller fixes: the loaded store is frozen
out of Python's garbage collector, and the optional SAT pruning uses conflict budgets instead of
timer threads (thousands of timer threads were contending with the main thread). Together these
took one S11 case from 7 nodes in four minutes to about 5,000; H9 now takes 2.4 minutes and its
proof is 5,867 items (the cheaper cover search finds fewer shared reductions than the exhaustive
one, which reached 3,172 items in 6 minutes).

### 8.5 Why S11 does not finish: irreducible nodes

The restarted run (8 workers, 14:10 to 21:20 on 2026-11-19, about 2.8 million new facts, 1.2 GB)
closed no new case and was stopped. Every worker spent the whole time in one or two 10-channel
nodes, residuals of an S11 case after one sentinel, with t = 5 layers left. Worker 1's first such
node, P1, is

    ((0,1),(3,4),(5,6)), ((0,2),(1,3),(8,9)), ((2,3),(4,7),(5,8),(6,9))   on 10 channels, t = 5.

The prover needed about 4 hours and 206,000 facts to prove P1. Its second node, P2 (third layer
(0,1),(2,7),(5,8),(6,9)), was unfinished after another 167,000. Across the two, 831 nodes after
layer 4 needed one more split, with about 440 children each. SAT refutes P1 in 1.6 seconds.

`irreducible.py` asks whether such a node reduces to fewer channels (all checks by SAT, results in
`results/irreducible_s11_stuck.txt`):

* **P1 has no residual reduction.** All 1,160 sets of 1 to 3 input sentinels leave a 7- to
  9-channel residual that has a 5-layer completion. With 4 or more sentinels at most 6 channels
  remain and D(6) = 5, so a completion always exists. A deletion-minimal subset of P1's outputs
  that 5 layers cannot sort still has 55 of its 97 unsorted vectors. Keeping the sentinel in the
  network instead of removing its path does reduce P1 (§8.6).
* **P2 reduces once, then stops.** Six single sentinels (for example channel 3 at −∞) leave a
  9-channel node with no completion. That node, R2, has no reduction of any kind tried here
  (§8.6). The prover missed the first reduction: it tries residuals with the most sentinels
  first, at most 40 of them, so a one-sentinel residual can go untried.

The same checks on all 19 distinct 3-layer prefixes on 10 channels under which a worker stored at
least 40,000 facts (the stored nodes are these prefixes, with t = 5, or 4-layer nodes that start
with them, with t = 4):

* 5 prefixes have a 5-layer completion (SAT finds one in 0.2 seconds). The work under them went
  into 4-layer nodes below them.
* 12 have none and reduce by one sentinel to 9 channels. P2 is one of them; the prover was
  splitting P2, so it missed that reduction. For the other 11 the stored facts do not show whether
  the prover reached the prefix itself or only 4-layer nodes below it.
* 2 have none and no residual reduction: P1 and I7, whose layers are (0,1),(3,4),(5,6), then
  (1,3),(4,7),(8,9), then (0,1),(2,4),(5,8),(6,9). They are the same node: complementing every
  bit and permuting the channels maps P1's outputs onto I7's (§8.6).

P1 and P2 share their first two layers and differ only in the third, so the first two layers do
not decide irreducibility. (A first version of `irreducible.py` did not check that the node itself
has no completion and called the 5 extendable prefixes irreducible too. It also deleted a fixed
channel before asking whether 5 layers sort the rest, a question that says nothing about the
node; the current version keeps the channel.)

**Comparison with the five-wire lemma** (report Appendix A, used for D(7) ≥ 6). That lemma's last
step has no residual reduction either: merging a sorted triple and a sorted pair in two layers is
impossible, while every one-sentinel residual (a 2+2 or 3+1 merge) can be done in two layers. Its proof forces
the third layer with sentinels and then counts dependencies: the median depends on all five
inputs, but after two layers an output depends on at most four. Our nodes share the first
feature but not the finish. Output k depends on channel i if two outputs of the prefix that
differ only in channel i sort differently at position k. In all 19 prefixes, whatever their verdict, the
middle outputs already depend on all 10 channels, and with t = 5 layers left an output may depend
on up to 32. The count only bites with 3 layers left (at most 8). There it closes about 45% of
P1's depth-5 leaves, as a one-line certificate in place of a sentinel line, but it does not
shorten the split. The 55-vector cores sit in the middle weights (4 to 7 ones), as a
median-type obstruction would. With 5 layers left, though, no single count captures it.

So with residual sentinels alone, a node like P1 can only be closed after more layers are fixed.
§8.6 looks at what P1 and R2 are made of and finds a second kind of sentinel restriction that
catches P1 but not R2. §8.7 shows that this restriction cannot shorten a proof. What does shorten
it is the choice of residuals below the split: guided by SAT, the prover proves P1 with 4,016
facts instead of about 206,000. A proof of that size is still far from a hand proof, which matches
the assessment in depth-hand-proofs/h9.md §9 that D(13) ≥ 9 stays out of reach by hand.

### 8.6 What the irreducible nodes are made of

Three nodes above have no residual reduction: P1, I7, and R2, the 9-channel residual of P2 after
channel 3 at −∞ (layers (0,1),(4,5); (0,2),(7,8); (2,6),(4,7),(5,8); t = 5). `structure.py` takes
them apart; its output is in `results/structure_irreducible.txt`. `irreducible.py` now also runs
the tracked checks described below (`results/irreducible_s11_stuck.txt`). Everything here is
decided by SAT.

**Blocks.** No comparator in these prefixes joins two groups of channels, so each node splits into
independent blocks. Call x_i ≤ x_j a relation of the node if it holds on every output. Each node's
outputs are exactly the 0/1 vectors that respect all its relations, and every relation stays
inside one block:

* P1 = A × B (18 × 6 = 108 outputs). A, on channels {0,1,2,3,4,7}, has the relations 0<2<3,
  1<3, 1<7 and 4<7, a zigzag 0–2–3–1–7–4. B, on {5,6,8,9}, is a diamond: 5 is the minimum, 9 the
  maximum, and 6 and 8 are unordered.
* I7 is P1 laid out differently. Complementing every bit and permuting the channels maps P1's
  outputs onto I7's, so I7 has a 5-layer completion exactly when P1 has one. The prover's memo
  already uses this equivalence.
* R2 = C × D × E (8 × 6 × 2 = 96 outputs). C, on {0,1,2,6}, is the zigzag 1 > 0 < 6 > 2. D, on
  {4,5,7,8}, is again a diamond. E is the free channel 3.

**Three jobs.** The 5 remaining layers must finish each block and merge the blocks. The table
gives the fewest layers for each combination of jobs:

| jobs | P1 | R2 |
|---|---|---|
| merge only (blocks given sorted) | 4 | 5 |
| merge, and finish the diamond | 4 | 5 |
| merge, and finish the other block | 5 | 5 |
| all three | 6 | 6 |

Merging alone, or merging and finishing one block, fits into 5 layers. Merging and finishing both
blocks needs 6.

**Residual sentinels fail.** Every single sentinel leaves a residual that 5 layers complete. On
P1, a sentinel in the diamond turns it into a 3-element block, and a sentinel in A shrinks A; in
both cases the rest fits into 5 layers.

**Tracked sentinels.** A residual removes the sentinel's whole path, including the part through
the missing suffix, so it forgets that the sentinel still has to reach its final channel. One can
instead restrict the inputs and keep all channels. This tracked sentinel is an exact restriction
of the node. On P1 it works for six sentinels:
* +∞ on input 0 or 1 ends the prefix on channel 3 and still has to climb six channels;
* −∞ on input 5, 6, 8 or 9 ends on channel 5 and still has to descend five.

No 5-layer suffix sorts either set of 90 outputs, although the residuals of the same sentinels
have completions. In terms of P1's outputs, the two sets are the outputs with x_3 = 1 and those
with x_5 = 0.

**The layout decides.** In I7 the corresponding sentinels already sit on their final channels, and
no tracked sentinel or single fixed value lacks a sorter. Moving P1's blocks over the channels
(each block keeps its internal order) gives 210 equivalent layouts. In 35 of them one fixed value
already lacks a sorter:
* the diamond's minimum, when it must travel 3 to 6 channels;
* A's top element, when it must travel 6.

R2 has no such layout among its 630.

**Weights.** For all three nodes, every single weight class (the outputs with w ones, a selection
problem) can be sorted in 5 layers. No 5-layer suffix sorts weights 3 to 6 together, nor (for P1
and I7) weights 4 to 7. At least four consecutive weights take part. This is not a median
obstruction like the five-wire lemma's, where weight 3 alone already fails.

**Least structure.** Adding relations shrinks the output set. Twelve greedy random runs found
three maximal additions that keep P1 without a 5-layer sorter:
* channel 3 above everything (that is, x_3 = 1);
* channel 5 below everything (x_5 = 0);
* 5<2 together with 7<3.

An exhaustive search inside the blocks finds only 7<3. The diamond admits nothing: ordering 6 and
8 either way gives a 5-layer sorter. For R2 all twelve runs found the same single addition, 2<1,
which is also the only one inside C; it turns C into two elements below two.

**The five-wire lemma again.** Its last step (merge a sorted triple and a sorted pair in two
layers) behaves like P1. It has no residual reduction. With the triple on channels 0–2 and the
pair on 3–4, tracked sentinels reduce it: the triple's +∞ must travel two channels and the pair's
−∞ three. In 8 of its 10 layouts nothing does. Its proof counts dependencies instead, which works
in every layout. For P1 and R2 no such count is known, because with 5 layers left an output may
depend on up to 32 inputs.

**What this means for the prover.**
* A tracked sentinel gives a true statement but never a shorter proof (§8.7). Every sound step
  for a tracked node is open to the plain node as well.
* The layout does not change a split either. Equivalent prefixes have equivalent children, so P1
  and I7 split into the same classes.
* R2 resists every single restriction tried here, in every layout, so it needs a split. What made
  S11 too large, though, was the prover's choice of residuals below these splits (§8.7).

### 8.7 A split on the sentinel's path, and what does shrink P1's proof

The next idea after §8.6 was to split P1 on the path of its tracked sentinel (−∞ on input 5,
which still has to descend five channels), hoping for a proof much smaller than the 206,000 facts
the prover used. That cannot work, for two reasons. The measurement that showed it also found what
does shrink the proof.

**Tracking never gives a shorter proof.** A tracked node (P with the inputs restricted to
x_c = ±∞, all channels kept) can be closed soundly in three ways:
* drop the tracked sentinel, which gives an ordinary residual of the plain node P;
* restrict further;
* split, whose children are restrictions of the plain node's children.

Each of these is open to the plain node too. By induction on the remaining layers, the smallest
proof of the tracked node is never smaller than the smallest proof of P. A split on the
sentinel's path is the same split regrouped by where the sentinel goes, so the same holds for it.

**Keeping a tracked sentinel while removing another is not sound in general.** The residual
argument untangles a generalized network into a standard one (Knuth 5.3.4-16). That step needs a
network that sorts every input, and a restricted node sorts only some. Three wires already show
it. The generalized network [2:0], [0:1], [1:2] (each comparator puts the minimum on its first
wire) sorts every input with −∞ on wire 1. Its untangled form (0,2), (1,2), (0,2) sends
(3, −∞, 1) to (1, −∞, 3).

**Measured.** `split_profile.py` splits a node on its next layer the way `sprove.py` does. For each
child class it asks SAT whether some single-sentinel residual has no completion. One sentinel is
enough to test: if a residual of several sentinels has no completion, neither has the residual
of any one of them.

| | P1 (10 channels, t = 5) | R2 (9 channels, t = 5) |
|---|---|---|
| child classes of the split | 2,157 | 385 |
| closed by the height bound | 17 | 0 |
| closed by a residual without completion | 2,140 | 383 |
| open (needs its own split) | 0 | 2 |

With the inputs restricted to x5 = −∞, P1's split closes 2,153 classes, four fewer, as the
argument predicts.

So no child of P1's split needs a split of its own. In the stopped run the prover split 478 of
them again, with about 440 children each. Its candidate residuals (at most 40, ordered by height
and then by number of sentinels) did not include one without a completion.

**SAT-guided residual choice.** With `--guide`, `sprove.py` goes through its candidate residuals in
its usual order and asks SAT which one has no completion. It recurses into the first such
residual and skips the ones that SAT completes. SAT only orders the search. Every step is still one
of the prover's rules, and `check_facts.py FACT:<id>` checks the result from definitions.
`sprove.py --node N T 'PREFIX'` proves a single node. The guided runs below, and the unguided run in
the middle column, start from the store as it was before the S11 run: 4,818 facts, with the
statements D(3) to D(11) and eight sparse-start statements, among them SS(9,8,2,3).

| | stopped run (unguided) | unguided, same store | guided |
|---|---|---|---|
| P1: time | about 4 hours | unfinished, stopped after 1 hour | 187 s |
| P1: new facts | about 206,000 | 109,688 by then (143 splits) | 6,577 (36 splits, 10,561 SAT calls) |
| P1: facts the proof needs | | | 4,016, checked, 0 failures |
| P2: time | unfinished after 167,000 facts | not run | 25 s |
| P2: new facts | | | 980 (16 splits) |
| P2: facts the proof needs | | | 1,327, checked, 0 failures |

For P1 and P2, then, the residual choice made the proofs large, not the structure of the nodes.
§8.8 proves all of S11 this way.

Both proofs are kept in `facts_guided/` (4.8 MB: the base store plus the two runs). To re-run and to
check them:

    venv-python sprove.py STORE --oracle --guide --node 10 5 '[[[0,1],[3,4],[5,6]],[[0,2],[1,3],[8,9]],[[2,3],[4,7],[5,8],[6,9]]]'
    venv-python check_facts.py facts_guided FACT:20261120-081349-68902-12974 FACT:20261120-081546-69023-1908

The check needs 4,548 facts for the two and finds no failure.

### 8.8 S11 by the sentinel prover

With the changes below, the prover proves S11 = SS(11, 8, 4, 3), and with it D(13) ≥ 9, in about
3½ hours on up to 10 cores. SAT only steers the search. The proof consists of sentinel residuals,
splits, subsumptions and uses of proved lemmas, and `check_facts.py` checks every one of its
382,318 facts from definitions, with no failure. With all 18 statements recorded in the store
(D(3) to D(11), the sparse-start lemmas and S11), 382,322 facts are checked, again with no failure.

**Setup.** `s11_cases.py` proves the 164 second-layer cases: the classes of the S11 root's split,
grouped up to relabelling and complement the way the prover groups them. The 177 DRAT cases of §6
use a different grouping. The run starts from the store as it was before S11 (4,818 facts).
`sprove.py facts_s11g SS:11,8,4,3 --assemble` then proves the statement from the stored cases: one
split, 164 store hits, 18 seconds.

**Changes made during the run**, all in `sprove.py` and `s11_cases.py`:
* **Sharing** (`--share`). Every worker reads the other workers' new facts once a minute and takes
  the next unclaimed case. Loaded facts are kept compact, and at most 40,000 output sets stay
  cached. Without sharing, 91–99% of each worker's early facts (for seven of the eight workers)
  repeated another worker's, and memory grew by about 5 GB an hour.
* **A faster guide.** A residual of several sentinels can only lack a completion if every
  one-sentinel residual inside it does. So the guide decides the one-sentinel residuals first and
  stops if all of them complete. Before each SAT call it looks in the shared store, and it records
  SAT's completions as YES facts. Those are hints for the search and never part of a proof. On one
  case the new guide covered 28,017 nodes in 20 minutes against 15,943 for the first one.
* **Cheaper cover selection.** The counting of comparators that touch given positions uses bit
  masks now. Profiling had shown it taking about a quarter of the time.
* **Helpers** (`--help I,J`). For the last hard cases, extra workers prove a case already claimed
  by another, but they go through every split from the largest child down. With sharing, the two
  meet in the middle.

| | time | workers | cases closed |
|---|---|---|---|
| no sharing, first guide | 08:23–09:00 | 8 | 3 |
| sharing, first guide | 09:02–10:45 | 8 | 39 more |
| sharing, faster guide, helpers at the end | 10:52–11:52 | 8, then up to 10 | the remaining 122 |

The stopped run of §8.5 (unguided, no sharing) had used 8 workers for 7 hours without closing a
case. The last six cases (6, 37, 38, 39, 40, 42) took 37 to 61 minutes each in the final segment,
on top of the work stored for them before.

**The proof.** It needs 382,318 of the 963,460 stored facts. 1,595 of them come from the base
store: D(3) to D(11) and the sparse-start lemmas. The stored facts include 60,869 YES hints and
the work repeated before sharing was on.

| rule | facts |
|---|---|
| sentinel residual that is a stored fact (`sent`) | 277,650 |
| use of a proved sparse-start lemma (`lemma`) | 90,943 |
| height bound (`quick`) | 4,617 |
| split or absorb (7,217 in all, listing 564,376 children and 100,559 sentinel covers) | 3,383 + 3,834 |
| subsumption (`sub`) | 1,891 |

Most of its nodes have 10 channels (219,076), 9 (95,300) or 8 (58,113); only 6,321 have all 11.

**What it is.** This is a second proof of S11, independent of SAT: every step is a sentinel
argument, a split or a subsumption, each re-checked from definitions. With 382,318 steps it is a
computer proof, not a hand proof. D(13) ≥ 9 by hand stays out of reach (depth-hand-proofs/h9.md
§9), but the computer proof no longer rests on trusting a SAT solver and a DRAT checker.

**Checking faster.** The first checks took hours on the 264 splits of 10-channel nodes with five
layers left. Each of those splits lists about 102 folded sentinel covers, and the checker tried all
of them on every next layer, each time simulating all 2^r inputs, before it looked at the listed
children. `check_facts.py` now runs on several cores (`--jobs N`), records each verified fact as it
goes (a stopped check resumes), caps its cache of output sets, and tests a next layer against the
listed children first. The simulation skips the output set where only the height and schedules are
read. The tests themselves are unchanged. On P1 and P2 the new checker accepts exactly what the old
one accepts. It rejects a corrupted sentinel step, a split without its children and a split without
its sentinel covers, just as the old one does. The last, resumed check of S11 took 33 minutes on
6 cores.

The store is kept in `facts_s11g/` (386 MB). To re-run and to check:

    venv-python s11_cases.py facts_s11g 8 K --oracle --guide --share     # for K = 0..7
    venv-python sprove.py facts_s11g SS:11,8,4,3 --assemble
    venv-python check_facts.py facts_s11g SS:11,8,4,3 --jobs 6

### 8.9 The routes to S11 compared

Four ways of proving S11 were tried. Two give complete proofs, and two stopped short.

| | SAT per case + DRAT (§6, §7) | coarser sentinel arguments (§8.2) | sentinel prover, unguided (§8.5) | sentinel prover, guided + shared (§8.8) |
|---|---|---|---|---|
| status | complete: 177 cases, all UNSAT | partial | stalled: 1 of 164 cases | complete: 164 cases |
| finding the proof | 23.5 CPU-h (median 5.3 min per case) | minutes | about 80 CPU-h (two runs, 8 workers) | about 27 CPU-h (estimated, restarts included) |
| certifying it | 19.3 h re-solving + 23.7 h `drat-trim` | none | none | last check run 33 min on 6 cores, 0 failures |
| proof object | 27.5 GB of DRAT (median 146 MB per case) | none | 2.8 million facts, no proof | 382,318 facts, 168 MB |
| trusted | the CNF encoding (symmetry normal form, end-game constraints, CEGAR) and `drat-trim`; 3 cases re-solved with an independent plain encoder | | | the rules (sentinel residuals, subsumption, splits, uses of proved lemmas) and the Python checker; no solver, no encoding |

* **Two independent proofs.** The SAT proof rests on an encoding and a solver whose UNSAT answers
  DRAT certifies. The sentinel proof uses neither and rests on a few combinatorial rules and a
  small checker. An error would have to get past both.
* **Size.** The sentinel proof is about 160 times smaller than the DRAT proofs and costs about the
  same compute, or less once DRAT certification is counted. Each of its facts is a statement a
  person can check by hand; a DRAT line means nothing to a reader.
* **No hand proof.** Subsumption leaves 87 cases. Pairs of extra sentinels reducing to SS(9,8,2,3)
  cover 58 of the 177 cases, and four sentinels on 13 channels still leave 113 of 495 classes.
  Nodes like R2 resist every single sentinel restriction (§8.6), and tracking a sentinel cannot
  shorten a proof (§8.7). S11 is tight.
* **Search control, not mathematics.** Both sentinel runs use the same rules. The guided run
  differs in two ways: SAT picks a residual that has no completion instead of the prover trying up
  to 40 blind, and the workers share facts (before, 91–99% of each worker's early facts repeated
  another's). On P1 alone that is 4,016 facts against about 206,000.

For S14 (and so D(17) ≥ 10), the SAT route had no answer for its one probe case after an hour.
Whether the guided sentinel prover scales to 14 channels is untested.

### 8.10 Smaller S11 proofs: compaction, and family lemmas tested

`proof_shape.py facts_s11g SS:11,8,4,3 --families` measures where the S11 proof spends its facts
and how much smaller it could be (output in `results/proof_shape_s11.txt`). Nothing is rewritten;
the numbers are what the existing rules would allow.

**Where the facts go.** Of the 382,318 facts, the largest groups are:
* 10 channels with 4 layers left: 123,702 sentinel steps and 75,014 lemma steps;
* 9 channels with 4 left: 58,234 sentinel steps;
* 8 channels with 3 left: 47,286 sentinel steps.

Lemma uses: H9 = SS(9,7,3,2) 58,664 times, SS(9,8,2,3) 20,357, SS(8,7,2,3) 10,990. Most of the
10-channel facts are children of splits of P1-like nodes (10 channels, 5 layers left), with about
1,100 children each.

**Compaction with the existing rules.**

| | facts | splits |
|---|---|---|
| as stored | 382,318 | 7,217 |
| merge splits whose output sets are equivalent | 306,869 | 4,757 |
| also replace a split by subsumption from another needed split (same channels, layers and caps) | 270,732 | 2,610 |
| also fold children closed by a leaf rule (height bound or lemma, directly or after one sentinel step) into the parent's list of sentinel covers | 168,593 | 2,601 |

Most of the duplicate splits come from workers that proved the same node before sharing was on.

**Family lemmas, tested.** The idea was to prove a lemma once for each recurring block-product
family (like P1's zigzag × diamond) and reuse it. Reuse would go through subsumption: a split
follows from any node that has no completion with at least as many layers left and whose output
set fits inside the split's after relabeling channels.
* **Families barely recur.** The 791 distinct splits with at least 5 layers left fall into 553
  families by block structure (block sizes, pattern counts, degrees in the order); the largest
  has 23 members. Only 361 are products of two or more blocks. Most are a single 9- or 10-channel
  block whose order has two levels (every element is minimal or maximal).
* **Reuse is rare where it matters.** For each such split, `proof_shape.py` searched every stored
  fact with no completion (any rule; same channels; at least as many layers left; caps no tighter;
  not equivalent) for one that fits inside it. It found one for 228 of the 791, 74 of them facts
  closed without a split. By group:
  * 9 channels, 5 layers left: 193 of 398;
  * 10 channels, 5 left (the P1 type): 14 of 217;
  * 11 channels, 6 left: 0 of 50.
* **Effect.** On top of the compaction above, 168,593 → 168,538 facts. Subsumption between the
  needed splits already catches nearly all of these.
* **Why.** A core must still have no completion, and for these nodes that takes most of the node.
  P1's smallest subsets without a sorter keep 55 of its 97 unsorted outputs, and its maximal
  strengthenings keep 90 of 108 outputs (§8.6). Two different nodes rarely share that much.

So with the existing rules the S11 proof can shrink to about 169,000 facts and 2,600 splits. The
10-channel splits with 5 layers left are distinct hard cases, not variants of a few, and a family
lemma does not reach them. For the prover, one change follows. Its subsumption step looks only
at stored split facts, at most 60 of them. Looking at all stored facts would find the 9-channel
reuse during the search instead of afterwards.

**The wider subsumption step, measured.** With `--wide-sub` (in `sprove.py` and `s11_cases.py`) the
step looks at every stored fact without a completion, of any rule, with at least as many layers
left and caps no tighter. New facts carry the weight counts of their output set (`wc`), so most
candidates are ruled out before any embedding is tried. On the S11 store this search finds a
subsuming fact for 39 of 40 splits that the family test had covered, mostly within 0.1 s. The
benchmark below runs S11 cases 16–31 twice at the same time from the base store, with 4 shared,
guided workers each (`results/wide_sub_benchmark.txt`):

| | without `--wide-sub` | with `--wide-sub` |
|---|---|---|
| wall time | 149 min | 147 min |
| hardest case (20) | 6,598 s | 6,493 s |
| facts the 16 case proofs need | 153,868 | 150,692 (−2%) |
| splits in them | 3,104 | 2,832 (−9%) |
| subsumption steps | 999 | 1,290 |
| check | 0 failures | 0 failures |

The wider step replaces about one split in eleven by a subsumption. It costs no time, but most
splits it replaces are small, and a subsumption pulls in the covering fact's own proof, so the
proof shrinks by only 2%. It is a small gain, not a change of scale.

### 8.11 Toward S14: a compiled core and symmetry-reduced splits

S14 = SS(14, 9, 5, 3) gives $D(17)\ge 10$ through the descent (§5.2). Its 682 case roots are much
bigger than S11's, so the S11 prover does not carry over:

| | S11 | S14 |
|---|---|---|
| next layers in a case root's split | 13,289–19,319 | 672,163–1,008,413 |
| outputs of a case root | 270–648 | 1,296–3,888 |
| next layers after the third layer | | 660,991 (one sample node) |

A first probe with the pure-Python prover wrote 222 facts in 36 minutes with 8 workers. A
240-second profile of case 0 expanded 2 nodes. The listed sentinel covers took 130 s (29.7 million
calls of one test) and 9 SAT calls 52 s.

**What was built.** (The S14 measurement scripts are in `s14/`.)
* `fastcore.c` holds the hot loops. `fastcore.py` loads it through ctypes and builds it with clang
  on first use; `SP_PURE=1` keeps everything in Python. Output sets are bitmaps. It computes:
  * output sets, layer images, channel signatures and non-redundant pairs;
  * equivalence under relabeling and complement, and automorphisms. Hash sums of key multisets
    prune the search, and each leaf is checked exactly;
  * the canonical next layers (below), and hashes and invariants of their children;
  * the greedy choice of listed sentinel covers (`_qcover`), making the same choices as the Python
    loop.
* `test_fastcore.py` compares every routine with its Python version on random nodes and on S11
  and S14 case roots; all agree.
* `sentinel_prover.py` and `sprove.py` use it for output sets, equivalence, splits of nodes with at
  least `fast_n` = 10 channels, and the sentinel covers. Options `qcover_max_n`, `oracle_max_n`,
  `guide_big_n` and `guide_big_seconds` limit costly steps on big nodes; `ss_cases.py --opt k=v,...`
  sets them.
* `check_facts.py` does not use the core.

**The symmetry rule.** An automorphism of a node's output set X is a relabeling g, a channel
permutation σ applied after complementing every bit when g is flagged, with g(X) = X. For a next
layer L, let g(L) be the layer with comparators (min, max) of (σ(i), σ(j)) for each (i, j) in L.
The child of g(L) is a relabeling of the child of L (of its complement when g is flagged). Both
are output sets of standard prefixes, so they have the same answer (the symmetry row of §8.3).

A split step may list automorphisms (`aut`): up to 500 found by the C search, not necessarily a
group. The prover then expands only the layers that no listed g maps to a lexicographically
smaller layer. The checker verifies three things for each listed g:
* σ is a permutation;
* g(X) = X;
* g maps the non-redundant pairs onto themselves. This holds whenever X contains the sorted
  vectors, as every prefix output set does.

It then skips the same layers. This is sound. Images of enumerated layers are enumerated layers.
Each orbit under the group the listed g's generate has a least layer, and no listed g maps that
layer lower, so it is checked. Every skipped layer's child is equivalent to that layer's child.

The list on P1's root (one automorphism, exchanging channels 6 and 8) was corrupted in copies of
the store:

| list in the step | check |
|---|---|
| as found | passes |
| not a permutation | fails |
| a permutation that is not an automorphism | fails |
| the right permutation, complement flag set | fails |
| the right one plus a false one | fails |
| removed | passes (every layer checked, children matched up to equivalence) |

**Effect on the proofs.**
* **10 channels: no change.** P2 and P1 (§8.7) prove with the same node counts as before (1,214 and
  4,480). Only P1's root has an automorphism. The times are 36 s and 241 s with 8 other jobs
  running; SAT guide calls bound these nodes. The checker verifies P1's 3,356 facts, 0 failures.
* **S11 roots.** Case 0: 13,289 next layers and 8 automorphisms leave 2,504 canonical layers. The
  largest root (288 automorphisms): 19,319 leave 176.
* **S14 case 0, 300-second profile** (12-channel limits on covers, oracle and guide): the prover
  expanded 388 nodes, against 2–3 before. SAT is now 63% of the time (470 calls, 0.4 s each), SAT
  encoding 13%, choosing cover facts 10%, and the compiled sentinel covers 5%.

**S14, measured with the core.** All runs use the S14 store (`facts_s14/`: the S11 proof's facts
and statements). Above 12 channels the extension oracle is off and guide SAT calls get 2 s.
* **Case roots.** The C core lists a root's canonical next layers in about a second:

  | case | outputs | next layers | automorphisms | canonical |
  |---|---|---|---|---|
  | 0 | 1,296 | 672,163 | 64 (all) | 17,881 |
  | 340 | 1,800 | 809,961 | 32 (all) | 41,896 |
  | 681 | 3,888 | 1,008,413 | 500 (search cut off) | 3,032 |

* **Sentinel covers after the third layer.** On two sampled 14-channel nodes with six layers left,
  the compiled covers close 490,522 of 493,375 next layers (38 sentinel sets, 2.5 s) and all
  927,453 (10 sets, 4.2 s). At a case root, with seven layers left, they close few: 0 of 17,881 for
  case 0, 1,500 of 41,896 for case 340.
* **Cover facts are too costly at the root.** With them, neither case 0 nor case 340 had listed
  its root split after 30 minutes. They had proved 54,000 facts on 9–11 channels for candidate
  covers. `absorb_max_n=12` turns cover facts off above 12 channels.
* **Children of the roots.** The children of a case root are its nodes after the third layer. A
  sample of 60 random canonical children per case, 30 s each:

  | case | closed at once | still open after 30 s |
  |---|---|---|
  | 0 | 22 (each by one sentinel step onto a fact proved earlier that day, §8.12) | 38 |
  | 340 | 49 (46 by one sentinel step, 3 quick) | 11 |

* **Checks.** The four largest splits from these runs that list automorphisms (up to 23, on 11
  channels) and compiled covers check from definitions: 27,195 facts needed, 0 failures.
* **The open children, 15 minutes each.** Four of case 0's and two of case 340's, run after the
  sample, when the store held about 19,000 more facts:

  | child | result |
  |---|---|
  | case 0, sample 0 | closed at once now (a fact proved meanwhile matched) |
  | case 0, sample 1 | closed in 173 s (160 new facts) |
  | case 0, sample 2 | closed at once now |
  | case 0, sample 3 | open after 900 s (24,140 new facts) |
  | case 340, sample 14 | closed in 313 s (4 new facts, 30 guide SAT calls) |
  | case 340, sample 15 | closed in 374 s (2,767 new facts) |

  The 80 facts on 13 or 14 channels from these runs check, 0 failures.
* **SAT on the same cases.** `thinsat.py 14 9 5 --capped 3` ran on eight cases (0, 1, 2, 100,
  250, 400, 550, 681), 3 hours each. None finished. Case 0's first round took 1,913 s and found a
  counterexample network (64 failing inputs); its second round had no answer after 2.5 hours.
  Case 1's first round took 7,052 s. The other six had no first-round answer.

**What this means for S14.** The core removed the cost of the splits. A root's canonical layers
take a second, and the compiled covers close nearly every next layer of a node after the third
layer. What is left is the hard children. A case root has 3,000–42,000 canonical children. In the
samples, 18–63% of them do not close at once, and those take minutes each: about 5 minutes on
average over the six above, at least, since one did not finish. Treating the children as
independent puts case 0 at roughly 900 CPU-hours and case 340 at roughly 600. That estimate
ignores sharing, and §8.12 shows that sharing dominates: the children reduce to a small pool of
residual nodes on 10 and 11 channels, and one whole case (681) is proved in minutes.

### 8.12 What makes S14's root children hard

The samples in §8.11 treated the children of a case root as independent. They are not: almost
every child closes through a small, shared pool of residual nodes.

**The children reduce to sparse 10- and 11-channel residuals.** A root child is a 14-channel node
after three layers, with six layers left. The children that closed at once in §8.11 did not reuse
S11 facts. Each fixed 3 or 4 sentinels and reduced to an 11- or 10-channel node with six layers
left, proved earlier the same day by the root runs while they built candidate covers. 16 such
facts closed all 77 of these children, one of them 24. `s14/s14_classes.py` measures this on
1,500 random canonical children of each of cases 0, 340 and 681, using the prover's own candidate
order and its first 300 sentinel sets per child (output in `s14/s14_classes.json`):

| children (4,500) | |
|---|---|
| closed by a quick step at the child | 1,158 |
| a candidate residual is a stored fact without completion | 2,290 (through 18 classes) |
| no candidate residual known yet | 1,052 |
| of these, every candidate residual has a completion | 35 |

The most used classes are very sparse prefixes. One is a 10-channel prefix with layers of 1, 1
and 3 comparators; most others are 11-channel prefixes with 2, 1 and 4, which reschedule into
two layers of 4 and 3. Four sentinels absorb nearly all comparators of the first three layers,
and six layers cannot sort what is left.

**Why a child is hard.** For a child that does not close at once, the prover tries its candidate
residuals in order (lowest residual height first). Two things make that slow.
* **Candidates with a completion.** Of the 11 classes that would cover the most open children
  and were decided (`s14/s14_topclasses.py`), 5 have a completion and close nothing. The first would
  have covered 442 children: a 10-channel residual whose comparators fit in one layer of four.
* **Costly residuals without a completion.** The other 6 took 1 s to 251 s and up to 4,703 facts.
  Three more were still open after 15 minutes (19,000–34,000 facts). The hard child of case 0
  (§8.11, sample 3) picked an 11-channel residual with three layers of 3 comparators. Proving it
  means a split whose children reduce to 10-channel nodes with five layers left, the P1 type of
  §8.5.

How many comparisons four sentinels can leave unabsorbed tracks this only loosely. Children closed
by a quick step keep 1–3 real comparisons, those closed by a stored residual 2–5, and those where
every candidate completes mostly 5–7.

**Sparse-start lemmas would close most children at once, but the obvious ones are false.** A
proved SS(r, 6 + h, a, h) closes every child that has a residual on r channels whose real
comparisons fit in h layers of at most a. Share of the 3,342 children that need a residual that
each lemma would cover:

| lemma | covers | true? |
|---|---|---|
| SS(10, 8, 3, 2) | 97% | false: split the first layer of a depth-7 10-sorter into 3 + 2 |
| SS(10, 8, 2, 2) | 53% | false: SAT finds a depth-8 network with layer sizes 2,2,5,5,4,4,5,4 |
| SS(10, 9, 2, 3) | 81% | false: split the first layer of a depth-7 10-sorter into 2 + 2 + 1 |
| SS(11, 8, 4, 2) | 90% | unknown |
| SS(11, 8, 3, 2) | 50% | unknown (SAT: no first-round answer in about 7 minutes of compute) |
| SS(11, 9, 3, 3) | 83% | unknown |

So the residual facts are specific prefixes, not instances of a uniform statement.

**Whole cases.** With sharing, the unit of work is a case, not a child.
* **Case 681 is proved.** Its second layer is empty. Sentinels on channels 2, 4 and 6 (+∞) leave an
  11-channel node whose first layer has 2 comparators, with seven layers left. That node has no
  completion (a split with 40 children), so the case root closes in one sentinel step: 112 s, and
  the proof checks with 0 failures. The root needed none of its 3,032 children. Proving all of
  them anyway took 7 workers about 8 minutes, plus about 5 minutes each for four children whose
  residual was a 10-channel node with layers of 3 and 2 comparators. (The laptop slept from 14:57
  to 21:34, so the logged wall times of those four children are mostly sleep.)
* **A survey of all 682 case roots**, 30 s each, 7 workers sharing facts
  (`s14/s14_root_survey.py`), by the size of the second layer:

  | second-layer comparators | cases | closed at the root | open after 30 s |
  |---|---|---|---|
  | 0 | 1 | 1 | 0 |
  | 1 | 4 | 3 | 1 |
  | 2 | 21 | 17 | 4 |
  | 3 | 76 | 62 | 14 |
  | 4 | 220 | 0 | 220 |
  | 5 | 360 | 0 | 360 |

  Every closed root closed by one sentinel step. All 82 root facts check: 391,277 facts needed,
  0 failures. No root was found to have a completion.

So 83 of the 682 cases are proved, and the cost of S14 is the 580 cases whose second layer has 4
or 5 comparators. Those need a root split with 10,000–42,000 canonical children. The children
mostly close through a pool of shared residual classes on 10 and 11 channels. §8.13 measures
what it costs to finish one such case.

### 8.13 One five-comparator case end to end: case 0

Case 0 has the smallest output set (1,296 vectors) of the 580 open cases. Its second layer has
5 comparators, and its root split has 17,881 canonical children (64 automorphisms). The run took
about 7 worker-hours on 7 workers (64 minutes) and was stopped on battery power before the case
finished.

**Scripts.**
* `s14/s14_case_run.py` proves the children in passes. Workers take the children in a fixed
  random order and claim each with a file, so faster cores take more. Facts are shared through the
  store. Each pass gives a child a time cap, and a child still open is retried in the next pass.
  A random order makes a pass's progress an unbiased sample of the case.
* `s14/s14_case_status.py` summarizes the logs.
* `s14/s14_case_sweep.py` closes, without any proving, every child that one sentinel step onto a
  stored residual closes, and lists the rest.
* `s14/s14_case_root.py` assembles the root once every child is proved. It first checks that all
  children are stored, then splits the root without trying sentinel residuals there (the survey
  showed the root dives into a costly one). It ran on case 681, whose root and children are
  stored; its split path is not yet exercised.

**What happened.**

| step | settings | time | children closed | left open |
|---|---|---|---|---|
| pass 1 | 10 s cap | 3 min | 643 of the first 739, all at once | 96 (13%) |
| pass 2 | 600 s cap | 31 min | 18: 4 at once, 11 in 25–61 s, 3 in 160–215 s | 18 at 600 s, 4,400–13,400 nodes each |
| pass 3 | 600 s cap, new guidance | 21 min | 5, all at once | 7, each also open in pass 2 |
| sweep | lookups only, 4 workers | 5 min | 14,500 | 980 |

So 16,901 of the 17,881 children (94.5%) are proved. The other 980 have no stored residual
among their sentinel candidates and need real proofs. The 7 children still open after pass 3 had
each been worked on for 20 minutes and had 17,000–27,000 nodes.

**Where the time goes.** The children of pass 2 that closed in 25–61 s spent almost all of it on
SAT guidance before reaching a stored residual beyond the first 300 candidates. A profile of one
hard child (300 s, 2,418 nodes) shows 4,314 SAT guide calls taking 97 s, half of it building the
CNF model. The rest is the prover's own Python work: sentinel states were computed 6.7 million
times and classes looked up 458,000 times. In 31 minutes the pass-2 workers wrote 205,000 facts,
only 1% of them duplicates across workers. Most are small nodes:

| node (channels, layers left) | facts |
|---|---|
| 9, 3 | 94,000 |
| 10, 4 | 39,000 |
| 10, 3 | 17,000 |
| 8, 3 | 15,000 |
| 9, 4 | 14,000 |

The trees grow through splits:
* 10-channel nodes with five layers left (the P1 type of §8.5) split into 870 children on
  average, at most 1,900;
* 9-channel nodes with four layers left split into 40–100;
* 8-channel nodes with three left split into about 50.

**Guidance options** (sprove.py; off by default, so earlier runs are unchanged):
* `store_first_n=13, store_first_big=10**6`: at nodes with at least 13 channels (the root
  children), look up every sentinel candidate's residual in the store before any SAT call, not
  only the first 300.
* `guide_skip_n=13`: no SAT verdict for 13-channel residuals. These are the single sentinels of a
  child; each such call took about 6 s against a 2 s limit and never decided anything.
* `guide_conflicts=10000` (was 50,000): SAT limits are checked between rounds of this many
  conflicts, so they are kept more closely.

An A/B test ran three hard children for 150 s each, old settings against new, on separate copies
of the store:

| child | old settings | new settings |
|---|---|---|
| 3557 | open, 2,531 nodes | closed in 0.1 s by a stored residual |
| 11207 | open, 1 node: all 150 s in 21 SAT calls at the child | open, 2,278 nodes |
| 17481 | open, 1,762 nodes | open, 3,112 nodes |

The store copies diverged after the first child, so the closure of 3557 may partly come from
facts the new run proved for 17481. A lookup-only sample measures the window effect directly:
* 1,571 of 1,800 fresh children (87%) close within the first 300 candidates;
* 114 (6%) close only with the full window;
* 9 were already proved;
* 106 (6%) had no stored residual.

Of the hard children rerun in pass 3, 5 closed at once, through the wider window and facts
proved in the meantime.

**What finishing case 0 would cost.** About 21 of the children without a stored residual were
followed through passes 2 and 3:
* 3 closed in about 3 minutes;
* 5 closed at once on their second try;
* 7 were still open after 20 minutes;
* the rest were unfinished when the passes stopped.

If a third of the 980 behave like those 7, they alone need more than 100 worker-hours. At the
measured rate of about 1,000 new facts per worker-minute, that is millions of facts. Sharing will
shrink this, but the run gives no sign that it shrinks to a few hours.

**Memory is the hard limit.** Every worker holds the whole store in memory, about 2.1 KB per
fact. The store now has about 976,000 facts (400 MB on disk), and loading it takes 2.0 GB per
worker, so 7 workers already need 14 GB of the laptop's 16. At 5 million facts one worker would
need about 10 GB.

**What this means.** With the current prover and store, case 0 cannot be finished on this
laptop, and S14 has 580 such cases. Suppose sharing between cases cut each case's cost tenfold.
S14 would still need thousands of worker-hours and hundreds of millions of facts. That is
comparable to the 7,700 CPU-hours of the original 2015 computation, for a proof far too large to
check by hand. Three things would change the picture:
1. a rule that closes 10-channel nodes with five layers left without splitting them, since those
   splits multiply the trees about 900-fold;
2. a store that is not copied into every worker, on disk or in shared memory;
3. a descent for D(17) that does not go through S14.

### 8.14 Closing the hard children: rules tried, and a cheaper route to D(17)

The 980 hard children of case 0 (§8.13) were the test set. Scripts are in `sat14/`; logs are in
`logs/sat14_*` and `logs/t13_*`.

**Why the prover stalls on them.** No sentinel step closes a hard child. `sat14/cand_probe.py`
enumerates every sentinel set, not only the prover's pool, on child 10890:
* residuals of 4 and 5 sentinels (10 and 9 channels) have completions; SAT finds them in under
  a second;
* residuals of 1–3 sentinels are undecided within the guide's budget.

The prover's guidance also combines sentinels only from a pool of about 4 channels, so it never
sees most 3- and 4-sentinel sets. Once no candidate is known to lack a completion, the prover
recurses into undecided 12- and 13-channel residuals, which may have completions. That is where
the 10,000+ nodes per child go.

**Rules that do not close them.**

| idea | result |
|---|---|
| split on layer 4, close by the compiled sentinel covers (`split_probe.py`) | 389,000–814,000 next layers per child; 386 to 135,650 stay open (4 children) |
| subsumption among hard children (`sub_probe.py`) | 3 of 100 embed into a smaller sampled child |
| reuse an input core across children (`core_probe.py`) | the core of child 10098 is 616 of its 623 outputs |
| quick rule as clauses on layer 4 (`child_sat_plus.py`) | 85–98% of next layers satisfy every clause |
| one SAT instance for six children (`multi_child_sat.py`) | no answer after 42 min; the six alone took 23.5 min in total |

**Sparse-start lemmas.** `lemma_cover.py` computes which lemmas would close 40 sampled hard
children through some sentinel set. Lemmas at depth one above D(r) cover everything but are
false or no easier than S14. At tight depth:

| lemma | closes | true? |
|---|---|---|
| SS(13, 9, a, 1) for a = 3, 4, 5 | 100% | a = 5 false: 3 sentinels on a depth-9 16-sorter leave first layer 5; a = 3, 4 open |
| SS(13, 9, 4, 2) | 85% | open |
| SS(11, 8, 4, 1) | 55% | **false**: SAT network, 103 s |
| SS(11, 8, 3, 1) | 50% | **false**: SAT network, 398 s |
| SS(11, 8, 4, 2) | 48% | open: CEGAR still had 2–5 failing inputs after 81 min |
| SS(12, 8, 5, 1) | 15% | open (10 min) |

Also false: SS(9, 7, 3, 1) (0.4 s) and SS(10, 7, 4, 1) (27 s). **Depth-optimal sorters need not
start with a full layer.** SAT found a depth-8 11-sorter whose first layer has 3 comparators
(`first_layer.py`, `logs/sat14_first_layer.log`). One-layer sparse starts are no route to S14.

**SAT closes every hard child it was given, with checkable certificates.** netsat's model has
the end-game constraints. Each run below refutes "prefix (L1, L2, L3) plus six layers sorts":

| setup on child 10098 | time |
|---|---|
| all outputs encoded, CaDiCaL 1.9.5 (pysat) | 93 s |
| CEGAR, CaDiCaL 1.9.5 | 161 s |
| all outputs, kissat 4.0.4 | 196 s |
| CEGAR, glucose 4 | 312 s |
| CEGAR, co-saturation constraints | 326 s |
| CEGAR, 100 starting inputs | 413 s |

These runs shared the CPU, so the times are noisy.
* With all outputs encoded, 6 random hard children took 152–371 s each.
* With CEGAR, 3 of the prover's hardest children were still open at 300 s.
* The standalone CaDiCaL 2.1.2 refuted child 10098 in 131 s with an 80 MB DRAT proof, which
  drat-trim verified in 87 s.

That is a usable rule, about 4 minutes per hard child including the check. But it does not
scale to S14.

**S14 is far bigger than case 0 suggests.** `exceptional_census.py` lists every case's
canonical children:

| statement | cases | canonical root children | exceptional children |
|---|---|---|---|
| S14 = T3(14, 5) ≥ 10 | 682 | 107,264,708 | 11,402 |
| T3(13, 4) ≥ 10 | 220 | 2,538,881 | 27,582 |
| T3(12, 3) ≥ 10 | 58 | 41,039 | 3,748 |

A child is exceptional when no sentinel of the first layer has a good track through layers 2–3
(§4.1). At 5% hard children and about 4 minutes each, S14 child by child is hundreds of
thousands of CPU-hours.

**The descent with exceptions skips almost all of them.** §4.1 gives
T3(14, 5) ≥ min(T3(13, 4), E3(14, 5)) and T3(13, 4) ≥ min(T3(12, 3), E3(13, 4)).

In prover terms: once SS(13, 9, 4, 3) is a registered statement, a non-exceptional S14 child
closes by its good-track sentinel and the lemma rule. The root's sentinel covers can close such
children in bulk. Only exceptional children need their own proofs.
* In S14's case 0, 36 of 17,881 children are exceptional, all 36 among the 980 hard ones.
* T3(13, 4)'s case 0 has 1,747 children:
  * a lookup sweep closes 1,613 and leaves 134 hard;
  * 202 are exceptional at (13, 4), and these include 121 of the 134 hard ones;
  * 6 random hard children took 56–140 s each by SAT.
* A 30-second survey of T3(13, 4)'s 220 case roots: all 1 case with an empty second layer,
  all 4 with 1 comparator, 19 of 20 with 2 and 39 of 60 with 3 close at the root; none of
  the 130 with 4.
* Whole statements are too big for one SAT call. E3(14, 5), E3(13, 4), E3(12, 3), T3(13, 4),
  T3(12, 3) and T3(11, 2) were each undecided after 30 minutes.

So D(17) ≥ 10 would follow from three pieces:
1. no completion for the 11,402 exceptional S14 children;
2. no completion for the 27,582 exceptional T3(13, 4) children;
3. T3(12, 3) ≥ 10 itself (58 cases, 41,039 children, which can descend once more with 3,748
   exceptions).

If every exceptional child needs SAT, at the measured 2–4 minutes, that is roughly 1,200–1,600
CPU-hours. The published computation took about 7,700. Sentinel steps and stored residuals
should close part of them first. §8.15 builds the route, starting one level lower at
SS(11, 9, 2, 3).

### 8.15 The descent route, built: run `descent_run.sh`

This implements the route of §8.14 and starts it one level lower, where the statement is cheap:

| statement | cases | root children | exceptional | proved with |
|---|---|---|---|---|
| SS(11, 9, 2, 3) = T3(11, 2) ≥ 10 | 16 | 918 | 215 | the prover and SAT; proved and checked here |
| SS(12, 9, 3, 3) = T3(12, 3) ≥ 10 | 58 | 41,039 | 3,748 | lemma SS(11, 9, 2, 3) + SAT for the rest |
| SS(13, 9, 4, 3) = T3(13, 4) ≥ 10 | 220 | 2,538,881 | 27,582 | lemma SS(12, 9, 3, 3) + SAT for the rest |
| SS(14, 9, 5, 3) = S14 | 682 | 107,264,708 | 11,402 | lemma SS(13, 9, 4, 3) + SAT for the rest |

S14 gives $D(17)\ge10$ by the hand descent (§4, §5.2).

**Two new proof rules**, in `sprove.py` and checked independently by `check_facts.py`:
* **Lemma steps in the residual's own layers** (`'sched': 'asis'`). A good-track sentinel (§3)
  leaves a residual with at most a − 1 real comparators in each of its three layers. That is
  exactly what SS(n − 1, 9, a − 1, 3) excludes. Rescheduling the residual as soon or as late as
  possible can push more comparators into one layer, so the lemma rule now also tries the
  residual as it stands, empty layers included. This works in the lemma rule, the leaf test and
  the sentinel covers of splits (Python and the C core). The checker recounts the real
  comparators per layer with its own sentinel simulation.
* **SAT certificates** (`'rule': 'sat'`, `satcert.py`). The node's CNF is netsat's encoding with
  every unsorted output of the prefix, generated deterministically from the node. It is solved
  by the standalone CaDiCaL with a DRAT proof, and the proof is checked by drat-trim and then
  deleted. The record (CNF sha256, times, verdict) goes to `STORE/sat_certs.jsonl`.
  `check_facts.py` regenerates the CNF from the fact's prefix and compares the hash. It accepts
  the recorded drat-trim verdict, or with `--resat` re-solves and re-checks. The trusted base is
  netsat's encoding with its published end-game normal forms (as in the S11 SAT proof) and
  drat-trim. Whenever covers or quick steps rely on recorded statements, the checker now also
  checks those statements' proofs.

**The driver**, `descent_cases.py SS:n,9,a,3 STORE W w`, handles each case of a level:
1. try the case root with the ordinary prover (`--root-seconds`, default 60);
2. otherwise split it on the third layer; the sentinel covers close every third layer with a
   good track, through the lemma one level down;
3. give each remaining child, and the child with an empty third layer, a short prover attempt
   (`--child-seconds`, default 20), then a SAT certificate of the child itself;
4. assemble the case root from the stored facts.

Then `--assemble` proves the statement, and the next level can use it as a lemma.
* Workers claim cases with files under `STORE/claims/` and share facts through the store.
* A child that SAT completes to a sorting network is written to `STORE/COUNTEREXAMPLES.jsonl`
  and stops the worker.
* `descent_init.py` builds a fresh store from `results/descent_base_*`: D(3..11) and the small
  sparse-start lemmas, 1,178 facts in 55 KB. S11 is left out, since the descent does not use it.

**Validation.**

*Tests:*
* `test_fastcore.py` passes. Its new section 10 runs all 82 cases of S9 = SS(9, 7, 3, 3) with
  the lemma SS(8, 7, 2, 3). Over 86,993 third layers, the covers close every one that has a good
  track, and C and Python agree. They close none of the exceptional ones.
* `sat14/descent_negative.py` makes the checker reject a `sat` fact with a wrong CNF hash, one
  whose certificate record is missing, and a split whose covers were removed.

*S9 from scratch*, in a store holding only D(3..10) and SS(8, 7, 2, 3):
* the root attempt was skipped and every open child sent to SAT, so the whole path is
  exercised;
* all 82 cases were proved, with 184 children by SAT certificates (138 records, all
  drat-trim-verified), and the statement assembled;
* `check_facts.py` verified 281 facts with 0 failures, including the base statements; with
  `--resat`, all certificates were re-solved and re-checked, 0 failures.

*SS(11, 9, 2, 3) on real sizes*, in a fresh store, one worker, 12 minutes:
* 13 case roots closed directly;
* 2 cases needed splits (80 children by the prover, 6 by SAT);
* the statement assembled, and its proof checks: 1,250 facts, 0 failures.

*T3(12, 3) case 21*, with that lemma: 4 sentinel covers close 901 of its 920 third layers. The
19 left open are exactly its exceptional ones.

*SAT on 11- and 12-channel children* took 29–57 s to solve plus about as long to check.
Hard 13- and 14-channel children took 1–6 minutes to solve (§8.14).

**Cost and memory.**
* About 43,000 exceptional children in all. If every one needs SAT, at 1–2 minutes (11–12
  channels) to 3–8 minutes (13–14 channels) including the proof check, that is on the order of
  2,000–3,000 CPU-hours, most of it at T3(13, 4).
* Every worker holds the whole store in memory, about 2 KB per fact. The SAT route adds one
  fact per child, but prover attempts add hundreds; `--child-seconds -1` skips them.
* CaDiCaL needs about 0.5 GB per 14-channel child. Each certificate briefly needs about 10 MB of
  CNF and up to 100 MB of proof in `SATCERT_TMP`.

**How to run it on another machine.**
1. Python 3.10 or later with `pip install python-sat`, and a C compiler (`cc`, or set `CC`);
   the C core builds itself on first import.
2. CaDiCaL (`git clone https://github.com/arminbiere/cadical && cd cadical && ./configure && make`)
   and drat-trim (`git clone https://github.com/marijnheule/drat-trim && cd drat-trim && make`).
   Point `CADICAL` and `DRATTRIM` at the binaries, or put them on `PATH`.
3. From `thin-layers/`:
   `CADICAL=... DRATTRIM=... SATCERT_TMP=/fast/tmp PY=python3 ./descent_run.sh /data/store 32`.
   It builds the store, runs 32 workers per level, assembles each level, and finally runs
   `check_facts.py` on S14. That check includes all four levels and the base statements.
4. Progress: `python3 descent_cases.py SS:13,9,4,3 /data/store --status`, and the logs
   `/data/store/log_*`. Rerunning the same command resumes.
5. If a level stops with open cases (a SAT limit was hit, or a worker died), remove
   `/data/store/claims/<level>` and rerun.
6. `DESCENT_OPTS` passes options to every worker, e.g. `"--child-seconds -1 --sat-seconds 7200"`.

None of SS(12, 9, 3, 3), SS(13, 9, 4, 3) or S14 is proved yet: that is the run. SS(11, 9, 2, 3)
was proved here, in a scratch store.

## 9. Toward a hand proof for the efficient prefixes

The route of §8.15 settles the exceptional configurations by SAT. A hand proof of $D(17)\ge10$
needs an argument for them instead. [efficient-prefixes.md](efficient-prefixes.md) collects what
is known.
* **Structure theorem (proved).** Exceptional configurations have full second and third layers,
  and the tracks that meet layer 2 land on layer 3's idle channels. At (14, 5), layer 2 contains at
  least two merges.
* **Normal form.** Redundant comparators can be deleted, which shrinks the cases.
* **What provably cannot settle them.** Sentinel reductions, one-layer sparse lemmas (several are
  false at optimal depth), a splitting construction that refutes many candidate statements, and
  static linear-extension arguments.
* **Probe tokens settle the $D(11)$ level without SAT.** Every normalized exceptional prefix of
  E3(9, 3), E3(8, 2) and E3(7, 1) (1,010 + 663 + 59) fails the token cone bound at layer 5: after
  any fourth and fifth layer, some output's tokens lie on at least 5 channels. With the descent
  this gives $D(11)\ge8$ from a two-second enumeration (`hand/tokcore.c`), cross-checked without
  pruning (`hand/tokfull.c`).
* **In fact every sparse prefix fails, not only the exceptional ones.** All 87,075 prefixes of
  $T_3(9,3)$ (and all of $T_3(8,2)$, $T_3(7,1)$) fail at layer 5 in under two minutes. So
  $D(11)\ge8$ needs only the descent to $T_3(9,3)$ and one lemma, (W): after a sparse 9-channel
  prefix and any two more layers, ranks 3–5 still lie in at least 13 channel intervals.
  efficient-prefixes.md §7 reduces (W) exactly to counting "separated" pairs: 2-element hitting
  sets of the families of positions of the smallest and largest elements.
* **The obstruction is local to the middle outputs.** At (9, 3), a sum over outputs 3–5 already
  exceeds the cone, but the median alone refutes nothing. The sum over all outputs never
  suffices, so the total spread is the wrong potential.
* **Tokens are rank intervals (proved).** Channel $c$ holds a token of output $k$ exactly when the
  element on $c$ can have rank $k$. These ranks form an interval fixed by the least term and
  clause sizes of the channel's Boolean function. An overlap-free calculus of these intervals is
  too weak over several layers (it refutes 205 of 1,010 prefixes at (9, 3)), so overlaps matter.
* **(W) has short certificates, but one per class.** Take any of the 1,003 leftover prefixes at
  (9, 3). An LP certificate proves (W) for every fourth and fifth layer at once
  (efficient-prefixes.md §7.3–§7.6). It consists of potentials on the nine channels and cover values
  on the possible fourth-layer outputs.
  * The overlaps it needs are pairwise and visible in the prefix: which shortest terms of two prefix
    channels meet.
  * Still, the 136 classes need separate certificates of about a thousand checks each. That is a
    checkable appendix, not yet a readable proof.
  * The fifth layer can be dropped. Let $N_t$ count the fourth-layer outputs that still have a
    partner with gain at least $t$. Then a fifth layer removes at most
    $\lfloor N_1/2\rfloor+\lfloor N_2/2\rfloor+\lfloor N_3/2\rfloor$. Layer-4 removal plus this
    count is at most 14 for every fourth layer of every leftover (efficient-prefixes.md §7.7).
* **$D(13)\ge9$ without SAT (efficient-prefixes.md §9).** The hand descent reduces it to
  $T_3(11,4)\ge9$: 2,647,384 sparse 11-channel prefixes in 315,835 reachable-set classes, with three
  free layers. Every class is settled by the exact token search, in about 15 CPU-hours.
  * 315,619 classes are settled through a sentinel residual whose 10-channel class tokens refute:
    4,561 such classes are refuted, and 10 others complete to depth-8 sorters.
  * The other 216 classes are refuted directly.
  * Prefixes of one class extend or fail together (subsumption). Witnesses are in
    `logs/hand_d13_token_witness.tsv.gz`.
  * **Checked independently** (efficient-prefixes.md §9.2, `hand/indep13/run_all.sh`). New code
    recomputes the family, the classes, the residuals and every token search. It agrees on every
    count, in about 9 CPU-hours.
    * Classes are identified by explicit, state-checked permutations, not hashes. The partition agrees
      prefix by prefix with the 128-bit hash classes.
    * The token search uses fewer facts: no end-game normal form and no merge filter. Its node counts
      equal the original's at every layer for all 4,787 searches.
    * The hash-free certificate is `logs/ind13_class_witness.tsv.gz`.
* **$D(17)$, the same strategy (efficient-prefixes.md §10).** Reachable-set classes cut the
  exceptional children that the SAT route of §8.15 must refute. One refutation settles a class, and a
  class that also contains a non-exceptional prefix needs none.
  * (12, 3): 3,748 children become 787 classes.
  * (13, 4): 27,582 children become 6,238 classes.
  * In all, roughly 9,500 SAT refutations instead of 43,000. Tokens cannot replace them: four free
    layers cost about 16 CPU-hours per class.
* **At 14 channels** the evidence is heuristic. Beam search brings half of the feasible prefixes
  inside the cone at layer 7, but no exceptional S14 prefix: those miss by 7–11 channels in the
  middle outputs. $D(17)$ needs four layers before the cone, out of reach of exhaustive search.
