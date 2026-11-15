# A nine-real component obstruction four layers before the end

The later [three-component theorem](three-component-obstruction.md)
strengthens this to **at most two components**, now entirely by hand.
The earlier size result and its original sample observations are preserved
below.

**Structural consequence.** Fix any signed-sentinel restriction leaving
nine real inputs in a hypothetical depth-d sorter. Form the interaction
graph of those real tracks through the first d-4 layers. **At least one
connected component has five or more real tracks.** The components need
not themselves be sorted.

This follows from the new hand lower bounds for merging
[four, three and two sorted values](../depth-hand-proofs/h9_feedback_round2_merge432.md)
and [three sorted triples](../depth-hand-proofs/h9_feedback_round3_merge333.md),
together with the [four-four-one merger theorem](d13_feedback_round3_merger441.md).
All three need at least five merger layers. Their proofs use small hand
lower bounds and dependency cones; no SAT result is a premise.

## Proof of the component transfer

A real track is a logical register, rather than the identity of the
particular value currently occupying it. Comparators meeting a signed
infinity have predetermined routing. Delete those comparisons and carry
the real-register labels through their fixed swaps. Every retained
real-real comparison joins its two register labels in the interaction
graph.

Suppose all its components have size at most four. The packing argument
below places them in three blocks of one of the specified sizes.
Prune the whole hypothetical sorter to the nine real inputs. Relabel
the registers so the proposed blocks are consecutive, then untangle
the whole pruned network into ascending comparisons. Untangling changes
labels within interaction components; it does not create a comparison
between components before the cut. The pruned network remains a sorter.

Every input already sorted within each of the three blocks is fixed by
the prefix: each prefix comparison is internal to a block. These inputs
therefore belong to the prefix image, whether or not the prefix sorts
arbitrary inputs within its components. Its last four layers would have
to merge those three independently sorted blocks. The corresponding merger theorem
contradicts this. This proves the transfer. The argument applies at any
ambient width n>=9 and any cut with four layers left.

## Recognizing component sizes

Every component-size partition of nine with largest part at most four
fits one of (4,3,2), (3,3,3), and (4,4,1).

To see this without a search, suppose a component has size four. The
remaining five vertices can be split into sizes three and two unless
their components have sizes four and one; that gives (4,4,1) directly.
If there is no size-four
component but at least two triples, three triples fit (3,3,3); otherwise
the remaining components have sizes (2,1) or (1,1,1) and fit (4,3,2).
With exactly one triple, the remaining sizes are ones and twos summing
to six and can be split into four and two. With only ones and twos,
the odd total supplies a singleton: form a group of three, then split
the remaining six into four and two.

The (4,4,1) theorem has a particularly short proof. A sorted triple and
two singletons need four merger layers: either the singletons first
compare with each other, leaving an impossible two-layer (3,2) merger,
or sentinels on their two triple partners blind the first layer and
leave a forbidden two-layer sorter on three reals. In a proposed
four-layer (4,4,1) merger, the singleton must first meet one four-block.
Keeping each other vertex of that block with the singleton and either
consecutive triple of the opposite block forces three different
partners into that opposite block's two middle vertices. This is
impossible. The linked note gives the details, including the cone bounds.

For D13>=9 the relevant cut is after layer4 in a hypothetical depth8
sorter. For D18>=11 it is after layer6 in a hypothetical depth10 sorter.
Thus this tests restrictions with many retained comparisons; blinding
all early layers is not required.

## Bounded D18 observations

[merge_component_states.cpp](merge_component_states.cpp) enumerates
normalized first-layer type placements leaving nine reals. It tracks
the components directly. In `max4` mode it stops a placement when a
component reaches five vertices, since subsequent unions cannot shrink
it. The earlier `432` and `both` modes are retained to reproduce tests
made before all three merger lemmas were available.

The [strengthened audit](results/merge-component18-max4-initial.json) tests six
specified six-layer prefixes: the three earlier combined/cube/budget
candidates, and beam rows0,16,32 with their previously retained candidate
sixth matchings. Each has710,828 normalized placements. None has a
restriction meeting this component criterion. These are samples, not a
complete cover; no D18 prefix is newly excluded here.

At layer5, beam rows0,16,32 have respectively640,9,936,64 qualifying
placements, represented by6,20,2 distinct partitions of physical real
positions. Their recorded sixth matchings all create a component of
size at least five in every such restriction. This explains why the
criterion does not eliminate their existing sixth-layer candidates.

For a fixed restriction at a cut one layer earlier, each packing into
one of the forbidden block shapes gives a simple necessary clause:
the next matching must contain a real-real comparator crossing two of
those blocks. Otherwise the packing survives into the forbidden cut.
All packings must be considered. This is a way to add the new hand
lemma to a synthesis formula; no speedup is claimed here.

## Independent controls

[merge_component_verify.py](merge_component_verify.py) independently
builds graphs using adjacency sets and tests bin packing recursively.
It checks108 small prefix/mode combinations against all8,676 signed
assignments leaving nine reals, and checks all30 integer partitions
of nine. Direct comparison of the original and pruned computations
passes68,608 binary functional replays.

A planted prefix consisting of independent (4,3,2) block computations
has qualifying restrictions. A genuine depth11 eighteen-wire sorter
is checked on all262,144 binary inputs; its cut after layer7 has no
qualifying restriction, as required when four layers remain. The
[control manifest](results/merge-component-verification.json) records
source digests and scope. The controls corroborate the collector;
the mathematical implication is the component-transfer proof above.
