# Integrated Mathathon report and audit package

- [Report PDF](report.pdf) and [single self-contained LaTeX source](report.tex)
- [21-slide presentation PDF](slides.pdf) and [editable Beamer source](slides.tex), preserving the collaborator's deck structure
- [Claim ledger](supplementary/claim-ledger.json): 21 statements, premises, exact evidence hashes, checks, and scope limits
- [Fresh verification results](supplementary/validation.json) and [finite replay transcript](supplementary/replay-log.txt)
- [Lean source and declaration mapping](supplementary/lean/README.md), [build log](supplementary/lean/lean-build.log), and [direct source-check log](supplementary/lean/lean-source-check.log)
- [Source provenance manifest](supplementary/source-manifest.json) and [deliverable manifest](supplementary/deliverable-manifest.json)
- [Build, replay, and collaborator integration instructions](HANDOFF.md)

The report is the authoritative synthesis for these frozen snapshots. The original research notes are retained as evidence and can describe earlier intermediate states. Appendix E gives the audit protocol; Appendix F expands structural proofs. Appendix G records the presentation background. [The slide-to-report map](supplementary/presentation-review.md) documents all 21 slides and the substantive consistency corrections. The second collaborator's explicit AKS parameter bound is integrated in Section 10.1, with its exact arithmetic audit and overlap review under `supplementary/asymptotic/`. The older Seiferas-style proposals retain their separate unfinished status.

From this directory, run `python3 supplementary/audit_package.py` to check evidence bindings, and `python3 supplementary/replay.py` to rerun selected finite certificates. Inside `supplementary/lean`, run `lake build` and `lake env lean SortingDepth.lean`. The present Lean results are two-layer removal and the halving recurrence. We plan to formalize all of the work.

All seven audited whole-case CNF/DRAT bundles are included. Their archived checker logs are historical; the package-integrity audit is not a new DRAT run. No competition submission has been performed.
