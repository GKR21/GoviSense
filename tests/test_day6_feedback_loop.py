"""
Tests for Day 6 Item 7: Feedback Loop & Planting Reports
"""

import pytest
import tempfile
from pathlib import Path
from govisense.feedback.planting_reports import (
    PlantingReport,
    PlantingReportStore,
    ReTriggerResult,
)


def test_planting_report_consent_and_validation():
    with tempfile.TemporaryDirectory() as tmpdir:
        store_path = Path(tmpdir) / "reports.json"
        store = PlantingReportStore(storage_path=store_path)

        # 1. Reject without explicit consent
        with pytest.raises(ValueError, match="Consent is required"):
            store.submit_report(
                PlantingReport(
                    crop_id="big_onion",
                    season="Maha 2025/2026",
                    planned_area_ha=5.0,
                    actual_area_ha=4.5,
                    consent_given=False,
                    pseudonymous_id="ANU-FARMER-999",
                )
            )

        # 2. Reject negative areas
        with pytest.raises(ValueError, match="cannot be negative"):
            store.submit_report(
                PlantingReport(
                    crop_id="big_onion",
                    season="Maha 2025/2026",
                    planned_area_ha=-1.0,
                    actual_area_ha=2.0,
                    consent_given=True,
                    pseudonymous_id="ANU-FARMER-999",
                )
            )

        # 3. Successful submission
        res = store.submit_report(
            PlantingReport(
                crop_id="big_onion",
                season="Maha 2025/2026",
                planned_area_ha=5.0,
                actual_area_ha=4.5,
                consent_given=True,
                pseudonymous_id="ANU-FARMER-001",
            )
        )
        assert res["status"] == "ACCEPTED"
        assert res["cumulative_reported_ha"] == pytest.approx(4.5)


def test_planting_report_retrigger_updates_pipeline():
    with tempfile.TemporaryDirectory() as tmpdir:
        store_path = Path(tmpdir) / "reports.json"
        store = PlantingReportStore(storage_path=store_path)

        # Farmer 1 reports 300 ha
        store.submit_report(
            PlantingReport(
                crop_id="big_onion",
                season="Maha 2025/2026",
                planned_area_ha=300.0,
                actual_area_ha=300.0,
                consent_given=True,
                pseudonymous_id="F-1",
            )
        )

        retrigger = store.retrigger_crop(
            crop_id="big_onion",
            season="Maha 2025/2026",
            target_month=4,
        )

        assert isinstance(retrigger, ReTriggerResult)
        assert retrigger.crop_id == "big_onion"
        assert retrigger.total_reported_ha == pytest.approx(300.0)
        # New recommended area should reflect reported acreage
        assert retrigger.new_a_rec_ha <= retrigger.previous_target_ha
        assert not retrigger.oversupply_stop_triggered


def test_planting_report_oversupply_stop_rule_trigger():
    with tempfile.TemporaryDirectory() as tmpdir:
        store_path = Path(tmpdir) / "reports.json"
        store = PlantingReportStore(storage_path=store_path)

        # Massive bumper acreage reported (e.g. 5,000 ha > 110% of target)
        store.submit_report(
            PlantingReport(
                crop_id="big_onion",
                season="Maha 2025/2026",
                planned_area_ha=5000.0,
                actual_area_ha=5000.0,
                consent_given=True,
                pseudonymous_id="COOP-ANURADHAPURA",
            )
        )

        retrigger = store.retrigger_crop(
            crop_id="big_onion",
            season="Maha 2025/2026",
            target_month=4,
        )
        # A_rec must drop to 0 under oversupply stop rule
        assert retrigger.oversupply_stop_triggered is True
        assert retrigger.new_a_rec_ha == 0.0
        assert "STOP" in retrigger.action_summary
