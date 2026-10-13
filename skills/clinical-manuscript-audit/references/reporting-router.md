# Reporting guideline router

Use study aim/design first. Pick one main guideline per component and appropriate extensions. Verify the latest version on the primary publisher or EQUATOR site for each new manuscript; journal-specific rules may add or narrow requirements. Reporting checklists improve transparency; they are **not** risk-of-bias instruments, proof of study quality, or a substitute for scientific peer review.

| Design or component | Main guide | Extensions/notes | Official source |
|---|---|---|---|
| Cohort, case-control, cross-sectional | STROBE | Use design-specific checklist. When routine electronic health, registry, claims, or administrative data underpin analyses, add RECORD. For pharmacoepidemiology with routinely collected data consider RECORD-PE. | https://www.equator-network.org/reporting-guidelines/strobe/ |
| Routine observational health data | RECORD plus STROBE | Report coding algorithms, population identification, dataset linkage, data completeness and access. | https://www.equator-network.org/reporting-guidelines/record/ |
| Routine-data pharmacoepidemiology | RECORD-PE with applicable RECORD/STROBE | Specify exposures, lags, washouts, treatment switching, confounding and ascertainment. | https://www.equator-network.org/reporting-guidelines/record-pe/ |
| Randomized controlled trial report | CONSORT 2025 | AI intervention: consider CONSORT-AI extension. Check eligibility, allocation, trial registrations, protocol/SAP, analyzed Ns, harms, protocol deviations. | https://www.bmj.com/content/389/bmj-2024-081123 |
| Trial protocol | SPIRIT 2025 | Use the protocol guideline, not the trial-results checklist alone. | https://www.equator-network.org/reporting-guidelines/ |
| Systematic review / meta-analysis | PRISMA 2020 | Protocol: PRISMA-P; other review types and extensions require lookup. Ensure correct effect metric, study selection, risk of bias, synthesis method, heterogeneity. | https://www.prisma-statement.org/prisma-2020 |
| Diagnostic accuracy | STARD 2015 | If AI-based index test, also use STARD-AI (2025); review spectrum, reference standard, blinding, missing/indeterminate tests. | https://www.equator-network.org/reporting-guidelines/stard/ |
| AI diagnostic accuracy | STARD-AI | Complements STARD 2015; reports dataset curation, test-set evaluation and algorithmic bias. | https://www.equator-network.org/reporting-guidelines/the-stard-ai-reporting-guideline-for-diagnostic-accuracy-studies-using-artificial-intelligence/ |
| Clinical prediction model (regression or ML) | TRIPOD+AI (2024) | Development/validation/updating; report calibration, discrimination, overfitting, data leakage, validation, fairness. Not simply any paper using regression. | https://www.bmj.com/content/385/bmj-2023-078378 |
| Health economic evaluation | CHEERS 2022 | Perspective, time horizon, model structure, costs, effects, discounting, uncertainty. | https://www.equator-network.org/reporting-guidelines/cheers/ |
| Qualitative research | SRQR or COREQ | Choose by design/method; interviews/focus groups may use COREQ. | https://www.equator-network.org/reporting-guidelines/ |
| Quality improvement | SQUIRE 2.0 | Context, improvement theory, study of intervention, mechanisms, sustainability. | https://www.equator-network.org/reporting-guidelines/squire/ |
| Case report | CARE | Case timeline, patient perspective/consent where applicable. | https://www.equator-network.org/reporting-guidelines/ |
| Animal experiment | ARRIVE 2.0 | Species, randomization, blinding, sample-size rationale, outcome definitions. | https://www.equator-network.org/reporting-guidelines/ |
| Mixed-methods or multi-component paper | Main component guideline + relevant secondary guide(s) | Record the reason for each choice; some manuscripts require two or more checklists. | https://www.equator-network.org/reporting-guidelines/ |

## Global overlays

- ICMJE recommendations, latest: https://www.icmje.org/recommendations/
- ICMJE statistics: https://icmje.org/recommendations/browse/manuscript-preparation/preparing-for-submission.html
- ICMJE AI disclosure: https://icmje.org/recommendations/browse/artificial-intelligence/ai-use-by-authors.html
- SAMPL statistical reporting: https://www.equator-network.org/reporting-guidelines/sampl/
- The EQUATOR library is continually updated: https://www.equator-network.org/reporting-guidelines/

## Router record (write in project notes)

1. What is the unit of analysis: patient, encounter, hospital, cluster, study, or model?
2. What is the primary research question: association, causal treatment effect, diagnostic test accuracy, prediction, evidence synthesis, implementation, or other?
3. What is the main design, sampling scheme, timing, and data source?
4. Are there secondary components (e.g., cohort + prediction model) that require additional guides?
5. Which version was checked, at what official URL, on what date, and does the journal request another version?
6. Which checklist items are inapplicable, why, and who approved that decision?

Never automatically label a statistical regression as prediction-model research, or an observational treatment comparison as a randomized clinical trial. Never reproduce or claim completion of a proprietary/third-party checklist without inspecting it.
