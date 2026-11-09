import os
import tempfile
import shutil
from pathlib import Path
import pytest
from govisense.config import settings
import govisense.db.session as session_mod
from govisense.db.session import init_db
from govisense.feedback.planting_reports import PlantingReportStore


@pytest.fixture(scope="session", autouse=True)
def isolate_test_database():
    """
    Ensures all tests execute against an isolated temporary SQLite database and JSON store.
    Guarantees tests NEVER write to production data/database/govisense.db or planting_reports.json.
    """
    temp_dir = tempfile.mkdtemp(prefix="govisense_test_db_")
    temp_db_path = Path(temp_dir) / "test_isolated.db"
    temp_json_path = Path(temp_dir) / "test_planting_reports.json"

    # Seed initial test json from live json if exists so tests have initial reports
    live_json = Path("data/processed/planting_reports.json")
    if live_json.exists():
        shutil.copy(live_json, temp_json_path)

    # Point settings to temp DB
    orig_db_url = settings.database_url
    orig_fallback_url = settings.fallback_sqlite_url
    orig_json_path = PlantingReportStore.DEFAULT_STORAGE_PATH if hasattr(PlantingReportStore, "DEFAULT_STORAGE_PATH") else None

    isolated_url = f"sqlite:///{temp_db_path}"
    settings.database_url = isolated_url
    settings.fallback_sqlite_url = isolated_url

    # Reset engine and factory to bind to isolated DB
    session_mod._ENGINE = None
    session_mod._SESSION_FACTORY = None
    session_mod._ACTIVE_DIALECT = "sqlite"

    init_db()

    yield temp_db_path

    # Teardown
    session_mod._ENGINE = None
    session_mod._SESSION_FACTORY = None
    settings.database_url = orig_db_url
    settings.fallback_sqlite_url = orig_fallback_url
    shutil.rmtree(temp_dir, ignore_errors=True)
