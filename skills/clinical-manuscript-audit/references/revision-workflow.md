# Major Revision & Reviewer Response — evidence-first workflow

Use this document when an editor requests **Major Revision**, **Minor Revision**, **revise and resubmit**, **reviewer response**, **rebuttal letter**, **返修**, **审稿意见回复**, or a later revision round. Keep it separate from first-draft creation; do not automatically rewrite the whole manuscript.

## Intake (never skip)

Ask for the original editor decision, ALL reviewer comments, submitted manuscript (including table/figure/supplement versions), prior response letters if R2+, and any already revised sections. Request source statistical outputs only for critiques that require them. The assistant may analyze partial materials but must visibly identify missing documents. Never infer reviewer comments from a summary. Redact patient identifiers and honor publisher embargo and institutional data policies.

1. Identify revision round (`R1`, `R2`, ...), deadline, journal response format and whether changes should be tracked/highlighted.
2. Reproduce *every* reviewer/editor comment as provided, with source (document and paragraph/page). Break multi-part comments into atomic requests but keep the unaltered original text and a stable source location. Mark uncertainty rather than pretending the extraction is complete. Obtain author confirmation that all comments were captured.
3. Generate a **comment matrix** using `references/revision-data-contract.md` as the data contract. Give IDs like `ED-R1-01`, `R1-01`, `R2-03` and retain IDs across discussions. Tag `major` based on scientific importance, not reviewer numbering alone.
4. Classify request: methods, statistics, interpretation, literature, reporting, figures, language, ethics, other. Select action: revise text, clarify without change, reanalyze, partially disagree, or disagree. Define evidence and author/biostatistician tasks for each.
5. Build a change plan **before** drafting a response. For requests requiring new statistical work, record requested analysis as `planned` until actually run and independently verified. Use manuscript result registry for actual new data. Avoid modifying planned analyses or inventing post hoc analyses; clearly label exploratory work.
6. Revise only the verified manuscript section(s). Keep source version, before/after excerpts, table/figure updates, change ID, final location and author verification. Do not fabricate page/line locations before final pagination.
7. Draft professional, courteous point-by-point responses. Quote reviewer text exactly and provide a direct answer, methodological reasoning, what was ACTUALLY changed, and specific manuscript location only if checked. Explicitly distinguish **completed**, **planned**, and **not feasible** analysis. Never turn plans into past tense.
8. For justified disagreement: acknowledge the underlying concern, explain the specific reason, substantiate it with design/data/literature, and, when helpful, clarify a potential misunderstanding in the manuscript. Avoid combative or evasive language. Resolve conflicting reviewer requests by explicit documented author decision, not silently choosing one.
9. Independently audit as clinical author, statistician, epidemiologist, and handling editor. Check statistics, interpretation, abstract/tables/supplement consistency, previous-round responses, and new bias introduced by changes. Run both existing manuscript audit when applicable and `revision_audit.py audit --stage submission`.
10. Generate response letter and optionally cover letter **only after verification**. Align each claim about completed actions with verified source changes and analyses. Human author checks every response; editor/journal requirements take precedence for format.

## Standard output for first pass

Generate one matrix, without attempting to bluff answers:

| ID | Exact reviewer text/source | Atomic concern | Scientific priority | Data or analysis needed? | Proposed response/decision | Target section | Verified evidence | Owner | State |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Then a prioritized plan grouped by **must analyze**, **must revise/clarify**, **reasoned disagreement**, and **format-only**. Ask author to approve disputed science and analysis scope.

## Detailed response letter convention

- Heading `Response to Reviewers — Round Rn`, editor first if applicable, then Reviewer 1, Reviewer 2, etc.
- Quote the **original comment verbatim** and address every independent request; maintain stable IDs.
- Write `Response:` with concise appreciation only when appropriate, then the scientific answer, verified actions and location. Optional `Revised text:` may quote the precise after-excerpt.
- If no change is justified, explicitly say so and show reasoning. Do not invent a modified location.
- If an analysis is still pending, label `[TO_VERIFY: analysis completion]` in INTERNAL draft and stop submission clearance.
- Do not imply the journal has accepted a rebuttal. Do not misrepresent new analyses as prespecified.

## Multi-round and conflicting comment rules

Keep prior rounds immutable in `revision_rounds.csv` and related registry rows. For a follow-up comment in R2/R3, link `prior_comment_ids` to original R1/R2 comments; for wholly new critiques mark `origin=new`. If two reviewers make conflicting requests, record both in `comment_conflicts.csv` plus a single, evidence-based resolution and author approval. Revisit prior round commitments before drafting a contradictory newer response.

## Submission gate

- Original comments and editorial requirements verified for completeness by human author.
- Every current-round comment has approved response, actual strategy, and resolved state.
- Every response claiming an actual manuscript change has a linked verified change and final location.
- Every response claiming a new analysis has a linked verified analysis output; statistical interpretation reviewed by human expert.
- Disagreements have substantive justifications; contradictions are resolved and approved.
- Line/page numbers checked against FINAL revised file; no placeholders.
- Correct journal style, editable marked-up manuscript, clean manuscript, tables/figures/supplement changes and editor letter as required.

## Scientific boundary

The CLI checks registry schema and links; it does not compare Word tracked changes, verify that uploaded decision letters were completely transcribed, independently rerun analyses, or establish the scientific quality of the response. Make limitations and open tasks explicit in every audit report.
