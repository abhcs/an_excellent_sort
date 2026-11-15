# Two real values and hand obstructions to shallow completion

**D(18) is still open in this work.** These results replace separate
comparison-count bounds by a condition tracking which pairs of positions
must interact. They give an exact characterization of sorting and short
certificates excluding particular prefixes. The missing step is a complete
argument covering all possible depth-ten networks on 18 channels.

The statements below are derived here from elementary comparator properties.
No claim of novelty relative to the entire literature is made. They apply
to every width, including widths greater than 18. Comparators are standard:
the smaller output goes to the smaller channel index.

The continuation [Contexts and exact two-layer completion](two-layer-context-proofs.md)
proves that this pair graph is exactly the graph of possible inversions,
adds induced-subgraph obstructions, and gives a complete context-sensitive
test for a specified prefix without using SAT. It also replaces the example's
20-run obstruction by an eight-run three-free-wire certificate, and records
an 18-wire counterexample to making that simpler obstruction universal.

## An exact two-value criterion

Put two arbitrary distinct finite values on two input channels, and assign
each other channel either negative or positive infinity. Until the finite
values meet in a comparator, their positions depend only on the infinity
signs, not on their relative order.

**Theorem 1.** A comparator network sorts if and only if every such signed
placement makes the two finite values meet in some comparator.

**Proof.** Necessity follows by swapping the finite input values. If they
never meet, they follow fixed routes to two different outputs; one of the
two input orders leaves them in the wrong order.

For sufficiency, take two binary inputs x,y of the same weight differing
only by exchanging a zero and a one. Mark these two positions as finite,
and replace their common zeros by negative infinities and common ones by
positive infinities. By hypothesis the finite values meet. At their first
comparison, the two runs become identical, and therefore have identical
outputs. Thresholding the extended values back to zero and one shows that
the original binary inputs have identical outputs as well.

The graph of weight-w binary inputs under these exchanges is connected.
Consequently all inputs of weight w have the same output. One such input
is already sorted and is fixed by every standard comparator. Their common
output is therefore sorted. Apply the zero-one principle. ∎

This is an equivalence, unlike the earlier necessary bounds on nine-real
restrictions. A proof of D(18)>=11 can therefore be phrased exactly as:

> Every ten-layer network on 18 channels admits a signed placement of two
> finite values which never meet.

The reformulation does not make that universal statement automatic.

It is constructive in the other direction too. Given a failing binary
input, exchange its misplaced ones with misplaced zeros until it becomes
the sorted input of the same weight. Somewhere along this path two
neighboring inputs have different network outputs. Mark their differing
positions as finite and use their common bits as infinity signs. The two
finite values cannot meet. This takes at most floor(n/2)+1 network
evaluations, with no SAT call.

## The pair graph of a prefix

Let U be the set of binary outputs of a prefix P. Define its **pair graph**
G(P) on the channel positions. Join i and j when two members of U differ
only at i,j, with the bits 01 and 10 in those positions. Each edge can be
witnessed by two explicit original inputs and their prefix outputs.

**Lemma 2.** For each weight, the corresponding members of U are connected
under these exchanges.

**Proof.** Connect their preimages by exchanges within the input weight
class. A comparator does not increase Hamming distance between equal-weight
binary vectors. Thus each step maps either to a repeated output or to an
exchange edge. The image of the path connects the two outputs. ∎

**Theorem 3.** A suffix sorts U if and only if, for every witnessed exchange
edge within U, its two marked positions meet when all other positions are
fixed to the signs specified by their common bits.

**Proof.** For any one edge, meeting is equivalent to the two binary runs
coalescing, as in Theorem 1. Necessity follows because sorted equal-weight
outputs are identical. For sufficiency, Lemma 2 makes all outputs of each
weight identical. Their class contains the already-sorted binary vector,
which the suffix fixes. ∎

Only a spanning tree of each weight class is needed for this equivalence.
Taking all edges is useful for detecting small structural obstructions.

**One-layer corollary.** P has a one-layer sorting completion if and only
if G(P) is a matching. The final layer must contain all its edges.

For one layer, two differing positions can coalesce only by being directly
compared. Conversely, comparing all graph edges coalesces each connected
weight class. This gives an exact last-layer test.

## Why the components are intervals

The next argument uses both monotonicity and preservation of the number
of ones. It also gives a direct route to the interval-block property used
in existing suffix arguments.

**Lemma 4, the plateau argument.** Let C be a component of G(P), and write
f_i(x) for the output bit on channel i. For every input of weight w,

