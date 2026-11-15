# Local activity tables for partial D18 sixth layers

These finite witnesses support the [partial-layer theorem](d18_rank_partner_round7_partial.md).
Input indices refer to the unchanged bank of the source beam in [the original tables](rank-layer-round6-hand-tables.md).
For each family, keep its fixed sixth-layer gates. A proposed seventh-layer partner v may be idle in layer6 (`idle`) or have the sixth-layer mate listed. All unlisted sixth-layer gates are disjoint and cannot affect the values tested.
A width row evaluates min or max at the proposed seventh-layer edge and shows a rank gap at least8. Partner/mate groups combine identical witnesses.

## beam00 (bank beam00)

Fixed L6 gates: `[(1, 4), (5, 6), (12, 13)]`. Free wires: `[0, 2, 3, 7, 8, 9, 10, 11, 14, 15, 16, 17]`.

| Mandatory pivot | Low input:rank | High input:rank |
|---:|---|---|
| 12 | 0:5 | 1:15 |

| Pivot | Proposed L7 partner | L6 mate(s) of partner | Output | Low input:rank | High input:rank |
|---:|---:|---|---|---|---|
| 12 | 0 | idle,2,3,7,8,9,10,11,14,15,16,17 | max | 0:5 | 1:15 |
| 12 | 1 | 4 | max | 0:5 | 1:15 |
| 12 | 2 | idle,0,9,14,15,16,17 | min | 1:2 | 17:10 |
| 12 | 2 | 3,8 | max | 15:7 | 1:15 |
| 12 | 2 | 7,10 | max | 0:5 | 1:15 |
| 12 | 2 | 11 | max | 2:6 | 1:15 |
| 12 | 3 | idle,0,2,8,9,14,15,16,17 | max | 15:7 | 1:15 |
| 12 | 3 | 7,10 | max | 0:5 | 1:15 |
| 12 | 3 | 11 | max | 2:6 | 1:15 |
| 12 | 4 | 1 | max | 3:6 | 1:15 |
| 12 | 5 | 6 | max | 0:5 | 1:15 |
| 12 | 6 | 5 | max | 0:6 | 1:15 |
| 12 | 7 | idle,0,11,17 | min | 2:3 | 12:13 |
| 12 | 7 | 2,3 | min | 0:5 | 12:13 |
| 12 | 7 | 8,9,10,14,15,16 | max | 0:5 | 1:15 |
| 12 | 8 | idle,0,9,14,15,16,17 | min | 10:2 | 8:10 |
| 12 | 8 | 2,3 | max | 15:7 | 1:15 |
| 12 | 8 | 7 | min | 0:5 | 12:13 |
| 12 | 8 | 10 | max | 0:5 | 1:15 |
| 12 | 8 | 11 | max | 2:6 | 1:15 |
| 12 | 9 | idle,0,2,3,7,8,16,17 | min | 0:5 | 1:13 |
| 12 | 9 | 10 | max | 0:5 | 1:15 |
| 12 | 9 | 11 | max | 2:6 | 1:15 |
| 12 | 9 | 14,15 | max | 15:7 | 1:15 |
| 12 | 10 | idle,0,11,17 | min | 0:3 | 13:13 |
| 12 | 10 | 2,3,8 | min | 0:5 | 13:13 |
| 12 | 10 | 7,14,15,16 | max | 0:5 | 1:15 |
| 12 | 10 | 9 | min | 0:5 | 1:13 |
| 12 | 11 | idle,0,7,10 | max | 2:6 | 7:16 |
| 12 | 11 | 2,3,8,9,17 | min | 0:5 | 14:14 |
| 12 | 11 | 14,15,16 | max | 2:6 | 1:15 |
| 12 | 13 | 12 | min | 0:5 | 1:15 |
| 12 | 14 | idle,0,2,3,7,8,10,16,17 | min | 0:5 | 11:13 |
| 12 | 14 | 9 | min | 0:5 | 1:13 |
| 12 | 14 | 11 | min | 0:5 | 14:14 |
| 12 | 14 | 15 | max | 15:7 | 1:15 |
| 12 | 15 | idle,0,2,3,8,16,17 | min | 0:5 | 16:13 |
| 12 | 15 | 7 | min | 0:5 | 12:13 |
| 12 | 15 | 9 | min | 0:5 | 1:13 |
| 12 | 15 | 10 | min | 0:5 | 13:13 |
| 12 | 15 | 11 | min | 0:5 | 14:14 |
| 12 | 15 | 14 | min | 0:5 | 11:13 |
| 12 | 16 | idle,0,2,3,7,8,9,10,11,14,15,17 | min | 0:5 | 1:14 |
| 12 | 17 | idle,0,2,3,7,8,9,10,11,14,15,16 | min | 0:5 | 1:15 |

