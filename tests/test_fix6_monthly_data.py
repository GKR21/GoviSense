import pytest
import pandas as pd
from govisense.db.session import get_session, init_db
from govisense.db.models import MonthlyDataModel
from govisense.provenance import compute_dataset_provenance
from govisense.api.main import get_latest_forecasts
from govisense.api.routes.farmer import farmer_top3_recommendations
from govisense.api.routes.data import get_evaluation_scoreboard


def test_monthly_data_table_populated_with_master_data():
    init_db()
    with get_session() as session:
        count = session.query(MonthlyDataModel).count()
        assert count == 168, f"Expected 168 rows in monthly_data table, got {count}"
        
        # Verify source_type distribution
        real_cnt = session.query(MonthlyDataModel).filter(MonthlyDataModel.source_type == "real").count()
        anchor_cnt = session.query(MonthlyDataModel).filter(MonthlyDataModel.source_type == "anchor").count()
        interp_cnt = session.query(MonthlyDataModel).filter(MonthlyDataModel.source_type == "interpolated").count()
        
        assert real_cnt == 140
        assert anchor_cnt == 22
        assert interp_cnt == 6


def test_compute_dataset_provenance_logic():
    # 1. Real / Anchor data
    df_real = pd.DataFrame([{"source_type": "real"}, {"source_type": "anchor"}])
    p_real = compute_dataset_provenance(df_real)
    assert p_real["data_quality"] == "real"
    assert p_real["is_demo"] is False
    assert isinstance(p_real["db_fallback"], bool)

    # 2. Interpolated data
    df_interp = pd.DataFrame([{"source_type": "real"}, {"source_type": "interpolated"}])
    p_interp = compute_dataset_provenance(df_interp)
    assert p_interp["data_quality"] == "interpolated"
    assert p_interp["is_demo"] is False

    # 3. Synthetic demo data
    df_synth = pd.DataFrame([{"source_type": "real"}, {"source_type": "synthetic"}])
    p_synth = compute_dataset_provenance(df_synth)
    assert p_synth["data_quality"] == "synthetic"
    assert p_synth["is_demo"] is True

    # 4. Empty data
    p_empty = compute_dataset_provenance(pd.DataFrame())
    assert p_empty["data_quality"] == "no_data"


def test_model_responses_include_db_fallback():
    # 1. Latest forecasts
    f_res = get_latest_forecasts()
    assert "db_fallback" in f_res
    assert isinstance(f_res["db_fallback"], bool)
    assert "data_quality" in f_res
    assert "is_demo" in f_res

    # 2. Farmer top 3
    t_res = farmer_top3_recommendations()
    assert "db_fallback" in t_res
    assert isinstance(t_res["db_fallback"], bool)
    assert "data_quality" in t_res
    assert "is_demo" in t_res

    # 3. Evaluation scoreboard
    s_res = get_evaluation_scoreboard()
    assert "db_fallback" in s_res
    assert isinstance(s_res["db_fallback"], bool)
    assert "data_quality" in s_res
    assert "is_demo" in s_res

