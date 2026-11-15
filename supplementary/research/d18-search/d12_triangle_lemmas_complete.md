# An exact hand criterion for four triples

Let `F={T1,T2,T3,T4}` be four distinct three-element sets. A matching
hits `Ti` when one of its edges lies inside `Ti`. The vertices may be
part of a larger ambient set; outside vertices cannot help hit a triple.

**Theorem.** No matching hits all four triples if and only if all three
conditions below hold:

1. Their union has at most seven vertices.
2. No pair belongs to three or more triples.
3. For every pair `e` belonging to two triples, the other two triples
   minus `e` are two distinct two-element sets meeting in exactly
   one vertex.

Condition 3 is vacuous for a pair-linear family, meaning that no pair
appears twice. Thus four pair-linear triples are an obstruction
precisely when their union has at most seven vertices.

This criterion is a hand theorem about arbitrary four-triple families.
It does not depend on the enumeration of first matchings in the
twelve-wire problem, nor on the observed four templates.

## 1. Two elementary selection facts

First, **any three triples can be hit by a matching**. If a pair `e`
occurs in two of them, select `e`. The third triple is either already
hit or has at least two vertices outside `e`; pair those vertices.

Otherwise the three triples are pair-linear. Any two have a union of
at least five vertices, and all three have a union of at least six:
each of their three pairwise intersections has size at most one, so
inclusion-exclusion gives a union size at least `9-3=6`. Hall's theorem
with two copies of each triple therefore selects two different
vertices from each, with all six selections distinct. Pair the two
vertices selected from each triple.

The version of Hall used here is the following familiar form: a family
of sets admits two distinct representatives from each, all different,
if every subfamily of `k` sets has union size at least `2k`. To reduce
it to ordinary Hall, duplicate each set. Any collection of copies
coming from `k` original sets has at most `2k` members and union size
at least `2k`.

Second, **four distinct triples whose union has at least eight vertices
can be hit**. If every three have union size at least six, the same
two-copy Hall condition holds: one triple has three vertices, two
distinct triples have at least four, three have at least six, and all
four have at least eight. Choose four disjoint pairs.

Otherwise three triples have union size at most five. The fourth has
only three vertices, so the union of all four can reach eight only
when those three have exactly five vertices and the fourth is disjoint
from them. Hit the first three by the preceding fact, and add any pair
of the disjoint fourth triple.

## 2. Proof of the criterion

If condition 1 fails, the second selection fact supplies a hitting
matching.

If condition 2 fails, select a pair lying in at least three triples.
The remaining triple is either already hit or has two free vertices,
which can be paired.

Suppose condition 2 holds but condition 3 fails for a repeated pair
`e`. Select `e` to hit its two triples. Put `A=Tj minus e` and
`B=Tk minus e` for the other two. Both have size at least two.

* If `A` and `B` share a pair, choose that pair; together with `e`
  it hits all four triples.
* Otherwise their intersection has size at most one. Because
  condition 3 fails, their union has at least four vertices. Two
  sets of size at least two admit disjoint pairs exactly when their
  union has size at least four. Choose such pairs, one inside each.
  Together with `e` they again hit all four triples.

Conversely, assume all three conditions and suppose a matching hits
all four triples. A matching uses at most three edges inside their
union of at most seven vertices, so one of its edges must hit at
least two triples. By condition 2 it hits exactly two. Call that edge
`e`. The remaining triples, after deleting `e`, are two different
pairs sharing one vertex. No single edge lies inside both, and
selecting their two respective pairs would violate the matching
condition. The remaining triples therefore cannot both be hit.
This contradiction proves the theorem. □

As a useful positive control, the four triples on a four-element set
`abc,abd,acd,bcd` fail condition 3: after choosing `ab`, both residual
sets are the same pair `cd`. The matching `ab,cd` hits all four.

## 3. Finite corroboration

`d12_triangle_lemmas_allfour.py` enumerates all vertex-to-triple
incidence multisets. There are 666 when the four triples are labelled,
and 66 up to permutations of the triples and vertices. Exact matching
dynamic programming finds seven obstructed types, all on at most seven
vertices, each with a vertex-price certificate. The data are in
`results/d12_triangle_lemmas_allfour.json`.

The four observed twelve-wire templates form four of these seven
types. The other three are pair-linear families on six or seven
vertices, handled by the union-size bound. This finite classification
corroborates the general hand criterion; it is not a premise of its proof.
