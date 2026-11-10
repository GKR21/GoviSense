"""
Normalized 3NF Lookup & Reference-Resolution Helpers for GoviSense (db.sql).

Centralizes mapping between API/domain string codes and PostgreSQL 3NF foreign keys:
- districts -> district_id
- seasons -> season_id
- crops / crop_categories / market_centers
- irrigation_types, soil_types, sale_channels, officer_designations
- decision_actions, data_quality_levels, alert_types, runs, forecast_models
- farmer_profiles, officers, users (ensuring FK & chk_user_role_link compliance)
"""

from __future__ import annotations

import re
import uuid
from datetime import date, datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from govisense.db.models import (
    CropCategoryModel,
    CropModel,
    CropTranslationModel,
    DistrictModel,
    DsDivisionModel,
    FarmerProfileModel,
    ForecastModelRef,
    MarketCenterModel,
    MarketCenterTranslationModel,
    OfficerDesignationModel,
    OfficerModel,
    PipelineRunModel,
    SeasonModel,
    UserModel,
    hash_password,
)
from govisense.provenance import compute_data_version, compute_model_version, get_git_commit

# Canonical code mapping tables (handle inputs uniformly)
_SOIL_ALIASES = {
    "rbe": "reddish_brown_earth",
    "reddish brown earth": "reddish_brown_earth",
    "reddish brown earth (rbe)": "reddish_brown_earth",
    "reddish brown earths (rbe)": "reddish_brown_earth",
    "reddish_brown_earth": "reddish_brown_earth",
    "lhg": "low_humic_gley",
    "low humic gley": "low_humic_gley",
    "low_humic_gley": "low_humic_gley",
    "alluvial": "alluvial",
    "regosol": "regosol",
}

_IRRIGATION_ALIASES = {
    "rainfed": "rainfed",
    "minor": "minor_tank",
    "minor_tank": "minor_tank",
    "major": "major_irrigation",
    "major_irrigation": "major_irrigation",
    "lift": "agro_well",
    "agro_well": "agro_well",
    "irrigated": "irrigated",
}

_SALE_CHANNEL_ALIASES = {
    "dec_wholesale": "DEC_WHOLESALE",
    "dedicated economic centre": "DEC_WHOLESALE",
    "dambulla dec": "DAMBULLA_DEC",
    "dambulla_dec": "DAMBULLA_DEC",
    "keppetipola dec": "KEPPETIPOLA_DEC",
    "keppetipola_dec": "KEPPETIPOLA_DEC",
    "asc buy-back": "ASC_BUYBACK",
    "asc_buyback": "ASC_BUYBACK",
    "local collector": "LOCAL_COLLECTOR",
    "local_collector": "LOCAL_COLLECTOR",
    "trader": "LOCAL_COLLECTOR",
}

_TRIGGER_ALIASES = {
    "scheduled": "scheduled",
    "manual": "manual",
    "officer": "manual",
    "system_init": "api",
    "retrigger_feedback": "retrigger_feedback",
    "retrigger": "retrigger_feedback",
    "test_audit": "test_audit",
    "api": "api",
}

_QUALITY_ALIASES = {
    "verified": "verified",
    "real": "verified",
    "anchor": "verified",
    "provisional": "provisional",
    "estimated": "provisional",
    "interpolated": "provisional",
    "partial": "provisional",
    "stale": "stale",
    "outdated": "stale",
    "demo": "demo",
    "synthetic": "demo",
    "demo_estimate": "demo",
    "no_data": "provisional",
}

_ACTION_ALIASES = {
    "hold_storage": "HOLD_STORAGE",
    "store": "HOLD_STORAGE",
    "plant_expansion": "PLANT_EXPANSION",
    "encourage_planting": "PLANT_EXPANSION",
    "restrict_expansion": "RESTRICT_EXPANSION",
    "import_later": "IMPORT_LATER",
    "delay_import": "IMPORT_LATER",
    "import_now": "IMPORT_NOW",
    "no_action": "NO_ACTION",
    "maintain": "NO_ACTION",
}

_ALERT_TYPE_ALIASES = {
    "glut_warning": "GLUT_WARNING",
    "shortage_warning": "SHORTAGE_WARNING",
    "shortage_risk": "SHORTAGE_WARNING",
    "weather": "WEATHER",
    "market": "MARKET",
    "market_alert": "MARKET",
    "system": "SYSTEM",
}


def parse_month_date(month_val: Any) -> date:
    """Normalizes 'YYYY-MM' / 'YYYY-MM-DD' / date / datetime into the 1st of that month."""
    if isinstance(month_val, datetime):
        return month_val.date().replace(day=1)
    if isinstance(month_val, date):
        return month_val.replace(day=1)
    text = str(month_val or "").strip()
    m = re.match(r"^(\d{4})-(\d{2})", text)
    if m:
        return date(int(m.group(1)), int(m.group(2)), 1)
    now = datetime.now(timezone.utc).date()
    return now.replace(day=1)


