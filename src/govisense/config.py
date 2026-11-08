"""
GoviSense Configuration Module
Team DARKBITE · ModelX 2.0 Phase 1
Pilot: Anuradhapura (Big Onion, Chilli)
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List

# Workspace Root & Directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DEMO_DATA_DIR = DATA_DIR / "demo"
MODELS_STORE_DIR = BASE_DIR / "models_store"

# Ensure runtime directories exist
for folder in [RAW_DATA_DIR, INTERIM_DATA_DIR, PROCESSED_DATA_DIR, DEMO_DATA_DIR, MODELS_STORE_DIR]:
    folder.mkdir(parents=True, exist_ok=True)


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
    national_population: float = 22_200_000.0  # DCS Sri Lanka Census projection
    pilot_district_population: float = 940_000.0  # Anuradhapura district
    
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
            pilot_district_demand_share=0.12,  # Anuradhapura/Dambulla regional hub demand
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
            pilot_district_demand_share=0.10,
            primary_season="Both",  # Grown in both Maha and Yala
            min_fair_farmgate_price=350.0,  # Rs/kg
            storage_loss_rate_monthly=0.04
        )
    })

    # Available land constraint for pilot area (hectares)
    max_arable_land_ha: float = 12_500.0


settings = GoviSenseSettings()
