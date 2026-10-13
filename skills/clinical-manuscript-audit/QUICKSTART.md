# Clinical Manuscript Writing & Scientific Audit

This package contains a reusable ChatGPT Skill and a local no-network audit CLI for manuscripts in clinical medicine, public health and epidemiology.

## Install into ChatGPT

For ChatGPT web **Plugin** upload, use `clinical-manuscript-chatgpt-plugin.zip` and ensure plugin-upload permission. For direct **Skill** upload in the Skills tab, use the standalone `skill.zip`. These are different package formats. The package contains one skill named `clinical-manuscript-audit`, including a `SKILL.md`, reference rubrics, blank project templates, and a Python checker.

## Start a manuscript project

Unzip the Skill package to a trusted local workspace, then run:

```bash
python clinical-manuscript-plugin/skills/clinical-manuscript-audit/scripts/manuscript_audit.py init --project my-study
```

Do not pass patient-level data or confidential study records into an external LLM or cloud service without institutional authorization. The blank templates contain no patient data.

Complete `my-study/study.json` and the CSV registries from source-verified results. Retain exact source table/figure/sheet references. Choose the study design based on the research question, not the statistical software used.

For iterative drafting:

```bash
python clinical-manuscript-plugin/skills/clinical-manuscript-audit/scripts/manuscript_audit.py audit --project my-study --stage drafting
```

For final human-controlled preflight:

```bash
python clinical-manuscript-plugin/skills/clinical-manuscript-audit/scripts/manuscript_audit.py audit --project my-study --stage submission
```

The report appears in `my-study/audit.md`. Exit code 2 indicates unresolved deterministic blockers; zero means no machine-detected blockers, **not** that the study or manuscript has been independently verified.

## Practical workflow with ChatGPT

1. Provide the study objective/design and de-identified summary data tables.
2. Ask the Skill to populate the study and result registry with explicit output locators.
3. Review the result registry before writing prose.
4. Have it draft Results and Methods first, then Introduction/Discussion and Abstract.
5. Use verified bibliographic sources and record which passage supports each claim.
6. Run the audit and resolve flagged problems with the statistician and author.
7. Complete the official reporting checklists and the journal's author instructions.
8. Obtain human signoff and AI-use disclosure before submission.

## Scope limitations

The bundled script is a schema / traceability / plausibility checker. It does not rerun statistical software, recompute trial effects, validate citations over the Internet, fully parse the manuscript, check the actual reporting checklist against every required official item, or grant IRB/ethics approvals. It cannot guarantee acceptance by a journal.

## Built-in tests

```bash
python -m unittest discover -s clinical-manuscript-plugin/skills/clinical-manuscript-audit/tests -v
```

The tests use invented, nonclinical data and are not evidence for any medical claim.

## Major Revision / Response to Reviewers (new in v1.1)

Provide the full editor decision, original reviewer comments, submitted manuscript, previous response letters for R2+, and verified results as needed. Ask the assistant to create an atomic Reviewer Comment Matrix **before** writing a rebuttal. Approve the change/analysis plan, then require verified manuscript modifications and source-traceable additional analyses. The final response letter must not describe uncompleted work as done.

For local deterministic cross-reference checks (not scientific validation), run:

```bash
python clinical-manuscript-plugin/skills/clinical-manuscript-audit/scripts/revision_audit.py init --project my-study
python clinical-manuscript-plugin/skills/clinical-manuscript-audit/scripts/revision_audit.py audit --project my-study --stage drafting
python clinical-manuscript-plugin/skills/clinical-manuscript-audit/scripts/revision_audit.py audit --project my-study --stage submission
python clinical-manuscript-plugin/skills/clinical-manuscript-audit/scripts/revision_audit.py render --project my-study --stage drafting
```

See `references/revision-workflow.md` and `references/revision-data-contract.md`. Renderer output is an **internal** draft and requires author approval and final location checks.
