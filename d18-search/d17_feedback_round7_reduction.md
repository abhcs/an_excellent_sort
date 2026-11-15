# A width-independent finite-assisted obstruction for the full case-606 family

**Theorem, with explicit finite premises.** Let the five A coordinates have
sentinel pairs

    AB, BC, CE, BD,                 A-,B-,C+,D+,E+,

and let the seven B coordinates have sentinel triples

    qab, qbc, qce, rce, qbd,         q-,a-,b-,c+,d+,e+,r+.

Take all twenty products of these choices and add any number t>=0 of
common real coordinates. In any physical embedding of the labels, no two
matching layers give at least floor((7+t)/2) real-real comparisons in one
of the layers for every state. Comparators and retained layers may be
empty or repeated; the count in the second layer is taken after exact
signed transport through the first.

This note closes the noncritical branch by a hand reduction to **86,370
canonical first matchings** and a separately checked finite arithmetic
certificate. Together with the accepted critical-dc result from
[round six](d17_feedback_round6_reduction.md), it proves the stated
family obstruction. The finite classifications in rounds five, six,
and seven remain premises: this is **not a fully symbolic hand proof**.
No SAT solver is used by the present certificate or its independent
checker. No global D17 or D18 lower bound follows merely from closing
this one signed family.

## 1. Even width, the remaining branch, and safe contraction

First take even active width n=12+t=2h, so t is even. Each state has five
sentinels and 2h-5 reals, and its peak is h-3 real-real gates. Fill the
second counted matching N to be perfect. A second-layer peak is equivalent
to two N-edges inside its transported five-sentinel set.

The [round-two normalization](d17_feedback_round2_normalization.md)
augments comparisons between universally comparable idle type coordinates
and excludes the possible four-idle antichains. Thus any cover has a
normalized first matching M that is perfect or has exactly two idle wires.
The critical branch dc is already excluded by round six. Here assume
dc is absent. Since d,c are incomparable over the full twenty states,
comparable-idle augmentation cannot introduce dc.

