import json
from pathlib import Path

from govisense.config import settings
from govisense.api.routes.feedback import PlantingReportPayload, submit_planting_report
from govisense.db.models import PlantingReportModel
from govisense.db.session import get_active_dialect, get_session


def test_50k_report_deleted_from_live_stores():
    # 1. Legacy SQLite file must remain removed
    assert not Path("data/database/govisense.db").exists(), "Legacy SQLite govisense.db must not exist!"
    assert Path("data/database/db.sql").exists(), "Canonical PostgreSQL schema data/database/db.sql must exist!"

    # 2. Live JSON check
    live_json = Path("data/processed/planting_reports.json")
    if live_json.exists():
        with open(live_json, encoding="utf-8") as f:
            data = json.load(f)
        for r in data:
            assert r.get("actual_area_ha", 0) < 10000
            assert "STOPRULE" not in r.get("pseudonymous_id", "")


def test_tests_use_isolated_postgresql_database():
    # Active test database must be an isolated PostgreSQL test DB initialized from db.sql
    assert get_active_dialect() == "postgresql"
    assert "govisense_test_" in settings.database_url

    with get_session() as session:
        initial_count = session.query(PlantingReportModel).count()

    payload = PlantingReportPayload(
        crop_id="big_onion",
        district="Anuradhapura",
        season="Maha 2025/2026",
        planned_area_ha=3.0,
        actual_area_ha=3.0,
        consent_given=True,
        pseudonymous_id="ISOLATION-TEST-FARMER-99",
    )
    res = submit_planting_report(payload)
    assert res["status"] == "ACCEPTED"

    with get_session() as session:
        after_count = session.query(PlantingReportModel).count()
    assert after_count == initial_count + 1
