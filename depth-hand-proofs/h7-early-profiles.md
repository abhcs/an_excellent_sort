# Hand proofs for the first two layers on seven and eight wires

**Result.** In a depth-six sorter on seven wires, each of the first two
layers has at least two comparators, and at least one has three. On
eight wires, each has at least three, and at least one has four.

The proof uses $D(5)\ge5$, $D(7)\ge6$, the five-wire thin-layer lemma,
and the hand proof of P7 from [h9.md](h9.md). The only new finite table
has 26 probes, seven third-layer forms and 22 final checks. No SAT
answer is a premise. These are building blocks; they do not settle
$D(13)$, $D(17)$ or $D(18)$.

## 1. A seven-wire sorter cannot have a one-comparator second layer

**Lemma Q7.** A sorter on seven wires with at most six layers has at
least two comparators in its second layer.

Fill only the first layer, to three comparators. Relabel and untangle
to make it $(0,1)(2,3)(4,5)$, with wire 6 idle. These operations preserve
the size of the second layer. An empty second layer contradicts
$D(7)\ge6$. A repeated first-layer gate in the second layer can be
deleted, giving the same contradiction.

If the sole second-layer gate meets wire 6, it touches only one first-layer
pair. Move the other two first-layer gates into the second layer; they
are disjoint from its gate. The resulting sorter has one comparator in
its first layer, contrary to P7.

Otherwise the gate joins two different first-layer pairs. Permuting those
pairs and, if necessary, negating values and reversing the wire order
reduces it to $(0,2)$ or $(0,3)$. Untangling reversed comparators preserves
the layer sizes. These represent equal and opposite endpoint roles in
the first layer, respectively.

Put two sentinels on two different first-layer pairs, each with the sign
that keeps it there. Choose them to blind the second layer. The five
remaining reals meet once in layer 1 and not at all in layer 2. After
pruning, they have at most five active layers, with a one-comparator
first layer. The five-wire thin-layer lemma therefore forces at least
two real-real comparisons in layer 3.

The distinct pairs of sentinel positions after layer 2 are:

| Second layer | Sentinel-position pairs |
|---|---|
| $(0,2)$ | $01,02,03,04,05$ |
| $(0,3)$ | $02,03,13,04,05,34,35$ |

Here $ij$ denotes the unordered pair $\{i,j\}$; signs need not be
listed because only positions determine real-real counts in the next
layer. Each row follows by choosing two of the three first pairs and
one of the two normalized signs on each, then retaining the choices
that blind layer 2.

The third layer must have three gates. If it had two, every listed
sentinel pair would have to avoid all four used wires; the union of the
listed pairs is the six-element set $\{0,\ldots,5\}$, which cannot fit
in the three idle wires. Fewer than two gates is immediately impossible.

Let $v$ be its idle wire. Deleting a listed sentinel pair must remove
at most one of its three gates. Thus every listed pair either contains
$v$ or is itself a third-layer gate. In the graph of listed pairs, every
vertex of degree at least three must consequently be $v$: deleting any
other vertex still leaves two incident edges, which cannot both be in
a matching.

For $(0,3)$, both 0 and 3 have degree four, a contradiction. For $(0,2)$,
this forces $v=0$. Thus only the following case remains:

$$L_1=01\,23\,45,\qquad L_2=02,\qquad
L_3\text{ pairs up }\{1,2,3,4,5,6\}.$$

The gate 45 in layer 3 would repeat its first-layer action, since neither
endpoint was used in layer 2. Delete it if present. The required three
gates then rule it out. There are twelve matchings of the other six
wires that avoid 45.

Swapping the first two input pairs and untangling layer 2 fixes $L_1,L_2$
and swaps labels 1 and 3 before layer 3. Untangling any reversed third-layer
gate only relabels later wires. This reduces the twelve matchings to the
seven forms in the table below. Section 2 rules all of them out and
finishes Q7.

## 2. A finite probe certificate for the remaining case

