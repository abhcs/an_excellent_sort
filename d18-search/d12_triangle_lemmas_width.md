# A signed-fork obstruction at every width

The twelve-wire obstruction extends to **every width at least ten**
when the extra coordinates are always real. Each of the five B
coordinates may have either fixed sentinel sign; the original split
of two minus and three plus signs is unnecessary.

This is a hand theorem. It uses the signed-fork and two-idle-wire hand
lemmas, with the width dependence checked explicitly below. It gives
new sufficient obstructions for sorting-network prefixes; it does
not establish that every relevant prefix contains this family.

## 1. Family and statement

Take five A coordinates

```
a-, b-, c+, d+, e+,
G = {ab, bc, ce, bd},
```

five B coordinates with arbitrary fixed signs, and `q >= 0` common
real coordinates. The width is `n=10+q`. For each edge `uv` of `G` and
each B coordinate `w`, put sentinels on `u,v,w` and reals everywhere
else. This gives twenty signed states, each with `R=n-3` real values.
A real-real gate is counted exactly when both incoming types are real.

**Width theorem.** For any two matching layers `M,N`, after transporting
the types through `M`, some state has at most

```
floor(R/2) - 1
```

real-real gates in each of `M` and `N`. Equivalently, two layers cannot
give every state the maximum possible `floor(R/2)` real-real gates in
at least one layer.

Partial matchings and repeated gates are allowed. No intermediate
matching is filled without a separate justification.

## 2. A universal protected-subfamily lemma

Fix any first matching `M`, without restricting its size. Let `f(v)`
be the output position of a singleton sentinel initially at `v`: its
low endpoint for a minus sentinel, high endpoint for a plus sentinel,
or `v` if idle.

Call a choice `(uv,w)` **protected** when `uv` is a G-edge outside M
and the B vertex `w` is not M-paired to either `u` or `v`. The two A
sentinels are then in different M-blocks, and the B sentinel is in a
third block, with an idle vertex treated as its own block. Its three
output sentinel positions are exactly `f(u),f(v),f(w)`.

**Protected-subfamily lemma.** No matching can contain a pair inside
every transported triple arising from the protected choices.

*Proof.* Write `C` for the number of A-B gates in M and `B_s` for the
number of same-sign B-B gates. The five B singleton images have exactly
`B_s` identifications. Different M-blocks have disjoint output positions.
We use the following elementary facts, proved in
[the safe-image note](d17_hand_defects_twelve_cross.md):

* Three distinct third positions force the common pair: hitting
  `uvp,uvq,uvr` with a matching forces edge `uv`.
* If two distinct positions outside a graph supply all triples for
  its edges, hitting them all forces that graph to be a matching.
* The folded graph `H={f(u)f(v): uv in G outside M}` is never a matching.
  Its proof depends only on the A signs and disjoint M-blocks.

If `B_s=0`, for each G-edge outside M exclude its at most two crossed
B partners. At least three distinct B images remain, all outside the
two A images. Every folded G-edge is forced, contradicting the fork
fact.

Otherwise consider B vertices not paired to any A vertex. They give
`t=5-C-B_s` distinct safe images outside all A images. If `t>=2`, the
two-image fact again contradicts the folded fork.

The remaining case has `B_s>=1`, `C+B_s>=4`, and `C+2B_s<=5`. Thus
`C=3,B_s=1`: three A vertices are crossed, and the other two B
vertices form one same-sign pair. The two noncross A vertices may
be idle, paired together, or paired to common reals; their precise
status will not matter.

If the fork center `b` is noncross, at least two of its three
neighbors are crossed. Each of these two rows excludes only one B
partner and has at least three third images. It therefore forces an
N-edge at `f(b)` to its crossed neighbor's image. The two crossed
images are distinct, a contradiction.

If `b` is crossed, it has a noncross neighbor `a0` and a crossed
neighbor `v`: among its four other A vertices only `e` is not a
neighbor, and there are two cross and two noncross vertices. Row
`b-a0` excludes one B partner and forces edge `f(b)f(a0)`.

For row `b-v`, exclude the two crossed B partners. The remaining
third positions are the image `p` of the same-sign B-B pair and
the image `q` of the third crossed A vertex's B partner. Their
M-blocks make them distinct from each other and from `f(b),f(v),f(a0)`.
The two triples `f(b)f(v)p` and `f(b)f(v)q` must be hit. But `f(b)`
already has partner `f(a0)` outside them, so they require `f(v)`
to pair with both `p` and `q`. Contradiction. □

This proof allows the two noncross A images to coincide. It uses no
number of common real coordinates and no B sign multiplicities.

## 3. Even widths: the four possible matching deficits

Let `n=2r>=10`, so every state has `2r-3` reals and a peak is `r-2`
real-real gates. Fill the last counted matching N to a perfect
matching. This only increases its counts; there is no subsequent
transport to preserve. N peaks precisely when it pairs two of the
three sentinels.

For a state, let `u` count its M-idle sentinel positions and let `s`
count its M-edges containing two sentinels. If `m=|M|`, then

