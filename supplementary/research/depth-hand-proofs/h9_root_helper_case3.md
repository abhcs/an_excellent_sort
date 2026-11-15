# H9 contact case3: a seven-row matching contradiction

This proves only the contact-system contradiction requested for fourth
layer `N=18 24 36 57`. The preceding reduction that produces these contacts
is a separate premise. Write `uv` for the unordered pair `{u,v}`.

Let `P` be any matching on wires0 through8 that avoids the four edges of
`N`. For each row below, `P` must have an edge contained in `R` and incident
with at least one endpoint of the sink pair `e`. The row numbering agrees
with the third object of `results/h9-feedback-round2-contacts.json`.

| Row | R | e |
|---:|---|---|
| 1 | 01357 | 57 |
| 2 | 34578 | 57 |
| 3 | 13478 | 18 |
| 4 | 13457 | 14 |
| 5 | 01258 | 18 |
| 6 | 01378 | 18 |
| 7 | 34678 | 78 |
| 8 | 34678 | 36 |
| 9 | 23478 | 24 |
| 10 | 01347 | 01 |

**Partner reduction.** Since `18` is forbidden, row3 requires one of wires
1,8 to have its partner in `A={3,4,7}`. Row5 requires one to have its partner
in the disjoint set `B={0,2,5}`. Hence both wires1,8 are matched, one into
each set. If the chosen A-partner is4, row6 forces the B-partner to be0.
There are therefore only seven possible unordered choices `(a,b)` of an
A-partner and a B-partner, and two orientations of each.

In the following table, `r=>uv` means row r forces edge uv after the two
displayed initial edges are fixed. `r=empty` means no legal edge remains for
that row. The three named leaves are proved immediately below.

| (a,b) | P contains `1a,8b` | P contains `1b,8a` |
|---|---|---|
| (3,0) | row1 empty | row1 empty |
| (3,2) | Leaf A | row9=>47; row10 empty |
| (3,5) | row1=>07; row7 empty | row2=>47; row10 empty |
| (4,0) | Leaf B | row4 empty |
| (7,0) | row7 empty | row1=>35; row4 empty |
| (7,2) | row7 empty | row9=>34; row10 empty |
| (7,5) | row7 empty | Leaf C |

Each table entry follows just by deleting candidate edges incident with an
already matched vertex; it does not enumerate the remaining matchings.

* **Leaf A (`13,28`).** Rows7 and8 reduce to `47 or67` and `46 or67`.
  As `47` and `46` cannot coexist, edge67 is forced. Rows1 and2 then force
  `05` and `45`, which cannot coexist.
* **Leaf B (`14,08`).** Rows1,7,9 reduce respectively to `35 or37`,
  `37 or67`, and `23 or27`. The first two rows require the partner of3 to
  lie in `{5,7}` and the partner of7 to lie in `{3,6}`. Neither edge
  required by row9 is then available.
* **Leaf C (`15,78`).** Rows8,9,10 reduce respectively to `34 or46`,
  `23 or34`, and `03 or04`. The first two rows require the partner of4 to
  lie in `{3,6}` and the partner of3 to lie in `{2,4}`. Neither edge
  required by row10 is then available.

Every branch contradicts the matching property. No matching P satisfies
the ten contact requirements while avoiding N. This includes nonperfect
matchings; no filling argument is used. □

The local checker `verify/h9_root_helper_case3.py` verifies the seven-row
reduction, each forced/empty entry, and the exact small clause sets at the
three leaves. Its optional finite cross-check considers only the16,8,8
choices inside those leaves, not the2620 complete nine-wire matchings.
