import numpy as np
import pytest
from govisense.evaluation.warning_eval import (
    derive_ground_truth_from_prices,
    bootstrap_metric_ci,
    evaluate_spi_against_price_ground_truth,
)
from govisense.data.clean import load_monthly_dataset


def test_derive_ground_truth_from_prices():
    # Price dropping from 100 to 80 is -20% -> Glut
    # Price rising from 80 to 110 is +37.5% -> Shortage
    # Price changing from 110 to 115 is +4.5% -> Balanced
    prices = np.array([100.0, 80.0, 110.0, 115.0])
    labels = derive_ground_truth_from_prices(prices, threshold_pct=0.15)
    assert labels[0] == "Glut"
    assert labels[1] == "Shortage"
    assert labels[2] == "Balanced"


def test_degenerate_case_reported_as_not_evaluable():
    # When all predictions are Glut or all ground truth are Glut
    prices = np.array([100.0, 100.0, 100.0, 100.0, 100.0])  # all Balanced
    all_glut_preds = ["Glut"] * len(prices)
    res = evaluate_spi_against_price_ground_truth(prices, all_glut_preds, target_class="Glut")
    assert res["status"] == "not evaluable"
    assert "Degenerate" in res["reason"]


def test_real_dataset_spi_warning_evaluation():
    raw_df = load_monthly_dataset()
    big_onion_df = raw_df[raw_df["crop"] == "big_onion"].sort_values("date")
    prices = big_onion_df["wholesale_price_rs_kg"].values
    
    # Model predictions
    spi_preds = ["Glut" if spi > 0.15 else ("Shortage" if spi < -0.15 else "Balanced") for spi in big_onion_df["actual_spi"].values]
    
    eval_res = evaluate_spi_against_price_ground_truth(prices, spi_preds, target_class="Glut")
    assert eval_res["status"] in ("evaluable", "not evaluable")
    if eval_res["status"] == "evaluable":
        assert "precision_ci" in eval_res["model"]
        assert "recall_ci" in eval_res["model"]
        assert "f1_ci" in eval_res["model"]
        assert "always_balanced_baseline" in eval_res
        assert "random_baseline" in eval_res
        assert eval_res["sample_size"] == len(prices)

