"""
Phase 3.1 & 3.2 Tests: Database Schema, Alembic Migrations, and Model Write-Paths
Team DARKBITE · ModelX 2.0
"""

import os
import tempfile
import pytest
from sqlalchemy import create_engine, inspect, text
from alembic.config import Config
from alembic import command

from govisense.db.models import (
    Base,
    hash_password,
    verify_password,
    validate_season_format,
    PipelineRunModel,
    ForecastSnapshotModel,
    EvaluationResultModel,
    PlantingReportModel,
    HarvestReportModel,
    UserModel,
    OfficerModel,
    FarmerProfileModel,
)
from govisense.db.session import get_session


def test_alembic_upgrade_and_downgrade():
    """Verify that alembic can upgrade from empty schema and downgrade back cleanly."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_path = tmp.name.replace("\\", "/")

    try:
        cfg = Config("alembic.ini")
        cfg.set_main_option("sqlalchemy.url", f"sqlite:///{tmp_path}")

        # 1. Run upgrade head
        command.upgrade(cfg, "head")

        eng = create_engine(f"sqlite:///{tmp_path}")
        inspector = inspect(eng)
        tables = set(inspector.get_table_names())

        expected_tables = {
            "users",
            "officers",
            "farmer_profiles",
            "planting_reports",
            "harvest_reports",
            "runs",
            "forecast_snapshots",
            "decision_history",
            "monthly_data",
            "data_catalogue",
            "alerts",
            "alert_status",
            "evaluation_results",
        }
        assert expected_tables.issubset(tables), f"Missing tables: {expected_tables - tables}"

        # 2. Check columns in forecast_snapshots
        fs_cols = {c["name"] for c in inspector.get_columns("forecast_snapshots")}
        assert "retail_price_method" in fs_cols
        assert "spi_raw" in fs_cols
        assert "data_quality" in fs_cols

        # 3. Run downgrade base
        command.downgrade(cfg, "base")
        inspector_down = inspect(create_engine(f"sqlite:///{tmp_path}"))
        remaining = set(inspector_down.get_table_names()) - {"alembic_version"}
        assert len(remaining) == 0, f"Tables remained after downgrade: {remaining}"

        # 4. Re-upgrade
        command.upgrade(cfg, "head")
        tables_reup = set(inspector.get_table_names())
        assert expected_tables.issubset(tables_reup)

    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


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
    """Verify sold + lost + stored <= harvest check constraint."""
    eng = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=eng)

    with eng.connect() as conn:
        # Valid disposition
        conn.execute(
            text(
                "INSERT INTO farmer_profiles (pseudonymous_id, district, total_land_ha, irrigation_type, consent_given, consent_at, language, created_at) "
                "VALUES ('LK-TEST-01', 'Anuradhapura', 1.0, 'irrigated', 1, CURRENT_TIMESTAMP, 'si', CURRENT_TIMESTAMP)"
            )
        )
        conn.execute(
            text(
                "INSERT INTO planting_reports (report_id, pseudonymous_id, crop_id, season, district, irrigation_type, planned_area_ha, actual_area_ha, consent_given, app_version, language, source, flags, timestamp) "
                "VALUES ('REP-01', 'LK-TEST-01', 'big_onion', 'Maha 2024/2025', 'Anuradhapura', 'irrigated', 1.0, 1.0, 1, '1.0', 'si', 'farmer_report', '[]', CURRENT_TIMESTAMP)"
            )
        )
        # 1000 kg harvested: 800 sold + 100 lost + 100 stored = 1000 <= 1000 (Passes)
        conn.execute(
            text(
                "INSERT INTO harvest_reports (harvest_id, planting_report_id, pseudonymous_id, crop_id, season, area_harvested_ha, harvest_quantity_kg, loss_kg, quantity_sold_kg, quantity_stored_kg, problems, flags, timestamp) "
                "VALUES ('HVST-01', 'REP-01', 'LK-TEST-01', 'big_onion', 'Maha 2024/2025', 1.0, 1000.0, 100.0, 800.0, 100.0, '[]', '[]', CURRENT_TIMESTAMP)"
            )
        )
        conn.commit()

        # Invalid disposition: 1000 harvested but sold 900 + stored 200 = 1100 > 1000 (Must fail constraint)
        with pytest.raises(Exception):
            conn.execute(
                text(
                    "INSERT INTO harvest_reports (harvest_id, planting_report_id, pseudonymous_id, crop_id, season, area_harvested_ha, harvest_quantity_kg, loss_kg, quantity_sold_kg, quantity_stored_kg, problems, flags, timestamp) "
                    "VALUES ('HVST-02', 'REP-01', 'LK-TEST-01', 'big_onion', 'Maha 2024/2025', 1.0, 1000.0, 0.0, 900.0, 200.0, '[]', '[]', CURRENT_TIMESTAMP)"
                )
            )
            conn.commit()
