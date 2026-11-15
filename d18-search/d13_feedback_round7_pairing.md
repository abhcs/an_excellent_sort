# An exact final-matching test for intervals of length at most four

Let F be any family of nonempty integer intervals, each containing at most
four positions in `0,...,n-1`. A matching block means either a matching
edge or an idle singleton.

**Final-matching projection theorem.** The following are equivalent:

1. Some arbitrary matching S has at most two blocks meeting each interval
   in F.
2. Some adjacent matching has that property.
3. There are Boolean variables `e_i`, one for each adjacent pair `(i,i+1)`,
   satisfying

```
not(e_i and e_(i+1))                         for all adjacent edge indices;
e_a or e_(a+1)                              for each [a,a+2] in F;
e_a and e_(a+2)                             for each [a,a+3] in F.
```

Intervals of length one or two impose no further condition. This
characterizes the final-matching part of two-layer forward reachability.
It does not assert that one common preceding matching exists.

## Why this is a necessary projection of two-layer reachability

The forward cone of a wire through matchings P,S is the union of its own
S-block and the S-block of its P-partner, if any. Therefore an attainable
rank interval meets at most two S-blocks.

A three-position interval meets at most two blocks exactly when it
contains an S-edge. A four-position interval meets at most two blocks
exactly when it is the union of two S-edges. If a wire c belongs to its
interval, these conditions also suffice for an **individual** choice of
a preceding partner for c. The difficulty left over is making all such
partner choices a single matching P.

For adjacent S, the displayed Boolean conditions are precisely the
three/four-position requirements and the matching property. Thus2 and3
are equivalent, and2 implies1.

## Uncrossing proof of1 implies2

Start with any S satisfying the requirements.

**First normalize the full four-intervals.** Each is a union of S-edges,
so any two have even intersection. Overlapping distinct four-intervals
therefore have starts differing by two. Each connected overlap component
has one start parity and an even-length contiguous union. No S-edge
leaves this union, because every position lies in a full four-interval
already paired internally. Replace its S-edges by consecutive adjacent
pairs starting at the left endpoint. This preserves every full interval.

It also preserves all required three-intervals. If an old edge inside
the union hit such a triple, the triple intersects the union in at least
two positions. With three positions inside, the new pairing contains an
edge of the triple. With exactly two inside, they are the first or last
two positions of the union, and the new pairing contains that boundary
edge. Old hits outside these unions are unchanged. This also covers
triples crossing a boundary; no unsupported boundary assumption is used.

**Now normalize the remaining edges.** Outside the normalized unions,
delete edges whose endpoints differ by at least three. Such an edge hits
no three-position interval and is needed by no full four-interval.

For any remaining length-two edge `(i,i+2)`, inspect its midpoint i+1.
It lies outside every normalized union. If it is idle, replace the edge
by `(i,i+1)`. The original edge hit only the triple `[i,i+2]`, which is
still hit. Otherwise, after the long-edge deletion, its partner can only
be i-1 or i+3; the two adjacent positions i,i+2 are already used.

* Edges `(i-1,i+1),(i,i+2)` can be replaced by
  `(i-1,i),(i+1,i+2)`.
* Edges `(i,i+2),(i+1,i+3)` can be replaced by
  `(i,i+1),(i+2,i+3)`.

In either case, both triples hit by the two old length-two edges remain
hit. These changes preserve a matching and reduce the number of
length-two edges. They never disturb the already normalized full
intervals. At termination every edge is adjacent, proving2. □

In fact the construction proves a domination statement: for **each**
arbitrary S, some adjacent S' satisfies every length-three or length-four
interval requirement that S satisfied, simultaneously.

## Consequences for endpoint constraints

The path constraints propagate a pairing phase. A required three-window
`[a,a+2]` gives exactly one of e_a,e_(a+1), since the matching constraints
forbid both. A full four-window fixes e_a and e_(a+2). Contradictions can
therefore propagate across chains of three-windows, not just between
overlapping saturated four-windows. The
[bridge lemma](d13_feedback_round7_bridge.md) is the shortest example
between two disjoint full four-windows of different phases.

With `L[c,k]=(lo_c>=k)` and `U[c,k]=(hi_c<k)`, a compact necessary
endpoint formulation adds

```
L[c,a+1] OR U[c,a+2] OR e_a OR e_(a+1)       for three-window inclusion;
L[c,a+1] OR U[c,a+3] OR e_a                  for four-window inclusion;
L[c,a+1] OR U[c,a+3] OR e_(a+2)             for four-window inclusion.
```

Under width at most four and `lo_c<=c<=hi_c`, a three-window need only
be considered for `c in [a-1,a+3]` within the wire range. A four-window
need only be considered for `c in [a,a+3]`. Including the adjacent-edge
matching clauses gives `14n-38` clauses and n-1 auxiliary edge variables
for n>=4:144 clauses at width13 and214 at width18. These counts exclude
the already existing width/endpoint encoding.

The formulation describes an existential adjacent S from the theorem.
It does not claim that this S can be substituted into an arbitrary
actual two-layer suffix without changing its preceding matching. As
usual, exact attainable intervals supply a satisfying endpoint choice
for every genuine sorting completion.

## The penultimate matching still matters

The six-wire prefix in the
[shared-middle-pair note](d13_feedback_round6_middle_pair.md) has intervals

```
[0,3], [0,3], [0,2], [3,4], [2,5], [4,5].
```

The adjacent matching `01 23 45` meets every interval in at most two
blocks, so it passes the exact projection above. But demands on wires0,1,4
would need three penultimate partners among positions2,3. No common P
exists. The final-matching projection should therefore complement, not
replace, shared-middle-pair or other preceding-layer capacity conditions.

## Independent finite controls

[d13_feedback_round7_pairing_verify.py](d13_feedback_round7_pairing_verify.py)
constructs the adjacent dominating matching for every arbitrary partial
matching at widths3 through10, and independently checks all interval
families at those widths against arbitrary versus adjacent matchings.
It also verifies the six-wire separation and the endpoint clause counts.
These checks corroborate the arbitrary-width uncrossing proof. No SAT
solver or full two-layer connectivity encoder is used.
