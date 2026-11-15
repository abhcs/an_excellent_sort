# Fixed tables for the H9 case `02 14 56`

These are the finite premises of the [hand proof](h9_feedback_round5_021456.md).
Comparators use two digits; longer strings denote position sets. Signed placements refer to original inputs.
Every demand row retains exactly `3-demand` RR gates through L3.

## 1. Ordered pairs after L3

| Case | L3 | Forbidden L4 pairs |
|---:|---|---|
| 1 | `12 35 46 78` | `02 05 06 12 14 16 35 36 46 78` |
| 2 | `12 37 46 58` | `02 06 07 12 14 16 37 46 56 58` |
| 3 | `13 25 46 78` | `03 05 06 13 14 16 25 26 46 78` |
| 4 | `13 27 46 58` | `03 06 07 13 14 16 27 46 56 58` |
| 5 | `15 23 46 78` | `02 03 06 14 15 16 23 46 56 78` |
| 6 | `15 27 38 46` | `06 07 08 14 15 16 27 38 46 56` |
| 7 | `17 23 46 58` | `02 03 06 14 16 17 23 46 56 58` |
| 8 | `17 25 38 46` | `05 06 08 14 16 17 25 26 38 46` |
| 9 | `17 28 35 46` | `05 06 08 14 16 17 28 35 36 46` |

## 2. Five-real demands

