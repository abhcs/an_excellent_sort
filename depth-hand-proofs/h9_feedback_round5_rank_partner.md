# Rank-threshold partners: a reusable ending lemma

This general lemma compresses the47 ending arguments of the
[H9 case `02 14 56`](h9_feedback_round5_021456.md). It uses the same
fifteen concrete inputs; the accepted endpoint tables and certificate
remain unchanged. The compression is an alternate certificate, not a
new coverage claim.

## 1. The arbitrary-width lemma

Consider any comparator prefix on n inputs, followed by one matching Q
and then d further layers. Put c=2^d. Choose any finite bank of input
permutations of ranks0 through n−1. At the prefix cut let x_i denote
wire i on a bank run x, and let l_i,h_i be its smallest and largest
observed ranks.

**Threshold partner lemma.** If h_i−l_i≥c, Q must use i. Any Q partner
j must obey both rules on every bank run x:

* if x_i≤h_i−c, then x_j≥h_i−c+1;
* if x_i≥l_i+c, then x_j≤l_i+c−1.

For the first rule, some anchor run gives the comparison's maximum at
least h_i. If both inputs on another run were at most h_i−c, its maximum
would differ by at least c between the two runs. For the second, an
anchor gives the minimum at most l_i; both inputs at least l_i+c on
another run again give a gap of c. The attainable-rank interval lemma
then supplies at least c+1 ranks at that Q output, but its d remaining
layers can reach at most c final positions. The same argument applied
to an idle wire proves the mandatory-use assertion.

The interval lemma holds for every comparator prefix on arbitrary real
inputs: swaps of consecutive rank values connect the input permutations,
and each such swap changes any fixed output by at most one. Identifying
the two values proves that last assertion because a monotone value map
commutes with every comparator. Thus intermediate ranks are attained.

For each i, let C(i) be the set of other wires satisfying both threshold
rules. Every possible Q edge ij requires j∈C(i) **and** i∈C(j).
This reciprocity is essential: a partner may have a smaller low endpoint
or a larger high endpoint than the original pivot.

In fact, reciprocal compatibility exactly captures the endpoint-range
test on the chosen finite bank. The minimum output's observed low is
min(l_i,l_j), and the maximum output's observed high is max(h_i,h_j).
A forbidden minimum gap is witnessed by both inputs reaching at least
min(l_i,l_j)+c; apply the high rule at an endpoint attaining that smaller
low. A forbidden maximum gap is witnessed by both inputs being at most
max(h_i,h_j)−c; apply the low rule at an endpoint attaining that larger
high. These are also sufficient to witness the corresponding range gap.
Compatibility is only a necessary condition for a sorting completion.

This defines a general partner graph: retain ij exactly when both
membership conditions hold. Q must be a matching in this graph covering
every vertex with observed span at least c. An isolated mandatory vertex
is impossible. More generally, an independent set of mandatory vertices
with fewer neighbors than vertices is impossible by the matching bound.
The statement applies to every n and d, without a perfect-Q assumption.

## 2. Forty-seven short partner intersections

