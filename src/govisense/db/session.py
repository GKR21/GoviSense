"""
Database Session and Engine Configuration for GoviSense
Team DARKBITE · ModelX 2.0 Phase 2
Pilot: Anuradhapura (Big Onion, Chilli)

Provides:
  - Database engine supporting SQLite (with WAL mode & busy timeout) and PostgreSQL
  - Concurrent-write safety for SQLite via WAL, timeout, and thread lock
  - SessionLocal factory and FastAPI dependency get_db()
  - Database initialization and automated legacy JSON data migration
"""

from __future__ import annotations

import os
import json
import logging
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

from govisense.config import PROCESSED_DATA_DIR
from govisense.db.models import (
    Base,
    User,
    PlantingReportRecord,
    DecisionHistoryRecord,
    Alert,
    MarketPriceRecord,
)

logger = logging.getLogger("govisense.db")

# Thread lock to serialize SQLite writes across worker threads
sqlite_write_lock = threading.Lock()

# Database URL configuration
DEFAULT_DB_PATH = PROCESSED_DATA_DIR / "govisense.db"
_raw_url = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH.as_posix()}")

# Standardize postgres URI for SQLAlchemy
if _raw_url.startswith("postgres://"):
    _raw_url = _raw_url.replace("postgres://", "postgresql://", 1)

DATABASE_URL = _raw_url

# Configure engine with concurrent-write safety
is_sqlite = DATABASE_URL.startswith("sqlite")

engine_kwargs = {}
if is_sqlite:
    engine_kwargs = {
        "connect_args": {
            "check_same_thread": False,
            "timeout": 30.0,  # 30 seconds busy wait
        }
    }
else:
    engine_kwargs = {
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
    }

engine = create_engine(DATABASE_URL, **engine_kwargs)


# Enable WAL mode and pragma configurations for SQLite on connect
if is_sqlite:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA busy_timeout=30000")  # 30,000 ms
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager for non-HTTP workflows and internal services."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def migrate_legacy_json_files(db: Session) -> None:
    """
    Migrates legacy planting_reports.json and decision_history.json
    into SQLite/PostgreSQL if database tables are currently empty.
    """
    # 1. Planting Reports Migration
    planting_json_path = PROCESSED_DATA_DIR / "planting_reports.json"
    if planting_json_path.exists():
        existing_count = db.query(PlantingReportRecord).count()
        if existing_count == 0:
            try:
                with open(planting_json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                records = []
                for item in data:
                    records.append(
                        PlantingReportRecord(
                            report_id=item.get("report_id", ""),
                            crop_id=item.get("crop_id", "big_onion"),
                            season=item.get("season", "Maha 2025/2026"),
                            planned_area_ha=float(item.get("planned_area_ha", 0.0)),
                            actual_area_ha=float(item.get("actual_area_ha", 0.0)),
                            consent_given=bool(item.get("consent_given", True)),
                            pseudonymous_id=item.get("pseudonymous_id", "ANON"),
                            harvest_outcome_mt=item.get("harvest_outcome_mt"),
                            sale_price_rs_kg=item.get("sale_price_rs_kg"),
                            sale_channel=item.get("sale_channel"),
                            notes=item.get("notes"),
                            timestamp=item.get("timestamp", ""),
                        )
                    )
                if records:
                    db.bulk_save_objects(records)
                    db.commit()
                    logger.info(f"Migrated {len(records)} planting reports from JSON to database.")
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to migrate planting_reports.json: {e}")

    # 2. Decision History Migration
    history_json_path = PROCESSED_DATA_DIR / "decision_history.json"
    if history_json_path.exists():
        existing_count = db.query(DecisionHistoryRecord).count()
        if existing_count == 0:
            try:
                with open(history_json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                records = []
                for item in data:
                    records.append(
                        DecisionHistoryRecord(
                            decision_id=item.get("decision_id", ""),
                            crop_id=item.get("crop_id", "big_onion"),
                            season=item.get("season", "Maha 2025/2026"),
                            officer_id=item.get("officer_id", "OFFICER-001"),
                            action_type=item.get("action_type", "HOLD_STORAGE"),
                            quantity=float(item.get("quantity", 0.0)),
                            unit=item.get("unit", "MT"),
                            rationale=item.get("rationale", ""),
                            model_version=item.get("model_version", "LightGBM-v2.1+HiGHS-LP"),
                            data_version=item.get("data_version", "CBSL-HARTI-DOA-2024.12"),
                            assumptions=item.get("assumptions", {}),
                            timestamp=item.get("timestamp", ""),
                        )
                    )
                if records:
                    db.bulk_save_objects(records)
                    db.commit()
                    logger.info(f"Migrated {len(records)} decision history items from JSON to database.")
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to migrate decision_history.json: {e}")


def seed_default_users(db: Session) -> None:
    """Seeds demo officer and farmer accounts if the users table is empty."""
    user_count = db.query(User).count()
    if user_count == 0:
        try:
            from govisense.api.auth import get_password_hash
            hash_func = get_password_hash
        except Exception:
            import hashlib
            def hash_func(pw: str) -> str:
                return hashlib.sha256(pw.encode()).hexdigest()

        demo_users = [
            User(
                username="officer_anuradhapura",
                hashed_password=hash_func("Officer@123"),
                role="officer",
                full_name="Kavinda Perera (Agricultural Officer)",
                phone_number="+94771234567",
                district="Anuradhapura",
                is_active=True,
            ),
            User(
                username="farmer_kamal",
                hashed_password=hash_func("Farmer@123"),
                role="farmer",
                full_name="Kamal Gunaratne",
                phone_number="+94777654321",
                district="Anuradhapura",
                is_active=True,
            ),
        ]
        db.bulk_save_objects(demo_users)
        db.commit()
        logger.info("Seeded default demo users (officer_anuradhapura, farmer_kamal).")


def init_db() -> None:
    """Initializes tables, sets up WAL pragmas, and runs initial data migrations."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    with get_db_session() as db:
        migrate_legacy_json_files(db)
        seed_default_users(db)

