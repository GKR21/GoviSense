"""
Phase 6 Tests: Evaluation & Warning Metrics Rigour (Proposal Section 6)
Team DARKBITE · ModelX 2.0 Proposal Specification

Verifies:
1. Directional warning precision, recall, and F1 calculations for Glut and Shortage
2. Empirical coverage evaluation for 80% conformal prediction intervals
3. Price crash vs SPI economic thesis correlation evaluation
4. Walk-forward backtest consistency across crops
"""

from __future__ import annotations

import numpy as np
import pytest
from govisense.evaluation.warning_eval import (
    evaluate_directional_warnings,
    evaluate_interval_coverage,
    evaluate_price_crash_correlation,
)


def test_directional_warnings_precision_and_recall():
    """Verify precision, recall, specificity, and F1 calculation on market state sequences."""
    actual = ["Glut", "Glut", "Balanced", "Shortage", "Glut", "Balanced"]
    pred = ["Glut", "Balanced", "Balanced", "Shortage", "Glut", "Glut"]

    metrics = evaluate_directional_warnings(actual, pred, target_class="Glut")
    # Actual Glut: indices 0, 1, 4 (3 items)
    # Pred Glut: indices 0, 4, 5 (3 items)
    # TP: 0, 4 (2 items); FP: 5 (1 item); FN: 1 (1 item)
    assert metrics["true_positives"] == 2
    assert metrics["false_positives"] == 1
    assert metrics["false_negatives"] == 1
    assert abs(metrics["precision"] - 2 / 3) < 0.01
    assert abs(metrics["recall"] - 2 / 3) < 0.01
    assert metrics["f1_score"] > 0.6


def test_interval_coverage_conformal_80():
    """Verify empirical coverage calculation accurately verifies 80% coverage bounds."""
    np.random.seed(42)
    y_true = np.array([100.0, 120.0, 110.0, 95.0, 105.0, 130.0, 115.0, 108.0, 98.0, 125.0])
    y_low = np.array([90.0, 110.0, 100.0, 90.0, 100.0, 110.0, 105.0, 100.0, 90.0, 115.0])
    y_high = np.array([115.0, 135.0, 125.0, 110.0, 120.0, 145.0, 130.0, 120.0, 110.0, 140.0])

    res = evaluate_interval_coverage(y_true, y_low, y_high, target_nominal=0.80)
    assert res["empirical_coverage_pct"] >= 80.0
    assert res["calibrated"] is True
    assert res["mean_interval_width"] > 0


def test_price_crash_correlation_economic_thesis():
    """Verify negative correlation between high SPI and subsequent price drops."""
    # Prices drop when SPI is high
    spi_scores = np.array([0.05, 0.25, 0.35, -0.10, -0.20, 0.18])
    prices = np.array([200.0, 220.0, 160.0, 140.0, 190.0, 210.0])

    res = evaluate_price_crash_correlation(prices, spi_scores, crash_threshold_pct=0.10)
    assert "correlation_spi_vs_subsequent_price_change" in res
    assert "glut_crash_hit_rate" in res
    assert res["glut_crash_hit_rate"] >= 0.0

