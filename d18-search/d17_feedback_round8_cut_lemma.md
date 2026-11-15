# A cut-budget lemma and a hand replacement for the deepest noncritical cases

**Hand results.** An incidence-distance inequality gives one reusable
obstruction for families of odd sentinel sets. Its four-state parity
corollary proves that the case-606 family cannot be covered when the
first matching contains the four gates

    A--b, B--q, C--E, c--e.                         (1)

This holds at arbitrary active width, with any number of common reals
and any physical embedding. It handles an arbitrary-size first matching,
and its proof is a nine-row explicit hand table after safe normalization.
All four cases that needed a second branch in round seven satisfy (1).
Their old search trees are no longer necessary for this branch.

**Finite compression.** The same inequality also replaces all 2,728
zero-full-row proof trees from round seven by witnesses on four to six
states, with radii only 0,1,2. A separate checker verified the resulting
29,038-byte certificate. The selection of such witnesses for all 2,728
first matchings is still finite verification; no fully symbolic
classification of that entire branch is claimed. The full family theorem
remains the finite-assisted result of
[round seven](d17_feedback_round7_reduction.md).

## 1. A boundary budget for odd sentinel sets

Let S1,...,Sm be sets of the same odd size 2t+1. A matching is supposed
to have t internal edges in every Si. Define the incidence signature
of a wire v by

    sigma(v) = (1[v in S1],...,1[v in Sm]),

and let d(u,v) be the Hamming distance of two such signatures. Suppose
nonnegative numbers r(v) satisfy

    r(v) <= |sigma(v)|,
    r(u)+r(v) <= d(u,v) for every pair u!=v.         (2)

Set every unlisted wire's radius to zero.

**Cut-budget lemma.** If sum_v r(v)>m, no matching can have t internal
edges in all the Si.

*Proof.* Complete a hypothetical matching to a perfect one, adding an
unused wire if the ambient width is odd. This cannot remove internal
edges. A new wire has zero incidence; the first condition in (2) is
exactly the distance inequality needed for edges incident to it.

Each odd set Si with t internal edges has exactly one edge crossing its
boundary. Summing these boundary counts over the m states gives

    sum_{uv in N} d(u,v) = m.

But (2), summed over the perfect matching, makes the left side at least
sum_v r(v)>m, a contradiction. This proof is independent of wire order,
ambient width, and the signs that produced the sentinel sets. ∎

This is equivalently a vertex-price bound. Let f(v)=|sigma(v)| and let
w(u,v) count the sets containing both endpoints. Then

    d(u,v)=f(u)+f(v)-2w(u,v).

The prices p(v)=(f(v)-r(v))/2 are nonnegative and satisfy
p(u)+p(v)>=w(u,v). Since sum_v f(v)=(2t+1)m, the inequality
sum r(v)>m gives sum p(v)<tm, below the demanded number of internal
edges counted across states. The cut formulation exposes a particularly
simple combinatorial special case.

**Unique-signature corollary.** It suffices to find m+1 wires whose
nonzero signatures occur only once among all wires and have pairwise
distance at least two. Give those wires radius one and every other
wire radius zero. Distances from an unselected wire are at least one
by uniqueness; distances between selected wires are at least two.

In particular, m+1 uniquely occurring nonzero signatures of the **same
parity** suffice: two distinct binary words of the same parity differ
in at least two positions. Thus four five-sentinel states are impossible
whenever five such wire signatures can be displayed. This corollary
requires no prices, matching enumeration, or case split on N.

## 2. The four-gate branch reduces by hand to nine residual forms

Use the case-606 notation

    G={AB,BC,CE,BD},     A-,B-,C+,D+,E+;
    B={qab,qbc,qce,rce,qbd},
    q-,a-,b-,c+,d+,e+,r+.

Assume M contains (1). These four disjoint gates use eight of the twelve
variable coordinates. The remaining four variables are

    D+, d+, a-, r+.

Their type functions obey a<=0<=D,d,r. The three positive coordinates
D,d,r are pairwise incomparable over the full twenty states. All common
reals are comparable with every coordinate.

Add comparators between comparable idle coordinates, using the hand
augmentation lemma. These additions preserve the four gates in (1).
The remaining idle coordinates form an antichain among D,d,a,r and the
common reals, of width three. At even active width there can consequently
be zero or two idles. A two-idle pair must be one of Dd,Dr,dr.

Now delete common-real M-pairs and apply the proved external-real
contraction whenever two remaining variables with common-real partners
are comparable. These operations preserve coverage and the deficit,
and preserve (1). The externally paired variables become an antichain
of even size, hence size zero or two, again drawn from D,d,r.

If M is perfect, the possibilities are the three pairings of D,d,a,r,
or a positive pair externally matched to common reals x,y while the
other positive coordinate pairs with a. These give six forms. If M has
two idles, those are a positive pair; the remaining a and positive
coordinate are comparable, so their external partners contract away
and they pair internally. These give three forms. This is a hand
exhaustion, independent of the 86,370-case list.

## 3. Four-state parity witnesses for all nine forms

For the following explicit table use physical label order

    D,A,B,C,E,d,a,b,c,q,e,r[,x,y].

The labels x,y are common real inputs. A common permutation and the
standard fixed output-swap argument give arbitrary physical embeddings.
Index states by i=5j+k, where the A rows j=0,1,2,3 are AB,BC,CE,BD and
the B columns k=0,1,2,3,4 are qab,qbc,qce,rce,qbd. The fixed four gates
(1) are present in every row of this table.

