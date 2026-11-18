# Fixed ending certificates for H9 prefix 02 15 36

Fix the first two layers `01 23 45 | 02 15 36`. The tables below exclude
the31 specified third/fourth-layer pairs from seven-layer sorting
networks. They use sixteen explicit input permutations, threshold
partner guards, and five saturated-cone parity exclusions. No SAT
premise or enumeration of the remaining three layers is needed.

**Scope:** proving that these31 pairs cover all possible continuations
requires the separate third/fourth-layer hand classification. These
ending certificates alone are not a completed H9 class proof.

## 1. Mandatory partners after four layers

Let Q denote layer five, leaving two layers afterward. For an actual
comparator prefix, the ranks attainable at any wire form an interval:
swapping two consecutive ranks in an input changes any fixed output
rank by at most one, and adjacent rank swaps connect all permutations.
The two remaining layers give each Q output a forward cone of at most
four positions. Thus an observed rank gap of at least four is impossible
at any Q output of a sorting network.

At the cut before Q, let l and h be a wire's smallest and largest
observed ranks in the fixed bank. If h-l>=4, that wire is mandatory in Q.
For a prospective partner j, two necessary threshold rules follow:

* On every bank run with pivot value at most h-4, j must have value
  greater than h-4. Otherwise the comparison's maximum is at most h-4
  there but at least h on the high-anchor run.
* On every run with pivot value at least l+4, j must have value less
  than l+4. Otherwise the comparison's minimum is at least l+4 there
  but at most l on the low-anchor run.

The same rules applied from j's side may rule out an edge not excluded
from the pivot's side. These reciprocal guards are necessary even when
j itself is not mandatory. This is the arbitrary-width
[threshold-partner lemma](h9_feedback_round5_rank_partner.md).

An isolated mandatory pivot is impossible. Two mandatory pivots sharing
only one possible partner are also impossible because Q is a matching.

## 2. Saturated four-cone parity

Consider any wire with two layers P,S remaining. Its forward cone has
at most four positions. If it has four positions, it is the union of
two complete edges of the final matching S: its P comparison must have
two outputs, and both must be compared by S to distinct partners.
Therefore any two full four-position forward cones have an **even**
intersection, as each is a union of edges from one common matching S.

For a proposed Q edge, suppose explicit runs give a rank gap of exactly
three at each of its two outputs. The interval lemma forces four ranks
at each output. In any sorting completion, capacity forces the forward
cones to equal these four-rank intervals. An odd intersection of the
intervals therefore rules out the proposed Q edge. This argument needs
only the endpoint witnesses; it does not assume that the bank exhausts
the prefix image.

Five edges are excluded this way. After deleting edge24 in form1.4,
mandatory pivots1 and4 both have only partner3. In the other four forms,
the parity exclusion removes the sole remaining partner of a mandatory
pivot. The other26 forms already have an isolated pivot from threshold
guards alone.

## 3. The31 fixed prefixes

The case numbers refer to the eighteen third-layer representatives.
The labels here identify these explicit layer arrays; their separate
coverage proof is not an input to the endpoint calculation.

