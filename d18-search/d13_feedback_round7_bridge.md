# Three ranks can block a change of final pairing

**Bridge lemma.** Suppose two layers remain after a comparator prefix.
If some wires have the full four-rank intervals

```
I = [a,a+3],            J = [a+5,a+8],
```

then no wire's attainable ranks can contain the three-rank bridge
`K=[a+3,a+5]`. Matchings may be partial, and the final matching need not
be assumed adjacent.

## Hand proof

Call the last two matchings P,S, and count an S-idle position as a singleton
block. The forward cone from one wire through P,S is the union of at most
two S-blocks: its own S-block and that of its P-partner, if present.

Consequently, any three ranks in such a cone contain an S-edge. Otherwise
the three positions belong to three different S-blocks.

Each attainable four-rank interval saturates the two-layer cone bound.
It is therefore exactly a cone and is a union of two S-edges. Thus all
positions of I and J are paired internally. In the bridge K, its left
endpoint a+3 is paired to a position of I outside K, and its right
endpoint a+5 is paired to a position of J outside K. Its middle position
a+4 cannot form an internal edge with either endpoint. Hence K contains
no S-edge, contradicting the preceding three-rank necessity. □

This strengthens width bounds, pairwise full-cone parity, and the
[shared-middle-pair condition](d13_feedback_round6_middle_pair.md).

## Endpoint encoding

Use `L[c,k]=(lo_c>=k)` and `U[c,k]=(hi_c<k)`, with the latter strict.
For distinct wires i,j,c, the following six-literal clause expresses the
lemma:

```
L[i,a+1] OR U[i,a+3]
OR L[j,a+6] OR U[j,a+8]
OR L[c,a+4] OR U[c,a+5].
```

The first two pairs negate inclusion of I and J. Under the width-four
bound those inclusions are exact full intervals. The final pair negates
inclusion of the three-rank bridge. Actual attainable intervals can
always be chosen in an endpoint encoding, so overapproximation variables
do not invalidate the necessary condition.

For a standard prefix, an interval includes its own wire index. Thus
i ranges over I and j over J. The bridge interval and the width-four
bound allow c in `[a+2,a+6]`. The two outside choices already force a
full four-rank interval with odd overlap against J or I. The genuinely
new clauses can therefore restrict c to `[a+3,a+5]`. Omitting c=i or c=j
leaves40 clauses per shift a:200 clauses at width13 and400 at width18.
The mathematical lemma itself allows any c.

## An actual prefix missed by the earlier conditions

The following nine-wire prefix has26 comparisons in nine layers:

```
23 45 67 | 12 34 78 | 01 23 45 | 12 56 | 01 45 67 |
34 56 78 | 23 45 67 | 12 34 56 | 23 45 67.
```

Its exact attainable-rank intervals, on wires0 through8, are

```
[0,3], [0,2], [0,2], [3,5], [2,4],
[5,8], [4,6], [6,8], [6,8].
```

Every wire and every rank has degree at most four. The only full
four-rank intervals are `[0,3]` and `[5,8]`, which are disjoint. Therefore
the parity constraints and all shared-middle-pair constraints pass.
Nevertheless wire3 has `[3,5]`, the forbidden bridge between the full
intervals on wires0 and5. This prefix has no two-layer completion.

The [independent verifier](d13_feedback_round7_bridge_verify.py) replays
all9!=362,880 distinct real orders, computes the exact supports above,
and records an explicit input permutation for every attainable wire/rank
pair. It also enumerates the2,620 possible final matchings on nine
positions: exactly nine preserve both full intervals, and none contains
an edge inside the bridge. Finally, each pair of the three named interval
demands has an explicit two-layer routing control, so all three demands
are essential to this local obstruction.

The example separates necessary conditions; it is not a new D13 cover
closure. No SAT solve or full-cover sweep is used.
