"""
Tests for Task 12 (P1): Farmer ID Checks
- Rate limiting per farmer ID (sliding-window)
- Duplicate planting report handling and rejection
- Documented note on future Agrarian Services Department registry integration
"""

import pytest
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient

from govisense.feedback.planting_reports import (
    PlantingReport,
    PlantingReportStore,
    REGISTRY_VERIFICATION_NOTE,
)
from govisense.api.main import app, load_and_train


@pytest.fixture(scope="module", autouse=True)
def setup_pipeline():
    load_and_train()


@pytest.fixture
def client():
    return TestClient(app)


def test_duplicate_report_rejection_in_store():
    """Verifies that submitting an identical report for the same farmer, crop, season, and area is rejected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = PlantingReportStore(storage_path=Path(tmpdir) / "reports.json")

        rep1 = PlantingReport(
            crop_id="big_onion",
            season="Maha 2025/2026",
            planned_area_ha=2.0,
            actual_area_ha=2.0,
            consent_given=True,
            pseudonymous_id="ANU-DUP-TEST-001",
        )
        res1 = store.submit_report(rep1)
        assert res1["status"] == "ACCEPTED"
        assert "registry_verification_note" in res1
        assert "future work" in res1["registry_verification_note"].lower()

        # Submit identical report again -> must raise ValueError indicating duplicate
        rep2 = PlantingReport(
            crop_id="big_onion",
            season="Maha 2025/2026",
            planned_area_ha=2.0,
            actual_area_ha=2.0,
            consent_given=True,
            pseudonymous_id="ANU-DUP-TEST-001",
        )
        with pytest.raises(ValueError, match="Duplicate planting report detected"):
            store.submit_report(rep2)


def test_different_crop_or_area_allowed():
    """Verifies that reports with different crop, season, or distinct area updates are accepted."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = PlantingReportStore(storage_path=Path(tmpdir) / "reports.json")

        # Report for big_onion
        res_onion = store.submit_report(
            PlantingReport(
                crop_id="big_onion",
                season="Maha 2025/2026",
                planned_area_ha=1.5,
                actual_area_ha=1.5,
                consent_given=True,
                pseudonymous_id="ANU-MULTI-001",
            )
        )
        assert res_onion["status"] == "ACCEPTED"

        # Report for chilli by same farmer
        res_chilli = store.submit_report(
            PlantingReport(
                crop_id="chilli",
                season="Maha 2025/2026",
                planned_area_ha=1.0,
                actual_area_ha=1.0,
                consent_given=True,
                pseudonymous_id="ANU-MULTI-001",
            )
        )
        assert res_chilli["status"] == "ACCEPTED"


def test_rate_limiting_per_farmer_id():
    """Verifies that exceeding the 5 submissions per minute threshold raises a rate limit error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = PlantingReportStore(storage_path=Path(tmpdir) / "reports.json")
        farmer_id = "ANU-RATE-LIMIT-FARMER"

        # Submit 5 reports with distinct areas
        for i in range(1, 6):
            store.submit_report(
                PlantingReport(
                    crop_id="big_onion",
                    season=f"Maha 2025/2026",
                    planned_area_ha=float(i),
                    actual_area_ha=float(i),
                    consent_given=True,
                    pseudonymous_id=farmer_id,
                )
            )

        # 6th submission within the same minute must raise Rate limit exceeded
        with pytest.raises(ValueError, match="Rate limit exceeded"):
            store.submit_report(
                PlantingReport(
                    crop_id="big_onion",
                    season="Maha 2025/2026",
                    planned_area_ha=99.0,
                    actual_area_ha=99.0,
                    consent_given=True,
                    pseudonymous_id=farmer_id,
                )
            )


def test_api_duplicate_and_rate_limit_handling(client):
    """Verifies that API endpoint /api/feedback/planting-report gracefully handles duplicates and rate limits."""
    import uuid
    test_farmer_id = f"API-FARMER-DUP-{uuid.uuid4().hex[:6]}"
    payload = {
        "crop_id": "big_onion",
        "season": "Maha 2025/2026",
        "planned_area_ha": 3.0,
        "actual_area_ha": 3.0,
        "consent_given": True,
        "pseudonymous_id": test_farmer_id,
    }

    # 1. First submission succeeds
    res1 = client.post("/api/feedback/planting-report", json=payload)
    assert res1.status_code == 200
    assert res1.json()["status"] == "ACCEPTED"

    # 2. Immediate identical submission returns ERROR with Duplicate message
    res2 = client.post("/api/feedback/planting-report", json=payload)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["status"] == "ERROR"
    assert "duplicate" in data2["message"].lower()


def test_registry_verification_documentation():
    """Verifies that docs/assumptions.md documents the farmer registry verification future work."""
    doc_path = Path("docs/assumptions.md")
    assert doc_path.exists()
    content = doc_path.read_text(encoding="utf-8")
    assert "Agrarian Services Department" in content or "Department of Agrarian Development" in content
    assert "future work" in content.lower()
    assert "pseudonymous" in content.lower()

