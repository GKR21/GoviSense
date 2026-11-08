"""
GoviSense Configuration Module
Team DARKBITE · ModelX 2.0 Phase 1
Pilot: Anuradhapura (Big Onion, Chilli)
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Workspace Root & Directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DEMO_DATA_DIR = DATA_DIR / "demo"
DATABASE_DIR = DATA_DIR / "database"
MODELS_STORE_DIR = BASE_DIR / "models_store"

# Ensure runtime directories exist
for folder in [RAW_DATA_DIR, INTERIM_DATA_DIR, PROCESSED_DATA_DIR, DEMO_DATA_DIR, DATABASE_DIR, MODELS_STORE_DIR]:
    folder.mkdir(parents=True, exist_ok=True)


# Canonical Seasons (defined once, used everywhere)
SEASONS: Dict[str, Dict[str, Any]] = {
    "Maha": {
        "planting_months": [9, 10, 11, 12],
        "harvest_months": [1, 2, 3, 4],
        "description": "Northeast monsoon season",
    },
    "Yala": {
        "planting_months": [4, 5, 6],
        "harvest_months": [7, 8, 9, 10],
        "description": "Southwest monsoon season",
    },
}

# Single Source of Truth for Hub Share:
# Computed strictly from official DOA CPP 2026 Planned Production:
# Anuradhapura planned production / National planned production:
# Big Onion: 35,051 t / 82,149 t = 0.4267
# Chilli: 23,186 t / 142,116 t = 0.1631
# Red Onion: 514 t / 76,374 t = 0.0067
# Potato: National coverage
HUB_SHARE: Dict[str, float] = {
    "big_onion": round(35051.0 / 82149.0, 4),
    "chilli": round(23186.0 / 142116.0, 4),
    "chilli_green": round(23186.0 / 142116.0, 4),
    "red_onion": round(514.0 / 76374.0, 4),
    "potato": 0.05,
}

# Regional Secondary District Shares (Matale / Dambulla Hub)
MATALE_HUB_SHARE: Dict[str, float] = {
    "big_onion": round(44262.0 / 82149.0, 4),
    "chilli": round(3292.0 / 142116.0, 4),
}


@dataclass(frozen=True)
class CropConfig:
    crop_id: str
    name_en: str
    name_si: str
    planting_to_harvest_lag_months: int
    base_yield_mt_per_ha: float
    per_capita_monthly_kg: float
    pilot_district_demand_share: float  # Share of pilot market vs national hub flow
    primary_season: str  # Yala or Maha or Both
    min_fair_farmgate_price: float  # Rs/kg floor price for farmers
    storage_loss_rate_monthly: float  # Post-harvest loss rate


@dataclass
class GoviSenseSettings:
    pilot_district: str = "Anuradhapura"
    secondary_district: str = "Matale"
    national_population: float = 22_200_000.0  # DCS Sri Lanka Census projection
    pilot_district_population: float = 940_000.0  # Anuradhapura district
    matale_district_population: float = 515_000.0  # Matale district
    
    # SPI Thresholds (Configurable in config.py, adjustable by officers in /api/simulate)
    # Source: Proposal Section 6; HARTI Market Outlook; docs/assumptions.md
    spi_glut_threshold: float = 0.15
    spi_shortage_threshold: float = -0.15
    spi_ratio_glut_threshold: float = 1.20
    spi_ratio_shortage_threshold: float = 0.80

    # Unreported area ratio range [min, max]
    # Source: DOA Agricultural Statistics Unit (ASU) & HARTI Market Research Division (MRD); docs/assumptions.md
    unreported_area_ratio_min: float = 0.10
    unreported_area_ratio_max: float = 0.25

    # Lead times for importation (weeks)
    # Source: CBSL & Sri Lanka Ports Authority (SLPA) Shipping Trade Bulletin; docs/assumptions.md
    import_lead_time_weeks: Dict[str, int] = field(default_factory=lambda: {
        "big_onion": 7,
        "potato": 6,
        "chilli": 6,
        "red_onion": 6,
    })

    # Linear Programming Cost Parameters for Decision Optimizer (A4)
    # Sources cited in docs/assumptions.md
    storage_cost_rs_per_mt_month: Dict[str, float] = field(default_factory=lambda: {
        "big_onion": 4500.0,
        "chilli": 6000.0,
        "red_onion": 5000.0,
        "potato": 4000.0,
    })
    transport_cost_rs_per_mt_km: float = 45.0  # NTC Freight Tariff Schedule 2025
    distance_to_dambulla_km: Dict[str, float] = field(default_factory=lambda: {
        "Anuradhapura": 65.0,
        "Matale": 45.0,
    })
    cif_colombo_rs_per_mt: Dict[str, float] = field(default_factory=lambda: {
        "big_onion": 140000.0,
        "chilli": 420000.0,
        "red_onion": 210000.0,
        "potato": 180000.0,
    })
    import_tariff_rs_per_mt: Dict[str, float] = field(default_factory=lambda: {
        "big_onion": 50000.0,
        "chilli": 150000.0,
        "red_onion": 60000.0,
        "potato": 50000.0,
    })
    unmet_demand_penalty_rs_per_mt: Dict[str, float] = field(default_factory=lambda: {
        "big_onion": 350000.0,
        "chilli": 900000.0,
        "red_onion": 450000.0,
        "potato": 380000.0,
    })

    # Farmer Allocation Constraints (A1)
    # Source: Proposal Section 6 & DOA Extension Guidelines; docs/assumptions.md
    allocation_change_cap_pct: float = 0.30
    max_farmer_single_crop_share: float = 0.60
    oversupply_stop_rule_threshold: float = 1.10

    # Retail Price Modeling (A2)
    # Source: CBSL Weekly Economic Indicators & HARTI retail-to-wholesale margins; docs/assumptions.md
    transport_markup_rs_kg: float = 12.0
    retail_margin_ratio: float = 0.18
    
    # Crop Definitions
    crops: Dict[str, CropConfig] = field(default_factory=lambda: {
        "big_onion": CropConfig(
            crop_id="big_onion",
            name_en="Big Onion",
            name_si="ලොකු ලූණු",
            planting_to_harvest_lag_months=3,
            base_yield_mt_per_ha=15.5,
            per_capita_monthly_kg=0.45,  # HIES 2019/2023 avg
            pilot_district_demand_share=HUB_SHARE["big_onion"],
            primary_season="Yala",  # Peak harvest July-Oct in Matale/Anuradhapura
            min_fair_farmgate_price=120.0,  # Rs/kg
            storage_loss_rate_monthly=0.08
        ),
        "chilli": CropConfig(
            crop_id="chilli",
            name_en="Chilli (Green/Dry)",
            name_si="අමු මිරිස් / වියළි මිරිස්",
            planting_to_harvest_lag_months=3,
            base_yield_mt_per_ha=5.2,
            per_capita_monthly_kg=0.25,
            pilot_district_demand_share=HUB_SHARE["chilli"],
            primary_season="Both",  # Grown in both Maha and Yala
            min_fair_farmgate_price=350.0,  # Rs/kg
            storage_loss_rate_monthly=0.04
        ),
        "red_onion": CropConfig(
            crop_id="red_onion",
            name_en="Red Onion",
            name_si="රතු ලූණු",
            planting_to_harvest_lag_months=3,
            base_yield_mt_per_ha=13.6,
            per_capita_monthly_kg=0.30,
            pilot_district_demand_share=HUB_SHARE["red_onion"],
            primary_season="Both",
            min_fair_farmgate_price=180.0,
            storage_loss_rate_monthly=0.06
        ),
        "potato": CropConfig(
            crop_id="potato",
            name_en="Potato",
            name_si="අර්තාපල්",
            planting_to_harvest_lag_months=3,
            base_yield_mt_per_ha=16.6,
            per_capita_monthly_kg=0.40,
            pilot_district_demand_share=HUB_SHARE["potato"],
            primary_season="Both",
            min_fair_farmgate_price=220.0,
            storage_loss_rate_monthly=0.05
        )
    })

    # Available land constraint for pilot area (hectares)
    max_arable_land_ha: float = 12_500.0

    # PostgreSQL Database persistence configuration
    database_url: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg2://postgres:postgres@localhost:5432/govisense",
        )
    )
    fallback_sqlite_url: str = field(
        default_factory=lambda: os.getenv(
            "FALLBACK_DATABASE_URL",
            f"sqlite:///{DATABASE_DIR / 'govisense.db'}",
        )
    )
    db_echo: bool = field(
        default_factory=lambda: os.getenv("DB_ECHO", "false").lower() in ("true", "1", "yes")
    )


settings = GoviSenseSettings()
