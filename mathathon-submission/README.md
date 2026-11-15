# Integrated Mathathon report and audit package

- [Report PDF](report.pdf) and [single self-contained LaTeX source](report.tex)
- [Presentation PDF](slides.pdf), [editable PowerPoint](slides.pptx), and [slide generator](source/slides.mjs)
- [Claim ledger](supplementary/claim-ledger.json): statements, premises, exact evidence hashes, checks, and scope limits
- [Fresh verification results](supplementary/validation.json) and [finite replay transcript](supplementary/replay-log.txt)
- [Lean source and declaration mapping](supplementary/lean/README.md), [build log](supplementary/lean/lean-build.log), and [direct source-check log](supplementary/lean/lean-source-check.log)
- [Source provenance manifest](supplementary/source-manifest.json) and [deliverable manifest](supplementary/deliverable-manifest.json)
- [Build, replay, and collaborator integration instructions](HANDOFF.md)

The report is the authoritative synthesis for these frozen snapshots. The original research notes are retained as evidence and can describe earlier intermediate states. Appendix E gives the audit protocol; Appendix F expands structural proofs. The open-model AKS contribution remains pending.

From this directory, run `python3 supplementary/audit_package.py` to check evidence bindings, and `python3 supplementary/replay.py` to rerun selected finite certificates. Inside `supplementary/lean`, run `lake build` and `lake env lean SortingDepth.lean`. The present Lean results are two-layer removal and the halving recurrence. We plan to formalize all of the work.

All seven audited whole-case CNF/DRAT bundles are included. Their archived checker logs are historical; the package-integrity audit is not a new DRAT run. No competition submission has been performed.
