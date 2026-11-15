# Coupled restrictions for sorting network depth bounds

**D(18) remains unresolved.** The results below describe all ways to blind
the first two layers with half as many signed infinities as channels. They
give a distinction between widths 17 and 18, constraints coupling the
resulting smaller networks, and a general obstruction to extending the
argument by blindly deleting another layer. The theorems apply beyond
18 channels. No claim of novelty relative to all prior literature is made.

The preceding [transfer theorem and even-width barrier](../depth-hand-proofs/extension.md)
show why separate bounds on the sizes of the first two retained layers
cannot distinguish D(18) from D(17). Here we retain the positions and signs
of all restrictions and their evolution through a common suffix.

## The family of restrictions after two layers

Let P consist of two layers L1 and L2 on n channels, with L1 maximal.
Write p=floor(n/2) and r=ceil(n/2). Replace p inputs by fixed signed
infinities, leaving r arbitrary real values. A layer is **blind** if none
of its comparators compares two real values. Let F(P) be the set of
distinct signed states after L2 obtainable while both layers are blind.
Represent a state by a vector in {-1,0,+1}^n, where 0 means an arbitrary
real value. We count states of types, not assignments of the real values.

Every blind L1 comparator needs an infinity. Since there are exactly p
of each, every first-layer pair contains exactly one infinity and the
possible idle channel contains a real. After L1 the infinity is either
negative at the min endpoint or positive at the max endpoint. Thus all
initial placements reduce to 2^p choices after L1. There is no loss from
placing these normalized choices directly at the input.

The multigraph L1 union L2 consists of alternating paths and cycles.
A **stick** is a path on 2m vertices whose two endpoint channels are idle
in L2. A **head** is an odd path containing the unique possible channel
idle in L1. Cycles can include a repeated first-layer edge. Label each
vertex by its min or max role in L1.

Call a cycle **frozen** if every L2 edge joins two vertices with the same
L1 role. Otherwise call it flexible. Let c be the number of flexible
cycles, and let the sticks have sizes 2m1,...,2ms.

**Theorem 1.** Distinct states in F(P) have distinct sets of real positions,
and their exact number is

$$|F(P)|=2^c\prod_{i=1}^s(m_i+1).$$

**Proof.** The real vertices immediately after L1 form an independent set
of L1 union L2, containing one vertex of every L1 pair and the possible
idle L1 vertex. Analyze each component separately.

On a head, independence forces alternating choices starting at its real
idle vertex. There is exactly one choice.

On a stick, traverse the path starting with an L1 edge. Encode choosing
the left or right real vertex in consecutive L1 pairs by 0 or 1. An L2
edge forbids adjacent choices 10, so the possibilities are precisely

$$0^j1^{m-j},\qquad 0\le j\le m.$$

For 0<j<m the unique L2 edge at the transition contains two infinities;
every other L2 edge contains one real. Both idle endpoints are real.
Different interior j give different empty L2 edges. For j=0 or m, every
L2 edge contains one real and just one idle endpoint is real. Thus all
m+1 resulting real-position sets are distinct.

On a cycle the same exclusion holds cyclically, leaving just two choices,
the two alternating color classes. Each L2 edge has one real and one
infinity. If its endpoints have the same L1 role, either choice supplies
the same sign of infinity, giving the same signed output on that edge.
If the roles differ, one choice supplies a negative infinity and the
other a positive infinity, so the real outputs occupy opposite endpoints.
The two complete states therefore coincide exactly for frozen cycles.

Components are disjoint. Their choices multiply, and within each component
coincident real-position sets give the same signed state. This proves
both assertions. ∎

This includes the interior stick choices with a double-infinity comparator.
Counting only the two proper color classes would omit valid restrictions.

## The distinction at widths congruent to two modulo four

**Corollary 2.** For n=4q+2, every two-layer prefix with maximal L1 has at
least two states in F(P). The bound is sharp.

**Proof.** A stick contributes at least two states. If there are no sticks,
all components are cycles. In a frozen cycle with m first-layer edges,
let a and b count the min-min and max-max second-layer edges. Then
2a=m=2b, so m is even and the component has size divisible by four.
Consequently frozen cycles cannot alone cover 4q+2 vertices. At least
one cycle is flexible and contributes two states. Sharpness follows
from q frozen four-cycles and one isolated first-layer pair. ∎

By comparison, a 17-channel prefix can have a single state: take four
frozen four-cycles and an isolated L1 channel. This preserves information
lost in the earlier two-cap transfer theorem. It does not by itself
increase a depth bound: each smaller restriction must still be analyzed
inside the same larger network.

The prefixes with exactly two states at width 4q+2 have a particularly
simple classification:

