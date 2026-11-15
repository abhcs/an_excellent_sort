# Partial sixth-layer obstructions from rank partners

The three [concrete D18 prefix exclusions](rank-frontier-round6-hand.md)
extend to entire families of sixth layers. Keep only the first five
layers of the named beam in the unchanged
[source certificate](results/rank-layer-round6-hand-certificate.json).
No sixth-layer matching containing the following fixed gates extends
to a ten-layer sorter:

| Five-layer prefix | Required gates in L6 | All other L6 gates |
|---|---|---|
| beam00 | (1,4), (5,6), (12,13) | arbitrary on the other12 wires |
| beam16 | (4,6), (5,15), (7,14), (16,17) | arbitrary on the other10 wires |
| beam32a | (0,1), (2,8), (4,5), (6,9), (10,14), (12,13) | arbitrary on the other6 wires |
| beam32b | (2,8), (3,7), (4,5), (6,9), (10,14), (12,13) | arbitrary on the other6 wires |

Idle wires are permitted throughout. These are conditional exclusions
after the three specified five-layer prefixes, not a complete D18 cover.
The proof uses the original69 concrete input permutations and explicit
[local activity tables](d18_rank_partner_round7_tables.md). It neither
enumerates complete sixth layers nor uses a SAT answer.

## 1. A general partial-layer support theorem

Let P be any comparator prefix on n wires. The proposed continuation is
an unknown matching M, then a matching Q, then d further layers. Put
c=2^d. Fix any submatching F of M and a finite bank of distinct-rank
input permutations. A wire covered by F has a known value after M on
every bank input, because all other M gates are disjoint from F.

For each wire v, the following list contains every possible local
activity of M at v:

* If F covers v, use its fixed F comparator.
* Otherwise v may be idle, or may compare with any other wire not
  covered by F. The smaller physical index takes the minimum, and
  the larger takes the maximum.

An activity fixes v's bank vector without specifying the rest of M.
Different activity choices need not be simultaneously consistent;
allowing them independently only enlarges the set of possible partners.

Choose a pivot p covered by F. If its observed rank span after M is
at least c, Q must use p. For each possible Q partner v and each local
M activity at v, evaluate the minimum and maximum of the fixed pivot
vector and the resulting v-vector. Exclude that activity if either
output has witnessed span at least c.

For d≥1, also exclude it if both outputs have witnessed span c−1
and their intervals have odd intersection. To justify this rule,
attainable ranks at a wire form an interval. A span c−1 therefore
forces c attainable ranks. Its d-layer forward cone has size at most c,
so it must equal that rank interval. Reaching size c requires doubling
at every remaining layer, including the last. Each full cone is thus
a union of final-layer comparator edges. The intersection of two
such unions has even size. This applies to the two outputs of one
comparison as well as to outputs of disjoint comparisons.

Let R_F(p) contain v if at least one of its local activities survives
these tests. In every completion of M containing F, any Q partner of p
must belong to R_F(p). Consequently:

* An empty R_F(p) for a mandatory pivot excludes every completion of F.
* More generally, mandatory pivots with no edges between them must
  have at least as many possible neighboring wires as pivots.
* If a small partner graph forces Q edges whose endpoints are all
  covered by F, their output vectors are fixed. Any odd intersection
  of two forced full cones excludes every completion of F.

The width rule is exactly the finite-bank rank-threshold partner test
from the [arbitrary-width lemma](../depth-hand-proofs/h9_feedback_round5_rank_partner.md):
for envelope [l,h], a partner must be above h−c whenever the pivot is
at most h−c, and below l+c whenever the pivot is at least l+c.
The reverse membership condition must also hold. The local activity
test applies this rule before M has been fully chosen.

For completeness, the rank-interval fact requires no finite-bank
completeness assumption. All input permutations are connected by swaps
of consecutive rank values. Each such swap changes any fixed network
output by at most one: identifying the two swapped values commutes with
minimum and maximum. Every rank between any two witnessed endpoints
is therefore attained. The bank supplies endpoint witnesses only.

## 2. Three isolated or forced partner arguments

Here P has five layers, M=L6, Q=L7, and d=3, so c=8. The tables check
every local activity permitted by each displayed partial matching F.
They give the following universal neighborhoods, regardless of all
other sixth-layer choices:

| Family | Mandatory pivot | R_F(p) |
|---|---:|---|
| beam00 | 12 | empty |
| beam16 | 6 | empty |
| beam32a | 5 | {2,8} |
| beam32a | 12 | {8} |
| beam32b | 5 | {2,8} |
| beam32b | 12 | {8} |

The first two families fail immediately. In either beam32 family,
Q must contain (8,12), then (2,5). All four endpoints are covered by F,
so the two output vectors are independent of the unchosen M gates.
The minimum at output8 of (8,12) has witnessed ranks3 and10, forcing
full cone [3,10]. The maximum at output5 of (2,5) has ranks4 and11,
forcing full cone [4,11]. Their intersection has seven positions,
contrary to the full-cone parity rule.

The local support calculation uses only width exclusions except for
(2,12) in each beam32 family. Its two outputs force [2,9] and [9,16],
whose one-position intersection excludes that edge. This is why
wire12's support is {8}, while wire5's is {2,8}.

## 3. Constraints before fixing L6

These certificates can be imposed as forbidden partial-matchings after
their corresponding five-layer prefixes. For example, after beam00,
L6 cannot contain all three of (1,4), (5,6), (12,13). No choice of its
remaining gates can repair that pattern. After beam32, write

```
C = {(2,8),(4,5),(6,9),(10,14),(12,13)}.
```

If L6 contains C, it can contain neither (0,1) nor (3,7). These are
two structural constraints on an unfinished L6, not clauses obtained
from an exact sorting search.

For scale, a free k-wire set has I_k possible matchings, where
`I_0=I_1=1` and `I_k=I_{k-1}+(k-1)I_{k-2}`. Thus the first two
patterns cover140,152 and9,496 labelled sixth-layer matchings under
their respective five-layer prefixes. Each beam32 pattern covers76;
their overlap fixes seven gates and covers10, so together they cover142.
These counts include redundant comparisons and idle wires. They are
not counts of canonical D18 cover cases.

## 4. Fixed verification

The [independent checker](d18_rank_partner_round7_partial_check.py)
checks the unchanged source-certificate hash and all required activity
domains. Each exclusion is verified on its explicit rank endpoints;
the printed tables group activities sharing the same witnesses.
The domains are local choices at one partner wire, never full M
matchings. The [audit](results/d18-rank-partner-round7-partial-proof.json)
records exact counts and hashes. The original six-prefix certificates
and tables are unchanged.
