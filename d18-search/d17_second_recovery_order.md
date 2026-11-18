# A nine-wire seven-layer sorter needs three gates in its second layer

This reconstruction separates a hand reduction from two small residual
SAT statements. Both residuals now have independently checked certificates.
Full H9 remains an explicit premise:
a nine-wire sorting network of depth seven cannot have at most three
gates in each of its first two layers. This is not a complete hand proof
of H9 or D17.

## 1. The hand reduction has only two product images left

Let M,N be the first two layers and suppose |N| <= 2. If |M| <= 3,
H9 immediately excludes the network. Otherwise |M|=4.

If |N| <= 1, at most two M-gates meet N. Move any disjoint M-gate
forward into N. The new counts are (3, at most2), contradicting H9.
If |N|=2 and an M-gate avoids N, the same move gives (3,3).

It remains that all four M-gates meet N. The four endpoints of N must
then touch exactly one endpoint of each M-gate. In particular the idle
wire is untouched, no N-gate repeats an M-gate, and each N-gate joins
two different M-pairs. The interaction graph is exactly two disjoint
four-vertex paths and a singleton. Each path has two M-gates and one
N-gate. Call the two endpoints of an M-gate its lower and upper roles.

If either path's N-gate joins opposite roles, its image is the four-wire
N-poset from [the first-layer theorem](d17_feedback_round10_order.md).
That theorem gives explicit fixed-permutation image identities between
the schedules (2,1) and (1,2). Reschedule this one component. The other
component is independent, so the product image is unchanged up to a
fixed output permutation. Absorb that permutation into the suffix and
untangle, exactly as in the cited proof. The first two counts become
(3,3), again excluded by H9.

Thus both remaining paths join the same roles. A lower--lower join has
type U; an upper--upper join has its dual type D. Interchanging the two
components identifies UD with DU. Global value reversal and reversal
of wire order identify UU with DD. Only UU and UD remain.

## 2. Exact same-role images, with real preimages

The canonical U prefix is

    01 23 | 02.

Its image consists exactly of the vectors y satisfying

    y0 <= y1, y2, y3,       y2 <= max(y1,y3).       (U)

Indeed, after the first pairs let a<=b and c<=d. The outputs are
(min(a,c), b, max(a,c), d), which satisfy (U). Conversely:

* If y2<=y3, use input (y0,y1,y2,y3).
* If y2>y3, (U) implies y2<=y1; use input (y2,y1,y0,y3).

In both cases the first pairs are ordered and comparison02 returns y.
These preimages work for arbitrary real values, including ties. The
disjunction in (U) is essential: the image is smaller than its ordinary
pairwise-order hull.

The canonical D prefix is

    01 23 | 13.

Its image consists exactly of z satisfying

    z0,z1,z2 <= z3,         min(z0,z2) <= z1.        (D)

If z0<=z1, use input z. Otherwise the second condition forces z2<=z1;
use (z0,z3,z2,z1). Again the first pairs are ordered and comparison13
returns z. Equivalently, z_i=-y_(3-i) exchanges the two image formulas.

Any physical four-path with a same-role join is a fixed coordinate
permutation of one of these images. Name the two M-pairs by their roles
and send the smaller N-output to the canonical smaller N-output; this
identifies all four coordinates. Products inherit a uniform coordinate
permutation because the components are independent.

## 3. The two finite closure statements

The canonical nine-wire prefixes are

    UU: 01 23 45 67 | 02 46,      wire8 idle;
    UD: 01 23 45 67 | 02 57,      wire8 idle.

It suffices to show that neither admits a five-layer sorting suffix.
For each, the encoder uses every unsorted binary image of the prefix.
The zero-one principle therefore establishes the full real statement.
Only the established last-two-layer normal form phi1--phi4 is used;
self-duality, co-saturation, lexicographic constraints and early
nonredundancy restrictions are all disabled.

The source, exact CNF, proof and independent checker records are saved
under `d17_second_recovery_*` and `results/d17-second-recovery-*`.
Both fresh runs returned UNSAT and passed DRAT checking. Each solve and
each proof check had its own ten-second wall bound; all jobs are terminal.

| Residual | Variables | Clauses | Solver process | DRAT check |
|---|---:|---:|---:|---:|
| UU | 3,347 | 35,837 | 0.345 s | 0.427 s |
| UD | 3,299 | 34,895 | 0.228 s | 0.163 s |

The [batch record](results/d17-second-recovery-batch.json) binds the CNF,
proof, encoder, worker, checker source and checker binary hashes. The
[replay checker](d17_second_recovery_check.py) reconstructs both CNFs
byte-for-byte, checks the real-image formulas on finite order and tie
controls, and enumerates all415 possible second matchings of size at
most two after the canonical four-gate first matching. The hand proof
above, rather than that enumeration, establishes the universal reduction.

The two checked finite statements and exhaustive hand reduction prove
|N|>=3. Combined with the already established first-layer bound
|M|>=3 and H9's peak-four condition, the only first-two count profiles
for a seven-layer nine-wire sorter are (3,4), (4,3), and (4,4).

For a signed restriction leaving nine arbitrary real tracks after two
blind layers in a depth-nine seventeen-wire sorter, this means each
of physical layers3 and4 must contain at least three real--real gates.
This necessary condition applies simultaneously to every such signed
restriction. No new seventeen-wire cover case is claimed in this note.
