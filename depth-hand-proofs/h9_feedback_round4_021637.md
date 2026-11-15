# The H9 case `02 16 37`

This hand proof excludes a seven-layer nine-wire sorter starting
with `L1=01 23 45`, `L2=02 16 37`. Its finite tables are in the
[certificate appendix](h9_feedback_round4_tables.md). The dependencies
are the [hand H7 profile](h7-early-profiles.md), the five-wire thin
lemma ([README](README.md), Lemma 3), ordinary comparator
untangling, the attainable-rank interval lemma proved below, and the
two-layer forward-cone bound. No solver result or exhaustive matching
scan is a proof premise.

Write M=L3, N=L4 and Q=L5. A two-digit string denotes a comparator;
a longer string denotes a set of positions. The notation `+i` or `-i`
places positive or negative infinity at original input i. An RR gate
compares two retained real tracks. Real-track identities follow the
fixed routing at sentinel comparisons, and all boundary sets use
physical positions at the specified cut. Rescheduling commutes gates
on disjoint real tracks, followed by ordinary untangling.

## 1. A deletion triangle determines L3

The following two-sentinel restrictions retain two disjoint gates
through L2:

| Input sentinels | Retained original tracks | Sentinel positions after L2 |
|---|---|---|
| `+0,+2` | `45,13` | 67 |
| `+0,-2` | `45,37` | 06 |
| `-0,+2` | `45,16` | 07 |

Collapse the two disjoint gates to one layer. H7 forces L3 to retain
at least three edges after deletion of each pair 67,06,07. If L3
has three edges, all of 0,6,7 must be idle. If it has four, its idle
vertex must lie in {0,6,7}, and the other two vertices must be paired:
otherwise two of the tested vertices occupy different edges and
their deletion removes two gates. Gates 06 and 07 never fire, because
after L2 wire0 is at most both wires6 and7. Hence only idle0 with
edge67 is possible in the four-edge case.

Thus, putting W={1,2,3,4,5,8},

```
L3 = K, or K+67,  with K a perfect matching of W.
```

Gate45 is already ordered, so K cannot contain it. The prefix image
is invariant under `(1 3)(6 7)`. To see this for arbitrary reals,
write the first two sorted input pairs as `(a,A),(b,B)`, and the
inputs on6,7 as s,t. The relevant outputs after L2 are

```
0=min(a,b), 2=max(a,b),
1=min(A,s), 6=max(A,s), 3=min(B,t), 7=max(B,t).
```

Exchanging `(a,A,s)` with `(b,B,t)` has exactly the stated effect.
Conjugate the suffix by this image symmetry and untangle through
the whole suffix. Sorted distinct inputs fix the final output
permutation, so no output-order assumption is lost.

The twelve perfect matchings of W avoiding45 reduce to seven forms:

| K type | K | Case without67 | Case with67 |
|---|---|---:|---:|
| A | `12 34 58` | 1 | 2 |
| B | `12 35 48` | 3 | 4 |
| C | `13 24 58` | 5 | 6 |
| D | `13 25 48` | 7 | 8 |
| E | `14 25 38` | 9 | 10 |
| F | `14 28 35` | 11 | 12 |
| G | `15 24 38` | 13 | 14 |

For a direct classification, pair1 with2,3,4,5 or8 and pair the
other four vertices in their three possible ways, omitting45;
identify choices exchanged by1 and3. This gives the seven rows.

## 2. Five-real demands and ordered pairs

If four sentinels leave t=1 or2 RR gates through L3, L4 must retain
at least `3-t` RR gates on their real set R. Otherwise the first
four original layers retain at most two gates. Schedule them in
two layers with one gate each and append the final three layers,
contradicting the five-wire thin lemma.

The appendix lists every signed placement used below. A listed
ordered pair ab is forbidden as an L4 comparator. These inequalities
are obtained by the elementary min/max rules: after comparing a,b,
the minimum is below every old upper bound of either input, and
the maximum is above every old lower bound of either input; common
bounds apply to both outputs. There is one useful additional bound
when67 is present. Before L3, all of0,1,2,3 are at most
`max(x6,x7)`. After67 this is wire7. Since K compares1,2,3 either
with one another or with higher-numbered wires4,5,8, all of1,2,3
remain at most wire7. Thus17,27,37 are also forbidden.

## 3. Eight third-layer forms fail directly

All seven forms without67, and case12 with67, are contradicted by
their displayed five-real demands. Cases1,3,7,9,11,12 have strict
price certificates. If w(ab) counts the displayed real sets
containing a,b, the appendix gives nonnegative prices p and a gate
charge g satisfying

