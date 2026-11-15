# Two more D(18) prefix exclusions using five reals

These hand certificates exclude every depth-ten completion of two
specified **six-layer** prefixes. They do not close complete two-layer
cover cases. The exact prefixes, placements and track routings are in
the [verified certificate](results/commuting-prefix18-additional-hand-proofs.json).

## 1. Six blinded layers in the budget-survivor prefix

Take the first six layers of `results/budget-counterexample18.json`.
Put negative sentinels on inputs `1,2,5,9,13,14`, positive sentinels on
`4,8,10,11,12,16,17`, and arbitrary reals on the other five inputs.

Every comparison in these six layers meets a sentinel. The reals end
on positions `{6,7,8,9,10}` without comparing to one another. Four
remaining layers cannot sort them, since D(5)>=5. Thus even the first
six layers of this previously saved nine-real-budget survivor cannot
extend to a depth-ten sorter.

## 2. Four restrictions of the cube-free candidate

Take the first six layers of `results/cube-free-prefix-probe18.json`.
For each placement below, the retained comparisons all involve just one
pair of real tracks. Repeated comparisons of that pair compress to its
last orientation, by the [compression lemma](commuting-prefix-hand-proof.md).

| Row | Negative sentinel inputs | Positive sentinel inputs | Compressed oriented pair | Real positions after L6 |
|---|---|---|---|---|
| 1 | 0,1,3,5,7,9,17 | 8,11,12,14,15,16 | `(4,2)` | 5,7,8,10,11 |
| 2 | 1,2,5,6,9,10,11,13 | 4,8,14,16,17 | `(3,7)` | 5,7,11,12,13 |
| 3 | 0,3,9,10,11,12,13,14 | 1,2,6,7,8 | `(15,16)` | 7,10,11,12,15 |
| 4 | 0,1,3,5,9,10,11,12,13,14 | 2,6,8 | `(15,16)` | 7,8,12,13,15 |

If a depth-ten completion existed, each restriction would give a
five-wire sorter in five layers whose first layer has one comparison.
The hand five-wire thin-layer lemma (README Lemma 3) therefore forces
the next original layer, L7, to retain two comparisons in every row.

Give positions `7,11,12` price 3/2, positions `5,8,10,13,15` price
1/2, and all others price zero. For every edge, the number of the four
real sets containing it is bounded by the sum of its endpoint prices.
The total available price is 7, so every matching's total retained
count over the four sets is at most 7. The required total is 8.
This contradiction excludes all depth-ten completions of this prefix.

The pair inequalities can be checked directly from the four sets.
Only pairs `7,11` and `7,12` occur three times; both have price sum 3.
Pairs occurring twice have at least one price-3/2 endpoint. Every other
occurring pair has price sum at least 1.

## 3. Independent checks and scope

[commuting_prefix_additional_verify.py](commuting_prefix_additional_verify.py)
independently reconstructs the retained comparison traces and checks
the compression on every ordering of the five arbitrary reals: 600
direct runs across the five placements. It also verifies all 153
pair-price inequalities for the four-row proof.

Discovery used [commuting_prefix_states.cpp](commuting_prefix_states.cpp),
but the proofs need only these five displayed placements and the
elementary small-width lower bounds. No SAT certificate or search
exhaustion is a premise.
