# Fixed fourth-layer tables for `02 15 36`

These tables accompany [the hand classification](h9_recovery_021536_fourths.md).
Case 2 has a separate idle-wire certificate. Rows number signed five-real demands.
A local clause `r:k(edges)` requires k of the listed additional edges.
Each core leaves at most five unused wires; the local table rule is proved in the note.

## Case 1: M=`12 34 56 78`

Forbidden N edges: `02 05 06 12 16 34 35 36 56 78`.

| Row | Original sentinels | Real set | Demand |
|---:|---|---|---:|
| 1 | `+0 +1 +2 -4` | 01478 | 2 |
| 2 | `-0 -1 +2 -4` | 24578 | 2 |
| 3 | `+0 -2 -3 +4` | 14578 | 2 |
| 4 | `-0 +2 +4 +7` | 12347 | 1 |
| 5 | `-0 +2 +4 -7` | 12348 | 1 |

| Forced core | Unmet clauses | Additional edges |
|---|---|---|
| `01 47 58` | 5:1(23) | `23` |
| `01 48 57` | 4:1(23) | `23` |
| `17 25 48` | none | `none / 03` |
| `18 25 47` | none | `none / 03` |

Surviving N: `01 23 47 58`; `01 23 48 57`; `03 17 25 48`; `03 18 25 47`; `17 25 48`; `18 25 47`.

## Case 3: M=`12 37 48`

Forbidden N edges: `02 05 06 12 15 36 37 45 48`.

| Row | Original sentinels | Real set | Demand |
|---:|---|---|---:|
| 1 | `-0 -1 -4 -6` | 25678 | 2 |
| 2 | `+0 -2 -3 -4` | 12678 | 2 |
| 3 | `-0 +2 +4 +5` | 12347 | 1 |
| 4 | `+0 +2 -4 +6` | 01238 | 1 |
| 5 | `-0 +2 +4 +6` | 12348 | 1 |
| 6 | `-0 +2 -4 +6` | 12358 | 1 |
| 7 | `+0 -2 +4 +7` | 13468 | 1 |
| 8 | `-0 -2 +4 +7` | 23468 | 1 |
| 9 | `+2 +3 -4 -5` | 03578 | 1 |
| 10 | `+2 +3 -4 +6` | 01358 | 1 |
| 11 | `+2 +3 -4 -6` | 01578 | 1 |
| 12 | `+2 -4 -5 +6` | 02358 | 1 |

| Forced core | Unmet clauses | Additional edges |
|---|---|---|
| `16 25 78` | 8:1(34); 10:1(03) | `impossible` |
| `16 27 58` | 4:1(03); 8:1(34) | `impossible` |
| `16 28 57` | 3:1(34); 10:1(03) | `impossible` |
| `17 25 68` | 5:1(34); 10:1(03) | `impossible` |
| `17 26 58` | 4:1(03); 7:1(34) | `impossible` |
| `17 28 56` | 7:1(34); 10:1(03) | `impossible` |
| `18 25 67` | 8:1(34); 9:1(03) | `impossible` |
| `18 26 57` | 3:1(34); 12:1(03) | `impossible` |
| `18 27 56` | 8:1(34); 12:1(03) | `impossible` |
| `26 78` | 4:1(01 03 13); 6:1(13 35); 7:1(13 14 34); 12:1(03 35) | `impossible` |
| `27 68` | 5:1(13 14 34); 11:1(01); 12:1(03 35) | `impossible` |
| `28 67` | 7:1(13 14 34); 9:1(03 35); 11:1(01) | `impossible` |

Surviving N: none.

## Case 4: M=`12 37 48 56`

Forbidden N edges: `02 05 06 12 16 36 37 46 48 56`.

| Row | Original sentinels | Real set | Demand |
|---:|---|---|---:|
| 1 | `-0 -1 +2 -4` | 23578 | 2 |
| 2 | `+0 +1 -4 -6` | 01578 | 2 |
| 3 | `+0 -2 -3 +4` | 14578 | 2 |
| 4 | `+0 -2 -3 -4` | 12578 | 2 |
| 5 | `-0 -2 -3 +4` | 24578 | 2 |

| Forced core | Unmet clauses | Additional edges |
|---|---|---|
| none | Odd-core deletion obstruction | `impossible` |

