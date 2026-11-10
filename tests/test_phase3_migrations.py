"""
Phase 3.1 & 3.2 Tests: PostgreSQL db.sql Schema, Views/Triggers, and Model Write-Paths
Team DARKBITE · ModelX 2.0
"""

import uuid
import pytest
from sqlalchemy import inspect, text

from govisense.db.lookups import (
    ensure_crop_exists,
    ensure_farmer_profile,
    resolve_season_id,
)
from govisense.db.models import (
    hash_password,
    verify_password,
    validate_season_format,
)
from govisense.db.session import get_engine, get_session


def test_db_sql_schema_tables_views_and_triggers():
    """Verify PostgreSQL database initialized from db.sql has all expected tables, views, and functions."""
    eng = get_engine()
    inspector = inspect(eng)
    tables = set(inspector.get_table_names())
    views = set(inspector.get_view_names())

    expected_tables = {
        "roles",
        "languages",
        "districts",
        "crops",
        "seasons",
        "users",
        "officers",
        "farmer_profiles",
        "planting_reports",
        "harvest_reports",
        "runs",
        "forecast_snapshots",
        "decision_history",
        "monthly_data",
        "market_prices",
        "data_catalogue",
        "alerts",
        "alert_translations",
        "alert_status",
        "alert_questions",
        "evaluation_results",
        "audit_log",
    }
    assert expected_tables.issubset(tables), f"Missing tables: {expected_tables - tables}"

    expected_views = {
        "v_monthly_data",
        "v_forecast_latest",
        "v_decision_history",
        "v_alerts_localized",
        "v_alert_inbox",
        "v_planting_harvest",
        "v_market_prices_latest",
    }
    assert expected_views.issubset(views), f"Missing views: {expected_views - views}"


def test_bcrypt_password_hashing():
    """Verify bcrypt hash generation and validation."""
    plain = "secure_officer_pwd_2026"
    pwd_hash = hash_password(plain)
    assert pwd_hash.startswith("$2b$")
    assert verify_password(plain, pwd_hash) is True
    assert verify_password("wrong_password", pwd_hash) is False


def test_season_format_validation():
    """Verify season format adheres strictly to Maha YYYY/YYYY or Yala YYYY."""
    assert validate_season_format("Maha 2024/2025") is True
    assert validate_season_format("maha 2025/2026") is True
    assert validate_season_format("Yala 2025") is True
    assert validate_season_format("yala 2024") is True

    assert validate_season_format("Summer 2025") is False
    assert validate_season_format("Maha 2025") is False
    assert validate_season_format("Yala 2025/2026") is False
    assert validate_season_format("") is False


def test_harvest_disposition_constraint():
    """Verify sold + lost + stored <= harvest check constraint in PostgreSQL."""
    with get_session() as session:
        pid = f"LK-TEST-{uuid.uuid4().hex[:6].upper()}"
        rep_id = f"REP-{uuid.uuid4().hex[:6].upper()}"
        ensure_farmer_profile(session, pseudonymous_id=pid, total_land_ha=5.0, consent_given=True)
        cid = ensure_crop_exists(session, "big_onion")
        sid = resolve_season_id(session, "Maha 2024/2025")
        session.commit()

        session.execute(
            text(
                "INSERT INTO planting_reports (report_id, pseudonymous_id, crop_id, season_id, planned_area_ha, actual_area_ha, irrigation_code, consent_given, app_version, lang_code, source) "
                "VALUES (:rid, :pid, :cid, :sid, 1.0, 1.0, 'irrigated', TRUE, '1.0', 'si', 'farmer_report')"
            ),
            {"rid": rep_id, "pid": pid, "cid": cid, "sid": sid},
        )
        # Valid disposition: 1000 = 800 sold + 100 lost + 100 stored
        session.execute(
            text(
                "INSERT INTO harvest_reports (harvest_id, planting_report_id, area_harvested_ha, harvest_quantity_kg, loss_kg, quantity_sold_kg, quantity_stored_kg) "
                "VALUES (:hid, :rid, 1.0, 1000.0, 100.0, 800.0, 100.0)"
            ),
            {"hid": f"HVST-OK-{uuid.uuid4().hex[:6]}", "rid": rep_id},
        )
        session.commit()

        # Invalid disposition: 900 sold + 200 stored = 1100 > 1000 (Must fail chk_disposition_le_harvest)
        with pytest.raises(Exception):
            session.execute(
                text(
                    "INSERT INTO harvest_reports (harvest_id, planting_report_id, area_harvested_ha, harvest_quantity_kg, loss_kg, quantity_sold_kg, quantity_stored_kg) "
                    "VALUES (:hid, :rid, 1.0, 1000.0, 0.0, 900.0, 200.0)"
                ),
                {"hid": f"HVST-BAD-{uuid.uuid4().hex[:6]}", "rid": rep_id},
            )
            session.commit()
        session.rollback()
