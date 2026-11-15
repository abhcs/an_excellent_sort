# A full three-rank block needs a fourth wire, but cannot use a fixed rank to sort

All positions and ranks are numbered from zero. A matching layer allows idle
wires. Write Q(c) for the exact attainable ranks at wire c of a comparator
prefix, evaluated over all distinct input permutations. The results below
place no adjacency or perfectness restriction on either remaining layer.

## Four-wire component forced by three demands

Let T be any set of three wires. Suppose that each wire t in T must reach
every position in T through two matching layers P,S. Then there is a unique
wire u outside T such that both layers preserve E=T union {u}, and every
wire in E has forward cone exactly E.

Indeed, each forward cone is the union of at most two S-blocks. Therefore S
must pair two vertices a,b of T. Let t be its remaining vertex. Each of a,b
must be P-paired to a vertex in the S-block of t. They need distinct
partners, so that block must be {t,u} for some u outside T. The two P-edges
are a-t,b-u or a-u,b-t. These four edges isolate E in both layers and give
every wire of E the full cone E. This proves the assertion without a
normal-form assumption.

Consequently, for any required rank relation R, u can be a borrower only
if every demand out of E stays in E and every demand from outside E stays
outside E. This strengthens a row-only test R(u) subset E: an incoming
demand from outside also excludes u.

For pairwise disjoint three-wire sets T_i, each with all three demands,
the four-wire components are pairwise disjoint. Two such components cannot
intersect because they are isolated connected components of P union S;
nor can they coincide, since their union contains six distinct required
wires. Thus the T_i require distinct borrowers, all outside their union.
For eligible-borrower sets B_i, every subfamily J must satisfy the Hall
inequality |union over i in J of B_i| >= |J|. This is necessary, not a
general sufficiency claim for the other demands.

## Consequences for exact attainable ranks

Suppose Q(t)=T for all three t in T. In every run, those three positions
hold precisely the three ranks T. Permutation conservation implies that
no outside wire can hold a rank in T. The borrower forced above must have
Q(u) subset T union {u}; therefore Q(u)={u}. Such a borrower is a fixed-rank
wire. In particular, k disjoint full three-rank blocks need at least k
distinct fixed-rank wires just to satisfy two-layer reachability.

If S is additionally adjacent and T=[a,a+2], its borrower is either a-1 or
a+3: the third T vertex must be paired across one of the two boundaries.
This gives a path Hall condition, stronger than counting all fixed wires.
This paragraph uses adjacency; all previous conclusions do not.

## Stronger sorting obstruction: no full three-rank block

**Theorem.** If an actual comparator prefix has

    Q(a)=Q(a+1)=Q(a+2)={a,a+1,a+2},

then it has no sorting completion of two comparator layers, at any width.

Assume a completion P,S. The four-wire lemma isolates E=T union {u}, and
rank conservation makes u fixed at rank u. Since T is a consecutive
interval and u is outside it, the value on u is uniformly below all three
T values or uniformly above them, in the same direction as the wire
indices. Its P-comparison is therefore redundant and leaves u unchanged.
Its S-comparison is redundant for the same reason. Removing these two
comparisons leaves two matching layers on the three T wires. Some T wire
is idle in the first layer and hence has a forward cone of size at most
two through both layers. Every rank of T is attainable at that wire,
contradicting correct routing to all three output positions. QED.

This is a sorting obstruction beyond the exact two-layer reachability
criterion. It uses exact attainable sets and actual rank conservation;
it must not be asserted merely because an auxiliary overapproximation
variable chooses these endpoints. Conversely, an endpoint encoder may
soundly require an exact attainable vector to avoid this pattern, but a
looser interval assignment might widen a triple and evade the test.

## Actual prefixes and separating controls

The four-wire prefix

    03 | 13 | 23

has exact rank intervals [0,2],[0,2],[0,2],[3,3]. All 24 real input orders
verify this. It passes wire/rank degree four, saturated-four parity,
middle-pair, bridge, and exact two-layer reachability: P=02,13 followed by
S=01,23 gives every wire the four-position cone. Nevertheless the theorem
excludes a two-layer sorting completion. Direct replay of all 100 pairs
of four-wire matching layers independently corroborates the rejection.

A five-wire prefix is

    13 | 12 | 23 | 02,34 | 14,23.

All 120 input orders give exact intervals [0,2],[0,2],[0,2],[3,4],[3,4].
This also passes all the earlier interval checks and last-layer projection
(S=01,34), but fails even arbitrary-ending two-layer reachability: neither
outside wire is an eligible borrower. All 676 matching pairs corroborate
this. The four semantic demands consisting of the three full T rows and
the single demand from wire 3 to rank 4 already suffice; each one-demand
deletion has an explicit two-layer reachability witness in the checker.

These controls extend to widths 13,18, or larger as actual comparator
prefixes. Partition the positions into consecutive blocks, including a
three-block and singleton or larger blocks as desired. Sweep all
comparators between different blocks in a fixed order, repeating the
sweep n(n-1)/2 times. Any nontrivial comparison strictly decreases the
inversion count. If a sweep performs no swap, no cross-block inversion
remains; if it performs a swap, it consumes at least one of the at most
n(n-1)/2 inversions. Therefore the final state separates the blocks by
rank. Every input already ordered between blocks is fixed, so every rank
in each block remains attainable at every wire of that block. The exact
Q vector consists of the full block intervals.

For example, blocks 3+2+4+4 at width 13 pass the old degree, parity,
middle-pair, bridge, and last-layer projection tests, but have no fixed
borrower and fail two-layer reachability. Blocks 3+1+...+1 at widths 13
and 18 pass exact two-layer reachability by borrowing one singleton, yet
the sorting obstruction still rejects them. These are separating
prefix constructions, not depth-efficient D13/D18 cover closures.

The [independent checker](d13_feedback_round8_triples_verify.py) records
the real-order supports, deletion controls, and a finite audit of the
four-wire lemma. Enumeration corroborates the hand proofs; none is a SAT
premise and no complete D13 prefix case is closed by these controls.
