# The remaining two-idle-wire case: a hand proof

**Result.** The five-gate first-matching case of the twelve-wire obstruction
is impossible. Together with the earlier small, four-gate and perfect
cases, this closes the remaining first-matching size by hand.

The proof has a broader form. Let there be the five signed A coordinates

    4+,5-,6-,7+,8+,       G={56,67,78,46},

five B coordinates, each with an arbitrary fixed sentinel sign, and any
even number of additional coordinates that are always real. For each G
edge and each B choice, put sentinels on those three positions and reals
elsewhere. At width n=2r>=10, a peak means r-2 retained real-real gates.
The argument below excludes a first matching of r-1 gates: **exactly two
idle wires**. For n=12, this is the five-gate case and the target is four.

All B sign assignments are allowed. The original case-607 family has two
minus and three plus B signs, but their multiplicities are not used here.

## 1. Preliminaries and the exact transport correction

Fill only the final counted matching N. This increases its retained
counts and causes no further transport. A perfect N peaks precisely when
it pairs two of the three sentinels: otherwise three different N-edges
are touched and only r-3 real-real edges remain.

Let M have r-1 gates. A state peaks in M exactly when its three sentinels
touch at most one M-edge. In particular, touching two distinct M-edges
forces its peak into N.

Let f(v) be the position of a singleton sentinel after M: the lower
endpoint for a minus sentinel, the upper endpoint for a plus sentinel,
and v if idle. Two distinct A images can coincide only when those two
A vertices form an M-edge and have equal signs.

**Corrected row-image lemma.** Suppose both endpoints u,v of a G-edge
are used by M, and uv is not itself an M-edge. Then all five choices
of the B sentinel miss their M-peak. Every transported triple contains
f(u),f(v), and its third position has exactly

    5-b

distinct possibilities, where b is the number of same-sign B--B edges
of M. Since b<=2, N must pair f(u) with f(v).

*Proof.* The two A sentinels already touch two different M-edges, even
if the B sentinel lies in one of those edges. Thus at most r-3 M-gates
are real-real.

If the B sentinel is not paired to u or v, its singleton image supplies
the third position. If it is paired to one of them, both endpoints of
that M-block are sentinels after comparison. The A singleton image is
still occupied, and the **other endpoint** supplies the third position.
In particular, when equal signs make the A and B singleton images
coincide, one must use this other endpoint rather than erase a sentinel.

Different M-blocks cannot identify their output positions. Among the five
B choices, only the two endpoints of a same-sign B--B edge give the same
third position. The count is therefore exactly 5-b. Three distinct third
positions outside {f(u),f(v)} force the pair f(u)f(v) into N: without it,
a matching can pair each of f(u),f(v) to at most one third position. ∎

The condition that both A endpoints are used matters. If one A sentinel
is idle and the other shares its M-edge with the B sentinel, only one
M-block is touched and the state can peak in M. That choice must not be
forced into N.

We use two previously proved graph facts from
[d17_hand_defects_twelve_cross.md](d17_hand_defects_twelve_cross.md):

* the folded pairs f(u)f(v) for all G-edges uv outside M cannot form a
  matching, for any M;
* if two distinct common third positions must be paired with every edge
  of a graph H, then H must itself be a matching.

These facts use only the signed A fork and disjoint matching blocks, not
the width or the B sign distribution.

## 2. Comparable idle coordinates reduce to the perfect case

The perfect-first-matching case is excluded in Section 6 of
[d17_feedback_twelve_structure.md](d17_feedback_twelve_structure.md).
That proof extends unchanged to arbitrary additional common real wires:
a perfect matching has r-2 real-real gates precisely when the sentinel
triple contains a matching edge; all its transport and image counts are
the same. The proof also does not assume a particular B sign distribution.

If the two M-idle type coordinates are comparable in the same direction
in every state, add their comparator to M. It applies one fixed output
permutation, identity or transposition, to every type vector. Conjugate N
by that fixed permutation. First retained counts cannot decrease; second
retained counts are unchanged. This would produce a forbidden perfect
first matching.

Therefore the idle coordinates must be incomparable. In particular:

* neither can be an always-real coordinate;
* they cannot have opposite sentinel signs;
* within A, they cannot be 56 or 78, whose same-sign sentinel supports
  are nested.

If both idles lie in A, the only possibilities are consequently 47 or
48. This classification is independent of the B signs.

## 3. No idle A vertex, or two idle A vertices

If no A vertex is idle, the corrected row-image lemma forces every
folded G-edge outside M into N. The folded-fork contradiction finishes
this case. This includes two idle B vertices, without needing their signs.

Now suppose both idle vertices lie in A. They are 47 or 48, neither a
G-edge. Every G-row has at least one used A endpoint, and all B vertices
are used.

Write c for the number of A--B edges and b for the number of same-sign
B--B edges. Exclude B choices paired to A. The remaining choices have

    t=5-c-b

distinct singleton images, disjoint from all A images. For a G-edge
outside M, a used A endpoint and a safe used B sentinel touch two
M-blocks. Thus if t>=2, the two-image graph lemma and the folded-fork
contradiction finish the case.

Otherwise c+b>=4. Only three A vertices are used, so c<=3, while
c+2b<=5. These inequalities force c=3,b=1. M therefore has three A--B
edges, a same-sign B--B edge, and only common-real pairings elsewhere.
There are no A--A edges, so the five A images are distinct.

