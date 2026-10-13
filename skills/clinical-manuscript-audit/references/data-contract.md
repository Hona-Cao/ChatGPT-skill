# Data contract for one manuscript project

Project files are intentionally **not** bundled with any patient-level data. The skill's `init` command creates blank templates. Use UTF-8 CSV with a header row. Keep the original source files separately, in authorized storage, and store a human-readable locator in `source_location`.

## study.json

- `study_id`: stable opaque project ID (no patient identifiers).
- `title`, `objective`, `population`, `main_outcome`, `target_journal`: sourced text or empty pending details.
- `primary_design`: one of `cohort`, `case_control`, `cross_sectional`, `rct`, `systematic_review`, `diagnostic_accuracy`, `prediction_model`, `economic_evaluation`, `qualitative`, `quality_improvement`, `case_report`, `animal`, `mixed_methods`, `other`. Leave empty when uncertain, then resolve at intake.
- `secondary_components`: zero or more of the above to invoke additional checklists when truly applicable.
- `routine_health_data`, `pharmacoepidemiology`, `ai_diagnostic`, `ai_intervention`, `protocol_only`: booleans affecting guideline extensions.
- `analysis_software`: array of software names and versions as documented, e.g. `["Stata 18", "R 4.4.2"]`; an empty array is valid during drafting, but version evidence should be recorded before submission.
- `analysis_plan_status`: `confirmed`, `partial`, or `unknown`.
- `data_handling_confirmed`, `human_signoff`: booleans; mark true **only after actual authorization/signoff**. `human_signoff` cannot be set by AI.

## results.csv

Required headings:

`result_id,role,source_file,source_location,population,outcome,comparison,model,effect_measure,estimate,ci_lower,ci_upper,ci_level,p_value,sample_n,events_n,denominator_n,timepoint,adjustment_set,prespecified,notes`

- `result_id`: unique stable ID e.g. `RES-001`.
- `role`: `primary`, `secondary`, `exploratory`, `sensitivity`, `descriptive`, `subgroup`.
- `source_file` and `source_location`: an author-accessible table/figure/output, plus exact sheet/page/cell/row or model block.
- `effect_measure`: examples `OR`, `RR`, `HR`, `IRR`, `PR`, `RD`, `MD`, `SMD`, `BETA`, `CORR`, `AUC`, `SENS`, `SPEC`, `OTHER`; empty for counts.
- `estimate`, `ci_lower`, `ci_upper`, `p_value`: numeric text (P may be `0.034`, `<0.001`, or `>0.99`), blank where not applicable.
- `ci_level`: percent, e.g. `95`; blank when no CI.
- `sample_n`, `events_n`, `denominator_n`: nonnegative integer where applicable; empty is not the same as 0.
- `prespecified`: `yes`, `no`, or `unknown`; never invent a plan.

## claims.csv

Required headings:

`claim_id,section,claim_type,claim_text,result_ids,reference_ids,status,notes`

- `claim_type`: `result`, `literature`, `inference`, `method`.
- `result_ids`, `reference_ids`: use `|` between multiple IDs (`RES-001|RES-003`).
- `status`: `draft`, `evidence_checked`, `approved`. Only human authors assign `approved`.
- Internal draft uses `[R:RES-001]` / `[REF:REF-001]` markers; the claim registry records substantive support and must be checked against text.

## references.csv

Required headings:

`reference_id,title,doi,pmid,source_url,verification_status,verified_passage,notes`

- `verification_status`: `pending`, `verified`, `rejected`.
- `verified` requires author/authorized tool review of an **actual relevant passage**, captured in `verified_passage`; title + DOI alone cannot establish claim support.
- Use stable DOI, PMID or resolvable source URL (some legitimate documents have no DOI).

## reporting_checklist.csv

Required headings:

`guideline,item_id,status,manuscript_location,notes,official_url`

- Each applicable **official checklist** item is separately entered from the source, not generated from memory.
- `status`: `present`, `missing`, `not_applicable`, `pending`. `not_applicable` requires a documented reason.
- `manuscript_location`: actual manuscript section/paragraph or page/line once finalized.
- Required guidelines returned by the router are only suggestions; the investigator checks the current checklist/extension and journal rules.

## Files produced by the CLI

- `audit.md` - machine-checkable flags and routing suggestions; not a methodological peer-review certificate.
- The manuscript itself remains a human-authored/approved document and is not automatically invented by the CLI.

## Recommended project structure

```
study-project/
  study.json
  results.csv
  claims.csv
  references.csv
  reporting_checklist.csv
  manuscript/
    draft.md
  audit.md
```

## Ingestion of other software

- SPSS: export pivot tables/selected output as CSV (or manually transcribe validated estimates), retain output table title and source.
- Stata: export frames / collected results with `export delimited`, keep estimation command and model label.
- R: export tidy output using `write.csv()` with unit/estimate metadata; keep analysis code location.
- SAS: PROC EXPORT for selected output tables, keep procedure settings and model contrasts.
- Python: `DataFrame.to_csv(index=False)`; preserve code/version and transformation provenance.
- Excel/Word/PDF: parse through file-handling tools then **human-check** against source before populating the registry.

Normalization is **not re-analysis**. If a source result cannot be represented unambiguously, retain it in `notes` and escalate for a statistician to interpret.
