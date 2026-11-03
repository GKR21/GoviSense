"""
Tests for Day 6 Item 8: Confidence Badge Rules & Decision History Audit
"""

import pytest
import tempfile
from pathlib import Path
from govisense.db.history import (
    evaluate_confidence_badge,
    DecisionRecord,
    DecisionHistoryStore,
)


def test_confidence_badge_5_rules():
    # 1. High confidence: All 5 rules pass
    eval_high = evaluate_confidence_badge(
        crop_id="big_onion",
        data_age_days=20,          # Rule 1: Fresh <= 45
        area_reported_share=0.40,  # Rule 2: Adequate >= 20%
        model_wape=0.14,           # Rule 3: Model beats baseline
        baseline_wape=0.22,
        spi_validated=True,        # Rule 4: SPI thesis verified
        soil_ph_available=True,    # Rule 5: Soil pH present
    )
    assert eval_high.badge == "high"
    assert eval_high.score_pct == 100.0
    assert eval_high.data_fresh is True
    assert eval_high.area_reported_share_adequate is True
    assert eval_high.model_beats_baseline is True
    assert eval_high.spi_validation_passed is True
    assert eval_high.soil_data_present is True

    # 2. Low confidence: Chili decoupling rule (SPI thesis unverified)
    eval_chilli = evaluate_confidence_badge(
        crop_id="chilli",
        data_age_days=10,
        area_reported_share=0.30,
        model_wape=0.12,
        baseline_wape=0.18,
        spi_validated=False,       # Decoupled
        soil_ph_available=True,
    )
    assert eval_chilli.badge == "low"
    assert eval_chilli.spi_validation_passed is False

    # 3. Medium confidence: Stale data and no soil data
    eval_med = evaluate_confidence_badge(
        crop_id="big_onion",
        data_age_days=60,          # Stale > 45 days
        area_reported_share=0.15,  # Low < 20%
        model_wape=0.15,
        baseline_wape=0.20,
        spi_validated=True,
        soil_ph_available=False,   # Missing
    )
    assert eval_med.badge in ["medium", "low"]


def test_decision_history_audit_logging():
    with tempfile.TemporaryDirectory() as tmpdir:
        history_path = Path(tmpdir) / "history.json"
        store = DecisionHistoryStore(storage_path=history_path)

        record = DecisionRecord(
            crop_id="big_onion",
            season="Maha 2025/2026",
            officer_id="OFFICER-DAMBULLA-07",
            action_type="HOLD_STORAGE",
            quantity=3500.0,
            unit="MT",
            rationale="Activate cold room buffer to protect floor price of Rs 120/kg.",
            assumptions={
                "loss_pct": 0.15,
                "safety_buffer": 0.05,
                "spi_bands": 0.15,
            },
        )

        res = store.log_decision(record)
        assert res["status"] == "RECORDED"
        assert res["decision_id"].startswith("DEC-")

        # Retrieve and verify persistence
        history = store.list_decisions(crop_id="big_onion")
        assert len(history) == 1
        item = history[0]
        assert item.officer_id == "OFFICER-DAMBULLA-07"
        assert item.action_type == "HOLD_STORAGE"
        assert item.quantity == 3500.0
        assert item.assumptions["loss_pct"] == 0.15
        assert item.model_version.startswith("GoviSense")

