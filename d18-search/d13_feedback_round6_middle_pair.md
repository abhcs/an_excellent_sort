# A shared middle pair has capacity two

**Lemma.** Suppose a comparator prefix has two layers left to sort. Put

```
I = [a,a+3],       J = [a+2,a+5].
```

Among the four physical wires `a,a+1,a+4,a+5`, at most two can have the
following full attainable-rank intervals: I on either of the first two
wires, or J on either of the last two wires.

This is stronger than bounding both degrees of the rank-position relation
by four and forbidding odd intersections of full four-rank intervals.

## Hand proof

Write the last two matchings as P,S. If a wire attains four ranks, its
structural two-layer forward cone is exactly those four positions. Full
growth forces this cone to be a union of two S-edges.

Assume three of the four stated demands hold. There are only two outer
wires associated with each interval, so both I and J occur as exact
cones. Their intersection `M={a+2,a+3}` is a two-position union of S-edges,
and therefore is itself one S-edge. Likewise `I\M={a,a+1}` and
`J\M={a+4,a+5}` are S-edges.

Each demanded outer wire c lies on its outer S-edge. To reach all of I or
J in two layers, its P-partner must belong to M: its own S-edge supplies
the outer pair, and its partner's S-edge must supply the middle pair.
Three distinct demanded outer wires would therefore need three distinct
P-partners among the two middle positions. This violates the matching
property. □

The argument allows arbitrary partial matchings and arbitrary comparator
orientations. It does not assume that the final matching contains only
adjacent comparisons. The three final edges are forced by the saturated
cones themselves.

## Thirty-two endpoint clauses for thirteen wires

Use the reviewed conventions `L[c,k] = (lo_c>=k)` and
`U[c,k] = (hi_c<k)`. The latter inequality is strict.

For each `a=0,...,7` and each three-element subset T of
`{a,a+1,a+4,a+5}`, set `s(c)=a` for c in the left pair and `s(c)=a+2`
for c in the right pair. Add the six-literal clause

```
OR over c in T:  L[c,s(c)+1] OR U[c,s(c)+3].
```

If all literals were false, each chosen interval would contain its entire
four-rank window; with the wire-width bound it would equal that window.
The lemma forbids the resulting three demands. There are8 shifts times4
triples, hence32 clauses. More generally there are `4(n-5)` such clauses
at width n>=6.

As with the existing endpoint encoder, selected intervals may
overapproximate actual ones. Soundness follows because every genuine
completion can choose its exact attainable intervals. This note does not
modify or run a SAT encoder with the new clauses.

## An actual prefix separates the old and new conditions

Consider the following six-wire prefix:

```
01 24 | 05 | 45 | 12 34 | 23 | 35.
```

Its exact attainable-rank intervals are:

| Wire | Interval |
|---:|---|
| 0 | [0,3] |
| 1 | [0,3] |
| 2 | [0,2] |
| 3 | [3,4] |
| 4 | [2,5] |
| 5 | [4,5] |

Every wire carries at most four ranks, and every rank occurs on at most
four wires. The full four-rank intervals have even pairwise intersections.
Nevertheless wires0,1,4 are three forbidden outer demands for a=0. The
prefix cannot be completed by two layers. Thus the new lemma detects a
real comparator-prefix obstruction missed by the two degree bounds and
the existing parity clauses together.

The [local verifier](d13_feedback_round6_middle_pair_verify.py) computes
these exact intervals on all720 real permutations. It also checks all
four forbidden three-demand patterns against the5776 pairs of six-wire
partial matchings. Each two-demand pattern has an explicit positive
control. A complete six-wire odd-even transposition sorter supplies a
separate valid two-layer-ending control. These finite checks corroborate
the hand proof; no SAT is used.

## What pairwise parity captures exactly

For a family of equal four-position integer intervals, the following are
equivalent:

1. Every pair has even intersection.
2. There is a matching for which each interval is a union of whole edges.
3. There is such a matching using only adjacent edges.

The implications3=>2=>1 are immediate. For1=>3, overlapping intervals
have starts differing by0 or2. Thus every connected overlap component
has one start parity and an even-length contiguous union. Pair consecutive
positions starting at its left endpoint. These pairs respect every
interval in that component; disjoint components do not conflict.

Therefore extra restrictions on the final matching alone cannot improve
pairwise parity for just these full intervals. The shared-middle-pair
lemma adds the capacity of the preceding matching, which is exactly the
information missing from that condition.
