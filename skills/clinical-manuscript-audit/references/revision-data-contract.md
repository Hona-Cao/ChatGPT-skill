# Major revision data contract (v1.1)

For each manuscript project keep a `/revision` subfolder. Its files are UTF-8 CSV/JSON and can be generated from Word/PDF review letters by the assistant **with author confirmation**. The local CLI never sends data to an external server.

## Files

- `revision_meta.json`: current_round, all_comments_captured, response_letter_author_approved, revision_locations_checked, journal_requirements_checked. Boolean flags are **human attestations**; don't set true on an AI guess.
- `revision_rounds.csv`: each R1/R2/R3 round, original decision letter location, received date, manuscript version, status `active|ready|submitted`.
- `review_comments.csv`: one row per independently answerable point. Preserve verbatim text, reviewer identity, and source paragraph/line; `atomic_request` is your interpretation and must not overwrite original text.
- `revision_changes.csv`: each actual substantive textual/table/figure/supplement modification, `before_excerpt`, `after_excerpt`, final manuscript file/version/location, linked comment IDs and human verification. A `planned`/`edited` change is **not** verified.
- `additional_analyses.csv`: new analysis or reanalysis requested by reviewers, its status `planned|running|completed_unverified|verified|not_feasible|cancelled`, output provenance and person who checked it. Do not use `verified` until source output exists and has been reviewed.
- `review_responses.csv`: exactly one entry per atomic comment, with response text, the action flags `claims_revision` and `claims_analysis` (`yes|no`), status `draft|ready_for_review|approved`, and approving author.
- `comment_conflicts.csv`: contradictions between comments or between review rounds, their grouped IDs, documented resolution and human approval. Leave header only if no conflicts exist.

## Reviewer comment fields

IDs should be unique across rounds: `ED-R1-01`, `R1-01`, `R1-02`, `R2-01` ... (their exact spelling is flexible but never change a released ID). `round` is `R1`, `R2`, etc. `origin` is `initial`, `new`, `followup`, or `editorial` (followup at R2+ must link `prior_comment_ids`). `category` = `methods|statistics|interpretation|literature|reporting|figures|language|ethics|other`; `priority` = `critical|major|minor`; `decision` = `pending|revise|clarify|reanalyze|partially_disagree|disagree`; `status` = `open|in_progress|resolved`. `requires_new_analysis` = `yes|no` for the **author-approved response plan**, not merely an analysis demanded by a reviewer. For reasoned disagreement with an infeasible/unnecessary requested analysis, use `no` and record the scientific rationale. Any related `analysis_ids` must refer to `additional_analyses.csv`. `conflict_id` links the conflict table if used. `rationale` is required for disagreement. For IDs separated within a field use a semicolon (`;`); always quote fields with CSV quoting when commas or newlines occur.

## Traceability example (fictional schema only)

`review_comments.csv`:

| comment_id | round | decision | requires_new_analysis | analysis_ids | status |
| --- | --- | --- | --- | --- | --- |
| R1-02 | R1 | reanalyze | yes | ANA-R1-01 | in_progress |

`additional_analyses.csv` must contain `ANA-R1-01` with output file, locator, and verified_by before status can be verified. `revision_changes.csv` would show `CHG-R1-03` linked to `R1-02`, with `verified_location` such as `Revised Manuscript v2, Results, lines 150-158` only after final line numbering was confirmed. `review_responses.csv` should initially say the work is ongoing, **not** "We have completed the additional analysis". The exact numerical results belong in the original `results.csv`, not ad hoc invented prose.

## Commands

Run from the skill folder:

```bash
python scripts/revision_audit.py init --project /path/to/my-study
python scripts/revision_audit.py audit --project /path/to/my-study --stage drafting
python scripts/revision_audit.py audit --project /path/to/my-study --stage submission
python scripts/revision_audit.py render --project /path/to/my-study --stage drafting
```

`init` will refuse to overwrite an existing `/revision` folder. The `audit` command writes `/revision/revision_audit.md`. Drafting reports incomplete work as warnings; submission reports unresolved tasks as blockers. `render` produces an **internal** draft letter from existing response text; it does **not** hallucinate answers. The letter is never an automatically certified final submission file. Render refuses to overwrite the existing letter unless `--overwrite` is supplied.

## Minimal completion criteria

Before a `submission` audit: fill original reviewer/editor texts, verify the collection is complete, approve exact comments and decisions, verify revisions + analysis outputs, check manuscript locations, approve each response, approve the overall letter, and check target journal requirements. A no-blocker machine report is **only a prerequisite** to human signoff, not a quality guarantee.