After all local activities are considered, only these supports remain:

| Pivot | Remaining (L7 partner,L6 mate) choices |
|---:|---|
| 12 | none |

## beam16 (bank beam16)

Fixed L6 gates: `[(4, 6), (5, 15), (7, 14), (16, 17)]`. Free wires: `[0, 1, 2, 3, 8, 9, 10, 11, 12, 13]`.

| Mandatory pivot | Low input:rank | High input:rank |
|---:|---|---|
| 6 | 0:4 | 1:14 |

| Pivot | Proposed L7 partner | L6 mate(s) of partner | Output | Low input:rank | High input:rank |
|---:|---:|---|---|---|---|
| 6 | 0 | idle,1,2,3,8,9,10,11,12,13 | max | 0:4 | 1:14 |
| 6 | 1 | idle,0,2,3,8,9,10,11,12,13 | max | 0:4 | 1:14 |
| 6 | 2 | idle,0,1,3,8,9,10,11,12,13 | max | 0:4 | 1:14 |
| 6 | 3 | idle,0,1,2 | min | 1:3 | 16:12 |
| 6 | 3 | 8,9,11,12,13 | max | 4:5 | 1:14 |
| 6 | 3 | 10 | max | 0:5 | 1:14 |
| 6 | 4 | 6 | max | 0:4 | 1:14 |
| 6 | 5 | 15 | min | 7:1 | 8:9 |
| 6 | 7 | 14 | min | 0:4 | 1:12 |
| 6 | 8 | idle,9,11,12 | min | 12:2 | 11:12 |
| 6 | 8 | 0,1,2,3 | min | 0:4 | 11:12 |
| 6 | 8 | 10 | max | 0:5 | 1:14 |
| 6 | 8 | 13 | max | 0:6 | 1:14 |
| 6 | 9 | idle,8,11,12 | min | 12:3 | 11:12 |
| 6 | 9 | 0,1,2,3 | min | 0:4 | 11:12 |
| 6 | 9 | 10 | max | 0:5 | 1:14 |
| 6 | 9 | 13 | max | 0:6 | 1:14 |
| 6 | 10 | idle,0,1,2,11,12,13 | max | 0:5 | 1:14 |
| 6 | 10 | 3 | min | 0:4 | 16:12 |
| 6 | 10 | 8,9 | min | 0:4 | 11:12 |
| 6 | 11 | idle,0,1,2,3,8,9,10 | min | 0:4 | 14:13 |
| 6 | 11 | 12 | min | 0:4 | 11:12 |
| 6 | 11 | 13 | max | 0:6 | 1:14 |
| 6 | 12 | idle,0,1,2,3,8,9,10 | min | 0:4 | 11:12 |
| 6 | 12 | 11 | min | 0:4 | 14:13 |
| 6 | 12 | 13 | max | 0:6 | 1:14 |
| 6 | 13 | idle,0,1,2,10 | max | 0:6 | 1:14 |
| 6 | 13 | 3 | min | 0:4 | 16:12 |
| 6 | 13 | 8,9,12 | min | 0:4 | 11:12 |
| 6 | 13 | 11 | min | 0:4 | 14:13 |
| 6 | 14 | 7 | min | 0:4 | 1:14 |
| 6 | 15 | 5 | min | 0:4 | 1:13 |
| 6 | 16 | 17 | min | 0:4 | 1:14 |
| 6 | 17 | 16 | min | 0:4 | 1:14 |

After all local activities are considered, only these supports remain:

| Pivot | Remaining (L7 partner,L6 mate) choices |
|---:|---|
| 6 | none |

## beam32a (bank beam32)

Fixed L6 gates: `[(0, 1), (2, 8), (4, 5), (6, 9), (10, 14), (12, 13)]`. Free wires: `[3, 7, 11, 15, 16, 17]`.

| Mandatory pivot | Low input:rank | High input:rank |
|---:|---|---|
| 5 | 0:1 | 1:11 |
| 12 | 13:6 | 1:16 |