$$\sum_{i\in C}f_i(x)=|C\cap\{n-w,\ldots,n-1\}|.$$

If the right side has the same value at weights w and w+1, every f_i with
i in C is constant across both of those input levels.

**Proof.** Within each weight class, Lemma 2 connects every output to the
sorted vector. Each exchange moves a one within a component of G(P), so
the component sum equals that of the sorted vector.

For neighboring inputs x<=y of weights w,w+1, monotonicity gives
f_i(x)<=f_i(y). If the component sums are equal, all these inequalities
are equalities. The inclusion graph between the two adjacent weight
levels is connected, so all f_i are constant on both levels. ∎

**Theorem 5.** Every component of G(P) is an interval of channel positions.
Each component already contains exactly its correct set of output ranks.

**Proof.** Suppose a component C has vertices on both sides of a missing
channel j. Put w=n-j-1. Its component sum does not change from w to w+1,
since the newly included channel of the sorted vector is j, outside C.
By Lemma 4, every channel of C below index j has bit zero on both levels,
and every channel of C above j has bit one on both levels.

Monotonicity extends the first conclusion to all weights at most w, and
the second to all weights at least w+1. Therefore no exchange edge inside
C can cross j: at the lower weights its left endpoint cannot change, and
at the higher weights its right endpoint cannot change. This contradicts
the connectedness of C.

For an interval component, the component-sum formula says that its bits
are precisely the appropriate segment of the sorted output, up to internal
order. Applying this at every threshold proves the rank assertion for
arbitrary distinct inputs. ∎

Comparators between different components can be deleted from any sorting
suffix: the values in the earlier interval are already all smaller, and
internal comparisons preserve that fact. The completion problem thus
splits into independent problems on the interval components, whose layers
can run in parallel. Every required graph edge must be connected inside
the suffix, so after deletion of redundant cross-component comparators,
these are exactly the suffix's connected blocks.

## Five possible partners in two layers

For a proposed suffix, temporarily allow either routing choice when one
marked value meets an infinity. This enlarges the set of possible meetings,
so impossibility in this relaxed routing model is a valid obstruction.

**Theorem 6.** If P has a two-layer sorting completion, every vertex of
G(P) has degree at most five.

**Proof.** Let the two layers be M,N and fix a starting wire u. In M its
marked value can meet at most its one partner. Otherwise it can leave M
on at most two wires. Each of those wires has at most one partner in N.
The value arriving at either N partner can have started on at most two
wires before M. Thus u can meet at most 1+2*2=5 different starting wires
in the two layers. Each graph neighbor is a required meeting. ∎

If u is unused in M, the same argument gives at most two possible partners.
Thus graph degree at least three forces u to be used in the penultimate
layer.

More generally, with k layers left,

$$\Delta(G(P))\le1+4+\cdots+4^{k-1}=\frac{4^k-1}{3}.$$

For a first meeting in layer t, u has at most 2^(t-1) possible arrival
wires. Each one's comparator partner has a backward cone containing at
most 2^(t-1) possible starting wires. Sum over the first meeting time.
The bounds for one, two and three remaining layers are 1, 5 and 21.

## A parity obstruction stronger than the degree bound

**Theorem 7.** Suppose a vertex u has five required neighbors. In every
two-layer completion, the six-element set

$$S_u=\{u\}\cup N_{G(P)}(u)$$

is partitioned into three pairs of the penultimate layer M.

**Proof.** To reach the upper bound of five partners in Theorem 6, u must
be paired with one required neighbor in M. Its other four required
neighbors must occupy two complete M-pairs, reached by the two possible
comparisons in N. Otherwise there would be at most four possible partners.
All six vertices are therefore paired within S_u. ∎

**Odd-intersection corollary.** If S_u and S_v have odd intersection,
P cannot have a two-layer sorting completion. Their intersection would
have to be partitioned into M-pairs, which is impossible.

More strongly, partition the wires by their membership in all such
six-element sets. Every nonempty membership cell must have even size,
because M preserves every set. This can detect contradictions not exposed
by any single pairwise intersection.

For example, K_{2,5} is a forbidden subgraph of G(P) for two-layer
completion. The two five-neighbor vertices give six-element sets whose
intersection consists of their five common neighbors.

These are hand proofs. They do not require the intermediate layers to be
maximal, and they do not restrict the completion to be symmetric.

## A path structure and planarity obstruction