| Case | Row | Input sentinels | Reals after L3 | Required L4 edges |
|---:|---:|---|---|---:|
| 1 | 1 | `+0 +1 +2 +4` | 01378 | 2 |
| 1 | 2 | `-0 -1 +2 -4` | 23678 | 1 |
| 1 | 3 | `+0 -2 -4 -5` | 24578 | 2 |
| 1 | 4 | `-0 +2 -4 +7` | 23467 | 1 |
| 1 | 5 | `-0 +2 -4 -7` | 23468 | 1 |
| 2 | 1 | `+0 +1 +2 +4` | 01358 | 2 |
| 2 | 2 | `+0 +1 +2 -6` | 01348 | 2 |
| 2 | 3 | `+0 -2 -4 -5` | 23478 | 2 |
| 2 | 4 | `-0 +2 -4 -5` | 23468 | 2 |
| 2 | 5 | `+0 -2 +4 +6` | 12357 | 1 |
| 3 | 1 | `+0 +1 +2 +4` | 01278 | 2 |
| 3 | 2 | `+0 +1 -4 +7` | 02347 | 1 |
| 3 | 3 | `+0 +1 -4 -7` | 02348 | 1 |
| 3 | 4 | `-0 +2 -4 -5` | 45678 | 1 |
| 3 | 5 | `-0 -2 -4 -5` | 34678 | 1 |
| 3 | 6 | `+0 -2 +4 +7` | 12357 | 1 |
| 3 | 7 | `+0 -2 +4 -7` | 12358 | 1 |
| 3 | 8 | `-0 -2 +4 +7` | 13457 | 1 |
| 3 | 9 | `-0 -2 +4 -7` | 13458 | 1 |
| 3 | 10 | `+0 +2 -6 +7` | 01457 | 1 |
| 3 | 11 | `+0 +2 -6 -7` | 01458 | 1 |
| 3 | 12 | `+0 -4 -5 +7` | 03457 | 1 |
| 3 | 13 | `+0 -4 -5 -7` | 03458 | 1 |
| 4 | 1 | `+0 +1 +2 -6` | 01248 | 2 |
| 4 | 2 | `+0 +1 -4 -5` | 02348 | 2 |
| 4 | 3 | `+0 -2 -4 -5` | 23478 | 2 |
| 4 | 4 | `-0 -2 -4 -5` | 34678 | 2 |
| 4 | 5 | `-0 +2 +4 +6` | 12457 | 1 |
| 4 | 6 | `-0 -2 +4 +6` | 13457 | 1 |
| 5 | 1 | `-0 -1 -2 +4` | 34578 | 2 |
| 5 | 2 | `+0 +1 +4 +5` | 01278 | 1 |
| 5 | 3 | `+0 +1 -4 -5` | 02478 | 1 |
| 5 | 4 | `+0 +1 +4 +7` | 01257 | 1 |
| 5 | 5 | `+0 +1 +4 -7` | 01258 | 1 |
| 5 | 6 | `+0 +1 -4 +7` | 02457 | 1 |
| 5 | 7 | `+0 +1 -4 -7` | 02458 | 1 |
| 5 | 8 | `-0 +2 -4 -5` | 24678 | 1 |
| 5 | 9 | `+0 -2 +4 +7` | 12357 | 1 |
| 5 | 10 | `+0 -2 +4 -7` | 12358 | 1 |
| 5 | 11 | `-0 +2 -4 +7` | 24567 | 1 |
| 5 | 12 | `-0 +2 -4 -7` | 24568 | 1 |
| 6 | 1 | `+0 +1 +2 +4` | 01235 | 2 |
| 6 | 2 | `+0 +1 +2 -4` | 02345 | 2 |
| 6 | 3 | `-0 -1 +2 -4` | 23567 | 1 |
| 6 | 4 | `-0 -1 -2 -4` | 35678 | 1 |
| 6 | 5 | `+0 -2 -3 +4` | 12578 | 1 |
| 6 | 6 | `-0 +2 -3 +4` | 13457 | 1 |
| 6 | 7 | `-0 +2 -3 -4` | 34567 | 1 |
| 6 | 8 | `+0 -2 +4 +5` | 12378 | 1 |
| 6 | 9 | `+0 -2 +4 -5` | 23578 | 1 |
| 6 | 10 | `+0 -2 -4 -5` | 23478 | 1 |
| 6 | 11 | `-0 +2 -4 -5` | 23467 | 1 |
| 7 | 1 | `-0 -1 -2 +4` | 34578 | 2 |
| 7 | 2 | `+0 +1 -4 +8` | 02457 | 1 |
| 7 | 3 | `+0 +1 -6 +7` | 01248 | 1 |
| 7 | 4 | `+0 -2 -4 -5` | 23478 | 2 |
| 7 | 5 | `-0 +2 -4 -5` | 24678 | 2 |
| 7 | 6 | `-0 -2 -4 -5` | 34678 | 2 |
| 7 | 7 | `-0 +2 +4 +6` | 12457 | 1 |
| 7 | 8 | `-0 +2 +4 +7` | 12458 | 1 |
| 8 | 1 | `+0 +1 +2 +4` | 01237 | 2 |
| 8 | 2 | `+0 +1 +2 -4` | 02347 | 2 |
| 8 | 3 | `+0 -2 +4 +5` | 12358 | 1 |
| 8 | 4 | `+0 -2 +4 -5` | 23578 | 1 |
| 8 | 5 | `-0 +2 -4 -5` | 34567 | 2 |
| 8 | 6 | `-0 -2 +4 +7` | 13458 | 1 |
| 8 | 7 | `+0 -4 -5 -8` | 04578 | 1 |
| 9 | 1 | `-0 -1 +2 -4` | 23678 | 1 |
| 9 | 2 | `+0 +1 -4 -5` | 02457 | 2 |
| 9 | 3 | `-0 +2 +3 -4` | 23467 | 1 |
| 9 | 4 | `+0 +2 +4 -5` | 02378 | 1 |
| 9 | 5 | `+0 -2 -4 -5` | 24578 | 2 |
| 9 | 6 | `-0 -2 -4 -5` | 45678 | 2 |
| 9 | 7 | `-0 +2 +4 +7` | 12348 | 1 |
| 9 | 8 | `-0 -2 +4 +7` | 13458 | 1 |
| 9 | 9 | `+0 +2 -4 -8` | 03478 | 1 |

## 3. Fourth-layer forms and isolated pivots

Each listed pivot must be used by L5, but every possible partner is excluded by its endpoint rows below.
Cases7 and9 already fail the matching arguments.

