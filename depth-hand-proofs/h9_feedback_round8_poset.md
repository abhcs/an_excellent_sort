# A nine-real poset obstruction with five layers remaining

The accepted H9 cases [03 16 47](h9_feedback_round6_031647.md) and
[03 16 57](h9_feedback_round7_031657.md) imply an image obstruction
that can be recognized at any cut of a wider network. Its application
requires a genuine signed restriction with **exactly nine real tracks**.
The bounded D18 check below found no new prefix exclusion.

## 1. Two forbidden product images

Let U be the five-coordinate poset on01236 with relations

```
0 < 3,   0 < 6,   1 < 6,   2 < 3.
```

There are no other relations except those implied by these; in
particular U has height two. On coordinates457 let F− be the
minimum-centered fork `4<5,4<7`, and let F+ be the maximum-centered
fork `4<7,5<7`. Coordinate8 is independent. Write P− and P+ for the
sets of all real vectors respecting respectively

```
U × F− × {8},       U × F+ × {8}.
```

The products mean that coordinates in distinct factors have no order
requirements. It is enough to consider distinct values; continuity
extends sorting statements to equal values.

**Poset obstruction.** Neither P− nor P+ can be sorted in five
comparator layers. The assertion remains true after any fixed
permutation of the nine coordinates, even if comparator orientations
and output labels are allowed to be arbitrary.

For the canonical coordinates, the two-layer networks

```
C−: 01 23 45 | 03 16 47,
C+: 01 23 45 | 03 16 57
```

have images exactly P− and P+. Necessity of the inequalities follows
from their comparisons. For sufficiency on the core, a target vector x
is obtained by placing `x0,x6,x2,x3,x1` at original positions0,1,2,3,6.
For F− put `x4,x5,x7` at4,5,7; for F+ put `x4,x7,x5` there.
Both constructions use only the specified inequalities. Coordinate8
is untouched.

A five-layer completion of either product, attached after the
corresponding C, would therefore sort all nine real inputs in seven
layers with that first two-layer prefix. The two accepted hand proofs
exclude precisely these networks. Thus each product requires at least
six further layers.

### Arbitrary relabeling and image containment

Suppose a comparator prefix A, on exactly nine reals, has an image
containing π(P−) or π(P+) for some fixed coordinate permutation π.
Any five-layer continuation sorting the entire image of A would sort
this contained product as well.

Relabel its input tracks by π inverse. This gives a network on the
canonical product with five layers of comparisons, possibly reversed,
and a fixed permutation of sorted output labels. Prepend C− or C+.
The resulting generalized network sorts every nine-real input up to
that fixed output permutation.

Untangle each reversed comparator through the whole remaining suffix:
reverse its orientation and swap its two labels in all later layers.
This preserves each layer's gate count and changes only a fixed final
output permutation. It leaves the canonical first two layers intact.
The now-ascending network therefore outputs `ρ(sort(x))` for a fixed
permutation ρ. On every strictly increasing input, all ascending gates
leave the input unchanged. Hence ρ fixes that vector and is the identity.
This produces the forbidden canonical seven-layer sorter.

This proves the containment version; equality of images is unnecessary.
The permutation must be uniform over the image, rather than chosen
separately for individual input orders. Global value reversal also
proves the statement for the dual of either product.

## 2. Lifting the obstruction to arbitrary ambient width

**Signed-cut theorem.** Fix any prefix of a comparator network on n
wires. Assign fixed signed infinities to n−9 original inputs and leave
exactly nine arbitrary real inputs. Suppose the set of reachable
nine-real vectors at the cut contains a fixed relabeling of P− or P+.
Then that prefix cannot extend to a sorting network using at most five
more layers.

The sentinel positions and the routes past them depend only on their
signs, not on real values. Prune every comparison involving a sentinel,
following the real tracks through its fixed routing. Each remaining
layer is a matching on the nine reals. Orientations or labels may
change, but the preceding relabeling/untangling argument permits this.
A full ambient sorter would sort the nine reals after this restriction,
contradicting the poset obstruction.

Equivalently, it suffices to exhibit a reachable family at the cut
with exactly nine free real coordinates and every other coordinate a
fixed signed sentinel, provided the required full product image is
contained in that family. Such a family must be proved reachable;
setting values at a cut is not itself an allowed input restriction.

