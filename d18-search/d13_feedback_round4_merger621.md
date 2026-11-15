# Six sorted, two sorted, one singleton need five merger layers

**Theorem.** No four comparator layers can merge independently sorted
blocks of lengths `6+2+1`. This is a hand proof; SAT is not a premise.

Use positions `A=012345`, `B=67`, and singleton `C=8`, after relabelling
and untangling. Write the hypothetical four matchings as `N,Q,P,S`.
Delete comparisons of N internal to either sorted block, since they never
swap. No assumption that N is perfect is made.

## 1. Only two first matchings survive

The singleton C must be used by N. Otherwise its nine possible ranks would
have only three layers in which to reach nine output positions, whereas a
three-layer forward cone has size at most eight.

If C meets one B entry, retain the other B entry, C, and any consecutive
triple of A. These are a sorted triple and two arbitrary singletons. A
blind N would leave a three-layer `3+1+1` merger, contradicting the
[hand311 lemma](d13_feedback_round3_merger441.md). Thus the other B entry
would need an A partner in every consecutive A-triple. Their intersection
is empty. Consequently C meets an A entry `j`.

For either B entry, retain it, C, and any consecutive A-triple avoiding j.
Again N must retain a comparison, so that B entry must meet the triple.
The intersection of the eligible triples is:

| j | Intersection |
|---:|---|
| 0 | {3} |
| 1 | {3,4} |
| 2 | {3,4,5} |
| 3 | {0,1,2} |
| 4 | {1,2} |
| 5 | {2} |

Both B entries need distinct partners in this intersection. This excludes
j=0,5. If j=2, retain A-positions0,1, both B entries, and C. All N edges
are blind. One layer prepares these two sorted pairs and the singleton,
so the three remaining merger layers would sort five arbitrary values in
four layers, contrary to `D(5)>=5`. The reflected argument excludes j=3.

Global value negation followed by reversal inside each block exchanges
j=1 and j=4 and preserves depth after untangling. Thus j=1 suffices, and
the two possible first layers are

```
N1 = 18 36 47,       N2 = 18 37 46.                  (1)
```

All B,C entries are used, so there are no further nonredundant N edges.

## 2. A pivot that no second comparison can narrow enough

At the cut after Q, every wire must carry at most four possible ranks:
its two remaining layers have at most four reachable final positions.
Ranks here are numbered0 through8.

We use the established attainable-rank interval lemma. It applies to this
sorted-block input family by prepending independent block sorters. For
completeness, any two permutations of ranks are connected by swaps of
consecutive rank values. Such a swap changes the value at any comparator
network output by at most one: collapse those two values to the same value,
and all output values coincide. Thus the ranks on a given wire include
every integer between any two ranks witnessed there.

After either first layer in (1), wire8 contains `max(A1,C)`. Consider the
following four inputs, each already sorted inside A and B:

| Input | A | B | C |
|---|---|---|---:|
| L | 0,1,3,4,5,6 | 7,8 | 2 |
| H | 0,1,2,3,4,5 | 6,7 | 8 |
| K | 3,4,5,6,7,8 | 1,2 | 0 |
| J | 0,1,2,3,4,6 | 5,7 | 8 |

If Q leaves wire8 idle, L and H give it ranks2 and8, already too wide.
Otherwise let v be its Q partner. The table gives one of that comparison's
outputs and two witnessed ranks; it is valid for both N1 and N2.

| Partner v | Comparison output | Low witness | High witness |
|---|---|---|---|
| 0 or1 | maximum | 2 on L | 8 on H |
| 2 | maximum | 3 on L | 8 on H |
| 3 or4 | maximum | 4 on K | 8 on H |
| 5 | minimum | 2 on L | 6 on J |
| 6 | minimum | 2 on L | 6 on H |
| 7 | minimum | 2 on L | 7 on H |

Every row has a rank gap of at least four. The interval lemma supplies at
least five attainable ranks on the indicated physical output wire after
Q, contradicting the four-position forward-cone bound. This covers every
Q partner, including a repeated comparison; no second-layer normal form
is needed. Hence the four-layer merger does not exist. □

## 3. Scope and verification

Together with the other nine-real merger hand lemmas, this excludes
interaction components that can be packed into a `6+2+1` partition at a
cut with four layers left. It does not by itself close a D13 prefix-cover
case.

[d13_feedback_round4_merger621_verify.py](d13_feedback_round4_merger621_verify.py)
checks the six triple intersections, the two blind restrictions excluding
j=2,3, and the four-input endpoint table for both first matchings. It also
independently lists the252 sorted-block interleavings and verifies the
attainable intervals for every pivot-partner comparison. No SAT solver or
enumeration of next-layer matchings is used.
