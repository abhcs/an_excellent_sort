# A five-layer D(18) prefix excluded by four hand restrictions

**Result.** The following five layers cannot begin a depth-ten sorter on
eighteen wires. The proof uses four explicit seven-real restrictions,
rescheduling, and a vertex-price inequality. SAT and exhaustive search
are not premises.

```
L1 = (0,6)(1,10)(2,15)(3,5)(4,9)(7,16)(8,13)(11,17)(12,14)
L2 = (0,12)(1,4)(2,6)(3,11)(5,17)(7,15)(8,9)(10,14)(13,16)
L3 = (0,5)(1,16)(2,13)(3,10)(4,15)(6,9)(7,14)(8,11)(12,17)
L4 = (0,15)(1,7)(2,3)(4,12)(5,9)(6,10)(8,14)(11,13)(16,17)
L5 = (0,1)(2,8)(3,4)(5,7)(6,11)(9,15)(10,12)(13,14)(16,17)
```

The exact arrays are also in the
[certificate](results/commuting-prefix18-hand-proof.json).
This is the first five layers of the saved
`combined-prefix-probe18.json` candidate. The result excludes every
continuation of this particular prefix; it does not exclude an entire
case of the complete two-layer cover.

## 1. Four restrictions compress five layers to one

In the table, every position not listed as a negative or positive
sentinel contains an arbitrary real. The two retained comparisons are
specified by their **original input track labels**, with the minimum
sent to the first listed track. Their orientations need not agree with
the order of those labels. Each pair of comparisons uses disjoint tracks.

| Restriction | Negative sentinel inputs | Positive sentinel inputs | Compressed oriented comparisons | Real positions after L5 |
|---|---|---|---|---|
| 1 | 1,2,3,7,10,12,15 | 9,11,13,17 | `(6,0)`, `(8,14)` | 7,8,9,10,11,12,13 |
| 2 | 0,1,3,7,8,10,12 | 2,6,15,17 | `(9,4)`, `(13,16)` | 4,7,10,11,12,13,16 |
| 3 | 1,2,3,7,8,10,12,15 | 9,11,17 | `(6,0)`, `(13,16)` | 7,9,10,11,12,13,16 |
| 4 | 1,2,3,7,8,10,12,15,16 | 9,17 | `(6,0)`, `(11,14)` | 7,9,10,12,13,14,16 |

The retained track comparisons layer by layer are particularly short:

| Restriction | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|
| 1 | `(0,6)` | empty | empty | `(8,14)` | `(6,0)` |
| 2 | `(4,9)` | `(13,16)` | empty | empty | `(9,4)` |
| 3 | `(0,6)` | `(13,16)` | empty | empty | `(6,0)` |
| 4 | `(0,6)` | empty | empty | empty | `(6,0)`, `(11,14)` |

In particular the comparison in L1 is redundant after retaining the
oppositely oriented comparison of the same pair in L5. The other pair
is disjoint from it. These identities explain the compression without
an enumeration over real values.

**Compression lemma.** Follow real tracks through comparisons with
sentinels. If all retained comparisons belong to disjoint pairs of
tracks, the whole prefix is equivalent to one layer with one comparison
on each pair, followed by a fixed routing of its outputs.

For each pair, its last comparison determines which track receives the
minimum and which receives the maximum. Earlier comparisons of that
same pair are redundant. Comparisons on different pairs commute.
Sentinel comparisons have fixed outcomes and supply only the routing.
This proves the lemma, including reversed orientations on a retained
pair. Pruning and untangling convert the resulting generalized sorter
to an ordinary sorter while preserving layer sizes.

Applying this argument to each table row compresses L1,...,L5 to a single
layer of two comparisons. In a hypothetical depth-ten completion, the
five remaining layers would therefore give a sorter on seven reals in
at most six layers, starting with two comparisons. The
[hand seven-wire profile theorem](../depth-hand-proofs/h7-early-profiles.md)
forces its next layer to have three comparisons.

Thus the same original matching L6 must retain three real-real
comparisons on **each** of the four displayed real-position sets.

## 2. A general four-set obstruction

Let C be a set of common real positions and let a,b,c,x,y,z be six
different positions outside C. Consider

```
C+{a,b,x}, C+{b,c,y}, C+{a,b,c}, C+{a,c,z}.
```

Give every position in C price 2; give a,b,c price 1; give every other
position price 0. For an edge uv, its multiplicity is the number of
these four real sets containing both u and v. Directly:

* a common/common edge has multiplicity 4 and price sum 4;
* a common/a,b,c edge has multiplicity 3 and price sum 3;
* an edge among a,b,c has multiplicity 2 and price sum 2;
* every other occurring edge has multiplicity 1 and price sum at least 1.

Since edges of a matching are disjoint, the sum of its retained counts
over the four sets is at most `2|C|+3`. If each real set has R=|C|+3
positions, this is `2R-3`, strictly less than `4 floor(R/2)` for every
R>=3. No matching can attain the maximum retained count on all four
sets simultaneously. Extra ambient positions do not change the argument.

For our four restrictions take

```
C={7,10,12,13}, (a,b,c)=(9,11,16), (x,y,z)=(8,4,14).
```

The total price is 11. Section 1 requires a total of 12 retained
comparisons in L6. This contradiction excludes every depth-ten
completion of the five-layer prefix. □

## 3. Verification and the distinction from the blinding route

[commuting_prefix_hand_verify.py](commuting_prefix_hand_verify.py)
independently runs all 7! distinct-real assignments for each of the
four restrictions, checks exact equality with the stated compressed
layer and fixed output routing, and checks every one of the 153
edge-price inequalities. All 20,160 direct-value comparisons pass.
The resulting [certificate](results/commuting-prefix18-hand-proof.json)
binds the inputs and verifier by hash.

The C++ discovery program [commuting_prefix_states.cpp](commuting_prefix_states.cpp)
searched normalized signed placements for this rescheduling condition.
It found nine distinct seven-real cut sets for the prefix; four suffice
for the hand proof. Its exhaustive search is not needed to check or
justify the four explicit restrictions.

The separate [fixed-prefix audit](results/signed-fork-prefix18-samples.json)
found no literal signed-fork family after four fully blinded layers in
160 sampled D18 prefixes: 155 had no seven-real blind restriction at
all, and the other five had at most two cut states. None had an
eight-real blind restriction. These samples are not a complete cover.
The present proof makes progress on this limitation by allowing early
real comparisons and compressing them, then using a one-layer price
obstruction at the next layer.
