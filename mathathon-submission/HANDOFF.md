# Mathathon report and presentation

This is the integrated, reviewable version of the available work. The package is prepared for publication on the repository main branch. No competition submission has been performed.

- `report.tex` is the single self-contained report source, with embedded bibliography and appendices. `report.pdf` is its compiled 32-page output.
- `slides.pdf` has 18 presentation slides and 2 backup slides. The speaker notes in `slides.pptx` target 19 minutes 15 seconds, leaving room within the 20-minute talk limit. `source/slides.mjs` is the editable generator; the tables in the PowerPoint are native editable tables.
- `supplementary/claim-ledger.json` maps 20 claims to their dependencies, evidence hashes, replay commands, and limitations. Appendix E embeds the ledger and audit protocol in the report; Appendix F expands the cycle and short merger proofs.
- `supplementary/source-manifest.json` records exact source commits and SHA-256 hashes. `supplementary/validation.json` distinguishes fresh checks from historical evidence.
- The companion `mathathon-submission.zip` contains this directory, including the seven large CNF/DRAT certificate sets. Local caches and runtime dependencies are excluded.

## Integrated snapshots

Structural research: `7bcc462c92af6ea523cf2a79c03070dc4c21b770` (`codex/d18-structural`), incorporating the earlier hand-proof branch at `56723660f2644a22679b8c951407f6e65f7ac64c`.

Collaborator construction and AKS report: `53034fa080e0b1014dc796281a515ce357765868` (`origin/main`). Its constructions and available AKS analysis are incorporated. The original contributor source is retained as `supplementary/collaborator/main-source.txt`; it is historical input, not the submission report.

The committed structural follow-up is included. The H9 hand count is 26/50, and the complete-case counts are 4/117, 3/609, and 0/411. A selected five-layer exclusion does not close a whole two-layer case.

Lean formalization: `61d98e102ad40076908a487e9c808c8feb26402e` (`lean-repository`). Both `lake build` and `lake env lean SortingDepth.lean` passed. The two-layer removal and halving recurrence use only the standard axioms `propext`, `Classical.choice`, and `Quot.sound`. The arbitrary-k layer-cap theorem, H9, merger arguments, and SAT encoders are outside that formal scope. Sources, pinned dependencies, and logs are in `supplementary/lean`.

The report and slide 18 explicitly state the plan to formalize all of the team's work in Lean, while separating that goal from the two results already checked.

Run `python3 supplementary/audit_package.py` for byte-integrity checks; this does not run DRAT or verify encoders.

## Forthcoming contribution

The user confirmed that another collaborator will push the open-model AKS contribution. It is not yet integrated. The main edit locations are report Section 10, its status table, the abstract and Section 1 if the conclusions change, and slide 15. Update the AI contribution statement in Section 11 and slide 18 as appropriate. DeepSeek V4.1 Flash and KimiK3.1 Pro are credited using the model names supplied by the team.

For the incoming work, distinguish a proposed parameter optimization from a proved bound. Check separator construction, invariant, rounding, termination for all sizes, and conversion from stages to comparator layers. Preserve the exact source commit in the title block. Update slides only after their claims appear in the report. Avoid claiming new records without establishing the relevant prior-art comparison.

## Build and replay

From this directory, with a LaTeX installation:

```sh
mkdir -p ../.mathathon-build
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=../.mathathon-build report.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=../.mathathon-build report.tex
cp ../.mathathon-build/report.pdf report.pdf
```

The slide generator requires a Node runtime with `@oai/artifact-tool` available (the Codex bundled workspace runtime supplies it):

```sh
node source/export_slides.mjs
```

It writes `../.mathathon-build/slides-draft.pptx`. Review and finalize that file, then export to `slides.pdf` with PowerPoint or LibreOffice. The delivered PowerPoint was checked with the presentation skill's package, font, geometry, table, and re-import validators. Every final PDF page and slide was visually reviewed. An estimated table-height warning on slide 11 was checked against the rendered PDF; there is no overlap.

Run `python3 supplementary/replay.py` to repeat the selected finite checks and all four construction certificates. Python 3, NumPy, python-sat, and a C++17 compiler are required. The replay uses a disposable copy so archived evidence stays unchanged. It does not rerun the large SAT searches or DRAT checker. To repeat Lean verification, run `lake build` and `lake env lean SortingDepth.lean` inside `supplementary/lean`; dependencies are pinned in its lockfile. If NumPy and python-sat are in different Python environments, `MATHATHON_COMPONENT_PYTHON` can select the interpreter for the component control only. Historical absolute paths in old result files need relocation for those larger experiments.

## Submission requirements

The [official rules](https://competition.sair.foundation/competitions/mathathon/participant-rules) require the single report `.tex`, compiled report PDF, slides PDF, and any supplementary material in one ZIP or a repository at a full commit hash. Team identities and the repository link are confined to the report's title block; every slide claim is present in the report. The reported deadline is November 15, 2026, noon Pacific. This version is ready for team review and the forthcoming contribution, not a record of submission.
