# Presentation consistency review

The active presentation is `../slides.tex` and its compiled `../slides.pdf`, with 21 slides and a 19 minute 10 second speaker-note budget. It adapts the collaborator's `slides_beamer.tex` at commit `53034fa080e0b1014dc796281a515ce357765868`. The original source is frozen at `collaborator/slides_beamer-source.txt`.

The sequence remains: introduction, research aims, three outcomes (lower bounds, AKS parameters, constructions), verification, lessons, and open problems. The existing palette, typography and illustrations are retained. The report is the authoritative mathematical record. Appendix G explicitly includes the introductory background so the slides do not add unstated mathematical claims.

| Slide | Topic | Report coverage | Consistency action |
|---|---|---|---|
| 1 | Cover | Sections 1, 11 | Retained cover and research framing; corrected model names in notes. |
| 2 | Sequential sorting | Appendix G | Retained introductory decision-tree explanation, made distinct-input assumption explicit. |
| 3 | Sorting networks | Section 2; Appendix G | Retained five-wire diagram and definitions. Appendix G describes its layers. |
| 4 | Batcher | Appendix G | Retained bitonic split and recursion diagram as prior work. |
| 5 | Approximate halvers | Appendix G | Added the k <= n/2 range to the rank guarantee. |
| 6 | Expander halvers | Appendix G | Retained drawing as a schematic, corrected explanation to discuss wires and binary monotonicity. |
| 7 | Landscape | Sections 1, 10.1; Appendix G | Limited numerical context to results stated in the report; retained the gap between simple and logarithmic-depth constructions. |
| 8 | Purpose | Sections 1, 8, 11 | Retained four research directions, corrected AI tool names and roles. |
| 9 | Outcomes | Sections 1, 2, 9, 10.1 | Replaced unsupported novelty claims with completed hand proofs, the new parameter theorem and verified finite upper bounds. |
| 10 | Halving lemma | Section 2.1; Appendix E.4 | Added n >= 3 and the precise Lean scope. |
| 11 | Halving proof | Section 2, Theorem 2.1 | Retained diagram and proof idea; clarified first-layer filling and signs. |
| 12 | Small bounds | Section 2; Corollary 2.2; Appendix A | Emphasized complete hand proofs through D(10). D(32) >= 11 uses a published depth premise and has no priority claim. |
| 13 | Pushing further | Sections 6, 7; Appendix F | Replaced unaudited 32-wire sample counts with the nine-row cycle argument, 26/50 H9 hand coverage and the exact D18 scope. |
| 14 | AKS tree | Section 10.1; Appendix G | Retained conceptual tree. Added termination and final local sorting rather than saying shrinking bags alone sort. |
| 15 | AKS constants | Sections 10.1, 10.2 | Replaced the placeholder with the checked bound, validity threshold and full-bound crossover. Older Seiferas proposals remain unverified. |
| 16 | Multiway merge | Section 9, Theorem 9.1 | Retained construction explanation and credited Lee--Batcher recursion. |
| 17 | Finite constructions | Section 9, Table 2 | Retained table and collaborator formula comparison. Removed global best-known wording. |
| 18 | Construction verification | Section 9.1 | Retained compositional proof idea and explicitly labelled the extra controls as historical, not rerun. |
| 19 | Negative results | Sections 3, 5, 8 | Used the audited layer-cap and blinding limitations and the recorded inconclusive D18 run. |
| 20 | Lessons and verification | Sections 2.1, 6.1, 8, 10.2; Appendix E | Used documented indexing/untangling/depth-unit issues and the verified Lean scope. |
| 21 | Open problems | Sections 1, 8; Appendix E.4 | Retained future-work ending and explicitly included the plan to formalize all results. |

The final PDF was rendered and every slide inspected. The final TeX build has no overfull boxes or font-substitution warnings. This is a Beamer/PDF deliverable, not a PowerPoint rendering. Numeric tables were compared with the report, and the notes identify evidence status and report locations. The separate mathematical replay and Lean logs retain their stated scopes.

The required report is still one self-contained `.tex` file with its PDF. The additional `slides.tex` is editable presentation source included as supplementary material. The repository-root `slides_beamer.tex` and `slides.pdf` match the active submission source and PDF. The previous 20-slide technical PowerPoint deck is superseded and is available in Git history.
