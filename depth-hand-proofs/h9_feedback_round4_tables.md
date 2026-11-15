# Fixed certificate tables for the H9 case `02 16 37`

These are the explicit finite premises of the [hand proof](h9_feedback_round4_021637.md).
A two-digit string denotes an unordered comparator; a longer string denotes a set of positions.
Sentinels are placed at the original network inputs. Every displayed real set is at the stated layer boundary.

## 1. Ordered pairs after L3

Each pair below is already ordered and may be omitted from L4. The proof gives the min/max derivation rule and the additional common upper bound at wire7.

| Case | L3 | Forbidden L4 pairs |
|---:|---|---|
| 1 | `12 34 58` | `02 06 07 12 16 34 37 38 58` |
| 2 | `12 34 58 67` | `02 06 07 12 17 27 34 37 38 58 67` |
| 3 | `12 35 48` | `02 06 07 12 16 35 37 45 48` |
| 4 | `12 35 48 67` | `02 06 07 12 17 27 35 37 45 48 67` |
| 5 | `13 24 58` | `04 06 07 13 16 17 24 28 58` |
| 6 | `13 24 58 67` | `04 06 07 13 16 17 24 27 28 37 58 67` |
| 7 | `13 25 48` | `05 06 07 13 16 17 25 45 48` |
| 8 | `13 25 48 67` | `05 06 07 13 16 17 25 27 37 45 48 67` |
| 9 | `14 25 38` | `05 06 07 14 15 16 25 37 38` |
| 10 | `14 25 38 67` | `05 06 07 14 15 17 25 27 37 38 67` |
| 11 | `14 28 35` | `06 07 08 14 15 16 28 35 37` |
| 12 | `14 28 35 67` | `06 07 08 14 15 17 27 28 35 37 67` |
| 13 | `15 24 38` | `04 06 07 15 16 24 25 37 38` |
| 14 | `15 24 38 67` | `04 06 07 15 17 24 25 27 37 38 67` |

## 2. Direct five-real contradictions

Every row in this section retains exactly one RR gate through L3, so L4 requires two edges in R.

| Case | Input sentinels | R after L3 |
|---:|---|---|
| 1 | `+0 +1 +2 +4` | 01345 |
| 1 | `+0 +1 +2 -4` | 01458 |
| 1 | `-0 -1 +2 +4` | 23456 |
| 1 | `-0 -1 +2 -4` | 24568 |
| 1 | `+0 -2 -3 +4` | 12457 |
| 3 | `+0 +1 +2 +4` | 01348 |
| 3 | `+0 +1 +2 -4` | 01358 |
| 3 | `-0 -1 +2 +4` | 23468 |
| 3 | `+0 -2 -3 -4` | 12578 |
| 5 | `-0 -1 +2 +4` | 23456 |
| 5 | `-0 -1 +2 -4` | 34568 |
| 5 | `+0 -2 -3 +4` | 23457 |
| 5 | `+0 -2 -3 -4` | 34578 |
| 7 | `-0 -1 +2 +4` | 23468 |
| 7 | `-0 -1 +2 -4` | 23568 |
| 7 | `+0 +1 -4 -7` | 02378 |
| 9 | `-0 -1 -2 -3` | 45678 |
| 9 | `-0 -1 +2 +4` | 23468 |
| 9 | `+0 +1 -4 -7` | 02478 |
| 9 | `-0 -1 +4 -7` | 24678 |
| 11 | `-0 -1 -2 -3` | 45678 |
| 11 | `+0 +1 +2 +4` | 01234 |
| 11 | `-0 -1 -2 +4` | 34678 |
| 11 | `+0 -2 -3 -4` | 24578 |
| 12 | `+0 +1 +2 +4` | 01234 |
| 12 | `-0 -1 +2 +4` | 23468 |
| 12 | `+0 +1 -4 -7` | 02456 |
| 12 | `+2 +3 +4 -6` | 02346 |
| 13 | `-0 -1 -2 -3` | 45678 |
| 13 | `+0 +1 +2 +4` | 01238 |
| 13 | `-0 -1 +2 -4` | 34568 |
| 13 | `+0 +1 +4 -7` | 01278 |

