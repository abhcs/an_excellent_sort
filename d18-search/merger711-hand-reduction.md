# A seven-block and two singletons need five merger layers

A proposed four-layer merger of `7+1+1` has, up to reversal and exchange
of the singleton inputs, just two possible first matchings:

```
A = a0<a1<...<a6; singletons u,v
N = (a1,u)(a4,v), or N = (a2,u)(a4,v).
```

Both starts are excluded by the hand rank and cone arguments below.
The earlier tiny SAT certificate is corroboration, not a proof premise.

## A saturated-cone parity lemma at every width

For every integer d>=1, merging sorted lists of lengths `2^d-1` and2
needs at least d+1 comparator layers.

Write the short list as b0<b1. The attainable final ranks of b0 are
exactly0 through2^d-1, and those of b1 are1 through2^d. A depth-d forward
cone has at most2^d positions. Thus a hypothetical d-layer merger must
have exactly those two cones, with their indicated2^d positions.

Equality in the doubling bound forces each cone to expand fully at
every layer. In the last matching, every member of the preceding cone
is paired with a distinct position outside it. Each final cone is
therefore a disjoint union of edges of that same last matching. Their
intersection must also be a union of whole matching edges, hence have
even size. But the two required rank intervals intersect in2^d-1
positions, an odd number. Contradiction.

In particular, a `7+2` merger needs at least four layers. This lemma uses
actual reachable rank positions to force equality in the structural
cone bound; it does not assert that every structural cone is attainable.

## Applying it to711

Delete first-layer comparisons internal to A, which never swap on this
input family. Both singleton inputs must be used in the first layer:
each can finish in any of nine ranks, and only eight positions can be
reached through the three remaining layers if it is idle.

If u and v compare with each other, the remaining three layers must
merge A with their sorted pair. The saturated-cone lemma excludes this.
Thus they compare with distinct A-positions a_i,a_j, with i<j. There are
no other nonredundant first-layer comparators.

Every consecutive triple of A must contain at least one of a_i,a_j.
Otherwise retain that triple and u,v and replace all other A entries
by ordered sentinels. The first layer becomes blind, and three remaining
layers would merge `3+1+1`, contradicting its hand lower bound of four.

The three gaps before, between, and after i,j must consequently have
length at most two. Thus

```
i<=2, j>=4, j-i-1<=2,
```

leaving exactly `(i,j)=(1,4),(2,4),(2,5)`. Global value reversal exchanges
the first and third possibilities; swapping u,v is an input symmetry.
The two displayed first matchings exhaust the remaining cases.


## Rank intervals and two layers of routing

For any fixed comparison prefix and input family consisting of sorted
blocks, the attainable ranks at each wire form an integer interval.
Indeed, all interleavings of the blocks are connected by swapping adjacent
ranks from different blocks. At each comparator, changing the two adjacent
rank labels can change either output rank by at most one: every other
rank has the same comparison outcome relative to both labels. The same
holds through the entire prefix. Along a path between interleavings that
attain the minimum and maximum wire ranks, every intermediate rank must
therefore occur.

If two layers remain, a wire can reach at most four final positions.
Consequently a wire attaining ranks l and h with h-l>=4 is impossible.
More generally, two wires whose attainable rank intervals each contain
four positions must have exact structural forward cones equal to those
four-position intervals. The saturation argument above makes each cone
a union of last-layer matching edges. They cannot intersect in an odd
number of positions.

In the following tables, input `(u,v)=(s,t)` means that the singleton
ranks are s,t and the seven A inputs, in order, are the remaining ranks
from0,...,8. Each row supplies two explicit valid inputs. Its stated
minimum or maximum output of the proposed next comparator has rank at
most l on the first input and at least h on the second. The gap h-l is
at least four, ruling out every partner listed in that row.

## First start: N=(a1,u)(a4,v)

Use physical positions0,...,6 for A,7 for u,8 for v. After N, wire7
contains max(a1,u) and can attain ranks2 and8. It cannot be idle in the
next matching Q. Every possible partner is excluded by this table:

| Partner of7 | Output | First input(u,v) | l | Second input(u,v) | h |
|---|---|---|---:|---|---:|
|0,1,2|max|(3,8)|3|(8,7)|8|
|3|max|(0,8)|4|(8,7)|8|
|4|max|(0,1)|3|(8,7)|8|
|5,6|min|(0,8)|2|(8,0)|6|
|8|min|(0,8)|2|(7,6)|6|

These five rows cover all eight partners, so this first start is impossible.

## Second start: N=(a2,u)(a4,v)

Wire7 now attains ranks3 and8 and must again be used in Q. The following
table rules out every partner except5:

| Partner of7 | Output | First input(u,v) | l | Second input(u,v) | h |
|---|---|---|---:|---|---:|
|0,1,2|max|(3,8)|3|(8,7)|8|
|3|max|(0,8)|4|(8,7)|8|
|4|max|(0,1)|4|(8,7)|8|
|6|min|(0,8)|3|(8,0)|7|
|8|min|(0,8)|3|(8,7)|7|

Thus Q contains57. Wire4 attains ranks0 and5, so cannot be idle. Its
possible partners5 and7 are already used. Among the remaining positions,
all partners except1 are excluded:

| Partner of4 | Output | First input(u,v) | l | Second input(u,v) | h |
|---|---|---|---:|---|---:|
|0|max|(8,0)|1|(0,8)|5|
|2|max|(0,1)|1|(0,8)|5|
|3|min|(8,0)|0|(0,8)|4|
|6,8|min|(8,0)|0|(0,8)|5|

Therefore Q also contains14. After N and those two forced comparisons,
input(8,0) puts ranks2 and6 on wires4 and5; input(0,8) puts ranks5 and3
on them. Their attainable intervals contain respectively `[2,5]` and
`[3,6]`. Both require four positions in the last two layers. Those exact
forward cones intersect in the three positions3,4,5, contradicting the
saturated-cone parity lemma. Other comparisons in Q do not touch wires
1,4,5,7 and cannot change this conclusion.

Both possible first starts fail. Thus merging7+1+1 needs at least five
layers, completing the hand proof. The local verifier
[merger711_hand_verify.py](merger711_hand_verify.py) checks the displayed
inputs and all grouping indices. Its exhaustive72-interleaving check is
corroboration of the rank intervals, not a premise of the endpoint proof.