def format_month_str(d: Any) -> str:
    if isinstance(d, (date, datetime)):
        return d.strftime("%Y-%m")
    return str(d)[:7]


def normalize_crop_id(crop_id: str) -> str:
    c = (crop_id or "big_onion").strip().lower()
    if c == "chilli_green":
        return "chilli"
    return c


def normalize_irrigation_code(irrigation_type: Optional[str], irrigation_subtype: Optional[str] = None) -> str:
    for candidate in (irrigation_subtype, irrigation_type):
        if candidate:
            key = candidate.strip().lower()
            if key in _IRRIGATION_ALIASES:
                return _IRRIGATION_ALIASES[key]
    return "irrigated"


def normalize_soil_code(soil_type: Optional[str]) -> Optional[str]:
    if not soil_type:
        return None
    return _SOIL_ALIASES.get(soil_type.strip().lower())


def normalize_sale_channel(channel: Optional[str]) -> Optional[str]:
    if not channel:
        return None
    return _SALE_CHANNEL_ALIASES.get(channel.strip().lower(), "DEC_WHOLESALE")


def normalize_trigger_type(trigger: Optional[str]) -> str:
    if not trigger:
        return "api"
    return _TRIGGER_ALIASES.get(trigger.strip().lower(), "api")


def normalize_data_quality(quality: Optional[str]) -> str:
    if not quality:
        return "provisional"
    return _QUALITY_ALIASES.get(quality.strip().lower(), "provisional")


def normalize_decision_action(action: Optional[str]) -> Optional[str]:
    if not action:
        return None
    return _ACTION_ALIASES.get(action.strip().lower(), "NO_ACTION")


def normalize_alert_type(alert_type: Optional[str]) -> str:
    if not alert_type:
        return "MARKET"
    return _ALERT_TYPE_ALIASES.get(alert_type.strip().lower(), "MARKET")


def normalize_lang_code(lang: Optional[str]) -> str:
    code = (lang or "si").strip().lower()
    return code if code in ("en", "si", "ta") else "en"


def resolve_district_id(db: Session, district_name: Optional[str] = "Anuradhapura") -> int:
    """Resolves a district name to districts.district_id, defaulting to Anuradhapura."""
    clean = (district_name or "Anuradhapura").strip()
    if clean.lower() in ("national", "national / hq", "hq", "all"):
        clean = "Anuradhapura"
    clean = re.sub(r"\s+district$", "", clean, flags=re.IGNORECASE).strip()

    row = db.query(DistrictModel).filter(func.lower(DistrictModel.name) == clean.lower()).first()
    if row:
        return int(row.district_id)

    fallback = db.query(DistrictModel).filter(DistrictModel.name == "Anuradhapura").first()
    if fallback:
        return int(fallback.district_id)

    row = DistrictModel(name=clean)
    db.add(row)
    db.flush()
    return int(row.district_id)


def resolve_division_id(db: Session, district_id: int, division_name: Optional[str]) -> Optional[int]:
    if not division_name or not division_name.strip():
        return None
    clean = division_name.strip()
    row = (
        db.query(DsDivisionModel)
        .filter(DsDivisionModel.district_id == district_id, func.lower(DsDivisionModel.name) == clean.lower())
        .first()
    )
    if row:
        return int(row.division_id)
    row = DsDivisionModel(district_id=district_id, name=clean)
    db.add(row)
    db.flush()
    return int(row.division_id)


def resolve_designation_id(db: Session, role_name: Optional[str]) -> int:
    clean = (role_name or "Agricultural Extension Officer").strip()
    row = (
        db.query(OfficerDesignationModel)
        .filter(func.lower(OfficerDesignationModel.name) == clean.lower())
        .first()
    )
    if row:
        return int(row.designation_id)
    row = OfficerDesignationModel(name=clean)
    db.add(row)
    db.flush()
    return int(row.designation_id)