| Label | L4 | Pivot |
|---|---|---:|
| 1.1 | `01 24 37 58` | 7 |
| 1.2 | `01 24 38 57` | 4 |
| 1.3 | `01 25 37 48` | 2 |
| 1.4 | `01 25 38 47` | 8 |
| 1.5 | `01 27 38 45` | 8 |
| 1.6 | `01 28 37 45` | 7 |
| 2.1 | `01 24 38 57` | 4 |
| 3.1 | `01 27 34 58` | 7 |
| 3.2 | `01 27 35 48` | 7 |
| 3.3 | `01 27 38 45` | 7 |
| 3.4 | `01 28 34 57` | 8 |
| 3.5 | `01 28 35 47` | 8 |
| 3.6 | `01 28 37 45` | 8 |
| 3.7 | `02 17 34 58` | 7 |
| 3.8 | `02 17 35 48` | 7 |
| 3.9 | `02 17 38 45` | 7 |
| 3.10 | `02 18 34 57` | 8 |
| 3.11 | `02 18 35 47` | 8 |
| 3.12 | `02 18 37 45` | 8 |
| 3.13 | `07 12 34 58` | 7 |
| 3.14 | `07 12 35 48` | 7 |
| 3.15 | `07 12 38 45` | 7 |
| 3.16 | `08 12 34 57` | 8 |
| 3.17 | `08 12 35 47` | 8 |
| 3.18 | `08 12 37 45` | 8 |
| 4.1 | `02 15 37 48` | 8 |
| 5.1 | `27 34 58` | 3 |
| 5.2 | `28 34 57` | 3 |
| 5.3 | `12 47 58` | 3 |
| 5.4 | `12 48 57` | 3 |
| 5.5 | `12 36 47 58` | 3 |
| 5.6 | `12 36 48 57` | 3 |
| 5.7 | `01 24 37 58` | 3 |
| 5.8 | `01 24 38 57` | 3 |
| 5.9 | `01 25 37 48` | 3 |
| 5.10 | `01 25 38 47` | 3 |
| 5.11 | `01 27 34 58` | 3 |
| 5.12 | `01 27 35 48` | 3 |
| 5.13 | `01 27 38 45` | 3 |
| 5.14 | `01 28 34 57` | 3 |
| 5.15 | `01 28 35 47` | 3 |
| 5.16 | `01 28 37 45` | 3 |
| 6.1 | `01 23 45 78` | 3 |
| 6.2 | `01 24 35 78` | 5 |
| 6.3 | `01 25 34 78` | 4 |
| 6.4 | `02 18 35 47` | 2 |
| 8.1 | `02 18 37 45` | 7 |

## 4. Fifteen concrete inputs

Each row is a permutation of ranks0 through8 on the original wires. Only these inputs need evaluation.

| Input | Ranks on wires0,...,8 |
|---|---|
| A | `456701823` |
| B | `012834567` |
| C | `234567801` |
| D | `567801234` |
| E | `051267834` |
| F | `456701283` |
| G | `560123784` |
| H | `345678012` |
| I | `345607812` |
| J | `016723458` |
| K | `013456278` |
| L | `345601782` |
| M | `014526783` |
| N | `123456780` |
| O | `031456728` |

## 5. Endpoint exclusions

`idle` means the pivot value itself. Otherwise the output is the minimum or maximum of the pivot and proposed partner after L4.
Every displayed low/high gap is at least four. The rank-interval lemma supplies at least five attainable ranks on that L5 output; its last two layers can reach at most four final positions.
Grouped partner lists use identical witnesses.

### 1.1

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 7 | idle | idle | H:1 | K:7 |
| 7 | 0 | max | A:2 | K:7 |
| 7 | 1 | max | E:3 | K:7 |
| 7 | 2 | max | D:3 | K:7 |
| 7 | 3 | max | H:1 | K:7 |
| 7 | 4 | min | H:1 | C:5 |
| 7 | 5 | min | C:1 | B:6 |
| 7 | 6 | min | H:1 | I:6 |
| 7 | 8 | min | H:1 | K:7 |

### 1.2

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 4 | idle | idle | B:3 | D:7 |
| 4 | 0,2 | max | B:3 | D:7 |
| 4 | 1 | min | B:1 | D:5 |
| 4 | 3 | min | H:0 | M:4 |
| 4 | 5 | min | C:0 | J:5 |
| 4 | 6 | min | B:3 | H:7 |
| 4 | 7 | min | B:3 | D:7 |
| 4 | 8 | min | H:2 | F:6 |

### 1.3

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 2 | idle | idle | B:2 | D:7 |
| 2 | 0,1 | max | B:2 | D:7 |
| 2 | 3 | max | G:3 | D:7 |
| 2 | 4 | max | B:3 | D:7 |
| 2 | 5 | min | B:2 | D:7 |
| 2 | 6 | min | B:2 | A:6 |
| 2 | 7 | min | H:1 | I:5 |
| 2 | 8 | min | B:2 | F:6 |

