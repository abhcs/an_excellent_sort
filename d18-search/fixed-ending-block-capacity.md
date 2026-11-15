# Exact capacity test for the matching before a fixed last layer

Fix a last matching S on n positions. Its blocks are its two-element
edges and its idle singleton positions. For each wire c before the last
two layers, let R_c be a required rank set containing c; it may be an
attainable interval or any smaller set of witnessed ranks.

There exists a preceding matching P whose forward cone through P,S
contains every R_c if and only if the following conditions hold.

1. Each R_c meets at most two S-blocks.
2. Define a wire to be free if R_c is contained in its own block. Otherwise
   it demands the unique other block met by R_c. Let k_BC count the wires
   in block B demanding block C, and let f_C count free wires in C. Then
   for every block C,

   sum over B != C of max(0, k_BC - k_CB) <= f_C.

The blocks may be nonadjacent, and neither P nor S must be perfect. The
criterion is exact for required-set reachability; it does not assert
that P,S sort the prefix's data.

## Proof

A forward cone through P,S is the union of the wire's own S-block and
its P-partner's S-block. Thus a wire whose required set meets three
blocks is impossible. A wire demanding C must have a partner in C.

If such a partner is itself demanding rather than free, it must demand
the first wire's block B. At most min(k_BC,k_CB) demands from B to C
can be paired this way. Every remaining demand from B to C must consume
a distinct free vertex of C. Summing these unavoidable demands proves
the displayed capacity inequality.

Conversely, for each unordered pair of blocks B,C, match as many of
the reciprocal demands as possible: min(k_BC,k_CB). The chosen vertices
for different pairs are disjoint, since a nonfree vertex has exactly
one target block. The remaining demands into C number exactly the sum
in the inequality. Match them injectively to distinct free vertices of
C, which is possible by the inequality. These operations never reuse a
vertex: each remaining demanding vertex is one source, and every
chosen free vertex is one destination. Leave other vertices idle.

Every demanded wire is now partnered into its target block, and every
free wire already has its required set in its own block. All required
sets are contained in their forward cones. This constructs P and proves
sufficiency. □

## Relation to the earlier obstructions

For the six-wire shared-middle-pair example, use S=01 23 45 and required
sets [0,3],[0,3],[0,2],[3,4],[2,5],[4,5]. Blocks A=01 and C=45 send
respectively two and one demands into B=23. B sends one back to each,
leaving one excess demand into B but f_B=0. Its capacity inequality
fails. This is the same three-into-two partner obstruction, expressed
without enumerating P.

For adjacent S and contiguous intervals R_c, every demanding wire targets
one of the two neighboring S-blocks. The same inequalities are therefore
local along the block order. Combined with the
[final-matching projection theorem](d13_feedback_round7_pairing.md),
they separate two issues: which last pairings can meet every rank interval,
and which of those pairings admit a common preceding matching.
The projection theorem alone does not promise that its adjacent pairing
preserves preceding-layer feasibility. No such inference is made here.

The [independent finite control](fixed_ending_block_capacity_verify.py)
compares the criterion with direct enumeration of P for every interval
vector on four positions and every S, then for deterministic samples on
six positions. It also checks the six-wire capacity contradiction above.
These checks corroborate the proof; they are not its premise.


## Linear local test when the last pairs are adjacent

For an adjacent S, list its blocks in position order. A contiguous required
interval can demand only a neighboring block: demanding a farther block
would meet at least three blocks. For block B let L(B), R(B), F(B) count
its wires demanding its left neighbor, its right neighbor, or neither.
No wire may demand both neighbors. For consecutive blocks A,B,C, the
capacity criterion reduces to

    max(0, R(A)-L(B)) + max(0, L(C)-R(B)) <= F(B).

Missing end neighbors have zero demand. In addition, every interval at a
wire of B must lie inside A union B when it extends left, or B union C
when it extends right. Thus all conditions for B depend only on three
consecutive blocks, each of length one or two.

It follows that existence of an adjacent S and a common P can be decided
in linear time in n for a fixed interval vector. Tile the positions by
blocks of lengths one or two. A dynamic program remembers the last two
block lengths and the current endpoint; appending the next block checks
the middle block's inequalities and interval containment. There are at
most four nonboundary states at each endpoint and two transitions per
state. Flush the final block with a missing right neighbor. A surviving
tiling gives S, and reciprocal cancellation constructs P as in the proof.
This is an exact decision procedure for two-layer rank-set reachability
with an adjacent last matching, not for sorting the full data family.


[adjacent_rank_ending.py](adjacent_rank_ending.py) implements this linear
DP and constructs both matchings for any accepted interval vector. Its
[direct-cone verifier](adjacent_rank_ending_verify.py) compares against
all matching pairs for all 576 four-wire interval vectors and 5,000
six-wire samples. It rejects the middle-pair and bridge examples and
accepts the actual cut intervals of the known eighteen-wire sorter.
