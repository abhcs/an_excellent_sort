# Structural reductions: all four-gate and perfect first matchings

**Result.** The twelve-wire case-607 family cannot be covered by two
matching layers when the first matching has four or six gates. These
are hand arguments, using the safe-image and folded-fork lemmas in
`d17_hand_defects_twelve_cross.md`. The five-gate case is completed in
`d17_hand_defects_twelve_five.md`. Together these notes give a complete
hand proof of this particular twelve-wire obstruction, covering every
first-matching size. No full D17 lower bound is claimed here.

The six-gate argument was proposed by the root agent and independently
checked here. The four-gate argument and local classifications below
were developed here. The verifier checks only small local identities and
classifications; it does not repeat the complete first-matching scan.

## 1. Labels, counts and safe normalization

Use abstract A labels

    a=3-, b=4-, c=5+, d=2+, e=6+

in the compact twelve-wire indexing. The sentinel-pair graph is the fork

    G={ab,bc,ce,bd}.

The B vertices are compact indices 7,...,11: two have minus sign and
three have plus sign. The other two wires are always real. A state has
two sentinels on a G-edge and one sentinel at an arbitrary B vertex.
Every state has nine real wires. The complete signed states and index
map are in `results/d17-feedback-twelve-states.json`.

Write M for the first matching, N for the second, m=|M|, and S for the
three sentinel positions. If u is the number of idle sentinel wires and
s is the number of M-edges joining two sentinels, then

    e_M(R)=m-3+u+s.                                  (1)

Indeed, the three sentinels hit exactly 3-u-s matching edges.

We may fill N to a perfect matching: this only adds retained gates and
there is no subsequent transport to preserve. For perfect N, (1) gives

    e_N(R)=3+s_N,

so N peaks exactly when it pairs two vertices of the transported sentinel
triple. We refer to this as hitting that triple.

There is a second safe augmentation: if an N-edge joins two wires idle
in M, add that edge to M. First retained counts can only increase.
Sorting those two types does not change whether both are real, so the
retained count in their N-edge is unchanged; all other N-edges are
disjoint from them and unchanged. This holds simultaneously for every
state. Iterating leaves the M-idle set independent in N and hence of
size at most six. Thus m>=3 may be assumed by this normalization alone.

In the union of normalized M and perfect N, the components are repeated
edges, alternating even cycles, and alternating paths with N-edges at
both ends and at least four vertices. If p is the number of path
components, m=6-p. This supplies a topology reduction without filling M.
Arbitrarily adding edges to M is not a safe operation.

## 2. Singleton transport and image lemmas

Let f(v) be the destination of a lone sentinel at v under M: the low
endpoint for minus, the high endpoint for plus, and v if idle. Two
different vertices can have the same image only if they are the two
endpoints of a same-sign M-edge.

Let C be the number of A-B gates, B_s the number of same-sign B-B gates,
and z the number of idle B vertices. A basic safe B choice is one not
paired to A. The numbers of distinct safe images and distinct used safe
images are respectively

    t=5-C-B_s,                 t_used=5-C-B_s-z.       (2)

Their images lie outside all A images. For a G-edge uv outside M and a
safe B choice w, the transported sentinel triple is exactly
{f(u),f(v),f(w)}.

We use two proved facts from the companion cross-edge note:

* A graph H whose edge triples {u,v,p} and {u,v,q} are all hit by one
  matching, for two distinct common positions p,q outside H, must itself
  be a matching.
* The folded graph of G-edges outside M is never a matching.

Three distinct third positions force the particular edge uv into N:
without uv, the two endpoints u,v can each have only one N-partner.

An opposite-sign A-B gate also gives a safe singleton image on its B
endpoint: the two singleton images are distinct, even when both
endpoints are sentinels. Its first-layer peak possibilities must still
be checked separately. We do not count it as a basic safe choice in (2).

## 3. One full column and a cross gate

Suppose there are no A-A gates, so f is injective on A. Relabel its five
images as a,b,c,d,e. Suppose a position p outside A gives all four
required triples {u,v,p}, uv in G.

**Full-column forcing.** N must contain pb and ce.

*Proof.* If p is not paired to an A vertex, every G-edge would have to
be an N-edge. If p is paired to x in A, every G-edge not incident to x
must be an N-edge. The fork after removing the star at x is a matching
only for x=b. The remaining edge is ce. Thus pb and ce are forced.

Now suppose an A-B gate has A endpoint x!=b, and all states formed from
its B endpoint and G-edges not incident to x require a peak in N.

**Cross-gate contradiction.** Those requirements are inconsistent with
the full column, regardless of the signs of the cross gate.

*Same signs.* The B singleton image is x. For x=a or d choose the row
bc; for x=c or e choose the row ab. The resulting triple of A images
cannot contain an N-edge: two of its vertices already have partners
outside the triple, by pb and ce.

