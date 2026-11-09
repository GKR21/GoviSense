"""
Tests for Day 5 Fix 4: SPI Thesis Validation & Classification Metrics
"""

import pytest
import pandas as pd
from govisense.models.a3_supply_pressure import SupplyPressureEngine
from govisense.evaluation.backtest import run_walk_forward_evaluation
from govisense.data.clean import load_monthly_dataset, engineer_features


@pytest.fixture(scope="module")
def processed_df():
    raw_df = load_monthly_dataset()
    return engineer_features(raw_df)


def test_spi_historical_thesis_validation(processed_df):
    engine = SupplyPressureEngine()
    results = engine.validate_historical_alignment(processed_df)

    assert "big_onion" in results
    assert "chilli" in results

    bo = results["big_onion"]
    ch = results["chilli"]

    # Big Onion thesis evaluation (computed objectively from empirical correlation)
    assert isinstance(bo["thesis_confirmed"], bool)
    assert bo["confidence_badge"] in ["high", "medium", "low"]
    assert bo["spi_vs_next_month_price_change_corr"] is not None
    assert bo["glut_precision"] is not None
    assert bo["shortage_recall"] is not None
    assert bo["majority_class_baseline_pct"] > 0

    # Chilli fails thesis (price pressure does not follow SPI)
    assert ch["thesis_confirmed"] is False
    assert ch["confidence_badge"] == "low"
    assert "did not follow SPI" in ch["confidence_reason"]


def test_spi_walk_forward_evaluation_metrics():
    report = run_walk_forward_evaluation(["big_onion", "chilli"])

    # Big Onion SPI metrics
    bo_spi = report["big_onion"]["spi_classification"]
    assert "glut_precision" in bo_spi
    assert "shortage_recall" in bo_spi
    assert "majority_class_baseline_pct" in bo_spi
    assert bo_spi["total_eval_points"] > 0

    # Chilli badge and label: "low confidence", "price pressure did not follow SPI"
    ch_spi = report["chilli"]["spi_classification"]
    assert ch_spi["confidence_badge"] == "low confidence"
    assert "price pressure did not follow SPI" in ch_spi["label"]

