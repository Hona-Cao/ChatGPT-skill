"""Synthetic, nonclinical test fixtures for the local audit CLI."""

import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("manuscript_audit", SKILL / "scripts" / "manuscript_audit.py")
mod = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def write_csv(path, rows, columns):
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.p = Path(self.tmp.name) / "project"
        self.assertEqual(0, mod.create_project(self.p))

    def complete_project(self, with_secondary=True):
        study = json.loads((self.p / "study.json").read_text())
        study.update({
            "study_id": "SYN-001", "title": "Synthetic audit validation only",
            "objective": "Evaluate an illustrative exposure and example outcome",
            "population": "Imaginary participants; not real patient data",
            "main_outcome": "Fictional outcome", "primary_design": "cohort",
            "secondary_components": ["prediction_model"] if with_secondary else [],
            "routine_health_data": True, "analysis_software": ["R 4.4"],
            "analysis_plan_status": "confirmed", "target_journal": "Test Journal",
            "data_handling_confirmed": True,
            "official_checklist_complete": True,
            "human_signoff": True,
        })
        (self.p / "study.json").write_text(json.dumps(study), encoding="utf-8")
        write_csv(self.p / "results.csv", [{
            "result_id": "RES-001", "role": "primary",
            "source_file": "synthetic-test-table.csv", "source_location": "row 2",
            "population": "fictional sample", "outcome": "illustrative outcome",
            "comparison": "A vs B", "model": "adjusted logistic model",
            "effect_measure": "OR", "estimate": "1.40", "ci_lower": "1.10",
            "ci_upper": "1.85", "ci_level": "95", "p_value": "0.008",
            "sample_n": "400", "events_n": "80", "denominator_n": "400",
            "timepoint": "study period", "adjustment_set": "age, sex",
            "prespecified": "yes", "notes": "Synthetic values: do not cite as evidence",
        }], mod.REQUIRED_COLUMNS["results.csv"])
        write_csv(self.p / "references.csv", [{
            "reference_id": "REF-001", "title": "Fictional publication for schema validation",
            "doi": "10.1234/synthetic.1", "pmid": "", "source_url": "",
            "verification_status": "verified", "verified_passage": "Synthetic passage checked by test fixture only",
            "notes": "This is not a real literature source",
        }], mod.REQUIRED_COLUMNS["references.csv"])
        write_csv(self.p / "claims.csv", [
            {
                "claim_id": "CLM-001", "section": "Results", "claim_type": "result",
                "claim_text": "The odds were higher in group A in this fictional dataset",
                "result_ids": "RES-001", "reference_ids": "", "status": "approved",
                "notes": "Test-only human-signoff flag",
            },
            {
                "claim_id": "CLM-002", "section": "Introduction", "claim_type": "literature",
                "claim_text": "Illustrative background assertion in synthetic fixture",
                "result_ids": "", "reference_ids": "REF-001", "status": "approved",
                "notes": "Synthetic bibliographic metadata, not for publication",
            },
        ], mod.REQUIRED_COLUMNS["claims.csv"])
        guides = ["STROBE", "RECORD", "TRIPOD+AI"] if with_secondary else ["STROBE", "RECORD"]
        write_csv(self.p / "reporting_checklist.csv", [
            {"guideline": g, "item_id": "synthetic-demo", "status": "present",
             "manuscript_location": "Methods, paragraph 1", "notes": "Synthetic demo only; not a complete checklist",
             "official_url": mod.GUIDELINE_URLS[g]} for g in guides
        ], mod.REQUIRED_COLUMNS["reporting_checklist.csv"])
        draft = """# Fictional manuscript (test fixture only)

## Abstract

Synthetic objective, fictional methods, and illustrative result.

## Introduction

A fake background claim used solely for testing citation linkage. [REF:REF-001]

## Methods

This is synthetic data, no real participants and no actual study.

## Results

In a made-up model the OR was 1.40 (95% CI 1.10 to 1.85). [R:RES-001]

## Discussion

This paragraph is solely for checking structural requirements; it has no clinical applicability.
"""
        (self.p / "manuscript/draft.md").write_text(draft, encoding="utf-8")

    def test_blank_drafting_is_warnings_not_fake_completion(self):
        auditor = mod.Auditor(self.p, "drafting")
        auditor.run()
        self.assertFalse(auditor.has_blockers())
        self.assertIn("NO_RESULTS", [i.code for i in auditor.issues])
        self.assertIn("DESIGN_MISSING", [i.code for i in auditor.issues])

    def test_blank_submission_is_blocked(self):
        auditor = mod.Auditor(self.p, "submission")
        auditor.run()
        self.assertTrue(auditor.has_blockers())
        self.assertIn("HUMAN_SIGNOFF", [i.code for i in auditor.issues])
        self.assertIn("CHECKLIST_ATTESTATION", [i.code for i in auditor.issues])

    def test_combined_guideline_routing_and_clean_synthetic_registry(self):
        self.complete_project()
        auditor = mod.Auditor(self.p, "submission")
        auditor.run()
        self.assertEqual(["STROBE", "TRIPOD+AI", "RECORD"], auditor.guidelines)
        self.assertFalse(auditor.has_blockers(), auditor.report())
        self.assertEqual(0, sum(i.severity == "WARNING" for i in auditor.issues), auditor.report())

    def test_detect_invalid_numeric_and_reference(self):
        self.complete_project(with_secondary=False)
        path = self.p / "results.csv"
        with path.open(encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
        rows[0]["ci_lower"] = "2.0"  # CI is reversed and point estimate outside it
        rows[0]["p_value"] = "0.000"  # exact zero cannot be reported
        write_csv(path, rows, mod.REQUIRED_COLUMNS["results.csv"])
        claims = self.p / "claims.csv"
        with claims.open(encoding="utf-8", newline="") as fh:
            cl = list(csv.DictReader(fh))
        cl[1]["reference_ids"] = "REF-UNKNOWN"
        write_csv(claims, cl, mod.REQUIRED_COLUMNS["claims.csv"])
        auditor = mod.Auditor(self.p, "submission")
        auditor.run()
        self.assertTrue(auditor.has_blockers())
        codes = {i.code for i in auditor.issues}
        self.assertIn("CI_ORDER", codes)
        self.assertIn("P_ZERO", codes)
        self.assertIn("UNKNOWN_REFERENCE_ID", codes)

    def test_ci_p_heuristic_is_not_a_certainty(self):
        self.complete_project(with_secondary=False)
        path = self.p / "results.csv"
        with path.open(encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
        rows[0]["p_value"] = "0.45"
        write_csv(path, rows, mod.REQUIRED_COLUMNS["results.csv"])
        auditor = mod.Auditor(self.p, "drafting")
        auditor.run()
        self.assertTrue(any(i.code == "P_CI_POSSIBLE_MISMATCH" and i.severity == "WARNING" for i in auditor.issues))
        self.assertFalse(auditor.has_blockers())

    def test_guideline_extension_for_ai_diagnostic(self):
        self.complete_project(with_secondary=False)
        study = json.loads((self.p / "study.json").read_text())
        study.update(primary_design="diagnostic_accuracy", secondary_components=[], routine_health_data=False, ai_diagnostic=True)
        auditor = mod.Auditor(self.p, "drafting")
        self.assertEqual(["STARD 2015", "STARD-AI"], auditor.get_guidelines(study))


if __name__ == "__main__":
    unittest.main()
