# Fixed tables for H9 `03 16 57`

These tables supply the finite premises of the [hand proof](h9_feedback_round7_031657.md).
Comparator names have two digits; longer strings denote sets of positions.

## 1. Third layers and propagated order

| Case | M=L3 | Forbidden N=L4 pairs |
|---:|---|---|
| 1 | `01 24 36 58` | `01 03 06 16 24 26 27 36 57 58` |
| 3 | `04 12 36 58` | `03 04 06 07 12 13 16 36 57 58` |
| 4 | `04 15 28 36` | `03 04 06 07 15 16 17 26 28 36` |
| 6 | `08 14 25 36` | `03 06 08 14 16 17 25 26 27 36` |

## 2. Five-real demands

Every row retains exactly `3-demand` RR gates through L3. Signed inputs are original input positions.

| Case | Row | Original sentinels | Real positions after M | Demand on N |
|---:|---:|---|---|---:|
| 1 | 1 | `-0 -1 -2 +4` | 34568 | 1 |
| 1 | 2 | `-0 -1 +2 -7` | 23478 | 1 |
| 1 | 3 | `-0 -1 -2 -7` | 34678 | 1 |
| 1 | 4 | `+0 -1 +4 +5` | 12358 | 1 |
| 1 | 5 | `+0 -1 +4 +7` | 12345 | 1 |
| 1 | 6 | `+0 +2 +3 +4` | 01258 | 1 |
| 1 | 7 | `-0 -2 -3 +4` | 14568 | 1 |
| 1 | 8 | `+0 +2 -4 -5` | 01478 | 2 |
| 1 | 9 | `-0 -2 -4 -5` | 13678 | 1 |
| 1 | 10 | `+0 +2 +4 +7` | 01245 | 1 |
| 1 | 11 | `-0 -2 +4 +7` | 13456 | 1 |
| 1 | 12 | `-0 -2 +4 -7` | 13468 | 1 |
| 3 | 1 | `+0 -1 -2 +4` | 23458 | 2 |
| 3 | 2 | `+0 -1 -2 -7` | 23478 | 2 |
| 3 | 3 | `+0 +2 +3 +4` | 01458 | 1 |
| 3 | 4 | `+0 +2 -4 -5` | 12478 | 2 |
| 3 | 5 | `+0 +2 +4 +7` | 01245 | 1 |
| 4 | 1 | `-0 -1 -2 +4` | 34568 | 2 |
| 4 | 2 | `+0 +2 +3 +4` | 01245 | 1 |
| 4 | 3 | `+0 +2 -4 -5` | 24578 | 2 |
| 4 | 4 | `+0 +2 +4 +6` | 01248 | 1 |
| 4 | 5 | `+2 +3 +4 -6` | 02345 | 1 |
| 4 | 6 | `+2 +4 +5 -6` | 02358 | 1 |
| 6 | 1 | `-0 -1 -2 +4` | 34568 | 2 |
| 6 | 2 | `+0 +2 +3 +4` | 01248 | 1 |
| 6 | 3 | `+0 +2 +4 +5` | 01258 | 1 |
| 6 | 4 | `+0 +2 -4 -5` | 04578 | 2 |
| 6 | 5 | `+2 +3 +4 -6` | 02348 | 1 |
| 6 | 6 | `+2 +4 -6 +8` | 02345 | 1 |

## 3. Local fourth-layer classifications

For cases1 and3, a displayed demand-two real set supplies two base edges.
There are exactly twelve permitted bases. The residual clauses are written `row:need(edges)`; only those rows are used.
At most two edges fit on the five unused vertices. Branch on one edge of the indicated anchor clause.
A branch `e→F` requires the other edge to belong to F; `e→∅` is impossible.
The notation `e→optional F` also permits no second edge.
The intersection rule in the main proof verifies each branch directly.
Optional unused edges are included, so no maximality assumption is made.

### Case 1: base set 01478