| Pivot | Proposed L7 partner | L6 mate(s) of partner | Output | Low input:rank | High input:rank |
|---:|---:|---|---|---|---|
| 5 | 0 | 1 | max | 0:2 | 1:11 |
| 5 | 1 | 0 | max | 0:3 | 1:11 |
| 5 | 3 | idle,15,16,17 | max | 19:3 | 1:11 |
| 5 | 3 | 7 | max | 4:3 | 1:11 |
| 5 | 3 | 11 | max | 10:3 | 1:11 |
| 5 | 4 | 5 | max | 0:1 | 1:11 |
| 5 | 6 | 9 | max | 4:2 | 1:11 |
| 5 | 7 | idle,17 | max | 4:3 | 18:14 |
| 5 | 7 | 3,11 | min | 0:1 | 1:10 |
| 5 | 7 | 15 | max | 4:3 | 17:12 |
| 5 | 7 | 16 | max | 4:3 | 17:13 |
| 5 | 9 | 6 | min | 0:1 | 1:11 |
| 5 | 10 | 14 | max | 22:3 | 6:12 |
| 5 | 11 | idle | max | 10:3 | 1:15 |
| 5 | 11 | 3,7 | min | 0:1 | 1:11 |
| 5 | 11 | 15 | max | 10:3 | 11:12 |
| 5 | 11 | 16 | max | 10:3 | 9:14 |
| 5 | 11 | 17 | max | 10:3 | 11:14 |
| 5 | 12 | 13 | min | 0:1 | 1:11 |
| 5 | 13 | 12 | min | 0:1 | 1:11 |
| 5 | 14 | 10 | min | 0:1 | 1:11 |
| 5 | 15 | idle,3,16,17 | max | 3:7 | 0:15 |
| 5 | 15 | 7 | min | 0:1 | 1:10 |
| 5 | 15 | 11 | min | 0:1 | 1:11 |
| 5 | 16 | idle,3,15,17 | min | 0:1 | 12:10 |
| 5 | 16 | 7 | min | 0:1 | 1:10 |
| 5 | 16 | 11 | min | 0:1 | 1:11 |
| 5 | 17 | idle,3,7,11,15,16 | min | 0:1 | 1:11 |
| 12 | 0 | 1 | max | 13:6 | 1:16 |
| 12 | 1 | 0 | max | 15:7 | 1:16 |
| 12 | 3 | idle,15,16,17 | min | 16:2 | 17:10 |
| 12 | 3 | 7,11 | max | 13:6 | 1:16 |
| 12 | 4 | 5 | max | 13:6 | 1:16 |
| 12 | 5 | 4 | min | 0:1 | 1:11 |
| 12 | 6 | 9 | max | 13:6 | 1:16 |
| 12 | 7 | idle,17 | min | 4:3 | 18:14 |
| 12 | 7 | 3 | min | 19:5 | 18:14 |
| 12 | 7 | 11,15 | max | 13:6 | 1:16 |
| 12 | 7 | 16 | min | 4:3 | 17:13 |
| 12 | 9 | 6 | min | 13:6 | 21:14 |
| 12 | 10 | 14 | min | 22:3 | 6:12 |
| 12 | 11 | idle | min | 10:3 | 1:15 |
| 12 | 11 | 3 | min | 29:5 | 1:15 |
| 12 | 11 | 7 | min | 13:5 | 1:15 |
| 12 | 11 | 15 | max | 13:6 | 1:16 |
| 12 | 11 | 16 | min | 10:3 | 9:14 |
| 12 | 11 | 17 | min | 10:3 | 11:14 |
| 12 | 13 | 12 | min | 13:6 | 1:16 |
| 12 | 14 | 10 | min | 13:6 | 1:14 |
| 12 | 15 | idle,3,16,17 | min | 6:5 | 2:13 |
| 12 | 15 | 7 | min | 13:6 | 18:14 |
| 12 | 15 | 11 | min | 13:6 | 1:15 |
| 12 | 16 | idle,3,7,15 | min | 13:6 | 23:15 |
| 12 | 16 | 11 | min | 13:6 | 1:15 |
| 12 | 16 | 17 | min | 13:6 | 3:14 |
| 12 | 17 | idle,3,7,15,16 | min | 13:6 | 14:15 |
| 12 | 17 | 11 | min | 13:6 | 1:15 |

Both outputs in each following row have witnessed span7. Their full cones would have the stated odd intersection.

| Pivot | L7 partner | L6 mate | Minimum low/high input:rank | Maximum low/high input:rank | Odd overlap |
|---:|---:|---:|---|---|---:|
| 12 | 2 | 8 | 1:2 / 29:9 | 13:9 / 1:16 | 1 |

After all local activities are considered, only these supports remain:

| Pivot | Remaining (L7 partner,L6 mate) choices |
|---:|---|
| 5 | (2,8); (8,2) |
| 12 | (8,2) |

The two forced L7 edges have incompatible full cones:

| L7 edge | Output | Low input:rank | High input:rank |
|---|---|---|---|
| (8, 12) | min | 28:3 | 0:10 |
| (2, 5) | max | 0:4 | 1:11 |

## beam32b (bank beam32)

Fixed L6 gates: `[(2, 8), (3, 7), (4, 5), (6, 9), (10, 14), (12, 13)]`. Free wires: `[0, 1, 11, 15, 16, 17]`.

