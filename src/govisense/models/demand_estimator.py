"""
WP1 Demand Estimator
GoviSense — Team DARKBITE · ModelX 2.0 Phase 1

Provides monthly demand estimates per crop with low/mid/high scenario range.

Anchors:
  Big Onion: ~320,000 MT/year national requirement (Commodity Board).
  Chilli & others: DCS per-capita consumption × population.

Usage:
  from govisense.models.demand_estimator import DemandEstimator
  d = DemandEstimator()
  result = d.estimate("big_onion", month=4)   # April (festival)
  print(result.demand_mt, result.demand_low, result.demand_high)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional
from govisense.config import settings


# Seasonal demand multipliers (month → factor).
# April = Sinhala/Tamil New Year, December = Festive season.
SEASONAL_FACTORS: Dict[int, float] = {
    1: 1.00, 2: 0.98, 3: 1.05, 4: 1.30, 5: 1.10, 6: 0.95,
    7: 0.96, 8: 1.02, 9: 1.00, 10: 1.05, 11: 1.08, 12: 1.25,
}

# National annual demand anchors (MT/year).
# Big Onion: Commodity Board confirmed ~320,000 t/year (year to verify).
# Chilli & others: DCS HIES per-capita consumption × national population.
NATIONAL_ANNUAL_DEMAND_MT: Dict[str, Optional[float]] = {
    "big_onion": 320_000.0,
    "chilli": 66_600.0,
    "chilli_green": 66_600.0,
    "tomato": 80_000.0,
    "brinjal": 100_000.0,
    "bitter_gourd": 35_000.0,
    "snake_gourd": 40_000.0,
    "long_bean": 45_000.0,
    "cowpea": 15_000.0,
    "sesame": 10_000.0,
    "mung_bean": 18_000.0,
}

# Anuradhapura/Dambulla trading-hub catchment fraction of national demand
HUB_SHARE: Dict[str, float] = {
    "big_onion": 0.25,   # 50% of Dambulla corridor ≈ 25% national
    "chilli": 0.10,      # 40% of pilot corridor ≈ 10% national
    "chilli_green": 0.10,
    "tomato": 0.15,
    "brinjal": 0.12,
    "bitter_gourd": 0.10,
    "snake_gourd": 0.10,
    "long_bean": 0.10,
    "cowpea": 0.08,
    "sesame": 0.08,
    "mung_bean": 0.08,
}

# Demand scenario spread: ±10%
SCENARIO_SPREAD = 0.10


@dataclass
class DemandResult:
    """Monthly demand estimate for a crop."""
    crop: str
    month: int
    seasonal_factor: float
    demand_mt: float          # mid estimate
    demand_low: float         # -10%
    demand_high: float        # +10%
    source_note: str


class DemandEstimator:
    """
    Computes monthly demand per crop for the Anuradhapura pilot hub.

    Method:
      1. If national annual demand is confirmed (big onion), use it as anchor.
      2. Otherwise compute from per-capita consumption × national population.
      3. Apply hub share fraction (Dambulla/Anuradhapura trading corridor).
      4. Apply seasonal factor for the target month.
      5. Return low/mid/high range (±10%).
    """

    def __init__(self):
        self._pop = settings.national_population

    def _annual_national_demand(self, crop: str):
        """Return (annual_mt, source_note) for a crop."""
        anchor = NATIONAL_ANNUAL_DEMAND_MT.get(crop)
        if anchor is not None:
            if crop == "big_onion":
                return anchor, "Commodity Board national requirement (~320,000 t/year; year to verify)"
            return anchor, "DCS HIES per-capita consumption × national population"

        cfg = settings.crops.get(crop)
        if cfg is None:
            return 0.0, "Unknown crop — no demand data"

        # per_capita_monthly_kg × 12 → annual kg/person; × population / 1000 → MT
        annual_mt = (cfg.per_capita_monthly_kg * 12.0 * self._pop) / 1000.0
        return annual_mt, "DCS HIES per-capita consumption × national population"

    def estimate(
        self,
        crop: str,
        month: int,
        scenario: str = "mid",
    ) -> DemandResult:
        """
        Estimate hub demand for a crop in a given month.

        Args:
            crop:     crop_id string (e.g. "big_onion")
            month:    calendar month 1-12
            scenario: "low", "mid", or "high"
        """
        annual_mt, source = self._annual_national_demand(crop)
        hub = HUB_SHARE.get(crop, 0.10)
        sf = SEASONAL_FACTORS.get(month, 1.0)

        monthly_hub_mt = (annual_mt / 12.0) * hub * sf
        low = monthly_hub_mt * (1.0 - SCENARIO_SPREAD)
        high = monthly_hub_mt * (1.0 + SCENARIO_SPREAD)

        if scenario == "low":
            mid_val = low
        elif scenario == "high":
            mid_val = high
        else:
            mid_val = monthly_hub_mt

        return DemandResult(
            crop=crop,
            month=month,
            seasonal_factor=sf,
            demand_mt=round(mid_val, 1),
            demand_low=round(low, 1),
            demand_high=round(high, 1),
            source_note=source,
        )

    def annual_hub_demand(self, crop: str) -> float:
        """Return the annual hub demand in MT (mid estimate, no seasonal factor)."""
        annual_mt, _ = self._annual_national_demand(crop)
        hub = HUB_SHARE.get(crop, 0.10)
        return round(annual_mt * hub, 1)


if __name__ == "__main__":
    d = DemandEstimator()
    for crop in ["big_onion", "chilli"]:
        print(f"\n=== {crop.upper()} ===")
        print(f"  Annual hub demand: {d.annual_hub_demand(crop):,.1f} MT/year")
        for month in [1, 4, 8, 12]:
            r = d.estimate(crop, month)
            print(
                f"  Month {month:2d} (sf={r.seasonal_factor}): "
                f"low={r.demand_low:.1f}  mid={r.demand_mt:.1f}  high={r.demand_high:.1f} MT"
            )
        print(f"  Source: {d.estimate(crop, 1).source_note}")
