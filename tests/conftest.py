import os
import shutil
import tempfile
import urllib.parse
import uuid
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

from govisense.config import settings
import govisense.db.session as session_mod
from govisense.db.session import _normalize_db_url, init_db


def _build_db_url(base_url: str, db_name: str) -> str:
    parsed = urllib.parse.urlsplit(base_url)
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, f"/{db_name}", parsed.query, parsed.fragment))


@pytest.fixture(scope="session", autouse=True)
def isolate_test_database():
    """
    Configures all tests to run strictly against an isolated PostgreSQL database
    initialized from data/database/db.sql (no SQLite fallback).
    """
    base_url = _normalize_db_url(os.getenv("TEST_DATABASE_URL") or settings.database_url)
    if "postgresql" not in base_url:
        raise RuntimeError(f"Tests require PostgreSQL DATABASE_URL (got '{base_url}').")

    parsed = urllib.parse.urlsplit(base_url)
    admin_db = parsed.path.lstrip("/") or "postgres"
    test_db_name = f"govisense_test_{uuid.uuid4().hex[:8]}"

    admin_url = _build_db_url(base_url, admin_db)
    isolated_url = _build_db_url(base_url, test_db_name)

    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT", connect_args={"connect_timeout": 10})
    with admin_engine.connect() as conn:
        conn.execute(text(f'CREATE DATABASE "{test_db_name}"'))

    temp_dir = tempfile.mkdtemp(prefix="govisense_test_json_")
    temp_json_path = Path(temp_dir) / "test_planting_reports.json"
    live_json = Path("data/processed/planting_reports.json")
    if live_json.exists():
        shutil.copy(live_json, temp_json_path)

    orig_db_url = settings.database_url
    settings.database_url = isolated_url

    session_mod._ENGINE = None
    session_mod._SESSION_FACTORY = None
    session_mod._ACTIVE_DIALECT = "postgresql"

    try:
        init_db()
        yield isolated_url
    finally:
        if session_mod._ENGINE is not None:
            session_mod._ENGINE.dispose()
        session_mod._ENGINE = None
        session_mod._SESSION_FACTORY = None
        settings.database_url = orig_db_url

        try:
            with admin_engine.connect() as conn:
                conn.execute(
                    text(
                        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                        "WHERE datname = :db AND pid <> pg_backend_pid()"
                    ),
                    {"db": test_db_name},
                )
                conn.execute(text(f'DROP DATABASE IF EXISTS "{test_db_name}"'))
        finally:
            admin_engine.dispose()
            shutil.rmtree(temp_dir, ignore_errors=True)