**Scope caveat.** Nine selected coordinates inside a larger set of real
tracks are insufficient. Other ordinary values may take part in later
comparisons and increase the available routing resources. The theorem
requires that every outside coordinate has actually been fixed to a
signed sentinel uniformly over the family. It cannot be applied merely
by ignoring additional common real coordinates.

For a hypothetical depth-ten D18 sorter, this is a forbidden signed
nine-real image after five layers. It is distinct from the H9 strategy
that blinds three layers and then invokes the first-two-layer profile
on a seven-layer nine-real remainder. No claim is made that every D18
prefix admits either restriction.

## 3. A small component recognition criterion

A convenient sufficient criterion is an independent decomposition of
the pruned real-track interaction graph into components of sizes5,3,1.
All RR gates of a component stay within it; blind comparisons may move
its physical positions without affecting independence.

For the five-component, compute the image on permutations of its five
values. If it contains the sixteen U order types after a fixed relabeling,
and the three-component similarly contains the two order types of F−
or F+ after a fixed relabeling, the product image is contained. The
singleton is free. To realize any target vector, choose a preimage for
each component using that component's target values, and combine them.
The components do not interact, so these preimages are compatible.

Only5!=120 and3!=6 input orders are needed for this recognition check.
Comparison networks depend only on the relative order of their inputs,
so an order-type preimage works for arbitrary distinct real values.
The nine cut positions are recovered by the deterministic sentinel
routing; they need not be consecutive or in the original track order.
This criterion also allows each component image to be larger than the
specified poset image.

A coarser preliminary filter packs interaction components into bins of
sizes5,3,1. It may miss containments arising despite comparisons between
those prospective factors. Accordingly, failure of this filter is not
a proof that the general signed-cut theorem cannot apply.

## 4. Bounded recognition in three saved D18 five-prefixes

The input prefixes are the first five layers of the three records in
[the saved rank certificate](../d18-search/results/rank-layer-round6-hand-certificate.json).
The search fixes exactly nine signed sentinels and normalizes their
positions after the full first matching. It considers two families:

* no first-layer RR gate: each initial pair contains one real and one
  sentinel, giving2^9=512 normalized signed patterns;
* exactly one first-layer RR gate: choose its pair in9 ways, a different
  all-sentinel pair in8 ways, one of its three normalized sign patterns
  `--,-+,++`, and the seven remaining single-real patterns in2^7 ways.
  This gives27,648 patterns.

These families exhaust the normalized restrictions with zero or one
first-layer RR gate. They do not exhaust signed restrictions with two
or more first-layer RR gates.

For each pattern the scan traces the real-track gates through the five
layers and applies the component packing filter. In these prefixes
every survivor has exactly the component profile5+3+1:

| Prefix | Patterns tested | Packing survivors | Five-component image size | Three-component image size | Recognized obstruction |
|---|---:|---:|---:|---:|---:|
| beam00 | 28,160 | 64 | 4 | 2 | 0 |
| beam16 | 28,160 | 128 | 5 | 1 | 0 |
| beam32 | 28,160 | 64 | 3 | 2 | 0 |

All packing survivors have one first-layer RR gate. Each five-component
image is smaller than the required sixteen U orders, so no relabeling
can contain U. The beam16 fork images are also smaller than the two
required orders. This is a negative result for the stated cheap
component recognition test, not a complete search for poset-image
containment and not a new D18 exclusion.

## 5. Checks and provenance

The independent checker verifies both canonical component images,
their sixteen/two order counts, and two eighteen-wire positive controls.
Each control appends three blind routing comparisons after one of the
canonical two-layer prefixes; all nine auxiliary inputs are negative
sentinels. The resulting five-layer cut has nonconsecutive real tracks,
yet the recognizer recovers the same forbidden product.

It also replays the bounded normalized-pattern census and every
surviving small component image. The preceding two H9 certificates are
bound by their accepted SHA256 values; their proof sources are unchanged.
No solver is invoked, and no new H9 class is claimed by this extraction.

Files: [bounded discovery](verify/h9_feedback_round8_poset_probe.py),
[fixed checker](verify/h9_feedback_round8_poset_verify.py), and
[verification report](results/h9-feedback-round8-poset-proof.json).
