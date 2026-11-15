# Two H9 cases with a six-vertex fence image

No nine-wire depth-seven sorter starts with `01 23 45` followed by
either `03 14 67` or `03 16 27`. The proof closes these two H9
second-layer classes; it does not alone establish all of H9.

The target second layers are `03 14 67` and `03 16 27`, in each case
after `L1=01 23 45`. We prove they have isomorphic images and exclude
a five-layer completion of that image. Write M=L3, N=L4, Q=L5.
Delete universally redundant gates throughout. Signed restrictions use
original input positions, with real-track identities followed through
all blind comparisons.

The proof uses the [H7 early profile](h7-early-profiles.md), the
five-wire thin lemma (README Lemma 3), and the
[rank-threshold partner lemma](h9_feedback_round5_rank_partner.md).
The [fixed appendix](h9_feedback_round9_tables.md) supplies the signed
restrictions, case10 edge intersections, and concrete rank witnesses.

## 1. One product image for both second layers

For `L2=03 14 67`, the image on012345 is exactly the height-two poset

```
03,04,14,15,23:     x0<=x3,x4; x1<=x4,x5; x2<=x3.
```

Given a target x satisfying these inequalities, put
`x0,x4,x2,x3,x1,x5` on the original six inputs. The first layer is
already sorted on each pair; the second produces x. Wires6,7 form
an independent sorted pair and8 is independent. The undirected
Hasse diagram of the six-poset is the path `2–3–0–4–1–5`.

For `L2=03 16 27`, the image on012367 is exactly

```
03,06,16,23,27:     x0<=x3,x6; x1<=x6; x2<=x3,x7.
```

The preimage on0,1,2,3,6,7 is `x0,x6,x2,x3,x1,x7`. The sorted pair
is45 and8 is independent. The coordinate map from the first image to
this image is

```
old coordinate: 0 1 2 3 4 5 6 7 8
new coordinate: 0 2 1 6 3 7 4 5 8.
```

It identifies every poset relation and the independent sorted pair.
Thus a five-layer completion of either image gives one for the other,
by relabeling and untangling the full suffix. As in the
[poset transfer theorem](h9_feedback_round8_poset.md), prepend the
canonical two-layer prefix before untangling. Sorted distinct inputs
force the final output permutation to be the identity. It suffices to
exclude `03 14 67`.

This image also has the order-reversing symmetry

```
π=(0 4)(1 3)(2 5)(6 7),   with8 fixed.
```

Coordinate permutation π together with global value negation preserves
the image. Conjugating the suffix by this operation, then untangling,
therefore preserves existence of a completion and all layer sizes.

## 2. A deletion path forces twelve third layers

The following restrictions leave two disjoint RR gates through L2.

| Original sentinels | Boundary sentinel pair | Retained gates at the boundary |
|---|---|---|
| `+0 +2` | 34 | `15,67` |
| `-0 -4` | 01 | `23,67` |
| `+2 -4` | 13 | `04,67` |

Collapse the retained gates into one layer. The H7 early profile forces
at least three M edges avoiding each displayed pair.

Here is the general matching fact being used. On2r+1 vertices, suppose
a matching leaves at least r−1 edges after deleting either endpoint
pair of each edge in a four-vertex path a–b–c–d. The matching has r
edges: a smaller matching would have to avoid all four path vertices,
leaving too few vertices. Let v be its unique idle vertex. Any path edge
not incident to v must itself be a matching edge, since otherwise its
two used endpoints delete two matching edges. The idle vertex must
therefore be b or c; otherwise two adjacent path edges would have to
belong to the matching. If v=b, edge cd is forced; if v=c, edge ab is
forced.

Apply this to the path0–1–3–4. M has four gates, with either idle1 and34,
or idle3 and01. The image duality π exchanges these alternatives. Choose
idle3 and01. The other six vertices245678 are perfectly matched, and
pair67 is forbidden because it is already ordered. There are fifteen
perfect matchings of six vertices; three contain67. The twelve forms
are listed in the appendix, numbered as follows:

| Case | M |
|---:|---|
| 1 | `01 24 56 78` |
| 2 | `01 24 57 68` |
| 3 | `01 25 46 78` |
| 4 | `01 25 47 68` |
| 5 | `01 26 45 78` |
| 6 | `01 26 47 58` |
| 7 | `01 26 48 57` |
| 8 | `01 27 45 68` |
| 9 | `01 27 46 58` |
| 10 | `01 27 48 56` |
| 11 | `01 28 46 57` |
| 12 | `01 28 47 56` |

## 3. Two reusable matching rules

Every signed demand in the appendix leaves five reals and exactly3−d
RR gates through L3, where d=1 or2. N must contribute at least d edges
inside its real set: otherwise schedule the at most two retained gates
through L4 one each in two layers and append L5–L7, contradicting the
five-wire thin lemma. A five-set followed by “two” below means demand2;
a contact means demand1. Ordered pairs in the appendix are forbidden
by elementary min/max propagation.