A probe is a pair of states differing only by changing a 0 to a 1 on
one wire, marked `*`. Through a comparator layer they still differ on
exactly one wire: compare the two states directly, or use h9.md Lemma 13.
If a probe has $6-k$ fixed ones, its sorted outputs differ at wire $k$.

Write $P_t(k)$ for the wires on which our output-$k$ probes can differ
after layer $t$. Each must reach output $k$ through the remaining
network. With two layers remaining, a backward dependency cone has at
most four wires. Therefore a necessary condition is

$$|P_4(k)|\le4.$$

After the specified first two layers, the possible states are the
Cartesian product of

```
core 0..3: 0000 0001 0011 0100 0101 0110 0111 1111
pair 4,5: 00 01 11
wire 6:   0 1
```

Every displayed core state is fixed by the core prefix except `0110`,
which is obtained from input `1100`. This supplies a direct input
witness for each state used below; there is no search assumption.

Use the following 26 probes after layer 2. The first column is the
required output wire $k$.

```text
4 01100*0
4 01*1000
4 00110*0
3 *111000
3 011100*
2 111100*
4 0100*10
3 01*1010
3 0011*10
2 *111010
4 000011*
3 010011*
2 01*1110
4 010*001
3 01100*1
4 00*1001
3 01010*1
3 00110*1
4 0*00011
3 010*011
2 011*011
2 01*1011
2 0011*11
3 0*00111
2 01*0111
2 0*01111
```

Apply any of the seven third layers to these probes. The median probes
reach all seven wires: $P_3(3)=\{0,\ldots,6\}$. A single next-layer
gate can reduce this support by at most one. Thus $|P_4(3)|\le4$ forces
exactly three gates, each merging its two median probe positions to
one. Call these the *median edges*.

For output 2, put $p_2=|P_3(2)|$. For a possible gate $e$, let $w_2(e)$
be the change in this support size when just $e$ is applied. For any
matching $M$, disjointness makes the changes additive:

$$|P_4(2)|=p_2+\sum_{e\in M}w_2(e).$$

The following table is obtained by applying one layer to the explicit
probes. The entry `03:-1` denotes edge 03 with weight $-1$; a positive
weight is possible because a probe at one endpoint can move to either
endpoint on different states.

| Case | Third layer | $p_2$ | Median edges, with $w_2$ |
|---|---|---:|---|
| 1 | `12 34 56` | 6 | `03:-1, 05:+0, 06:-1, 13:+0, 16:-1, 24:-1, 25:+0, 26:-1, 35:+0, 46:-1` |
| 2 | `12 35 46` | 6 | `03:+0, 04:-1, 06:+0, 14:+0, 15:+0, 24:-1, 25:+0, 26:-1, 34:+0, 56:+0` |
| 3 | `13 24 56` | 5 | `02:-1, 05:+0, 06:-1, 12:+0, 16:-1, 25:+1, 34:+0, 35:+0, 36:+0, 46:-1` |
| 4 | `13 25 46` | 5 | `02:+0, 04:-1, 06:+0, 14:+0, 15:+0, 24:+0, 34:+0, 35:+0, 36:+0, 56:+0` |
| 5 | `14 25 36` | 5 | `01:-1, 02:+0, 03:+0, 12:+0, 13:+0, 16:+0, 35:+0, 45:+0, 46:+0, 56:+0` |
| 6 | `14 26 35` | 6 | `01:-1, 02:+0, 03:+0, 12:+0, 13:+0, 25:+0, 45:+0, 46:-1, 56:+0` |
| 7 | `15 24 36` | 5 | `01:+0, 02:-1, 03:+0, 12:+0, 16:+0, 23:+0, 35:+0, 45:+0, 46:+0, 56:+0` |

