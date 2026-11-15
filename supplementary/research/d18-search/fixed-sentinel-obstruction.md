# A two-layer obstruction that survives adding sentinel wires

The obstructions from [the D(17) audit](d17_feedback_results.md)
have smaller forms on twelve and fourteen wires. **The twelve-wire
obstruction now has a complete hand proof.** Its first matching is
handled by the [small-matching argument](d17_hand_defects_twelve_cross.md),
the [four-gate and perfect cases](d17_feedback_twelve_structure.md),
and the [remaining five-gate case](d17_hand_defects_twelve_five.md).
The proof uses no SAT or exhaustive first-matching enumeration as a premise.
A hand pruning argument makes it valid at every larger width with fixed
auxiliary sentinels. The earlier checked SAT proofs and a three-second
finite proof remain as independent corroboration.
The subsequent [width theorem](d12_triangle_lemmas_width.md) also permits
arbitrarily many common real coordinates: for every number R>=7 of
reals, some restriction misses the maximum floor(R/2) real-real count in
both layers. Its seven/eight-real versions supply additional purely
hand-based targets for D(18).
This is a reusable structural obstruction; it does not by itself close
any D(18) complete-cover case.

## A smaller twelve-wire pattern

Write `R` for a real, `-` for negative infinity and `+` for positive
infinity. The twenty twelve-wire states are `RR A B`, with

```
A in { R--RR, RR-+R, RRR++, +R-RR }
B in { R-RRR, RRR-R, RRRR+, RR+RR, +RRRR }.
```

For any two arbitrary matching layers, one of these states has at most
three real-real gates in each layer, with types transported through the
first before counting the second. This pure coverage statement allows
repeated gates and empty layers. Its direct encoding has 1,816 variables
and 14,468 clauses; UNSAT took 2.11 seconds and independent DRAT checking
took 1.30 seconds. See the [state family](results/d17-feedback-twelve-states.json),
[audit](results/d17-feedback-twelve-audit.json), and
[certificate](results/d17-feedback-twelve-main/result/check/certificate.json).

The pattern comes from case 607 by removing its five common fixed
sentinels: negative infinities on wires 0, 3, 9 and 13, and positive
infinity on wire 14. Its retained original labels are
`1,2,4,5,6,7,8,10,11,12,15,16`.
The hand lifting proof below consequently applies at every width at
least twelve, using this smaller family.

### Extracting a small proof from the SAT result

For a fixed first matching M, retain the restrictions that do not already
have four real-real gates. After transporting their signs, record just
their three sentinel positions. The last counted matching N can safely
be completed to a perfect matching. It has four real-real gates precisely
when it pairs two sentinels, so it must hit each recorded triple.

[Four short hand obstructions](d12_triangle_lemmas.md) rule out such an N.
All four use the same inequality: give an edge weight equal to the number
of triples containing it. A matching's weight equals the number of triples
it hits. Nonnegative vertex prices bounding each edge weight then bound
the matching weight. The four patterns have total price 3 or 7/2, so no
matching can hit all four triples.

The [finite scanner](d12_triangle_scan.cpp) examines **all 140,152 partial
first matchings**, including empty and perfect ones. Every matching
produces four triples of one of these four types. There are 3,957 distinct
labelled cores. A separate verifier checks their prices, exact matching
optima, representative transports and explicit template isomorphisms.
The [combined audit](results/d12-triangle-proof-audit.json) binds the
sources, complete signed family, scan and independent verification.

```sh
python3 d18-search/d12_triangle_audit.py
```

This finite proof consists of an enumeration choosing four restrictions
and a hand inequality refuting each resulting pattern. Its universal
selection of a four-triple pattern is not itself claimed to be a hand
argument. A subsequent, separate proof avoids that enumeration entirely:
it classifies the first matching by size and closes every size, including
the final [five-gate branch](d17_hand_defects_twelve_five.md). Thus the
two-matching obstruction itself is now proved by hand, even though the
four-triple catalogue is still obtained by computation.

There is also an [exact hand criterion for arbitrary four-triple
families](d12_triangle_lemmas_complete.md). It is independent of this
twelve-wire enumeration and can be used to recognize other small
obstructions at larger widths.

## 1. The twenty states on fourteen wires

Write `R` for a real, `-` for negative infinity and `+` for positive
infinity. Concatenation below specifies physical wires in order.
Let F consist of the twenty words `RR A B`, where

```
A in { R--RR, RR-+R, RRR++, +R-RR }
B in { -RR--RR, -RRR-+R, -RRRR++, -R+R-RR, R++R-RR }.
```

Every state has nine reals. For a matching M, count a retained comparator
exactly when both of its incoming types are R. Propagate types by ordinary
min/max before counting the next matching.

