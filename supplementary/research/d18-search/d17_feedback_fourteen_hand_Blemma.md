# A five-column forcing lemma for the fourteen-wire cases

**Result.** The five B states of case 606 force a common pair of
sentinels to be matched. After any first matching, this row-forcing
property survives unless that matching contains one specified B edge.
The exception has an exact four-wire alternative. This is a reusable
hand lemma, not a complete hand proof of case 606 or 608.

The lemma explains why the extra fifth B state matters: the sixteen-state
products of two forks admit two-layer peak coverage. Directly replayed
controls are in `results/d17-feedback-fourteen-hand-fourbyfour606/` and
`...fourbyfour608/`. The full twenty-state obstructions remain valid, but
their existing universal proofs for these two cases still use SAT.

## 1. The two extended B forks

Write G={ab,bc,ce,bd}, with fork center b. For case 606 the five B
sentinel triples are

    qab, qbc, qce, rce, qbd.                        (1)

The signs are q-,a-,b-,c+,d+,e+,r+. In the seven-coordinate B block their
physical labels are

    d=0, a=1, b=2, c=3, q=4, e=5, r=6.

These correspond to original seventeen-wire labels

    d=10, a=11, b=12, c=13, q=14, e=15, r=16.

For case 608 the triples are

    qab, qbc, qce, qbd, rbd.                        (2)

Here q-,a-,b-,c+,d+,e+,r+ again, with B-block labels

    q=0, r=1, d=2, a=3, b=4, c=5, e=6.

Thus four columns consist of a signed fork plus the common negative
sentinel q. The fifth changes q- to a real and changes the common real
r to a positive sentinel. It duplicates the outer edge ce in case 606
and the edge bd in case 608.

## 2. Common three-set plus fork

Let C be three common sentinel positions, disjoint from the five fork
vertices. Suppose a matching N contains two edges in every set

    C union {x,y},             xy in G.              (3)

**Lemma.** N contains an edge inside C. If p is the remaining C vertex,
N also contains pb and ce.

*Proof.* Without an edge inside C, two matching edges in (3) must pair
both x and y into C. Every one of the five fork vertices occurs in a
G-edge, so all five would need distinct partners among three vertices.
This is impossible.

Once two C vertices are paired, the remaining triple {p,x,y} must
contain an edge for every G-edge. If p is paired to z in the fork, all
G-edges not incident to z must themselves belong to N. This is possible
only for z=b, because deleting any other vertex leaves two incident
edges. Deleting b leaves precisely ce. If p is paired outside the fork,
all G-edges would be required. Hence pb and ce are forced. ∎

The proof remains valid if the variable pair graph is the triangle
bc,be,ce with the attached edge ab: deleting b is still the only way to
leave a matching. It also applies to a renamed copy of the original fork.

## 3. Static five-column classification

Add two common sentinel positions u,v to each B triple, giving five
sets of size five. Require N to contain two edges in each set.

For the first four fork columns take C={u,v,q}. Section 2 gives one
C-edge, plus pb and ce, where p is its unpaired C vertex.

**Case 606.** The extra set is {u,v,r,c,e}. Its fixed edge ce supplies
one pair. If the C-edge were uq or vq, both u and v would have partners
outside {u,v,r}, leaving no second edge in this extra set. Thus N must
contain exactly the following core:

    uv, qb, ce.                                    (4)

Conversely these three edges suffice for all five sets; additional
disjoint edges are irrelevant.

**Case 608.** The extra set is {u,v,r,b,d}. In each of the three possible
pairings of {u,v,q,b} produced by Section 2, it already contains one
edge. The only possible second edge is rd. Consequently N must contain

    ce, rd, and a perfect matching of {u,v,q,b}.     (5)

All three perfect matchings of that four-set work. These are exact
classifications of arbitrary partial matchings, independent of width
or the signs used to obtain the current sets.

## 4. Case-606 transport: one critical comparator

Across the five signed B states (1), the coordinate functions obey

    q <= b <= a <= 0 <= r <= e <= c,

while d is positive only in the last column qbd. It is incomparable
with r,e,c and comparable with every other coordinate. Therefore the
only B-B comparisons that do not act as a fixed permutation of the type
coordinates are

    dc, de, dr.                                    (6)