| Label | Third layer M | Fourth layer N | Mandatory pivots | Final obstruction |
|---|---|---|---|---|
| 1.1 | `12 34 56 78` | `01 23 47 58` | 4 | isolated pivot |
| 1.2 | `12 34 56 78` | `01 23 48 57` | 5 | isolated pivot |
| 1.3 | `12 34 56 78` | `03 17 25 48` | 7 | isolated pivot |
| 1.4 | `12 34 56 78` | `03 18 25 47` | 1,4 | pivots1,4 share partner3 after parity24 |
| 1.5 | `12 34 56 78` | `17 25 48` | 0 | isolated pivot |
| 1.6 | `12 34 56 78` | `18 25 47` | 0 | isolated pivot |
| 5.1 | `13 24 56 78` | `01 27 34 58` | 7 | isolated pivot |
| 5.2 | `13 24 56 78` | `01 27 35 48` | 7 | isolated pivot |
| 5.3 | `13 24 56 78` | `01 27 38 45` | 7 | isolated pivot |
| 5.4 | `13 24 56 78` | `01 28 34 57` | 8 | isolated pivot |
| 5.5 | `13 24 56 78` | `01 28 35 47` | 8 | isolated pivot |
| 5.6 | `13 24 56 78` | `01 28 37 45` | 8 | isolated pivot |
| 5.7 | `13 24 56 78` | `02 17 34 58` | 7 | isolated pivot |
| 5.8 | `13 24 56 78` | `02 17 35 48` | 7 | isolated pivot |
| 5.9 | `13 24 56 78` | `02 17 38 45` | 7 | isolated pivot |
| 5.10 | `13 24 56 78` | `02 18 34 57` | 8 | isolated pivot |
| 5.11 | `13 24 56 78` | `02 18 35 47` | 8 | isolated pivot |
| 5.12 | `13 24 56 78` | `02 18 37 45` | 8 | isolated pivot |
| 5.13 | `13 24 56 78` | `07 12 34 58` | 7 | isolated pivot |
| 5.14 | `13 24 56 78` | `07 12 35 48` | 7 | isolated pivot |
| 5.15 | `13 24 56 78` | `07 12 38 45` | 7 | isolated pivot |
| 5.16 | `13 24 56 78` | `08 12 34 57` | 8 | isolated pivot |
| 5.17 | `13 24 56 78` | `08 12 35 47` | 8 | isolated pivot |
| 5.18 | `13 24 56 78` | `08 12 37 45` | 8 | isolated pivot |
| 8.1 | `13 27 48 56` | `01 28 35 47` | 8 | isolated pivot |
| 8.2 | `13 27 48 56` | `02 14 38 57` | 8 | isolated after parity 58 |
| 9.1 | `14 23 56 78` | `02 17 35 48` | 7 | isolated after parity 37 |
| 9.2 | `14 23 56 78` | `02 18 35 47` | 0 | isolated pivot |
| 14.1 | `17 23 48 56` | `02 14 35 78` | 7 | isolated after parity 37 |
| 16.1 | `17 24 38 56` | `02 18 37 45` | 8 | isolated pivot |
| 16.2 | `17 24 38 56` | `03 12 47 58` | 8 | isolated after parity 48 |

## 4. Sixteen explicit input permutations

Ranks on original wires0 through8:

| Input | Ranks |
|---|---|
| A | `012347856` |
| B | `014523678` |
| C | `015623478` |
| D | `023456718` |
| E | `051627834` |
| F | `061237485` |
| G | `234506781` |
| H | `234567801` |
| I | `345607812` |
| J | `345678012` |
| K | `450167283` |
| L | `456701283` |
| M | `456701823` |
| N | `560178234` |
| O | `567801234` |
| P | `670128345` |

## 5. Mandatory-pivot guards

An endpoint entry A:0–B:5 gives observed ranks0 and5 on inputs A,B.
A lo guard excludes the listed partners whose values are at most h-4 on that same run; a hi guard uses at least l+4.
The directed remainder follows own guards. The remainder before parity also applies the reciprocal table below.