```
2w(ab) <= p(a)+p(b)+g   for every permitted edge ab,
sum p + 4g < 4t,       where t is the number of displayed sets.
```

Each set needs two matching edges, so the demanded twice-weight is
at least4t. A matching has at most four edges and uses each vertex
price once, making the inequalities contradictory.

The two equality cases have short parity proofs independent of
forbidden comparisons:

* **Case5:** the four real sets are `C+a+b`, with C={3,4,5},
  a in {2,8} and b in {6,7}. Give C vertices price2 and a-vertices
  price1. The total price8 equals the four two-edge demands.
  Equality forces the two a-vertices to use both b-vertices;
  the odd common triple C would then have to pair internally.
* **Case13:** the four sets are `{h,a}+X` and `{h,a}+Y`, with
  h=8, a in {3,7}, X={0,1,2}, Y={4,5,6}. Give h price2 and
  X,Y vertices price1. Equality with total price8 forces h to
  consume one a-vertex. Each odd triple X,Y needs an external
  a-partner, but only one remains.

These are the two matching obstructions proved in the
[earlier fork-and-pairs case](h9_feedback_next_078.md#4-cases-78-equality-and-parity).

## 4. Two extensions of a four-set

The remaining cases are2,4,6,8,10,14. We use this simple matching
lemma repeatedly. If |T|=4 and a matching has two edges in both
T+u and T+v, with u,v distinct outside T, then either:

* T is paired internally; or
* T has exactly one internal edge, and u,v meet the two remaining
  T vertices.

With no internal T edge an extension has at most one edge; with
one internal edge each external vertex must provide its own second
edge. With three distinct extensions the latter alternative is
impossible, so T must be internally paired.

In the following arguments a named five-set means its two-edge
demand from the appendix.

**Case2.** Use T=1456 and extensions0,2. If T pairs internally,
sets01345 and01458 force respectively03 and08, impossible. Otherwise
the unused vertices are3,7,8, with only optional edge78 permitted.
Set01345 forces2 to meet6. Set23456 then forces45 and01. Thus
`N=01 26 45`, with optional78.

**Case4.** Use T=1568 and extensions0,2. If T pairs internally,
set01358 forces03, and23468 forces68 and24. Then01348 has only
one edge, a contradiction. Otherwise01358 forces26; set23468
forces34, and23568 forces58 and01. Thus `N=01 26 34 58`.

**Case6.** Use T=2356 and extensions0,4. If T pairs internally,
sets01235 and34568 force01 and48. This gives
`N=01 48 J`, where J is any perfect matching of2356. Otherwise
01235 forces46, and34568 forces35 and02. The remaining vertices
are1,7,8. The additional two-gate restriction `+0,+2,-4,-5`
leaves R=01348 and requires at least one N edge there. It forces18.
The fourth possibility is `N=02 18 35 46`.

**Case8.** Sets23468,23568,02368 are three extensions of T=2368,
so T is internally paired. Set01238 forces01. Only47 or57 may
be added on the remaining vertices4,5,7. For `+0,+2`, the first
three layers retain five gates of height two, with sentinels6,7
and sinks13,25,48. Each sink must meet an N RR edge, by the H7
untouched-sink argument of the earlier proof. Pairing23,68 leaves
48 untouched; pairing26,38 leaves25 untouched. Hence
`N=01 28 36`, with optional47 or57.

**Case10.** Sets23468,02468,12468,24568 extend T=2468, so T pairs
internally. Set02348 forces03; only57 is optional on the remaining
vertices. The same `+0,+2` restriction has sinks14,25,38.
Pairing26,48 leaves25 untouched; pairing28,46 leaves14 untouched.
Thus `N=03 24 68`, with optional57.

**Case14.** Use T=1268 and extensions0,4. If T pairs internally,
sets01238 and14568 force03 and45; set34568 then forces68 and12.
If T is not internally paired, set01238 forces46, set14568 forces
18 and02, and34568 forces35. Thus the two possibilities are
`N=03 12 45 68` and `N=02 18 35 46`.

The H7 sink rule used here is proved in
[the earlier fork-and-pairs case](h9_feedback_next_078.md#1-three-small-matching-tools):
if an old sink were untouched, move all sinks after L4 into a third
rescheduled layer. At most four retained gates remain in the first
two layers. Appending L5–L7 would contradict H7's requirement of at
least five gates in the first two layers of a depth-six sorter.

This derives exactly fourteen fourth-layer forms, without scanning
arbitrary fourth-layer matchings.

## 5. Rank endpoints finish twelve of the fourteen forms

**Attainable-rank interval lemma.** Fix any comparator prefix and
one of its output wires. Over all input permutations of ranks0
through8, the attainable ranks at that wire form an integer interval.
Indeed, consecutive-rank value swaps connect all input permutations.
For a swap of ranks k and k+1, identify those two ranks. This monotone
identification commutes with every minimum and maximum, and makes
the two inputs identical. Hence any output value either stays fixed
or changes between k and k+1. Along a path of such swaps it changes
by at most one, so every intermediate rank is attained.

After L5, a value has only two layers left and can reach at most four
output positions. Its rank determines its required final position.
Consequently no wire after L5 can attain five distinct ranks. In
particular, two witnessed ranks differing by at least four exclude
that wire, by the interval lemma.

Write Q=L5. For a proposed Q edge uv, evaluate the minimum and maximum
of the values at u,v after L4. All other Q comparisons are disjoint,
so they cannot affect these two outputs. A large rank gap on either
output forbids uv. A large gap on the value at an idle wire forbids
leaving that wire idle. This argument permits every partner, including
comparisons repeated from earlier layers.

The appendix supplies fourteen explicit permutations, shared across
all fourteen L4 forms. Its endpoint rows evaluate only those inputs.
They give the following complete partner reductions; labels are those
of the appendix's L4 table.

| L4 label | Consequence for Q |
|---|---|
| 2.1, 2.2 | Wire0 cannot be idle and has no possible partner. |
| 6.2, 6.3 | Wire5 cannot be idle and has no possible partner. |
| 8.1, 8.2, 8.3, 14.1, 14.2 | Wire8 cannot be idle and has no possible partner. |
| 10.1, 10.2 | Wire1 cannot be idle and has no possible partner. |
| 6.4 | Each of3,5,8 must be used, and can only meet2 or4. |
| 4.1 | Successively force03,14,25,68. |
| 6.1 | Successively force78,26,34,15. |

The first eleven forms are impossible immediately. In6.4, the three
required wires have only two distinct possible partners, also impossible.
In either forced row, vertices already matched are removed from subsequent
partner choices; idle choices are explicitly excluded. Thus the final
two forms force the complete four-edge Q matchings shown.

## 6. Two untouched sinks close the forced forms

We use a five-real sink rule. Suppose a restriction retains exactly
three RR gates through L4, and one sink of this three-gate dependency
graph meets no RR edge of Q. Track the real identities through any
sentinel swaps. The old sink remains a sink after Q, and every Q RR
gate is a sink. The combined graph has height at most three: if the
old graph has height at most two this is immediate; otherwise its
three gates form a chain, and its last gate is the untouched sink.
After removing all sinks, at most two gates remain. Put those gates,
in dependency order, one each in the first two rescheduled layers;
put every sink in the third. The final two original layers would
then give a five-wire depth-five sorter with both first layers thin,
contrary to the five-wire thin lemma.

The appendix gives exactly two restrictions for this rule:

| L4 label | Forced Q | Input sentinels | Reals after L4 | Untouched sink |
|---|---|---|---|---|
| 4.1 | `03 14 25 68` | `+0 +1 +2 -4` | 01458 | 58 |
| 6.1 | `15 26 34 78` | `+0 +1 +2 +4` | 01235 | 23 |

The three retained gates, expressed on the real tracks at the L4
boundary, are respectively `45,01,58` and `13,01,23` in their original
order. In the first row the only Q RR edge is14, so sink58 is untouched.
In the second row the only Q RR edge is15, so sink23 is untouched.
This excludes both forced forms and completes the `02 16 37` case.

## 7. Scope and independent audit

This closes one additional H9 second-layer class. It is not a proof
of all H9 classes or of the full D(11) lower bound.

The solver-free [fixed-certificate checker](verify/h9_feedback_round4_proof.py)
checks the printed rank bank and all160 endpoint exclusions with196
prefix runs. It also checks the signed restrictions on all33000
relevant real orders, verifies the six price inequalities and the
two parity patterns, and corroborates the hand matching reductions.
The latter matching scans are checks of the displayed arguments;
the hand proof does not use their absence of survivors as a premise.
The [audit record](results/h9-feedback-round4-proof.json) records the
source, certificate, appendix, and proof hashes. Earlier price and
contact-search artifacts are discovery material and are not premises.
