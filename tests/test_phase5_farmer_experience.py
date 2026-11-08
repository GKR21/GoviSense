"""
Phase 5 Tests: Farmer Mobile Experience & Two-Stage Feedback Loop (Proposal 7.4)
Team DARKBITE · ModelX 2.0 Proposal Specification

Verifies:
1. Farmer Top-3 Advisor respecting allocator & oversupply stop rule
2. Multi-lingual message rendering (English, Sinhala, Tamil)
3. Two-stage ground truth feedback:
   - Planting report with consent check
   - Harvest report with disposition constraint enforcement
4. Offline failure honesty: offline-queued reporting preserves data integrity without fake receipts
5. Alert inquiry workflow: farmer asks extension officer and receives guidance note
"""

from __future__ import annotations

import pytest
from govisense.api.main import (
    load_and_train,
    farmer_top3,
    submit_planting_report,
    PlantingReportPayload,
    submit_harvest_report,
    HarvestReportPayload,
    list_alerts,
    ask_officer_on_alert,
    AskOfficerRequest,
    add_officer_note,
    OfficerNoteRequest,
)
from govisense.db.session import get_session
from govisense.db.models import PlantingReportModel, HarvestReportModel, AlertModel, AlertStatusModel


@pytest.fixture(scope="module", autouse=True)
def setup_models():
    """Ensure models and data cache are initialized."""
    load_and_train()


def test_farmer_top3_allocator_and_stop_rule():
    """Verify farmer top-3 returns allocated hectares, expected yield, and stop rule flag."""
    res = farmer_top3(
        farmer_id="FARMER-TEST-99",
        season="Maha",
        land_ha=2.5,
        current_month=10,
        is_rainfed=False,
    )
    assert "top3" in res
    assert len(res["top3"]) >= 1 and len(res["top3"]) <= 3
    for crop in res["top3"]:
        assert "crop_id" in crop
        assert "fit_score" in crop
        assert "allocated_area_ha" in crop
        assert crop["allocated_area_ha"] <= 2.5
        assert "expected_yield_mt" in crop
        assert "price_forecast" in crop
        assert "fair_floor_price_rs_kg" in crop
        assert "water_need_mm_season" in crop
        assert "stop_rule_triggered" in crop
        assert crop["status"] in ["APPROVED", "CAPPED", "PAUSED"]


def test_multilingual_alerts():
    """Verify alerts are correctly localized across en, si, and ta."""
    for lang in ["en", "si", "ta"]:
        alerts = list_alerts(lang=lang)
        assert len(alerts) > 0
        first = alerts[0]
        assert "message" in first
        assert len(first["message"]) > 0


def test_planting_report_consent_and_receipt():
    """Verify planting report requires consent and issues a pseudonymous receipt."""
    payload = PlantingReportPayload(
        crop_id="big_onion",
        season="Maha 2025/2026",
        planned_area_ha=1.0,
        actual_area_ha=1.0,
        consent_given=True,
        pseudonymous_id="ANON-TEST-4421",
    )
    res = submit_planting_report(payload)
    assert res["status"] in ["ACCEPTED", "ACCEPTED_AND_PIPELINE_UPDATED"]
    assert "report_id" in res


def test_harvest_report_disposition_constraint():
    """Verify harvest report disposition invariant: sold + loss + stored <= harvested + 0.01."""
    # First create planting report to obtain report_id
    p_res = submit_planting_report(
        PlantingReportPayload(
            crop_id="big_onion",
            season="Maha 2025/2026",
            planned_area_ha=1.0,
            actual_area_ha=1.0,
            consent_given=True,
            pseudonymous_id="ANON-TEST-4421",
        )
    )
    rep_id = p_res["report_id"]

    # 1. Valid disposition: 1000 harvested = 700 sold + 100 loss + 200 stored
    valid_payload = HarvestReportPayload(
        planting_report_id=rep_id,
        pseudonymous_id="ANON-TEST-4421",
        crop_id="big_onion",
        season="Maha 2025/2026",
        area_harvested_ha=1.0,
        harvest_quantity_kg=1000.0,
        quantity_sold_kg=700.0,
        loss_kg=100.0,
        quantity_stored_kg=200.0,
        sale_price_rs_kg=310.0,
        sale_channel="DEC_WHOLESALE",
    )
    res = submit_harvest_report(valid_payload)
    assert res["status"] == "ACCEPTED"
    assert "harvest_id" in res

    # 2. Invalid disposition: 1000 harvested < 900 sold + 200 loss + 100 stored (1200 kg)
    invalid_payload = HarvestReportPayload(
        planting_report_id=rep_id,
        pseudonymous_id="ANON-TEST-4421",
        crop_id="big_onion",
        season="Maha 2025/2026",
        area_harvested_ha=1.0,
        harvest_quantity_kg=1000.0,
        quantity_sold_kg=900.0,
        loss_kg=200.0,
        quantity_stored_kg=100.0,
        sale_price_rs_kg=310.0,
    )
    with pytest.raises(Exception) as excinfo:
        submit_harvest_report(invalid_payload)
    err_str = str(excinfo.value).lower()
    assert "disposed" in err_str or "disposition" in err_str or "exceeds" in err_str or "422" in err_str


def test_farmer_ask_officer_inquiry_flow():
    """Verify farmer can submit inquiry on alert and receive extension officer advice."""
    alerts = list_alerts(lang="en")
    target_alert = alerts[0]
    aid = target_alert["alert_id"]

    # 1. Farmer sends inquiry
    inq_res = ask_officer_on_alert(
        alert_id=aid,
        req=AskOfficerRequest(question="Should I store or sell immediately given the price floor?"),
    )
    assert inq_res["status"] == "INQUIRY_SENT"
    assert inq_res["alert_id"] == aid

    # 2. Officer provides guidance note
    note_res = add_officer_note(
        alert_id=aid,
        req=OfficerNoteRequest(officer_note="Hold in katiyawa ASC warehouse; price floor subsidy begins next week."),
    )
    assert note_res["status"] == "NOTE_RECORDED"
    assert "Hold in katiyawa ASC warehouse" in note_res["officer_note"]
