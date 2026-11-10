"""
Database Engine & Session Management for GoviSense (Strictly PostgreSQL + db.sql)
Team DARKBITE · ModelX 2.0
Pilot: Anuradhapura (Big Onion, Chilli)

Connects strictly to PostgreSQL via SQLAlchemy + psycopg2 and initializes
the 42-table 3NF schema directly from data/database/db.sql.
"""

from __future__ import annotations

import json
import logging
import threading
from contextlib import contextmanager
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Generator, Optional

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from govisense.config import PROCESSED_DATA_DIR, settings
from govisense.db.lookups import (
    ensure_crop_exists,
    ensure_farmer_profile,
    ensure_officer,
    ensure_pipeline_run,
    normalize_crop_id,
    normalize_decision_action,
    parse_month_date,
    resolve_district_id,
    resolve_market_center_id,
    resolve_season_id,
)
from govisense.db.models import (
    CropModel,
    DecisionRecordModel,
    MarketPriceRecord,
    MonthlyDataModel,
    PlantingReportModel,
    UserModel,
    compute_sha256_hash,
    hash_password,
)

logger = logging.getLogger("govisense.db")

# Thread lock for serialized write sections
db_write_lock = threading.Lock()
sqlite_write_lock = db_write_lock  # Backward-compatibility alias for imports

_ENGINE: Optional[Engine] = None
_SESSION_FACTORY: Optional[sessionmaker] = None
_ACTIVE_DIALECT: str = "postgresql"