For the strict cases, these are twice the vertex prices, the twice-gate charge g, and the resulting budget. The required twice-total is four times the number of rows.

| Case | Twice vertex prices at 0,...,8 | g | Budget | Demand |
|---:|---|---:|---:|---:|
| 1 | `2,2,2,0,6,4,2,0,0` | 0 | 18 | 20 |
| 3 | `0,2,0,2,0,0,0,0,2` | 2 | 14 | 16 |
| 7 | `0,0,3,3,0,0,2,0,3` | 0 | 11 | 12 |
| 9 | `0,0,2,0,4,0,2,2,4` | 0 | 14 | 16 |
| 11 | `0,0,0,0,2,0,0,2,2` | 2 | 14 | 16 |
| 12 | `2,0,4,2,4,0,2,0,0` | 0 | 14 | 16 |

Cases5 and13 use the two parity arguments in the main proof; no strict price witness is claimed for them.

## 3. Fourth-layer demands

Demand2 rows retain one RR gate through L3; the sole demand1 row retains two.

| Case | Input sentinels | R after L3 | Required L4 edges in R |
|---:|---|---|---:|
| 2 | `+0 +1 +2 +4` | 01345 | 2 |
| 2 | `+0 +1 +2 -4` | 01458 | 2 |
| 2 | `-0 -1 +2 +4` | 23456 | 2 |
| 2 | `-0 -1 +2 -4` | 24568 | 2 |
| 2 | `+0 +1 +4 -7` | 01456 | 2 |
| 2 | `+0 -2 -3 +4` | 12456 | 2 |
| 4 | `+0 +1 +2 +4` | 01348 | 2 |
| 4 | `+0 +1 +2 -4` | 01358 | 2 |
| 4 | `-0 -1 +2 +4` | 23468 | 2 |
| 4 | `-0 -1 +2 -4` | 23568 | 2 |
| 4 | `+0 +1 -4 -7` | 01568 | 2 |
| 4 | `+0 -2 -3 -4` | 12568 | 2 |
| 6 | `+0 +1 +2 +4` | 01235 | 2 |
| 6 | `-0 -1 +2 +4` | 23456 | 2 |
| 6 | `-0 -1 +2 -4` | 34568 | 2 |
| 6 | `+0 +1 +4 -7` | 02356 | 2 |
| 6 | `+0 +2 -4 -5` | 01348 | 1 |
| 8 | `+0 +1 +2 -4` | 01238 | 2 |
| 8 | `-0 -1 +2 +4` | 23468 | 2 |
| 8 | `-0 -1 +2 -4` | 23568 | 2 |
| 8 | `+0 +1 -4 -7` | 02368 | 2 |
| 10 | `+0 +1 +2 -4` | 02348 | 2 |
| 10 | `-0 -1 +2 +4` | 23468 | 2 |
| 10 | `+0 +1 -4 -7` | 02468 | 2 |
| 10 | `+0 -2 -3 +4` | 12468 | 2 |
| 10 | `+0 -2 -3 -4` | 24568 | 2 |
| 14 | `+0 +1 +2 +4` | 01238 | 2 |
| 14 | `-0 -1 +2 -4` | 34568 | 2 |
| 14 | `+0 +1 +4 -7` | 01268 | 2 |
| 14 | `+0 -2 -3 +4` | 12468 | 2 |
| 14 | `+0 -2 -3 -4` | 14568 | 2 |

The two seven-real restrictions retain five gates of height two. Every listed sink must be touched by an L4 RR edge.

| Case | Input sentinels | Real positions after L3 | Sinks |
|---:|---|---|---|
| 8 | `+0 +2` | 0123458 | `13 25 48` |
| 10 | `+0 +2` | 0123458 | `14 25 38` |