*Opposite signs.* Its B image q lies outside A and differs from p. For
x=a, the rows bc and bd would require q to pair with both c and d; for
x=d, use ab and bc; for x=c, use ab and bd; for x=e, use ab and bc.
These choices are incompatible with matching, and sometimes already
contradict the forced edge ce. The respective rows are all disjoint
from x, as required. The exceptional central endpoint x=b is deliberately
excluded: its only nonincident row ce is already hit.

## 4. Deleting an idle fork edge

Let E0 be a fork edge whose two endpoints are idle in M. Suppose the
other three A vertices contain at most one A-A gate P. Remove E0 and
any G-edge equal to P, then fold the remaining edges by f. The resulting
graph is not a matching.

If P is absent or has opposite signs, folding is injective on A. The
only opposite-sign fork edge disjoint from another fork edge is P=bd,
E0=ce; its two surviving edges ab,bc still meet. In all other injective
cases, G-E0 already contains two incident edges.

For a same-sign P, the following table gives two surviving incident edges
after identifying the endpoints of P. Identified letters denote the
same image; every displayed pair consists of distinct edges.

| P | E0 | Incident surviving edges |
|---|---|---|
| ab | ce | bc,bd |
| ce | ab | bc,bd |
| ce | bd | ab,bc |
| cd | ab | bc,ce |
| de | ab | bc,cd |
| de | bc | ab,bd |

These are all possibilities: a,b are the minus vertices and c,d,e are
the plus vertices, while P must be disjoint from E0. This is a small
signed-fork classification, not an enumeration of twelve-wire matchings.

## 5. Every four-gate first matching fails

For m=4, equation (1) shows that a peak is possible only when all three
sentinels are idle. To see this without arithmetic cases, all four gates
must be real-real. Consequently at most two of the twenty states can
peak: four idle vertices can contain either an A-edge and two B choices,
or at most two A-edges and one B choice.

### No first peaks

All twenty states require N. If t>=2, the two-image and folded-fork
lemmas give a contradiction. Otherwise t=1, and C+B_s=4. Since
C+2B_s<=5, the only possibilities are (C,B_s)=(3,1) and (4,0).
All four M-gates are accounted for by these types, so there are no A-A
gates. A safe column forces pb and ce. Among at least three cross gates
there is one at a noncentral A vertex; its nonincident rows all need N.
Section 3 gives a contradiction.

### At least one first peak, with exactly two idle A vertices

The idle A pair must be a G-edge E0. There are at least one and at most
two idle B vertices. Since at most three A vertices are used and at
most four B vertices are used, C<=3 and C+2B_s<=4; hence C+B_s<=3 and
t>=2.

Choose two distinct safe B images. Every G-edge except E0 and any A-A
gate requires N for both choices: that row has a used A sentinel, so
cannot put all three sentinels on idle wires. There is at most one A-A
gate, disjoint from E0. Section 4 says the required folded graph is not
a matching, contradicting the two-image lemma.

### At least one first peak, with three idle A vertices

There is exactly one idle B vertex and both always-real wires are used.
If t_used>=2, two used safe choices make every G-edge outside M require
N, contradicting the folded-fork lemma.

Otherwise C+B_s>=3. Only two A vertices and four B vertices are used, so
C<=2 and C+2B_s<=4. Necessarily C=2, B_s=1. The four gates are two A-B
gates, one same-sign B-B gate, and the gate between the always-real
wires. There are no A-A gates. The used safe B image supplies a full
required column, so Section 3 forces pb and ce. One of the two cross
gates has noncentral A endpoint. Its B sentinel is used, so none of its
nonincident rows can peak in a four-gate M. Section 3 again contradicts
N. This exhausts the possibilities for four idle wires. ∎

## 6. Every perfect first matching fails

For m=6, a first peak is equivalent to an M-edge inside the sentinel
triple. Fix a G-row uv outside M. Exclude only the B choices paired by M
to u or v. Every remaining triple has no internal M-edge, so requires N.

The five B singleton images have exactly B_s identifications. Excluding
the at most two specified B vertices leaves at least 5-B_s-2 distinct
third images outside {f(u),f(v)}. These states transport exactly by f.
If B_s=0, three third images force every folded G-edge into N, which the
folded-fork lemma forbids.

If t>=2, the basic safe-image argument also forbids M. Thus any remaining
case has C+B_s>=4 and C+2B_s<=5, with B_s>=1. This forces C=3, B_s=1.
There are two noncross A vertices. They are either paired together,
with the always-real wires paired together, or each paired to an
always-real wire.

If the fork center b is noncross, at least two of its neighbors are
cross vertices. Their rows lie outside M and each excludes at most one
B choice, leaving three third images. They force two distinct N-edges
at f(b), impossible. Distinct cross A vertices have distinct images.

If b is cross, it has a noncross neighbor a0, because only one of the
other four A vertices is not a neighbor. Row b-a0 excludes one B choice
and forces N to pair f(b) with f(a0). The center also has a cross
neighbor v, since there are only two noncross A vertices.

