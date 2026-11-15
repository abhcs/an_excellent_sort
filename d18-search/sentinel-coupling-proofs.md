# Exact transport of normalized sentinel restrictions

**Status.** These hand-proved constraints apply at arbitrary width. They
do not settle D(18), and eliminate none of its 411 cover cases on their
own. They strengthen and correct a statement in the earlier
[coupled-restriction note](structural-frontier.md).

The real-position distance of two normalized restrictions can only
decrease, through two specified types of comparison. Comparable
restrictions keep their exact distance. Once restrictions coincide,
they remain identical.

## 1. Seven joint types

A sentinel configuration is a vector over $\{-1,0,1\}$: $0$ denotes
an arbitrary real, and $-1,1$ denote signed infinities. On each first-layer
pair $(a,b)$, $a<b$, a normalized placement chooses $(-1,0)$ or $(0,1)$.
Idle wires hold reals. Thus two normalized placements $P,Q$ satisfy
$|P_i-Q_i|\le1$ on every wire. Their seven possible joint types are

$$(-1,-1),\quad (-1,0),(0,-1),\quad (0,0),\quad
  (0,1),(1,0),\quad (1,1).$$

**Theorem 1 (exact transport).** A common comparator preserves the
multiset of its two joint input types except for the following changes:

$$\{(-1,0),(0,-1)\}\longmapsto\{(-1,-1),(0,0)\},$$
$$\{(0,1),(1,0)\}\longmapsto\{(0,0),(1,1)\}.$$

The seven-type condition remains true through every later layer.

*Proof.* The low output receives the coordinatewise minimum and the high
output the coordinatewise maximum. Every pair of the seven types is
comparable except the two displayed pairs, whose minimum and maximum
are exactly as shown. Induct over comparators. $\square$

The theorem applies to any two configurations satisfying the seven-type
condition, even if they did not come from the normalized construction.
It excludes the joint types $(-1,1)$ and $(1,-1)$ and does not apply to
arbitrary pairs of ternary configurations.

Let the two real-position sets $R_P,R_Q$ have the same size $r$, and put

$$d(P,Q)=\tfrac12|R_P\mathbin{\triangle}R_Q|=r-|R_P\cap R_Q|.$$

If a layer has $e_-$ comparisons of the first exceptional kind and
$e_+$ of the second, then

$$d(P',Q')=d(P,Q)-e_--e_+.$$

Each exceptional comparison replaces two exclusive real positions by
one common real position. All other comparisons preserve their count.

**Corollary 2 (permanent coalescence).** Distance never increases. If
$R_P=R_Q$, the entire signed configurations are equal and remain equal.

*Proof.* The only permitted types with both coordinates real or both
nonreal are $(-1,-1),(0,0),(1,1)$. $\square$

The earlier claim that neighboring stick restrictions could have equal
real sets and subsequently separate was incorrect for these placements.
Even non-neighboring restrictions cannot separate after coalescing.
General contraction in numeric $L^1$ distance was too weak to show this.

## 2. Comparable restrictions keep their exact distance

**Theorem 3.** Suppose the seven-type condition holds, each run has $r$
reals, and $P\le Q$ coordinatewise. The multiset of joint types is
invariant. If $k$ is the number of positive sentinels of $Q$ minus that
of $P$, then at every later layer boundary

$$d(P,Q)=k,\qquad |R_P\cap R_Q|=r-k.$$

*Proof.* Only the five types

$$(-1,-1)<(-1,0)<(0,0)<(0,1)<(1,1)$$

occur. They form a chain, so a comparator just orders them. Equal real
counts imply equal numbers of $(-1,0)$ and $(0,1)$; each number is $k$.
$\square$

Index a normalized placement by the set $S$ of first-layer pairs on
which it chooses the positive sentinel. If $S\subseteq T$, then

$$d(P_S^{(t)},P_T^{(t)})=|T\setminus S|$$

after every common prefix of length $t$, whether or not its second layer
is blind. In particular this holds along any coordinatewise chain of
half-blind placements. A stick's natural path of placements need not be
monotone as a whole; its individual neighboring pairs are comparable,
so each neighboring distance stays exactly one.

**Corollary 4 (full pairing).** If $r$ is even and two comparable
restrictions differ by an odd number of sign choices, no later matching
can pair up both real sets.

*Proof.* Their intersection has odd size $r-k$. Pairing both sets would
also pair their intersection. $\square$

This extends the three-colour [H9 six-cycle argument](../depth-hand-proofs/h9-cycle-case.md)
to allow common negative and common positive sentinels. Assigning the
same extra sentinel in both runs to an originally common real input
preserves the five-type condition. Such pruning can change the parity
of the retained width, but a depth contradiction still requires valid
facts about that smaller width.

## 3. How many mergers a sorting suffix must perform

Let $s_P,s_Q$ count positive sentinels and set $\delta=|s_P-s_Q|$.
The seven-type condition and equal real counts give $\delta\le d\le r$.