The matching arguments in the main proof leave precisely these forms. Labels C.N are used below.

| Label | L4 |
|---|---|
| 2.1 | `01 26 45` |
| 2.2 | `01 26 45 78` |
| 4.1 | `01 26 34 58` |
| 6.1 | `01 23 48 56` |
| 6.2 | `01 25 36 48` |
| 6.3 | `01 26 35 48` |
| 6.4 | `02 18 35 46` |
| 8.1 | `01 28 36` |
| 8.2 | `01 28 36 57` |
| 8.3 | `01 28 36 47` |
| 10.1 | `03 24 68` |
| 10.2 | `03 24 57 68` |
| 14.1 | `02 18 35 46` |
| 14.2 | `03 12 45 68` |

## 4. Fourteen real inputs for every ending

Each nine-digit string is a permutation of ranks0 through8 on the original inputs. No enumeration of rank permutations is a premise.

| Input | Ranks on wires0,...,8 |
|---|---|
| A | `456701823` |
| B | `450167823` |
| C | `014567238` |
| D | `567801234` |
| E | `345678012` |
| F | `345601782` |
| G | `670123845` |
| H | `051236748` |
| I | `012567384` |
| J | `345607128` |
| K | `234506781` |
| L | `012734586` |
| M | `051623784` |
| N | `123456780` |

The attainable-rank interval lemma and two-layer forward-cone bound exclude any idle wire or comparison output with two witnessed ranks differing by at least four.
The following plans use only those exclusions. In a forced plan, earlier forced edges remove their vertices from later partner choices. In the Hall row, three required vertices have only two possible outside partners.

| Label | Consequence of endpoint rows |
|---|---|
| 2.1 | wire0 must be used but has no partner |
| 2.2 | wire0 must be used but has no partner |
| 4.1 | force 03, then 14, then 52, then 68 |
| 6.1 | force 87, then 62, then 34, then 15 |
| 6.2 | wire5 must be used but has no partner |
| 6.3 | wire5 must be used but has no partner |
| 6.4 | required wires3,5,8 can only meet2,4 |
| 8.1 | wire8 must be used but has no partner |
| 8.2 | wire8 must be used but has no partner |
| 8.3 | wire8 must be used but has no partner |
| 10.1 | wire1 must be used but has no partner |
| 10.2 | wire1 must be used but has no partner |
| 14.1 | wire8 must be used but has no partner |
| 14.2 | wire8 must be used but has no partner |

## 5. Rank endpoint rows

`idle` is the value on the pivot itself; `min` or `max` is the indicated output of its proposed next comparison. Each low/high cell names a bank input and the rank actually produced.
Partner lists combine rows with identical witnesses and values. Every gap is at least four.

### 2.1

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 0 | idle | idle | B:0 | A:4 |
| 0 | 1 | max | C:1 | G:6 |
| 0 | 2,6,7 | min | B:0 | A:4 |
| 0 | 3 | max | B:1 | I:5 |
| 0 | 4 | max | N:1 | C:6 |
| 0 | 5 | max | D:3 | C:7 |
| 0 | 8 | max | F:3 | C:8 |

### 2.2

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 0 | idle | idle | B:0 | A:4 |
| 0 | 1 | max | C:1 | G:6 |
| 0 | 2,6,8 | min | B:0 | A:4 |
| 0 | 3 | max | B:1 | I:5 |
| 0 | 4 | max | N:1 | C:6 |
| 0 | 5 | max | D:3 | C:7 |
| 0 | 7 | max | F:3 | B:7 |