Here d=2 and c=4. Input letters refer to the unchanged fifteen-input
bank in the [original appendix](h9_feedback_round5_tables.md#4-fifteen-concrete-inputs).
An endpoint entry `A:2–B:7` gives the pivot's observed low and high.
A guard `C lo:012` excludes those listed partners because both their
values and the pivot value on input C are at most h−4. A `hi` guard
uses values at least l+4. The listed guards' union removes all partners
except those explicitly named in the remainder column. Every pivot's
endpoint gap is at least four, so leaving it idle is also impossible.

Forty-four rows have empty remainder immediately. For the other three,
the reciprocal table below applies the same lemma from each remaining
partner's side. Thus all47 ending forms are excluded without a table
of423 separate partner/output endpoint pairs.

| Label | Pivot | Endpoints | Guards and excluded partners | Remainder |
|---|---:|---|---|---|
| 1.1 | 7 | H:1–K:7 | A lo:035; C hi:468; D lo:023; E lo:013 | empty |
| 1.2 | 8 | H:2–G:8 | A lo:0135; B hi:57; D lo:0235; G hi:46 | empty |
| 1.3 | 7 | H:1–K:7 | E lo:013; I hi:256; K hi:468 | empty |
| 1.4 | 8 | H:2–F:8 | A lo:0134; F hi:25; G hi:67 | empty |
| 1.5 | 8 | H:2–G:8 | A lo:0123; B hi:57; D lo:0234; G hi:56 | empty |
| 1.6 | 7 | H:1–K:7 | C hi:456; E lo:013; J hi:258 | empty |
| 2.1 | 8 | H:2–J:8 | A lo:0135; B hi:37; C hi:46; D lo:0235 | empty |
| 3.1 | 7 | H:1–K:7 | A lo:025; B hi:468; D lo:023; E lo:012 | empty |
| 3.2 | 7 | H:1–K:7 | E lo:012; I hi:356; K hi:468 | empty |
| 3.3 | 7 | H:1–K:7 | A lo:023; D lo:024; E lo:012; I hi:568 | empty |
| 3.4 | 8 | H:2–G:8 | A lo:0125; B hi:47; D lo:0235; G hi:46 | empty |
| 3.5 | 8 | H:2–F:8 | A lo:0124; F hi:35; G hi:67 | empty |
| 3.6 | 8 | H:2–G:8 | A lo:0123; B hi:37; D lo:0234; G hi:56 | empty |
| 3.7 | 7 | I:1–K:7 | A lo:015; B hi:468; D lo:013; E lo:012 | empty |
| 3.8 | 7 | I:1–K:7 | E lo:012; J hi:358; K hi:468 | empty |
| 3.9 | 7 | I:1–K:7 | B hi:368; D lo:014; E lo:012; J hi:358 | empty |
| 3.10 | 8 | I:2–G:8 | A lo:0125; B hi:47; D lo:0135; G hi:46 | empty |
| 3.11 | 8 | I:2–F:8 | A lo:0124; F hi:35; G hi:67 | empty |
| 3.12 | 8 | I:2–G:8 | A lo:0123; B hi:37; D lo:0134; G hi:56 | empty |
| 3.13 | 7 | N:1–K:7 | B hi:468; C lo:015; E lo:012; M lo:013 | empty |
| 3.14 | 7 | N:1–K:7 | D hi:356; E lo:012; K hi:468 | empty |
| 3.15 | 7 | N:1–K:7 | B hi:368; D hi:568; E lo:012; M lo:014 | empty |
| 3.16 | 8 | C:2–G:8 | A lo:0125; B hi:47; G hi:46; I lo:0135 | empty |
| 3.17 | 8 | C:2–F:8 | A lo:0124; F hi:35; G hi:67 | empty |
| 3.18 | 8 | C:2–G:8 | A lo:0123; B hi:37; G hi:56; I lo:0134 | empty |
| 4.1 | 8 | F:3–J:8 | B hi:7; C hi:6; D lo:0145 | 23 |
| 5.1 | 8 | A:3–K:8 | A lo:0125; B hi:4; C hi:6; D lo:1235; K hi:7 | empty |
| 5.2 | 2 | E:1–F:6 | E lo:03; F hi:468; H lo:15; J hi:478 | empty |
| 5.3 | 3 | E:2–B:8 | A hi:26; B hi:78; E lo:0145 | empty |
| 5.4 | 3 | E:2–B:8 | A hi:26; B hi:78; E lo:0145 | empty |
| 5.5 | 3 | E:2–A:7 | A hi:26; E lo:014; H hi:67; I hi:68 | 5 |
| 5.6 | 3 | E:2–A:7 | A hi:26; E lo:015; H hi:68; I hi:67 | 4 |
| 5.7 | 3 | N:0–B:6 | A lo:05; E lo:02; G hi:4678; N lo:01 | empty |
| 5.8 | 3 | C:1–F:7 | A lo:057; C lo:015; E lo:025; F hi:468 | empty |
| 5.9 | 3 | C:0–B:6 | A lo:02; B hi:5678; C lo:04; N lo:01 | empty |
| 5.10 | 3 | C:1–B:7 | A lo:024; B hi:678; C lo:014; F hi:568 | empty |
| 5.11 | 8 | A:3–K:8 | A lo:0125; B hi:4; C hi:6; D lo:0235; K hi:7 | empty |
| 5.12 | 3 | A:1–I:6 | A lo:02; C hi:568; D lo:04; I hi:567; K lo:01 | empty |
| 5.13 | 3 | C:1–B:7 | A lo:024; B hi:678; C lo:012; G hi:568 | empty |
| 5.14 | 2 | C:1–F:6 | B lo:01; C lo:05; E lo:03; F hi:468; J hi:478 | empty |
| 5.15 | 2 | C:1–F:6 | B lo:01; C lo:04; E lo:03; F hi:568; J hi:578 | empty |
| 5.16 | 3 | C:0–B:6 | A lo:04; B hi:5678; C lo:02; N lo:01 | empty |
| 6.1 | 3 | C:1–B:7 | A lo:024; B hi:678; C lo:012; G hi:568 | empty |
| 6.2 | 5 | L:2–B:7 | A lo:023; B hi:78; C hi:46; G lo:013 | empty |
| 6.3 | 5 | A:2–C:7 | A lo:023; C hi:46; F hi:78; K lo:012 | empty |
| 6.4 | 2 | E:1–F:6 | B lo:01; C lo:03; G hi:467; J hi:578 | empty |
| 8.1 | 7 | I:2–G:8 | A lo:0123; B hi:38; D lo:0134; G hi:56 | empty |

The remaining directed memberships fail as follows. Each guard excludes the original pivot, so reciprocity forbids that edge.

| Label | Original pivot | Candidate partner | Partner endpoints | Partner guard |
|---|---:|---:|---|---|
| 4.1 | 8 | 2 | E:1–F:6 | G hi:678 |
| 4.1 | 8 | 3 | G:2–D:7 | B hi:78 |
| 5.5 | 3 | 5 | A:1–M:6 | M hi:368 |
| 5.6 | 3 | 4 | C:1–G:6 | G hi:368 |

## 3. Verification

The [independent checker](verify/h9_feedback_round5_partner_proof.py) checks the original certificate hash, evaluates only the fixed fifteen inputs, reads back these printed rows, and verifies every threshold exclusion and reciprocal membership.
It also cross-checks the exact equivalence with the finite-bank minimum/maximum range test. No matching enumeration, solver, or additional input search is used.
The [audit](results/h9-feedback-round5-partner-proof.json) records the counts and source hashes.
