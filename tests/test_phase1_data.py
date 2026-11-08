"""
Test Suite for Phase 1: Data Layer (Proposal Sections 5.1 - 5.3)
Verifies:
1.1 Real raw source files staged with snapshot dates
1.2 monthly_master.csv source_type tracking (real, anchor, interpolated) with 0 synthetic rows
1.3 Data catalogue schema, licence terms, and canonical seasons
1.4 Real PDF extraction against proposal benchmarks & agronomic range checks
1.5 Hand-checked sample audit & blank review sheet
1.6 Hybrid temporality: source outage simulation downgrades confidence badge
1.7 Scope expansion: Matale district and Red Onion / Potato integration
1.8 Single source of truth: no competing hub share literals in production modules
"""

import pytest
import re
import pandas as pd
from pathlib import Path

from govisense.config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    DEMO_DATA_DIR,
    settings,
    SEASONS,
    HUB_SHARE,
    MATALE_HUB_SHARE,
)
from govisense.data.extract_cpp import (
    CPPExtractor,
    check_agronomic_plausibility,
)
from govisense.data.catalogue import DataCatalogue
from govisense.data.validate import validate_master_dataset, audit_hand_checked_sample
from govisense.db.history import evaluate_confidence_badge


# ---------------------------------------------------------------------------
# 1.1 Real Raw Sources & Staging
# ---------------------------------------------------------------------------

def test_real_sources_staged():
    cpp_2026 = RAW_DATA_DIR / "cpp" / "doa_cpp_seasonal_2026.pdf"
    assert cpp_2026.exists() and cpp_2026.stat().st_size > 500_000

    cbsl_pdfs = list((RAW_DATA_DIR / "cbsl").glob("price_report_*.pdf"))
    assert len(cbsl_pdfs) >= 5

    cbsl_hist = RAW_DATA_DIR / "cbsl" / "cbsl_daily_prices_historical.csv"
    assert cbsl_hist.exists() and cbsl_hist.stat().st_size > 1_000_000

    wfp_csv = RAW_DATA_DIR / "wfp" / "wfp_food_prices_lka.csv"
    assert wfp_csv.exists() and wfp_csv.stat().st_size > 2_000_000

    weather_csv = RAW_DATA_DIR / "weather" / "anuradhapura_nasa_power_monthly.csv"
    assert weather_csv.exists() and weather_csv.stat().st_size > 5_000

    manual_actions = Path("MANUAL_ACTIONS.md")
    assert manual_actions.exists()


# ---------------------------------------------------------------------------
# 1.2 Replace Synthetic Series & source_type Integrity
# ---------------------------------------------------------------------------

def test_monthly_master_source_type_integrity():
    master_path = PROCESSED_DATA_DIR / "monthly_master.csv"
    assert master_path.exists()
    df = pd.read_csv(master_path)

    assert "source_type" in df.columns
    assert "provenance_price" in df.columns
    assert "provenance_area" in df.columns

    # Must contain real, anchor, and interpolated
    types = set(df["source_type"].unique())
    assert "real" in types
    assert "anchor" in types
    assert "interpolated" in types

    # Production master must NEVER contain synthetic rows
    synthetic_count = (df["source_type"] == "synthetic").sum()
    assert synthetic_count == 0, "Production monthly_master must have 0 synthetic rows"

    # Verify demo data is isolated
    demo_path = DEMO_DATA_DIR / "demo_seed_anuradhapura.csv"
    if demo_path.exists():
        demo_df = pd.read_csv(demo_path)
        assert (demo_df["source_type"] == "synthetic").all()


# ---------------------------------------------------------------------------
# 1.3 Cleaning, Canonical Seasons & Licence Terms
# ---------------------------------------------------------------------------

def test_canonical_seasons_and_licence():
    assert "Maha" in SEASONS
    assert "Yala" in SEASONS
    assert SEASONS["Maha"]["planting_months"] == [9, 10, 11, 12]
    assert SEASONS["Yala"]["planting_months"] == [4, 5, 6]

    cat = DataCatalogue()
    wfp_entry = cat.get_dataset("WFP_FOOD_PRICES_LKA")
    assert wfp_entry is not None
    assert "CC BY-IGO" in wfp_entry.licence

    cbsl_entry = cat.get_dataset("CBSL_DAILY_PRICES")
    assert cbsl_entry is not None
    assert "public government publication, terms not stated" in cbsl_entry.licence


# ---------------------------------------------------------------------------
# 1.4 Hardened Real PDF Extraction & Agronomic Range Checks
# ---------------------------------------------------------------------------

