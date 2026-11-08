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
    
    # SPI Thresholds
    spi_glut_threshold: float = 0.15
    spi_shortage_threshold: float = -0.15
    
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