def _normalize_db_url(url: str) -> str:
    """Normalize Postgres URLs to use psycopg2 dialect."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://") and not url.startswith("postgresql+"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


def get_engine(force_new: bool = False) -> Engine:
    """
    Returns the active PostgreSQL SQLAlchemy Engine.
    Strictly requires PostgreSQL; raises on misconfiguration or unreachable server.
    """
    global _ENGINE, _SESSION_FACTORY, _ACTIVE_DIALECT

    if _ENGINE is not None and not force_new:
        return _ENGINE

    target_url = _normalize_db_url(settings.database_url)
    if "postgresql" not in target_url:
        raise RuntimeError(
            f"GoviSense requires a PostgreSQL DATABASE_URL (got '{target_url}'). "
            "SQLite fallback has been removed."
        )

    pg_engine = create_engine(
        target_url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=180,
        echo=settings.db_echo,
        connect_args={"connect_timeout": 10},
    )
    with pg_engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    _ENGINE = pg_engine
    _ACTIVE_DIALECT = "postgresql"
    _SESSION_FACTORY = sessionmaker(autocommit=False, autoflush=False, bind=_ENGINE)
    logger.info("Connected to PostgreSQL database at %s", target_url.split("@")[-1])
    return _ENGINE


def get_session() -> Session:
    """Creates a new SQLAlchemy session."""
    global _SESSION_FACTORY
    if _SESSION_FACTORY is None or _ENGINE is None:
        get_engine()
    return _SESSION_FACTORY()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a SQLAlchemy database session,
    committing on clean exit and closing automatically.
    """
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager for non-HTTP workflows and internal services."""
    db = get_session()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_active_dialect() -> str:
    """Returns 'postgresql'."""
    if _ENGINE is None:
        get_engine()
    return _ACTIVE_DIALECT


def apply_db_sql_schema(eng: Engine, schema_sql_path: Optional[Path] = None) -> bool:
    """
    Executes data/database/db.sql against PostgreSQL if core schema tables
    are not yet present. Returns True if db.sql was applied, False if already present.
    """
    with eng.connect() as conn:
        existing = conn.execute(text("SELECT to_regclass('public.roles')")).scalar()
        if existing is not None:
            return False

    sql_path = schema_sql_path or settings.db_schema_path
    if not sql_path.exists():
        raise FileNotFoundError(f"Canonical schema file not found: {sql_path}")

    sql_text = sql_path.read_text(encoding="utf-8")
    raw_conn = eng.raw_connection()
    try:
        raw_conn.autocommit = True
        with raw_conn.cursor() as cur:
            cur.execute(sql_text)
        logger.info("Initialized PostgreSQL database schema & reference seed data from %s", sql_path)
    finally:
        raw_conn.close()
    return True


def seed_reference_extensions(db: Session) -> None:
    """
    Ensures additional crops supported by market price bulletins / config
    (maize, red_onion, potato) exist in the 3NF crops lookup table.
    """
    extra_crops = [
        (
            "maize",
            "cereal",
            {
                "en": "Maize (Feed Grade)",
                "si": "බඩඉරිඟු (සත්ත්ව ආහාර)",
                "ta": "மக்காச்சோளம் (தீவனம்)",
            },
        ),
        (
            "red_onion",
            "vegetable",
            {
                "en": "Red Onion (Jaffna / Puttalam)",
                "si": "රතු ළූණු (යාපනය / පුත්තලම)",
                "ta": "சின்ன வெங்காயம் (யாழ்ப்பாணம்)",
            },
        ),
        (
            "potato",
            "vegetable",
            {
                "en": "Potato (Nuwara Eliya)",
                "si": "අර්තාපල් (නුවරඑළිය)",
                "ta": "உருளைக்கிழங்கு (நுவரெலியா)",
            },
        ),
    ]
    for cid, cat, names in extra_crops:
        if not db.query(CropModel).filter(CropModel.crop_id == cid).first():
            ensure_crop_exists(db, cid, category_code=cat, names=names)
    db.commit()


def seed_master_data_if_empty(eng: Engine) -> None:
    """Seeds normalized monthly_data table from monthly_master.csv if empty."""
    import pandas as pd

    master_csv = PROCESSED_DATA_DIR / "monthly_master.csv"
    if not master_csv.exists():
        return

    SessionMaker = sessionmaker(bind=eng)
    with SessionMaker() as session:
        try:
            if session.query(MonthlyDataModel).count() > 0:
                return
            df = pd.read_csv(master_csv)
            crop_cache: dict[str, str] = {}
            dist_cache: dict[str, int] = {}
            rows_to_insert = []
            for _, r in df.iterrows():
                raw_crop = str(r["crop"])
                if raw_crop not in crop_cache:
                    crop_cache[raw_crop] = ensure_crop_exists(session, raw_crop)
                raw_dist = str(r["district"])
                if raw_dist not in dist_cache:
                    dist_cache[raw_dist] = resolve_district_id(session, raw_dist)

                src_type = str(r.get("source_type", "real")).strip().lower()
                if src_type not in ("real", "anchor", "interpolated", "synthetic"):
                    src_type = "real"
                rows_to_insert.append(
                    {
                        "crop_id": crop_cache[raw_crop],
                        "district_id": dist_cache[raw_dist],
                        "month": parse_month_date(str(r["year_month"])),
                        "planted_area_ha": float(r["planted_extent_ha"]) if pd.notnull(r["planted_extent_ha"]) else None,
                        "production_mt": float(r["harvest_volume_mt"]) if pd.notnull(r["harvest_volume_mt"]) else None,
                        "wholesale_price_rs_kg": float(r["wholesale_price_rs_kg"]) if pd.notnull(r["wholesale_price_rs_kg"]) else None,
                        "retail_price_rs_kg": float(r["retail_price_rs_kg"]) if pd.notnull(r["retail_price_rs_kg"]) else None,
                        "farmgate_price_rs_kg": float(r["farmgate_price_rs_kg"]) if pd.notnull(r["farmgate_price_rs_kg"]) else None,
                        "imports_mt": float(r["import_volume_mt"]) if pd.notnull(r["import_volume_mt"]) else None,
                        "weather_rainfall_anomaly": float(r["rainfall_anomaly_mm"]) if pd.notnull(r["rainfall_anomaly_mm"]) else None,
                        "source_type": src_type,
                    }
                )
            session.bulk_insert_mappings(MonthlyDataModel, rows_to_insert)
            session.commit()
            logger.info("Loaded %d master rows into monthly_data table.", len(rows_to_insert))
        except Exception as exc:
            session.rollback()
            logger.warning("Could not auto-seed monthly_data table: %s", exc)


def migrate_legacy_json_files(db: Session) -> None:
    """
    Migrates legacy planting_reports.json and decision_history.json
    into normalized PostgreSQL tables if currently empty.
    """
    planting_json_path = PROCESSED_DATA_DIR / "planting_reports.json"
    if planting_json_path.exists():
        try:
            if db.query(PlantingReportModel).count() == 0:
                data = json.loads(planting_json_path.read_text(encoding="utf-8"))
                seen_keys = set()
                for item in data:
                    pseudo = item.get("pseudonymous_id", "ANON-LEGACY")
                    cid = ensure_crop_exists(db, item.get("crop_id", "big_onion"))
                    season_id = resolve_season_id(db, item.get("season", "Maha 2025/2026"))
                    key = (pseudo, cid, season_id)
                    if key in seen_keys:
                        continue
                    seen_keys.add(key)

                    planned = max(0.01, float(item.get("planned_area_ha", 1.0) or 1.0))
                    actual_raw = item.get("actual_area_ha")
                    actual = float(actual_raw) if actual_raw is not None and float(actual_raw) > 0 else None
                    ensure_farmer_profile(
                        db,
                        pseudonymous_id=pseudo,
                        total_land_ha=max(50.0, planned, actual or 0.0),
                        consent_given=bool(item.get("consent_given", True)),
                    )
                    db.add(
                        PlantingReportModel(
                            report_id=item.get("report_id") or None,
                            pseudonymous_id=pseudo,
                            crop_id=cid,
                            season_id=season_id,
                            planned_area_ha=planned,
                            actual_area_ha=actual,
                            irrigation_code="irrigated",
                            consent_given=bool(item.get("consent_given", True)),
                            notes=item.get("notes"),
                        )
                    )
                db.commit()
                logger.info("Migrated %d planting reports from JSON to PostgreSQL.", len(seen_keys))
        except Exception as e:
            db.rollback()
            logger.warning("Failed to migrate planting_reports.json: %s", e)

    history_json_path = PROCESSED_DATA_DIR / "decision_history.json"
    if history_json_path.exists():
        try:
            if db.query(DecisionRecordModel).count() == 0:
                data = json.loads(history_json_path.read_text(encoding="utf-8"))
                for item in data:
                    cid = ensure_crop_exists(db, item.get("crop_id", "big_onion"))
                    season_id = resolve_season_id(db, item.get("season", "Maha 2025/2026"))
                    officer_id = item.get("officer_id", "OFFICER-001")
                    ensure_officer(db, officer_id=officer_id)
                    run_id = ensure_pipeline_run(
                        db,
                        run_id=item.get("run_id"),
                        trigger_type="manual",
                        model_version=item.get("model_version"),
                        data_version=item.get("data_version"),
                        assumptions=item.get("assumptions") or {},
                    )
                    action = normalize_decision_action(item.get("action_type", "HOLD_STORAGE")) or "HOLD_STORAGE"
                    dec_id = item.get("decision_id") or f"DEC-{abs(hash(str(item))) % 10**8:08d}"
                    rec_hash = item.get("hash") or item.get("record_hash") or compute_sha256_hash(
                        {"decision_id": dec_id, "crop_id": cid, "action_type": action, "officer_id": officer_id}
                    )
                    db.add(
                        DecisionRecordModel(
                            decision_id=dec_id,
                            run_id=run_id,
                            record_hash=rec_hash[:64],
                            crop_id=cid,
                            season_id=season_id,
                            officer_id=officer_id,
                            action_type=action,
                            quantity=float(item.get("quantity", 0.0) or 0.0),
                            unit=item.get("unit", "MT"),
                            rationale=item.get("rationale", "Migrated decision record"),
                        )
                    )
                db.commit()
                logger.info("Migrated %d decision history items from JSON to PostgreSQL.", len(data))
        except Exception as e:
            db.rollback()
            logger.warning("Failed to migrate decision_history.json: %s", e)


def seed_default_users(db: Session) -> None:
    """
    Seeds default admin, officer, and farmer accounts respecting db.sql's
    chk_user_role_link constraint (every farmer links to farmer_profiles; every officer links to officers).
    """
    existing_usernames = {u.username for u in db.query(UserModel.username).all()}

    if "admin_govisense" not in existing_usernames:
        db.add(
            UserModel(
                username="admin_govisense",
                password_hash=hash_password("Admin@123"),
                role_code="admin",
                full_name="System Administrator (National)",
                phone_number="+94112345678",
                is_active=True,
            )
        )

    if "officer_anuradhapura" not in existing_usernames:
        ensure_officer(
            db,
            officer_id="OFF-ANU-01",
            name="Kavinda Perera",
            district="Anuradhapura",
            role="Agricultural Extension Officer",
        )
        db.add(
            UserModel(
                username="officer_anuradhapura",
                password_hash=hash_password("Officer@123"),
                role_code="officer",
                officer_id="OFF-ANU-01",
                full_name="Kavinda Perera (Agricultural Officer)",
                phone_number="+94771234567",
                is_active=True,
            )
        )

    if "farmer_kamal" not in existing_usernames:
        ensure_farmer_profile(
            db,
            pseudonymous_id="LK-AP-KAMAL",
            district="Anuradhapura",
            total_land_ha=2.5,
            irrigation_type="irrigated",
            consent_given=True,
            language="si",
        )
        db.add(
            UserModel(
                username="farmer_kamal",
                password_hash=hash_password("Farmer@123"),
                role_code="farmer",
                pseudonymous_id="LK-AP-KAMAL",
                full_name="Kamal Gunaratne",
                phone_number="+94777654321",
                is_active=True,
            )
        )

    db.commit()


def seed_market_prices(db: Session) -> None:
    """Seeds CBSL & HARTI benchmark DEC market prices into normalized market_prices if empty."""
    try:
        if db.query(MarketPriceRecord).count() > 0:
            return

        ref_date = date(2026, 11, 8)
        entries = [
            ("big_onion", "vegetable", "Dambulla DEC", "Matale", 342.5, 440.0),
            ("chilli", "spice", "Dambulla DEC", "Matale", 260.0, 380.0),
            ("green_gram", "pulse", "Keppetipola DEC", "Badulla", 415.0, 535.0),
            ("maize", "cereal", "Anuradhapura DEC", "Anuradhapura", 121.5, 155.0),
            ("red_onion", "vegetable", "Meegoda DEC", "Colombo", 315.0, 420.0),
            ("potato", "vegetable", "Keppetipola DEC", "Badulla", 310.0, 410.0),
        ]
        for raw_crop, cat, center_name, dist_name, w_price, r_price in entries:
            cid = ensure_crop_exists(db, normalize_crop_id(raw_crop), category_code=cat)
            center_id = resolve_market_center_id(db, center_name, district_name=dist_name)
            db.add(
                MarketPriceRecord(
                    crop_id=cid,
                    center_id=center_id,
                    price_date=ref_date,
                    wholesale_price=w_price,
                    retail_price=r_price,
                )
            )
        db.commit()
        logger.info("Seeded 6 benchmark DEC market prices into market_prices.")
    except Exception as e:
        db.rollback()
        logger.warning("Error seeding market prices: %s", e)


def init_db(engine: Optional[Engine] = None, schema_sql_path: Optional[Path] = None) -> None:
    """
    Initializes PostgreSQL schema from data/database/db.sql and runs baseline seeders.
    """
    eng = engine or get_engine()
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    apply_db_sql_schema(eng, schema_sql_path=schema_sql_path)

    with get_db_session() as db:
        seed_reference_extensions(db)

    seed_master_data_if_empty(eng)

    with get_db_session() as db:
        seed_default_users(db)
        seed_market_prices(db)
        migrate_legacy_json_files(db)


def __getattr__(name: str):
    """Lazy access for module-level `engine` compatibility."""
    if name == "engine":
        return get_engine()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