* One isolated first-layer pair, with all remaining components frozen cycles.
* One flexible cycle of size congruent to two modulo four, with all
  remaining components frozen cycles.

For 18 channels, 51 of the 411 saturated representatives have exactly
two states. Five have the isolated pair; the other 46 have a flexible
cycle. If that cycle has h second-layer edges joining opposite L1 roles,
the two real sets differ by h deletions and h additions. Here h is odd:
writing a for the number of min-min edges gives m=2a+h with m odd.
The isolated-pair case has h=1. Enumeration gives:

| h | Intersection of the two nine-real sets | Representatives |
|---|---:|---:|
| 1 | 8 | 12 |
| 3 | 6 | 18 |
| 5 | 4 | 15 |
| 7 | 2 | 5 |
| 9 | 0 | 1 |

## Restrictions stay close through a common suffix

For a type state x, let R(x) be its set of real positions. For a layer M,
let e_M(R) count comparators of M with both endpoints in R. This is exactly
the number of comparators left in that layer after pruning the infinities.

**Lemma 3.** Applying any comparator layer to two type states cannot
increase their L1 distance. If both states have r real positions and

$$\|x-y\|_1\le2h,$$

then after any common suffix prefix they still satisfy

$$|R(x)\mathbin{\triangle}R(y)|\le2h.$$

For every next layer M, their retained comparator counts differ by at most h.

**Proof.** Sorting two pairs is nonexpansive:

$$|\min(a,b)-\min(c,d)|+|\max(a,b)-\max(c,d)|
 \le |a-c|+|b-d|.$$

If the pair orders agree this is equality; if they disagree the
uncrossing inequality for absolute distances proves the claim. Summing
over the disjoint comparators, including unchanged idle coordinates,
proves contraction for a layer and hence for any suffix.

Every position belonging to just one real set contributes at least one
to the L1 distance. Equal real counts make the symmetric difference even.
If two equal-size real sets differ by k exchanges, each exchanged vertex
can change the count of internal matching edges by at most one. Equivalently,
every edge counted only on one side uses a vertex exclusive to that side,
and each such vertex meets at most one edge. Thus the absolute difference
of comparator counts is at most k, which is at most h. ∎

**Theorem 4.** Order a stick's m+1 states as in Theorem 1, holding all
other components fixed. Neighboring states initially differ in exactly
one exchanged real position. Through every common later layer their
real sets remain distinct and differ by exactly one exchange. The numbers of
retained comparators in every corresponding later layer differ by at
most one.

**Proof.** Consecutive choices flip just one first-layer pair between
(-1,0) and (0,+1) at its min and max endpoints. In one direction the
whole state increases coordinatewise. The two runs have only the five
joint types (-1,-1), (-1,0), (0,0), (0,1), (1,1), in that coordinatewise
order. Every comparator sorts these types, preserving their multiset.
Exactly one (-1,0) and one (0,1) remain forever, so the real sets always
differ by one exchange. Apply Lemma 3 to bound the comparator counts. ∎

**Correction and extension.** An earlier version incorrectly said these
real sets could coincide and later separate. They cannot. More generally,
for any two normalized placements, the real-set distance never increases
and coalescence is permanent. The [exact transport theorem](sentinel-coupling-proofs.md)
proves this using seven joint types, identifies the comparisons that can
decrease the distance, and classifies the constraints in all 411 D(18)
prefix cases. It eliminates none of those cases by itself.

Multiple sticks give independent chains; the same bound holds when just
one chain coordinate changes by one step. This is a joint restriction on
the whole collection of retained layer-size profiles, which separate
small-sorter bounds do not express.

For the two-state cycle cases above, the signed distance after L2 is 2h:
same-role edges contribute zero and opposite-role edges contribute two.
Lemma 3 therefore gives a bound of h on the difference of comparator
counts in every later layer. In particular, the 12 cases with h=1 satisfy
the same one-exchange constraint as neighboring stick states.

There is also a useful exact description of an individual stick. If h
of its m-1 second-layer edges join opposite roles, the union of its
real-position sets has size m+1+h and their intersection is empty. Each
idle endpoint can hold a real, each same-role edge contributes one possible
real position, and each opposite-role edge contributes two. Every L2
edge is empty in one interior configuration, and each idle endpoint is
absent in one endpoint configuration. If h=0, the family is exactly all
m-element subsets of a fixed (m+1)-element set.

## A third layer can defeat every blind restriction

The preceding coupling result suggests studying partial comparison
profiles. A universal extension by another entirely blind layer fails
much more strongly than a single example would show.

