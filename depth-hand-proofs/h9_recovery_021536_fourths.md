# Fourth-layer hand classification for `02 15 36`

For the eighteen third layers in the [hand reduction](h9_recovery_021536_reduction.md),
this note handles all except case 2, which has its own
[idle-wire rank proof](h9_recovery_021536_case2.md). Eleven of the
seventeen forms here admit no fourth layer. The other six leave exactly
31 fourth-layer forms, all excluded by the
[fixed rank-ending certificates](h9_recovery_021536_endings.md).

The arguments use hand matching lemmas and the explicit
[small tables](h9_recovery_021536_fourths_tables.md). A table completes
a forced core only on at most five unused vertices. It never assumes
that the fourth layer N is maximal, and no SAT answer or global
nine-wire matching enumeration is a premise.

## 1. What the signed rows require

Each appendix row fixes four original inputs to signed sentinels and
leaves five reals. Through the first three layers it retains exactly
`3-d` real-real gates, where the row's demand d is one or two. N must
contain at least d edges inside the displayed real set. Otherwise at
most two real-real gates have occurred through N. Serialize them into
two layers, then append the original last three layers. This would be
a five-wire depth-five sorter with at most one gate in each of its
first two layers, contradicting the five-wire thin lemma.

All forbidden N edges in the appendix are universally ordered pairs
after the given third layer, obtained by elementary min/max propagation.
Delete these redundant comparisons without changing the prefix image
or its possible completions.

## 2. Reusable matching lemmas

**Even core with two extensions.** Let T have four vertices, and let
x,y be distinct vertices outside T. If both `T+x` and `T+y` demand two
edges, either N perfectly matches T, or N has one edge inside T and
pairs x and y to its two remaining vertices. Each five-set must contain
an edge of T. If T has only one, its two unused vertices must supply
the second edge in the two demands, separately. This gives three
perfect cores or twelve three-edge cores before forbidden edges are
removed.

**Two odd sets with a common pair.** Let A and B be disjoint odd sets
of size `2r-1`, and let u,v lie outside them. Suppose both `A+uv` and
`B+uv` require r edges. If uv is in N, each odd set needs at least r-1
internal edges. If uv is absent, the two demands use 2r distinct edges
on a union of 4r vertices, so N perfectly matches that union. Each odd
set has exactly r-1 internal edges and its remaining vertex meets one
of u,v; the two sets use different members of the pair. No edge can
join A to B because all 2r edges are already counted by the demands.

For triples A,B this gives nine cores containing uv and eighteen
four-edge cores without it, before removing forbidden edges. The
statement permits additional vertices in the ambient network.

**Odd core and a deletion graph.** Let T have `2r-1` vertices. Let G
be a nonempty graph outside T. There is a matching giving r edges
inside `T+uv` for every edge uv of G if and only if G has a vertex v
such that `G-v` is a matching. External matching partners do not change
this criterion.

For necessity, write h for the number of internal T edges. Each demand
can receive at most two further edges, so h is r-1 or r-2. In the
second case, both endpoints of every edge of G must be paired to the
three unused T vertices. G therefore uses at most three vertices, and
deleting any one of them leaves a matching. In the first case there is
one unused T vertex t. If t is matched to a vertex v of G, every edge
of `G-v` must itself belong to N. If t is idle or has a different
partner, all of G must belong to N. Either way the claimed vertex
exists. For sufficiency, pair all but one vertex t of T internally,
add tv, and add the edges of `G-v`.

In particular, a four-cycle G is impossible. So is a G with two
vertices of degree at least three: after deleting any one vertex,
at least one of those vertices still has degree at least two.

**Shared triangle.** Two five-sets with intersection T of size three,
each demanding two edges, force an edge of N inside T. Otherwise four
distinct matching edges would fit inside their seven-vertex union.

**Weighted demands.** Give each demand row a nonnegative weight w.
Suppose each allowed edge ab occurs in rows of total weight at most
`p(a)+p(b)`, for nonnegative vertex prices p. Any matching then meets
weighted demands totalling at most the sum of all prices. Thus required
weighted demand larger than that sum is impossible. This applies at
arbitrary ambient width and permits idle vertices.

## 3. Four immediate odd-core contradictions

The appendix provides exactly these demand-two sets `T+uv`.

| Cases | T | Edges uv of G | Obstruction |
|---|---|---|---|
| 4 | 578 | `23,01,14,12,24` | vertices 1 and 2 each have degree three |
| 11 | 268 | `01,04,17,47` | four-cycle |
| 12 | 258 | `01,04,17,47` | four-cycle |
| 18 | 245 | `78,01,18,07` | four-cycle |

The odd-core lemma excludes N in all four cases.

## 4. Cases 1, 5, 6 and 9

**Case 1.** The sets `01478` and `24578` share triangle `478`; since
78 is forbidden, N contains 47 or 48. Suppose it contains 47. The
three demand-two sets then require edges in the triples `018`, `258`
and `158`. If 18 occurs, 25 is forced. If 58 occurs, 01 is forced.
If neither occurs, `158` requires 15, then `018` requires 08, leaving
no edge for `258`. These are all possibilities.

For core `47,18,25`, the unused vertices are `036`, where only 03 is
permitted; it is optional. For core `47,58,01`, contact `12348` forces
23. The displayed demand and forbidden-edge conditions are invariant
under swapping labels 7 and 8, so their classifications for edge 48
are the exchanged three forms. This symmetry is only of the necessary
conditions; no symmetry of the full third-layer image is assumed.
There are six N forms.

