# The H9 case `03 16 47`

This is a proof draft for the prefix `L1=01 23 45`, `L2=03 16 47`.
Sections1–2 give a structural third-layer reduction. The fourth-layer
classification and fixed rank certificate are in preparation; no new
aggregate coverage claim is made here yet.

Write M=L3, N=L4 and Q=L5. A signed input `+i` or `-i` is an infinity
at original input i. All retained gates use real-track identities,
including their deterministic routing past sentinels. Boundary sets
below refer to physical positions after the specified layer.

We use the [H7 profile](h7-early-profiles.md), the
[six-wire profile](h9_feedback_reschedule.md#1-two-rescheduling-facts),
the five-wire thin lemma, and the
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

## 3. Fourth layers and rank partners

The structural classification and fixed certificate are being assembled.
Current discovery data show that five-real demands alone leave51 fourth
layers, all excluded by an isolated mandatory rank partner. These counts
are discovery feedback, not a premise or a completed proof of this section.