Surviving N: none.

## Case 5: M=`13 24 56 78`

Forbidden N edges: `04 05 06 13 15 16 24 26 56 78`.

| Row | Original sentinels | Real set | Demand |
|---:|---|---|---:|
| 1 | `+0 +1 +2 +4` | 01278 | 2 |
| 2 | `-0 -1 +2 -4` | 34578 | 2 |

| Forced core | Unmet clauses | Additional edges |
|---|---|---|
| `01 27 34 58` | none | `none` |
| `01 27 35 48` | none | `none` |
| `01 27 38 45` | none | `none` |
| `01 28 34 57` | none | `none` |
| `01 28 35 47` | none | `none` |
| `01 28 37 45` | none | `none` |
| `02 17 34 58` | none | `none` |
| `02 17 35 48` | none | `none` |
| `02 17 38 45` | none | `none` |
| `02 18 34 57` | none | `none` |
| `02 18 35 47` | none | `none` |
| `02 18 37 45` | none | `none` |
| `07 12 34 58` | none | `none` |
| `07 12 35 48` | none | `none` |
| `07 12 38 45` | none | `none` |
| `08 12 34 57` | none | `none` |
| `08 12 35 47` | none | `none` |
| `08 12 37 45` | none | `none` |

Surviving N: `01 27 34 58`; `01 27 35 48`; `01 27 38 45`; `01 28 34 57`; `01 28 35 47`; `01 28 37 45`; `02 17 34 58`; `02 17 35 48`; `02 17 38 45`; `02 18 34 57`; `02 18 35 47`; `02 18 37 45`; `07 12 34 58`; `07 12 35 48`; `07 12 38 45`; `08 12 34 57`; `08 12 35 47`; `08 12 37 45`.

## Case 6: M=`13 24 78`

Forbidden N edges: `04 05 06 13 15 16 24 25 78`.

| Row | Original sentinels | Real set | Demand |
|---:|---|---|---:|
| 1 | `+0 +1 +2 +4` | 01278 | 2 |
| 2 | `+0 -2 -3 -4` | 34678 | 2 |
| 3 | `-0 +2 -4 +6` | 14578 | 1 |
| 4 | `-0 +2 -4 +7` | 13457 | 1 |
| 5 | `-0 +2 -4 -7` | 13458 | 1 |
| 6 | `+2 +3 -4 -5` | 03578 | 1 |
| 7 | `+2 -4 -5 +7` | 03457 | 1 |
| 8 | `+2 -4 -5 -7` | 03458 | 1 |

| Forced core | Unmet clauses | Additional edges |
|---|---|---|
| none | Common-pair contact contradiction | `impossible` |

Surviving N: none.

## Case 7: M=`13 27 48`

Forbidden N edges: `05 06 07 13 15 16 27 45 48`.

| Row | Original sentinels | Real set | Demand |
|---:|---|---|---:|
| 1 | `+0 -2 -3 -4` | 23678 | 2 |
| 2 | `-0 -2 -3 +4` | 34678 | 2 |
| 3 | `+0 +2 +4 -5` | 01278 | 1 |
| 4 | `-0 +2 +4 +5` | 12347 | 1 |
| 5 | `-0 +2 -4 +6` | 12578 | 1 |
| 6 | `+2 +3 -4 -5` | 02358 | 2 |

| Forced core | Unmet clauses | Additional edges |
|---|---|---|
| `23 46 78` | 6:1(none) | `impossible` |
| `23 47 68` | 6:1(none) | `impossible` |
| `26 34 78` | 6:2(none) | `impossible` |
| `26 38 47` | 6:1(none) | `impossible` |
| `28 34 67` | 6:1(none) | `impossible` |
| `28 36 47` | 6:1(none) | `impossible` |
| `28 37 46` | 6:1(none) | `impossible` |
| `36 78` | 6:2(02 25) | `impossible` |
| `37 68` | 6:2(02 25) | `impossible` |
| `38 67` | 3:1(01 02 12); 4:1(12 14 24); 5:1(12 25); 6:1(02 25) | `impossible` |

Surviving N: none.

## Case 8: M=`13 27 48 56`

Forbidden N edges: `05 06 07 13 15 16 27 46 48 56`.

