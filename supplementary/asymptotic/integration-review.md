# Comparison and audit of the second collaborator's parameter note

Source: `sorting_network_depth_bound.tex` at commit `65e9237800eb0e77f196b1fd4452db49d4577684`. The unchanged source bytes are archived as `../collaborator/sorting_network_depth_bound-source.txt` so the submission retains one report `.tex` file.

Compared against `main.tex` at `53034fa080e0b1014dc796281a515ce357765868`, unchanged in the new source commit, and the integrated report at `b619a0b0fb9c644a187236f9fd332ade606e11e6`.

## Overlap not added again

The definition of sorting depth, Batcher's baseline, general AKS background, and Chvatal's published coefficient 1830 were already in `main.tex`. The new note contains no new small-width lower bounds or 128/256/512/1024 constructions. Its result is separate from the Seiferas accounting issue, the approximately 281084 calculation, and the unreviewed approximately 6300 proposal. The new proof does not certify those older proposals.

## Distinct information integrated

- The theorem `D(N) <= (5236/3) log2(N) - 40651` for every integer `N >= 2^79`.
- Fixed parameters `k=64`, `A=2048`, `nu=1/32`, `M=2^59`, `mu=2^-28`, `delta_F=128/4095`, `epsilon_F=1/20000000`, `epsilon_B=467/10^10`, `delta=8/10^10`.
- The separator-shape table, including all 22 advancing-bottom cases, and the special root scramble.
- Rational bounds verifying separator quality and the five outsider-invariant inequalities.
- The parity-rounded stopping calculation, five residue classes, and exact comparator-depth accounting.

The new coefficient is smaller than 1830 by exactly 127/2745, about 4.6266%. This is a comparison with a specific published construction, not a global priority claim. The new full affine bound becomes smaller than Chvatal's `1830 log2(N)-58657` only when `log2(N)>27009/127`, approximately 212.67. The offset and validity range are therefore retained in the report and slides.

## Review against the original source

The source consulted is Chvatal, *Lecture Notes on the New AKS Sorting Network*, DCS-TR-294 (1992), DOI https://doi.org/10.7282/T379487B, author-hosted PDF https://users.encs.concordia.ca/~chvatal/aks.pdf. Its Section 3 definitions and Section 5 block formulas match the substitutions in the new note. Theorem 5.1 requires integer sizes with `m>=100`, `n>=16`, even `f>=10`, and `m=2f+kb`, along with the displayed quality conditions. These hold for nonempty fringes. For empty fringes, the bulk proof in Lemma 6.1 applies independently of fringe parameters; applying it to both orders and using a union bound supplies simultaneous bulk quality. Conditions (4.1)--(4.5) are those used in Lemma 4.5. The final `mu*delta*c<1` bound removes outsiders of order one and permits the parent-group final sort.

The construction uses fixed scrambles whose existence comes from the published probabilistic argument. No new explicit scramble wiring or simplified AKS architecture is claimed. The original paper is cited, not republished in this package.

## Fresh checks

`verify_chvatal_parameters.py` uses exact `Fraction` arithmetic, rational Taylor-series bounds, and integer parity rounding. It rederives the 25 separator shapes and maximal scaling exponents, checks all parameter constraints, exhausts the finite stopping residue calculation, and independently checks rounded meetings for 500 dimensions, `14<=d<=513`. The proof for all dimensions uses the period `d -> d+5`, `t_f -> t_f+17`, not extrapolation from these controls. `parameter-check.json` records the exact outputs and source/checker digests.

Status: the parameter application and proof have been checked against the cited hypotheses. This is not Lean verification, an independent reproving of Chvatal's separator theorem, or a test of an instantiated enormous network. The existing Lean verification scope remains two-layer removal and the halving recurrence.