**Extension rule.** Let T be a four-set. Demand2 on both T+x and T+y,
with distinct x,y outside T, forces either a perfect matching on T,
or one T edge with x and y paired to the two remaining vertices of T.
Each five-set needs at least one T edge. If only one occurs, each
external vertex must supply the other edge, using distinct remaining
T vertices. A third demand2 on T+z, with a third external z, is then
impossible. Thus **three distinct extensions force a perfect matching
on T**.

**Shared-pair rule.** Suppose T is a four-set, x,y are outside it, and
S is a disjoint three-set outside T+x+y. If T+x, T+y, and `{a,b}+S`
each demand2, where a,b belong to T, then ab is a matching edge.
By the extension rule, either T is perfectly paired, or only one T
edge occurs and all its other vertices meet x,y. If ab is absent,
all T vertices are already used, and no T edge is internal to
`{a,b}+S`; the three vertices of S can
supply at most one edge, contradicting its demand2.

We also use the shared-triangle rule from the previous case: two
five-sets with three-set intersection T and demand2 force an edge
inside T. Their union has seven vertices, so four distinct demanded
edges cannot be disjoint. If their outside pairs are ab and cd and
ab is forbidden, cd is forced, and the remaining T vertex meets a
or b.

## 4. Fourth-layer classifications

Row references in this section are to the signed demand appendix.
Every argument includes optional gates on unused vertices.

### Cases1 and3

In both cases, rows with real sets13457 and34567 are the extensions
of T=3457 by1 and6. Apply the extension rule.

In case1, if T is perfectly paired, demand12567 forces57 and hence34.
Demand34678 then forces68, and12567 forces12. Thus
`N=12 34 57 68`.

Otherwise write the edges as e in T, 1u and6t, with u,t the remaining
T vertices. The only free vertices are0,2,8. Demand12567 cannot obtain
an edge from these free vertices, so its two edges must be1u and6t,
forcing `{u,t}={5,7}` and e34. Pair56 is forbidden, leaving15 and67.
Contact02357 forces02; contact12468 then has no edge. This branch fails.

In case3, a perfect T matching is forced by demand01247 to contain47
and35. Demand35678 forces68; contact12567 forces12. Thus
`N=12 35 47 68`.

In the nonperfect branch e,1u,6t, free vertices are again0,2,8. If e47,
demand01247 forces02, but35678 has at most one edge. Otherwise01247
requires u in `{4,7}` and02. Demand35678 then requires both e and6t
inside that set, forcing u4. Thus e pairs two of357 and t is the third.
Contact12368 forces t3, giving e57 and36. Contact12568 now has no edge.

### Cases2 and4

Three extensions force a perfect matching on T=3458: in case2 the
external vertices are1,6,7 (rows2–4), and in case4 they are the same
vertices (rows1,3,4).

Case2 demand01258 forces58 and34, then an edge among012. Pair01 is
forbidden. If02 occurs, contact12478 forces17, leaving contact12456
empty. Hence12 occurs. The only optional extra edge is06, giving

```
12 34 58;   06 12 34 58.
```

Case4 demand01248 similarly forces48 and35, then02 or12. If02 occurs,
contact12578 would require the forbidden17. Hence12 occurs, and the
only optional extra edge is06:

```
12 35 48;   06 12 35 48.
```

### Case5

The sets13467,12467,14678 are three extensions of T=1467, so T is
perfectly paired. Demand34567 then requires35. The unused vertices
are0,2,8; pair28 is forbidden, so an extra02 or08 is optional. Therefore
N consists of35, any of the three perfect matchings of1467, and either
no extra edge,02,or08. This gives nine forms.

### Cases6 and7

For case6, demand-two sets01456 and34568 share T=456. Pair01 is
forbidden, so the shared-triangle rule forces38 and an edge e in T;
the remaining T vertex t meets0 or1. If it meets0, one of contacts
14678 and15678 has no edge among these three, and its only possible
extra edge is the forbidden17. Thus t meets1. N consists of38 and
a perfect matching of1456. On the remaining027, only02 is permitted
and is optional. There are six forms.

For case7, use the extensions12456 and14567 of T=1456. If T is
perfectly paired, demand34568 forces38, again giving the same six
forms, with optional02.

In the nonperfect branch, one T edge e occurs and the remaining T
vertices meet2 and7. Demand34568 forces e inside456 and also38.
Neither of the other edges meets contacts01346 and01345 internally.
Thus e would have to lie inside both contacts. Their intersection
with456 is the singleton4, which cannot contain an edge.

### Case8

Use the extensions13478 and12478 of T=1478. A perfect T matching
forces35 from demand34578 and26 from12468. This gives three forms:
`N=26 35+J`, where J is any perfect matching of1478.

Otherwise N has one T edge e,3t and2u, with unused vertices0,5,6.
No permitted optional edge among those vertices is internal to12468.
That demand therefore forces t7 and e inside148. Demand34578 then
forces u1 and e48. The edges are12,37,48; contact23456 forces56.
This gives the fourth form `12 37 48 56`.

