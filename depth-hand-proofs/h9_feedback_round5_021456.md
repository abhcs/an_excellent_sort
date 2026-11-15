# The H9 case `02 14 56`

No seven-layer nine-wire sorter begins with `L1=01 23 45` and
`L2=02 14 56`. This hand proof uses the explicit signed restrictions,
matching arguments, and rank witnesses below. Its fixed certificates
pass the independent audit in Section4. Aggregate coverage is updated
separately after independent review.

Write M=L3, N=L4 and Q=L5. The notation `+i` or `-i` means a positive
or negative infinity at original input i. RR gates compare two retained
real tracks. Track identities follow the deterministic routing through
sentinel comparisons; stated sets use positions at the named boundary.
Disjoint real-track gates may commute, followed by ordinary untangling.

The proof uses the [H7 early profile](h7-early-profiles.md), the
[six-wire profile](h9_feedback_reschedule.md#1-two-rescheduling-facts),
the five-wire thin lemma (README Lemma 3), and the rank-interval and
forward-cone lemmas in the [previous H9 case](h9_feedback_round4_021637.md).

## 1. The complete third-layer reduction

The placements `-0,-4` and `-0,+4` retain two disjoint gates through
L2. Their sentinel pairs are respectively01 and06; the retained gates,
expressed at that cut, are `23,56` and `23,14`. Collapsing each prefix
to one layer and applying H7 shows that deleting either pair from M
must leave three RR gates.

Thus M has at least three gates. If it has three,0,1,6 are all idle.
If it has four, its idle vertex is one of0,1,6: an idle vertex outside
this set would require both01 and06 as edges. An idle1 forces06,
and an idle6 forces01. Consequently there are only two types:

* **Type A:** a perfect matching K on `{2,3,4,5,7,8}`, optionally
  accompanied by01 or06;
* **Type B:** a four-edge matching with idle0.

The universally ordered pairs after L2 are `02,03,04,14,16,56`.
Delete these redundant gates whenever considering M.

The following six signed restrictions will be used repeatedly.
Their retained gates are expressed at the L2 boundary.

| Name | Input sentinels | Sentinels after L2 | Retained gates through L2 |
|---|---|---|---|
| P | `+0 -2 +4` | `-0 +4 +6` | none |
| B | `+0 -2 -6` | `-0 +4 -5` | `16` |
| C | `+0 +1 +4` | `+2 +4 +6` | `03` |
| D | `+0 +4` | `+4 +6` | `23,02` |
| E | `+0 +1 +2 +4` | `+2 +3 +4 +6` | none |
| F | `+0 -2` | `-0 +4` | `15,56` |

Two simple consequences will be used. If a three-sentinel restriction
leaves two disjoint gates through L3, collapse them to one first layer.
The six-wire profile then forces N to pair all six real positions.
Two such real sets with an odd intersection are impossible: a matching
pairing both must pair their intersection. If a two-sentinel restriction
leaves at most four gates of height at most two through L3, rescheduling
would give a depth-six seven-wire sorter with at most four gates in its
first two layers, also impossible by H7.

### Type A is impossible

First suppose45 is absent from K. Write `4t,5s,e` for its three edges;
the first two are distinct. Under P the only retained gates are `5s,e`.
Under B they are the old gate16 and e; K avoids both1 and6, so they
are disjoint. The optional01 or06 is blind in both restrictions.

Put `u=max(4,t)` and `v=min(5,s)`. The sentinel sets after M are
`{0,6,u}` for P and `{0,u,v}` for B. Here u is never6, v is never6,
and u differs from v because `4t` and `5s` are disjoint. The two
six-real sets have intersection size five, giving the pairing
contradiction.

It remains that `K=45+J`, where J pairs `{2,3,7,8}`. If01 is the
optional gate, F blinds01 and45. Its only new RR gates are J, disjoint
from the height-two tracks5,6 of its old chain. Four gates have height
two, contrary to H7. In the other two options (no extra gate or06),
E blinds all three layers unless `J=23 78`. For this last J, P and C
retain two disjoint gates and end with sentinel sets056 and356.
Their real sets again intersect in five positions. Thus Type A fails.

### Type B must contain46

Suppose instead that46 is absent. Restriction D has two old gates,
whose height-two tracks occupy0,2. If M pairs2 with4 or6, both of
those tracks miss the two M RR gates (0 is idle). Four gates would
have height two. Therefore2 cannot meet4 or6.

Under P, precisely two M gates are RR. Under C, sentinel positions
2,4,6 occupy three different M edges, leaving one RR gate. If3 meets
one of2,4,6, that RR gate is disjoint from C's old gate03. Let the
positive sentinels from4 and6 finish at u,v, and the one from2 at a.
P has sentinel set `{0,u,v}`, while C has `{a,u,v}`. These sets differ
in exactly one position, so the forced six-real pairings contradict.
Thus3 cannot meet2,4,6 either.

Now2 and3 must meet distinct vertices of `{1,5,7,8}`. The remaining
vertices4 and6 cannot meet each other, and cannot meet2 or3; nor may
they use14,16 or56. They therefore meet the other two vertices of
`{1,5,7,8}`. Every M edge meets `{2,3,4,6}`, making E blind through
L3. This would sort five reals in the remaining four layers, a
contradiction.

We have proved exactly

```
M = 46 + K,   with idle0 and K a perfect matching of{1,2,3,5,7,8}.
```

The first two layers leave7,8 untouched, so their image is invariant
under swapping7 and8. Conjugate the suffix and untangle through all
later layers; sorted distinct inputs fix its final output permutation.
The fifteen K choices consequently reduce to nine representatives:

| Case | M |
|---:|---|
| 1 | `12 35 46 78` |
| 2 | `12 37 46 58` |
| 3 | `13 25 46 78` |
| 4 | `13 27 46 58` |
| 5 | `15 23 46 78` |
| 6 | `15 27 38 46` |
| 7 | `17 23 46 58` |
| 8 | `17 25 38 46` |
| 9 | `17 28 35 46` |

## 2. Fourth-layer reduction

The [fixed tables](h9_feedback_round5_tables.md) give signed five-real
restrictions for each case. If t=1 or2 RR gates remain through L3,
N needs at least `3-t` RR gates on their real set. Otherwise the first
four original layers contain at most two retained gates; schedule one
each in two layers and append the last three, contradicting the five-wire
thin lemma. A demand2 set is written simply as a five-digit string below.
A demand1 set is explicitly called a contact. Universally ordered pairs,
also listed in the tables, may be deleted from N. Elementary min/max
propagation proves all of them; no extra relation is needed.

Recall the two-extension lemma: two edges in both `T+u` and `T+v`,
where |T|=4, imply either an internal pairing of T, or one internal
T edge with u,v matched to the two other T vertices. Three different
extensions force the internal pairing. Also, a matching hitting three
distinct triangles of a four-set must pair the four-set: their common
intersection has only one vertex, so one edge cannot hit all three.

### Case1: six matchings

The two demand2 sets01378 and24578 have disjoint triples A=013,
B=245 and common pair78, whose edge is forbidden. Their four demanded
edges are therefore distinct. Each triple needs at least one partner
in78, so exactly one of7,8 meets A and the other meets B. The remaining
two A vertices pair internally, as do the remaining two B vertices;
wire6 is idle.

If the internal A edge were03 or13, contact23678 would force B's
unpaired vertex to be2, hence its internal edge45. One of the two
contacts23467,23468 then has no edge: choose the one containing A's
partner from78. Thus the internal A edge is01. The six forms are

```
N = 01 3u + a perfect matching of{2,4,5,v},
where {u,v}={7,8} and v is paired to one of2,4,5.
```

### Case2: one matching

Sets01358 and01348 extend T=0138 by5,4. In the noninternal alternative,
the three prescribed edges use exactly0,1,3,4,5,8, leaving2,6,7.
Each of23478 and23468 has at most one prescribed edge (on348), so
they require respectively27 and26, impossible.

If T pairs internally, any pairing except01,38 leaves23478 with only
three available vertices2,4,7, so cannot supply two edges. After01,38,
the two demands23478,23468 require either24 or the pair47,26;
the third possibility27,46 is forbidden. Contact12357 excludes47,26.
Thus24 is present, and the same contact forces57. Hence
`N=01 24 38 57`.

### Case3: eighteen matchings

Set01278 needs two edges and78 is forbidden. Put A=012 and C=78.
Either both C vertices meet A, or one C vertex c meets a in A and
the other two A vertices pair internally.

In the second alternative put `d=C\{c}`. The contacts in the appendix
force the following three triangles on T=345d to be hit:

| Internal A edge | Three triangles |
|---|---|
| 01 | `34d,35d,345` |
| 02 | `35d,45d,345` |
| 12 | `34d,45d,345` |

Thus N pairs T internally and leaves6 idle. This gives eighteen forms:
choose the internal A edge (three ways), c (two ways), and the perfect
matching of T (three ways).

For completeness, the first alternative is impossible. The indicated
contacts yield these residual edge clauses after both C partners are
fixed. A clause requires at least one of its edges.

| Two A partners of C | Required clauses |
|---|---|
| 0,1 | `34 or36`; `23 or35` |
| 0,2 | `45 or56`; `15 or35` |
| 1,2 | `04 or34`; `34 or36`; `34 or35 or45`; `04 or45` |

In the first two rows all choices from the two clauses meet the same
vertex, and none is common. In the last row, using34 makes the last
clause impossible; without34 the first two force04,36, making the
third clause impossible. The table applies to either assignment of7,8.

### Case4: one matching

Sets01248 and02348 extend T=0248 by1,3. If T pairs internally,
pairings04,28 and08,24 leave only3,6,7 available in demand34678,
which is impossible. Thus02,48 occur. Demand23478 then forces37,
and contact12457 forces15. Hence `N=02 15 37 48`.

In the noninternal alternative, demand23478 forces01: its other four
vertices2,3,4,8 must already supply two prescribed edges. The three
possibilities are therefore

```
01 23 48,    01 34 28,    01 38 24.
```

Demand34678 forces67 in each. Contacts13457,12457,13457 respectively
then have no edge. So this alternative is excluded.

### Case5: sixteen matchings

Set34578 needs two edges, and78 is forbidden. Its twelve possible
two-edge matchings fall into the following six patterns, where
`{u,v}={7,8}`. The residual contacts give the displayed clauses;
their short consequences determine all possible additional edges.

| Two edges in34578 | Residual clauses | Additional edges |
|---|---|---|
| `4u 5v` | `01 or12`; `12 or13` | 12, optionally36 |
| `34 5u` | `0v or2v`; `12 or1v or2v`; `26 or2v or6v` | 2v, optionally01 |
| `35 4u` | `01 or12`; `0v or2v`; `26 or2v or6v` | 01,2v |
| `3u 5v` | `01 or12`; `04 or24`; `24 or26` | 01,24 |
| `3u 45` | `0v or2v`; `01 or12`; `26 or2v or6v` | 01,2v |
| `3u 4v` | `01 or12`; `12 or25`; `25 or26` | 01,25 |

For the first row, avoiding12 would require the conflicting01 and13.
For the second, avoiding2v forces0v and12, leaving the last clause
empty. In rows3 and5, choosing12 has the same failure, so01 and2v
are forced. In row4,12 forces04 and leaves the last clause empty.
In row6,12 immediately empties the last clause. The only permitted
edges on the final three unused vertices are exactly the optional
ones shown. This proves all sixteen forms, including four with only
three gates.

### Case6: four matchings

Sets01235 and02345 extend T=0235 by1,4. In the noninternal alternative,
1 cannot meet5 because15 is forbidden. If1 meets0, the other two
prescribed edges pair2345. The contacts force78: use12578 for pairing
23,45 and12378 for either other pairing. This gives three forms
`N=01 78 J`, with J any perfect matching of2345.

If1 meets2 or3, the six possible prescribed triples and the contacts
which force the conflicting67 and78 are:

| Prescribed edges | Contact forcing67 | Contact forcing78 |
|---|---|---|
| `12 04 35` or `13 04 25` | 23467 | 23478 |
| `12 34 05` | 23567 | 23578 |
| `13 24 05` | 34567 | 23578 |
| `12 45 03` or `13 45 02` | 23567 | 23578 |

If T pairs internally, its three possible pairings give residual clauses
on the five unused vertices1,4,6,7,8:

| Internal T pairing | Required clauses |
|---|---|
| `02 35` | `17 or18 or78`; `47 or48 or78`; `47 or67` |
| `03 25` | `67 or68 or78`; `17 or18 or78`; `47 or48 or78`; `47 or67` |
| `05 23` | `67 or68 or78`; `17 or18 or78`; `17 or47`; `47 or67` |

For02,35, choosing67 forces both18 and48, impossible; choosing47
forces18. Thus the fourth form is `N=02 18 35 47`. For03,25,
choosing47 forces68 and empties the second clause; choosing67 forces
the conflicting18 and48. In the final row17 conflicts with every
option in the last clause, so47 is forced; then68 is forced and the
second clause is empty. No other form remains.

### Case7: a direct contradiction

Sets34578,23478,34678 are three extensions of T=3478, so T pairs
internally. Demand24678 then forces26. The three T pairings give:

| T pairing | Contacts forcing incompatible edges |
|---|---|
| `34 78` or `38 47` | 01248 forces01;12458 forces15 |
| `37 48` | 02457 forces05;12457 forces15 |

Thus no N exists.

### Case8: one matching

Sets01237 and02347 extend T=0237 by1,4. If T pairs internally,
pairings03,27 and07,23 leave only4,5,6 available in demand34567,
which cannot supply two edges. For02,37, the residual requirements are

```
45 or56;    15 or18 or58;    45 or48 or58.
```

Choosing56 forces18 and empties the last clause. Choosing45 forces18.
Hence `N=02 18 37 45`.

In the noninternal alternative, only5,6,8 are unused. Demand34567
forces56, and contact23578 forces the internal T edge to be23,27 or37.
Together with the same demand, the prescribed edges must therefore be

```
01 23 47 56,  01 27 34 56,
01 24 37 56,  04 12 37 56.
```

Contact13458 excludes all but the second; contact12358 excludes the
second as well.

### Case9: a direct contradiction

Sets02457 and24578 extend T=2457 by0,8. If T pairs internally,
demand45678 forces68. Pairings24,57 and25,47 then have contacts02378
and13458 forcing03 and13. Pairing27,45 instead uses contacts03478
and12348 to force03 and13. Both are impossible.

In the noninternal alternative, demand45678 forces02 and a pairing
of4578: the only other unused vertices are1,3,6, none of which can
provide an additional edge in that five-set. Contact23467 then forces
47, leaving58. But contact23678 has no edge, even if the only possible
additional edge13 is present. This excludes the final case.

The matching arguments leave exactly47 forms in Cases1–6 and8, with
counts6,1,18,1,16,4,1. Cases7 and9 are already contradicted.

## 3. Rank endpoints

All47 fourth-layer forms retained by the five-real demands alone have
a mandatory Q pivot with no possible partner. The appendix labels each
form, names its pivot, and gives explicit witnesses excluding the idle
choice and each of its eight possible partners. The same fifteen input
permutations are shared by all47 forms.

Here is the rank argument in full. At any fixed wire of a comparator
prefix, the attainable ranks over all input permutations form an integer
interval. Swapping consecutive rank values connects all input permutations.
For one such swap of k and k+1, identify those two values. The monotone
identification commutes with minimum and maximum, so every output either
stays fixed or changes between k and k+1. Along a path of these swaps,
the value at the fixed wire changes by at most one. It therefore attains
every rank between any two witnessed endpoint ranks.

A wire after Q has only two layers left. Its value can reach at most
four final output positions, and each attainable rank requires its own
final position. Thus two witnessed ranks with difference at least four
at that wire are impossible: the interval contains at least five ranks.

For an idle pivot, the appendix evaluates its value after L4. For a
proposed partner v, it evaluates either the minimum or maximum of the
pivot and v after L4. These are the two physical outputs of that Q
comparison. All other Q gates are disjoint, so none can affect the
displayed output. Every endpoint row has a rank gap of at least four.
The rows include comparisons repeated from earlier layers, and make no
assumption that Q is a maximal matching.

For each of the47 forms, every way to handle its pivot is consequently
excluded. Together with the direct contradictions in Cases7 and9,
this completes the `02 14 56` class. □

## 4. Fixed certificates and verification

The [solver-free checker](verify/h9_feedback_round5_proof.py) reads back
the [printed tables](h9_feedback_round5_tables.md) and checks all423
endpoint exclusions by running the fifteen displayed permutations
through each of the47 fixed prefixes:705 prefix evaluations in total.
It checks the moving-track restrictions on223,680 real orderings,
audits94 residual edge clauses used in the matching arguments, and
corroborates the derived third- and fourth-layer families. Its only
code dependency is the already-reviewed moving-track and replay helper
from the previous H9 checker; it imports no solver or discovery module.

The finite matching scans corroborate the structural classifications
proved above. Their absence of further survivors is not a proof premise.
The [audit record](results/h9-feedback-round5-proof.json) includes the
source, trace-helper, certificate, appendix, and proof hashes. The
separate probe, reduction, fourth-layer, and price-search files are
discovery material; no SAT answer is used in this proof. This closes
one H9 class, not all remaining classes or the full D(11) hand-proof goal.