### 4.1

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 0 | idle | idle | B:0 | A:4 |
| 0 | 1 | max | C:1 | G:6 |
| 0 | 2,6,7 | min | B:0 | A:4 |
| 0 | 4 | max | D:2 | C:6 |
| 0 | 5 | max | K:2 | C:7 |
| 0 | 8 | max | A:4 | C:8 |
| 1 | idle | idle | C:1 | G:6 |
| 1 | 2 | min | C:1 | A:5 |
| 1 | 5 | max | K:3 | C:7 |
| 1 | 6,7 | min | C:1 | G:6 |
| 1 | 8 | min | C:1 | G:5 |
| 5 | idle | idle | K:1 | C:7 |
| 5 | 6 | min | K:1 | B:5 |
| 5 | 7 | min | K:1 | B:6 |
| 5 | 8 | min | K:1 | C:7 |
| 6 | idle | idle | I:3 | A:7 |
| 6 | 7 | min | I:3 | A:7 |

### 6.1

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 8 | idle | idle | M:4 | C:8 |
| 8 | 0 | max | M:4 | C:8 |
| 8 | 1 | min | B:1 | D:5 |
| 8 | 2 | min | A:0 | B:4 |
| 8 | 3 | min | J:2 | G:6 |
| 8 | 4 | min | F:2 | E:7 |
| 8 | 5 | min | N:0 | H:4 |
| 8 | 6 | min | B:3 | C:7 |
| 6 | idle | idle | B:3 | A:7 |
| 6 | 0 | max | B:3 | A:7 |
| 6 | 1 | min | B:1 | D:5 |
| 6 | 3 | min | J:2 | F:6 |
| 6 | 4 | min | F:2 | C:6 |
| 6 | 5 | min | N:0 | H:4 |
| 3 | idle | idle | J:2 | G:7 |
| 3 | 0 | max | J:2 | G:7 |
| 3 | 1 | min | B:1 | M:5 |
| 3 | 5 | min | N:0 | H:4 |
| 1 | idle | idle | B:1 | D:5 |
| 1 | 0 | max | B:1 | D:5 |

### 6.2

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 5 | idle | idle | A:1 | C:7 |
| 5 | 0 | max | A:2 | C:7 |
| 5 | 1 | max | G:3 | C:7 |
| 5 | 2 | max | A:1 | C:7 |
| 5 | 3 | max | D:3 | C:7 |
| 5 | 4 | min | A:1 | C:6 |
| 5 | 6 | min | A:1 | H:5 |
| 5 | 7 | min | A:1 | H:6 |
| 5 | 8 | min | A:1 | C:7 |

### 6.3

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 5 | idle | idle | E:2 | C:7 |
| 5 | 0 | max | E:2 | C:7 |
| 5 | 1 | min | B:1 | M:5 |
| 5 | 2 | max | D:3 | C:7 |
| 5 | 3 | min | N:0 | H:5 |
| 5 | 4 | min | E:2 | C:6 |
| 5 | 6 | min | E:2 | F:6 |
| 5 | 7 | min | E:2 | G:7 |
| 5 | 8 | min | E:2 | C:7 |

### 6.4

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 3 | idle | idle | N:0 | H:5 |
| 3 | 0 | max | A:1 | H:5 |
| 3 | 1 | max | E:1 | H:5 |
| 3 | 5,7,8 | min | N:0 | H:5 |
| 3 | 6 | min | N:0 | H:4 |
| 5 | idle | idle | E:2 | C:7 |
| 5 | 0 | max | D:3 | C:7 |
| 5 | 1 | max | E:2 | C:7 |
| 5 | 3 | min | N:0 | H:5 |
| 5 | 6 | min | E:2 | C:6 |
| 5 | 7 | min | E:2 | G:7 |
| 5 | 8 | min | E:2 | C:7 |
| 8 | idle | idle | A:3 | C:8 |
| 8 | 0,1 | max | A:3 | C:8 |
| 8 | 3 | min | N:0 | H:5 |
| 8 | 5 | min | E:2 | C:7 |
| 8 | 6 | min | A:3 | E:7 |
| 8 | 7 | min | A:3 | B:7 |