**Case 5.** Demand two on `01278` and `34578`, with 78 forbidden, invokes
the common-pair lemma. Choose an internal edge of each triple `012`
and `345` and match their unused vertices to 7 and 8 in either order.
All `3*3*2=18` forms are listed in the appendix.

**Case 6.** Demand two on `01278` and `34678`, again with 78 forbidden,
forces the same shape, with triples A=`012` and B=`346`. Let a,b be
their unmatched vertices before connecting them to 7 and 8. Wire 5 is
idle in N. If the internal B edge is not 34, the contacts `13457` and
`13458` force a=1 and b in `34`: each must use the appropriate one of
the two edges to 7 and 8. But contacts `03457` and `03458` similarly
force a=0. Hence the internal B edge must be 34, so b=6. Now contact
`14578` forces a=1, whereas contact `03578` forces a=0. No N exists.

**Case 9.** Sets `01278` and `13578` share triangle `178`. Since 78 is
forbidden, N has 17 or 18. If it has 17, demands `02478` and `34578`
must be met by perfect matchings on `0248` and `3458`. Their intersection
`48` is closed under N partners, forcing 48, and then 02 and 35. Edge
18 gives the exchanged form. Thus precisely two N forms remain.

## 5. Case 14 forces one fourth layer

Sets `01278` and `23578` share triangle `278`, so one of 27,28,78 is
an N edge. If 27 is used, demand `02578` needs 08 or 58 because 05 is
forbidden. Edge 08 leaves demand `13578` with only three available
vertices. Edge 58 makes that demand force 13, after which `01278`
cannot receive its second edge. Thus 27 is impossible.

If 28 is used, `02578` instead needs 07 or 57. Edge 07 again leaves
only three available vertices for `13578`; edge 57 forces 13, after
which `01278` has no second edge. Thus 78 is forced.

The four demand-two rows now reduce to contacts `012`, `235`, `135`
and `025`. At most three N edges remain. An edge must serve at least
two contacts; the only possibilities are 02,25,35. Edge 25 forces 01
from `012`, leaving `135` unserved. Edge 02 forces 35 and vice versa.
Thus both 02 and 35 occur. Finally contact `01348` forces 14. The
unique remaining N is `02 14 35 78`.

## 6. Case 17 by vertex prices

Take the five appendix rows in their printed order, with weights

```
2,1,2,2,3.
```

Their demands have weighted total 17. Give wires 0 through 8 the prices

```
0,3,3,0,3,0,1,3,3,
```

whose sum is 16. Each of the 27 allowed edges occurs in rows with total
weight at most the sum of its two endpoint prices. This is a direct
two-endpoint arithmetic check using the five printed sets; the fixed
checker verifies all 27 inequalities. The weighted-demand lemma gives
17<=16, a contradiction.

## 7. The remaining small local tables

Apply the even-core extension lemma to the following two demand-two
sets. Every necessary core is either one of the three perfect T
matchings or one T edge with x,y paired to its two unused vertices.
Remove cores containing forbidden comparisons.

| Case | T | x,y | Permitted cores |
|---:|---|---|---:|
| 3 | 2678 | 5,1 | 12 |
| 7 | 3678 | 2,4 | 10 |
| 8 | 0128 | 4,3 | 10 |
| 16 | 0128 | 3,5 | 10 |

For cases 13 and 15 use the common-pair lemma:

| Case | Odd triple A | Odd triple B | Common pair | Permitted cores |
|---:|---|---|---|---:|
| 13 | 136 | 025 | 78 | 16 |
| 15 | 023 | 467 | 18 | 22 |

In case 10, demand-two sets `01278` and `13678` force a shared-triangle
edge 17 or 18 because 78 is forbidden. With 17, the two demands further
require one edge in `028` and one in `368`. The disjoint possibilities
are `02+36`, `02+38`, `02+68`, `08+36`, `28+36`. Exchanging 7 and 8
gives the other five cores. This exhausts the ten printed cores.

**Local table rule.** A core of two edges leaves five unused vertices.
Every unmet row is a clause requiring one or two edges from its printed
list. Choose any edge in a smallest unmet clause. Only three vertices
remain, so every still-unmet row must accept the same final edge; a
residual demand of two is impossible. If no clause remains, the extra
edge is optional. A three-edge core starts directly with this last-edge
intersection. A four-edge core leaves no possible additional edge.

The appendix applies exactly this rule. Its clauses are chosen from
the displayed necessary demands. Every printed completion is also
checked against all the demands. Cases 3,7,10,13,15 leave none; cases
8 and 16 each leave two. All optional incomplete matchings are included.

Together with the direct arguments, the counts are

```
case: 1  3 4 5  6 7 8 9 10 11 12 13 14 15 16 17 18
N:    6  0 0 18 0 0 2 2 0  0  0  0  1  0  2  0  0.
```

The [fixed checker](verify/h9_recovery_021536_fourths_check.py) replays
all 100 printed signed demands on their 120 real orders, verifies
propagated inequalities and the matching recipes, and checks each local
clause intersection. The reusable lemmas and their applications are the
coverage proof; the checker is a verification of their fixed finite
premises. Acceptance of the complete H9 class also requires the separate
third-layer reduction, case-2 argument, and 31 ending refutations.
