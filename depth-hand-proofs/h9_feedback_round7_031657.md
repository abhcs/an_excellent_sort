# The H9 case `03 16 57`

No nine-wire depth-seven sorter begins with `01 23 45`, then
`03 16 57`. This proof closes one further H9 second-layer class.
It does not alone establish all of H9 or the D(11) lower bound.

Write `L1=01 23 45`, `L2=03 16 57`, M=L3, N=L4, Q=L5. The hypotheses
are those of H9: nine wires and at most seven layers. Delete universally
redundant comparators throughout. Retained gates always follow real-track
identities through deterministic sentinel routing.

We use the [H7 profile](h7-early-profiles.md), the
[six-wire profile](h9_feedback_reschedule.md#1-two-rescheduling-facts),
`D(5)>=5`, the five-wire thin lemma (README Lemma 3), and the
[rank-threshold lemma](h9_feedback_round5_rank_partner.md). The
[previous class](h9_feedback_round6_031647.md) supplies two complete
three-layer exclusions and the five-unused-wire intersection lemma.

## 1. Reversing the separate fork's polarity

The two-layer image on01236 is exactly

```
x0 <= x3,x6;   x1 <= x6;   x2 <= x3.
```

It is invariant under `σ=(1 2)(3 6)`, as proved in the previous class.
Here the independent fork457 has a maximum center7: its image is
exactly `x4,x5 <= x7`. For sufficiency, place `x4,x7,x5` on original
wires4,5,7; the two comparisons produce the desired vector. Its leaf
symmetry is `τ=(4 5)`. Either image symmetry can conjugate the entire
suffix; untangling all reversed gates preserves layer sizes and sorting.

The former proof used the same core and a minimum-centered fork. Its
structural reduction transfers with the following explicit restrictions.
All boundary positions and retained gates in this table are after L2.

| Name | Original sentinels | Boundary sentinels | Retained gates |
|---|---|---|---|
| A | `-0 +5` | `-0 +7` | `23,16` |
| P | `+0 +2 +5` | `+3 +6 +7` | none |
| D | `+0 +5` | `+6 +7` | `23,03` |
| E | `+0 +2` | `+3 +6` | `45,57` |
| F | `+0 +2 -4 -5` | `+3 -4 -5 +6` | none |
| B | `+0 +2 -4` | `+3 -4 +6` | `57` |

A leaves two disjoint gates. Collapse them into one layer; H7 requires
at least three M edges avoiding07. Thus M has three gates with0,7
idle, or four gates with idle0, idle7, or edge07.

P requires at least two M RR gates. Otherwise, after its two blinded
layers, a further sentinel blinds the only possible first gate on six
reals, leaving a forbidden four-layer five-wire sorter. D and E each
retain a two-gate chain. If their two height-two tracks miss the M RR
gates and only two such gates survive, the first three layers reschedule
into two layers with four gates total, contradicting H7.

For a three-gate M with0,7 idle, P forces36 or an idle among3,6. Use σ
to choose idle3 in the latter case. Under D, both height-two tracks0,3
then miss all RR gates, giving the contradiction just stated.

For a four-gate M with idle0, P forces37,36 or67; σ changes67 into37.
Again D has track0 idle and track3 blinded, with only two M RR gates.
For a four-gate M containing07, P forces36 or an idle among3,6. Use σ
to choose idle3; D blinds track0 on07 and leaves track3 idle or blinded
on36. These possibilities fail too. Therefore **M has four gates and
idle7**.

Suppose36 is absent. Under E, sentinels3,6 meet distinct M edges,
leaving two RR gates. Its height-two tracks are5,7. Since7 is idle,
if5 meets3 or6 the four-gate rescheduling contradiction applies.
By τ the same holds for4. After excluding the ordered pairs
`03,06,16,23,47,57`, the partner of3 lies in `{1,8}` and the partner
of6 in `{2,8}`. Restriction F would blind all three initial layers
unless45 is present. The only possibilities are

```
08 13 26 45;   02 13 45 68;   01 26 38 45.
```

Under P each retains exactly two disjoint gates,45 and the edge at0.
Under B the retained gates are old57 and the same edge at0. If u,v
are the final positive-sentinel positions from3,6, the sentinel sets
are `{7,u,v}` and `{4,u,v}`, with u,v in `{3,6,8}`. The two real
six-sets intersect in five positions. Collapsing their two disjoint
gates into one layer, the six-wire profile requires N to pair both
six-sets completely. Their odd intersection makes that impossible.
Thus **36 is present**.

M is therefore36 plus a perfect matching K of `{0,1,2,4,5,8}`, with7
idle. The two image symmetries act on K by the swaps1↔2 and4↔5.
Its fifteen matchings reduce to these six forms:

| Case | M |
|---:|---|
| 1 | `01 24 36 58` |
| 2 | `01 28 36 45` |
| 3 | `04 12 36 58` |
| 4 | `04 15 28 36` |
| 5 | `08 12 36 45` |
| 6 | `08 14 25 36` |

## 2. Two cases transfer by a three-wire sorting identity

On the three wires4,5,7, the comparator words

```
45;57;45       and       45;47;57
```

both output the three values in increasing order. Consequently, if M
contains45, the entire three-layer prefix here equals the previous
class's three-layer prefix obtained by replacing L2's57 by47 and M's45
by57. Every other comparator acts outside this triple and is unchanged.
This is equality of functions, not only equality of images.

Cases2 and5 are thus exactly the already excluded round6 cases2 and5.
No new fourth-layer enumeration or endpoint bank is needed for them.
Only cases1,3,4,6 remain.

## 3. The fourth layers

The [fixed appendix](h9_feedback_round7_tables.md) gives signed
five-real demands for these four cases.
A demand d retains exactly3−d RR gates through L3, with d=1 or2. N
must supply at least d edges inside the resulting real set: otherwise
at most two gates remain through L4, and scheduling them one each in
two layers before L5–L7 violates the five-wire thin lemma.
Universally ordered pairs in the appendix follow by elementary min/max
propagation and are forbidden in N.

### Cases1 and3: five-unused-wire intersections

Case1 requires two edges on01478; case3 requires two on23458. In each
set one pair is forbidden, leaving twelve possible two-edge bases.
After a base is chosen, five unused wires support at most two further
edges. Choose an edge e from a residual demand clause. Only three
vertices remain, so all unmet clauses must contain the same final
edge f. If a clause still demands two edges, or that intersection is
empty, the branch is impossible. If all clauses are already met, f is
optional. This is the previous proof's general intersection lemma.

The appendix prints all24 bases and their edge intersections. They give
six N forms in each case:

| Case | N forms |
|---:|---|
| 1 | `02 14 35 78`; `02 17 35 48`; `02 18 35 47`; `07 13 25 48`; `07 14 25 38`; `07 18 25 34` |
| 3 | `01 24 35 78`; `01 27 35 48`; `01 28 35 47`; `05 17 23 48`; `05 17 24 38`; `05 17 28 34` |

### Cases4 and6: the shared-triangle rule

The following rule gives a shorter classification. Suppose two real
five-sets are `T∪{a,b}` and `T∪{c,d}`, with T a three-set disjoint
from a,b,c,d, and each needs two matching edges. If ab is forbidden,
the matching must contain:

* an edge e inside T;
* the edge cd;
* an edge from the remaining vertex t of T to either a or b.

To prove this, the union has seven vertices. Without an edge inside T,
the four demanded edges would be distinct disjoint edges on that union,
which is impossible. Once e is chosen, each set still needs an edge,
on `{t,a,b}` and `{t,c,d}` respectively. Both cannot use t, so one
of ab or cd occurs. Since ab is forbidden, cd is forced, and the other
edge must be ta or tb. This necessary rule leaves only three choices
for e and two for t's partner.

For case4 the two demand-two sets are34568 and24578. For case6 they
are34568 and04578. In both cases T=458 and ab=36 is forbidden.
Thus case4 forces27 and case6 forces07; the remaining T vertex t
meets3 or6. The following demand-one contacts force the fourth edge
and then force t to meet3. Row numbers refer to the appendix.

| Case | e | t | Contact forcing fourth edge | Fourth edge | Contact forcing3t |
|---:|---|---:|---:|---|---:|
| 4 | 45 | 8 | 4 | 01 | 6 |
| 4 | 48 | 5 | 2 | 01 | 5 |
| 4 | 58 | 4 | 2 | 01 | 5 |
| 6 | 45 | 8 | 2 | 12 | 5 |
| 6 | 48 | 5 | 3 | 12 | 6 |
| 6 | 58 | 4 | 2 | 12 | 5 |

For example, case4 with e45 must contain27 and either38 or68.
Contact01248 (row4) contains no complete edge among those, and the
only permitted extra edge meeting the contact is01. Contact02358
(row6) then forces38. The other five rows use the same one-edge check.

Therefore case4 has `N=01 27+J`, and case6 has `N=07 12+J`, where J
is one of the three perfect matchings of3458. There are three forms
in each case, for a total of eighteen new N forms.

## 4. Two untouched-sink contradictions

Two of the eighteen forms have a short H7 rescheduling obstruction.

| Case | M | N | Original sentinels | Sentinel positions after M | Retained old gates at the M boundary | N RR gates | Untouched old sink |
|---:|---|---|---|---|---|---|---|
| 1 | `01 24 36 58` | `02 17 35 48` | `-0 -7` | 05 | `23,47,16,24,36` | `17,48` | 36 |
| 3 | `04 12 36 58` | `01 27 35 48` | `-0 +4` | 07 | `23,16,12,36,58` | `35,48` | 12 |

The five old gates have real-track height two. In each row the two
N RR gates are disjoint from the indicated old sink. Move these three
sink gates into a third layer. The other four gates can be placed in
their original height-one or height-two layers, since no moved gate
has a successor among them. Original L5–L7 then yield a seven-wire
sorter in six layers with at most four gates in its first two layers,
contradicting H7.

The sink statement uses moving real identities. A blind N gate can
route a track but does not create a real-real dependency. Therefore
an old sink remains a sink exactly when none of its tracks meets an
N RR gate, as recorded in the table.

## 5. The other sixteen endings

For every other N form the appendix supplies an isolated mandatory
Q pivot, using concrete input permutations and the threshold-partner
lemma with capacity four. A pivot whose observed span is at least four
cannot be idle: the attainable-rank interval would contain at least
five ranks, but only two layers would remain after Q.

If its observed endpoints are l,h, an input with pivot rank at most
h−4 forces any partner rank to exceed h−4; an input with pivot rank
at least l+4 forces any partner rank to be below l+4. Each condition
comes from the rank gap at the maximum or minimum output of the
comparison. Reciprocal conditions from candidate partners apply too.
The fixed guard unions in the appendix exclude every partner, leaving
no possible Q.

These rank contradictions and the two sink restrictions eliminate all
eighteen new N forms. Together with the functional transfer of cases2
and5, they exclude the whole H9 class `03 16 57`.


## 6. Fixed verification and proof dependencies

The [independent checker](verify/h9_feedback_round7_proof.py) imports
only the Python standard library. It reads the fixed certificate and
printed premises, with no discovery imports, global nine-wire matching
scan, rank-input search, or solver call. It checks:

* the named signed restrictions and fifteen-to-six M orbit reduction;
* equality of the two three-wire sorting words and the accepted
  round6 certificate hash for the two transferred cases;
* 29 signed demand rows, 24 five-vertex base cases with40 local edge
  branches, and all six shared-triangle contact rows;
* the two sink reschedulings, with 34,560 direct real-order replays
  across all signed restrictions and demand rows;
* nineteen concrete rank inputs for the sixteen endings:304 prefix
  evaluations,64 pivot guards, and nine reciprocal guards.

The reusable additions are the polarity transfer for the independent
fork, the shared-triangle matching rule, and the old-sink version of
H7 rescheduling. The only prior whole-case dependency is the two
explicit round6 three-layer forms transferred in §2. All remaining
contradictions use the hand early profiles, the five-wire thin lemma,
and rank intervals. No unresolved computer search is a premise.

The fixed certificate SHA256 is

```
d9237f438467d95088717b2016cc8734453ea62f4540f3ecbe48994a9cc6ca60
```

The [audit](results/h9-feedback-round7-proof.json) records this hash and
the hashes of the printed table, proof note, and checker. Discovery
runs were bounded and finished normally; no solver was used.