| Case | Remaining fourth layer | Output-4 probe positions |
|---|---|---|
| 1 | `16 24 35` | `12456` |
| 1 | `03 25 46` | `12456` |
| 1 | `03 16 24` | `12456` |
| 1 | `03 16 25` | `12456` |
| 1 | `05 16 24` | `12456` |
| 1 | `06 24 35` | `12456` |
| 1 | `06 13 24` | `23456` |
| 2 | `04 15 26` | `12345` |
| 3 | `12 35 46` | `23456` |
| 3 | `02 35 46` | `13456` |
| 3 | `02 16 34` | `13456` |
| 3 | `02 16 35` | `13456` |
| 3 | `05 12 46` | `23456` |
| 3 | `05 16 34` | `13456` |
| 3 | `06 12 34` | `23456` |
| 3 | `06 12 35` | `23456` |
| 4 | `04 15 36` | `12345` |
| 5 | `01 35 46` | `12345` |
| 6 | `01 25 46` | `12345` |
| 7 | `02 35 46` | `13456` |
| 7 | `02 16 45` | `13456` |
| 7 | `02 16 35` | `13456` |

The second table lists every three-edge matching in the corresponding
median-edge graph with $p_2+\sum w_2\le4$. Each has five output-4 probe
positions, violating the cone bound. This proves Q7. $\square$

## 3. Two thin first layers on seven wires are impossible

**Lemma H7.** No depth-six seven-wire sorter has at most two comparators
in each of its first two layers.

*Proof.* P7 handles first-layer size at most one. Otherwise let its two
pairs be $A,B$, with three idle wires.

If one first-layer pair is untouched by the second layer, move its gate
into the second layer. The first layer then has one gate, violating P7.

If the second layer joins two initially idle wires, its only other
possible gate must touch both $A,B$; otherwise the preceding case applies.
Move the idle-idle gate into the first layer. The second layer then has
one gate, violating Q7.

In the remaining case, every second-layer gate touches $A$ or $B$, and
both pairs are touched. Choose one endpoint from each pair so that they
together meet every second-layer gate. This is possible with at most
two second-layer gates: if one touches only $A$, assign it to $A$ and
assign the other to $B$; otherwise interchange the roles or assign the
two gates to different pairs arbitrarily.

Place sentinels at the chosen endpoints, with signs keeping them there
in the first layer. Both first layers are blind. The five remaining
reals would be sorted in four layers, contradicting $D(5)\ge5$.
$\square$

P7, Q7 and H7 give the seven-wire profiles $(2,3),(3,2),(3,3)$.

## 4. The eight-wire consequence

**Theorem.** The first two layer sizes of a depth-six eight-wire sorter
are $(3,4),(4,3)$ or $(4,4)$.

*Proof.* If its first layer has at most two gates, one infinity removes
a gate and leaves a depth-six seven-wire sorter with at most one gate
in its first layer, contrary to P7. An empty first layer is excluded by
$D(7)\ge6$ after pruning a wire and dropping that layer.

If its second layer has at most two gates, place an infinity on an
endpoint of one, choosing the sign that keeps it on that wire through
the first layer. It removes a second-layer gate. Pruning leaves the
seven-wire sorter forbidden by Q7. The empty case is immediate.

If both layers have at most three gates, they now have exactly three
each. Their six-wire supports intersect. An infinity at a common wire,
with the sign that keeps it there in the first layer, removes a gate
in both. Pruning leaves the sorter forbidden by H7. $\square$

## Verification and the larger cases

[`verify/h7_profiles_proof.py`](verify/h7_profiles_proof.py) verifies each
probe using two explicit original inputs, the reduction from twelve
third layers to seven, both tables, and all 232 possible fourth layers
as an independent cross-check. The [certificate](results/h7-profiles-proof.json)
records those inputs and all table data. It uses no SAT solver.

Small SAT tests independently confirmed the excluded profiles and found
sorters with profiles $(2,3)$ on seven wires and $(3,4)$ on eight; every
positive was checked on all binary inputs. See the
[probe audit](results/early-profiles-7-8/audit.json).

For a putative depth-eight sorter on 13 wires, each half-blind seven-real
restriction must therefore have one of these seven-wire profiles in
original layers 3 and 4. A [complete-cover screen](../d18-search/results/profile-frontier13/audit.json)
found compatible third and fourth layers for **all 117 prefix cases**.
The witnesses were replayed by direct sentinel simulation. They are not
sorting networks. This particular two-layer profile condition alone
does not eliminate a D(13) prefix case.
