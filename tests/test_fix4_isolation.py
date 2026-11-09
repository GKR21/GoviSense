import sqlite3
import json
from pathlib import Path
from govisense.config import settings
from govisense.api.routes.feedback import submit_planting_report, PlantingReportPayload


def test_50k_report_deleted_from_live_stores():
    # 1. Live SQLite check
    live_db = Path("data/database/govisense.db")
    if live_db.exists():
        conn = sqlite3.connect(str(live_db))
        c = conn.cursor()
        c.execute("SELECT count(*) FROM planting_reports WHERE actual_area_ha >= 10000 OR pseudonymous_id LIKE '%STOPRULE%'")
        count = c.fetchone()[0]
        conn.close()
        assert count == 0, f"Found {count} 50k/stoprule reports in live DB!"

    # 2. Live JSON check
    live_json = Path("data/processed/planting_reports.json")
    if live_json.exists():
        with open(live_json) as f:
            data = json.load(f)
        for r in data:
            assert r.get("actual_area_ha", 0) < 10000
            assert "STOPRULE" not in r.get("pseudonymous_id", "")


def test_tests_use_isolated_database():
    # The active test database must be an isolated temporary database, not live govisense.db
    assert "test_isolated.db" in settings.database_url or "test_isolated.db" in settings.fallback_sqlite_url
    assert "data/database/govisense.db" not in settings.database_url
    
    # Submitting a report in a test writes to the isolated DB, not live DB
    initial_live_count = 0
    live_db = Path("data/database/govisense.db")
    if live_db.exists():
        conn = sqlite3.connect(str(live_db))
        c = conn.cursor()
        c.execute("SELECT count(*) FROM planting_reports")
        initial_live_count = c.fetchone()[0]
        conn.close()

    payload = PlantingReportPayload(
        crop="big_onion",
        crop_id="big_onion",
        district="Anuradhapura",
        season="Maha 2025/2026",
        planned_area_ha=3.0,
        actual_area_ha=3.0,
        consent_given=True,
        pseudonymous_id="ISOLATION-TEST-FARMER-99"
    )
    submit_planting_report(payload)

    # Live DB count must remain unchanged
    if live_db.exists():
        conn = sqlite3.connect(str(live_db))
        c = conn.cursor()
        c.execute("SELECT count(*) FROM planting_reports")
        after_live_count = c.fetchone()[0]
        conn.close()
        assert after_live_count == initial_live_count, "Test report leaked into live database!"
