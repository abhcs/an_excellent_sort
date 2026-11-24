# A hand reduction for the H9 prefix `02 15 36`

Let a hypothetical nine-wire depth-seven sorter have

```
L1 = 01 23 45,   L2 = 02 15 36.
```

Write M=L3 and N=L4. After deleting universally redundant comparisons,
M must be a perfect matching K on `123478`, optionally together with
`56`; wire 0 is idle. Up to interchanging the unused input wires 7 and
8, these are the eighteen forms below. This is a complete hand reduction
of M, not yet a proof that this H9 class has no completion.

The proof uses the established [seven-wire early profiles](h7-early-profiles.md)
and the five-wire thin-layer lemma, [README Lemma 3](README.md): no network of at most five
layers on five channels whose first two layers contain **at most one comparator each** sorts.
(It does not say a depth-5 five-sorter needs two comparators in each of those layers; the
sorter `34 / 13 24 / 02 34 / 01 23 / 12 34` has a one-comparator first layer.) No SAT answer or matching census is
a premise. Signs below specify original inputs; retained gates are
followed on their fixed real tracks through sentinel comparisons.

## 1. Two deletion pairs give only two alternatives

The following two restrictions leave disjoint real-real gates through
the first two layers. The listed orientations are allowed to be
generalized; this does not affect their disjointness or layer counts.

| Original sentinels | Sentinel positions after L2 | Retained boundary gates |
|---|---|---|
| `+0,+2` | `56` | `41,02` |
| `+0,-2` | `05` | `41,36` |

Merge the two retained gates into one layer on seven reals. H7 forces
at least three M gates avoiding each of the pairs `56` and `05`.

M therefore has three or four gates. If it has three, all three must
avoid `056`, so they perfectly match `123478`. If it has four and its
idle vertex is v, every deletion pair not containing v must itself be
an M gate. If v lies outside `056`, this requires both `05` and `56`,
which collide. If v=6 it requires `05`, but `x0<=x5` holds after L2,
so that gate is redundant and has been removed. If v=0, `56` is forced
and the other three gates perfectly match `123478`. The only alternative
left to exclude is a four-gate M with idle vertex 5.

The inequalities needed here and below are obtained directly by min/max
propagation:

```
x0<=x2,x5,x6;   x1<=x5;   x3<=x6;   x4<=x5.
```

In particular `02` and `06` cannot be M gates in the idle-5 alternative.

## 2. A six-real exchange rule

A six-wire sorter of depth at most five needs at least two gates first.
If it had at most one, a sentinel would erase that gate and leave five
reals to be sorted in four layers, contrary to D(5)>=5.

Moreover, if its first layer has two gates, its second has three.
Otherwise both have two. A second layer with at most one gate is
excluded by choosing a sentinel on one of its endpoints, with a sign
that keeps it on that physical wire through the first layer; erasing
the second layer would leave five reals with only four layers.
Their four-vertex supports intersect. Put a sentinel
at a common wire, choosing its sign to keep it there through the first
layer. The resulting five-wire depth-five sorter has at most one gate
in each of its first two layers, contrary to the five-wire thin lemma.

Consequently, if a three-layer restriction on six reals has exactly two
retained gates on disjoint tracks, N must perfectly match its six real
positions. Two six-sets differing by one vertex cannot both be perfectly
matched by the same N: their intersection has five vertices and is
closed under the matching partner, which is impossible.

Assume now M has four gates and idle vertex 5. Use these restrictions:

| Label | Original sentinels | Signed state after L2 | Earlier retained gate |
|---|---|---|---|
| A | `-0,+2,+4` | `-0,+5,+6` | none |
| B | `-0,+2,-4` | `-0,-4,+6` | `15` |
| C | `-0,-1,+2` | `-0,-1,+6` | `45` |

Here “signed state” lists only sentinels; all other wires hold reals.
In A, the sentinel at 5 is idle. The other two meet different M gates
because `06` is forbidden. Exactly two disjoint M gates remain.