def _season_dates_for_label(label: str, ref_date: Optional[date] = None) -> tuple[str, str, date, date]:
    clean = (label or "").strip()
    m_maha = re.match(r"^maha\s+(\d{4})/(\d{4})$", clean, re.IGNORECASE)
    if m_maha:
        y1, y2 = int(m_maha.group(1)), int(m_maha.group(2))
        return f"Maha {y1}/{y2}", "Maha", date(y1, 10, 1), date(y2, 3, 31)

    m_yala = re.match(r"^yala\s+(\d{4})$", clean, re.IGNORECASE)
    if m_yala:
        y = int(m_yala.group(1))
        return f"Yala {y}", "Yala", date(y, 4, 1), date(y, 9, 30)

    d = ref_date or parse_month_date(clean) if re.match(r"^\d{4}-\d{2}", clean) else (ref_date or date(2025, 11, 1))
    if d.month >= 10:
        return f"Maha {d.year}/{d.year + 1}", "Maha", date(d.year, 10, 1), date(d.year + 1, 3, 31)
    if d.month <= 3:
        return f"Maha {d.year - 1}/{d.year}", "Maha", date(d.year - 1, 10, 1), date(d.year, 3, 31)
    return f"Yala {d.year}", "Yala", date(d.year, 4, 1), date(d.year, 9, 30)


def resolve_season_id(db: Session, season_label: Optional[str], ref_date: Optional[date] = None) -> int:
    """
    Resolves a season label ('Maha 2025/2026', 'Maha', 'Yala', or 'YYYY-MM') to seasons.season_id,
    respecting the non-overlapping daterange GiST exclusion constraint in db.sql.
    """
    clean = (season_label or "Maha 2025/2026").strip()
    if clean.lower() == "maha":
        clean = "Maha 2025/2026"
    elif clean.lower() == "yala":
        clean = "Yala 2025"

    existing = db.query(SeasonModel).filter(func.lower(SeasonModel.label) == clean.lower()).first()
    if existing:
        return int(existing.season_id)

    canonical_label, s_type, start_d, end_d = _season_dates_for_label(clean, ref_date=ref_date)
    existing = db.query(SeasonModel).filter(SeasonModel.label == canonical_label).first()
    if existing:
        return int(existing.season_id)

    # Check if date range already covered by an existing season
    overlapping = (
        db.query(SeasonModel)
        .filter(SeasonModel.start_date <= end_d, SeasonModel.end_date >= start_d)
        .first()
    )
    if overlapping:
        return int(overlapping.season_id)

    new_season = SeasonModel(
        label=canonical_label,
        season_type=s_type,
        start_date=start_d,
        end_date=end_d,
    )
    db.add(new_season)
    db.flush()
    return int(new_season.season_id)


def ensure_crop_exists(
    db: Session,
    crop_id: str,
    category_code: Optional[str] = None,
    names: Optional[Dict[str, str]] = None,
) -> str:
    cid = normalize_crop_id(crop_id)
    if cid == "all":
        cid = "big_onion"
    existing = db.query(CropModel).filter(CropModel.crop_id == cid).first()
    if not existing:
        cat = (category_code or "vegetable").strip().lower()
        cat_map = {"grain": "cereal", "tuber": "vegetable"}
        cat_norm = cat_map.get(cat, cat)
        if not db.query(CropCategoryModel).filter(CropCategoryModel.category_code == cat_norm).first():
            db.add(CropCategoryModel(category_code=cat_norm, name=cat_norm.replace("_", " ").title()))
            db.flush()
        existing = CropModel(crop_id=cid, category_code=cat_norm)
        db.add(existing)
        db.flush()

    if names:
        for lang, label in names.items():
            if not label:
                continue
            lc = normalize_lang_code(lang)
            tr = (
                db.query(CropTranslationModel)
                .filter(CropTranslationModel.crop_id == cid, CropTranslationModel.lang_code == lc)
                .first()
            )
            if not tr:
                db.add(CropTranslationModel(crop_id=cid, lang_code=lc, name=label))
        db.flush()
    return cid


def resolve_market_center_id(
    db: Session,
    center_name: str,
    district_name: Optional[str] = None,
    names: Optional[Dict[str, str]] = None,
) -> int:
    clean = center_name.strip()
    center = db.query(MarketCenterModel).filter(func.lower(MarketCenterModel.name) == clean.lower()).first()
    if not center:
        dist_id = resolve_district_id(db, district_name) if district_name else None
        center = MarketCenterModel(name=clean, district_id=dist_id)
        db.add(center)
        db.flush()

    if names:
        for lang, label in names.items():
            if not label:
                continue
            lc = normalize_lang_code(lang)
            tr = (
                db.query(MarketCenterTranslationModel)
                .filter(
                    MarketCenterTranslationModel.center_id == center.center_id,
                    MarketCenterTranslationModel.lang_code == lc,
                )
                .first()
            )
            if not tr:
                db.add(MarketCenterTranslationModel(center_id=center.center_id, lang_code=lc, name=label))
        db.flush()
    return int(center.center_id)


def ensure_forecast_model(db: Session, model_name: str, model_kind: str = "price", is_baseline: bool = False) -> str:
    clean = (model_name or "SARIMAX-LightGBM-ensemble").strip()[:60]
    existing = db.query(ForecastModelRef).filter(ForecastModelRef.model_name == clean).first()
    if not existing:
        kind = model_kind if model_kind in ("price", "supply", "baseline", "component") else "component"
        db.add(ForecastModelRef(model_name=clean, model_kind=kind, is_baseline=is_baseline))
        db.flush()
    return clean


