"""
Test Fix F7: Multi-Horizon Backtest (t+1..t+3) and Last-Value / Seasonal-Naive Baselines
Team DARKBITE · ModelX 2.0 Completion
"""

import pytest
from govisense.evaluation.backtest import run_walk_forward_evaluation
from govisense.api.routes.data import get_evaluation_scoreboard
from govisense.db.session import get_session
from govisense.db.models import EvaluationResultModel


def test_walk_forward_multi_horizon_evaluation():
    """
    Verify run_walk_forward_evaluation computes metrics across t+1, t+2, and t+3
    and evaluates against both seasonal naive (t-12) and last-value baselines.
    """
    report = run_walk_forward_evaluation(crops=["big_onion", "chilli"])
    assert "_metadata" in report

    for crop in ["big_onion", "chilli"]:
        assert crop in report
        c_res = report[crop]
        assert "horizons" in c_res
        horizons = c_res["horizons"]

        # Check horizons t+1, t+2, t+3 are all evaluated
        for h in [1, 2, 3]:
            h_key = f"t+{h}"
            assert h_key in horizons
            h_data = horizons[h_key]
            assert h_data["n_eval_points"] == 8

            # A1 Supply forecast checks
            a1_data = h_data["a1_supply"]
            assert a1_data["wape_model"] is not None
            assert a1_data["wape_seasonal_naive"] is not None
            assert a1_data["wape_last_value"] is not None

            # A2 Price forecast checks
            a2_data = h_data["a2_price"]
            assert a2_data["wape_model"] is not None
            assert a2_data["wape_seasonal_naive"] is not None
            assert a2_data["wape_last_value"] is not None
            assert a2_data["wape_sarimax"] is not None

        # Check multi_horizon_rows have baseline_name populated
        mh_rows = c_res.get("multi_horizon_rows", [])
        assert len(mh_rows) > 0
        baseline_names = {r["baseline_name"] for r in mh_rows}
        assert "seasonal_naive" in baseline_names
        assert "last_value" in baseline_names
        assert "SARIMAX" in baseline_names


def test_scoreboard_persists_baseline_names():
    """
    Verify that calling get_evaluation_scoreboard saves rows with
    explicit baseline_name values to EvaluationResultModel.
    """
    with get_session() as session:
        # Clear existing rows to test live population
        session.query(EvaluationResultModel).delete()
        session.commit()

    resp = get_evaluation_scoreboard()
    assert "scoreboard" in resp
    assert len(resp["scoreboard"]) > 0

    with get_session() as session:
        stored = session.query(EvaluationResultModel).all()
        assert len(stored) > 0
        baselines = {r.baseline_name for r in stored if r.baseline_name}
        assert "seasonal_naive" in baselines
        assert "last_value" in baselines
        assert "SARIMAX" in baselines

        # Verify periods include t+1, t+2, t+3
        periods = {r.evaluation_period for r in stored if r.evaluation_period}
        assert "walk-forward_t+1" in periods
        assert "walk-forward_t+2" in periods
        assert "walk-forward_t+3" in periods