### 8.1

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 8 | idle | idle | F:2 | C:8 |
| 8 | 0 | max | A:3 | C:8 |
| 8 | 1 | max | A:4 | C:8 |
| 8 | 2 | max | F:2 | C:8 |
| 8 | 3 | min | E:1 | L:5 |
| 8 | 4 | min | A:0 | C:6 |
| 8 | 5 | min | F:2 | C:7 |
| 8 | 6 | min | F:2 | L:6 |
| 8 | 7 | min | F:2 | H:7 |

### 8.2

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 8 | idle | idle | F:2 | C:8 |
| 8 | 0 | max | A:3 | C:8 |
| 8 | 1 | max | A:4 | C:8 |
| 8 | 2 | max | F:2 | C:8 |
| 8 | 3 | min | E:1 | L:5 |
| 8 | 4 | min | A:0 | C:6 |
| 8 | 5 | min | F:2 | B:6 |
| 8 | 6 | min | F:2 | L:6 |
| 8 | 7 | min | F:2 | C:7 |

### 8.3

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 8 | idle | idle | F:2 | C:8 |
| 8 | 0 | max | A:3 | C:8 |
| 8 | 1 | max | A:4 | C:8 |
| 8 | 2,4 | max | F:2 | C:8 |
| 8 | 3 | min | E:1 | L:5 |
| 8 | 5 | min | F:2 | C:7 |
| 8 | 6 | min | F:2 | L:6 |
| 8 | 7 | min | F:2 | H:7 |

### 10.1

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 1 | idle | idle | A:0 | B:5 |
| 1 | 0 | max | C:1 | B:5 |
| 1 | 2 | min | A:0 | B:4 |
| 1 | 3 | max | G:2 | L:6 |
| 1 | 4,5,7 | min | A:0 | B:5 |
| 1 | 6 | max | C:2 | F:6 |
| 1 | 8 | max | E:4 | C:8 |

### 10.2

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 1 | idle | idle | A:0 | B:5 |
| 1 | 0 | max | C:1 | B:5 |
| 1 | 2 | min | A:0 | B:4 |
| 1 | 3 | max | G:2 | L:6 |
| 1 | 4,5,7 | min | A:0 | B:5 |
| 1 | 6 | max | C:2 | F:6 |
| 1 | 8 | max | E:4 | C:8 |

### 14.1

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 8 | idle | idle | E:2 | C:8 |
| 8 | 0 | max | A:3 | C:8 |
| 8 | 1,3 | max | E:2 | C:8 |
| 8 | 2 | max | A:4 | C:8 |
| 8 | 4 | max | E:4 | C:8 |
| 8 | 5 | min | E:2 | C:7 |
| 8 | 6 | min | E:2 | C:6 |
| 8 | 7 | min | E:2 | H:7 |

### 14.2

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 8 | idle | idle | B:3 | C:8 |
| 8 | 0,6 | max | B:3 | C:8 |
| 8 | 1 | max | B:4 | C:8 |
| 8 | 2 | min | A:1 | H:5 |
| 8 | 3 | min | B:1 | L:6 |
| 8 | 4 | min | D:2 | C:6 |
| 8 | 5 | min | B:3 | C:7 |
| 8 | 7 | min | B:3 | A:7 |

## 6. The two forced endings violate a sink contact

Each row retains exactly three RR gates through L4. The forced L5 matching has no RR edge touching the named sink.

| Label | Forced L5 | Input sentinels | R after L4 | Sink |
|---|---|---|---|---|
| 4.1 | `03 14 25 68` | `+0 +1 +2 -4` | 01458 | 58 |
| 6.1 | `15 26 34 78` | `+0 +1 +2 +4` | 01235 | 23 |

The [independent checker](verify/h9_feedback_round4_proof.py) checks every displayed premise and the complete coverage of the endpoint plans. Its [audit](results/h9-feedback-round4-proof.json) records the finite counts and source hashes.
