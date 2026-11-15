# A stronger D13 rescheduling condition, and two surviving prefixes

**Result.** The following hand-proved necessary condition strengthens the
early retained-count screen: after the first four layers of a hypothetical
depth-eight thirteen-wire sorter, every seven-real restriction must have
at least five retained gates or a three-gate dependency chain. Every
eight-real restriction must have at least seven retained gates or such a
chain.

Nevertheless, complete-cover cases 0 and 116 each have a **common pair**
of layers 3 and 4 satisfying this condition for every signed placement.
These witnesses establish a limit of this stronger early-prefix approach.
They are relaxation survivors, not sorting networks, and close neither
case.

## 1. The hand lemma

Prune fixed signed infinities and follow the logical real tracks. A
real-real comparison depends on every earlier retained comparison sharing
one of its tracks. Let h be the longest chain of retained comparisons in
the first four original layers, and let T be their total number.
Comparisons with disjoint tracks commute, so these retained gates can be
scheduled in h matching layers, preserving the order along every track.
Sentinel transport only relabels the real tracks; untangling comparator
orientations preserves the layer and gate counts.

If h<=2, put those comparisons into two layers and retain original layers
5 through 8. The resulting seven- or eight-wire sorter has at most six
layers. The hand-proved early-profile theorem gives

    seven wires:  first two counts (2,3), (3,2), or (3,3);
    eight wires:  first two counts (3,4), (4,3), or (4,4).

See `depth-hand-proofs/h7-early-profiles.md`. Hence T>=5 for seven reals,
and T>=7 for eight reals. Empty scheduled layers cause no exception:
they would violate the same theorem, or the corresponding depth lower
bound. Therefore

    seven reals: h>=3 or T>=5;
    eight reals: h>=3 or T>=7.                       (1)

This proof uses hand facts only; it does not invoke H9.

The earlier trial used only restrictions for which the first three layers
commute into one. In that situation the merged layer and layer 4 must
obey the same early profiles. Condition (1) includes that special case,
because the merged layer followed by layer 4 has dependency depth at
most two.

## 2. A common survivor for each named complete-cover case

All labels in this section are the original complete-cover labels, not
the separate relabelled labels used by the cut-six endpoint certificates.

For case `n13-r0000`, use

```text
L1: 01 23 45 67 89 (10,11)
L2: 02 13 46 57 (8,10) (9,11)
L3: 12 (3,10) (4,11) (5,12) 69 78
L4: 07 13 28 56 (9,12)
```

For case `n13-r0116`, use

```text
L1: 01 23 45 78 (9,10) (11,12)
L2: 03 12 46 79 (10,11)
L3: (0,12) (1,11) 23 48 56 (9,10)
L4: 01 (2,12) (3,11) (5,10) 68 79
```

Here a two-digit token such as 46 denotes (4,6); larger labels are
parenthesized. The JSON result files give the unambiguous layer arrays:
[case 0](results/d13-hand-next-reschedule-two-0000.json) and
[case 116](results/d13-hand-next-reschedule-two-0116.json).

The independent verifier explicitly tries all

    C(13,6)*2^6 = 109,824 seven-real signed placements,
    C(13,5)*2^5 =  41,184 eight-real signed placements

on each four-layer prefix. It tracks real-wire dependencies directly,
without the SAT encoding or first-layer normalization.

| Case | Seven-real placements with h<=2 | Eight-real placements with h<=2 | Violations of (1) |
|---|---:|---:|---:|
| 0 | 3,960 | 0 | 0 |
| 116 | 12,316 | 700 | 0 |

Thus both witnesses pass **all** 151,008 signed placements, not a sampled
or selected family. The SAT encoding deduplicated them to 2,592 and
10,082 records respectively; full replay removes dependence on that
reduction for the survivor claim.

## 3. Search scope and terminal records

`d13_hand_next_reschedule_two.py` searches only common matchings L3,L4.
For each restriction, it carries the exact type state and whether a real
track has already reached dependency depth two. A third-layer comparator
on a depth-two real creates a three-gate chain. A fourth-layer real-real
comparator does likewise if one input track has depth at least two after
L3. Otherwise it enforces the retained-gate lower bound in (1).

The first two fixed layers remain those of the cover case. Adjacent-layer
repeated comparators are omitted by the usual safe redundancy deletion.
No sorting suffix, rank bounds, final-layer normal form, or H9 predicate
is encoded.

Both stronger-screen runs terminated `SURVIVOR`: 0.096 seconds of solving
for case 0 and 6.70 seconds for case 116. The earlier, weaker commuting-
three-layer screen also found survivors, in 0.16 and 11.58 seconds.
Every child had a hard 60-second external wall cap; all four runs completed.
Terminal records are the corresponding `*-terminal.json` files.

A preliminary direct scan also found no nine-real restriction of either
prefix for which the first two retained layers commute into one layer
with at most three gates. Thus that direct H9 merger supplies no test
on these two cases. This finite scan is reported in
`results/d13-hand-next-commuting9.json`; it is not a new lower-bound proof.

## 4. Reproduction and conclusion

```sh
python d18-search/d13_hand_next_reschedule_verify.py
```

The [independent replay](results/d13-hand-next-reschedule-verification.json)
is `VERIFIED` and uses no SAT. It checks the printed four-layer networks
on every signed placement above, using a separate real-track dependency
calculation.

Condition (1) is a reusable hand lemma, but its application at this early
cut leaves both named complete-cover cases open. Further progress needs
a stronger condition or a later cut. A failure of an older saved witness
must not be substituted for a refutation of its whole prefix.
