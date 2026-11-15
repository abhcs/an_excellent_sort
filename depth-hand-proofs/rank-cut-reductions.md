# Rank-cut tests and smaller targets for D(13) and D(17)

**Status.** This note proves reductions, not the desired lower bounds.
The 12-wire auxiliary problem remains open in these experiments; the
16-wire problem has not been attempted. The [H9 proof](h9.md) has been
improved separately: all 43 formerly exhaustive ending checks now have
six-run hand certificates. Its earlier case enumeration remains necessary.
D(18) is still unresolved.

## Exact omission of weight levels

Let P be any standard comparator network and N a matching of adjacent
wires on 0,...,n-1. Label a binary weight level by its zero count z and set

    Z(N) = {z : 1 <= z < n and (z-1,z) is not in N}.

**Rank-cut theorem.** P;N sorts every input if and only if it sorts all
binary inputs with zero count in Z(N).

**Proof.** Necessity is immediate. At a tested level z, no comparator of N
crosses the zero/one cut of the sorted output. Every comparator therefore
has equal output bits, whose only predecessor is the same equal pair.
Consequently P itself sorts every input at that level.

At an omitted level z, the comparator (z-1,z) belongs to N. Matching
disjointness makes both neighboring levels z-1,z+1 tested, except for
the constant levels 0,n, which every standard network fixes anyway.
Given x with z zeros, flip one zero to one to obtain x+, and one one
to zero to obtain x-. Monotonicity gives

    0^(z+1) 1^(n-z-1) = P(x-) <= P(x) <= P(x+) = 0^(z-1) 1^(n-z+1).

Every position of P(x) outside z-1,z is correct. Preservation of weight
makes those two bits 01 or 10, and their comparator in N sorts them.
Apply the zero-one principle. ∎

This is an exact reduction for a specified final matching. It does not
assert that arbitrary weight subsets suffice or that every sorter has
one globally alternating final layer. The verifier checks the equivalence
on 5,810 combinations of arbitrary prefixes of length zero through three
and adjacent last layers, at widths three and four.

## A complete cover of endings

After redundant gates are removed, a sorting network's final layer is
adjacent. Add comparisons between adjacent idle wires until the matching
is maximal. This is safe because the new gates are disjoint from the
original final gates and act on an already sorted output. No middle
layer is filled.

For a cap a on each of the first two layers at even width n, choose

    L1 = {(s,s+1),(s+2,s+3),...,(s+2a-2,s+2a-1)}, s=(n-2a)/2.

Filling only the first layer up to a comparisons, then relabeling and
untangling, gives this form while preserving all layer sizes. This L1
is reflection invariant. Final matchings may therefore be quotiented
by reflection of the entire network. The completion is not required to
be self-dual. Later redundancy removal and final-layer padding preserve
the caps on the first two layers.

| Width | Adjacent matchings | Maximal matchings | Cases up to reflection |
|---|---:|---:|---:|
| 6 | 13 | 4 | 3 |
| 8 | 34 | 7 | 5 |
| 10 | 89 | 12 | 8 |
| 12 | 233 | 21 | **13** |
| 16 | 1,597 | 65 | **37** |
| 18 | 4,181 | 114 | 63 |

[The cover check](results/thin-ending-cover-checks.json) independently
verifies that every adjacent matching extends a representative or its
reflection. The hand argument establishes why the cover suffices.

## The two auxiliary statements

Let T(r,a) be the least depth of an r-wire sorter with at most a
comparators in each of its first two layers. The hand transfer theorem
in [extension.md](extension.md), with one signed infinity, gives

    D(2p+1) >= T(2p,p-1).

The infinity can be chosen to meet one comparator in each of the first
two layers, unless the second layer already has at most p-1 comparators.
Pruning leaves 2p reals, at most p-1 comparisons in each of those layers,
and no increase in depth. The transfer proof handles every second-layer
matching and the renumberings introduced by pruning.

Thus these **unproved auxiliary statements** would suffice:

* T(12,5)>=9 would give D(13)>=9. It has 13 ending cases at depth eight.
* T(16,7)>=10 would give D(17)>=10. It has 37 ending cases at depth nine.

A sorting witness at either excluded depth would disprove that proposed
auxiliary statement, not the known value of D(13) or D(17).

## Validation and actual results

`verify/thin_layers_endings.py` fixes N and encodes only zero counts in
Z(N), using the shared-ending SAT model. Nonredundancy in the first free
layer is computed from the **full** first-layer image, not the tested
subset. Every SAT witness is checked independently on all 2^n inputs
and against both layer caps.

The [calibration](results/thin-ending-checks.json) refutes all three
ending cases for T(6,2)<=5 and all five for T(8,3)<=6. At depth six,
each six-wire ending case has a full verified sorting witness. These
controls accompany the 5,810 rank-cut equivalence checks.

For T(12,5)<=8, **all 13 trials reached their 15-second limits**. A
90-second CaDiCaL retry of case 0 also timed out, as did a 180-second
Kissat retry of case 10, whose ending is the pattern of the locally
verified 12/40/8 sorter. See the
[13-case audit](results/thin12-d8-endings-attempt1/audit.json) and
[retry audit](results/thin12-d8-endings-cadical/audit.json), and
[case-10 audit](results/thin12-d8-endings-case10-180s/audit.json).
No case is closed. The formulas encode 479–639 unsorted prefix outputs,
using approximately 26,000–34,000 variables and 437,000–579,000 clauses.
The 37 sixteen-wire cases have not been attempted in this run.

Child processes enforce hard wall limits. Manifests record the case list
and source hashes; timeouts never count as refutations. No independently
checked DRAT/LRAT proof trace is claimed.

From the private worktree, using a Python environment with python-sat:

```bash
python depth-hand-proofs/verify/thin_layers_endings.py --check \
  --out /private/tmp/thin-ending-checks.json
python depth-hand-proofs/verify/thin_layers_endings.py \
  --n 12 --depth 8 --cap 5 --seconds 15 --solver kissat404 \
  --out /private/tmp/thin12-fresh-attempt
python3 depth-hand-proofs/verify/h9_ending_certificates.py --verify \
  depth-hand-proofs/results/h9-ending-certificates.json
```
