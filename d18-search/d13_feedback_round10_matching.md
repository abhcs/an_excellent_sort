# Exact two-layer sorting is a mandatory-vertex matching problem

Let X be any family of binary vectors on n ordered wires. Each vector is
labelled by its actual number of zeros. P is a matching of standard
comparators, and S must be an adjacent matching. X need not be the image
of a prefix, need not contain sorted inputs, and need not contain all
inputs of a weight.

For every possible P mode at wire c (idle, minimum with a higher wire,
or maximum with a lower wire), evaluate its output bit on X. Call the
mode impossible if either:

1. Some k-zero input produces a wrong sorted bit at c outside k-1,k.
2. It produces zero on some input with k=c and one on some input with
   k=c+1.

Otherwise the mode is valid. The two events in item 2 are respectively
the LEFT and RIGHT requirements from the previous finite-state DP.
An empty family causes no requirements.

## Conservation eliminates the last matching

**Theorem.** P can be followed by one common adjacent S sorting every
vector of X if and only if every output mode selected by P is valid.

Necessity follows immediately: an away-from-boundary wrong bit cannot
be corrected by the final adjacent layer, and a wire cannot participate
in both its left and right final edges.

For sufficiency, put y=P(x) and let x have k zeros. Validity at every wire
fixes all y positions outside k-1,k to their sorted values. P conserves
weight, so the middle pair contains one zero and one one. If it is 10,
the same state therefore requests RIGHT at k-1 and LEFT at k. Every
required final edge is requested reciprocally at its two endpoints.

Take the union of these edges over X. If two of them overlapped, their
shared wire would have both a LEFT and a RIGHT requirement, contradicting
validity. Their union is thus an adjacent matching S. It corrects each
possible 10 middle pair. Every other edge of S compares equal already
correct bits for that input, so it does no harm. This S sorts all X. QED.

The conservation step is essential; independently invented endpoint
profiles need not have this property. For example, RIGHT at wires 0 and
1 and FREE at wire 2 contains no individually impossible profile, but
its required edges 01 and 12 conflict. Such profiles cannot come from
one weight-preserving P applied to a correctly weighted binary family
while satisfying all away-from-boundary conditions.

## Exact graph formulation

Construct a graph on the wires. An edge i-j is allowed precisely when
both output modes of that comparator are valid. Mark c mandatory when
its idle mode is impossible. Then

    a two-layer ending exists
    iff an allowed-edge matching covers every mandatory vertex.

The forward implication uses the theorem. Conversely, choose such a
matching P and leave all uncovered vertices idle. Every selected mode
is valid, including all uncovered idle modes, so the theorem constructs S.
Optional vertices need not be covered and P need not be perfect.

This is an exact graph condition, not just a cone bound. It admits short
hand certificates such as an isolated mandatory vertex, an independent
mandatory set with too few neighbors, or an odd allowed-edge component
all of whose vertices are mandatory. General weighted matching can also
decide it: give an allowed edge weight equal to its number of mandatory
endpoints and ask whether the maximum matching weight equals the number
of mandatory vertices.

There is also a direct reduction to perfect matching. Add every edge
between optional vertices. If n is odd, add one new dummy adjacent to
every optional vertex. A matching covering all mandatory vertices leaves
only optional vertices uncovered; their number has the parity of n, so
the added clique (and dummy, when needed) completes it to a perfect
matching. Conversely, remove added optional-optional and dummy edges
from a perfect matching to obtain an allowed matching still covering
every mandatory vertex. Thus an explicit Tutte deficiency in this
augmented graph is a hand certificate for the original ending problem.
This reduction does not assume that the allowed graph is bipartite.

For actual complete comparator-prefix images, the normal-form theorem
allows P to have span at most three. Then the earlier DP needs only its
fifteen crossing-P patterns; its extra S bit is unnecessary. For an
arbitrary binary family the graph theorem still permits arbitrary P,
but the span restriction need not be complete. The six-wire family of
all sorted inputs plus 100000 is sorted by P=05 and empty S, while a
span-three P followed by adjacent S cannot move the lone one far enough.

## Rank-width-two corollary for actual comparator prefixes

An actual comparator prefix has one-layer sorting completion if and only
if each exact attainable-rank interval Q(c) has width at most two.

The necessary direction is the final cone bound. For the converse,
intervals contain their own wire index, so in each cut permutation every
rank is displaced by at most one position. Such a permutation is a
product of disjoint adjacent swaps: inspecting its first nonfixed wire
forces a swap with the next wire, after which induction applies. If two
neighboring swaps occurred in different runs, their shared wire would
attain its predecessor, its own rank, and its successor, contradicting
width two. The union of all occurring swaps is therefore one matching
which sorts every cut permutation.

Thus the graph above can equivalently be computed from exact rank
intervals after each candidate P comparator: allow the edge when both
endpoint intervals have width at most two, and mark a wire mandatory
when its present interval has width greater than two. Disjoint P gates
do not affect each other's endpoint intervals. No exactness is needed
for a sound sufficient witness if enclosing intervals already have width
two, but a graph advertised as necessary and sufficient uses the actual
profiles or exact intervals.

For symbolic mode guards, write B for all away outputs being correct,
Lgood for all k=c outputs being one, and Rgood for all k=c+1 outputs
being zero. A selected mode need only require

    B AND (Lgood OR Rgood).

One-way guard implications suffice: a chosen valid mode can set its true
universal predicates, while a claimed true predicate is checked on every
relevant state. No final-edge variables, S-phase states, or last-layer
simulation variables are required.

## A four-wire obstruction beyond rank capacity and the triple rule

The actual four-wire prefix consisting only of comparator 01 has exact
intervals

    [0,2], [1,3], [0,3], [0,3].

It passes the width/rank-degree-four, parity, middle-pair, bridge, full
triple, and exact two-layer cone-capacity tests. For example P=02,13 and
S=01,23 give every wire the whole four-wire cone. Its allowed partner
graph is nevertheless empty, while every vertex is mandatory.

The following exact two-output interval table gives a small hand
certificate. Only the chosen comparator's two outputs are shown.

| Candidate P edge | Lower output interval | Higher output interval |
|---|---|---|
| 01 | [0,2] | [1,3] |
| 02 | [0,1] | [1,3] |
| 03 | [0,1] | [1,3] |
| 12 | [0,2] | [2,3] |
| 13 | [0,2] | [2,3] |
| 23 | [0,2] | [1,3] |

Every edge has an output of width at least three. To read the table
without enumerating all inputs, write the current values as
min(v0,v1), max(v0,v1), v2, v3. The minimum of three distinct inputs has
rank 0 or 1; the maximum has rank 2 or 3. The other listed min/max
expressions attain the three consecutive ranks shown by ordering their
three arguments appropriately. Repeating 01 does nothing.

This obstruction persists inside a rank-separated four-wire block at
any width; every comparator crossing its boundaries is redundant. Such
actual prefixes can be constructed by first partitioning the ranks into
consecutive blocks while fixing all block-ordered inputs, then applying
01 within the four-block. The cross-block sweep construction in the
[triple note](d13_feedback_round8_triples.md) provides one explicit method.
The block is even, so the earlier odd separated-block count alone does
not exclude it. These are separating controls, not new whole-cover
case exclusions.

The [checker](d13_feedback_round10_matching_verify.py) verifies the
conservation theorem directly against final-match enumeration, records
all real-order witnesses for the four-wire table, and checks the scope
counterexample. No SAT solver is used.