| Mandatory pivot | Low input:rank | High input:rank |
|---:|---|---|
| 5 | 0:1 | 1:11 |
| 12 | 13:6 | 1:16 |

| Pivot | Proposed L7 partner | L6 mate(s) of partner | Output | Low input:rank | High input:rank |
|---:|---:|---|---|---|---|
| 5 | 0 | idle,1,11,15,16,17 | max | 0:2 | 1:11 |
| 5 | 1 | idle,11,15,16,17 | max | 19:2 | 1:11 |
| 5 | 1 | 0 | max | 0:3 | 1:11 |
| 5 | 3 | 7 | max | 4:3 | 1:11 |
| 5 | 4 | 5 | max | 0:1 | 1:11 |
| 5 | 6 | 9 | max | 4:2 | 1:11 |
| 5 | 7 | 3 | min | 0:1 | 1:10 |
| 5 | 9 | 6 | min | 0:1 | 1:11 |
| 5 | 10 | 14 | max | 22:3 | 6:12 |
| 5 | 11 | idle,0 | max | 10:3 | 1:15 |
| 5 | 11 | 1 | min | 0:1 | 1:11 |
| 5 | 11 | 15 | max | 10:3 | 11:12 |
| 5 | 11 | 16 | max | 10:3 | 9:14 |
| 5 | 11 | 17 | max | 10:3 | 11:14 |
| 5 | 12 | 13 | min | 0:1 | 1:11 |
| 5 | 13 | 12 | min | 0:1 | 1:11 |
| 5 | 14 | 10 | min | 0:1 | 1:11 |
| 5 | 15 | idle,0,1,16,17 | max | 3:7 | 0:15 |
| 5 | 15 | 11 | min | 0:1 | 1:11 |
| 5 | 16 | idle,0,1,15,17 | min | 0:1 | 12:10 |
| 5 | 16 | 11 | min | 0:1 | 1:11 |
| 5 | 17 | idle,0,1,11,15,16 | min | 0:1 | 1:11 |
| 12 | 0 | idle,1,11,15,16,17 | max | 13:6 | 1:16 |
| 12 | 1 | idle,0,15,16,17 | max | 15:7 | 1:16 |
| 12 | 1 | 11 | max | 13:6 | 1:16 |
| 12 | 3 | 7 | max | 13:6 | 1:16 |
| 12 | 4 | 5 | max | 13:6 | 1:16 |
| 12 | 5 | 4 | min | 0:1 | 1:11 |
| 12 | 6 | 9 | max | 13:6 | 1:16 |
| 12 | 7 | 3 | min | 19:5 | 18:14 |
| 12 | 9 | 6 | min | 13:6 | 21:14 |
| 12 | 10 | 14 | min | 22:3 | 6:12 |
| 12 | 11 | idle,0 | min | 10:3 | 1:15 |
| 12 | 11 | 1 | min | 10:5 | 1:15 |
| 12 | 11 | 15 | max | 13:6 | 1:16 |
| 12 | 11 | 16 | min | 10:3 | 9:14 |
| 12 | 11 | 17 | min | 10:3 | 11:14 |
| 12 | 13 | 12 | min | 13:6 | 1:16 |
| 12 | 14 | 10 | min | 13:6 | 1:14 |
| 12 | 15 | idle,0,1,16,17 | min | 6:5 | 2:13 |
| 12 | 15 | 11 | min | 13:6 | 1:15 |
| 12 | 16 | idle,0,1,15 | min | 13:6 | 23:15 |
| 12 | 16 | 11 | min | 13:6 | 1:15 |
| 12 | 16 | 17 | min | 13:6 | 3:14 |
| 12 | 17 | idle,0,1,15,16 | min | 13:6 | 14:15 |
| 12 | 17 | 11 | min | 13:6 | 1:15 |

Both outputs in each following row have witnessed span7. Their full cones would have the stated odd intersection.

| Pivot | L7 partner | L6 mate | Minimum low/high input:rank | Maximum low/high input:rank | Odd overlap |
|---:|---:|---:|---|---|---:|
| 12 | 2 | 8 | 1:2 / 29:9 | 13:9 / 1:16 | 1 |

After all local activities are considered, only these supports remain:

| Pivot | Remaining (L7 partner,L6 mate) choices |
|---:|---|
| 5 | (2,8); (8,2) |
| 12 | (8,2) |

The two forced L7 edges have incompatible full cones:

| L7 edge | Output | Low input:rank | High input:rank |
|---|---|---|---|
| (8, 12) | min | 28:3 | 0:10 |
| (2, 5) | max | 0:4 | 1:11 |

The [independent checker](d18_rank_partner_round7_partial_check.py) checks every allowed local activity, every displayed witness, and the exact fixed-source hash. No sixth-layer matching is enumerated.