Let p be the image of the same-sign B--B pair. Its B column requires an
N-peak on every G-row: each row has a used A endpoint in another block.
To pair two sentinels in every triple {f(u),f(v),p}, N must pair p to
f(6), and must also contain f(7)f(8). Indeed, if p is paired to another
A image, deleting that vertex from G leaves two incident edges; if p is
paired outside the A images, G itself would have to be a matching.
Only deleting the center 6 leaves a matching, namely edge 78.

Vertex 5 is crossed for both possible idle pairs 47 and 48. Choose its
B partner as the third sentinel in row 67. This row and that B choice
touch at least two M-blocks, so require N. Its transported triple is

    {f(6),f(7),q},

where q lies in the M-block of 5. This q is different from p and f(8),
regardless of whether the two signs in the cross edge agree. But f(6)
is already paired to p and f(7) to f(8). No two vertices of the displayed
triple can be paired by N. Contradiction.

## 4. One idle A vertex and one idle B vertex

Let x be the idle A vertex. There is one idle B vertex, so at most four
B vertices are used. Continue to write c,b as above.

If b=0, every G-row outside M forces its folded pair into N. For a row
whose two A vertices are used this follows from the corrected lemma.
For row x-u, use the four used B choices, excluding u's B partner if u
is crossed. At least three distinct third images remain. Thus b>=1.

There are 4-c-b distinct images from **used safe B** choices. If this
number is at least two, every G-row outside M requires its peak for
both images: each row has a used A endpoint, and the safe B sentinel
hits another M-block. The two-image and folded-fork lemmas contradict.
Hence c+b>=3. Together with b>=1 and c+2b<=4, this leaves exactly

    c=2, b=1.

There are two crossed A vertices and two noncross used A vertices, in
addition to idle x. The two noncross used A vertices are either paired
together, or each paired to a common real coordinate. Extra common-real
pairings have no effect.

Let p be the same-sign B--B image. For a crossed A vertex u, write q_u
for its B partner's singleton image. This equals f(u) for equal signs,
and is the other endpoint of its M-block for opposite signs. In either
case q_u is distinct from every noncross A image and from p.

We need only the following constraints:

1. Every G-row outside M with both A endpoints used forces its folded
   pair into N, by the corrected row-image lemma.
2. Row x-u with u noncross forces N to pair x with f(u): its four used
   B choices lose only one image from the B--B merger, leaving three.
3. Row x-u with u crossed requires N to hit both triples

       {x,f(u),p}, {x,f(u),q_v},

   where v is the other crossed A vertex. These are exactly the two
   third images from used B choices other than u's own partner. Their
   positions are distinct from every noncross A image.

Classify the fork center 6.

**The center is idle.** Among its three neighbors there is at least one
crossed and at least one noncross used vertex: there are two of each
among the other four A vertices, only one of which is not a neighbor.
The noncross neighbor forces the N-partner of 6 to be a noncross image.
For a crossed neighbor u, both third positions in rule 3 lie outside
that partner. The two triples would require f(u) to be paired to two
different positions, impossible.

**The center is noncross and used.** At most one of its three neighbors
can be its A--A partner in M. Every other neighbor forces an N-edge at
f(6), by rule 1 or rule 2. Those other neighbor images are distinct:
there is only one other noncross used A vertex; crossed images belong
to different M-blocks; and idle x has a unique image. At least two
different N-edges at f(6) are forced, impossible.

**The center is crossed.** It has a noncross used neighbor a, because
only one of the other four A vertices is not its neighbor. Rule 1 forces
N to pair f(6) with f(a). If idle x is a neighbor, rule 3 gives two
triples whose third positions both avoid this noncross image, a
contradiction. Otherwise x=8. The other crossed A vertex is then also
a neighbor of 6, and rule 1 forces a second, distinct N-partner for
f(6). Again impossible.

Every possible position of the center is covered. This excludes the
last c=2,b=1 case and completes the two-idle-wire proof. ∎

## 5. Verification, boundary controls, and generality

Run

```sh
python d18-search/d17_hand_defects_twelve_five_verify.py
```

The checker uses no SAT and does not enumerate all first or second
matchings. It checks:

* all 240 local configurations in the final c=2,b=1 case: five idle-A
  choices, six crossed-A pairs, the A--A/common-partner alternatives,
  and all four same/opposite-sign choices on the cross edges;
* 320 direct row-transport checks covering all 32 B sign assignments,
  including the corrected third position when singleton images collide;
* 1,488 comparable-coordinate checks across those sign assignments;
* the remaining two A-idle pairs and their final transported triple;
* a boundary control where one A endpoint is idle and the B sentinel
  is its used neighbor's partner: this state **does** peak in M, so the
  checker ensures it is not covered by the both-used row lemma.

The [local record](results/d17-hand-defects-twelve-five-local.json) is
`VERIFIED`. The finite checks support the symbolic arguments above; the
proof is the three-case center argument, not a SAT or large matching scan.

The width and B-sign generalization follows from an audit of the proof:
all gates outside the displayed A/B blocks act only on common reals;
the peak threshold always differs from |M| by one; and all sign-sensitive
steps distinguish equality from opposition on a single edge. No step
uses exactly two common real wires or a 2-minus/3-plus B split. The
perfect-case lemma used for comparable idle coordinates has the same
independence, as its image-count proof shows. Thus this near-perfect
first-matching exclusion holds at every even width at least ten with
any fixed B signs.
