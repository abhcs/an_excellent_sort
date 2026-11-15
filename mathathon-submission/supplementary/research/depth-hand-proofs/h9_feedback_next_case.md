# A twenty-fourth H9 hand case

No seven-layer sorting network on nine wires has

```
L1 = 01 23 45,
L2 = 03 14 26.
```

This is a further class beyond the previous 23 hand cases. The proof
uses three commuting two-sentinel restrictions, one blind six-real
restriction, and one rescheduling. No SAT result or enumeration is
a premise.

## 1. Three deletion pairs force two alternatives

The following placements leave two disjoint retained real-track gates
through the first two layers. Track labels refer to the original inputs;
sentinel comparisons may move their physical positions.

| Sentinels on inputs | Retained gates through L2 | Sentinel positions after L2 |
|---|---|---|
| `+1,+3` | `45,26` | `{3,4}` |
| `+1,-2` | `45,03` | `{2,4}` |
| `+3,-4` | `01,26` | `{1,3}` |

Merge each pair of disjoint gates into a single first layer on seven
reals. The resulting network would have at most six layers. By the
[seven-wire early-profile theorem](h7-early-profiles.md), its second
layer must have three gates. Thus deleting each of the three displayed
sentinel pairs must leave at least three edges of the original `L3`.

The deletion graph has edges `34,24,13`, forming the path `2-4-3-1`.
The [deletion-pair lemma](h9_feedback_commute.md) says that `L3` has four
gates and one idle vertex, and that deleting this vertex from the path
must leave a matching. Therefore precisely these two alternatives remain:

* wire 4 is idle and `13` is a gate;
* wire 3 is idle and `24` is a gate.

## 2. Six reals force another gate

Put negative infinities on inputs 0, 2 and 4. Both first layers are
blind. After `L2` the sentinels occupy 0, 1 and 2; the six real
positions are 3 through 8.

A six-wire sorter of depth at most five must have at least two gates
in its first layer. Otherwise one further sentinel blinds that layer,
leaving five reals to be sorted in four layers, contrary to `D(5)>=5`.
Hence `L3` must have at least two real-real gates in this restriction.

In either alternative from Section 1, all three sentinel positions
0, 1, 2 are used by `L3`. If they occupied three different gates, only
one of the four gates would compare two reals. Therefore two of these
sentinels must be paired together.

In the first alternative, gate `13` already uses sentinel position 1,
so the sentinel pair must be `02`. In the second, gate `24` already
uses position 2, so it must be `01`. The complete remaining form is
therefore

```
L3 = 02 13 K, with wire 4 idle,
or
L3 = 01 24 K, with wire 3 idle,
```

where `K` is any perfect matching on `{5,6,7,8}`.

## 3. One rescheduling finishes both forms

Put negative infinities on inputs 2 and 4. The first two retained
gates are original `01` followed by `03`. After `L2`, the sentinels
are on wires 1 and 2; the real tracks used by those two gates occupy
wires 0, 3 and 4.

In either displayed third-layer form, both non-K gates meet a
sentinel. The only retained third-layer gates are precisely `K`.
Their tracks 5, 6, 7, 8 are disjoint from both earlier retained gates.
Commute K to the first retained layer. On seven reals the first three
original layers become

```
01 K | 03,
```

with gate counts `(3,1)`. Together with the four remaining layers this
would sort seven reals in at most six layers. Sentinel pruning and
untangling preserve these gate counts, as detailed in the earlier
[commutation proof](h9_feedback_commute.md). Lemma Q7 forbids a
one-gate second layer in a six-layer seven-wire sorter. Contradiction. □

This proves one additional representative and raises H9 hand coverage
to **24 of 50**. It does not settle the remaining 26 classes or turn
the complete D11 lower bound into a hand proof.

## Verification

[`verify/h9_feedback_next_proof.py`](verify/h9_feedback_next_proof.py)
checks all five placements and the three path constraints. As an
independent finite cross-check, it considers all 2,620 third-layer
matchings: 30 satisfy the path constraints, and exactly six also
satisfy the six-real first-layer bound. These are exactly the two
derived forms with the three matchings K. All six yield the displayed
`(3,1)` rescheduling. Direct runs on every ordering of the remaining
real inputs verify the track routing and rescheduling.

The [audit](results/h9-feedback-next-proof.json) contains every trace,
count, direct-run total and the checker source hash.

```sh
python3 depth-hand-proofs/verify/h9_feedback_next_proof.py --out depth-hand-proofs/results/h9-feedback-next-proof.json
```