| Base | Residual clauses | Anchor | Edge branches | Completions on unused wires |
|---|---|---:|---|---|
| `14 78` | 1:1(35 56); 4:1(23 25 35); 6:1(02 05 25) | 1 | 35→{02}; 56→∅ | `02 35` |
| `17 48` | 5:1(23 25 35); 10:1(02 05 25); 11:1(35 56) | 11 | 35→{02}; 56→∅ | `02 35` |
| `18 47` | 5:1(23 25 35); 10:1(02 05 25); 11:1(35 56) | 11 | 35→{02}; 56→∅ | `02 35` |
| `04 78` | 6:1(12 15 25); 7:1(15 56); 12:1(13) | 12 | 13→∅ | `impossible` |
| `04 17` | 6:1(25 28); 11:1(35 56); 12:1(38 68) | 6 | 25→∅; 28→∅ | `impossible` |
| `04 18` | 2:1(23 37); 3:1(37 67); 5:1(23 25 35); 11:1(35 56) | 2 | 23→∅; 37→∅ | `impossible` |
| `07 48` | 9:1(13); 10:1(12 15 25) | 9 | 13→{25} | `13 25` |
| `07 14` | 2:1(23 28 38); 6:1(25 28); 9:1(38 68) | 6 | 25→{38}; 28→∅ | `25 38` |
| `07 18` | 2:1(23 34); 3:1(34 46); 10:1(25 45) | 2 | 23→∅; 34→{25} | `25 34` |
| `08 47` | 7:1(15 56); 10:1(12 15 25); 12:1(13) | 12 | 13→∅ | `impossible` |
| `08 14` | 1:1(35 56); 2:1(23 37); 4:1(23 25 35); 9:1(37 67) | 1 | 35→∅; 56→∅ | `impossible` |
| `08 17` | 2:1(23 34); 7:1(45 46 56); 10:1(25 45); 12:1(34 46) | 2 | 23→∅; 34→∅ | `impossible` |

### Case 3: base set 23458

| Base | Residual clauses | Anchor | Edge branches | Completions on unused wires |
|---|---|---:|---|---|
| `35 48` | 2:1(27); 5:1(01 02) | 2 | 27→{01} | `01 27` |
| `38 45` | 4:2(17 27) | 4 | 17→∅; 27→∅ | `impossible` |
| `23 45` | 4:2(17 18 78) | 4 | 17→∅; 18→∅; 78→∅ | `impossible` |
| `23 48` | 4:1(17); 5:1(01 05 15) | 4 | 17→{05} | `05 17` |
| `24 35` | 2:1(78); 3:1(01 08 18) | 2 | 78→{01} | `01 78` |
| `24 38` | 3:1(01 05 15); 4:1(17) | 4 | 17→{05} | `05 17` |
| `25 48` | 2:1(37); 4:1(17) | 2 | 37→∅ | `impossible` |
| `25 34` | 4:2(17 18 78) | 4 | 17→∅; 18→∅; 78→∅ | `impossible` |
| `25 38` | 4:2(14 17 47) | 4 | 14→∅; 17→∅; 47→∅ | `impossible` |
| `28 45` | 2:1(37); 4:1(17) | 2 | 37→∅ | `impossible` |
| `28 34` | 4:1(17); 5:1(01 05 15) | 4 | 17→{05} | `05 17` |
| `28 35` | 2:1(47); 5:1(01 14) | 2 | 47→{01} | `01 47` |

## 4. N forms and isolated mandatory pivots

Sixteen rows have an isolated mandatory Q=L5 pivot by the threshold certificate in §6.
Two rows have sink restrictions in the main proof. Cases2 and5 transfer to the previous class.

| Label | N | Pivot |
|---|---|---:|
| 1.1 | `02 14 35 78` | 7 |
| 1.2 | `02 17 35 48` | sink |
| 1.3 | `02 18 35 47` | 4 |
| 1.4 | `07 13 25 48` | 7 |
| 1.5 | `07 14 25 38` | 3 |
| 1.6 | `07 18 25 34` | 1 |
| 3.1 | `01 24 35 78` | 7 |
| 3.2 | `01 27 35 48` | sink |
| 3.3 | `01 28 35 47` | 4 |
| 3.4 | `05 17 23 48` | 6 |
| 3.5 | `05 17 24 38` | 5 |
| 3.6 | `05 17 28 34` | 5 |
| 4.1 | `01 27 34 58` | 7 |
| 4.2 | `01 27 35 48` | 7 |
| 4.3 | `01 27 38 45` | 6 |
| 6.1 | `07 12 34 58` | 7 |
| 6.2 | `07 12 35 48` | 7 |
| 6.3 | `07 12 38 45` | 7 |

