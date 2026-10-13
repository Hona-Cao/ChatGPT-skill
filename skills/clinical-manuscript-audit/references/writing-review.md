# Evidence-grounded manuscript authoring and independent peer review

## Drafting order and constraints

1. **Results first**: organize around primary outcome -> secondary -> prespecified subgroups -> sensitivity/exploratory. Make each scientific statement map to `[R:RES-...]` and the corresponding row in `results.csv`; include adjusted/unadjusted, time point and uncertainty. No interpretation beyond source data.
2. **Methods second**: describe only what was actually done, using protocol, SAP, code or investigator-confirmed notes. Describe design, setting, recruitment, outcome/exposure definitions, measurement, missing-data approach, models, software/version, confounding adjustment and sensitivity analyses.
3. **Introduction third**: evidence-backed background -> uncertainty/gap -> clinical/public-health relevance -> objective. Use checked source passages and `[REF:REF-...]`. Do not overstate novelty.
4. **Discussion fourth**: (a) concise main findings, (b) contrast with strongest corroborating and dissenting literature, (c) plausible mechanisms as **hypotheses**, (d) strengths/limitations and likely bias direction when defensible, (e) implications and warranted next steps, (f) restrained conclusion. Never spin non-significant outcomes into proof of equivalence.
5. **Abstract last**: trace every number to results registry; align with Methods, Results, and main conclusion. Check abstract-specific journal/reporting guideline items.
6. **Polish last**: remove redundant claims, maintain terminology/tense, use precise medical English. Preserve all source numbers and scientific qualifiers.

## Claim-evidence alignment

- `claim_type=result`: at least one `result_id` that actually supports it, plus traceable table/source location.
- `claim_type=literature`: at least one verified `reference_id` with checked relevant passage; a paper's existence is not proof of the sentence.
- `claim_type=inference`: relevant results or verified literature plus explicit uncertainty and reasoning, with no stronger claim than the evidence allows.
- `claim_type=method`: protocol/code/researcher-confirmed source; do not create methods from textbook norms. Record context in `claims.csv` notes or study protocol.
- `status=approved` means a human author has checked the claim, **not** that an LLM approved it.

## Independent review template

For each reviewer role, report:

| Field | Meaning |
|---|---|
| issue_id | Stable review ID |
| reviewer_role | Clinician, epidemiologist, statistician, or journal reviewer |
| severity | BLOCKER, WARNING, INFO |
| finding | Specific sentence/table/analysis and what is wrong or uncertain |
| source | Result ID, source output, guideline item or paper passage |
| corrective_action | Narrowest evidence-preserving fix or required re-analysis |
| owner | Author/statistician/librarian/PI |
| status | OPEN, IN_REVIEW, RESOLVED with evidence |

Reviewer prompts:

- Clinician: Is the effect clinically meaningful? Does baseline risk, outcome definition and treatment context justify the language?
- Statistician: Are estimation, precision, multiplicity, missingness, adjustment, and model assumptions reported credibly?
- Epidemiologist: Could bias/confounding or design invalidate the interpretation? Are target population and generalizability honest?
- Editor: Does each reporting item have a location? Are ethics/registration/conflicts/data/AI disclosures and abstract congruent?

## Release protocol

- Submission stage requires zero BLOCKER flags and review of WARNING issues; open human signoff remains compulsory.
- Remove `[R:...]`/`[REF:...]` anchors only from clean export after registry checks; replace `[REF:...]` with journal-compatible verified citations before submission. Do not silently delete support markers in source draft.
- Report what was not audited: e.g., raw-data calculations, external full-text verification, ethics committee records, plagiarism screening, journal style checks.
- Document tools used, AI-assisted writing stages, human editorial oversight, and disclosures per current ICMJE and journal policy.