| Row | Original sentinels | Real set | Demand |
|---:|---|---|---:|
| 1 | `+0 +1 +2 +4` | 01248 | 2 |
| 2 | `+0 +1 +2 -4` | 01238 | 2 |
| 3 | `-0 -1 +2 -4` | 23578 | 2 |
| 4 | `+0 +1 -4 -6` | 02358 | 2 |
| 5 | `-0 -2 -3 +4` | 34578 | 2 |

| Forced core | Unmet clauses | Additional edges |
|---|---|---|
| `01 24 38` | 4:1(none) | `impossible` |
| `01 28` | 4:1(35); 5:2(34 35 37 45 47 57) | `35 47` |
| `02 14 38` | 5:1(57) | `57` |
| `02 18` | 3:2(35 37 57) | `impossible` |
| `03 14 28` | 5:2(57) | `impossible` |
| `03 18 24` | 5:2(57) | `impossible` |
| `04 12 38` | 4:1(none) | `impossible` |
| `04 18 23` | 5:2(57) | `impossible` |
| `08 12` | 3:2(35 37 57) | `impossible` |
| `08 14 23` | 5:2(57) | `impossible` |

Surviving N: `01 28 35 47`; `02 14 38 57`.

## Case 9: M=`14 23 56 78`

Forbidden N edges: `03 05 06 14 16 23 26 46 56 78`.

| Row | Original sentinels | Real set | Demand |
|---:|---|---|---:|
| 1 | `+0 +1 +2 +4` | 01278 | 2 |
| 2 | `+0 +1 +2 -4` | 02478 | 2 |
| 3 | `+0 -2 -3 +4` | 13578 | 2 |
| 4 | `+0 -2 -3 -4` | 34578 | 2 |

| Forced core | Unmet clauses | Additional edges |
|---|---|---|
| `02 17 35 48` | none | `none` |
| `02 18 35 47` | none | `none` |

Surviving N: `02 17 35 48`; `02 18 35 47`.

## Case 10: M=`14 23 78`

Forbidden N edges: `03 05 06 14 15 23 26 45 78`.

| Row | Original sentinels | Real set | Demand |
|---:|---|---|---:|
| 1 | `+0 +1 +2 +4` | 01278 | 2 |
| 2 | `-0 -1 +2 -4` | 23578 | 1 |
| 3 | `-0 -1 +2 +7` | 23457 | 1 |
| 4 | `-0 -1 +2 -7` | 23458 | 1 |
| 5 | `+0 -2 -3 +4` | 13678 | 2 |
| 6 | `-0 +2 +4 +7` | 12347 | 1 |
| 7 | `-0 +2 +4 -7` | 12348 | 1 |

| Forced core | Unmet clauses | Additional edges |
|---|---|---|
| `02 17 36` | 3:1(none) | `impossible` |
| `02 17 38` | 3:1(none) | `impossible` |
| `02 17 68` | 2:1(35); 7:1(34) | `impossible` |
| `02 18 36` | 4:1(none) | `impossible` |
| `02 18 37` | 4:1(none) | `impossible` |
| `02 18 67` | 2:1(35); 6:1(34) | `impossible` |
| `07 18 36` | 2:1(25); 6:1(24) | `impossible` |
| `08 17 36` | 2:1(25); 7:1(24) | `impossible` |
| `17 28 36` | 3:1(none) | `impossible` |
| `18 27 36` | 4:1(none) | `impossible` |

Surviving N: none.

## Case 11: M=`14 27 38`

Forbidden N edges: `05 06 07 14 15 27 36 38 45`.

| Row | Original sentinels | Real set | Demand |
|---:|---|---|---:|
| 1 | `+0 +1 +4 -6` | 01268 | 2 |
| 2 | `+0 +1 -4 -6` | 02468 | 2 |
| 3 | `+0 -2 -3 +4` | 12678 | 2 |
| 4 | `+0 -2 -3 -4` | 24678 | 2 |

| Forced core | Unmet clauses | Additional edges |
|---|---|---|
| none | Odd-core deletion obstruction | `impossible` |

Surviving N: none.

## Case 12: M=`14 27 38 56`

Forbidden N edges: `05 06 07 14 16 27 36 38 46 56`.

