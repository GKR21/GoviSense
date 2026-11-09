import pytest
from unittest.mock import patch
from fastapi import HTTPException
from govisense.feedback.planting_reports import PlantingReportStore
from govisense.api.routes.farmer import farmer_top3_recommendations


def test_planting_report_store_no_silent_json_fallback_on_db_error():
    store = PlantingReportStore(sync_db=True)
    with patch("govisense.feedback.planting_reports.get_session", side_effect=Exception("Database connection died")):
        with pytest.raises(RuntimeError) as exc_info:
            store.get_reports(crop_id="big_onion")
        assert "Database error querying planting reports" in str(exc_info.value)


def test_farmer_top3_no_silent_5000_demand_fallback():
    with patch("govisense.api.routes.farmer.demand_estimator.estimate", side_effect=Exception("Demand model uncalibrated")):
        with pytest.raises(HTTPException) as exc_info:
            farmer_top3_recommendations(district="Anuradhapura", current_month=5)
        assert exc_info.value.status_code in (500, 503)
        assert "Demand estimation" in exc_info.value.detail

