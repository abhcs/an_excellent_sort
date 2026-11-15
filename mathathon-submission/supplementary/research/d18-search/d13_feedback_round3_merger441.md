# Two singleton inputs force a five-layer4+4+1 merger

**Theorem.** Merging independently sorted blocks of lengths4,4,1 needs at
least five comparator layers. This has a short hand proof using only the
cone bound and `D(3)>=3`. No SAT result or H9 case is a premise.

## 1. A sorted triple and two singletons need four layers

Suppose three layers merge a sorted triple `a0<a1<a2` and two independent
singleton inputs `u,v`. Remove all first-layer comparators internal to the
triple, since they are redundant.

Both singleton inputs must be used in the first layer. If one were idle,
it would have only two layers left to reach all five possible output ranks,
whereas its forward cone contains at most four positions.

There are only two cases.

* If `u,v` are paired with each other, the remaining two layers must merge
  sorted blocks of lengths3 and2. Their median, rank2 with zero-based ranks,
  can initially be on **each of the five positions**. A two-layer backward
  cone contains at most four positions, so this is impossible.
* Otherwise `u,v` are paired with two distinct positions of the triple.
  Put negative infinities on those paired triple positions below the one
  unpaired position, and positive infinities on those above it. This
  respects the triple order. The first layer is blind on the three remaining
  arbitrary reals: `u,v` and the unpaired triple input. Two layers would
  then sort three arbitrary reals, contradicting `D(3)>=3`.

Thus a `3+1+1` merger needs at least four layers. In the first case, the
five possible median positions can also be seen from the attainable-rank
intervals of a sorted3-block and a sorted2-block: all five contain rank2.

## 2. The4+4+1 contradiction

Suppose four layers merge sorted blocks `A=a0<a1<a2<a3`,
`B=b0<b1<b2<b3`, and singleton `c`. Let `N` be the first merger matching,
and delete all its edges internal to either sorted block.

The singleton `c` must be used in `N`: otherwise its nine possible ranks
would have to reach nine outputs through only three layers, whose forward
cone has size at most eight. By exchanging the two four-blocks if needed,
assume `N` pairs `c` with `a_j`.

Fix any of the **three** other A-positions `a_i`, with `i!=j`. Keep `a_i`,
`c`, and either consecutive triple of B real:

```
{b0,b1,b2} or {b1,b2,b3}.
```

Put negative infinities below `a_i` in A and positive infinities above it;
set B's omitted endpoint to the appropriate infinity. These are valid
restrictions of the sorted-block family. They leave a sorted triple and
two arbitrary singletons. If `N` retained no comparison on them, the three
remaining layers would merge `3+1+1`, contrary to Section1.

The edge incident with `c` is blind, because its partner `a_j` is now a
sentinel. There are no internal B edges. Hence the only possible retained
edge is from `a_i` to a vertex of the selected B triple. The same partner
must work for both triples, so

```
partner_N(a_i) lies in {b1,b2}.
```

This holds for three distinct A-positions, which require three distinct
partners in a two-element set. Contradiction. □

The proof is invariant under fixed embeddings of the blocks: relabel and
untangle the whole merger. It covers nonperfect first matchings and does
not fill a middle layer.

## 3. A component criterion with no small-partition exceptions

Together with the hand proofs for
[4+3+2](../depth-hand-proofs/h9_feedback_round2_merge432.md) and
[3+3+3](../depth-hand-proofs/h9_feedback_round3_merge333.md), this gives a
uniform structural consequence:

> In a sorting network with four layers remaining, every restriction to
> nine arbitrary real inputs has a retained interaction component of size
> at least five before those four layers.

Here the graph joins logical real tracks whenever they have compared
before the cut. Sentinel comparisons only route those track labels. If
every component had size at most four, its component-size partition could
be packed into one of `4+3+2`, `3+3+3`, or `4+4+1`:

* Two parts of size4 give exactly `4+4+1`.
* Exactly one part of size4 leaves five vertices in parts of size at most3;
  these can be grouped into3 and2.
* With no4 and three3s, the partition is `3+3+3`.
* With two3s and smaller parts, combine one3 with a1 into4, keep the other3,
  and use the remaining two vertices for2.
* With one3, split the remaining1s and2s into4 and2. With no3 or4, first
  form3 from a2 and a1, or from three1s, then split the remaining six into4
  and2.

After relabelling and untangling, the prefix has no comparisons between
these packed blocks. It fixes every input sorted independently within
each packed block. Consequently its image contains the full corresponding
merger family, and four remaining layers contradict one of the three
hand merger theorems. This transfer does not assume that the interaction
components have themselves been sorted by the prefix.

For a hypothetical depth-eight D13 sorter the cut is after layer4. For a
hypothetical depth-ten D18 sorter it is after layer6. The criterion is
necessary for every continuation, but applying it to a chosen partial
network is not a closure of its whole two-layer cover case.

## 4. Bounded feedback and direct checks

Before the hand proof was found, tiny SAT feedback refuted the two proposed
short mergers. The independent bare encodings use only arbitrary matching
layers and ordinary comparison semantics, with **no ending or redundancy
normal forms**. They have50 binary inputs for441 and16 for311. The solver
subprocesses exited normally under30-second caps in0.20 and0.07 seconds
including process overhead. These computations are corroboration, not
premises of the proofs above.

The bare encoder is [d13_feedback_round3_merger_bare.py](d13_feedback_round3_merger_bare.py).
The local checker [d13_feedback_round3_merger_verify.py](d13_feedback_round3_merger_verify.py)
audits all six ordered singleton-to-triple pairings in Section1, explicit
median-position witnesses for the3+2 family, and the component-partition
classification. It also independently checks the two already generated
small DRAT certificates with30-second checker caps.

An earlier native-model setup attempt stopped on an assertion because
already-sorted inputs must be omitted from that API's `add_input` call.
The corrected attempt also returned UNSAT, and the independent bare model
confirmed it. All attempt statuses are retained under
`results/d13_feedback_round3-merger*-terminal.json`; no timeout was called
UNSAT and no solver is left running.