| Row | Original sentinels | Real set | Demand |
|---:|---|---|---:|
| 1 | `+0 +1 +4 -6` | 01258 | 2 |
| 2 | `+0 +1 -4 -6` | 02458 | 2 |
| 3 | `+0 -2 -3 +4` | 12578 | 2 |
| 4 | `+0 -2 -3 -4` | 24578 | 2 |

| Forced core | Unmet clauses | Additional edges |
|---|---|---|
| none | Odd-core deletion obstruction | `impossible` |

Surviving N: none.

## Case 13: M=`17 23 48`

Forbidden N edges: `03 05 06 15 17 23 26 45 48`.

| Row | Original sentinels | Real set | Demand |
|---:|---|---|---:|
| 1 | `-0 -1 +2 +8` | 23457 | 1 |
| 2 | `+0 +1 +4 -5` | 01268 | 1 |
| 3 | `+0 -2 -3 -4` | 13678 | 2 |
| 4 | `-0 +2 +3 +4` | 12478 | 1 |
| 5 | `+0 +2 +4 -5` | 01238 | 1 |
| 6 | `-0 +2 +4 +5` | 12347 | 1 |
| 7 | `-0 +2 -4 +7` | 12358 | 1 |
| 8 | `+2 +3 -4 -5` | 02578 | 2 |

| Forced core | Unmet clauses | Additional edges |
|---|---|---|
| `02 13 57 68` | 4:1(none) | `impossible` |
| `02 13 58 67` | 4:1(none) | `impossible` |
| `02 13 78` | 1:1(none) | `impossible` |
| `02 16 37 58` | 4:1(none) | `impossible` |
| `02 16 38 57` | 6:1(none) | `impossible` |
| `02 16 78` | 6:1(34); 7:1(35) | `impossible` |
| `02 18 36 57` | 6:1(none) | `impossible` |
| `02 36 78` | 7:1(none) | `impossible` |
| `07 13 25 68` | 4:1(none) | `impossible` |
| `07 16 25 38` | 6:1(none) | `impossible` |
| `07 18 25 36` | 6:1(none) | `impossible` |
| `08 13 25 67` | 4:1(none) | `impossible` |
| `08 16 25 37` | 4:1(none) | `impossible` |
| `13 25 78` | 2:1(none) | `impossible` |
| `16 25 78` | 5:1(none) | `impossible` |
| `25 36 78` | 5:1(01); 6:1(14) | `impossible` |

Surviving N: none.

## Case 14: M=`17 23 48 56`

Forbidden N edges: `03 05 06 16 17 23 26 46 48 56`.

| Row | Original sentinels | Real set | Demand |
|---:|---|---|---:|
| 1 | `+0 +1 +2 -4` | 01278 | 2 |
| 2 | `-0 -1 +2 -4` | 23578 | 2 |
| 3 | `+0 -2 -3 -4` | 13578 | 2 |
| 4 | `+0 +2 +4 -6` | 01348 | 1 |
| 5 | `+2 +3 -4 -5` | 02578 | 2 |

| Forced core | Unmet clauses | Additional edges |
|---|---|---|
| `02 35 78` | 4:1(14) | `14` |

Surviving N: `02 14 35 78`.

## Case 15: M=`17 24 38`

Forbidden N edges: `04 05 06 15 17 24 25 36 38`.

| Row | Original sentinels | Real set | Demand |
|---:|---|---|---:|
| 1 | `+0 +1 +2 +4` | 01238 | 2 |
| 2 | `-0 -1 -2 -4` | 35678 | 1 |
| 3 | `+0 -2 -3 -4` | 14678 | 2 |
| 4 | `+0 +2 -4 +6` | 01347 | 1 |
| 5 | `-0 +2 +4 +6` | 12347 | 1 |
| 6 | `-0 +2 -4 +6` | 13457 | 1 |
| 7 | `-0 +2 -4 +7` | 13458 | 1 |
| 8 | `+0 -2 +4 +8` | 12346 | 1 |
| 9 | `+2 +3 -4 -5` | 03578 | 1 |
| 10 | `+2 -4 -5 +6` | 03457 | 1 |
| 11 | `+2 -4 -5 -6` | 04578 | 1 |

