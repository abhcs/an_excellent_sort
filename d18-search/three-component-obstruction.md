# At most two components before the final four layers

**Theorem (pure hand proof).** In any sorting network, fix
signed infinities on all but nine arbitrary real inputs. Four layers
before the end, the interaction graph of the nine logical real tracks
has **at most two connected components**.

This strengthens the earlier [pure hand component-size theorem](merge-component-obstruction.md).
It applies at every ambient width, including D13 at cut4 of a proposed
depth8 sorter and D18 at cut6 of a proposed depth10 sorter. It does not
require the prefix to sort its individual components.

## Seven merger shapes suffice

If there were at least three components, group them into three nonempty
blocks. Their sizes sum to nine, and, up to order, are one of

```
7+1+1, 6+2+1, 5+3+1, 5+2+2, 4+4+1, 4+3+2, 3+3+3.
```

Prune the sentinel comparisons, relabel the packed blocks consecutively,
and untangle the whole restricted sorter. Before the cut all comparisons
are internal to these blocks. The prefix therefore fixes every input
already sorted within each block. Its remaining four layers would have
to merge that entire three-block family.

All seven shapes have hand lower bounds of at least five merger layers:
[711](merger711-hand-reduction.md),
[621](d13_feedback_round4_merger621.md),
[432](../depth-hand-proofs/h9_feedback_round2_merge432.md),
[333](../depth-hand-proofs/h9_feedback_round3_merge333.md),
[441](d13_feedback_round3_merger441.md), and
[531 and522](d13_feedback_round4_mergers.md).
Thus every possible three-block grouping is excluded, proving the theorem
without a computational premise.

The711 proof reduces to two first-layer starts, excludes one by a rank
interval table, and excludes the other by forcing two exact forward cones
with an odd intersection. It also proves a general saturated-cone parity
lemma: merging `2^d-1` sorted values with a sorted pair requires at least
d+1 layers, at every width. The621 proof uses a four-input rank table.

Small SAT experiments suggested these last hand proofs; their saved
certificates are corroboration only. The bare SAT encoding has four arbitrary matching layers and ordinary
comparison semantics on every binary sorted-block input. It uses no
ending, adjacency, or redundancy normal forms. The zero-one principle
applies to this restricted family because thresholding preserves the
order inside each block. For711 there are32 binary inputs, and for621
there are42. Both solves exited normally in less than0.19 seconds,
including process overhead, under separate10-second limits. Each DRAT
certificate verifies independently under a20-second checker cap.

Certificates for531 and522 are also retained as corroboration of the
hand proofs. The [verification manifest](results/merger-partition-round4-verification.json)
binds all four CNFs and proofs, encoder/helper sources, and the checker
by SHA256. It distinguishes this small merger result from the unresolved
full D18 problem.

## Concrete D18 exclusions

The stronger condition rejects three of six previously saved six-layer
prefixes. One, the combined candidate, was already excluded by the
[earlier five-layer hand proof](commuting-prefix-hand-proof.md).
The two beam candidates below are additional six-layer exclusions.

Each row fixes the listed negative and positive sentinels, leaving the
other nine inputs arbitrary. Components are listed by physical positions
after layer6; they denote logical track groups, not sorted sublists.

| Saved prefix | Negative inputs | Positive inputs | Components after L6 |
|---|---|---|---|
| combined-prefix-probe18 |0,1,3,7|9,11,13,14,17|{7}, {8}, {3,4,6,9,10,11,12}|
| beam00 with saved L6 |0,1,2,6|9,11,15,16,17|{3}, {5,6,7,10,11,12}, {8,14}|
| beam16 with saved L6 |0,4,5,12|10,11,15,16,17|{3,4,5,6,7,8,9}, {12}, {14}|

The [sample record](results/merge-component18-round4-three.json) includes
the exact layer arrays. Across all710,828 normalized placements, these
three prefixes have respectively40,8,744,128 obstructions. The other
three sampled prefixes have none. The independent verifier checks512
binary functional runs for each displayed restriction and all32,42,32
sorted-component binary inputs respectively.

This does not close their five-layer prefixes. For each of beam00,16,32,
a different sixth matching satisfies the stronger component condition on
every normalized placement. These explicit [relaxation survivors](results/merge-component18-round4-next-layer.json)
are independently replayed; they are not sorting networks. No complete
two-layer D18 cover case is closed.

## D13 observations and verification

The same collector rejects83 of117 saved four-layer D13 witnesses, versus
34 under the earlier largest-component-at-most-four test. It also finds
two normalized obstructing restrictions for the replacement case116
witness from the previous round. The [collection record](results/merge-component13-round4-three.json)
is a screen of specific witnesses, not a refutation of all their possible
third and fourth layers. Every one of the83 rejection witnesses was
independently replayed on all512 binary assignments to its nine real inputs.

The [updated case116 synthesis](d13_feedback_round4_component_cegar.py)
found another survivor in0.33 seconds after25 guarded component cuts:
adding comparator37 to the previous fourth layer removes its two
remaining obstructions. The [independent replay](results/d13_feedback_round4-component-cegar-r0116-verification.json)
checks all11,440 signed nine-real placements, all the prior raw five- and
seven-real blind-profile placements, and all25 cut translations. Thus this
stronger condition still does not close whole case116.

The updated collector's `three` mode stops only when component count
falls below three, since later comparisons cannot increase that count.
An independent adjacency-graph implementation checks144 small prefix/mode
combinations against11,568 raw signed placements, with93,696 direct binary
trace replays. A known depth11 sorter on eighteen inputs passes the
stronger condition at cut7 and is also verified on all262,144 binary
inputs. The [control report](results/merge-component-round4-verification.json)
records these scopes and source hashes.

Run the [certificate and prefix verifier](merger_partition_round4_verify.py)
with Python including `python-sat`; it invokes no SAT solver itself.
It needs a C++ compiler and the `drat-trim` executable at the path stated
in that script. Historical result records retain their original source
hashes rather than silently claiming verification of later revisions.

## Related bounds and sharpness

The same hand component-count statement holds for three reals with two
layers remaining, and for five reals with three layers remaining. For
three, three components would leave an impossible two-layer sorter on
three inputs. For five, any three-component grouping has shape311 or221.
The former has the hand four-layer lower bound; a three-layer221 merger,
preceded by a layer sorting its two pairs, would sort five arbitrary
inputs in four layers, contradicting D(5)>=5.

The bound of two components for nine reals cannot be reduced to one.
Sorted blocks of five and four have this explicit four-layer merger:

```
L1 = 05 16 27 38
L2 = 45
L3 = 24 36 57
L4 = 12 34 56 78
```

It passes all30 binary sorted-block inputs; the
[construction record](results/merge-component-sharpness54.json) also
records its derivation from a sixteen-wire merger. Prepending independent
sorters on the two blocks yields a genuine sorter with exactly two
interaction components four layers before the end. This is a sharpness
control for the structural theorem, not a new optimal-depth construction.
