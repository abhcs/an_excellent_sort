# Three more hand cases of H9 by commuting retained gates

Fix the first layer to `01 23 45`, with wires 6, 7 and 8 idle, as in
[H9](h9.md). Here `ij` means the comparator `(i,j)`. None of these three
second layers extends to a seven-layer sorter:

```
03 67
06 17
03 46 57
```

These are three of the 32 classes outside the previous hand coverage.
They raise that coverage from **18 to 21 of the 50 classes**. The proof
uses the [seven- and eight-wire early-profile hand results](h7-early-profiles.md),
sentinel pruning, and a matching argument. There is no SAT or exhaustive
search premise.

## 1. Commuting retained gates forces the next layer

Put one or two sentinels on a proposed seven-layer nine-wire sorter.
Trace the real wires through the first two layers, deleting every gate
that meets a sentinel. A gate with a sentinel moves its real value in a
fixed direction, independent of that value. Thus one can follow fixed
**real tracks** through those movements. A real-real comparator acts on
the two tracks arriving at its endpoints. Its outputs continue along
those same two tracks; their values have been compared, but no
data-dependent relabeling of tracks is made.

Suppose that all retained gates in the first two layers involve disjoint
pairs of these tracks. They commute, so combine them into a single first
layer. The retained network now has at most six layers. As in README
Tool C, untangle its generalized comparators and final fixed permutation;
this preserves every layer's gate count. Its second layer has exactly
the number of real-real gates in the original third layer.

The early-profile results therefore give:

* With **one sentinel and three disjoint retained gates**, the original
  third layer has four real-real gates. It pairs up the eight real
  positions, so its unique idle wire is the sentinel position.
* With **two sentinels and two disjoint retained gates**, the original
  third layer has three real-real gates.

These statements use the profiles `(3,4)` for an eight-wire sorter with
three gates first, and `(2,3)` for a seven-wire sorter with two gates
first. Empty layers cause no difficulty: a network with at most six
layers can be padded at its end before applying those results.

In the tables below the displayed retained pairs are already disjoint
real tracks labeled by their original input wires. No endpoint of a
retained gate from layer 1 moves through a sentinel in layer 2. This
also makes the commutation visible directly, without computing a
generalized network.

## 2. Two different forced idle wires

For `L2 = 03 67`, use these one-sentinel placements:

| Sentinel on input | Retained gates in L1 | Retained gates in L2 | Sentinel after L2 |
|---|---|---|---|
| `-0` | `23 45` | `67` | 0 |
| `+3` | `01 45` | `67` | 3 |

Each row has three disjoint retained gates. The preceding argument
forces the third layer's unique idle wire to be both 0 and 3, a
contradiction.

For `L2 = 06 17`, the same argument uses:

| Sentinel on input | Retained gates in L1 | Retained gates in L2 | Sentinel after L2 |
|---|---|---|---|
| `-0` | `23 45` | `17` | 0 |
| `+1` | `23 45` | `06` | 7 |

The second row's sentinel moves from 1 to 7 through `17`; this move
involves none of the displayed retained gates. The two rows force idle
wires 0 and 7, again impossible.

## 3. A reusable deletion-pair obstruction

**Lemma.** Let `M` be a matching on `2r+1` wires, and let `G` be a graph
whose edges specify pairs of wires to delete. Suppose that deleting
the two endpoints of every edge of `G` must leave at least `r-1`
edges of `M`. If `G` uses at least four vertices, then `M` has `r` edges,
with one idle vertex `v`, and `G-v` must be a subgraph of `M`.

*Proof.* A matching with fewer than `r-1` edges cannot meet even one
requirement. If it has exactly `r-1`, every specified deletion pair
must avoid all its endpoints. But it has only three idle vertices,
too few to contain the at least four vertices of `G`.

Thus `M` has `r` edges. Deleting a pair must remove at most one edge of
`M`. This happens precisely when the pair contains its idle vertex
`v`, or is itself an edge of `M`. Every edge of `G-v` is consequently
an edge of `M`. In particular, `G-v` must be a matching. □

**Corollary.** The four pairs in a copy of `K2,2` cannot all meet these
requirements. Deleting any vertex of `K2,2` leaves two edges with a
common endpoint; deleting a vertex outside it leaves the whole cycle.
Neither remaining graph is a matching.

Apply this to `L2 = 03 46 57` and the following four placements:

| Sentinels on inputs | Retained gate in L1 | Retained gate in L2 | Sentinel positions after L2 |
|---|---|---|---|
| `-0,-4` | `23` | `57` | `{0,4}` |
| `-0,+5` | `23` | `46` | `{0,7}` |
| `+3,-4` | `01` | `57` | `{3,4}` |
| `+3,+5` | `01` | `46` | `{3,7}` |

Every row has two disjoint retained gates. The seven-wire profile
forces at least three real-real gates in the original third layer.
Equivalently, deleting each of the four indicated pairs must leave
at least three edges of that layer. With `r=4`, the deletion graph is
the four-cycle with bipartition `{0,3}` and `{4,7}`. The corollary
excludes it. This finishes all three classes. □

## 4. Verification and scope

[`verify/h9_feedback_commute_proof.py`](verify/h9_feedback_commute_proof.py)
checks the eight displayed rows by following sentinel states and
fixed real tracks. Independently, it evaluates the original prefix
and the merged retained layer on all permutations of distinct real
values: 181,440 direct input checks. It also checks all 2,620 possible
third-layer matchings for each class, verifies that the representatives
occur in H9's 50-class list, and checks disjointness from the explicitly
listed previous 18 hand cases. The resulting
[audit](results/h9-feedback-commute-proof.json) records the rows and counts.
These computations check the displayed hand proof; they do not supply
an omitted classification argument.

Run from the repository root:

```sh
python3 depth-hand-proofs/verify/h9_feedback_commute_proof.py --out depth-hand-proofs/results/h9-feedback-commute-proof.json
```

The exploratory script `verify/h9_feedback_commute.py` also screens
the 50 second-layer representatives using all one- and two-sentinel
placements with commuting retained gates. This particular screen
finds exactly the three new cases above. Further cases require
additional reasoning; the full H9 statement remains computer-assisted.