### 1.4

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 8 | idle | idle | H:2 | F:8 |
| 8 | 0 | max | A:3 | F:8 |
| 8 | 1 | max | A:4 | F:8 |
| 8 | 2 | min | B:2 | F:6 |
| 8 | 3,4 | max | H:2 | F:8 |
| 8 | 5 | min | H:2 | B:7 |
| 8 | 6 | min | H:2 | G:7 |
| 8 | 7 | min | H:2 | K:7 |

### 1.5

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 8 | idle | idle | H:2 | F:8 |
| 8 | 0 | max | A:3 | F:8 |
| 8 | 1 | max | A:4 | F:8 |
| 8 | 2,3 | max | H:2 | F:8 |
| 8 | 4 | max | D:4 | F:8 |
| 8 | 5 | min | H:2 | B:7 |
| 8 | 6 | min | H:2 | G:7 |
| 8 | 7 | min | H:2 | K:7 |

### 1.6

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 7 | idle | idle | H:1 | K:7 |
| 7 | 0 | max | A:2 | K:7 |
| 7 | 1 | max | E:3 | K:7 |
| 7 | 2 | max | H:2 | K:7 |
| 7 | 3 | max | H:1 | K:7 |
| 7 | 4 | min | H:1 | C:5 |
| 7 | 5 | min | H:1 | B:6 |
| 7 | 6 | min | H:1 | I:6 |
| 7 | 8 | min | H:1 | K:7 |

### 2.1

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 4 | idle | idle | B:3 | D:7 |
| 4 | 0,2 | max | B:3 | D:7 |
| 4 | 1 | min | B:1 | D:5 |
| 4 | 3 | min | C:0 | J:5 |
| 4 | 5 | min | H:0 | O:4 |
| 4 | 6 | min | B:3 | H:7 |
| 4 | 7 | min | B:3 | D:7 |
| 4 | 8 | min | H:2 | C:6 |

### 3.1

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 7 | idle | idle | H:1 | K:7 |
| 7 | 0 | max | A:2 | K:7 |
| 7 | 1 | max | E:3 | K:7 |
| 7 | 2 | max | H:1 | K:7 |
| 7 | 3 | max | D:3 | K:7 |
| 7 | 4 | min | H:1 | B:6 |
| 7 | 5 | max | H:2 | K:7 |
| 7 | 6 | min | H:1 | K:6 |
| 7 | 8 | min | H:1 | K:7 |

### 3.2

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 7 | idle | idle | H:1 | K:7 |
| 7 | 0 | max | A:2 | K:7 |
| 7 | 1 | max | E:3 | K:7 |
| 7 | 2 | max | H:1 | K:7 |
| 7 | 3 | min | H:1 | I:5 |
| 7 | 4 | max | H:2 | K:7 |
| 7 | 5 | min | H:1 | B:6 |
| 7 | 6 | min | H:1 | K:6 |
| 7 | 8 | min | H:1 | K:7 |

### 3.3

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 7 | idle | idle | H:1 | K:7 |
| 7 | 0 | max | A:2 | K:7 |
| 7 | 1 | max | E:3 | K:7 |
| 7 | 2 | max | H:1 | K:7 |
| 7 | 3 | min | C:1 | B:6 |
| 7 | 4 | max | D:3 | K:7 |
| 7 | 5 | min | H:1 | I:5 |
| 7 | 6 | min | H:1 | K:6 |
| 7 | 8 | min | H:1 | K:7 |

### 3.4

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 8 | idle | idle | H:2 | F:8 |
| 8 | 0 | max | A:3 | F:8 |
| 8 | 1 | max | A:4 | F:8 |
| 8 | 2,5 | max | H:2 | F:8 |
| 8 | 3 | max | D:4 | F:8 |
| 8 | 4 | min | H:2 | B:7 |
| 8 | 6 | min | H:2 | G:7 |
| 8 | 7 | min | H:2 | K:7 |

### 3.5

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 8 | idle | idle | H:2 | F:8 |
| 8 | 0 | max | A:3 | F:8 |
| 8 | 1 | max | A:4 | F:8 |
| 8 | 2,4 | max | H:2 | F:8 |
| 8 | 3 | min | G:2 | F:6 |
| 8 | 5 | min | H:2 | B:7 |
| 8 | 6 | min | H:2 | G:7 |
| 8 | 7 | min | H:2 | K:7 |