The next deduction combines the pair graph with established last-layer
normal forms. For a sorting network with redundant comparators removed,
the last layer N consists of adjacent-channel comparisons; the preceding
layer M connects adjacent N-blocks. An N-block is a last-layer pair or an
unused singleton. These facts are Lemmas 3 and 9 of Codish, Cruz-Filipe and
Schneider-Kamp, [*Sorting Networks: the End Game*](https://arxiv.org/pdf/1411.6408).
Only these normal-form facts are imported here. The host-graph deduction
below is supplied explicitly.

Removing redundant comparisons preserves the function of the prefix and
therefore its pair graph. It is consequently legitimate when proving a
necessary condition for completion of a specified prefix.

**Theorem 8.** If a prefix P has a two-layer sorting completion, G(P) is a
subgraph of a disjoint union of graphs of the following form:

- partition the vertices into a line of bags, each of size one or two;
- join the two vertices of each two-vertex bag;
- join every vertex in one bag to every vertex in the next bag.

**Proof.** Take a nonredundant completion M,N. The union of two matchings
consists of alternating paths and even cycles. Contract the N-pairs. Each
remaining M-edge joins adjacent N-blocks in their channel order. Each
contracted vertex has degree at most two, counting parallel edges.
Consequently a cycle can only use two neighboring N-blocks, with parallel
M-edges: it is a four-cycle before contraction. Longer alternating cycles
are impossible.

Now contract M-pairs instead. Each original path becomes a path of bags
of size at most two; each four-cycle becomes two bags connected by two
parallel N-edges, which we treat as a single adjacency. Singleton paths
are allowed.

The two marked values can meet in M only when they start in the same bag.
They can meet in N only when they start in bags joined by an N-edge. If
we ignore the infinity signs, all pairs of vertices in two such bags are
potential meetings. Thus the relaxed collision host is exactly the graph
described above. Every edge of G(P) must be an edge of this host. ∎

**Consequences.** Every pair graph admitting a two-layer completion is
planar, has pathwidth at most three, and has bandwidth at most three under
some ordering of its vertices. In particular, a K5 or K3,3 subgraph (or a
subdivision of either) rules out completion. These are necessary conditions,
not sufficient conditions.

For bandwidth, list the bags in order. An edge spans at most three positions.
For pathwidth, use each union of two consecutive bags as a decomposition
bag; it has at most four vertices and the bags containing each vertex are
consecutive. The host is planar because each consecutive union is a clique
of size at most four, and successive cliques are attached along a vertex or
an edge. These attachments preserve planarity. Isolated bags cause no issue.

The same structure has useful metric consequences. If every two vertices
in a set S are at graph distance at most t, then

$$|S|\le 2t+2.$$

Indeed, any graph edge changes the bag index by at most one. The leftmost
and rightmost bags occupied by S can therefore differ by at most t,
and those t+1 bags contain at most 2t+2 vertices. Distances here are in
G(P); paths are allowed to leave S.

In particular, every radius-r ball has at most **4r+2 vertices**. With
two layers left, the bounds at radii one, two and three are **6, 10, 14**.
Also, a connected component on m vertices must have diameter at least
ceil(m/2)-1. These statements apply at every width.

A further cheap consequence is three-degeneracy: repeatedly removing a
vertex of degree at most three must remove the whole graph. In the host,
a vertex of an end bag has at most three neighbors; remove that bag and
continue. Every subgraph inherits this elimination property. Thus a
nonempty subgraph with minimum degree four is another obstruction.

There is also an edge-count bound, valid for n>=2:

$$|E(G(P))|\le\lfloor5n/2\rfloor-4.$$

To see this, connect the host's separate bag paths end to end; this only
adds edges. If it has p two-vertex bags and q singleton bags, with p>=1,
start from any two-vertex bag and grow the path in both directions.
The first bag contributes one edge, every other two-vertex bag at most
five, and every singleton at most two. The count is at most
5p+2q-4, which is at most floor(5(2p+q)/2)-4. If p=0, the host is a path
with n-1 edges and satisfies the same bound for n>=2. Hence an 18-channel
prefix with more than **41 required pairs** cannot be completed in two layers.

This improves on arbitrary two-layer routing: an alternating six-cycle
has collision host K6. That cycle can never be a nonredundant final suffix
of a sorting network. The distinction is why the normal-form hypothesis
is essential to the topology argument.

The verifier [two_layer_topology.py](two_layer_topology.py) checks every
normal-form suffix on two through eight channels: **2,559 suffixes**.
For each, it constructs the bag paths, independently computes the relaxed
collision host by routing, and checks the edge, bandwidth, degree-parity
and forbidden-subgraph conditions. A verified 18-channel sorting network
provides a positive control with a 41-edge host. The program detects K5
and K3,3 subgraphs directly; it does not yet test arbitrary subdivisions.
It also checks the radius-ball and three-degeneracy conditions.

For a concrete 18-channel application, the eight-layer prefix used below
has **12 required positions within distance two of wire 6**, exceeding the
bound of ten. [two-real-ball-certificate18.json](results/two-real-ball-certificate18.json)
contains a smaller witness: eleven positions, ten tree edges, and the
twenty binary runs witnessing those edges. Checking it needs neither SAT
nor exhaustive enumeration of all prefix outputs. This gives a second
hand obstruction for that prefix, using the last-layer normal forms.

These structural results hold for all n. They do not yet supply a universal
obstruction to eight-layer prefixes on 18 channels. An early 45-second
search found no prefix escaping both degree and parity. A later search
did find one, with 50 outputs: see the
[independent counterexample](results/degree-parity-counterexample18.json).
Thus those two tests alone cannot supply a universal lower-bound proof.
The newer [rank-profile and path-flow method](two-layer-capacity-proofs.md)
excludes that prefix and gives an exact two-layer completion criterion.

## An explicit 18-channel certificate

A bounded search produced an eight-layer prefix with 60 binary output
vectors and maximum pair-graph degree five. The degree bound alone does
not exclude it. The parity bound does:

$$S_4=\{0,1,2,3,4,6\},\qquad
  S_8=\{6,7,8,9,10,11\},\qquad S_4\cap S_8=\{6\}.$$

The penultimate partner of wire 6 would have to belong to both sets,
leaving only wire 6 itself. A comparator cannot join a wire to itself.
Therefore this prefix has **no two-layer sorting completion**.

[two-real-parity-certificate18.json](results/two-real-parity-certificate18.json)
contains the prefix and ten witnessed graph edges, five at each center.
Its independent certificate check uses only **20 explicit binary runs**;
it does not enumerate all prefix outputs or call a SAT solver. This is a
small certificate for one eight-layer prefix, not a resolution of an
entire two-layer case.

A separate SAT cross-check returned UNSAT on just 251 variables and 1,063
clauses. A known positive prefix with two layers remaining returned SAT,
and its resulting 18-wire network was checked on all 262,144 binary inputs.

## What the computation changed

The proposed raw comparison-budget lemma is false. An explicit ten-layer
network has at least 25 real-real comparators for **every** nine-real
restriction, yet fails to sort. Complete enumeration covers 710,828
normalized placements, with minimum exactly 25. A separate symbolic SAT
adversary also found no placement below 25. The compact witness and a
two-real failure certificate are in
[budget-counterexample18.json](results/budget-counterexample18.json).

There is a possible strengthening of the budget method: delete comparators
that never swap under the chosen restriction before applying the size lower
bound. On the counterexample's displayed minimum placement, comparisons
(8,10) in layer 9 and (9,10) in layer 10 never swap. Deleting them reduces
the retained size from 25 to 23. This was checked on all 512 assignments
to the nine real inputs; threshold commutation extends the redundancy
conclusion to arbitrary real values. The stronger condition excludes this
counterexample, but its sufficiency for a D(18) lower bound is unproved.

Moreover, the half-blind families from the preceding structural note have
common short completions for 79 of the 411 two-layer representatives.
After placing their common fixed infinities at the ends, the varying
part occupies at most 12 wires. Verified ten-wire or twelve-wire sorters
finish every such family within the depth budget. These partial-task
witnesses are generated and checked by
[coupled_family_witness.py](coupled_family_witness.py); they are not
18-wire sorting networks.

This is why pair interactions are the current target rather than raw
comparison counts or the half-blind family alone. To prove D(18)>=11,
we still need to exclude **every** possible eight-layer prefix, using
these obstructions, stronger graph constraints, or exact closure of the
remaining cases. The bounded search is not an enumeration of that space.

## Checks and current scope

[two_real_graph.py](two_real_graph.py) verifies the collision criterion,
interval components and exact one-layer test on all 1,196 networks of
depth at most three on three or four channels. It checks all 6,568 pairs
of matching layers on widths three through six, plus 500 sampled pairs
of layers on 18 channels and subgraphs of their possible-meeting graphs.
The proofs establish the general statements; these checks guard the
implementations and examples.

The two-real SAT formulation alone refuted depth five at width seven
in 0.71 seconds. A bounded attempt to find a nine-wire depth-seven sorter
with that formulation timed out after 20 seconds. This is a calibration
result, not evidence of a speedup over the existing exact encoder.

The full 18-wire cover still has zero resolved cases. Its only full
completion test timed out at 600 seconds. No full-cover SAT run is active.