| Forced core | Unmet clauses | Additional edges |
|---|---|---|
| `01 23 46 78` | 10:1(none) | `impossible` |
| `01 23 47 68` | 9:1(none) | `impossible` |
| `01 23 48 67` | 10:1(none) | `impossible` |
| `02 13 46 78` | 10:1(none) | `impossible` |
| `02 13 47 68` | 9:1(none) | `impossible` |
| `02 13 48 67` | 10:1(none) | `impossible` |
| `02 18 46` | 5:1(37); 11:1(57) | `impossible` |
| `02 18 47` | 8:1(none) | `impossible` |
| `02 18 67` | 9:1(35); 11:1(45) | `impossible` |
| `03 12 46 78` | 7:1(none) | `impossible` |
| `03 12 47 68` | 7:1(none) | `impossible` |
| `03 12 48 67` | 6:1(none) | `impossible` |
| `03 14 28 67` | 11:1(none) | `impossible` |
| `03 16 28 47` | 7:1(none) | `impossible` |
| `03 18 46` | 5:1(27); 11:1(57) | `impossible` |
| `03 18 47` | 2:1(56); 8:1(26) | `impossible` |
| `03 18 67` | 8:1(none) | `impossible` |
| `08 14 23 67` | 10:1(none) | `impossible` |
| `08 16 23 47` | 7:1(none) | `impossible` |
| `18 23 46` | 4:1(07); 6:1(57) | `impossible` |
| `18 23 47` | 9:1(none) | `impossible` |
| `18 23 67` | 9:1(none) | `impossible` |

Surviving N: none.

## Case 16: M=`17 24 38 56`

Forbidden N edges: `04 05 06 16 17 24 26 36 38 56`.

| Row | Original sentinels | Real set | Demand |
|---:|---|---|---:|
| 1 | `+0 +1 +2 +4` | 01238 | 2 |
| 2 | `-0 -1 +2 -4` | 34578 | 2 |
| 3 | `+0 +1 +4 -6` | 01258 | 2 |
| 4 | `+0 -2 -3 +4` | 12458 | 2 |
| 5 | `+0 -2 -3 -4` | 14578 | 2 |

| Forced core | Unmet clauses | Additional edges |
|---|---|---|
| `01 23 58` | 4:1(none) | `impossible` |
| `01 28` | 5:2(45 47 57) | `impossible` |
| `02 13 58` | 4:1(none) | `impossible` |
| `02 18` | 2:2(34 35 37 45 47 57); 4:1(45) | `37 45` |
| `03 12 58` | 5:1(47) | `47` |
| `03 15 28` | 2:2(47) | `impossible` |
| `03 18 25` | 2:2(47) | `impossible` |
| `08 12` | 5:2(45 47 57) | `impossible` |
| `08 13 25` | 5:2(47) | `impossible` |
| `08 15 23` | 4:1(none) | `impossible` |

Surviving N: `02 18 37 45`; `03 12 47 58`.

## Case 17: M=`17 28 34`

Forbidden N edges: `05 06 08 15 17 28 34 35 36`.

| Row | Original sentinels | Real set | Demand |
|---:|---|---|---:|
| 1 | `+0 -2 -3 +4` | 12468 | 2 |
| 2 | `-0 +2 +3 +4` | 12347 | 1 |
| 3 | `-0 -2 -3 +4` | 14678 | 2 |
| 4 | `-0 +2 +4 +5` | 12378 | 1 |
| 5 | `+2 +3 -4 -5` | 02457 | 2 |

| Forced core | Unmet clauses | Additional edges |
|---|---|---|
| none | Weighted demand17 exceeds capacity16 | `impossible` |

Surviving N: none.

## Case 18: M=`17 28 34 56`

Forbidden N edges: `05 06 08 16 17 28 34 35 36 56`.

| Row | Original sentinels | Real set | Demand |
|---:|---|---|---:|
| 1 | `-0 -1 +2 -4` | 24578 | 2 |
| 2 | `+0 +1 +4 -6` | 01245 | 2 |
| 3 | `+0 -2 -3 +4` | 12458 | 2 |
| 4 | `+2 +3 -4 -5` | 02457 | 2 |

| Forced core | Unmet clauses | Additional edges |
|---|---|---|
| none | Odd-core deletion obstruction | `impossible` |

Surviving N: none.