### 3.6

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 8 | idle | idle | H:2 | F:8 |
| 8 | 0 | max | A:3 | F:8 |
| 8 | 1 | max | A:4 | F:8 |
| 8 | 2 | max | H:2 | F:8 |
| 8 | 3 | min | C:0 | B:6 |
| 8 | 4 | max | D:4 | F:8 |
| 8 | 5 | min | H:2 | F:6 |
| 8 | 6 | min | H:2 | G:7 |
| 8 | 7 | min | H:2 | B:7 |

### 3.7

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 7 | idle | idle | I:1 | K:7 |
| 7 | 0 | max | A:2 | K:7 |
| 7 | 1 | max | I:1 | K:7 |
| 7 | 2 | max | E:3 | K:7 |
| 7 | 3 | max | D:3 | K:7 |
| 7 | 4 | min | I:1 | B:6 |
| 7 | 5 | max | I:2 | K:7 |
| 7 | 6 | min | I:1 | K:6 |
| 7 | 8 | min | I:1 | K:7 |

### 3.8

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 7 | idle | idle | I:1 | K:7 |
| 7 | 0 | max | A:2 | K:7 |
| 7 | 1 | max | I:1 | K:7 |
| 7 | 2 | max | E:3 | K:7 |
| 7 | 3 | min | I:1 | J:5 |
| 7 | 4 | max | I:2 | K:7 |
| 7 | 5 | min | I:1 | B:6 |
| 7 | 6 | min | I:1 | K:6 |
| 7 | 8 | min | I:1 | K:7 |

### 3.9

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 7 | idle | idle | I:1 | K:7 |
| 7 | 0 | max | A:2 | K:7 |
| 7 | 1 | max | I:1 | K:7 |
| 7 | 2 | max | E:3 | K:7 |
| 7 | 3 | min | C:1 | B:6 |
| 7 | 4 | max | D:3 | K:7 |
| 7 | 5 | min | I:1 | J:5 |
| 7 | 6 | min | I:1 | K:6 |
| 7 | 8 | min | I:1 | K:7 |

### 3.10

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 8 | idle | idle | I:2 | F:8 |
| 8 | 0 | max | A:3 | F:8 |
| 8 | 1,5 | max | I:2 | F:8 |
| 8 | 2 | max | A:4 | F:8 |
| 8 | 3 | max | D:4 | F:8 |
| 8 | 4 | min | I:2 | B:7 |
| 8 | 6 | min | I:2 | G:7 |
| 8 | 7 | min | I:2 | K:7 |

### 3.11

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 8 | idle | idle | I:2 | F:8 |
| 8 | 0 | max | A:3 | F:8 |
| 8 | 1,4 | max | I:2 | F:8 |
| 8 | 2 | max | A:4 | F:8 |
| 8 | 3 | min | G:2 | F:6 |
| 8 | 5 | min | I:2 | B:7 |
| 8 | 6 | min | I:2 | G:7 |
| 8 | 7 | min | I:2 | K:7 |

### 3.12

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 8 | idle | idle | I:2 | F:8 |
| 8 | 0 | max | A:3 | F:8 |
| 8 | 1 | max | I:2 | F:8 |
| 8 | 2 | max | A:4 | F:8 |
| 8 | 3 | min | C:0 | B:6 |
| 8 | 4 | max | D:4 | F:8 |
| 8 | 5 | min | I:2 | F:6 |
| 8 | 6 | min | I:2 | G:7 |
| 8 | 7 | min | I:2 | B:7 |

### 3.13

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 7 | idle | idle | N:1 | K:7 |
| 7 | 0 | max | N:1 | K:7 |
| 7 | 1 | max | N:2 | K:7 |
| 7 | 2 | max | E:3 | K:7 |
| 7 | 3 | max | M:3 | K:7 |
| 7 | 4 | min | N:1 | B:6 |
| 7 | 5 | max | C:2 | K:7 |
| 7 | 6 | min | N:1 | K:6 |
| 7 | 8 | min | N:1 | K:7 |

