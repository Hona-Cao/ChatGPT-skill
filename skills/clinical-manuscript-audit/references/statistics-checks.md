# Statistical and epidemiological review rubric

Apply each relevant check to the source analysis outputs, protocol, manuscript, and result registry. Record **observed evidence**, severity, and who should resolve discrepancies. Automated flags only detect limited inconsistencies.

## Every analysis

1. Identify estimand/question, effect-measure definition, population, comparator, time horizon, outcome and direction of benefit/harm.
2. Verify N and denominators by analysis and time point; missingness and exclusions; eligible/recruited/analyzed consistency; cluster count when relevant.
3. Separate descriptive, unadjusted, adjusted, primary, secondary, exploratory, subgroup and sensitivity analyses.
4. Check statistical test/model matches variable types and dependence structure, model assumptions, units, coding/referent, interaction terms, and multiplicity approach where relevant.
5. Report effect size and uncertainty where applicable. Differentiate CI from prediction interval and SD/SE. Do not calculate absent CIs from incomplete information.
6. Cross-check estimate, confidence limits, P value, model identity and null value. Apparent disagreement may arise from different tests/CI methods, transformations, or multiplicity adjustments: **flag, never silently correct**.
7. Verify missing data handling (complete-case, multiple imputation, inverse probability weighting, etc.), and avoid implying MAR/MCAR without grounds.
8. Distinguish scientific/clinical relevance from P<0.05; note imprecision, multiple testing, power and confidence limits; do not infer equivalence from non-significance.
9. Verify software/package and version when available, thresholds and pre-specified analysis plan; label unknown information accurately.

## Effect-measure pitfalls

- OR reflects odds, not directly risk; do not write "40% higher risk" for OR 1.40 unless converting via well-grounded baseline risk.
- HR is an instantaneous hazard ratio under model assumptions, not 1 - survival probability and not a risk ratio; review proportional-hazards assumption as applicable.
- RR, RD, IRR, PR, MD, SMD, AUC, sensitivity and specificity measure different things. Preserve correct units, reference group, denominator and period.
- For effect intervals, first establish null value: 1 for common ratio measures, 0 for differences; not a valid universal rule for AUC, sensitivity or specificity.
- P values of 0.000 must not be reported as exactly 0; use an appropriate threshold. Avoid inferring direction/significance from P alone.

## Design-specific probes

**Observational:** selection and information bias, temporality, residual confounding, collider control, immortal-time bias, reverse causality, attrition, measurement error, unmeasured confounding, positivity, propensity-score balance, and causal-language boundaries.

**Survival/time-to-event:** origin and start of risk, censoring, competing risks, follow-up duration, hazards assumptions, number-at-risk, lost-to-follow-up, and absolute risk at meaningful horizons.

**RCT:** random sequence, concealment, protocol deviations, ITT vs per-protocol analysis, clustering, interim analyses, loss to follow-up, harms, multiplicity and preregistration consistency.

**Cross-sectional/survey:** probability sampling, response rate, weighting, clustering/stratification, finite-population treatment if relevant, age standardization, nonresponse, prevalence vs incidence.

**Prediction:** development vs external validation, separation/leakage, events-per-parameter context, optimism correction, calibration (not AUC alone), decision utility and subgroup transportability.

**Diagnostic:** 2x2 counts/denominators, reference standard, index threshold setting, sensitivity/specificity with CIs, disease spectrum, verification and incorporation bias, equivocal/missing results.

**Meta-analysis:** study-level effects and uncertainty, heterogeneity, pooled method and weights, risk-of-bias approach, subgroup and publication bias analyses, certainty of evidence.

**Economic evaluations:** costs and utilities, perspective, horizon, discounting, uncertainty, model inputs and assumptions, incremental cost-effectiveness and scenarios.

## Severity

- **BLOCKER:** known false statistics, impossible sample accounting, unsupported causal claims, fabricated source/method, unapproved protocol change, or unverified core reference used as established fact. Resolve before submission.
- **WARNING:** potentially different P/CI calculations, unclear modeling choices, CI omission, substantial missingness without explanation, incomplete checklist, weak evidence or unresolved reviewer question. Escalate to statistician/PI.
- **INFO:** optional style and presentation recommendations; never hide them as statistical errors.

Use a separate human methods review to assess appropriateness. An internal consistency check does not establish correctness of analysis, raw-data quality, or causal validity.

## Methodological appraisal is distinct from reporting completeness

Select a **separate risk-of-bias or quality appraisal** framework when appropriate, but do not treat a reporting checklist as proof of study validity. These tools are typically designed for specific review questions or effect estimates, so use them with domain-expert oversight:

- Randomized intervention results: RoB 2 (https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-08).
- Nonrandomized studies of **intervention effects**: ROBINS-I (https://methods.cochrane.org/bias/risk-bias-non-randomized-studies-interventions). As of October 2026, the published ROBINS-I V2 material is still labeled draft; verify version before use. Do not apply ROBINS-I indiscriminately to descriptive cross-sectional studies.
- Prediction model development/evaluation: PROBAST+AI (2025), which separately addresses development quality and evaluation risk of bias (https://www.bmj.com/content/388/bmj-2024-082505).
- Diagnostic test accuracy study appraisal in a systematic-review context: QUADAS-3 (2026; https://doi.org/10.7326/ANNALS-25-02104). Distinguish primary-study reporting with STARD from secondary-review risk-of-bias appraisal.
- For reviews making confidence-in-evidence statements, consider the applicable GRADE framework, not just a pooled P value.

Do not automatically score or assert a low risk of bias from manuscript text. Record the assessors, source evidence, unresolved questions and uncertainty for every material judgment.