**Finite obstruction.** For any two matching layers M,N on fourteen
wires, some state in F has at most three retained comparators in M and
at most three in N after transport through M.

Repeated comparators and empty layers are allowed. There are no ending
normal forms, no fixed prefix, no nonemptiness assumption and no symmetry
restriction on M or N. The proof is currently SAT-based:

* 2,150 variables and 19,412 clauses;
* UNSAT in 4.57 seconds;
* independent DRAT verification in 3.11 seconds.

The [states and label map](results/d17-feedback-fourteen-states.json),
[audit](results/d17-feedback-fourteen-audit.json), and
[certificate manifest](results/d17-feedback-fourteen-main/result/check/certificate.json)
bind the result to [the encoder](d17_feedback_fourteen.py).
The sixteen-state subfamily with original indices 4 through 19 admits a
directly replayed pair of matching layers, providing a positive control.

These states arise from D17 case 608 by deleting wires 0, 3 and 11, which
are negative infinity in all twenty restrictions. The retained original
wire labels are

```
1,2,4,5,6,7,8,9,10,12,13,14,15,16.
```

## 2. Hand lemma: common fixed sentinels can be removed

Consider any family of signed states and two matching layers. Suppose
some wires have the same fixed sentinel value in every state in the
family. They can be removed, yielding two matching layers on the other
wires with exactly the same pair of retained-comparator counts for each
state.

**Proof.** Track the fixed sentinels separately from the other variables.
Comparing a fixed negative infinity with a variable sends the fixed
sentinel to the lower output and the variable to the upper output.
Comparing a fixed positive infinity with a variable does the opposite.
These routings are independent of the variable's signed value. Equality
causes no difficulty: choose the named fixed-sentinel track consistently.
Both identities remain valid when the variable itself is an infinity.

Every such comparator contributes zero retained comparisons. A comparator
between two designated fixed sentinels also contributes zero. Delete
these first-layer comparisons and follow their fixed routings. The
remaining first-layer comparisons form an ordinary matching on the
surviving input tracks, with their original relative order, followed by
a fixed relabelling of physical positions.

Pull the second matching back through that relabelling and discard its
comparisons involving designated fixed sentinels. This is again a
matching. A reversed orientation in this final counted layer can be
normalized: whether the two incoming types are both real is independent
of the comparator's orientation. Hence both counts are preserved for
every family member. No additional layer has been introduced. □

This lemma concerns two layers of counts; it does not assert equality of
the final signed-state positions after orientation normalization.

The property is also invariant under a common permutation of the input
wire labels. Map the first matching back to the old labels, orient its
comparators normally and absorb the resulting fixed output swaps into
the second matching. The first retained counts are unchanged, and the
second retained counts again do not depend on final orientations.

## 3. Width-independent consequence

Embed either the twelve-wire family above or the fourteen-wire family F
into any larger set of wires, in any
fixed order. On every extra wire place a fixed positive or negative
infinity, with the same choice across all twenty states. Then **no two
matching layers can give every state four retained gates in at least
one of the layers**.

Otherwise the pruning lemma and the common-permutation observation would
produce a pair of matchings covering the original small family,
contradicting its checked finite obstruction. The number of additional
wires is arbitrary; the twelve-wire version applies at every width at
least twelve.

To apply it to a sorter, one must establish the needed restriction
family and remaining-depth premise. For example, if twenty placements
leave nine arbitrary reals, blind all layers before a cut, and yield an
embedded copy of F with at most seven layers remaining, this obstruction
and H9 rule out that prefix. In a hypothetical depth-ten sorter on
eighteen wires, such a pattern after three blinded layers would suffice.
We have not proved that every relevant prefix contains such a pattern.

The [four-restriction price obstruction](d17_hand_defects_lemmas.md)
provides another hand-checkable way of excluding a particular next
matching. For the twelve-wire family, the complete hand classification
now supplies the universal contradiction. The remaining sorting-network
challenge is to force such a family in the relevant larger prefixes.

## 4. Direct validation of the pruning step

[fixed_sentinel_pruning.py](fixed_sentinel_pruning.py) implements the
track projection independently of the SAT encoders. It checks:

* every two-layer matching network on widths two through five, every
  choice of one fixed sentinel, both signs, and all signed assignments
  on the other wires: 570,072 count-preservation checks;
* 10,000 checks of the actual twenty-state template embedded at widths
  14, 17, 18, 20 and 24, with multiple fixed sentinels of both signs.

The [audit](results/fixed-sentinel-pruning.json) records the template,
label map and source hash. These checks validate the implementation;
the unbounded-width assertion follows from the hand proof above.