### Case9

Apply the shared-pair rule to T=1245, external vertices0,8, and the
third demand13567. It forces15. Demand35678 now requires a perfect
matching J of3678. Demand12458 forces24. Contact03457 can receive an
edge only if37 belongs to J, hence J is37,68. Thus
`N=15 24 37 68`.

### Case10

This case uses the local five-unused-wire rule. Choose the two N edges
inside demand12456. There are twelve permitted bases. After a base is
fixed, only five vertices remain; choosing one residual clause edge
leaves room for at most one more edge. All unmet clauses must contain
that same last edge. The appendix prints all twelve bases and their
single-edge intersections. Every branch fails, so there is no N.

### Case11

The demand-two sets13568,34568,35678 are three extensions of T=3568.
Demand12458 then forces the perfect T matching36,58. On the remaining
vertices01247, the demand and contacts respectively require

```
12 or14 or24;    14 or17;    04 or14;    12 or17 or27.
```

If14 occurs, the final clause forces27. Without14 the middle two
clauses force17 and04, making the first impossible. Thus
`N=14 27 36 58`.

### Case12

Demands13458 and34678 share T=348, so N has an edge inside T.

If this edge is34, demand12468 requires a perfect matching on1268.
Its three possibilities are12+68 (fails13458),16+28 (28 is forbidden),
and18+26 (fails34678).

If the T edge is38, demand12468 requires a perfect matching on1246.
The possibilities12+46 and16+24 fail13458, while14+26 fails34678.

If the T edge is48, the four demand-two sets leave contacts

```
135,136,126,367
```

on the seven remaining vertices. A matching has at most three edges
there, so one edge must meet two contacts. The only such pairs are13,
16,and36. Pair13 forces26 and67, which collide;16 forces35 and37,
which collide;36 forces15 and12, which collide. This last branch also
fails. There is no N.

The twelve cases leave exactly33 N forms, as listed in the appendix.

## 5. Rank partners exclude all33 endings

The fixed rank inputs in the appendix witness observed endpoint
intervals after L4. Only Q and two final layers remain. As proved in
the threshold-partner lemma, a wire with observed span at least four
must be used by Q. For such a pivot with endpoints l,h, an input on
which its value is at most h−4 forces the partner above h−4; an input
on which its value is at least l+4 forces the partner below l+4.
Both directions of every proposed edge must satisfy these conditions.
A violation produces a gap of four at the minimum or maximum Q
output; rank intervals then require five final positions, while the
last two layers reach at most four.

Thirty N forms have an isolated mandatory pivot. In the other three,
two mandatory pivots have only the same single possible partner:

| Case | N | Mandatory pivots | Only partner |
|---:|---|---|---:|
| 3 | `12 35 47 68` | 4,7 | 2 |
| 4 | `06 12 35 48` | 6,8 | 2 |
| 4 | `12 35 48` | 6,8 | 2 |

These are two-vertex Hall obstructions: a matching cannot cover both
mandatory pivots with one available partner. The fixed threshold guards
in the appendix certify every excluded membership and the mandatory
spans; no final matching enumeration is needed.

Thus every M form is excluded. The shared image argument proves both
H9 second-layer cases `03 14 67` and `03 16 27`.


## 6. Independent fixed verification

The [checker](verify/h9_feedback_round9_proof.py) imports only the Python
standard library and reads the fixed certificate and printed appendix.
It verifies the exact six-component images on all720 orders each,
the displayed coordinate isomorphism and order-reversing symmetry,
and the twelve M forms from the deletion-path conclusion.

It then checks66 signed five-real demands and the three initial
seven-real restrictions by23,040 direct real-order replays. For the
fourth-layer reduction it follows the proved extension, shared-pair,
and shared-triangle alternatives, completing each forced core only
on its three or five unused vertices. Case10 uses its twelve printed
bases and17 edge branches. Case12 uses the three shared-triangle
choices and three repeated-edge contradictions. This is not an
all-nine-wire matching scan.

All optional idle completions are checked explicitly, including both
sizes in cases2 and4, all nine forms in case5, and all six forms in
cases6 and7. A separate case8 check accepts its required56 extension
and rejects06. These controls guard against accidentally assuming N
is maximal.

For the endings, the checker evaluates the seventeen printed rank
inputs on33 distinct prefixes, giving561 distinct prefix/input runs.
It verifies107 pivot guards and62 reciprocal guards. Thirty forms
have isolated pivots; the other three have the displayed two-pivot
Hall obstruction. No solver, discovery import, final-layer matching
scan, or additional rank-input search is used.

The fixed certificate SHA256 is

```
a2515ba6952a2e01125fa5f43eb5f12c27ad117c8f2232e822ae160b1a312a85
```

The [audit](results/h9-feedback-round9-proof.json) records this hash
and the hashes of the proof, appendix, and checker. Discovery runs
were bounded and finished normally; no SAT process was launched.