### 3.14

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 7 | idle | idle | N:1 | K:7 |
| 7 | 0 | max | N:1 | K:7 |
| 7 | 1 | max | N:2 | K:7 |
| 7 | 2 | max | E:3 | K:7 |
| 7 | 3 | min | N:1 | D:5 |
| 7 | 4 | max | C:2 | K:7 |
| 7 | 5 | min | N:1 | B:6 |
| 7 | 6 | min | N:1 | K:6 |
| 7 | 8 | min | N:1 | K:7 |

### 3.15

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 7 | idle | idle | N:1 | K:7 |
| 7 | 0 | max | N:1 | K:7 |
| 7 | 1 | max | N:2 | K:7 |
| 7 | 2 | max | E:3 | K:7 |
| 7 | 3 | min | C:1 | B:6 |
| 7 | 4 | max | M:3 | K:7 |
| 7 | 5 | min | N:1 | D:5 |
| 7 | 6 | min | N:1 | K:6 |
| 7 | 8 | min | N:1 | K:7 |

### 3.16

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 8 | idle | idle | C:2 | F:8 |
| 8 | 0,5 | max | C:2 | F:8 |
| 8 | 1 | max | C:3 | F:8 |
| 8 | 2 | max | A:4 | F:8 |
| 8 | 3 | max | I:4 | F:8 |
| 8 | 4 | min | C:2 | B:7 |
| 8 | 6 | min | C:2 | G:7 |
| 8 | 7 | min | C:2 | K:7 |

### 3.17

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 8 | idle | idle | C:2 | F:8 |
| 8 | 0,4 | max | C:2 | F:8 |
| 8 | 1 | max | C:3 | F:8 |
| 8 | 2 | max | A:4 | F:8 |
| 8 | 3 | min | C:2 | F:6 |
| 8 | 5 | min | C:2 | B:7 |
| 8 | 6 | min | C:2 | G:7 |
| 8 | 7 | min | C:2 | K:7 |

### 3.18

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 8 | idle | idle | C:2 | F:8 |
| 8 | 0 | max | C:2 | F:8 |
| 8 | 1 | max | C:3 | F:8 |
| 8 | 2 | max | A:4 | F:8 |
| 8 | 3 | min | C:0 | B:6 |
| 8 | 4 | max | I:4 | F:8 |
| 8 | 5 | min | C:2 | F:6 |
| 8 | 6 | min | C:2 | G:7 |
| 8 | 7 | min | C:2 | B:7 |

### 4.1

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 8 | idle | idle | F:3 | J:8 |
| 8 | 0 | max | D:4 | J:8 |
| 8 | 1,4 | max | F:3 | J:8 |
| 8 | 2 | min | E:1 | G:5 |
| 8 | 3 | min | G:2 | B:6 |
| 8 | 5 | min | A:1 | O:6 |
| 8 | 6 | min | F:3 | C:7 |
| 8 | 7 | min | F:3 | B:7 |

### 5.1

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 3 | idle | idle | D:2 | H:6 |
| 3 | 0 | min | B:0 | A:4 |
| 3 | 1,5 | max | D:2 | H:6 |
| 3 | 2 | max | E:2 | H:6 |
| 3 | 4,6 | min | D:2 | H:6 |
| 3 | 7 | max | E:3 | D:7 |
| 3 | 8 | max | D:4 | F:8 |

### 5.2

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 3 | idle | idle | D:2 | H:6 |
| 3 | 0 | min | B:0 | A:4 |
| 3 | 1,5 | max | D:2 | H:6 |
| 3 | 2 | max | E:2 | F:6 |
| 3 | 4,6 | min | D:2 | H:6 |
| 3 | 7 | max | D:3 | C:7 |
| 3 | 8 | max | E:4 | F:8 |

### 5.3

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 3 | idle | idle | E:2 | B:8 |
| 3 | 0,1 | max | E:2 | B:8 |
| 3 | 2 | min | B:2 | D:7 |
| 3 | 4 | max | E:3 | B:8 |
| 3 | 5 | min | A:1 | M:5 |
| 3 | 6 | min | E:2 | A:7 |
| 3 | 7 | min | E:2 | B:6 |
| 3 | 8 | min | E:2 | B:7 |

### 5.4

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 3 | idle | idle | E:2 | B:8 |
| 3 | 0,1 | max | E:2 | B:8 |
| 3 | 2 | min | B:2 | D:7 |
| 3 | 4 | min | C:1 | G:5 |
| 3 | 5 | max | E:3 | B:8 |
| 3 | 6 | min | E:2 | A:7 |
| 3 | 7 | min | A:2 | B:6 |
| 3 | 8 | min | E:2 | B:7 |

