# Two H9 classes closed by rescheduling real comparisons

The following two second-layer classes, with first layer `01 23 45`,
cannot extend to a seven-layer sorter on nine wires:

```
02 14 35
02 14 36
```

Together with the [three commuting-prefix cases](h9_feedback_commute.md),
these raise the hand coverage of H9 from 18 to **23 of its 50 classes**.
The argument below has a uniform finish; its twelve possible third
layers do not require separate case proofs. No SAT answer or exhaustive
enumeration is a premise.

Write `L2 = 02 14 3b`, where `b` is 5 or 6. A signed input `+i` or
`-i` holds the indicated infinity. Real tracks retain fixed labels as
in the commuting-prefix note; moving a real past a sentinel changes
its physical wire but does not compare it with another real.

## 1. Two rescheduling facts

**Four-gate obstruction.** If two sentinels leave at most four real-real
gates in the first three layers, and these gates can be rescheduled
into two layers by commuting disjoint real-track gates, the original
network cannot sort.

Indeed, pruning and rescheduling would give a seven-wire sorter in at
most six layers. Its first two layers contain at most four gates in
total, contradicting the [seven-wire early-profile theorem](h7-early-profiles.md):
both have at least two gates, and one has three.

To recognize a two-layer schedule, give each retained gate height one
plus the maximum height of earlier gates on either of its tracks;
initial track heights are zero. Gates of the same height are disjoint.
If the largest height is two, putting gates in their height layers is
a valid rescheduling. Untangling preserves all layer sizes.

**Six-wire profile.** A sorter on six wires in at most five layers has
first-two-layer sizes `(2,3)`, `(3,2)` or `(3,3)`.

*Proof.* If its first layer has at most one gate, one sentinel blinds
that layer, leaving five reals to be sorted in at most four layers,
contrary to `D(5) >= 5`. If its second layer has one gate, choose an
endpoint of that gate and a sentinel sign that keeps the sentinel on
that wire through layer 1. Pruning again leaves only four active
layers for five reals. An empty second layer is immediate.

If both layers have exactly two gates, their four-wire supports
intersect. Put a sentinel on a common wire with the sign that keeps
it there through the first layer. It removes a gate from both layers.
The five reals would have at most one gate in each of their first two
layers, contrary to README Lemma 3. □

Consequently, if three sentinels leave exactly two disjoint retained
gates through original layers 1–3, merge those gates into one layer.
The six reals would then have a five-layer sorter starting with two
gates. Its next layer, original `L4`, must pair up all six real positions.

## 2. A four-vertex path constrains the third layer

Each row below leaves two disjoint real-track gates in the first two
layers. Merge them into a first layer on seven reals. The seven-wire
profile forces three real-real gates in `L3`, after deleting the
specified sentinel positions.

The retained gates are labeled by their original real tracks, not by
their possibly changed physical positions after `L2`.

| `b` | Sentinels on inputs | Retained gates through L2 | Sentinel positions after L2 |
|---|---|---|---|
| 5 or 6 | `+1,+3` | `45,02` | `{4,b}` |
| 5 or 6 | `-2,-4` | `01,3b` | `{0,1}` |
| 5 | `-0,+5` | `23,14` | `{0,5}` |
| 6 | `+1,-2` | `45,36` | `{0,4}` |

By the deletion-pair lemma in the commuting-prefix note, `L3` must have
four gates and one idle wire `v`; deleting `v` from the graph of the
three listed pairs must leave a matching. That graph is a four-vertex
path:

* For `b=5`, its edges are `45,05,01`. Only its two internal vertices
  0 and 5 can be idle. Thus `L3` has either **idle 0 and gate 45**, or
  **idle 5 and gate 01**.
* For `b=6`, its edges are `46,04,01`. Only its internal vertices
  0 and 4 can be idle. Thus `L3` has either **idle 0 and gate 46**, or
  **idle 4 and gate 01**.

For `b=5`, negate values and reverse labels 0 through 5; reverse labels
6 through 8 as well. This preserves the first two layers and exchanges
the two alternatives. Untangle any reversed third-layer gates, which
only relabels subsequent layers. We may therefore assume idle 0 and
gate 45.

