"""
GoviSense Crop Requirements Loader & Validator
Team DARKBITE · ModelX 2.0 Phase 1

Loads ``data/crop_requirements.csv`` and exposes typed, validated records
for use by the Suitability Scorer (WP2) and Target Area Calculator.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd


# Resolve the CSV relative to the repository root
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_CSV_PATH = _REPO_ROOT / "data" / "crop_requirements.csv"

# Required columns and their expected pandas dtypes (for validation)
_REQUIRED_COLUMNS: Dict[str, type] = {
    "crop_id": str,
    "crop_name_en": str,
    "crop_name_si": str,
    "duration_months": int,
    "plant_start_month": int,
    "plant_end_month": int,
    "water_mm_season": float,
    "temp_min_c": float,
    "temp_opt_low_c": float,
    "temp_opt_high_c": float,
    "temp_max_c": float,
    "soil_ph_min": float,
    "soil_ph_max": float,
    "rainfed_ok": bool,
    "yield_low_mt_ha": float,
    "yield_mid_mt_ha": float,
    "yield_high_mt_ha": float,
    "loss_pct": float,
    "cost_per_ha_rs": float,
    "source_note": str,
}


@dataclass(frozen=True)
class CropRequirement:
    """Typed, validated record for one crop from the crop_requirements CSV."""

    crop_id: str
    crop_name_en: str
    crop_name_si: str
    duration_months: int
    plant_start_month: int
    plant_end_month: int
    water_mm_season: float
    temp_min_c: float
    temp_opt_low_c: float
    temp_opt_high_c: float
    temp_max_c: float
    soil_ph_min: float
    soil_ph_max: float
    rainfed_ok: bool
    yield_low_mt_ha: float
    yield_mid_mt_ha: float
    yield_high_mt_ha: float
    loss_pct: float
    cost_per_ha_rs: float
    source_note: str

    def planting_months(self) -> List[int]:
        """Returns the list of valid planting months for this crop."""
        start = self.plant_start_month
        end = self.plant_end_month
        if start <= end:
            return list(range(start, end + 1))
        # Wraps around year-end (e.g., Nov → Feb)
        return list(range(start, 13)) + list(range(1, end + 1))

    def season_fits(self, current_month: int) -> bool:
        """Returns True if the current_month is within the planting window."""
        return current_month in self.planting_months()


def _validate_dataframe(df: pd.DataFrame) -> List[str]:
    """
    Validate the loaded DataFrame.  Returns a list of error messages;
    empty list means the data is clean.
    """
    errors: List[str] = []

    # Check all required columns are present
    missing = set(_REQUIRED_COLUMNS.keys()) - set(df.columns)
    if missing:
        errors.append(f"Missing columns: {sorted(missing)}")
        return errors  # Can't validate further without columns

    # Check no null crop_id
    if df["crop_id"].isnull().any():
        errors.append("crop_id contains null values")

    # Check uniqueness of crop_id
    dups = df["crop_id"][df["crop_id"].duplicated()].tolist()
    if dups:
        errors.append(f"Duplicate crop_id(s): {dups}")

    # Numeric range checks
    for row in df.itertuples(index=False):
        cid = row.crop_id
        if not (1 <= row.plant_start_month <= 12):
            errors.append(f"{cid}: plant_start_month={row.plant_start_month} out of [1,12]")
        if not (1 <= row.plant_end_month <= 12):
            errors.append(f"{cid}: plant_end_month={row.plant_end_month} out of [1,12]")
        if row.temp_min_c >= row.temp_opt_low_c:
            errors.append(f"{cid}: temp_min_c >= temp_opt_low_c")
        if row.temp_opt_low_c >= row.temp_opt_high_c:
            errors.append(f"{cid}: temp_opt_low_c >= temp_opt_high_c")
        if row.temp_opt_high_c >= row.temp_max_c:
            errors.append(f"{cid}: temp_opt_high_c >= temp_max_c")
        if row.soil_ph_min >= row.soil_ph_max:
            errors.append(f"{cid}: soil_ph_min >= soil_ph_max")
        if row.yield_low_mt_ha > row.yield_mid_mt_ha:
            errors.append(f"{cid}: yield_low > yield_mid")
        if row.yield_mid_mt_ha > row.yield_high_mt_ha:
            errors.append(f"{cid}: yield_mid > yield_high")
        if not (0.0 <= row.loss_pct < 1.0):
            errors.append(f"{cid}: loss_pct={row.loss_pct} not in [0,1)")

    return errors


def load_crop_requirements(csv_path: Optional[Path] = None) -> Dict[str, CropRequirement]:
    """
    Load and validate the crop requirements table.

    Parameters
    ----------
    csv_path : Path, optional
        Override path to the CSV (defaults to ``data/crop_requirements.csv``).

    Returns
    -------
    Dict[str, CropRequirement]
        Mapping of crop_id → CropRequirement dataclass.

    Raises
    ------
    FileNotFoundError
        If the CSV does not exist.
    ValueError
        If the CSV fails validation.
    """
    path = csv_path or _CSV_PATH
    if not path.exists():
        raise FileNotFoundError(f"crop_requirements.csv not found at {path}")

    df = pd.read_csv(path)

    # Coerce rainfed_ok to bool (CSV stores TRUE/FALSE strings)
    if "rainfed_ok" in df.columns:
        df["rainfed_ok"] = df["rainfed_ok"].astype(str).str.upper().map(
            {"TRUE": True, "FALSE": False, "1": True, "0": False}
        )

    # Normalize loss_pct if given as 0-100 percentage
    if "loss_pct" in df.columns:
        df["loss_pct"] = df["loss_pct"].apply(
            lambda v: float(v) / 100.0 if float(v) >= 1.0 else float(v)
        )

    errors = _validate_dataframe(df)
    if errors:
        raise ValueError(
            f"crop_requirements.csv failed validation:\n" + "\n".join(f"  • {e}" for e in errors)
        )

    result: Dict[str, CropRequirement] = {}
    for _, row in df.iterrows():
        cr = CropRequirement(
            crop_id=str(row["crop_id"]),
            crop_name_en=str(row["crop_name_en"]),
            crop_name_si=str(row["crop_name_si"]),
            duration_months=int(row["duration_months"]),
            plant_start_month=int(row["plant_start_month"]),
            plant_end_month=int(row["plant_end_month"]),
            water_mm_season=float(row["water_mm_season"]),
            temp_min_c=float(row["temp_min_c"]),
            temp_opt_low_c=float(row["temp_opt_low_c"]),
            temp_opt_high_c=float(row["temp_opt_high_c"]),
            temp_max_c=float(row["temp_max_c"]),
            soil_ph_min=float(row["soil_ph_min"]),
            soil_ph_max=float(row["soil_ph_max"]),
            rainfed_ok=bool(row["rainfed_ok"]),
            yield_low_mt_ha=float(row["yield_low_mt_ha"]),
            yield_mid_mt_ha=float(row["yield_mid_mt_ha"]),
            yield_high_mt_ha=float(row["yield_high_mt_ha"]),
            loss_pct=float(row["loss_pct"]),
            cost_per_ha_rs=float(row["cost_per_ha_rs"]),
            source_note=str(row["source_note"]),
        )
        result[cr.crop_id] = cr

    return result


# ---------------------------------------------------------------------------
# Module-level cache (loaded once on first call)
# ---------------------------------------------------------------------------
_CROP_REQUIREMENTS_CACHE: Optional[Dict[str, CropRequirement]] = None


def get_crop_requirements() -> Dict[str, CropRequirement]:
    """Return cached crop requirements (loads from CSV on first call)."""
    global _CROP_REQUIREMENTS_CACHE
    if _CROP_REQUIREMENTS_CACHE is None:
        _CROP_REQUIREMENTS_CACHE = load_crop_requirements()
    return _CROP_REQUIREMENTS_CACHE


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    crops = load_crop_requirements()
    print(f"Loaded {len(crops)} crop records:")
    for cid, cr in crops.items():
        print(
            f"  {cid:20s}  yield_mid={cr.yield_mid_mt_ha:5.1f} MT/ha  "
            f"plant window: {cr.plant_start_month}–{cr.plant_end_month}  "
            f"rainfed={cr.rainfed_ok}"
        )

    # Validation smoke
    bo = crops["big_onion"]
    assert bo.duration_months == 3
    assert bo.rainfed_ok is False
    assert bo.season_fits(6) is True
    assert bo.season_fits(10) is False
    print("\nAll assertions passed.")
