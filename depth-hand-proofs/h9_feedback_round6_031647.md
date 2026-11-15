# The H9 case `03 16 47`

No nine-wire depth-seven sorter can begin with
`L1=01 23 45`, `L2=03 16 47`. The argument reduces L3 structurally to
six forms, classifies L4 by small matching intersections, and excludes
every remaining form with explicit rank inputs.

This closes one H9 second-layer class. It does not by itself prove H9
or the full D(11) lower bound.

Write M=L3, N=L4 and Q=L5. A signed input `+i` or `-i` is an infinity
at original input i. All retained gates use real-track identities,
including their deterministic routing past sentinels. Boundary sets
below refer to physical positions after the specified layer. Delete
universally redundant comparators whenever they occur; this preserves
the sorter and can only reduce layer sizes.

We use the [H7 profile](h7-early-profiles.md), the
[six-wire profile](h9_feedback_reschedule.md#1-two-rescheduling-facts),
`D(5) >= 5`, the five-wire thin lemma (README Lemma 3), and the
[rank-threshold partner lemma](h9_feedback_round5_rank_partner.md).

## 1. Two exact image symmetries

The two-layer image is a product of three independent pieces: the
five-wire component01236, the fork457, and the idle wire8.

On01236, its image is exactly the set satisfying

```
x0≤x3,  x0≤x6,  x1≤x6,  x2≤x3.                 (1)
```

Necessity follows from the four comparisons. For sufficiency, use
original inputs on0,1,2,3,6 equal respectively
`x0,x6,x2,x3,x1`. The first layer sorts the pairs `(x0,x6)` and
`(x2,x3)` already in order. Then03 gives x0,x3 and16 gives x1,x6.
Thus every vector satisfying (1) is attained.

Similarly the image on457 is exactly `x4≤x5,x7`. Given such a vector,
place x4,x5,x7 on the original wires4,5,7; both comparisons already
respect the required inequalities. Hence the image is invariant under

```
σ=(1 2)(3 6),           τ=(5 7).                (2)
```

Either symmetry may conjugate the remaining network. Untangle all
reversed comparisons through the full suffix; sorted distinct inputs
fix the final output permutation. Comparator counts are preserved.

## 2. The third layer is `36+K`, with idle4

The placement `-0,-4` leaves two disjoint retained gates23 and16
through L2, and its sentinel positions are04. Merge those gates into
one layer. H7 forces M to retain at least three RR gates after deleting
positions04. Thus M has at least three gates. The possibilities are:

* three gates with0,4 idle;
* four gates with idle0;
* four gates with idle4;
* four gates containing04, with some other wire idle.

For the four-gate case this follows because either the unique idle
wire is0 or4, or the two used positions0,4 must occupy the same edge.

We use the following signed restrictions. Retained gates are expressed
at the L2 boundary, in chronological order.

| Name | Original sentinels | Sentinels after L2 | Retained gates |
|---|---|---|---|
| P | `+0 +2 -4` | `+3 -4 +6` | none |
| D | `+0 -4` | `-4 +6` | `23,03` |
| E | `+0 +2` | `+3 +6` | `45,47` |
| F | `+0 +2 +4 +5` | `+3 +5 +6 +7` | none |
| B | `+0 +2 +7` | `+3 +6 +7` | `45` |

Since P blinds both initial layers, M must have at least two RR gates
under P: otherwise one further sentinel blinds its only retained gate,
leaving five values to be sorted in four layers. Also, if D or E leaves
at most four gates of real-track height at most two through L3,
rescheduling gives a forbidden six-layer seven-wire sorter with at
most four gates in its first two layers.

### Only idle4 survives

For a three-gate M with0,4 idle, P's bound implies either36 is present
or one of3,6 is idle. In the latter case use σ to make3 idle. Under D,
the height-two tracks0,3 then miss every M RR gate: they are either
idle, or3 meets sentinel6 on36. There are two M RR gates, so the
four-gate rescheduling is impossible.

For a four-gate M with idle0, none of P's sentinel positions3,4,6 is
idle. Two of them must be paired, giving34,36 or46. Use σ to replace
46 by34. Under D, wire0 is idle and wire3 meets a sentinel on34 or36.
Exactly two M gates remain RR, again giving the forbidden rescheduling.

For a four-gate M containing04, P similarly requires36 or an idle
among3,6. Use σ to make the latter idle3. Under D, track0 is blinded
on04, while track3 is idle or blinded on36. Again precisely two M
gates are RR and the rescheduling is impossible.

Thus M has four gates and idle4.

### Gate36 is forced

Suppose36 is absent. Under E, positions3,6 occupy different M edges,
so exactly two M gates are RR. Its old height-two tracks are4,7.
Wire4 is idle. If7 meets3 or6, its gate is blind and the four-gate
rescheduling applies. Hence7 cannot meet3 or6. By τ, neither can5.

The universally ordered pairs after L2 are
`03,06,16,23,45,47`; delete them from M. Consequently the partner of3
is in `{1,8}`, and that of6 is in `{2,8}`. These partners are distinct.
Restriction F would blind M unless57 is a gate:3,6 already meet
distinct real positions, and otherwise5,7 would meet the other two
M gates. Therefore M is one of

```
13 26 57 08,    13 68 57 02,    38 26 57 01.     (3)
```

Let the positive sentinels from3,6 end at u,v in P and B. Both
restrictions retain exactly two disjoint gates through L3: under P,
they are57 and the edge incident to0; under B, they are the old45
and that edge incident to0. Their sentinel sets are respectively
`{4,u,v}` and `{7,u,v}`. Here u,v belong to `{3,6,8}`, so the two
six-real sets intersect in five positions.

Collapsing each pair of retained gates into one first layer gives a
six-wire depth-five sorter starting with two gates. Its next layer N
must pair all six positions by the six-wire profile. A matching pairing
both real sets would pair their odd intersection, impossible. This
excludes (3), proving

```
M = 36 + K,   idle4,
K any perfect matching of{0,1,2,5,7,8}.
```

On these matchings σ exchanges1,2 and reverses36; untangling that gate
restores36 and only relabels later layers. Together with τ, the fifteen
K choices reduce to six representatives:

| Case | M |
|---:|---|
| 1 | `01 25 36 78` |
| 2 | `01 28 36 57` |
| 3 | `05 12 36 78` |
| 4 | `05 17 28 36` |
| 5 | `08 12 36 57` |
| 6 | `08 15 27 36` |

## 3. A local fourth-layer classification

The [fixed tables](h9_feedback_round6_tables.md) list 67 signed
five-real restrictions. A row with demand d retains exactly 3−d
real-real gates through L3, where d is one or two. Thus N must have
at least d edges internal to its displayed real set. Otherwise at most
two gates remain through L4. Schedule them one each in two layers,
retaining their order if they meet, and append L5–L7. This gives a
five-wire depth-five sorter with at most one comparator in each of its
first two layers, contrary to the five-wire thin lemma.

The tables also list universally ordered pairs after M. Each follows
by elementary min/max propagation of earlier inequalities; delete any
such pair from N. No relation obtained by input enumeration is used.

### A five-unused-wire intersection lemma

Suppose two edges of a matching have been fixed, leaving five unused
vertices V. For each remaining demand write `(E,k)`, meaning that at
least k of the matching's remaining edges belong to E. Here E consists
of the permitted pairs in V internal to the appropriate real set, and
k is the original demand minus the contribution of the fixed edges.
Only positive residual demands need be kept.

Choose any residual clause `(E,k)`. A completion must use some edge e
of E. Once e is chosen, only three vertices remain unused, so there is
room for at most one more edge f. Subtract one from each clause whose
edge set contains e. Then:

* if any clause still demands two edges, this branch is impossible;
* otherwise, f must lie in every still-unmet clause and be disjoint
  from e; the intersection of those edge sets lists every possibility;
* if every clause is met by e alone, f is optional and can be any
  permitted pair on the three unused vertices.

This proves the rule for arbitrary edge sets and demands on five
vertices. It includes nonmaximal matchings. In particular, an empty
chosen clause is an immediate contradiction. When an unmet clause
remains, an empty intersection is also a contradiction.

### Applying the lemma

For the six M forms, choose these demand-two real sets:

| Case | Real set | Forbidden pair inside it |
|---:|---|---|
| 1 | 13578 | 78 |
| 2 | 13578 | 57 |
| 3 | 01247 | 12 |
| 4 | 35678 | 36 |
| 5 | 23578 | 57 |
| 6 | 01248 | 08 |

A matching on a five-set has at most two internal edges, so N has
exactly two there. They are the base edges in the tables. To list them,
choose the unused vertex in five ways and pair the other four in three
ways. Of those fifteen choices, three use the forbidden pair. The
remaining twelve are displayed explicitly for each case.

Each table row gives a subset of necessary residual clauses, an anchor
clause, and every branch edge e from that anchor. The displayed second
edge sets are exactly the intersections in the lemma. Thus the tables
are a finite hand classification with 72 bases and 152 single-edge
branches, all on at most five vertices. They do not assume that N has
four gates and do not require a scan of all nine-wire matchings.

For example, case1 with base `37 58` has the residual clauses

```
row4: at least one of 14,46;
row5: at least two of 02,04,12,14,24.
```

Branching on row4, edge46 contributes nothing to row5 and leaves room
for only one more edge, so it is impossible. Edge14 contributes one;
the only remaining edge disjoint from14 in row5 is02. This gives
`N=02 14 37 58`.

The optional branches are equally explicit. In case2, base `13 58`
leaves the clauses

```
row8: at least one of 02,04,24;
row10: at least one of 02,07,27.
```

Choosing02 meets both, so it may stand alone, or be accompanied by46
or67; pair47 is forbidden. Choosing04 forces27, while choosing24
forces07. These are exactly the five completions printed for that row.
Cases2 and5 each contain three instances of this pattern. These are
why some surviving N forms have only three gates.

As an example of an impossible branch, case6 with base `04 18` needs
23, one of25 or56, and one of25 or57. Edge23 meets the first clause
and leaves only vertices5,6,7. The other clauses then respectively
require56 and57, whose intersection is empty. The last case6 row is
therefore impossible. Its other eleven rows fail by the same stated
intersection rule.

The complete tables yield the following exact families under the
listed necessary conditions:

| Case | Number of N forms |
|---:|---:|
| 1 | 4 |
| 2 | 21 |
| 3 | 4 |
| 4 | 1 |
| 5 | 21 |
| 6 | 0 |

All 51 forms are displayed in the appendix. They also satisfy every
listed demand, so the local tables give exact classifications for these
necessary conditions, although only coverage is needed for the proof.

## 4. Every remaining N has an isolated rank partner

After L4, exactly three layers remain: Q followed by two more layers.
A value on one wire after Q can reach at most four final positions.
Consequently it cannot attain five ranks over the full input domain.

For completeness, ranks attained on any fixed wire after any comparator
prefix form an interval. Input permutations are connected by swaps of
consecutive rank values. Identifying those two values commutes with
all min/max comparisons, so such a swap changes each fixed output by
at most one. Traversing a path between two endpoint inputs therefore
attains every intermediate rank. A gap of at least four is impossible
at the output of Q.

Use the nineteen concrete input permutations in the appendix. For any
wire i at the L4 cut, write l_i,h_i for its observed low and high ranks.
If h_i−l_i is at least four, Q must use i. A proposed partner j must
satisfy both threshold rules on every bank input x:

```
x_i <= h_i−4  implies  x_j >= h_i−3;
x_i >= l_i+4  implies  x_j <= l_i+3.             (4)
```

Indeed, in the first rule an anchor input makes the comparison's
maximum at least h_i. If both inputs were at most h_i−4 on another
input, that maximum would have a forbidden rank gap. In the second
rule an anchor makes the minimum at most l_i, so both inputs at least
l_i+4 similarly give a forbidden gap at the minimum output. The same
conditions must hold with i and j exchanged. This is the arbitrary-width
[threshold-partner lemma](h9_feedback_round5_rank_partner.md), here with
capacity four.

The appendix gives a mandatory pivot for each of the 51 N forms,
concrete inputs attaining its endpoints, and threshold guards excluding
its partners. A `lo` guard records the first rule in (4); a `hi` guard
records the second. The union of exclusions removes every partner
except the explicitly listed remainders. Eight further guards from
the candidate partners' side exclude those remaining edges by
reciprocity. Every pivot is therefore isolated in the necessary partner
graph. Since its observed span is at least four, it cannot remain idle.
No Q can exist.

These contradictions exclude all six M cases and hence the original
second layer `03 16 47`.

## 5. Fixed verification and scope

The [independent checker](verify/h9_feedback_round6_proof.py) imports
only Python's standard library. It reads the fixed certificate and
printed tables, and checks:

* the five-wire image symmetry, fork symmetry, named signed
  restrictions, and the fifteen-to-six third-layer orbit reduction;
* every demand by direct real-track replay, totalling 29,040 real-order
  assignments across the named restrictions and demand rows;
* all twelve base choices per case and all 152 local edge intersections;
* all 51 rank obstructions on the nineteen printed inputs, with 969
  prefix evaluations, 201 pivot guards, and eight reciprocal guards.

The checker also preserves a three-edge N example in its positive
control for optional completion. It performs no solver call, global
nine-wire matching enumeration, or rank-input search. Discovery scripts
are separate and are not proof dependencies. The immutable certificate
has SHA256

```
c258d102a019b789a5a01edfae1b410629d1e61f8a2ba3f1976e09c6eabf05ae
```

The [audit](results/h9-feedback-round6-proof.json) records the certificate,
printed-table, prose, and checker hashes. This proof uses H7, the
six-wire early profile, `D(5) >= 5`, the five-wire thin lemma, and the
rank-interval/threshold argument. It uses no unresolved merger theorem
or SAT result.