def test_hardened_real_pdf_extraction_proposal_benchmarks():
    cpp_pdf = RAW_DATA_DIR / "cpp" / "doa_cpp_seasonal_2026.pdf"
    ext = CPPExtractor(target_district="all", include_national=True)
    recs = ext.extract_from_pdf(cpp_pdf)

    val = ext.validate_national_figures(recs)

    # Validate all 6 proposal table benchmarks
    assert val["big_onion_national_2026"]["is_valid"] is True
    assert val["big_onion_national_2026"]["planted_extent_ha"] == 4867.0
    assert val["big_onion_national_2026"]["harvest_volume_mt"] == 82149.0

    assert val["big_onion_matale_2026"]["is_valid"] is True
    assert val["big_onion_matale_2026"]["planted_extent_ha"] == 2214.0
    assert val["big_onion_matale_2026"]["harvest_volume_mt"] == 44262.0

    assert val["big_onion_anuradhapura_2026"]["is_valid"] is True
    assert val["big_onion_anuradhapura_2026"]["planted_extent_ha"] == 2131.0
    assert val["big_onion_anuradhapura_2026"]["harvest_volume_mt"] == 35051.0

    assert val["chilli_national_2026"]["is_valid"] is True
    assert val["chilli_national_2026"]["planted_extent_ha"] == 15899.0
    assert val["chilli_national_2026"]["harvest_volume_mt"] == 142116.0

    assert val["chilli_anuradhapura_2026"]["is_valid"] is True
    assert val["chilli_anuradhapura_2026"]["planted_extent_ha"] == 2493.0
    assert val["chilli_anuradhapura_2026"]["harvest_volume_mt"] == 23186.0

    assert val["red_onion_national_2026"]["is_valid"] is True
    assert val["red_onion_national_2026"]["planted_extent_ha"] == 5599.0
    assert val["red_onion_national_2026"]["harvest_volume_mt"] == 76374.0


def test_agronomic_range_checks_catches_typos():
    # Plausible record
    good_rec = {"crop": "big_onion", "planted_extent_ha": 2131.0, "yield_mt_per_ha": 16.45}
    assert len(check_agronomic_plausibility(good_rec)) == 0

    # Implausible fertilizer typo (e.g. 5,000 kg/ha)
    bad_fert = {"crop": "big_onion", "planted_extent_ha": 100.0, "yield_mt_per_ha": 15.0, "fertilizer_kg_per_ha": 5000.0}
    flags = check_agronomic_plausibility(bad_fert)
    assert len(flags) > 0
    assert "fertilizer" in flags[0].lower()


# ---------------------------------------------------------------------------
# 1.5 Hand-Checked Ground-Truth Audit & Review Sheet
# ---------------------------------------------------------------------------

def test_hand_checked_sample_and_review_sheet():
    review_sheet = Path("data/interim/hand_checked_review_sheet.csv")
    assert review_sheet.exists()
    rs_df = pd.read_csv(review_sheet)
    assert "page_number" in rs_df.columns
    assert "reviewer_verified_value" in rs_df.columns
    assert len(rs_df) >= 15

    master_df = pd.read_csv(PROCESSED_DATA_DIR / "monthly_master.csv")
    audit = audit_hand_checked_sample(master_df)
    assert audit.pass_status is True
    assert audit.error_rate_pct < 10.0


# ---------------------------------------------------------------------------
# 1.6 Hybrid Temporality: Outage Simulation Downgrades Confidence
# ---------------------------------------------------------------------------

def test_hybrid_temporality_outage_simulation():
    # Fresh data (15 days old) -> High confidence
    fresh = evaluate_confidence_badge("big_onion", data_age_days=15, area_reported_share=0.40)
    assert fresh.badge == "high"

    # Source outage simulated: data age becomes 65 days (> 45 limit)
    stale = evaluate_confidence_badge("big_onion", data_age_days=65, area_reported_share=0.40)
    assert stale.badge in ["medium", "low"]
    assert any("aging" in r.lower() or "exceeds" in r.lower() for r in stale.reasons)


# ---------------------------------------------------------------------------
# 1.7 Scope Expansion: Matale District, Red Onion, Potato
# ---------------------------------------------------------------------------

def test_scope_expansion_matale_and_crops():
    assert "red_onion" in settings.crops
    assert "potato" in settings.crops
    assert settings.crops["red_onion"].base_yield_mt_per_ha == 13.6
    assert settings.crops["potato"].base_yield_mt_per_ha == 16.6

    assert "big_onion" in MATALE_HUB_SHARE
    assert MATALE_HUB_SHARE["big_onion"] == round(44262.0 / 82149.0, 4)


# ---------------------------------------------------------------------------
# 1.8 Single Source of Truth: Grep Test for Competing Literals
# ---------------------------------------------------------------------------

def test_no_competing_hub_share_literals_in_modules():
    code_files = [
        Path("src/govisense/models/demand_estimator.py"),
        Path("scripts/seed_demo.py"),
    ]

    # Pattern looking for old hardcoded share assignments: e.g. 0.50 if crop == ... else 0.40
    forbidden_pattern = re.compile(r"0\.50\s+if\s+.*?0\.40")

    for f in code_files:
        assert f.exists()
        text = f.read_text(encoding="utf-8")
        assert not forbidden_pattern.search(text), f"Found forbidden competing share literal in {f}"

    # Assert HUB_SHARE values match exact CPP ratio
    assert HUB_SHARE["big_onion"] == round(35051.0 / 82149.0, 4)
    assert HUB_SHARE["chilli"] == round(23186.0 / 142116.0, 4)