Use the standard **saturated** two-layer representatives. The facts
needed here are that repeated-edge cycles are absent, a nontrivial stick
has at least six vertices, and an isolated first-layer pair can coexist
only with cycles. The complete-cover theorem and these normal forms are
from [Bundala et al., Theorem 6 and Corollary 5](https://arxiv.org/abs/1412.5302).

**Lemma 5.** A saturated two-layer prefix on 2p channels, p>=3, satisfies

$$|F(P)|\le2^{2p/3}.$$

**Proof.** Without an isolated first-layer pair, each stick uses m>=3
first-layer edges and contributes m+1<=4^(m/3). The inequality holds
at m=3 and its right-hand growth factor exceeds (m+2)/(m+1) for m>=3.
Each cycle uses m>=2 edges and contributes at most 2<=4^(m/3).
Multiplying gives 4^(p/3).

With an isolated pair, every remaining component is a cycle using at
least two first-layer edges. Hence the family size is at most
2^((p+1)/2)<=2^(2p/3) for p>=3. ∎

**Theorem 6.** For every saturated two-layer prefix on any even n>=18,
there exists a perfect third layer such that **no** placement of n/2
signed infinities blinds all three layers.

**Proof.** Put n=2p and choose a perfect matching uniformly. A fixed
p-element real set has no internal matching edge exactly when every edge
crosses between it and its complement. Of the (2p-1)!! matchings,
precisely p! cross. Thus this event has probability

$$\frac{p!}{(2p-1)!!}=\frac{2^p}{\binom{2p}{p}}.$$

The union bound and Lemma 5 show that the probability some state of F(P)
remains blind is at most

$$\frac{2^{5p/3}}{\binom{2p}{p}}.$$

At p=9 this is 32768/48620<1. The ratio of consecutive terms is

$$2^{5/3}\frac{p+1}{2(2p+1)}<1\qquad(p\ge9).$$

It remains below one for all larger p, so some matching defeats every
state simultaneously. The normalization in Theorem 1 covers every
possible initial signed placement. ∎

At n=18, the bound |F(P)|<=64 is attained by three six-vertex sticks.
There are 34,459,425 perfect matchings, and at most 64 times 9!, or
23,224,320, can leave any member blind. Therefore each saturated prefix
has at least **11,235,105** third layers defeating all its blind states.

The file [half-blind-obstructions18.json](results/half-blind-obstructions18.json)
contains one such third layer for each of the 411 prefixes. Every witness
was replayed against its complete family; no sampling trial needed more
than three attempts. These witnesses concern three-layer blinding, not
completion to a sorting network. They rule out universal three-layer
blinding with nine infinities, and therefore universal four-layer blinding
with those same infinities. They do not rule out arguments allowing some
real-real comparisons, other sentinel counts, or coupled restrictions.

## Verification and SAT status

The generator [two_layer_cover.py](two_layer_cover.py) reproduces all
48 raw, saturated and reflected class counts for n=3 through 18 in
Bundala et al. Its 18-channel cover has **411** representatives; quotienting
by reflection does not require a symmetric completion. The cover digest is
`3479c72a3dce2fe1d58d0fa80e11ccbdf9286c00b8585b1a15f23e325cb55ed2`.

[verify_two_layer_cover.py](verify_two_layer_cover.py) compares the
component enumeration with all labeled second-layer matchings through
n=10, checks the family formula on 13,228 labeled prefixes, and checks
348 small prefixes against every signed placement, independently of
normalization. It also checks every saturated representative through 18.

[verify_restriction_structure.py](verify_restriction_structure.py) checks
the local contraction inequality on all 81 ternary quadruples, all 526
stick components through 18, 167,800 successive transport steps under
sampled matchings, the family-size bound through 18, and all 411 explicit
third-layer witnesses. The proofs above establish the universal claims;
the finite checks audit their interpretation and implementation.

The exact completion runner passed both small controls: all 22 nine-wire
prefix cases are UNSAT at depth six, and a depth-seven sorter was found
and checked on all 512 binary inputs. The UNSAT results are solver-based;
there are no independently checked proof traces.

The one 18-wire test used 301,635 variables and 6,121,145 clauses. It
reached its 600-second wall-clock limit without SAT or UNSAT. Its
[audit](results/complete18-d10/audit.json) records one TIME_LIMIT and 410
NOT_SOLVED cases. This run has terminated. No 18-wire case in this complete
cover has been eliminated, and no depth-ten sorter has been found.

The subsequent [two-value hand proofs](two-real-hand-proofs.md) establish
an exact collision criterion, interval blocks, and a degree/parity
obstruction for two remaining layers. They also document short common
completions for 79 of these half-blind families. Thus those families alone
cannot settle their two-layer cases; the newer approach retains additional
pair interactions. No complete D(18) contradiction has yet been proved.
