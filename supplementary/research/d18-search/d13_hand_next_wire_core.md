# Case 116 needs a wide wire interval: a smaller checked structural target

**New result.** The eight central **rank-position degree bounds are not
needed** for the checked case-116 obstruction. The ten wire bounds alone
are impossible:

    |Q6(c)| <=4 for every c=2,...,11.

This statement ranges over every four-layer continuation of the fixed
relabelled two-layer prefix below. It contains no rank-cardinality bound,
common-ending routing, or simulated sorting suffix. It is a stronger
structural statement than the previous eighteen-bound core.

The application to this whole prefix is still SAT-assisted. The new
independently checked certificate is not a hand proof of the displayed
universal statement, and it closes no additional complete-cover case:
case 116 was already excluded by the earlier structural certificate.

## 1. Exact prefix and scope

These labels are the relabelled labels of the earlier checked probe
result, not the original cover labels used in the rescheduling note.

```text
L1: (0,6) (1,7) (2,9) (3,12) (4,11) (5,10)
L2: (0,5) (1,8) (2,10) (3,11) (4,12)
```

After any four further matching layers, at least one wire c between 2
and 11 has five or more attainable ranks. Therefore this prefix cannot
have a depth-eight sorting completion: a wire reaches at most four
outputs through the two remaining matching layers.

The free layers are arbitrary standard matching layers. The encoder
omits redundant comparisons using the existing model's safe redundancy
rules. Deleting such a comparison preserves the prefix function, hence
also the attainable ranks on every **named** wire, without adding a
layer. Thus those rules do not weaken the asserted statement about all
continuations. The unused two ending layers can be empty; they impose
no common routing or data-comparison requirements at this cut.

## 2. A two-run form of the new hand-proof target

The attainable ranks on one wire form an interval. The established
rank-interval lemma gives

    Q(c)=[tau0(c)-1, 13-tau1(c)],
    |Q(c)|=15-tau0(c)-tau1(c),

where tau0 is the smallest number of zero inputs forcing that wire to
zero, and tau1 the smallest number of one inputs forcing it to one.
These identities were already proved in `depth-hand-proofs/d13.md`,
Lemma 15; no novelty is claimed for them.

The new universal target is consequently equivalent to

    for every four-layer continuation, some c in {2,...,11}
    satisfies tau0(c)+tau1(c)<=10.                    (1)

For any fixed continuation, (1) has a particularly small witness: two
binary runs. One input with a zeros makes wire c output 0; another input
with b ones makes it output 1; and a+b<=10. No table of all rank probes
is needed to witness that wire's failure.

Equivalently, the zero-output input has at least three more ones than
the one-output input. This is a comparison of Hamming weights, not a
claim that the two inputs are coordinatewise ordered.

The unresolved step is to force such a pair of runs uniformly over all
four free matching layers. A small certificate for one selected
continuation does not establish that uniform assertion.

## 3. Endpoint encoding and checked proof

The fresh encoder is
[d13_hand_next_endpoints.py](d13_hand_next_endpoints.py). It uses the
interval endpoint representation introduced in `interval_frontier.py`.
For each wire c, choose an interval [lo_c,hi_c] containing its true
attainable interval. Boolean thresholds represent

    L_c(j): lo_c>=j,       U_c(j): hi_c<j.

For a binary input with z zeros, a cut-state zero on c enforces lo_c<z;
a cut-state one enforces hi_c>=z. Monotonicity of the endpoint thresholds
and the fact that sorted inputs are fixed ensure a consistent interval
containing c. The width-four clauses on a selected wire are

    L_c(k+1) or U_c(k+4),       k=0,...,8.

They state that lo_c<=k implies hi_c<=k+3. Choosing the exact attainable
interval satisfies every endpoint clause whenever that wire's true
interval has width at most four. UNSAT therefore excludes the necessary
wire-width condition, even though chosen intervals may overapproximate
the true ones.

The pure-wire solve with all thirteen wire bounds returned UNSAT in
25.43 seconds. Its semantic assumption core used only wires 2 through
11. A separate control run including all rank bounds also returned
UNSAT, in 28.66 seconds.

The formula was then rebuilt with **only those ten wire bounds**, no
rank-support cardinalities, and no routing. It was exported with a DRAT
proof and independently verified:

| Quantity | Value |
|---|---:|
| Variables | 23,509 |
| Clauses | 341,202 |
| Solve, including build/export | 19.79 s |
| Independent DRAT check | 13.69 s |
| Solver/checker status | UNSAT / VERIFIED |

The [result manifest](results/d13-hand-next-endpoints-central-checked.json)
binds the prefix, selected bounds, CNF, proof, checker, and encoder
dependencies by SHA-256. The certificate directory contains
[the CNF](results/d13-hand-next-endpoints-central-checked/problem.cnf),
[proof](results/d13-hand-next-endpoints-central-checked/proof.drat), and
[checker log](results/d13-hand-next-endpoints-central-checked/check.log).

All ten wire-bound unit clauses appear in the trimmed proof core. This
is **not** a deletion-minimality claim: removing a bound and finding a
different proof was not attempted. A checked CNF certificate also relies
on the soundness of the mathematical translation; it is not a formal
verification of that translation.

Each solver and checker child had a hard 60-second external wall cap.
Every process completed, and all terminal records are saved. No timeout
is reported as a refutation.

## 4. Controls and the relation to the earlier hand work

The existing depth-nine sorter extending this exact two-layer prefix
was replayed on all 8192 binary inputs. At cut seven, every wire interval
has width at most four, so the wire-bound condition passes at the correct
depth. The [control record](results/d13-hand-next-endpoints-controls.json)
also illustrates the two-run certificate on its cut-six prefix:

* wire 3 has interval [2,7];
* input `1111011111100` has three zeros and makes that wire output 0;
* input `0101100110010` has six ones and makes it output 1.

Strings list wires 0 through 12 from left to right. The sum 3+6=9 is
at most ten, certifying a wide interval on that **particular** six-layer
prefix. This illustration is not the universal case-116 proof.

The earlier six-probe and two-rank matching-price certificates in
`d13_hand_obstructions.md` likewise concern a selected five-layer
continuation. In contrast, the new checked wire-only statement quantifies
over every four-layer continuation of the fixed two-layer case. What
remains missing is its short hand derivation.
