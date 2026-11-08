"""
GoviSense Counterfactual Simulation Data Generator
Team DARKBITE · ModelX 2.0 Phase 1
Pilot: Anuradhapura (Big Onion, Chilli)

POLICY: SYNTHETIC DATA IS STRICTLY FOR LABELLED COUNTERFACTUAL SIMULATIONS.
Empirical production baseline uses monthly_master.csv (compiled from CBSL, HARTI, CPP, WFP).
This generator produces labelled counterfactual stress-test scenarios (e.g. climate anomalies,
import embargoes, acreage surges) for MarketAdoptionSimulator and Sandbox tests.
"""

from __future__ import annotations

import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from govisense.config import settings, DEMO_DATA_DIR, PROCESSED_DATA_DIR, HUB_SHARE


def generate_counterfactual_simulation_dataset(
    scenario_name: str = "stress_test_extreme_monsoon",
    rain_anomaly_scale: float = 60.0,
    acreage_expansion_pct: float = 0.20,
) -> pd.DataFrame:
    """
    Generates labelled synthetic time-series for stress-testing AI models and decision optimization.
    Every record is explicitly marked with is_simulation = True.
    """
    np.random.seed(42)
    dates = pd.date_range(start="2018-01-01", end="2024-12-01", freq="MS")

    records = []
    for crop in ["big_onion", "chilli"]:
        cfg = settings.crops[crop]
        national_demand = (settings.national_population * cfg.per_capita_monthly_kg) / 1000.0
        hub_share = HUB_SHARE.get(crop, 0.1631)
        base_hub_demand = national_demand * hub_share

        prev_price = 85.0 if crop == "big_onion" else 220.0
        prev_spi = 0.0

        for dt in dates:
            year = dt.year
            month = dt.month
            year_month = dt.strftime("%Y-%m")

            # Simulated weather anomaly
            is_maha_rain = month in [10, 11, 12, 1]
            base_rain = 180.0 if is_maha_rain else 60.0
            rain_anomaly = round(float(np.random.normal(0, rain_anomaly_scale)), 1)
            actual_rain = max(5.0, round(base_rain + rain_anomaly, 1))

            planted_extent = 3200.0 * (1.0 + acreage_expansion_pct) if month in [5, 6] else 300.0
            yield_val = 15.0 if crop == "big_onion" else 5.2
            harvest_vol = round(planted_extent * yield_val * 0.85, 1)
            import_vol = 500.0 if month in [8, 9] else 2500.0
            projected_demand = base_hub_demand

            effective_supply = (harvest_vol * 0.85) + (import_vol * 0.40)
            spi = round(float(np.clip((effective_supply - projected_demand) / projected_demand, -0.65, 0.75)), 3)

            wholesale_price = round(prev_price * (1.0 - 0.15 * spi), 1)
            retail_price = round(wholesale_price * 1.35 + 15.0, 1)
            farmgate_price = round(wholesale_price * 0.82, 1)

            prev_price = wholesale_price
            prev_spi = spi

            records.append({
                "year_month": year_month,
                "date": dt.strftime("%Y-%m-%d"),
                "year": year,
                "month": month,
                "district": "Anuradhapura",
                "crop": crop,
                "planted_extent_ha": planted_extent,
                "yield_mt_per_ha": yield_val,
                "harvest_volume_mt": harvest_vol,
                "projected_demand_mt": projected_demand,
                "import_volume_mt": import_vol,
                "rainfall_mm": actual_rain,
                "rainfall_anomaly_mm": rain_anomaly,
                "temp_celsius": 29.0,
                "temp_anomaly_celsius": 0.0,
                "wholesale_price_rs_kg": wholesale_price,
                "retail_price_rs_kg": retail_price,
                "farmgate_price_rs_kg": farmgate_price,
                "actual_spi": spi,
                "spi_class": "Glut" if spi > 0.15 else ("Shortage" if spi < -0.15 else "Balanced"),
                "is_interpolated": False,
                "source": "synthetic",  # EXPLICITLY LABELED AS SYNTHETIC SIMULATION
                "is_simulation": True,
                "simulation_scenario": scenario_name,
                "data_source": "demo_synthetic_only",
            })

    sim_df = pd.DataFrame(records)
    out_file = DEMO_DATA_DIR / f"demo_simulated_{scenario_name}.csv"
    demo_seed = DEMO_DATA_DIR / "demo_seed_anuradhapura.csv"
    sim_df.to_csv(out_file, index=False)
    sim_df.to_csv(demo_seed, index=False)
    print(f"✅ Generated {len(sim_df)} labelled synthetic demo simulation records at: {out_file}")
    return sim_df


if __name__ == "__main__":
    generate_counterfactual_simulation_dataset()