For row b-v, exclude their two cross B partners. The two remaining third
images are the image p of the same-sign B-B pair and the image q of the
B partner of the third cross A vertex. They are distinct from each other,
from f(b),f(v), and from f(a0). Both triples must be hit. The vertex f(b)
already has its partner f(a0) outside both triples, so the first triple
forces the edge f(v)p and the second forces f(v)q. These distinct edges
cannot both belong to a matching. Contradiction.

This argument allows the two noncross A images to coalesce. It needs
only their separation from the other matching blocks. Thus all perfect
first matchings are excluded. ∎

## 7. Comparable idle coordinates reduce five gates to six

There is a useful strengthening of repeated-edge augmentation. Suppose
x,y are idle in M and their signed type coordinates are universally
comparable over the whole family: either s_x<=s_y in every state, or
s_x>=s_y in every state. Their physical wire order does not matter.

**Comparable-coordinate augmentation.** Add the standard comparator xy
to M. There is a single fixed permutation pi of its two output wires
such that the new type vector is pi applied to the old type vector in
every state: pi is the identity if the types were already ordered, and
the transposition otherwise. Equal-type states satisfy either routing.
The other M-gates avoid x,y and are unchanged.

Replace N by the matching pi(N). Its retained count on the new types is
exactly its old retained count. Orienting each new N-edge in the standard
direction is harmless, since only its incoming real-real count matters.
The new M has no smaller retained count, so every old peak is preserved.

Consequently a five-gate solution whose idle coordinates are universally
comparable would give a perfect first-matching solution, forbidden by
Section 6. This argument permits either direction of type comparability;
requiring the pair already to be sorted would unnecessarily weaken it.

In the case-607 family, an always-real coordinate is comparable to every
other coordinate. Any minus-only variable is comparable to any plus-only
variable. Within A, the same-sign pairs ab and ce have nested sentinel
supports, so they too are comparable. The remaining incomparable idle
pairs are precisely:

* the two same-sign A pairs cd and de;
* the four same-sign B pairs;
* the thirteen same-sign A-B pairs.

There are nineteen candidate idle pairs in total. A and B choices vary
independently, while distinct B vertices are sentinels in different
columns; these observations establish incomparability for the displayed
pairs. Among A, the two plus pairs cd,de have nonnested supports. No
claim is made that all these remaining pairs are feasible; this is a
necessary classification for the remaining five-gate hand argument.

## 8. Checks and remaining scope

`d17_feedback_twelve_structure_verify.py` checks the nine local ternary
states for safe repeated-edge augmentation, all twelve instances of the
idle-edge folding lemma, the full-column classification on all 76
partial matchings of six vertices, and the same/opposite-sign cross-gate
contradictions with explicit central-endpoint controls. It also checks
the fixed identity/transposition routing on all twenty states for each
of the 47 comparable coordinate pairs, and confirms the nineteen
incomparable pairs listed above. It does not use SAT or search all
twelve-wire first matchings.

The checked twelve-wire UNSAT theorem remains available separately.
The arguments here close m=4 and m=6. The remaining size m=5 is now
closed by [the two-idle-wire hand proof](d17_hand_defects_twelve_five.md),
whose corrected row-image count and final three-center classification
were independently reviewed here. With the small-matching theorem in
`d17_hand_defects_twelve_cross.md`, the twelve-wire obstruction has a
complete hand proof. Extending it to larger widths uses the separately
proved [fixed-sentinel pruning lemma](fixed-sentinel-obstruction.md).

## 9. Sign and embedding scope

The four-gate and perfect-first-matching proofs do not use the particular
two-minus/three-plus assignment on B. They use only that each of its five
singleton sentinels has a fixed sign, with same-sign B-B pairs producing
one image identification apiece. Consequently these arguments hold for
all 32 assignments of signs to B.

They also use only the A sign partition {a,b}/{c,d,e}, not which part is
negative: simultaneously reversing the signs of A preserves all equal-
sign folding statements and opposite-sign distinctions. No argument
depends on the relative physical order of the twelve labelled wires.
Changing their embedding changes singleton destinations but not the
matching-block separation or the possible image identifications used in
the proof. Comparable-coordinate augmentation explicitly allows either
direction of the fixed type order.

The numerical count of nineteen incomparable idle pairs in Section 7 is
specific to the original B assignment. The augmentation lemma itself,
and the exclusion of comparable idle pairs, hold for all B signs and
all embeddings. The completed five-gate proof has the same generality:
its corrected row count is 5-B_s, and its last case distinguishes only
equal-sign identifications from different matching blocks. The earlier
small-matching argument is equally independent of the B sign counts.

Consequently the complete twelve-wire theorem holds for all 32 fixed B
sign assignments, either global sign choice on the two parts of A, and
every embedding of the twelve labels into ordered wires. It also survives
adding any number of coordinates carrying fixed signed infinities, by
the fixed-sentinel pruning lemma. This is a width-independent structural
template; its existence does not itself prove the full D17 or D18 bound.