```
e_M(R) = m - 3 + u + s.
```

Write `k=r-m`, so M has `2k` idle wires.

**`k>=3`.** Here `m<=r-3`, below the peak threshold. Every state must
peak in N, contrary to the protected-subfamily lemma.

**`k=0`.** M is perfect. Every protected state has its three sentinels
in three different M-edges, giving `r-3` real-real gates. Thus all
protected states must peak in N, again contradicting the lemma.

**`k=2`.** M has four idle wires. A first peak is possible precisely
when all three sentinel positions are idle. If there are no first
peaks, use the protected-subfamily lemma. Otherwise there are either
two or three idle A vertices; four idle A vertices would leave no
idle B choice.

If exactly two A vertices are idle, their pair is a G-edge `E0`, and
at least one B vertex is idle. Hence `C<=3`, `C+2B_s<=4`, and
`5-C-B_s>=2`. Every G-row other than `E0` and any A-A M-edge has a
used A endpoint, so cannot peak in M for either of two basic safe
B images. There is at most one A-A edge. The idle-edge folded-fork
lemma from Section 4 of
[the structure note](d17_feedback_twelve_structure.md) says that this
remaining folded graph is not a matching. The two-image lemma
contradicts N.

If three A vertices are idle, exactly one B vertex is idle and every
common real vertex is used. There are `4-C-B_s` used safe B images.
Two such images would force all folded G-rows and give a contradiction.
Otherwise the capacities `C<=2` and `C+2B_s<=4` force `C=2,B_s=1`.
Thus there are two A-B gates, one same-sign B-B gate, and all other
gates pair common reals together; zero such additional gates is allowed.
The used B-B image supplies a full required column. The full-column
lemma forces N to pair that image with the fork center and to contain
the outer edge `ce`. One of the two cross gates has noncentral A
endpoint, and its used B partner makes every nonincident G-row miss
M. The cross-gate contradiction in Section 3 of the structure note
finishes the case. Those local lemmas use only the A/B images.

**`k=1`.** There are exactly two idle wires. The
[two-idle-wire hand proof](d17_hand_defects_twelve_five.md) is stated
directly at width `2r>=10`, with arbitrary fixed B signs. It excludes
this case. Its comparable-idle augmentation reduces to the perfect
case just proved. In its only surviving local configuration, the two
noncross used A vertices are either paired together or each paired
to a common real; further common-real pairings have no effect.

These cases exhaust all first matchings and prove the even-width
theorem. The four-idle case above explicitly replaces the original
twelve-wire tight count of one common-real pair by any number of
such pairs, including none.

## 4. Odd widths and additional fixed sentinels

Suppose a counterexample existed at an odd width `n>=11`. Add one
always-real wire idle in both matchings. Counts do not change. The
new even width `n+1` has one more real, but its peak threshold is
the same:

```
floor((n-3)/2) = floor((n-2)/2)    for odd n.
```

This contradicts the even-width theorem and proves the statement for
all `n>=10`.

One may also add any number of coordinates that hold a fixed positive
or negative sentinel across all twenty states, and permute all
coordinates jointly. The [fixed-sentinel pruning lemma](fixed-sentinel-obstruction.md)
removes them from a hypothetical pair of covering layers while
preserving every pair of real-real counts. Therefore:

> For every `R>=7`, the signed fork plus singleton-B family with
> `R-7` common real coordinates is a two-layer obstruction at peak
> `floor(R/2)`, even after adding arbitrarily many common fixed
> sentinels and embedding the coordinates in any order.

## 5. Concrete sorting-network applications and their limits

Suppose twenty sentinel placements leave `R` arbitrary real inputs,
blind a prefix, and at the prefix boundary realize this family,
possibly with extra fixed sentinels. Any proposed sorting suffix
must sort every restriction. The width theorem ensures one
restriction has two first suffix layers both below the peak.

For `R=7` or `R=8`, a six-layer sorting suffix is impossible by the
[hand early-profile results](../depth-hand-proofs/h7-early-profiles.md):
one of its first two layers must attain the peak, respectively three
or four gates. Consequently:

* A hypothetical depth-ten sorter on eighteen wires is excluded if
  such a seven- or eight-real family appears after **four blinded
  prefix layers**. This implication uses only hand results.
* A hypothetical depth-nine sorter on seventeen wires is excluded
  if such a seven- or eight-real family appears after **three
  blinded prefix layers**, again using hand results.

For comparison, the nine-real version forbids a seven-layer suffix
using H9. It would apply after three blinded layers in the D18
depth-ten setting, or after two blinded layers in the D17 depth-nine
setting. H9's full proof remains computer-assisted, despite the
expanded hand coverage of individual classes.

The seven- and eight-real versions therefore give a different
structural target from the nine-real route. We have not proved that
every relevant prefix admits any of these families. No new full
D17 or D18 lower bound follows from the width theorem alone.

No new computation or solver result is used in this note. The local
hand lemmas and their existing checks are linked where applied.