For `b=6`, eliminate idle 4 and gate 01 directly. Put `-0,+3` on the
inputs. The first two retained gates are `45` followed by `14`, and
the sentinel positions after `L2` are `{0,6}`. The real tracks whose
heights are two occupy physical wires 1 and 4. In the proposed third
layer, wire 4 is idle and wire 1 is paired with sentinel 0. Thus neither
height-two track takes part in a third-layer real-real gate. Deleting
sentinels 0 and 6 removes two different gates of `L3`, leaving two.
All four retained gates through `L3` have height at most two. The
four-gate obstruction rules out this alternative.

Hence for both values of `b` we may assume that `L3` has idle wire 0
and gate `4b`.

## 3. Gate 12 is excluded

Suppose `12` also belongs to `L3`. Put `+3,-4` on the inputs. The first
two retained gates are `01` followed by `02`. The sentinel positions
after `L2` are `{1,b}`, and the height-two real tracks occupy physical
wires 0 and 2.

Wire 0 is idle in `L3`; wire 2 is paired with sentinel 1. The sentinel
at `b` meets gate `4b`. Exactly two third-layer gates therefore compare
reals, and neither meets a height-two track. Again the first three
layers retain four gates with a two-layer schedule, a contradiction.

We have derived the complete remaining form:

> `L3` is `4b`, together with a perfect matching of
> `T = {0,...,8} \ {0,4,b}` that avoids `12`.

There are twelve such matchings: pair wire 1 with any of the four
members of `T \ {1,2}`, then pair the remaining four wires in any of
three ways. The proof below treats all choices together.

## 4. Two six-real restrictions finish every form

Let `1t` and `2u` be the third-layer gates containing 1 and 2. They
are different because `12` was excluded. Both `t` and `u` exceed 2.
Write `e` for the remaining gate besides `4b,1t,2u`.

Use the placements

```
P: -0,+3,-4
Q: +2,+3,-4.
```

For `P`, no two reals meet in the first two layers. Its sentinel
positions after `L2` are `-0,-1,+b`. Gate `4b` leaves `+b` in place,
gate `1t` leaves `-1` in place, and wire 0 is idle. Thus its real set
after `L3` is

```
R_P = {0,...,8} \ {0,1,b},
```

and its only retained gates through `L3` are `2u` and `e`, which are
disjoint. The six-wire profile forces `L4` to pair up `R_P`.

For `Q`, the only retained gate in the first two layers is original
gate `01`. Its two real output tracks occupy wires 0 and 4 after
`L2`; its sentinel positions are `-1,+2,+b`. In `L3`, gates `1t`
and `4b` keep their sentinels fixed, while `2u` moves `+2` to `u`.
The only new retained gate is `e`, which avoids both 0 and 4. The two
retained gates through `L3` are therefore disjoint. Its real set is

```
R_Q = (R_P \ {u}) union {0}.
```

The six-wire profile also forces `L4` to pair up `R_Q`. But their
intersection has five vertices. A matching pairing up both sets would
have to pair up their intersection: a vertex lying in both must have
its partner in both. An odd set cannot be paired up. This contradiction
finishes both second-layer classes. □

## 5. Direct verification

[`verify/h9_feedback_reschedule_proof.py`](verify/h9_feedback_reschedule_proof.py)
checks the displayed sentinel rows, the height-two schedules, the
four-vertex-path alternatives, and the duality. It independently
checks all 2,620 possible third layers against the stated necessary
conditions. It then checks the two six-real placements on all twelve
canonical third layers for each value of `b`, including direct runs
on every permutation of six distinct real values.

The [audit](results/h9-feedback-reschedule-proof.json) contains the
trace and schedule certificates, matching counts, direct-run count,
and source hash. No sorter or suffix is searched for by the verifier.

```sh
python3 depth-hand-proofs/verify/h9_feedback_reschedule_proof.py --out depth-hand-proofs/results/h9-feedback-reschedule-proof.json
```

The separate exploratory scripts `h9_feedback_reschedule*.py` produced
finite feedback for the remaining H9 classes. They suggested this
proof, but none of their screen counts is used as a premise here.