### 5.5

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 3 | idle | idle | E:2 | A:7 |
| 3 | 0 | min | B:0 | D:5 |
| 3 | 1 | max | E:2 | A:7 |
| 3 | 2 | min | B:2 | A:6 |
| 3 | 4 | min | C:0 | G:4 |
| 3 | 5 | min | A:1 | M:5 |
| 3 | 6 | min | E:2 | A:7 |
| 3 | 7 | min | E:2 | H:6 |
| 3 | 8 | min | E:2 | I:6 |

### 5.6

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 3 | idle | idle | E:2 | A:7 |
| 3 | 0 | min | B:0 | D:5 |
| 3 | 1 | max | E:2 | A:7 |
| 3 | 2 | min | B:2 | A:6 |
| 3 | 4 | min | C:1 | G:5 |
| 3 | 5 | min | C:0 | B:4 |
| 3 | 6 | min | E:2 | A:7 |
| 3 | 7 | min | A:2 | I:6 |
| 3 | 8 | min | E:2 | H:6 |

### 5.7

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 3 | idle | idle | C:0 | B:6 |
| 3 | 0 | max | H:1 | B:6 |
| 3 | 1 | max | N:2 | B:6 |
| 3 | 2 | max | E:2 | B:6 |
| 3 | 4 | min | C:0 | J:5 |
| 3 | 5 | max | C:1 | B:6 |
| 3 | 6 | min | C:0 | B:5 |
| 3 | 7,8 | min | C:0 | B:6 |

### 5.8

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 3 | idle | idle | C:1 | B:7 |
| 3 | 0 | max | C:2 | B:7 |
| 3 | 1 | max | C:3 | B:7 |
| 3 | 2 | max | E:2 | B:7 |
| 3 | 4 | min | C:1 | F:6 |
| 3 | 5 | max | C:1 | B:7 |
| 3 | 6 | min | C:1 | L:6 |
| 3 | 7 | min | C:1 | B:6 |
| 3 | 8 | min | C:1 | B:7 |

### 5.9

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 3 | idle | idle | C:0 | B:6 |
| 3 | 0 | max | H:1 | B:6 |
| 3 | 1 | max | N:2 | B:6 |
| 3 | 2 | max | A:2 | B:6 |
| 3 | 4 | max | C:1 | B:6 |
| 3 | 5 | min | C:0 | J:5 |
| 3 | 6 | min | C:0 | B:5 |
| 3 | 7,8 | min | C:0 | B:6 |

### 5.10

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 3 | idle | idle | C:1 | B:7 |
| 3 | 0 | max | C:2 | B:7 |
| 3 | 1 | max | C:3 | B:7 |
| 3 | 2 | max | E:2 | B:7 |
| 3 | 4 | max | C:1 | B:7 |
| 3 | 5 | min | C:1 | F:6 |
| 3 | 6 | min | C:1 | L:6 |
| 3 | 7 | min | C:1 | B:6 |
| 3 | 8 | min | C:1 | B:7 |

### 5.11

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 3 | idle | idle | D:2 | H:6 |
| 3 | 0,5 | max | D:2 | H:6 |
| 3 | 1 | max | J:2 | H:6 |
| 3 | 2 | max | E:2 | H:6 |
| 3 | 4,6 | min | D:2 | H:6 |
| 3 | 7 | max | E:3 | D:7 |
| 3 | 8 | max | D:4 | F:8 |

### 5.12

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 3 | idle | idle | A:1 | I:6 |
| 3 | 0 | max | A:1 | I:6 |
| 3 | 1 | max | K:2 | I:6 |
| 3 | 2 | max | A:2 | I:6 |
| 3 | 4 | max | D:2 | G:6 |
| 3 | 5,6 | min | A:1 | I:6 |
| 3 | 7 | min | A:1 | I:5 |
| 3 | 8 | min | A:1 | C:5 |

### 5.13

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 3 | idle | idle | C:1 | B:7 |
| 3 | 0 | max | C:2 | B:7 |
| 3 | 1 | max | C:3 | B:7 |
| 3 | 2 | max | C:1 | B:7 |
| 3 | 4 | max | A:3 | B:7 |
| 3 | 5 | min | C:1 | G:5 |
| 3 | 6 | min | C:1 | L:6 |
| 3 | 7 | min | C:1 | B:6 |
| 3 | 8 | min | C:1 | B:7 |