Use the external-common-real contraction from
[round five](d17_feedback_round5_reduction.md#1-safe-contraction-of-common-real-partners),
with its deficit-preserving extension from
[round six](d17_feedback_round6_reduction.md#4-contraction-preserves-the-two-idle-deficit).
For clarity, its hypotheses and effect are:

* An M-edge between two common reals can be deleted with its endpoints.
  Width drops by two, |M| drops by one, and the peak drops by one.
* If M contains u--r and v--s with common reals r,s, and the one-sided
  type coordinates u,v are universally comparable, replace those two
  gates by u--v and delete r,s. The old first-layer RR contribution is
  2,1,0 when both, one, or neither of u,v is real; the new contribution
  is 1,0,0. Its loss is at most the one-unit decrease in the peak.
* In either contraction, fixed type routings identify two always-real
  output tracks to remove from N. No SS edge is lost. Pull the remaining
  N edges through the fixed routing of the new gate, then complete N.
  All old second-layer peaks survive because they retain two SS edges.

These operations preserve the deficit h-|M| and all peak coverage.
They concern the two layers of type counts, not the sorting function of
an entire network. Every comparability test here uses **all twenty
states**. No B column is omitted or treated as constant merely because
it was constant in a selected subfamily. Since d,c are incomparable,
the contractions also preserve the absence of dc.

## 2. Hand width bound: only twelve, fourteen, or sixteen active wires

Write E for the set of variable coordinates whose M partners are common
reals. Delete every common-real M-pair and contract comparable members
of E until E is an antichain of the full-family type order. The type
order has width four, as proved in round two; its maximal four-element
antichains are

    {D,X,d,y},       X in {C,E}, y in {c,e,r}.

Thus |E|<=4. A normalized two-idle matching has no common-real idle,
because a common real is comparable with every one-sided coordinate.
Its two idle variable coordinates form an incomparable pair. A perfect
matching has no idles. If I is the idle set, the other 12-|I|-|E|
variable coordinates are internally paired. Both 12 and |I| are even,
so |E| is even. Therefore the reduced active width is exactly

    n = 12+|E| in {12,14,16}.                       (1)

The external partners are distinct common reals; give them labels
12,13,... in increasing order of their variable partners. A common
permutation of physical labels preserves this pure two-layer count
property: reorient each first comparator and absorb its fixed output
swap into N. The last counted layer's orientation does not affect its
incoming RR counts. Thus this canonical labeling loses no physical
embedding or routing choice.

The following description is a complete finite cover of the normalized
noncritical branch, including zero A--B comparisons:

1. Choose I empty, or any incomparable pair of the twelve variables.
2. Choose E disjoint from I, of size zero, two, or four, pairwise
   incomparable over the full twenty states.
3. Pair every remaining variable internally, excluding dc; pair each
   E coordinate to its canonically labeled common real.

There are twenty-three incomparable variable pairs: two within A, three
within B, and eighteen across A/B. There are six four-antichains. The
finite checker enumerates every actual pairing in the description above;
the following counts are part of its checked coverage, not an extrapolation
from a width-fourteen scan.

| First matching | Width 12 | Width 14 | Width 16 | Total |
|---|---:|---:|---:|---:|
| Perfect | 9,450 | 20,265 | 630 | 30,345 |
| Two idles | 20,265 | 35,040 | 720 | 56,025 |
| Total | 29,715 | 55,305 | 1,350 | **86,370** |

In particular, the list includes 2,700 zero-cross cases. They were not
assumed closed by the earlier same-block-idle lemma. No restriction on
the number of A--B gates, nonempty layers, or repeated gates is imposed.

## 3. Hand inference rules: full rows and five-set boundaries

For a particular first matching, let a required state mean one with
fewer than h-3 first-layer RR gates. Its transported five-sentinel set
S must contain two N-edges.

The corrected full-row lemma from
[the B-family note](d17_feedback_fourteen_hand_Blemma.md#5-corrected-row-consequence-for-the-full-fourteen-wire-family)
applies because dc is absent. Fix an A row that is required in all five
B columns. Its A types are constant, so every A/B comparison has fixed
type routing within the row. The only nonfixed B/B gates can be de or dr;
the exact five-column classification covers both. If the transported
sets, in column order, are S0,...,S4, their unique forced three-edge core is

    T, (S0 intersect S1) minus T, (S2 intersect S3) minus T,
    where T = intersection of all five sets.         (2)

Each displayed set has two elements; the six endpoints are distinct.
These are the row's transported A pair, qb pair, and ce pair. Forced
cores from different rows may directly conflict at a vertex.

For a compatible partial matching K of already forced N-edges, two
elementary rules suffice for the remaining certificates:

**Boundary contradiction.** If a required five-set S has two K-edges
crossing its boundary, no completion of K can give it two internal
edges. Indeed two internal edges use four of S's five vertices, leaving
room for at most one boundary edge. Equivalently, the internal-edge cap
is |K inside S|+floor(|S minus endpoints(K)|/2).

**Forced pair.** If K has one internal edge in a required S and exactly
two S vertices remain unused, those two vertices must be paired.

When neither rule finishes a case, split on the internal N-edges still
needed by one required five-set. For an empty K, there are exactly fifteen
choices: choose the one unmatched S vertex and one of the three perfect
matchings of the remaining four. More generally, if one internal edge is
already known, choose the one additional edge from its unused vertices.
This split is complete because a five-set has at most two internal
matching edges. It is a local branch on at most five vertices, not an
enumeration of all final matching layers.

## 4. Complete finite certificate and independent coverage check

[`d17_feedback_round7_certificate.py`](d17_feedback_round7_certificate.py)
generates the canonical forms using the I/E antichain description,
computes exact signed first-layer transport, and records the preceding
row cores and arithmetic inferences. The certificate is stored as a
compressed JSON file:

[`d17-feedback-round7-core-certificate.json.gz`](results/d17-feedback-round7-core-certificate.json.gz).

It is 529,460 bytes compressed, or 4,807,564 bytes as JSON. Each first
matching is encoded by its partner vector in hexadecimal, using a
coordinate's own label for an idle. The vector's length gives the width.
The row mask identifies initial cores; each proof node records forced
state indices, then a boundary contradiction or a complete local split.
It can be inspected with Python's standard `gzip` and `json` modules.

The independent checker
[`d17_feedback_round7_check.py`](d17_feedback_round7_check.py) imports no
generator, discovery code, prior checker, or SAT package. It first
reconstructs and verifies the exact signed twenty-state input family.
It enumerates coverage by a different recursion: process the least
remaining variable, pairing it internally, making it idle, or assigning
it to the next external common-real label, while checking the relevant
antichain conditions. It proves uniqueness and equality between this
independent set and the certificate's entire list of first matchings.

For every case it recomputes first counts and exact signed transport,
checks the full-row hypotheses and forced core positions, and replays
the proof. Local branch completeness is checked by independently
enumerating disjoint edges on the unused vertices of the chosen five-set.
At each terminal arithmetic node it uses the crossing-edge criterion,
rather than the generator's internal-edge capacity calculation. A
conflicting collection of forced full-row cores is also a valid terminal
contradiction. These checks still invoke the hand necessity of (2);
they do not mistake a merely sufficient row core for a forced one.

The [independent report](results/d17-feedback-round7-core-check.json)
is **VERIFIED** for all 86,370 cases:

* 83,642 cases have a full required A row and need no branch. Of them,
  71,098 already have conflicting forced full-row cores; the rest end
  in boundary contradictions, with forced pairs where needed.
* 2,728 cases have no full required row. All begin with a fifteen-way
  five-set split. Only four perfect cases need one further three-way
  split. No proof tree has branch depth above two.
* In total there are 127,302 proof nodes, 2,732 branch nodes, and 2,648
  forced-pair inferences. The zero-cross cases are included throughout.

Certificate SHA-256:
`15af56696fc7dfb93aa70d287601e4fd819784d016e3af2699868681f0af558b`.
Independent checker SHA-256:
`a94251729c38b4d28c91b9dbd34ccfa59da7b1e9be56bb8f48f7e1c035754ddb`.
Exact input SHA-256:
`168d10b515cdc3552264089fa1b5eeaefd8ed635dc1630e5d53973abe44f6372`.

Generation took 4.14 seconds and checking 3.58 seconds, each under a
separate thirty-second limit and with exit zero. Their
[generation terminal record](results/d17-feedback-round7-certificate-terminal.json)
and [checking terminal record](results/d17-feedback-round7-check-terminal.json)
are saved. All exploratory screens are terminal too. Their counts and
feedback are not substituted for this coverage-complete verification.

The 86,370-case arithmetic verification is an explicit finite premise
of the noncritical theorem. Compressing it into a symbolic classification
of the partial-row patterns remains meaningful work; this note does not
call the resulting proof purely hand-derived.

## 5. Odd width, fixed sentinels, and the exact remaining scope

For odd active width n>=13, add one common real coordinate and leave it
idle in both counted layers. The even width becomes n+1, while the
required peak remains floor((n-5)/2): the original even number of reals
becomes odd, without increasing its maximum matching size. Thus an
odd-width cover would contradict the even-width theorem. This proves
the opening statement for every t>=0, not only even t.

The family can also be embedded among any common fixed signed sentinels,
using the proved
[fixed-sentinel pruning lemma](fixed-sentinel-obstruction.md).
Removing these fixed coordinates preserves the pure two-layer RR-count
cover question. A simultaneous flip of all sentinel signs also preserves
the obstruction: each first comparator's outputs are exchanged relative
to the negated types, a fixed permutation that is absorbed into N.

Consequently the theorem supplies a reusable test: if a transported
restriction family contains a copy of these twenty signed states, up to
one common coordinate permutation and optional global sign flip, with
all remaining coordinates common reals or common fixed sentinels, then
two matching layers cannot reach the real-wire maximum in every state.
This is a sufficient embedding condition. Arbitrary projections,
state-dependent permutations, or changing individual sentinel signs
are not covered by it.

Combining the noncritical closure here with the accepted critical closure
from round six gives a finite-assisted proof of the full case-606 signed
family obstruction, independently of the old universal SAT certificate.
The hand reductions apply at arbitrary width; the finite premises are
the explicitly bounded arithmetic classifications after those reductions.
To derive a network-depth lower bound, one must still establish the
appropriate restriction family at the chosen prefix and the separate
hand or certified statement that its surviving tail needs the tested
two-layer peak. No new full D17 cover count or D18 cover closure is made
here.

## 6. Direct embedding audit of the 609 D17 two-layer cover cases

The small SAT-free audit
[`d17_feedback_round7_embedding.py`](d17_feedback_round7_embedding.py)
recomputed the complete half-blind nine-real families for all 609 supplied
two-layer cover cases. It found no new direct embedding:

* Cases 0 through 605 have fewer than twenty distinct states, and therefore
  cannot contain this twenty-state family under a common coordinate map.
* Case 606 has exactly the expected embedding, with the base twelve labels
  mapping to original wires 4,5,6,7,8,10,11,12,13,14,15,16; wires 1,2 are
  common reals and 0,3,9 are common negative sentinels.
* Case 607 has only ten variable coordinates, whereas this family requires
  twelve. Its separate signed-fork obstruction is already proved by hand.
* Case 608 has twelve variable coordinates but a different multiset of
  negative/positive counts over its twenty states. In particular it has
  no state with five positive variable sentinels, whereas case 606 has
  both an all-positive and an all-negative state. Neither a coordinate
  permutation nor a global sign flip can fix this mismatch.

The [audit](results/d17-feedback-round7-embedding.json) completed in
0.136 seconds under its thirty-second limit; its
[terminal record](results/d17-feedback-round7-embedding-terminal.json)
is saved. This is an exact negative result for the stated direct
signed-family embedding test. It does not rule out stronger applications
using different restriction sizes, other prefix cuts, or a new structural
lemma for a proper subfamily. The new width-independent theorem is thus
available as a D18 target, but it does not immediately enlarge the known
D17 complete-cover exclusions.
