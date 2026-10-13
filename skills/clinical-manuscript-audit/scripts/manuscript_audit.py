#!/usr/bin/env python3
"""Local, standard-library-only project initializer and evidence-registry audit.

Important: This is a deterministic consistency check, NOT statistical reanalysis,
independent citation verification, clinical safety clearance, or an ethics review.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
STARTER = BASE / "assets" / "starter-project"

DESIGNS = {
    "cohort", "case_control", "cross_sectional", "rct", "systematic_review",
    "diagnostic_accuracy", "prediction_model", "economic_evaluation",
    "qualitative", "quality_improvement", "case_report", "animal",
    "mixed_methods", "other",
}
ROLE_VALUES = {"primary", "secondary", "exploratory", "sensitivity", "descriptive", "subgroup"}
CLAIM_TYPES = {"result", "literature", "inference", "method"}
CLAIM_STATUSES = {"draft", "evidence_checked", "approved"}
REFERENCE_STATUSES = {"pending", "verified", "rejected"}
CHECK_STATUSES = {"present", "missing", "not_applicable", "pending"}
RATIO_MEASURES = {"OR", "RR", "HR", "IRR", "PR", "DOR"}
DIFF_MEASURES = {"RD", "MD", "SMD", "BETA"}
BOUNDED01_MEASURES = {"AUC", "SENS", "SPEC"}
REQUIRED_COLUMNS = {
    "results.csv": ["result_id", "role", "source_file", "source_location", "population", "outcome", "comparison", "model", "effect_measure", "estimate", "ci_lower", "ci_upper", "ci_level", "p_value", "sample_n", "events_n", "denominator_n", "timepoint", "adjustment_set", "prespecified", "notes"],
    "claims.csv": ["claim_id", "section", "claim_type", "claim_text", "result_ids", "reference_ids", "status", "notes"],
    "references.csv": ["reference_id", "title", "doi", "pmid", "source_url", "verification_status", "verified_passage", "notes"],
    "reporting_checklist.csv": ["guideline", "item_id", "status", "manuscript_location", "notes", "official_url"],
}
GUIDELINE_URLS = {
    "STROBE": "https://www.equator-network.org/reporting-guidelines/strobe/",
    "RECORD": "https://www.equator-network.org/reporting-guidelines/record/",
    "RECORD-PE": "https://www.equator-network.org/reporting-guidelines/record-pe/",
    "CONSORT 2025": "https://www.bmj.com/content/389/bmj-2024-081123",
    "CONSORT-AI": "https://www.equator-network.org/reporting-guidelines/consort-artificial-intelligence/",
    "SPIRIT 2025": "https://www.equator-network.org/reporting-guidelines/",
    "PRISMA 2020": "https://www.prisma-statement.org/prisma-2020",
    "STARD 2015": "https://www.equator-network.org/reporting-guidelines/stard/",
    "STARD-AI": "https://www.equator-network.org/reporting-guidelines/the-stard-ai-reporting-guideline-for-diagnostic-accuracy-studies-using-artificial-intelligence/",
    "TRIPOD+AI": "https://www.bmj.com/content/385/bmj-2023-078378",
    "CHEERS 2022": "https://www.equator-network.org/reporting-guidelines/cheers/",
    "SRQR": "https://www.equator-network.org/reporting-guidelines/",
    "SQUIRE 2.0": "https://www.equator-network.org/reporting-guidelines/squire/",
    "CARE": "https://www.equator-network.org/reporting-guidelines/",
    "ARRIVE 2.0": "https://www.equator-network.org/reporting-guidelines/",
}
DESIGN_GUIDELINES = {
    "cohort": ["STROBE"], "case_control": ["STROBE"],
    "cross_sectional": ["STROBE"], "rct": ["CONSORT 2025"],
    "systematic_review": ["PRISMA 2020"],
    "diagnostic_accuracy": ["STARD 2015"],
    "prediction_model": ["TRIPOD+AI"],
    "economic_evaluation": ["CHEERS 2022"],
    "qualitative": ["SRQR"],
    "quality_improvement": ["SQUIRE 2.0"],
    "case_report": ["CARE"], "animal": ["ARRIVE 2.0"],
    "mixed_methods": [], "other": [],
}


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    detail: str


class Auditor:
    def __init__(self, project: Path, stage: str):
        self.project = project
        self.stage = stage
        self.issues: list[Issue] = []
        self.stats: dict[str, int] = {}
        self.guidelines: list[str] = []

    @property
    def submission(self) -> bool:
        return self.stage == "submission"

    def flag(self, severity: str, code: str, detail: str) -> None:
        self.issues.append(Issue(severity, code, detail))

    def gap(self, code: str, detail: str) -> None:
        self.flag("BLOCKER" if self.submission else "WARNING", code, detail)

    def read_study(self) -> dict:
        path = self.project / "study.json"
        if not path.exists():
            self.flag("BLOCKER", "FILE_MISSING", "study.json missing")
            return {}
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            self.flag("BLOCKER", "INVALID_JSON", f"study.json: {exc}")
            return {}
        if not isinstance(obj, dict):
            self.flag("BLOCKER", "INVALID_JSON", "study.json must contain a JSON object")
            return {}
        return obj

    def read_table(self, name: str) -> list[dict[str, str]]:
        path = self.project / name
        if not path.exists():
            self.flag("BLOCKER", "FILE_MISSING", f"{name} missing")
            return []
        try:
            with path.open(encoding="utf-8-sig", newline="") as fh:
                reader = csv.DictReader(fh)
                actual = reader.fieldnames or []
                missing = [c for c in REQUIRED_COLUMNS[name] if c not in actual]
                if missing:
                    self.flag("BLOCKER", "CSV_SCHEMA", f"{name} missing columns: {', '.join(missing)}")
                    return []
                rows = []
                for idx, row in enumerate(reader, 2):
                    if None in row:
                        self.flag("BLOCKER", "CSV_SHAPE", f"{name} row {idx} has excess fields (check commas/quoting)")
                        continue
                    if any((v or "").strip() for v in row.values()):
                        rows.append({k: (v or "").strip() for k, v in row.items()})
                return rows
        except (OSError, csv.Error, UnicodeDecodeError) as exc:
            self.flag("BLOCKER", "CSV_READ", f"{name}: {exc}")
            return []

    def get_guidelines(self, study: dict) -> list[str]:
        primary = (study.get("primary_design") or "").strip()
        secondary = study.get("secondary_components", [])
        if not isinstance(secondary, list):
            self.flag("BLOCKER", "DESIGN_SCHEMA", "secondary_components must be an array")
            secondary = []
        if not primary:
            self.gap("DESIGN_MISSING", "Choose the study's primary_design before guideline selection")
        elif primary not in DESIGNS:
            self.flag("BLOCKER", "DESIGN_UNKNOWN", f"Unrecognized primary_design: {primary}")
        for value in secondary:
            if value not in DESIGNS:
                self.flag("BLOCKER", "DESIGN_UNKNOWN", f"Unrecognized secondary design: {value}")
        guidelines: list[str] = []
        for design in [primary, *secondary]:
            for item in DESIGN_GUIDELINES.get(design, []):
                if item not in guidelines:
                    guidelines.append(item)
        uses_observational = bool({primary, *secondary} & {"cohort", "case_control", "cross_sectional"})
        if uses_observational and study.get("routine_health_data") is True:
            guidelines.append("RECORD")
            if study.get("pharmacoepidemiology") is True:
                guidelines.append("RECORD-PE")
        if "diagnostic_accuracy" in [primary, *secondary] and study.get("ai_diagnostic") is True:
            guidelines.append("STARD-AI")
        if "rct" in [primary, *secondary] and study.get("ai_intervention") is True:
            guidelines.append("CONSORT-AI")
        if study.get("protocol_only") is True and "rct" in [primary, *secondary]:
            guidelines = [g for g in guidelines if g not in ("CONSORT 2025", "CONSORT-AI")]
            guidelines.insert(0, "SPIRIT 2025")
        dedup = list(dict.fromkeys(guidelines))
        if primary in ("mixed_methods", "other"):
            self.flag("WARNING", "COMPLEX_DESIGN", "Mixed/other primary design needs an explicit human-chosen main reporting framework, beyond the component list")
        if not dedup:
            self.gap("GUIDELINE_SELECTION", "Design needs investigator-directed guideline selection; review EQUATOR guidance")
        return dedup

    def verify_study(self, study: dict) -> None:
        self.guidelines = self.get_guidelines(study)
        for field in ("study_id", "objective", "population", "main_outcome"):
            if not isinstance(study.get(field), str) or not study[field].strip():
                self.gap("STUDY_PROFILE", f"study.json missing or empty field: {field}")
        software = study.get("analysis_software", [])
        if not isinstance(software, list) or not all(isinstance(x, str) for x in software):
            self.flag("BLOCKER", "STUDY_SCHEMA", "analysis_software must be an array of strings")
        elif not software:
            self.gap("SOFTWARE_UNDOCUMENTED", "Record actual software/packages and versions when known")
        if self.submission and study.get("data_handling_confirmed") is not True:
            self.flag("BLOCKER", "PRIVACY_APPROVAL", "Data authorization/de-identification not confirmed")
        if self.submission and study.get("human_signoff") is not True:
            self.flag("BLOCKER", "HUMAN_SIGNOFF", "Human author/PI signoff has not been recorded")
        if self.submission and study.get("official_checklist_complete") is not True:
            self.flag("BLOCKER", "CHECKLIST_ATTESTATION", "Author has not confirmed every applicable official checklist item was inspected")
        if not study.get("target_journal"):
            self.flag("WARNING", "JOURNAL_UNKNOWN", "Target journal not set; journal-specific manuscript limits cannot be audited")
        if study.get("analysis_plan_status") not in ("confirmed", "partial", "unknown"):
            self.flag("WARNING", "SAP_UNKNOWN", "Analysis-plan status missing or unsupported; document prespecified vs exploratory analyses")

    @staticmethod
    def number(raw: str, field: str, rowid: str, flag) -> float | None:
        if not raw:
            return None
        try:
            value = float(raw)
            if not math.isfinite(value):
                raise ValueError("not finite")
            return value
        except ValueError:
            flag("BLOCKER", "NUMERIC_FORMAT", f"{rowid}: {field} must be finite numeric text, got {raw!r}")
            return None

    @staticmethod
    def count(raw: str, field: str, rowid: str, flag) -> int | None:
        if not raw:
            return None
        if not re.fullmatch(r"[0-9]+", raw):
            flag("BLOCKER", "COUNT_FORMAT", f"{rowid}: {field} must be a nonnegative integer, got {raw!r}")
            return None
        return int(raw)

    @staticmethod
    def p_value(raw: str, rowid: str, flag) -> tuple[str, float] | None:
        if not raw:
            return None
        m = re.fullmatch(r"\s*(<=|>=|<|>)?\s*(0?(?:\.\d+)?|1(?:\.0+)?)\s*", raw)
        if not m:
            flag("BLOCKER", "P_FORMAT", f"{rowid}: P value must be 0.03, <0.001, or >0.99; got {raw!r}")
            return None
        comp = m.group(1) or "="
        try:
            value = float(m.group(2))
        except ValueError:
            flag("BLOCKER", "P_FORMAT", f"{rowid}: invalid P value {raw!r}")
            return None
        if value < 0 or value > 1:
            flag("BLOCKER", "P_RANGE", f"{rowid}: P is outside [0,1]")
            return None
        if value == 0 and comp in ("=", "<", "<="):
            flag("BLOCKER", "P_ZERO", f"{rowid}: P must not be reported as exact zero")
        return comp, value

    @staticmethod
    def index(rows: list[dict[str, str]], key: str, table: str, flag) -> dict[str, dict[str, str]]:
        indexed = {}
        for idx, row in enumerate(rows, 2):
            identifier = row.get(key, "")
            if not identifier:
                flag("BLOCKER", "MISSING_ID", f"{table} row {idx} missing {key}")
            elif identifier in indexed:
                flag("BLOCKER", "DUPLICATE_ID", f"{table} duplicate {key}: {identifier}")
            else:
                indexed[identifier] = row
        return indexed

    def audit_results(self, rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
        results = self.index(rows, "result_id", "results.csv", self.flag)
        if not rows:
            self.gap("NO_RESULTS", "No results registered; do not draft numerical claims before source data are locked")
        for rid, row in results.items():
            if row["role"] not in ROLE_VALUES:
                self.flag("BLOCKER", "RESULT_ROLE", f"{rid}: invalid role {row['role']!r}")
            if not row["source_file"] or not row["source_location"]:
                self.gap("SOURCE_TRACE", f"{rid}: missing source_file or source_location")
            if not row["outcome"]:
                self.gap("OUTCOME_MISSING", f"{rid}: missing outcome label")
            measure = row["effect_measure"].upper()
            est = self.number(row["estimate"], "estimate", rid, self.flag)
            lo = self.number(row["ci_lower"], "ci_lower", rid, self.flag)
            hi = self.number(row["ci_upper"], "ci_upper", rid, self.flag)
            level = self.number(row["ci_level"], "ci_level", rid, self.flag)
            pval = self.p_value(row["p_value"], rid, self.flag)
            if (lo is None) != (hi is None):
                self.flag("WARNING", "INCOMPLETE_CI", f"{rid}: one CI bound is absent")
            if level is not None and not (0 < level < 100):
                self.flag("BLOCKER", "CI_LEVEL", f"{rid}: CI level must lie between 0 and 100")
            if lo is not None and hi is not None:
                if lo > hi:
                    self.flag("BLOCKER", "CI_ORDER", f"{rid}: lower CI limit exceeds upper limit")
                if est is not None and (est < lo or est > hi):
                    self.flag("BLOCKER", "ESTIMATE_OUTSIDE_CI", f"{rid}: estimate outside reported confidence limits; verify same estimate/scale")
            if measure in RATIO_MEASURES:
                if est is not None and est <= 0:
                    self.flag("BLOCKER", "RATIO_NONPOSITIVE", f"{rid}: {measure} estimate must be positive")
                if lo is not None and lo <= 0 or hi is not None and hi <= 0:
                    self.flag("BLOCKER", "RATIO_CI_NONPOSITIVE", f"{rid}: {measure} confidence limits must be positive")
            if measure in BOUNDED01_MEASURES:
                for label, value in (("estimate", est), ("ci_lower", lo), ("ci_upper", hi)):
                    if value is not None and not 0 <= value <= 1:
                        self.flag("WARNING", "BOUNDED_SCALE", f"{rid}: {label} for {measure} outside [0,1]; verify scale (0-100%?)")
            counts = {c: self.count(row[c], c, rid, self.flag) for c in ("sample_n", "events_n", "denominator_n")}
            events, denom = counts["events_n"], counts["denominator_n"]
            if events is not None and denom is not None and events > denom:
                self.flag("WARNING", "COUNT_RELATION", f"{rid}: events_n exceeds denominator_n; confirm whether recurrent events are counted")
            if row["prespecified"] not in ("yes", "no", "unknown"):
                self.flag("WARNING", "PRESPECIFIED_STATUS", f"{rid}: prespecified must be yes/no/unknown")
            if row["role"] == "primary" and row["prespecified"] == "unknown":
                self.flag("WARNING", "PRIMARY_PLAN", f"{rid}: primary result not linked to a confirmed analysis plan")
            if row["role"] == "primary" and est is not None and (lo is None or hi is None):
                self.flag("WARNING", "PRIMARY_PRECISION", f"{rid}: primary effect has no complete CI; check if interval is applicable/available")
            if pval is not None and lo is not None and hi is not None and level == 95 and lo <= hi:
                null = 1 if measure in RATIO_MEASURES else (0 if measure in DIFF_MEASURES else None)
                if null is not None:
                    excludes = lo > null or hi < null
                    comp, p = pval
                    p_sig = (comp == "=" and p < 0.01) or (comp in ("<", "<=") and p <= 0.01)
                    p_nonsig = (comp == "=" and p > 0.10) or (comp in (">", ">=") and p >= 0.10)
                    if (p_sig and not excludes) or (p_nonsig and excludes):
                        self.flag("WARNING", "P_CI_POSSIBLE_MISMATCH", f"{rid}: 95% CI and P significance look discordant; confirm same two-sided test, estimand and scale")
        return results

    def audit_references(self, rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
        refs = self.index(rows, "reference_id", "references.csv", self.flag)
        for rid, row in refs.items():
            status = row["verification_status"]
            if status not in REFERENCE_STATUSES:
                self.flag("BLOCKER", "REFERENCE_STATUS", f"{rid}: unsupported verification_status {status!r}")
            if status == "verified":
                if not row["title"] or not (row["doi"] or row["pmid"] or row["source_url"]):
                    self.flag("BLOCKER", "REFERENCE_IDENTITY", f"{rid}: verified source needs title and DOI/PMID/URL")
                if not row["verified_passage"]:
                    self.flag("BLOCKER", "REFERENCE_PASSAGE", f"{rid}: verified status requires checked supporting passage")
            if row["doi"] and not re.match(r"^10\.\d{4,9}/\S+$", row["doi"], re.I):
                self.flag("WARNING", "DOI_FORMAT", f"{rid}: DOI has an unexpected format; confirm official metadata")
        return refs

    def audit_claims(self, rows: list[dict[str, str]], results: dict, refs: dict) -> dict:
        claims = self.index(rows, "claim_id", "claims.csv", self.flag)
        if not rows:
            self.gap("NO_CLAIMS", "No prose claim registry supplied")
        for cid, row in claims.items():
            ctype, status = row["claim_type"], row["status"]
            if ctype not in CLAIM_TYPES:
                self.flag("BLOCKER", "CLAIM_TYPE", f"{cid}: invalid claim_type {ctype!r}")
            if status not in CLAIM_STATUSES:
                self.flag("BLOCKER", "CLAIM_STATUS", f"{cid}: invalid claim status {status!r}")
            elif self.submission and status != "approved":
                self.flag("BLOCKER", "CLAIM_UNAPPROVED", f"{cid}: only human-approved claims can be released")
            if not row["claim_text"]:
                self.gap("CLAIM_TEXT", f"{cid}: claim_text is empty")
            result_ids = [v.strip() for v in row["result_ids"].split("|") if v.strip()]
            ref_ids = [v.strip() for v in row["reference_ids"].split("|") if v.strip()]
            if ctype == "result" and not result_ids:
                self.gap("CLAIM_NO_RESULT", f"{cid}: result claim is not linked to results.csv")
            if ctype == "literature" and not ref_ids:
                self.gap("CLAIM_NO_REFERENCE", f"{cid}: literature claim is not linked to references.csv")
            if ctype == "inference" and not (result_ids or ref_ids):
                self.gap("INFERENCE_UNSUPPORTED", f"{cid}: inference needs traceable result or reference")
            if ctype == "method" and not (result_ids or ref_ids or row["notes"]):
                self.gap("METHOD_UNSOURCED", f"{cid}: method claim needs protocol/code/source note")
            for rid in result_ids:
                if rid not in results:
                    self.flag("BLOCKER", "UNKNOWN_RESULT_ID", f"{cid}: references nonexistent result {rid}")
            for ref_id in ref_ids:
                if ref_id not in refs:
                    self.flag("BLOCKER", "UNKNOWN_REFERENCE_ID", f"{cid}: references nonexistent literature item {ref_id}")
                elif refs[ref_id]["verification_status"] != "verified":
                    self.gap("REFERENCE_UNVERIFIED", f"{cid}: {ref_id} is not verified against an actual source passage")
        return claims

    def audit_manuscript(self, results: dict, refs: dict) -> None:
        path = self.project / "manuscript" / "draft.md"
        if not path.exists():
            self.gap("MANUSCRIPT_MISSING", "manuscript/draft.md not found")
            return
        text = path.read_text(encoding="utf-8")
        if len(text.strip()) < 100:
            self.gap("MANUSCRIPT_EMPTY", "manuscript/draft.md is empty or still a starter template")
        for kind, ident in re.findall(r"\[(R|REF):([A-Za-z0-9_-]+)\]", text):
            if kind == "R" and ident not in results:
                self.flag("BLOCKER", "UNKNOWN_DRAFT_RESULT", f"manuscript anchor [R:{ident}] has no registry entry")
            if kind == "REF" and ident not in refs:
                self.flag("BLOCKER", "UNKNOWN_DRAFT_REFERENCE", f"manuscript anchor [REF:{ident}] has no registry entry")
        if "[TO_VERIFY:" in text and self.submission:
            self.flag("BLOCKER", "UNRESOLVED_DRAFT_NOTE", "Manuscript still contains [TO_VERIFY:...] tags")
        for section in ("introduction", "methods", "results", "discussion", "abstract"):
            if not re.search(r"(?im)^#{1,3}\s+" + section + r"\b", text):
                self.gap("SECTION_MISSING", f"No Markdown heading for {section.title()}")
        if self.submission and ("[R:" not in text and "[REF:" not in text):
            self.flag("WARNING", "TRACE_MARKERS_ABSENT", "No internal evidence tags remain; verify clean manuscript with saved claim registry")

    def audit_checklist(self, rows: list[dict[str, str]], study: dict) -> None:
        recorded = {}
        for row in rows:
            label = row["guideline"].strip()
            key = (label, row["item_id"].strip())
            if not all(key):
                self.flag("BLOCKER", "CHECKLIST_ITEM", "Checklist row missing guideline or item_id")
                continue
            if key in recorded:
                self.flag("BLOCKER", "CHECKLIST_DUPLICATE", f"Duplicated checklist item: {label} / {row['item_id']}")
            recorded[key] = row
            if row["status"] not in CHECK_STATUSES:
                self.flag("BLOCKER", "CHECKLIST_STATUS", f"{key}: unsupported status {row['status']!r}")
            if row["status"] in ("missing", "pending"):
                self.gap("CHECKLIST_GAP", f"{label} item {row['item_id']} is {row['status']}")
            if row["status"] == "present" and not row["manuscript_location"]:
                self.gap("CHECKLIST_LOCATION", f"{label} item {row['item_id']}: no manuscript location")
            if row["status"] == "not_applicable" and not row["notes"]:
                self.gap("CHECKLIST_NA_RATIONALE", f"{label} item {row['item_id']}: no reason for N/A")
            if not row["official_url"]:
                self.flag("WARNING", "CHECKLIST_SOURCE", f"{label} item {row['item_id']}: no official checklist URL")
        for g in self.guidelines:
            if not any(label == g for label, _ in recorded):
                self.gap("CHECKLIST_GUIDELINE", f"No item-level checklist rows for suggested guideline: {g}")
        self.stats["checklist_items"] = len(rows)

    def run(self) -> None:
        if not self.project.is_dir():
            self.flag("BLOCKER", "PROJECT_MISSING", f"Project directory does not exist: {self.project}")
            return
        study = self.read_study()
        self.verify_study(study)
        results_rows = self.read_table("results.csv")
        ref_rows = self.read_table("references.csv")
        claims_rows = self.read_table("claims.csv")
        checklist_rows = self.read_table("reporting_checklist.csv")
        self.stats.update({"results": len(results_rows), "references": len(ref_rows), "claims": len(claims_rows)})
        results = self.audit_results(results_rows)
        refs = self.audit_references(ref_rows)
        self.audit_claims(claims_rows, results, refs)
        self.audit_manuscript(results, refs)
        self.audit_checklist(checklist_rows, study)
        self.flag("INFO", "SCOPE", "This check does not confirm raw-data computations, complete guideline coverage, source passage meaning, ethics approval, or causal validity")

    def report(self) -> str:
        blockers = sum(x.severity == "BLOCKER" for x in self.issues)
        warnings = sum(x.severity == "WARNING" for x in self.issues)
        lines = [
            "# Clinical Manuscript Audit (machine checks)", "",
            f"- Project: `{self.project.name}`",
            f"- Stage: `{self.stage}`",
            f"- Result rows: {self.stats.get('results', 0)}",
            f"- Claim rows: {self.stats.get('claims', 0)}",
            f"- Reference rows: {self.stats.get('references', 0)}",
            f"- Checklist rows entered: {self.stats.get('checklist_items', 0)}",
            f"- BLOCKER: {blockers}; WARNING: {warnings}",
            f"- Suggested applicable guides: {', '.join(self.guidelines) or 'not resolved'}",
            "", "## Official source links (confirm current checklist and journal extensions)", "",
        ]
        for g in self.guidelines:
            lines.append(f"- {g}: {GUIDELINE_URLS[g]}")
        lines += ["", "## Machine-detected issues", ""]
        for severity in ("BLOCKER", "WARNING", "INFO"):
            group = [x for x in self.issues if x.severity == severity]
            lines.append(f"### {severity} ({len(group)})")
            if not group:
                lines.append("- None detected (does not imply scientific validation).")
            for issue in group:
                lines.append(f"- **{issue.code}**: {issue.detail}")
            lines.append("")
        lines += [
            "## Manual signoff (not performed by this script)", "",
            "- [ ] Author/statistician checked all numeric source outputs and adjustment models.",
            "- [ ] Clinician/epidemiologist checked interpretation, bias and causal language.",
            "- [ ] Citation verifier checked passages and context for each literature claim.",
            "- [ ] Author checked complete official guideline checklist and manuscript item locations.",
            "- [ ] PI/corresponding author checked privacy, ethics, registration, disclosures and journal policy.",
            "", "This report is not an editorial acceptance decision or scientific validity certificate.",
        ]
        return "\n".join(lines) + "\n"

    def has_blockers(self) -> bool:
        return any(i.severity == "BLOCKER" for i in self.issues)


def create_project(path: Path) -> int:
    if path.exists():
        print(f"ERROR: project path already exists: {path}", file=sys.stderr)
        return 1
    if not STARTER.is_dir():
        print("ERROR: packaged starter-project assets missing", file=sys.stderr)
        return 1
    shutil.copytree(STARTER, path)
    print(f"Created blank project templates at: {path}")
    print("Populate study.json, results.csv, claims.csv, references.csv and reporting_checklist.csv from verified sources.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="Copy blank starter files into a new project directory")
    init.add_argument("--project", type=Path, required=True)
    audit = sub.add_parser("audit", help="Run deterministic schema and consistency checks")
    audit.add_argument("--project", type=Path, required=True)
    audit.add_argument("--stage", choices=("drafting", "submission"), default="drafting")
    audit.add_argument("--out", type=Path, help="Optional output markdown path; default PROJECT/audit.md")
    args = parser.parse_args()
    if args.command == "init":
        return create_project(args.project)
    auditor = Auditor(args.project, args.stage)
    auditor.run()
    report = auditor.report()
    dest = args.out if args.out else args.project / "audit.md"
    if args.project.is_dir():
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(report, encoding="utf-8")
        print(f"Report written to {dest}")
    print(f"BLOCKER={sum(x.severity == 'BLOCKER' for x in auditor.issues)} WARNING={sum(x.severity == 'WARNING' for x in auditor.issues)}")
    return 2 if auditor.has_blockers() else 0


if __name__ == "__main__":
    sys.exit(main())
