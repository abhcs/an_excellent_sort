# Rank-separated blocks cannot borrow wires from their neighbors

Let C be an actual comparator prefix on ordered wires0,...,n−1.
Write Q(c) for its exact attainable-rank interval at wire c. A boundary
b is separated when every output of C places ranks0,...,b−1 on the
first b wires. Equivalently,

    hi(c)<b for every c<b,

or, by rank conservation, lo(c)>=b for every c>=b.

## Suffix separation theorem

Every comparator crossing a separated boundary is redundant, throughout
every subsequent comparator suffix. Delete all such comparators. The
remaining suffix acts independently on the consecutive blocks between
separated boundaries, with no increase in depth.

Indeed, initially every value on the left is below every value on the
right. A comparison within either side preserves this property, and a
crossing comparison already has its smaller value on its lower wire.
Induction through the suffix proves both redundancy and persistence.
This statement requires no optimality or last-layer normal form.

Consequently, if an actual prefix has Q(c) contained in a consecutive
block I for every c in I, then both boundaries of I are separated.
Each run uses all ranks of I exactly once in I. Outsiders cannot contain
an I rank. Since their attainable sets are intervals containing their
own indices, every wire left of I stays below I and every wire right
of I stays above I. Thus no sorting completion can use an outside wire
to help this block.

## An odd-block obstruction at any remaining depth

Suppose d>=1 layers remain and I is a rank-separated block. Call a
wire c mandatory if |Q(c)|>2^(d−1). The first remaining layer must
compare every mandatory wire to another wire of I: an idle wire has
at most2^(d−1) reachable outputs in the other d−1 layers, and all
cross-block comparisons can be removed.

Therefore every odd separated block contains at least one wire with

    |Q(c)| <= 2^(d−1).

In particular, three wires with the same exact three-rank interval
cannot be sorted in two more layers. This gives a shorter proof of
the [full-three-rank sorting obstruction](d13_feedback_round8_triples.md).
More generally, an odd separated block of size m>2^(d−1), with Q(c)=I
on every wire of I, cannot be sorted in d more layers. This conclusion
does not assume that every permutation of I occurs at the cut.

The [threshold-partner lemma](../depth-hand-proofs/h9_feedback_round5_rank_partner.md)
strengthens the same argument. Compute its necessary partner graph
using any fixed bank of real inputs, then remove edges crossing a
separated boundary. A required matching must cover every mandatory
vertex inside its own block. In particular an independent set of
mandatory vertices with fewer neighbors than vertices is impossible.
The odd-block argument is the simplest matching obstruction.

## Consequence for the exact two-layer capacity formulation

When two layers remain, a final matching may be chosen adjacent after
the usual removal of redundant gates. It must also respect every
separated boundary b: its edge(b−1,b) is absent. For endpoint variables
U[c,b]=(hi(c)<b), this is the conditional clause

    not e[b−1] OR not U[0,b] OR ... OR not U[b−1,b].

The symmetric clause uses L[c,b]=(lo(c)>=b) for c>=b. These clauses
remain sound with enclosing endpoint intervals: enclosure wholly on
one side still proves actual separation. Exact endpoints prevent an
artificially widened assignment from concealing a separated boundary.

Combining these clauses with the exact fixed-final-matching block
capacity criterion automatically excludes a full three-rank block.
There can be no last edge crossing its two boundaries. If a preceding
matching edge crossed either boundary, both its source demands already
fit their own final blocks, so that edge could be removed without
losing a required path. A matching on the three remaining wires has
an idle vertex, whose two-layer cone has size at most two.

These are general necessary conditions and local hand tools. They do
not close a complete D13, D17, or D18 cover case on their own.