| Row | Additional gates | Idles | Required state indices | Five selected wires | Parity |
|---|---|---|---|---|---|
| 1 | Dd, ar | none | 5,6,10,15 | E,d,a,q,e | odd |
| 2 | Da, dr | none | 3,6,8,14 | C,E,q,e,r | odd |
| 3 | Dr, da | none | 3,6,10,15 | E,d,q,e,r | even |
| 4 | Dx, dy, ar | none | 5,6,10,15 | E,a,q,e,x | odd |
| 5 | Dx, ry, da | none | 5,6,10,15 | E,d,q,e,x | odd |
| 6 | dx, ry, Da | none | 5,6,11,16 | C,E,a,q,e | odd |
| 7 | ar | D,d | 0,1,3,7 | E,a,q,e,r | odd |
| 8 | da | D,r | 0,1,3,7 | E,d,q,e,r | odd |
| 9 | Da | d,r | 0,1,3,7 | A,E,q,e,r | odd |

The width-twelve rows have peak three. Every displayed state has only
two first-layer RR gates, except row 7/state 3, which has one. The three
width-fourteen rows 4--6 have peak four and exactly three first-layer RR
gates in each displayed state. Thus all four states in each table row
require their two SS pairs in N.

Here is the full incidence check. The rightmost bit refers to the first
listed state. The selected signatures are listed as sets; the other
nonzero signatures are a multiset. Every wire not listed has signature
0000.

| Table rows | Selected signatures | Other nonzero signatures |
|---|---|---|
| 1,4,5 | 0111,1000,1101,1011,0010 | 1111,1111,0100 |
| 2 | 1000,1110,0010,0111,1101 | 1011,1111,0101 |
| 3 | 0110,1100,1010,0011,1001 | 1111,1111,0100,0001 |
| 6 | 0100,0111,1000,1011,1110 | 0001,1111,1111 |
| 7,8 | 1000,0001,1011,1110,0100 | 0111,1111,0011,1100 |
| 9 | 0111,1000,1011,1110,0100 | 0001,1111,0011,1100 |

Each selected signature is nonzero, unique among all wires, and of the
displayed common parity. The unique-signature corollary gives a boundary
budget of at least five for four required states, a contradiction.
The tables can be checked directly by the four fixed comparisons and
the listed residual gates; no search over second matchings is involved.
For example, row 1's four transported sentinel sets are

    {A,B,E,a,q}, {A,B,E,q,e}, {A,B,C,E,a}, {A,B,d,a,q}.

Their selected E,d,a,q,e signatures are precisely those displayed above.

This proves the four-gate theorem at every even active width. For odd
active width, add one common real idle in both layers; the maximum
real-real count stays unchanged, so the even-width theorem applies.
Fixed auxiliary sentinels can be pruned by the existing hand lemma.

The small generator
[`d17_feedback_round8_spine.py`](d17_feedback_round8_spine.py) discovered
these choices. The independent
[`d17_feedback_round8_check.py`](d17_feedback_round8_check.py) reconstructs
the nine forms and all signed states without importing the generator,
replays the displayed first counts and all wire signatures, and checks
the four-variable order. Its
[nine-row report](results/d17-feedback-round8-spine-check.json) is VERIFIED.
This check corroborates the displayed hand exhaustion and tables; it is
not an exhaustive first-matching premise for the theorem.

## 4. A single inequality replaces all 2,728 partial-row proof trees

The remaining compression retains a finite first-matching selection.
For each of the 2,728 round-seven normal forms with no fully required
five-column A row, the new certificate identifies four to six required
states and nonnegative integer radii. Every radius is at most two,
and the radii sum to exactly m+1 for m selected states.

| Selected states | First-matching forms |
|---:|---:|
| 4 | 1,879 |
| 5 | 757 |
| 6 | 92 |

In 2,473 forms all nonzero radii are one, so the unique-signature
distance criterion suffices. The other 255 use one or two radius-two
wires. Every one of the former fifteen-way and three-way branches on
the final matching has been replaced by the same cut-budget inequality.

The discovery routine found prices through an integer symmetric-assignment
dual and then converted them to radii. That algorithm and its optimality
are **not proof premises**: the checker simply verifies (2) on every
pair of actual transported signatures and checks sum r=m+1. It also
checks that every selected state misses its first-layer peak, that no
full row was silently assumed, and that the certificate covers exactly
the accepted round-seven set of 2,728 partial-row forms.

The [compressed certificate](results/d17-feedback-round8-cut-certificate.json.gz)
is 29,038 bytes. Its SHA-256 is
`f77b8e62c42fe92d3480abc3de812703be0287a61440f452b2de937409c0630a`.
The [independent report](results/d17-feedback-round8-cut-check.json) is
VERIFIED. Generation completed in 3.25 seconds; the combined radius and
nine-table checks completed in 0.253 seconds. Both ran under separate
thirty-second limits and are terminal. Their
[generation record](results/d17-feedback-round8-cut-generation-terminal.json)
and [checking record](results/d17-feedback-round8-check-terminal.json)
are saved. No SAT or external optimization solver was used.

## 5. Exact scope of the compression

The cut-budget and unique-signature lemmas are general hand results for
odd sentinel sets and arbitrary ambient width. The four-gate branch
(1), including all four former depth-two cases, now has its own hand
normalization and explicit nine-row proof independent of the large
finite classification.

For the full 2,728-case partial-row branch, finding a suitable small
family and radii remains a finite choice. The broad symbolic gap is to
prove from the first matching's structure that such separated incidence
signatures must exist, without choosing witnesses separately for each
normal form. The present certificate makes that target concrete and
removes final-matching branching, but does not supply that universal
selection theorem. The full-row portion of round seven also retains its
finite selection of conflicting cores or boundary contradictions.

Thus the accepted full case-606 family obstruction remains finite-assisted.
No D17 complete-cover count changes, and no global D17/D18 claim is made.
All round-eight discovery and checking processes are terminal.