**Theorem 5.** A common suffix sorting both configurations must contain
exactly $d(P,Q)-\delta$ exceptional comparisons from Theorem 1.

*Proof.* In the two sorted configurations the real sets are intervals
of length $r$, offset by $\delta\le r$. Their distance is $\delta$.
Sum the distance-loss identity over the suffix. $\square$

More precisely, let $l,\bar l$ count $(-1,0),(0,-1)$, and let
$u,\bar u$ count $(0,1),(1,0)$. There must be exactly
$\min(l,\bar l)$ lower mergers and $\min(u,\bar u)$ upper mergers.
Each removes one of each type of its kind; in sorted configurations
only the direction consistent with the offset remains.

For equal numbers of sentinels of each sign, $\delta=0$ and the real
sets must eventually coalesce. For comparable restrictions, $d=\delta$
and neither kind of merger can ever occur.

## 4. The complete D(18) cover

Construct the half-blind family after layer 2 of each saturated prefix.
Every member has nine reals. Call a pair *rigid* if its distance cannot
change, as in Theorem 3. Direct evaluation gives:

| Property | Prefix cases |
|---|---:|
| At least one rigid pair | 390 |
| A rigid pair at odd distance | 382 |
| A rigid pair at distance at least three | 319 |
| No rigid pair in this family | 21 |

These are classifications, **not eliminations**. Nine is odd, so
Corollary 4 does not directly apply. A further pruning or a stronger
nine-wire profile statement is still needed for a depth contradiction.

The 51 two-state families have the following merger requirements:

| Distance $d$ | Rank gap $\delta$ | Required mergers | Cases |
|---|---|---|---:|
| 1 | 1 | 0 | 12 |
| 3 | 1 | 2 | 8 |
| 3 | 3 | 0 | 10 |
| 5 | 1 | 4 | 5 |
| 5 | 3 | 2 | 4 |
| 5 | 5 | 0 | 6 |
| 7 | 1 | 6 | 1 |
| 7 | 3 | 4 | 1 |
| 7 | 5 | 2 | 1 |
| 7 | 7 | 0 | 2 |
| 9 | 9 | 0 | 1 |

The [data file](results/sentinel-coupling18.json) records all 31,313
pairs, their states, distances, rank gaps and merger requirements,
bound to the complete-cover digest. No SAT solver is used.

## 5. The cost of using only pure opposite signs

Consider a pure negative-sentinel run $P$ and pure positive-sentinel
run $Q$ through a perfect first matching. Let $m_P,m_Q$ count retained
gates, and $c'$ common real positions afterwards. Let $u,v$ count gates
whose joint input types are both $(-1,0)$ or both $(0,1)$ respectively.
An exact per-gate count gives

$$m_P+m_Q=c'+u+v\ge c'.$$

Each common real output contributes one to the left side; the only
additional contributions are the gates counted by $u,v$. The
incomparable pair $(-1,1),(0,0)$ contributes zero on both sides.

At width $2p$, if each run has $s\le p$ sentinels whose supports overlap
in $k$ positions after the layer, this implies

$$m_P+m_Q\ge2(p-s)+k.$$

Thus an overlap cannot be added while keeping the minimal first-layer
cap $p-s$ in both runs. If both runs blind a perfect first matching,
their real sets are disjoint afterwards. This limitation concerns the
pure-sign variant; the seven-type construction allows common sentinels.

## 6. A boundary for a possible eight-wire application

It is false that every depth-six eight-wire sorter has a full first
layer. The [explicit counterexample](../depth-hand-proofs/results/eight-wire-first-layer-profile.json)
has first-layer size three and sorts all 256 binary inputs. Its layer
sizes are $(3,4,4,4,3,4)$.

Three is the exact minimum first-layer size at that depth. With at most
two first-layer gates, one signed infinity can remove one of them;
pruning would give a depth-six seven-wire sorter with at most one
first-layer gate, contradicting the hand-proved P7 lemma. An empty
first layer is excluded by $D(7)\ge6$ after dropping that layer and
pruning one wire.

Thus Corollary 4 cannot force an eight-real restriction at minimum depth
to be immediately fully paired. The subsequent
[early-profile hand proof](../depth-hand-proofs/h7-early-profiles.md)
does prove the two-layer substitute: each of its first two layers has
at least three gates, and one has four. Two comparable restrictions with
an odd, invariant intersection must therefore be fully paired in different layers,
with respective count profiles $(4,3)$ and $(3,4)$.

## Verification

[`sentinel_coupling.py`](sentinel_coupling.py) checks all 49 ordered
pairs of seven joint types, and all 16 cases for the pure-sign count
identity. It constructs every family in the cover and checks 187,878
additional transport steps on sampled matching continuations. The local
calculation and induction prove the general claims; sampling only audits
their implementation at larger widths.
The exact merger totals are also checked on 256 pairs of normalized
placements for each of two known 18-wire sorters. Both sorters are
independently verified on all 262,144 binary inputs.

```sh
python3 d18-search/sentinel_coupling.py --out d18-search/results/sentinel-coupling18.json
```