### 5.14

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 3 | idle | idle | D:2 | H:6 |
| 3 | 0,5 | max | D:2 | H:6 |
| 3 | 1 | max | J:2 | H:6 |
| 3 | 2 | max | E:2 | F:6 |
| 3 | 4,6 | min | D:2 | H:6 |
| 3 | 7 | max | D:3 | C:7 |
| 3 | 8 | max | E:4 | F:8 |

### 5.15

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 3 | idle | idle | A:1 | I:6 |
| 3 | 0 | max | A:1 | I:6 |
| 3 | 1 | max | K:2 | I:6 |
| 3 | 2 | max | E:2 | F:6 |
| 3 | 4 | max | A:2 | I:6 |
| 3 | 5,6 | min | A:1 | I:6 |
| 3 | 7 | min | A:1 | C:5 |
| 3 | 8 | min | A:1 | I:5 |

### 5.16

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 3 | idle | idle | C:0 | B:6 |
| 3 | 0 | max | H:1 | B:6 |
| 3 | 1 | max | N:2 | B:6 |
| 3 | 2 | min | C:0 | J:5 |
| 3 | 4 | max | A:2 | B:6 |
| 3 | 5 | min | C:0 | B:4 |
| 3 | 6 | min | C:0 | B:5 |
| 3 | 7,8 | min | C:0 | B:6 |

### 6.1

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 3 | idle | idle | C:1 | B:7 |
| 3 | 0 | max | C:2 | B:7 |
| 3 | 1 | max | C:3 | B:7 |
| 3 | 2 | max | C:1 | B:7 |
| 3 | 4 | max | A:3 | B:7 |
| 3 | 5 | min | C:1 | G:5 |
| 3 | 6 | min | C:1 | B:5 |
| 3 | 7 | min | C:1 | B:6 |
| 3 | 8 | min | C:1 | B:7 |

### 6.2

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 5 | idle | idle | L:2 | B:7 |
| 5 | 0,3 | max | L:2 | B:7 |
| 5 | 1 | min | B:1 | E:5 |
| 5 | 2 | max | A:3 | B:7 |
| 5 | 4 | min | L:2 | C:6 |
| 5 | 6 | min | L:2 | C:7 |
| 5 | 7 | min | L:2 | B:6 |
| 5 | 8 | min | L:2 | B:7 |

### 6.3

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 4 | idle | idle | F:3 | B:7 |
| 4 | 0,2 | max | F:3 | B:7 |
| 4 | 1 | min | B:1 | E:5 |
| 4 | 3 | min | N:0 | K:4 |
| 4 | 5 | min | A:2 | C:6 |
| 4 | 6 | min | F:3 | H:7 |
| 4 | 7 | min | O:2 | B:6 |
| 4 | 8 | min | F:3 | B:7 |

### 6.4

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 2 | idle | idle | E:1 | F:6 |
| 2 | 0 | max | E:1 | F:6 |
| 2 | 1 | max | B:2 | F:6 |
| 2 | 3 | max | C:2 | F:6 |
| 2 | 4 | min | E:1 | G:5 |
| 2 | 5 | min | E:1 | J:5 |
| 2 | 6 | min | E:1 | D:5 |
| 2 | 7,8 | min | E:1 | F:6 |

### 8.1

| Pivot | Excluded partner(s) | Output | Low witness | High witness |
|---:|---|---|---|---|
| 7 | idle | idle | I:2 | F:8 |
| 7 | 0 | max | A:3 | F:8 |
| 7 | 1 | max | I:2 | F:8 |
| 7 | 2 | max | A:4 | F:8 |
| 7 | 3 | min | N:0 | B:6 |
| 7 | 4 | max | D:4 | F:8 |
| 7 | 5 | min | I:2 | F:6 |
| 7 | 6 | min | I:2 | G:7 |
| 7 | 8 | min | I:2 | B:7 |

The [solver-free checker](verify/h9_feedback_round5_proof.py) reads back the printed premises and checks every rank exclusion. Its [audit](results/h9-feedback-round5-proof.json) records counts and hashes.