def ensure_pipeline_run(
    db: Session,
    run_id: Optional[str] = None,
    trigger_type: str = "api",
    model_version: Optional[str] = None,
    data_version: Optional[str] = None,
    assumptions: Optional[Dict[str, Any]] = None,
    git_commit: Optional[str] = None,
) -> str:
    rid = (run_id or f"RUN-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}")[:36]
    existing = db.query(PipelineRunModel).filter(PipelineRunModel.run_id == rid).first()
    if not existing:
        run = PipelineRunModel(
            run_id=rid,
            trigger_type=normalize_trigger_type(trigger_type),
            model_version=model_version or compute_model_version(),
            data_version=data_version or compute_data_version(),
            assumptions=assumptions if assumptions is not None else {},
            git_commit=(git_commit or get_git_commit())[:40],
        )
        db.add(run)
        db.flush()
    return rid


def ensure_officer(
    db: Session,
    officer_id: str,
    name: str = "Officer in Charge",
    district: str = "Anuradhapura",
    division: Optional[str] = None,
    role: str = "Agricultural Extension Officer",
) -> OfficerModel:
    off = db.query(OfficerModel).filter(OfficerModel.officer_id == officer_id).first()
    if off:
        return off
    dist_id = resolve_district_id(db, district)
    div_id = resolve_division_id(db, dist_id, division)
    desig_id = resolve_designation_id(db, role)
    off = OfficerModel(
        officer_id=officer_id,
        name=name,
        district_id=dist_id,
        division_id=div_id,
        designation_id=desig_id,
    )
    db.add(off)
    db.flush()
    return off


def ensure_farmer_profile(
    db: Session,
    pseudonymous_id: str,
    district: str = "Anuradhapura",
    divisional_secretariat: Optional[str] = None,
    total_land_ha: float = 5.0,
    irrigation_type: str = "irrigated",
    irrigation_subtype: Optional[str] = None,
    soil_type: Optional[str] = None,
    soil_ph: Optional[float] = None,
    consent_given: bool = True,
    language: str = "si",
) -> FarmerProfileModel:
    fp = db.query(FarmerProfileModel).filter(FarmerProfileModel.pseudonymous_id == pseudonymous_id).first()
    if fp:
        return fp
    dist_id = resolve_district_id(db, district)
    div_id = resolve_division_id(db, dist_id, divisional_secretariat)
    fp = FarmerProfileModel(
        pseudonymous_id=pseudonymous_id,
        district_id=dist_id,
        division_id=div_id,
        total_land_ha=max(0.01, float(total_land_ha)),
        irrigation_code=normalize_irrigation_code(irrigation_type, irrigation_subtype),
        soil_code=normalize_soil_code(soil_type),
        soil_ph=soil_ph,
        consent_given=bool(consent_given),
        consent_at=datetime.now(timezone.utc),
        lang_code=normalize_lang_code(language),
    )
    db.add(fp)
    db.flush()
    return fp


def ensure_user_for_actor(
    db: Session,
    identifier: str,
    default_role: str = "farmer",
) -> str:
    """Resolves a user_id or username or pseudonymous_id/officer_id to a valid users.user_id."""
    clean = (identifier or "anonymous_farmer").strip()
    u = (
        db.query(UserModel)
        .filter(
            (UserModel.user_id == clean)
            | (func.lower(UserModel.username) == clean.lower())
            | (UserModel.pseudonymous_id == clean)
            | (UserModel.officer_id == clean)
        )
        .first()
    )
    if u:
        return u.user_id

    role = default_role if default_role in ("farmer", "officer", "admin") else "farmer"
    user_id = f"USR-{uuid.uuid4().hex[:8].upper()}"
    username = clean[:50]
    if role == "officer":
        off = ensure_officer(db, officer_id=clean[:50], name=clean)
        u = UserModel(
            user_id=user_id,
            username=username,
            password_hash=hash_password(uuid.uuid4().hex),
            role_code="officer",
            officer_id=off.officer_id,
        )
    elif role == "farmer":
        fp = ensure_farmer_profile(db, pseudonymous_id=clean[:50])
        u = UserModel(
            user_id=user_id,
            username=username,
            password_hash=hash_password(uuid.uuid4().hex),
            role_code="farmer",
            pseudonymous_id=fp.pseudonymous_id,
        )
    else:
        u = UserModel(
            user_id=user_id,
            username=username,
            password_hash=hash_password(uuid.uuid4().hex),
            role_code="admin",
        )
    db.add(u)
    db.flush()
    return u.user_id