**A versus B.** Suppose M pairs wire 1 with 0 or 6, and pairs wire 4
with neither 0 nor 6. In B, the three sentinel positions `046` meet
three distinct M gates. Only one M gate remains, disjoint on real
tracks from the earlier gate `15`: wire 1 meets a sentinel and wire 5
is idle. Thus both restrictions have two disjoint retained gates.

Their final real sets differ by exactly one vertex. Indeed A and B
have identical types except at 4 and 5. Wire 5 is unchanged by M, and
the M partner of 4 is real in both restrictions. Replacing real 4 by
a negative sentinel changes exactly one output of that gate from real
to sentinel; replacing positive sentinel 5 by a real changes exactly
wire 5 in the other direction. The exchange rule gives a contradiction.
It follows that

```
01 in M implies 46 in M;    16 in M implies 04 in M.
```

**A versus C.** Suppose M pairs wire 4 with one of `0,1,6`, while wire 1
is paired with neither 0 nor 6. In C the sentinel positions `016` meet
three distinct M gates. Its earlier gate `45` is disjoint from the sole
remaining M gate, because wire 4 meets a sentinel and wire 5 is idle.
Now the exchange between A and C is at wires 1 and 5, so again the two
final six-real sets differ by one vertex. This excludes each of

```
14 in M;   04 in M without 16;   46 in M without 01.
```

Together these give `14` absent, `01` iff `46`, and `04` iff `16`.

## 3. The idle-5 alternative is impossible

If neither paired alternative occurs, M has no edge within `0146`:
the six possible edges are `01,04,06,14,16,46`, all excluded above.
Since M perfectly matches the other eight vertices, all four edges
must join `0146` to `2378`.

Put `-0,-1,+2,-4` on the original inputs. The first two layers are
blind and leave sentinels at exactly `0146`. Every M edge then meets
a sentinel. Five free reals would have only four remaining layers,
contrary to D(5)>=5. This rules out the all-cross alternative.

Otherwise M is one of

```
01 46 K,   or   04 16 K,
```

where K perfectly matches `2378`. Put `-0,+2` on the original inputs.
The sentinels after L2 occupy `06`, the earlier retained gates are
`45` followed by `15`, and both displayed non-K M gates are blind.
Following their fixed routing leaves the same two earlier gates on
boundary wires `145`; the two K gates are disjoint from those wires.

Move one K gate alongside `45` and the other alongside `15`. The first
three original layers now become two layers of two gates each on seven
reals. Appending the original last four layers contradicts H7. Thus
the idle-5 alternative is excluded completely.

## 4. Eighteen third-layer representatives

The remaining M is K or K+`56`, with K a perfect matching on `123478`.
There are fifteen such K. Interchanging untouched input wires 7 and 8
preserves the fixed prefix; untangling the later suffix preserves each
matching's edge set at the cut. Three K contain `78` and are fixed;
the other twelve occur in pairs. Hence nine representatives, each with
two choices for `56`, give the following eighteen M forms.

| Case | M |
|---:|---|
| 1 | `12 34 56 78` |
| 2 | `12 34 78` |
| 3 | `12 37 48` |
| 4 | `12 37 48 56` |
| 5 | `13 24 56 78` |
| 6 | `13 24 78` |
| 7 | `13 27 48` |
| 8 | `13 27 48 56` |
| 9 | `14 23 56 78` |
| 10 | `14 23 78` |
| 11 | `14 27 38` |
| 12 | `14 27 38 56` |
| 13 | `17 23 48` |
| 14 | `17 23 48 56` |
| 15 | `17 24 38` |
| 16 | `17 24 38 56` |
| 17 | `17 28 34` |
| 18 | `17 28 34 56` |

The [fixed checker](verify/h9_recovery_021536_reduction_verify.py) verifies
the displayed signed traces and real-track commutations, the exchange
conditions, and the eighteen-form list. Its small matching recipes are
independent cross-checks of the arguments above, not omitted proof steps.
The fourth-layer classifications and final contradictions remain separate
work; this reduction alone does not increase the accepted H9 class count.
