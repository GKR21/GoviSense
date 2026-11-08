"""
Phase 4 Tests: Officer Dashboard Endpoints & Workflows (Proposal 7.3)
Team DARKBITE · ModelX 2.0 Proposal Specification

Verifies that the officer dashboard backend supports:
1. Officer authentication and login (/api/auth/login)
2. Live What-If scenario simulation (/api/simulate)
3. Cryptographic decision logging with SHA-256 record hash (/api/history/log-action & /api/decide)
4. Adoption tracker with real database acreage, adherence, and predicted vs actual (/api/adoption/summary)
5. Differential privacy suppression on ground reports (< 5 records) (/api/feedback/ground-reports)
6. Data catalogue composition (real vs synthetic breakdown) (/api/catalogue/sources-summary)
7. Model accuracy scoreboard (/api/evaluation/scoreboard)
8. Officer alert inbox and guidance notes (/api/alerts & /api/alerts/{id}/officer-note)
"""

from __future__ import annotations

import pytest
from govisense.api.main import (
    load_and_train,
    login_user,
    LoginPayload,
    simulate_scenario,
    SimulationRequest,
    log_officer_action,
    DecisionLogPayload,
    get_adoption_summary,
    list_ground_reports,
    get_sources_summary,
    get_evaluation_scoreboard,
    list_alerts,
    acknowledge_alert,
    AlertAckPayload,
)
from govisense.api.routes.alerts import add_officer_note, OfficerNoteRequest
from govisense.db.session import get_session
from govisense.db.models import DecisionRecordModel, AlertModel


@pytest.fixture(scope="module", autouse=True)
def setup_models():
    """Ensure models and data cache are initialized."""
    load_and_train()


def test_officer_login_flow():
    """Verify officer login returns JWT access token and user metadata."""
    res = login_user(LoginPayload(username="officer1", password="password123"))
    assert "access_token" in res
    assert res["role"] in ["officer", "Officer"]
    assert "user_id" in res


def test_what_if_slider_simulation():
    """Verify simulate_scenario responds live to custom area and yield sliders."""
    res = simulate_scenario(
        SimulationRequest(
            crop="big_onion",
            custom_planted_extent_ha=2500.0,
            custom_yield_mt_ha=18.0,
            custom_loss_pct=0.12,
        )
    )
    assert res["crop"] == "big_onion"
    assert "simulated_supply_mt" in res
    # 2500 * 18 * (1 - 0.12) = 39,600 MT
    expected_supply = round(2500.0 * 18.0 * 0.88, 1)
    assert abs(res["simulated_supply_mt"] - expected_supply) < 1.0
    assert "primary_spi_ratio" in res
    assert "primary_spi_label" in res
    assert "scenarios" in res
    assert "run_id" in res
    assert res["assumptions_ref"] == "docs/assumptions.md"


def test_decision_logging_cryptographic_hash():
    """Verify decision sign-off calculates and stores a 64-char SHA-256 record hash."""
    payload = DecisionLogPayload(
        crop_id="big_onion",
        season="Maha 2025/2026",
        officer_id="OFF-TEST-01",
        action_type="IMPORT_LATER",
        quantity=1500.0,
        unit="MT",
        rationale="High domestic supply projected; deferring scheduled imports by 3 weeks.",
        model_version="LightGBM-v2.1+HiGHS-LP",
        data_version="CBSL-HARTI-DOA-2024.12",
        assumptions={
            "loss_pct": 0.15,
            "lead_time_weeks": 6,
            "district": "Anuradhapura",
        },
    )
    res = log_officer_action(payload)
    assert res["status"] == "RECORDED"
    assert "decision_id" in res
    assert "record_hash" in res
    assert len(res["record_hash"]) == 64  # Valid SHA-256 length

    # Verify record in DB has identical hash
    with get_session() as session:
        rec = session.query(DecisionRecordModel).filter(DecisionRecordModel.decision_id == res["decision_id"]).first()
        assert rec is not None
        assert rec.record_hash == res["record_hash"]


def test_adoption_tracker_summary_metrics():
    """Verify get_adoption_summary returns acreage, adherence, and predicted vs actual."""
    res = get_adoption_summary(crop_id="big_onion", season="Maha 2025/2026")
    assert "acreage" in res
    assert "target_area_ha" in res["acreage"]
    assert "reported_planted_area_ha" in res["acreage"]
    assert "coverage_pct" in res["acreage"]
    assert "recommendation_adherence" in res
    assert "predicted_vs_actual" in res
    pred_vs_act = res["predicted_vs_actual"]
    assert "predicted_production_mt" in pred_vs_act
    assert "actual_harvested_production_mt" in pred_vs_act


def test_ground_reports_differential_privacy():
    """Verify ground reports cohort suppression when fewer than 5 submissions exist."""
    res = list_ground_reports(crop_id="chilli", district="Polonnaruwa")
    if res.get("cohort_count", 0) < 5:
        assert res.get("privacy_suppressed") is True
        assert len(res.get("ground_reports", [])) == 0
        assert "anonymity" in res.get("message", "").lower() or "suppressed" in res.get("message", "").lower()


def test_sources_summary_real_vs_synthetic():
    """Verify get_sources_summary reports exact composition of real vs synthetic data."""
    res = get_sources_summary()
    assert "total_records" in res
    assert "real_count" in res
    assert "interpolated_count" in res
    assert "synthetic_count" in res
    assert "real_pct" in res
    assert res["total_records"] == res["real_count"] + res["interpolated_count"] + res["synthetic_count"]


def test_evaluation_scoreboard_metrics():
    """Verify get_evaluation_scoreboard reports WAPE, baseline comparison, and 80% coverage."""
    res = get_evaluation_scoreboard()
    assert "scoreboard" in res
    assert len(res["scoreboard"]) > 0
    first = res["scoreboard"][0]
    assert "crop" in first
    assert "module" in first
    assert "model_wape" in first
    assert "baseline_wape" in first
    assert "served_model" in first
    assert "interval_80_coverage_pct" in first


def test_officer_alert_note_flow():
    """Verify officer can inspect alerts and append an extension guidance note."""
    alerts = list_alerts(lang="en")
    assert len(alerts) > 0
    target_alert = alerts[0]
    aid = target_alert["alert_id"]

    # Append officer guidance note
    note_res = add_officer_note(
        alert_id=aid,
        req=OfficerNoteRequest(officer_note="District buffer warehouses opened. Hold sales until floor stabilizes."),
    )
    assert note_res["status"] == "NOTE_RECORDED"
    assert "officer_note" in note_res

    # Acknowledge alert
    ack_res = acknowledge_alert(alert_id=aid, payload=AlertAckPayload(ask_officer=False))
    assert ack_res["status"] == "ACKNOWLEDGED"