| Label | Pivot | Endpoints | Guards | Directed remainder | Remainder before parity |
|---|---:|---|---|---|---|
| 1.1 | 4 | H:0–B:5 | A hi:5678; B hi:3678; D lo:0; G lo:2 | 1 | empty |
| 1.2 | 5 | H:0–A:5 | A hi:4678; D lo:0; F hi:3678; G lo:2 | 1 | empty |
| 1.3 | 7 | D:2–B:7 | B hi:68; D lo:012; E lo:013; H lo:014; P hi:56 | empty | empty |
| 1.4 | 1 | A:1–P:5 | A lo:0; H lo:4; P hi:568 | 237 | 3 |
| 1.4 | 4 | H:0–B:5 | A hi:5678; D lo:0; H lo:1 | 23 | 23 |
| 1.5 | 0 | A:0–O:5 | A lo:1; K lo:3; L hi:2568 | 47 | empty |
| 1.6 | 0 | A:0–O:5 | A lo:1; D lo:4; K lo:3; L hi:2568; M hi:2567 | empty | empty |
| 5.1 | 7 | G:1–B:7 | A hi:568; D lo:012; N hi:346 | empty | empty |
| 5.2 | 7 | G:1–C:7 | A hi:568; C hi:468; D lo:012; L lo:023 | empty | empty |
| 5.3 | 7 | G:1–B:7 | B hi:368; D lo:012; J hi:456 | empty | empty |
| 5.4 | 8 | I:2–F:8 | A hi:67; E lo:0235; F hi:46; H lo:0125 | empty | empty |
| 5.5 | 8 | I:2–B:8 | A hi:56; B hi:67; H lo:0124; O lo:0234 | empty | empty |
| 5.6 | 8 | I:2–B:8 | A hi:56; B hi:67; E lo:0234; H lo:0123 | empty | empty |
| 5.7 | 7 | J:1–B:7 | A hi:568; B hi:468; D lo:012; L lo:013 | empty | empty |
| 5.8 | 7 | J:1–C:7 | C hi:468; D lo:012; E hi:356 | empty | empty |
| 5.9 | 7 | J:1–B:7 | A hi:568; B hi:368; D lo:012; K lo:014 | empty | empty |
| 5.10 | 8 | J:2–F:8 | A hi:67; F hi:46; H lo:0125; J lo:0135 | empty | empty |
| 5.11 | 8 | J:2–B:8 | A hi:56; B hi:67; H lo:0124; J lo:0134 | empty | empty |
| 5.12 | 8 | J:2–B:8 | A hi:56; B hi:67; H lo:0123; N lo:0134 | empty | empty |
| 5.13 | 7 | D:1–B:7 | A hi:568; B hi:468; D lo:012; E lo:013 | empty | empty |
| 5.14 | 7 | D:1–C:7 | A hi:568; C hi:468; D lo:012; K lo:013 | empty | empty |
| 5.15 | 7 | D:1–B:7 | B hi:368; D lo:012; O hi:456 | empty | empty |
| 5.16 | 8 | H:2–F:8 | A hi:67; E lo:0135; F hi:46; H lo:0125 | empty | empty |
| 5.17 | 8 | H:2–B:8 | A hi:56; B hi:67; H lo:0124; J lo:0134 | empty | empty |
| 5.18 | 8 | H:2–B:8 | A hi:56; B hi:67; E lo:0134; H lo:0123 | empty | empty |
| 8.1 | 8 | I:2–B:8 | A hi:56; B hi:67; G lo:0124; O lo:0234 | empty | empty |
| 8.2 | 8 | L:3–B:8 | B hi:7; D hi:6; L lo:0134 | 25 | 5 |
| 9.1 | 7 | G:1–B:7 | A hi:568; D lo:012; F hi:468 | 3 | 3 |
| 9.2 | 0 | A:0–M:4 | M hi:2356 | 1478 | empty |
| 14.1 | 7 | G:1–B:7 | A hi:568; D lo:012; F hi:468 | 3 | 3 |
| 16.1 | 8 | J:2–B:8 | A hi:56; B hi:67; L lo:0123; N lo:0134 | empty | empty |
| 16.2 | 8 | K:3–B:8 | A hi:6; B hi:7; K lo:0135 | 24 | 4 |

| Label | Pivot | Candidate partner | Partner endpoints | Reciprocal guard |
|---|---:|---:|---|---|
| 1.1 | 4 | 1 | A:1–P:6 | D lo:04 |
| 1.2 | 5 | 1 | A:1–P:6 | D lo:05 |
| 1.4 | 1 | 2 | A:2–O:6 | A lo:01 |
| 1.4 | 1 | 7 | L:3–B:7 | L lo:014 |
| 1.5 | 0 | 4 | H:1–K:6 | H lo:01 |
| 1.5 | 0 | 7 | D:2–B:7 | D lo:012 |
| 8.2 | 8 | 2 | D:1–L:6 | C hi:678 |
| 9.2 | 0 | 1 | G:0–K:5 | A lo:0 |
| 9.2 | 0 | 4 | H:0–F:5 | D lo:0 |
| 9.2 | 0 | 7 | M:2–B:7 | G lo:014 |
| 9.2 | 0 | 8 | I:2–B:8 | E lo:0124 |
| 16.2 | 8 | 2 | I:1–F:6 | F hi:678 |

## 6. Five parity exclusions

Each output interval contains four ranks. The displayed intersection has odd cardinality.

| Label | Forbidden Q edge | Minimum-output endpoints | Maximum-output endpoints | Intersection |
|---|---|---|---|---|
| 1.4 | `24` | H:0–B:3 | D:3–O:6 | 3 |
| 8.2 | `58` | K:2–A:5 | L:5–B:8 | 5 |
| 9.1 | `37` | G:1–J:4 | D:4–B:7 | 4 |
| 14.1 | `37` | G:1–E:4 | D:4–B:7 | 4 |
| 16.2 | `48` | D:2–C:5 | F:5–B:8 | 5 |

## 7. Fixed replay

The [checker](verify/h9_recovery_021536_endings_check.py) reads the fixed sixteen inputs, evaluates all31 displayed prefixes, and checks every endpoint, threshold guard, reciprocal guard, parity interval, and final matching contradiction. It also reads back the printed tables.
It uses no SAT solver, discovery import, search for inputs, or enumeration of nine-wire matchings. Its [result](results/h9-recovery-021536-endings-check.json) binds the certificate, note, and checker by hashes.
