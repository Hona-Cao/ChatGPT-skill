"""Synthetic tests for Major Revision / Reviewer Response cross-references."""
from __future__ import annotations

import csv
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("revision_audit", ROOT / "scripts" / "revision_audit.py")
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def save_rows(p: Path, name: str, rows):
    with (p / name).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=mod.HEADERS[name])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def load_rows(p: Path, name: str):
    with (p / name).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


class RevisionAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name) / "fictional-medical-paper"
        self.assertEqual(0, mod.init_project(self.project))
        self.rev = self.project / "revision"

    def mark_complete(self):
        meta_path = self.rev / "revision_meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta.update(
            current_round="R1", all_comments_captured=True,
            response_letter_author_approved=True, revision_locations_checked=True,
            journal_requirements_checked=True,
        )
        meta_path.write_text(json.dumps(meta), encoding="utf-8")
        save_rows(self.rev, "revision_rounds.csv", [dict(round="R1", decision_letter_source="editor-decision.txt", received_date="2026-10-01", manuscript_version="ms-v2", status="ready", notes="fictional")])
        save_rows(self.rev, "review_comments.csv", [dict(
            comment_id="R1-01", round="R1", reviewer="Reviewer 1", source_location="Review report paragraph 2",
            verbatim_comment="Please clarify effect sizes.", atomic_request="Clarify effect size explanation",
            category="statistics", priority="major", decision="revise", requires_new_analysis="no", analysis_ids="",
            prior_comment_ids="", origin="initial", conflict_id="", rationale="", owner="Lead author", status="resolved", notes="fictional",
        )])
        save_rows(self.rev, "revision_changes.csv", [dict(
            change_id="CHG-R1-01", round="R1", comment_ids="R1-01", section="Results", change_type="text",
            before_excerpt="Previous synthetic result.", after_excerpt="Revised fictional effect-size explanation.",
            source_file="ms-v2.docx", manuscript_version="ms-v2", verified_location="Results paragraph 2, lines 100-104",
            verified_by="Lead author", status="verified", notes="fictional",
        )])
        save_rows(self.rev, "review_responses.csv", [dict(
            comment_id="R1-01", response_text="We have revised the manuscript, Results, to clarify effect sizes (lines 100-104).",
            status="approved", claims_revision="yes", claims_analysis="no", approved_by="Lead author", notes="fictional",
        )])

    def codes(self, stage="submission"):
        obj = mod.RevisionAuditor(self.project, stage)
        obj.check()
        return obj, {i.code for i in obj.issues if i.severity == "BLOCKER"}

    def test_fresh_revision_is_not_submission_ready(self):
        self.assertTrue((self.rev / "review_comments.csv").exists())
        a, codes = self.codes()
        self.assertIn("NO_REVIEW_COMMENTS", codes)
        self.assertIn("AUTHOR_ATTESTATION", codes)
        self.assertTrue(a.has_blockers())

    def test_complete_synthetic_revision_passes_structural_gate(self):
        self.mark_complete()
        a, codes = self.codes()
        self.assertFalse(codes, a.report())
        self.assertIn("R1-01", mod.render(a))
        self.assertIn("Please clarify effect sizes.", mod.render(a))

    def test_verbal_claim_of_revision_without_actual_edit_blocked(self):
        self.mark_complete()
        save_rows(self.rev, "revision_changes.csv", [])
        _, codes = self.codes()
        self.assertIn("UNSUPPORTED_CHANGE_CLAIM", codes)
        self.assertIn("PROMISED_REVISION_NOT_VERIFIED", codes)

    def test_new_analysis_unverified_is_blocked(self):
        self.mark_complete()
        comments = load_rows(self.rev, "review_comments.csv")
        comments[0].update(requires_new_analysis="yes", decision="reanalyze", analysis_ids="ANA-01")
        save_rows(self.rev, "review_comments.csv", comments)
        analyses = [dict(analysis_id="ANA-01", round="R1", comment_ids="R1-01", analysis_description="Illustrative sensitivity analysis", status="planned", output_file="", output_location="", verified_result_ids="", verified_by="", notes="Pending")]
        save_rows(self.rev, "additional_analyses.csv", analyses)
        responses = load_rows(self.rev, "review_responses.csv")
        responses[0].update(claims_analysis="yes",response_text="We performed an additional sensitivity analysis and have revised the manuscript.")
        save_rows(self.rev, "review_responses.csv", responses)
        _, codes = self.codes()
        self.assertIn("UNSUPPORTED_ANALYSIS_CLAIM", codes)
        self.assertIn("REQUIRED_ANALYSIS_UNVERIFIED", codes)

    def test_verified_new_analysis_with_actual_output_passes(self):
        self.mark_complete()
        comments = load_rows(self.rev, "review_comments.csv")
        comments[0].update(requires_new_analysis="yes", decision="reanalyze", analysis_ids="ANA-01")
        save_rows(self.rev, "review_comments.csv", comments)
        save_rows(self.rev, "additional_analyses.csv", [dict(
            analysis_id="ANA-01", round="R1", comment_ids="R1-01", analysis_description="Synthetic sensitivity analysis",
            status="verified", output_file="output/sensitivity.txt", output_location="Table 2, row 3", verified_result_ids="",
            verified_by="Fictional statistician", notes="Synthetic fixture, not a real analysis",
        )])
        responses = load_rows(self.rev, "review_responses.csv")
        responses[0].update(claims_analysis="yes",response_text="We performed a new sensitivity analysis and revised the manuscript.")
        save_rows(self.rev, "review_responses.csv", responses)
        auditor, codes = self.codes()
        self.assertFalse(codes, auditor.report())

    def test_unknown_additional_result_id_is_blocked(self):
        self.mark_complete()
        comments = load_rows(self.rev, "review_comments.csv")
        comments[0].update(requires_new_analysis="yes", decision="reanalyze", analysis_ids="ANA-01")
        save_rows(self.rev, "review_comments.csv", comments)
        save_rows(self.rev, "additional_analyses.csv", [dict(
            analysis_id="ANA-01", round="R1", comment_ids="R1-01", analysis_description="Synthetic reanalysis",
            status="verified", output_file="output/sensitivity.txt", output_location="sheet 2 row 4", verified_result_ids="RES-MISSING",
            verified_by="Fictional statistician", notes="synthetic",
        )])
        (self.project / "results.csv").write_text("result_id,estimate\nRES-001,1.2\n", encoding="utf-8")
        responses = load_rows(self.rev, "review_responses.csv")
        responses[0].update(claims_analysis="yes",response_text="We conducted an additional sensitivity analysis and revised the manuscript.")
        save_rows(self.rev, "review_responses.csv", responses)
        _, codes = self.codes()
        self.assertIn("UNKNOWN_RESULT_ID", codes)

    def test_approved_response_missing_human_signoff_blocked(self):
        self.mark_complete()
        responses = load_rows(self.rev, "review_responses.csv")
        responses[0]["approved_by"] = ""
        save_rows(self.rev, "review_responses.csv", responses)
        _, codes = self.codes()
        self.assertIn("RESPONSE_NOT_APPROVED", codes)

    def test_change_location_not_verified(self):
        self.mark_complete()
        changes = load_rows(self.rev, "revision_changes.csv")
        changes[0]["verified_location"] = "page XX"
        save_rows(self.rev, "revision_changes.csv", changes)
        _, codes = self.codes()
        self.assertIn("LOCATION_PLACEHOLDER", codes)

    def test_response_placeholder_not_submission_ready(self):
        self.mark_complete()
        responses = load_rows(self.rev, "review_responses.csv")
        responses[0]["response_text"] = "We have revised [TO_VERIFY: lines]"
        save_rows(self.rev, "review_responses.csv", responses)
        _, codes = self.codes()
        self.assertIn("RESPONSE_PLACEHOLDER", codes)

    def test_disagreement_requires_rationale(self):
        self.mark_complete()
        comments = load_rows(self.rev, "review_comments.csv")
        comments[0].update(decision="disagree", rationale="")
        save_rows(self.rev, "review_comments.csv", comments)
        _, codes = self.codes()
        self.assertIn("REBUTTAL_BASIS", codes)

    def test_multi_round_followup_requires_previous_link(self):
        self.mark_complete()
        meta = json.loads((self.rev / "revision_meta.json").read_text())
        meta["current_round"] = "R2"
        (self.rev / "revision_meta.json").write_text(json.dumps(meta),encoding="utf-8")
        rounds = load_rows(self.rev, "revision_rounds.csv")
        rounds.append(dict(round="R2",decision_letter_source="R2-letter.txt",received_date="2026-11-01",manuscript_version="ms-v3",status="active",notes=""))
        save_rows(self.rev, "revision_rounds.csv", rounds)
        comments = load_rows(self.rev, "review_comments.csv")
        comments.append(dict(comments[0], comment_id="R2-01",round="R2",prior_comment_ids="",origin="followup",decision="clarify",status="resolved"))
        save_rows(self.rev, "review_comments.csv", comments)
        responses = load_rows(self.rev, "review_responses.csv")
        responses.append(dict(responses[0],comment_id="R2-01",claims_revision="no",response_text="We clarified this issue in our response."))
        save_rows(self.rev, "review_responses.csv", responses)
        _, codes = self.codes()
        self.assertIn("FOLLOWUP_SOURCE", codes)

    def test_conflicting_reviews_require_resolution(self):
        self.mark_complete()
        comments = load_rows(self.rev, "review_comments.csv")
        comments[0]["conflict_id"] = "CONFLICT-01"
        comments.append(dict(comments[0], comment_id="R1-02", reviewer="Reviewer 2", decision="clarify", conflict_id="CONFLICT-01"))
        save_rows(self.rev, "review_comments.csv", comments)
        responses = load_rows(self.rev, "review_responses.csv")
        responses.append(dict(responses[0], comment_id="R1-02", claims_revision="no",response_text="Clarified in the letter without a new edit."))
        save_rows(self.rev, "review_responses.csv", responses)
        save_rows(self.rev, "comment_conflicts.csv", [dict(conflict_id="CONFLICT-01", comment_ids="R1-01;R1-02", summary="Reviewers requested conflicting interpretations", resolution="", rationale="", approved_by="", notes="")])
        _, codes = self.codes()
        self.assertIn("CONFLICT_OPEN", codes)

    def test_render_never_overwrites_without_flag(self):
        self.mark_complete()
        command = [sys.executable, str(ROOT / "scripts" / "revision_audit.py"), "render", "--project", str(self.project), "--stage", "submission"]
        first = subprocess.run(command, capture_output=True, text=True)
        second = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(0, first.returncode, first.stderr)
        self.assertEqual(1, second.returncode, second.stderr)

    def test_missing_verified_analysis_never_renders_submission(self):
        self.mark_complete()
        responses = load_rows(self.rev, "review_responses.csv")
        responses[0].update(claims_analysis="yes",response_text="We have performed an additional sensitivity analysis.")
        save_rows(self.rev, "review_responses.csv", responses)
        command = [sys.executable, str(ROOT / "scripts" / "revision_audit.py"), "render", "--project", str(self.project), "--stage", "submission"]
        r = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(2, r.returncode, r.stdout+r.stderr)
        self.assertFalse((self.rev / "response-to-reviewers.md").exists())


if __name__ == "__main__":
    unittest.main()