They share d, so a matching contains at most one. Every other B-B gate
is a fixed identity or transposition over all five states. Such gates
may contribute first-layer real-real counts; we do not erase their
counts. We only absorb their fixed type routings into a relabelling of N.

Take the orientation in which the exceptional gate moves d's positive
sentinel to its partner. Reversing that physical orientation merely adds
a fixed output transposition, also absorbed into N. The exceptional gate
changes only the last B state qbd:

| First gate | New last B triple | Variable pairs in the four q-columns |
|---|---|---|
| none | qbd | ab,bc,ce,bd |
| de | qbe | ab,bc,ce,be |
| dr | qbr | ab,bc,ce,br |
| dc | qbc | ab,bc,ce,bc |

For none, de, and dr, Section 2 still forces the C-edge, pb, and ce.
The extra column rce then forces that C-edge to be uv, exactly as
before. Hence the core (4) survives.

For dc, the variable graph is the path ab,bc,ce. It has two possible
centers for the remaining C vertex: p can be paired to b, forcing ce,
or to c, forcing ab. The first alternative again gives (4). In the
second, the extra column rce forces re, leaving any perfect matching
of {u,v,q,c}. Thus the exact alternatives are

    uv, qb, ce;

or

    ab, re, and a perfect matching of {u,v,q,c}.     (7)

The second alternative includes matchings that do not pair u with v.
For example {ab,re,cu,qv} works. So the critical-edge exception cannot
be dropped. The gate dc coalesces the qbd state with qbc; it is the only
single matching gate that removes this branch of the signed family.

## 5. Corrected-row consequence for the full fourteen-wire family

Fix one A row in the case-606 twenty-state product. Its two A sentinels
and the types of every other A/common coordinate are constant while B
ranges over its five columns. Every comparison between such a constant
type and a B coordinate is universally comparable, because a B
coordinate ranges over {minus,real} or {real,plus}. It therefore acts
as a fixed type routing across this row.

Since the first layer is a matching, these fixed routings are disjoint
from any exceptional B-B gate in (6). The transported row is consequently
a relabelled copy of one of the four families in Section 4, with two
common A-sentinel positions u',v'.

**Row-forcing lemma.** Suppose the first matching M does not contain
the critical B edge dc, original edge (10,13). If all five states of an
A row require their peak in N, then N must pair their two transported
A sentinels u',v'.

Here N has first been safely completed to a perfect matching. On fourteen
wires with five sentinels, four real-real gates are equivalent to two
sentinel-sentinel gates, which is exactly the condition in Section 4.
For an A-row uv outside M, its sentinel positions are the singleton
images f(u),f(v). Thus every such fully required row forces the edge
f(u)f(v) into N.

This combines with the previously proved folded-fork lemma: if the
forced folded rows contain two distinct incident edges, coverage is
impossible. In particular:

* every first matching of at most three gates, without dc, is excluded;
* every four- or five-gate first matching using all five A vertices,
  without dc, is excluded. For four gates, any used sentinel prevents
  a first peak; for five gates, the two A sentinels in a row outside M
  touch distinct gates and leave at most three real-real gates.

The general conditional criterion uses the actual first counts: retain
the A rows with no first-layer peak in any of their five columns, omit
rows whose two A endpoints form an M-edge, and test the resulting folded
graph. This is a hand implication, not a claim that every first matching
satisfies its hypothesis. The critical dc branch and other partially
covered rows remain to be handled for a complete case-606 hand proof.

## 6. Checks and negative evidence

`d17_feedback_fourteen_hand_Bverify.py` checks all local coordinate-order
claims, the exact fixed-routing reduction for all 232 B-only matchings,
and the four canonical static classifications against all 2,620 partial
matchings on their nine relevant positions. This is a small independent
check of the lemmas; their proofs are the counting and graph arguments
above. No SAT is needed for this verifier.

The B-only audit agrees that a bypass of uv exists for exactly the 26
matchings containing dc. The full fourteen-wire and seventeen-wire
obstructions are not inferred from that local count. Nor are the
sixteen-state controls sorting networks: they satisfy only the two-layer
peak relaxation.