## 5. Nineteen concrete rank inputs

The entries are ranks on original wires0 through8. Only these permutations are evaluated by the rank checker.

| Input | Ranks |
|---|---|
| A | `670812345` |
| B | `012356478` |
| C | `071234856` |
| D | `234567801` |
| E | `456701823` |
| F | `015678234` |
| G | `045612738` |
| H | `023415678` |
| I | `340567812` |
| J | `041256783` |
| K | `014526783` |
| L | `051267834` |
| M | `450678123` |
| N | `015623478` |
| O | `450612738` |
| P | `041526783` |
| Q | `450612783` |
| R | `015627384` |
| S | `045612783` |

## 6. Threshold partner intersections

At the L4 cut, each pivot has the displayed endpoint ranks.
A `lo` guard excludes the listed partners because pivot and partner are both at most `high−4` on that input;
a `hi` guard uses values at least `low+4`. Any remaining directed partners fail reciprocity in the following table.
All pivot spans are at least four, forbidding an idle pivot.

| Label | Pivot | Endpoints | Guards | Remaining |
|---|---:|---|---|---|
| 1.1 | 7 | D:1–B:7 | B hi:458; C hi:468; D lo:013; G lo:023 | empty |
| 1.3 | 4 | A:1–F:7 | B hi:578; E lo:013; F hi:267 | empty |
| 1.4 | 7 | G:3–F:8 | A lo:0245; B hi:8; D hi:6; G lo:0125 | 3 |
| 1.5 | 3 | D:1–G:6 | A hi:468; F lo:01; I lo:25; K hi:678 | empty |
| 1.6 | 1 | F:1–C:6 | A hi:468; C hi:678; F lo:03; I lo:25 | empty |
| 3.1 | 7 | D:1–B:7 | B hi:458; C hi:468; D lo:013; G lo:023 | empty |
| 3.3 | 4 | G:1–F:7 | B hi:578; C lo:013; D hi:567; E lo:023 | empty |
| 3.4 | 6 | B:4–A:8 | B lo:0123 | 4578 |
| 3.5 | 5 | E:1–B:6 | A lo:01; B hi:478; D lo:03; G lo:02; H hi:678 | empty |
| 3.6 | 5 | E:1–B:6 | A lo:01; B hi:478; D lo:02; G lo:03; H hi:678 | empty |
| 4.1 | 7 | E:3–F:8 | A lo:0125; B hi:8; D hi:6; E lo:0123; F hi:4 | empty |
| 4.2 | 7 | E:3–R:8 | A lo:0123; B hi:8; D hi:6; E lo:0124; R hi:5 | empty |
| 4.3 | 6 | B:4–A:8 | B lo:0123 | 4578 |
| 6.1 | 7 | E:3–F:8 | B hi:8; D hi:6; E lo:0125; F hi:4; G lo:0123 | empty |
| 6.2 | 7 | E:3–R:8 | B hi:8; D hi:6; E lo:0124; O lo:0123; R hi:5 | empty |
| 6.3 | 7 | E:3–F:8 | B hi:8; D hi:6; E lo:0123; F hi:5; G lo:0124 | empty |

| Label | Pivot | Candidate | Candidate endpoints | Reciprocal guard |
|---|---:|---:|---|---|
| 1.4 | 7 | 3 | F:2–A:7 | Q hi:67 |
| 3.4 | 6 | 4 | D:1–A:5 | A hi:368 |
| 3.4 | 6 | 5 | E:1–B:6 | H hi:678 |
| 3.4 | 6 | 7 | O:3–F:8 | D hi:6 |
| 3.4 | 6 | 8 | S:3–G:8 | G hi:6 |
| 4.3 | 6 | 4 | G:1–J:5 | J hi:567 |
| 4.3 | 6 | 5 | N:3–C:7 | C hi:6 |
| 4.3 | 6 | 7 | E:3–F:8 | D hi:6 |
| 4.3 | 6 | 8 | J:3–B:8 | A hi:6 |

The [independent fixed checker](verify/h9_feedback_round7_proof.py) reads back these printed tables,
checks local clause intersections and signed restrictions, and evaluates the nineteen fixed rank inputs.
It does not enumerate nine-wire matchings or consult any discovery result.
Its [audit](results/h9-feedback-round7-proof.json) records counts and hashes.
