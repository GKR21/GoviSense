"""
AI 3 – Supply Pressure Index (SPI) Engine
Team DARKBITE · ModelX 2.0 Phase 1
Pilot: Anuradhapura (Big Onion, Chilli)

Calculates the headline balance score:
SPI = (Forecast Supply - Projected Demand) / Projected Demand

Labels:
- Glut (> +0.15): Oversupply, price crash likely
- Balanced (-0.15 to +0.15): Stable market
- Shortage (< -0.15): Undersupply, price spike likely
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from govisense.config import settings


@dataclass
class SPIResult:
    crop: str
    target_date: str
    forecast_supply_mt: float
    projected_demand_mt: float
    gap_mt: float
    spi_score: float
    spi_label: str  # "Glut", "Balanced", "Shortage"
    action_summary: str


class SupplyPressureEngine:
    def __init__(self):
        self.glut_threshold = settings.spi_glut_threshold
        self.shortage_threshold = settings.spi_shortage_threshold
        self.crops_cfg = settings.crops

    def project_monthly_demand(self, crop: str, month: int) -> float:
        """
        Calculates monthly consumption demand based on national population,
        per-capita consumption (HIES statistics), regional trading hub catchment,
        and seasonal calendar adjustments.
        """
        cfg = self.crops_cfg.get(crop)
        if not cfg:
            raise ValueError(f"Unknown crop: {crop}")

        # Calendar adjustment multipliers (e.g. Month 4 Sinhala/Tamil Avurudu, Month 12 Festive)
        festive_weights = {
            1: 1.00, 2: 0.98, 3: 1.05, 4: 1.30, 5: 1.10, 6: 0.95,
            7: 0.96, 8: 1.02, 9: 1.00, 10: 1.05, 11: 1.08, 12: 1.25
        }
        seasonal_factor = festive_weights.get(month, 1.0)
        
        # Regional pilot hub catchment (Dambulla/Anuradhapura trade corridor handles ~50% of big onion, ~40% of chilli)
        national_demand_mt = (settings.national_population * cfg.per_capita_monthly_kg) / 1000.0
        hub_share = 0.50 if crop == "big_onion" else 0.40
        base_demand_mt = national_demand_mt * hub_share
        return round(base_demand_mt * seasonal_factor, 1)

    def compute_spi(
        self,
        crop: str,
        forecast_supply_mt: float,
        month: int,
        target_date: str = "Upcoming",
        import_volume_mt: float = 0.0
    ) -> SPIResult:
        """
        Computes SPI score using AI 1 forecast supply vs projected demand.
        Includes regional market absorption fraction for pilot area supply.
        """
        projected_demand = self.project_monthly_demand(crop, month)
        
        # Effective available supply in the trading corridor
        effective_supply = (forecast_supply_mt * 0.85) + (import_volume_mt * 0.40)
        gap_mt = effective_supply - projected_demand
        
        if projected_demand <= 0:
            spi = 0.0
        else:
            spi = gap_mt / projected_demand

        spi = round(float(np.clip(spi, -0.65, 0.75)), 3)

        if spi > self.glut_threshold:
            label = "Glut"
            action = "Oversupply detected: Farm-gate crash risk. Activate storage buffers / defer imports."
        elif spi < self.shortage_threshold:
            label = "Shortage"
            action = "Deficit detected: Consumer price spike risk. Nudge planting expansion or plan targeted imports."
        else:
            label = "Balanced"
            action = "Supply & demand in equilibrium. Stable market conditions expected."

        return SPIResult(
            crop=crop,
            target_date=target_date,
            forecast_supply_mt=round(forecast_supply_mt, 1),
            projected_demand_mt=projected_demand,
            gap_mt=round(gap_mt, 1),
            spi_score=spi,
            spi_label=label,
            action_summary=action
        )

    def validate_historical_alignment(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validates the core thesis:
        High-SPI months line up with later wholesale price drops,
        and low-SPI months line up with subsequent price rises.
        """
        results = {}
        for crop_name, group in df.groupby("crop"):
            g = group.sort_values("date").copy()
            # Calculate 1-month and 2-month forward price percentage change
            g["price_pct_change_1m"] = g["wholesale_price_rs_kg"].pct_change(1).shift(-1)
            g["price_pct_change_2m"] = g["wholesale_price_rs_kg"].pct_change(2).shift(-2)
            
            clean_sub = g.dropna(subset=["actual_spi", "price_pct_change_1m"])
            
            # Correlation between SPI and forward price change should be NEGATIVE
            # (High SPI -> Oversupply -> Price change is negative)
            corr_1m = clean_sub["actual_spi"].corr(clean_sub["price_pct_change_1m"])
            corr_2m = clean_sub["actual_spi"].corr(clean_sub["price_pct_change_2m"])
            
            # Hit rate: Did Glut lead to price decline (or flat), and Shortage lead to price increase?
            glut_correct = (clean_sub[clean_sub["actual_spi"] > self.glut_threshold]["price_pct_change_1m"] <= 0.05).mean()
            short_correct = (clean_sub[clean_sub["actual_spi"] < self.shortage_threshold]["price_pct_change_1m"] >= -0.05).mean()
            overall_hit_rate = np.nanmean([glut_correct, short_correct]) * 100

            results[crop_name] = {
                "spi_vs_next_month_price_change_corr": round(float(corr_1m), 3),
                "spi_vs_2month_price_change_corr": round(float(corr_2m), 3),
                "glut_prediction_hit_rate_pct": round(float(glut_correct) * 100, 1),
                "shortage_prediction_hit_rate_pct": round(float(short_correct) * 100, 1),
                "overall_direction_hit_rate_pct": round(float(overall_hit_rate), 1),
                "thesis_confirmed": bool(corr_1m < -0.20 and overall_hit_rate > 65.0)
            }
        return results
