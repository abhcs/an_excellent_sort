# Mathathon report and presentation

This is the integrated, reviewable version of the available work. The package is prepared for publication on the repository main branch. No competition submission has been performed.

- `report.tex` is the single self-contained report source, with embedded bibliography and appendices. `report.pdf` is its compiled 37-page output.
- `slides.pdf` has 21 presentation slides. `slides.tex` is the editable Beamer source, adapted from the collaborator's `slides_beamer.tex` while retaining its sequence, palette and illustrations. Its speaker notes target 19 minutes 10 seconds. The repository-root `slides.pdf` is byte-identical to this PDF, and `slides_beamer.tex` matches this source.
- `supplementary/claim-ledger.json` maps 21 claims to their dependencies, evidence hashes, replay commands, and limitations. Appendix E embeds the ledger and audit protocol in the report; Appendix F expands the cycle and short merger proofs.
- `supplementary/source-manifest.json` records exact source commits and SHA-256 hashes. `supplementary/validation.json` distinguishes fresh checks from historical evidence.
- The companion `mathathon-submission.zip` contains this directory, including the seven large CNF/DRAT certificate sets. Local caches and runtime dependencies are excluded.

## Integrated snapshots

Structural research: `7bcc462c92af6ea523cf2a79c03070dc4c21b770` (`codex/d18-structural`), incorporating the earlier hand-proof branch at `56723660f2644a22679b8c951407f6e65f7ac64c`.

Collaborator construction and AKS report: `53034fa080e0b1014dc796281a515ce357765868` (`origin/main`). Its constructions and available AKS analysis are incorporated. The original contributor source is retained as `supplementary/collaborator/main-source.txt`; it is historical input, not the submission report.

The committed structural follow-up is included. The H9 hand count is 26/50, and the complete-case counts are 4/117, 3/609, and 0/411. A selected five-layer exclusion does not close a whole two-layer case.

Lean formalization: `61d98e102ad40076908a487e9c808c8feb26402e` (`lean-repository`). Both `lake build` and `lake env lean SortingDepth.lean` passed. The two-layer removal and halving recurrence use only the standard axioms `propext`, `Classical.choice`, and `Quot.sound`. The arbitrary-k layer-cap theorem, H9, merger arguments, and SAT encoders are outside that formal scope. Sources, pinned dependencies, and logs are in `supplementary/lean`.

The report and slide 21 explicitly state the plan to formalize all of the team's work in Lean. Slides 10 and 20 describe the two results already checked.

Run `python3 supplementary/audit_package.py` for byte-integrity checks; this does not run DRAT or verify encoders.

## Integrated second collaborator contribution

The distinct parameter theorem from `sorting_network_depth_bound.tex`, commit `65e9237800eb0e77f196b1fd4452db49d4577684`, is integrated in report Section 10.1 and slide 15. It gives `D(N) <= (5236/3) log2 N - 40651` for `N >= 2^79` using Chvatal's existing construction. Claim C21, check R15, and `supplementary/asymptotic/integration-review.md` document the new information, overlap with `main.tex`, imported premises, and fresh arithmetic checks.

The coefficient is about 4.63% below Chvatal's 1830; the full affine bound improves his only above `log2 N = 27009/127`. The separate Seiferas-style 281084 and 6300 proposals remain uncertified. No new simple AKS architecture, global priority, or Lean verification of the asymptotic theorem is claimed.

For future additions, update the precise claim, dependencies, source commit, and evidence hashes together. The report is the authoritative synthesis. Root-level collaborator reports remain source material; the revised root Beamer deck matches the submission deck. All slide claims must continue to appear in the report.

## Build and replay

From this directory, with a LaTeX installation:

```sh
mkdir -p ../.mathathon-build
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=../.mathathon-build report.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=../.mathathon-build report.tex
cp ../.mathathon-build/report.pdf report.pdf
```

Compile the slides from this directory with a TeX installation that includes Beamer, IBM Plex Sans, EB Garamond, TikZ and tcolorbox:

```sh
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=../.mathathon-build slides.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=../.mathathon-build slides.tex
cp ../.mathathon-build/slides.pdf slides.pdf
```

The report remains one self-contained report source. The separate `slides.tex` is supplementary editable presentation source; the required presentation deliverable is `slides.pdf`. Both compiled outputs were inspected visually. The final slide build has no overfull boxes or font-substitution warnings. `supplementary/presentation-review.md` maps every slide to the report and records the major corrections. The earlier technical PowerPoint deck is superseded and remains available in Git history, not as a second active submission deck.

Run `python3 supplementary/replay.py` to repeat the selected finite checks and all four construction certificates. Python 3, NumPy, python-sat, and a C++17 compiler are required. The replay uses a disposable copy so archived evidence stays unchanged. It does not rerun the large SAT searches or DRAT checker. To repeat Lean verification, run `lake build` and `lake env lean SortingDepth.lean` inside `supplementary/lean`; dependencies are pinned in its lockfile. If NumPy and python-sat are in different Python environments, `MATHATHON_COMPONENT_PYTHON` can select the interpreter for the component control only. Historical absolute paths in old result files need relocation for those larger experiments.

## Submission requirements

The [official rules](https://competition.sair.foundation/competitions/mathathon/participant-rules) require the single report `.tex`, compiled report PDF, slides PDF, and any supplementary material in one ZIP or a repository at a full commit hash. Team identities and the repository link are confined to the report's title block; every slide claim is present in the report. The reported deadline is November 15, 2026, noon Pacific. This version is ready for team review and future contributions, not a record of submission.
