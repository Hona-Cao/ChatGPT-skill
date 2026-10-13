#!/usr/bin/env python3
"""Deterministic Major Revision / Reviewer Response cross-reference checks.

This checks what was *recorded*, not whether a scientific rebuttal is convincing,
tracked Word edits are correct, analyses were actually run, or a reviewer is right.
Uses only Python standard library; never contacts external services.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
TEMPLATE = BASE / "assets" / "revision-starter"
HEADERS = {
    "revision_rounds.csv": ["round", "decision_letter_source", "received_date", "manuscript_version", "status", "notes"],
    "review_comments.csv": [
        "comment_id", "round", "reviewer", "source_location", "verbatim_comment",
        "atomic_request", "category", "priority", "decision", "requires_new_analysis",
        "analysis_ids", "prior_comment_ids", "origin", "conflict_id", "rationale", "owner", "status", "notes",
    ],
    "revision_changes.csv": [
        "change_id", "round", "comment_ids", "section", "change_type", "before_excerpt",
        "after_excerpt", "source_file", "manuscript_version", "verified_location",
        "verified_by", "status", "notes",
    ],
    "additional_analyses.csv": [
        "analysis_id", "round", "comment_ids", "analysis_description", "status",
        "output_file", "output_location", "verified_result_ids", "verified_by", "notes",
    ],
    "review_responses.csv": [
        "comment_id", "response_text", "status", "claims_revision", "claims_analysis", "approved_by", "notes",
    ],
    "comment_conflicts.csv": [
        "conflict_id", "comment_ids", "summary", "resolution", "rationale", "approved_by", "notes",
    ],
}
CATEGORIES = {"methods", "statistics", "interpretation", "literature", "reporting", "figures", "language", "ethics", "other"}
PRIORITIES = {"critical", "major", "minor"}
DECISIONS = {"pending", "revise", "clarify", "reanalyze", "partially_disagree", "disagree"}
COMMENT_STATES = {"open", "in_progress", "resolved"}
ANALYSIS_STATES = {"planned", "running", "completed_unverified", "verified", "not_feasible", "cancelled"}
CHANGE_STATES = {"planned", "edited", "verified"}
RESPONSE_STATES = {"draft", "ready_for_review", "approved"}
ORIGINS = {"initial", "followup", "new", "editorial"}
ROUND_STATES = {"active", "ready", "submitted"}
YESNO = {"yes", "no"}
CROSSREF_SPLIT = re.compile(r"[;,]")
PLACEHOLDER = re.compile(r"\[TO_VERIFY\b|\bTBD\b|\bpage\s+XX\b|\blines?\s+XX\b", re.I)
CHANGED_TEXT = re.compile(r"\bwe\s+(?:have\s+)?(?:revised|modified|updated|added|corrected)\b.{0,45}\b(?:manuscript|text|section|table|figure|supplement)\b", re.I)
ANALYSIS_TEXT = re.compile(r"\bwe\s+(?:have\s+)?(?:performed|conducted|reran|re-ran|reanalysed|reanalyzed)\b.{0,40}\b(?:analysis|analyses|model|test|regression)\b", re.I)


def refs(text: str) -> list[str]:
    return [s.strip() for s in CROSSREF_SPLIT.split(text or "") if s.strip()]


def yes(value: str) -> bool:
    return value.strip().lower() == "yes"


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    message: str


class RevisionAuditor:
    def __init__(self, project: Path, stage: str = "drafting"):
        self.project = project
        self.dir = project / "revision"
        self.stage = stage
        self.issues: list[Issue] = []
        self.tables: dict[str, list[dict[str, str]]] = {}
        self.meta: dict = {}
        self.current_round = ""
        self.counts: dict[str, int] = {}

    @property
    def submission(self) -> bool:
        return self.stage == "submission"

    def flag(self, severity: str, code: str, message: str) -> None:
        self.issues.append(Issue(severity, code, message))

    def gap(self, code: str, message: str) -> None:
        self.flag("BLOCKER" if self.submission else "WARNING", code, message)

    def read(self) -> None:
        if not self.dir.is_dir():
            self.flag("BLOCKER", "REVISION_DIR_MISSING", f"Missing revision directory: {self.dir}")
            return
        path = self.dir / "revision_meta.json"
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(obj, dict):
                raise ValueError("expected JSON object")
            self.meta = obj
        except (OSError, ValueError) as e:
            self.flag("BLOCKER", "META_INVALID", f"revision_meta.json: {e}")
        self.current_round = (self.meta.get("current_round") or "").strip()
        if not re.fullmatch(r"R[1-9][0-9]*", self.current_round):
            self.gap("CURRENT_ROUND", "Specify current_round such as R1 or R2 in revision_meta.json")
        for filename, header in HEADERS.items():
            path = self.dir / filename
            try:
                with path.open(encoding="utf-8-sig", newline="") as f:
                    reader = csv.DictReader(f)
                    if not reader.fieldnames or any(k not in reader.fieldnames for k in header):
                        self.flag("BLOCKER", "SCHEMA", f"{filename}: missing expected columns: {header}")
                        self.tables[filename] = []
                        continue
                    parsed = []
                    for rowno, row in enumerate(reader, 2):
                        if None in row:
                            self.flag("BLOCKER", "CSV_SHAPE", f"{filename}:{rowno} has extra comma-separated fields")
                            continue
                        values = {k: (v or "").strip() for k, v in row.items()}
                        if any(values.values()):
                            parsed.append(values)
                    self.tables[filename] = parsed
            except (OSError, csv.Error, UnicodeError) as e:
                self.flag("BLOCKER", "CSV_READ", f"{filename}: {e}")
                self.tables[filename] = []

    def rows(self, filename: str) -> list[dict[str, str]]:
        return self.tables.get(filename, [])

    def check(self) -> None:
        self.read()
        if not self.dir.is_dir():
            return
        for field in ("all_comments_captured", "response_letter_author_approved", "revision_locations_checked", "journal_requirements_checked"):
            if not isinstance(self.meta.get(field), bool):
                self.flag("BLOCKER", "META_FIELD_TYPE", f"{field} must be a JSON boolean")
            elif self.submission and self.meta[field] is not True:
                self.gap("AUTHOR_ATTESTATION", f"Revision author attestation incomplete: {field}")
        rounds = self._rounds()
        comments = self._comments(rounds)
        changes = self._changes(comments)
        analyses = self._analyses(comments)
        conflicts = self._conflicts(comments)
        self._responses(comments, changes, analyses)
        self._links(comments, changes, analyses, conflicts)
        self.counts = {"rounds": len(rounds), "comments": len(comments), "changes": len(changes), "analyses": len(analyses), "responses": len(self.rows("review_responses.csv"))}
        self.flag("INFO", "LIMITS", "CSV checks cannot verify tracked Word edits, actual analysis execution, completeness of imported reviewer text, or scientific validity; authors must compare original documents.")

    def _rounds(self) -> dict[str, dict]:
        data = {}
        for row in self.rows("revision_rounds.csv"):
            rid = row["round"]
            if not re.fullmatch(r"R[1-9][0-9]*", rid):
                self.flag("BLOCKER", "ROUND_ID", f"Invalid round {rid!r}")
            if rid in data:
                self.flag("BLOCKER", "DUPLICATE_ROUND", f"Duplicate revision round: {rid}")
            data[rid] = row
            if row["status"] not in ROUND_STATES:
                self.flag("BLOCKER", "ROUND_STATUS", f"{rid}: expected one of {sorted(ROUND_STATES)}")
            if not row["decision_letter_source"]:
                self.gap("LETTER_SOURCE", f"{rid}: decision letter source path/location missing")
        if self.current_round not in data:
            self.gap("ROUND_NOT_REGISTERED", f"Current revision round {self.current_round or '(blank)'} not listed in revision_rounds.csv")
        return data

    def _comments(self, rounds: dict) -> dict[str, dict]:
        data = {}
        for row in self.rows("review_comments.csv"):
            cid = row["comment_id"]
            if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]{1,48}", cid):
                self.flag("BLOCKER", "COMMENT_ID", f"Invalid comment ID: {cid!r}")
            if cid in data:
                self.flag("BLOCKER", "DUPLICATE_COMMENT", f"Comment ID repeated across rounds: {cid}")
            data[cid] = row
            if row["round"] not in rounds:
                self.flag("BLOCKER", "UNKNOWN_ROUND", f"{cid}: round {row['round']} not registered")
            for attr, allowed in (("category", CATEGORIES), ("priority", PRIORITIES), ("decision", DECISIONS), ("status", COMMENT_STATES), ("origin", ORIGINS)):
                if row[attr] not in allowed:
                    self.gap("COMMENT_FIELD", f"{cid}: {attr}={row[attr]!r} must be one of {sorted(allowed)}")
            if row["requires_new_analysis"] not in YESNO:
                self.gap("ANALYSIS_FLAG", f"{cid}: requires_new_analysis must be yes/no")
            for attr in ("reviewer", "source_location", "verbatim_comment", "atomic_request"):
                if not row[attr]:
                    self.gap("COMMENT_SOURCE", f"{cid}: missing {attr}; preserve original reviewer wording and provenance")
            if row["round"] != "R1" and row["origin"] == "followup" and not refs(row["prior_comment_ids"]):
                self.gap("FOLLOWUP_SOURCE", f"{cid}: followup requires a prior_comment_ids link")
            if row["decision"] in {"disagree", "partially_disagree"} and not row["rationale"]:
                self.gap("REBUTTAL_BASIS", f"{cid}: disagreement requires an explicit factual/scientific rationale")
            if self.submission and row["round"] == self.current_round:
                if row["decision"] == "pending":
                    self.gap("DECISION_PENDING", f"{cid}: no response strategy selected")
                if row["status"] != "resolved":
                    self.gap("COMMENT_OPEN", f"{cid}: status must be resolved, currently {row['status']!r}")
        if not any(row["round"] == self.current_round for row in data.values()):
            self.gap("NO_REVIEW_COMMENTS", "No comments recorded for current revision round")
        for cid, row in data.items():
            for prior in refs(row["prior_comment_ids"]):
                if prior not in data:
                    self.gap("PRIOR_COMMENT_UNKNOWN", f"{cid}: references unknown earlier comment {prior}")
                elif prior == cid or self._round_num(data[prior]["round"]) >= self._round_num(row["round"]):
                    self.flag("BLOCKER", "PRIOR_COMMENT_ORDER", f"{cid}: prior comment {prior} must be from an earlier round")
        return data

    @staticmethod
    def _round_num(value: str) -> int:
        return int(value[1:]) if re.fullmatch(r"R[1-9][0-9]*", value or "") else 0

    def _changes(self, comments: dict) -> dict[str, dict]:
        data = {}
        for row in self.rows("revision_changes.csv"):
            xid = row["change_id"]
            if not xid:
                self.flag("BLOCKER", "CHANGE_ID", "revision_changes.csv contains a row with no change_id")
                continue
            if xid in data:
                self.flag("BLOCKER", "DUPLICATE_CHANGE", f"Duplicated change ID {xid}")
            data[xid] = row
            if row["status"] not in CHANGE_STATES:
                self.flag("BLOCKER", "CHANGE_STATUS", f"{xid}: invalid status {row['status']!r}")
            for cid in refs(row["comment_ids"]):
                if cid not in comments:
                    self.flag("BLOCKER", "CHANGE_UNKNOWN_COMMENT", f"{xid} references unknown comment {cid}")
            if not refs(row["comment_ids"]):
                self.gap("CHANGE_NOT_LINKED", f"{xid} has no reviewer-comment link")
            if row["status"] == "verified":
                for key in ("section", "source_file", "manuscript_version", "verified_location", "verified_by"):
                    if not row[key]:
                        self.gap("CHANGE_VERIFICATION", f"{xid}: verified change lacks {key}")
                if row["change_type"] == "text" and not row["after_excerpt"]:
                    self.gap("CHANGE_AFTER_TEXT", f"{xid}: verified text change lacks after_excerpt")
                if PLACEHOLDER.search(row["verified_location"]):
                    self.gap("LOCATION_PLACEHOLDER", f"{xid}: placeholder rather than verified manuscript location")
        return data

    def _analyses(self, comments: dict) -> dict[str, dict]:
        data = {}
        for row in self.rows("additional_analyses.csv"):
            aid = row["analysis_id"]
            if not aid:
                self.flag("BLOCKER", "ANALYSIS_ID", "additional_analyses.csv contains row without analysis_id")
                continue
            if aid in data:
                self.flag("BLOCKER", "DUPLICATE_ANALYSIS", f"Duplicated analysis {aid}")
            data[aid] = row
            if row["status"] not in ANALYSIS_STATES:
                self.flag("BLOCKER", "ANALYSIS_STATUS", f"{aid}: invalid status {row['status']!r}")
            for cid in refs(row["comment_ids"]):
                if cid not in comments:
                    self.flag("BLOCKER", "ANALYSIS_UNKNOWN_COMMENT", f"{aid}: unknown linked comment {cid}")
            if not refs(row["comment_ids"]):
                self.gap("ANALYSIS_NOT_LINKED", f"{aid}: no reviewer-comment link")
            if row["status"] == "verified":
                for key in ("analysis_description", "output_file", "output_location", "verified_by"):
                    if not row[key]:
                        self.gap("ANALYSIS_VERIFICATION", f"{aid}: verified status lacks {key}")
                if PLACEHOLDER.search(row["output_location"]):
                    self.gap("ANALYSIS_LOCATION_PLACEHOLDER", f"{aid}: analysis output locator is placeholder")
        result_ids = set()
        registry = self.project / "results.csv"
        if registry.exists():
            try:
                with registry.open(encoding="utf-8-sig", newline="") as f:
                    reader = csv.DictReader(f)
                    if "result_id" not in (reader.fieldnames or []):
                        self.flag("BLOCKER", "RESULT_REGISTRY_SCHEMA", "results.csv lacks result_id column")
                    else:
                        result_ids = {r.get("result_id", "").strip() for r in reader}
            except (OSError, csv.Error, UnicodeError) as e:
                self.flag("BLOCKER", "RESULT_REGISTRY_READ", f"Could not read results.csv: {e}")
        for aid, row in data.items():
            linked_results = refs(row["verified_result_ids"])
            if linked_results and not registry.exists():
                self.gap("RESULT_REGISTRY_ABSENT", f"{aid}: result IDs supplied but project/results.csv not provided for cross-checking")
            for rid in linked_results:
                if registry.exists() and rid not in result_ids:
                    self.gap("UNKNOWN_RESULT_ID", f"{aid}: unknown source result ID {rid}")
        return data

    def _conflicts(self, comments: dict) -> dict[str, dict]:
        data = {}
        for row in self.rows("comment_conflicts.csv"):
            fid = row["conflict_id"]
            if not fid:
                self.flag("BLOCKER", "CONFLICT_ID", "A conflict row has no conflict_id")
                continue
            if fid in data:
                self.flag("BLOCKER", "DUPLICATE_CONFLICT", f"Duplicate conflict {fid}")
            data[fid] = row
            for cid in refs(row["comment_ids"]):
                if cid not in comments:
                    self.flag("BLOCKER", "CONFLICT_UNKNOWN_COMMENT", f"{fid}: unknown comment {cid}")
            if len(refs(row["comment_ids"])) < 2:
                self.gap("CONFLICT_COVERAGE", f"{fid}: record at least two conflicting comments")
            for key in ("resolution", "rationale", "approved_by"):
                if not row[key]:
                    self.gap("CONFLICT_OPEN", f"{fid}: conflict has no {key}")
        return data

    def _responses(self, comments: dict, changes: dict, analyses: dict) -> None:
        data = {}
        for row in self.rows("review_responses.csv"):
            cid = row["comment_id"]
            if cid in data:
                self.flag("BLOCKER", "DUPLICATE_RESPONSE", f"Multiple response rows for comment {cid}")
            data[cid] = row
            if cid not in comments:
                self.flag("BLOCKER", "ORPHAN_RESPONSE", f"Response references unknown reviewer comment {cid}")
                continue
            if row["status"] not in RESPONSE_STATES:
                self.flag("BLOCKER", "RESPONSE_STATUS", f"{cid}: invalid response status {row['status']!r}")
            if row["claims_revision"] not in YESNO or row["claims_analysis"] not in YESNO:
                self.gap("ACTION_FLAG", f"{cid}: claims_revision and claims_analysis must be yes/no")
            if not row["response_text"]:
                self.gap("RESPONSE_EMPTY", f"{cid}: no actual point-by-point response text")
            else:
                if PLACEHOLDER.search(row["response_text"]):
                    self.gap("RESPONSE_PLACEHOLDER", f"{cid}: response contains an unresolved placeholder")
                if CHANGED_TEXT.search(row["response_text"]) and not yes(row["claims_revision"]):
                    self.gap("REVISION_CLAIM_UNFLAGGED", f"{cid}: response claims a manuscript change but claims_revision is not yes")
                if ANALYSIS_TEXT.search(row["response_text"]) and not yes(row["claims_analysis"]):
                    self.gap("ANALYSIS_CLAIM_UNFLAGGED", f"{cid}: response implies an analysis but claims_analysis is not yes")
            linked_changes = [x for x in changes.values() if cid in refs(x["comment_ids"]) and x["status"] == "verified"]
            linked_analyses = [x for x in analyses.values() if cid in refs(x["comment_ids"]) and x["status"] == "verified"]
            if yes(row["claims_revision"]) and not linked_changes:
                self.gap("UNSUPPORTED_CHANGE_CLAIM", f"{cid}: says manuscript was revised but no verified linked revision exists")
            if yes(row["claims_analysis"]) and not linked_analyses:
                self.gap("UNSUPPORTED_ANALYSIS_CLAIM", f"{cid}: says new analysis was done but no verified linked analysis exists")
            if self.submission and comments[cid]["round"] == self.current_round:
                if row["status"] != "approved" or not row["approved_by"]:
                    self.gap("RESPONSE_NOT_APPROVED", f"{cid}: response and author verification are not complete")
                if row["status"] == "approved" and not row["response_text"]:
                    self.gap("EMPTY_APPROVED_RESPONSE", f"{cid}: approved response text cannot be empty")
        for cid, com in comments.items():
            if com["round"] == self.current_round and cid not in data:
                self.gap("RESPONSE_MISSING", f"No response record for {cid}")

    def _links(self, comments: dict, changes: dict, analyses: dict, conflicts: dict) -> None:
        for cid, row in comments.items():
            if row["round"] != self.current_round:
                continue
            verified_changes = [x for x in changes.values() if cid in refs(x["comment_ids"]) and x["status"] == "verified"]
            verified_analyses = [x for x in analyses.values() if cid in refs(x["comment_ids"]) and x["status"] == "verified"]
            if row["decision"] in {"revise", "reanalyze"} and not verified_changes:
                self.gap("PROMISED_REVISION_NOT_VERIFIED", f"{cid}: decision requires a verified manuscript/supplement change")
            if (yes(row["requires_new_analysis"]) or row["decision"] == "reanalyze") and not verified_analyses:
                self.gap("REQUIRED_ANALYSIS_UNVERIFIED", f"{cid}: new analysis not fully source-verified")
            for aid in refs(row["analysis_ids"]):
                if aid not in analyses:
                    self.flag("BLOCKER", "UNKNOWN_ANALYSIS", f"{cid}: references unknown analysis {aid}")
                elif cid not in refs(analyses[aid]["comment_ids"]):
                    self.gap("ANALYSIS_LINK_ASYMMETRY", f"{cid}: analysis {aid} does not link back to reviewer comment")
            fid = row["conflict_id"]
            if fid:
                if fid not in conflicts:
                    self.flag("BLOCKER", "UNKNOWN_CONFLICT", f"{cid}: conflict {fid} not registered")
                elif cid not in refs(conflicts[fid]["comment_ids"]):
                    self.gap("CONFLICT_LINK_ASYMMETRY", f"{cid}: conflict {fid} fails to link back")
        for xid, change in changes.items():
            for cid in refs(change["comment_ids"]):
                if cid in comments and comments[cid]["round"] != change["round"]:
                    self.gap("CHANGE_ROUND", f"{xid}: round differs from linked comment {cid}")
        for aid, analysis in analyses.items():
            for cid in refs(analysis["comment_ids"]):
                if cid in comments and comments[cid]["round"] != analysis["round"]:
                    self.gap("ANALYSIS_ROUND", f"{aid}: round differs from linked comment {cid}")

    def has_blockers(self) -> bool:
        return any(i.severity == "BLOCKER" for i in self.issues)

    def report(self) -> str:
        blockers = [x for x in self.issues if x.severity == "BLOCKER"]
        warnings = [x for x in self.issues if x.severity == "WARNING"]
        lines = [
            "# Major Revision / Response Audit (deterministic checks)", "",
            f"- Project: `{self.project}`; round: `{self.current_round or 'unassigned'}`; stage: `{self.stage}`",
            f"- Recorded comments: {self.counts.get('comments', 0)}; responses: {self.counts.get('responses', 0)}; verified changes/analyses are checked for links",
            f"- BLOCKER: {len(blockers)}; WARNING: {len(warnings)}", "",
        ]
        for level in ("BLOCKER", "WARNING", "INFO"):
            matched = [x for x in self.issues if x.severity == level]
            lines.extend([f"## {level} ({len(matched)})", ""])
            if not matched:
                lines.append("- No machine-detected issues (not scientific certification).")
            for issue in matched:
                lines.append(f"- **{issue.code}**: {issue.message}")
            lines.append("")
        lines.extend([
            "## Human audit, not performed by the script", "",
            "- [ ] Compare every extracted comment against the ORIGINAL editor decision letter and reviewer report; retain exact wording and all subquestions.",
            "- [ ] Compare every after_excerpt and location against the actual revised manuscript/figures/supplements.",
            "- [ ] Verify each additional analysis against source outputs and result registry; discuss clinical and statistical validity.",
            "- [ ] Check all scientific justifications for agreeing or disagreeing, and consistency across R1/R2/R3 rounds.",
            "- [ ] Check journal rebuttal format, page/line numbering, submission requirements, and all author approvals.",
            "", "Do not treat zero machine-detected blockers as proof of scientific correctness or a successful submission.",
        ])
        return "\n".join(lines) + "\n"


def init_project(project: Path) -> int:
    target = project / "revision"
    if target.exists():
        print(f"ERROR: revision folder already exists, refusing to overwrite: {target}", file=sys.stderr)
        return 1
    if not TEMPLATE.is_dir():
        print("ERROR: revision templates are not packaged", file=sys.stderr)
        return 1
    project.mkdir(parents=True, exist_ok=True)
    shutil.copytree(TEMPLATE, target)
    print(f"Revision project initialized at {target}; populate from original editor/reviewer documents.")
    return 0


def render(auditor: RevisionAuditor) -> str:
    """Draft response letter from explicit CSV, preserving verbatim comments.

    This never generates scientific answers from reviewer text by itself.
    """
    sections = ["# Response to Reviewers — INTERNAL DRAFT", "", "[TO_VERIFY: journal submission format, decision letter, manuscript version and author approval]", ""]
    comments = [r for r in auditor.rows("review_comments.csv") if r["round"] == auditor.current_round]
    responses = {r["comment_id"]: r for r in auditor.rows("review_responses.csv")}
    last = None
    for com in comments:
        if com["reviewer"] != last:
            sections.extend([f"## {com['reviewer']}", ""])
            last = com["reviewer"]
        cid = com["comment_id"]
        response = responses.get(cid, {})
        sections.extend([
            f"### {cid}", "", "**Original reviewer comment (verbatim)**", "",
            "> " + com["verbatim_comment"].replace("\n", "\n> "), "",
            "**Response**", "", response.get("response_text") or "[TO_VERIFY: author response not written]", "",
        ])
    sections.extend(["---", "", "Generated from reviewer-response registry. Verify manuscript line references against the final marked-up file; remove internal notes only after author review.", ""])
    return "\n".join(sections)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    cmds = parser.add_subparsers(dest="command", required=True)
    p = cmds.add_parser("init", help="Initialize revision folder without overwriting existing work")
    p.add_argument("--project", type=Path, required=True)
    p = cmds.add_parser("audit", help="Check reviewer-response cross references and completion")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--stage", choices=("drafting", "submission"), default="drafting")
    p.add_argument("--out", type=Path)
    p = cmds.add_parser("render", help="Generate INTERNAL response-letter draft, refusing unsupported final submission")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--stage", choices=("drafting", "submission"), default="drafting")
    p.add_argument("--out", type=Path)
    p.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.command == "init":
        return init_project(args.project)
    auditor = RevisionAuditor(args.project, args.stage)
    auditor.check()
    if args.command == "audit":
        out = args.out or auditor.dir / "revision_audit.md"
        if auditor.dir.is_dir():
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(auditor.report(), encoding="utf-8")
            print(f"Report: {out}")
        print(f"BLOCKER={sum(i.severity == 'BLOCKER' for i in auditor.issues)} WARNING={sum(i.severity == 'WARNING' for i in auditor.issues)}")
        return 2 if auditor.has_blockers() else 0
    if auditor.has_blockers():
        print("Cannot render response letter while structural or stage-specific blockers remain.", file=sys.stderr)
        return 2
    out = args.out or auditor.dir / "response-to-reviewers.md"
    if out.exists() and not args.overwrite:
        print(f"ERROR: refusing to overwrite existing response letter: {out}; use --overwrite explicitly", file=sys.stderr)
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(auditor), encoding="utf-8")
    print(f"Internal draft response letter: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
