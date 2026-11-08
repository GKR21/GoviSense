"""
WP2 Target Area Calculator
Team DARKBITE · ModelX 2.0 Phase 1
Pilot: Anuradhapura (Big Onion, Chilli)

Computes the recommended planted area (ha) for a crop in a given season
to meet a given demand target, accounting for post-harvest losses and a
safety buffer.  Caps recommendations at the available suitable land.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union, List, Dict, Any


@dataclass
class TargetAreaResult:
    """Result of TargetAreaCalculator.compute()."""

    crop: str
    season: str
    demand_season_mt: float       # Seasonal demand (MT) used as input
    yield_mid_mt_ha: float        # Mid yield used in calculation
    loss_pct: float               # Post-harvest loss fraction
    buffer: float                 # Safety buffer fraction (default 0.05 = 5%)
    a_target_ha: float            # Raw target area to meet demand
    a_cap_ha: Optional[float]     # Cap from suitable land area (None = uncapped)
    a_reported_ha: float          # Already-reported/committed area this season
    a_rec_ha: float               # Final recommended additional area (ha)
    rationale: str                # Human-readable explanation


class TargetAreaCalculator:
    """
    Computes the recommended additional planted area for a crop to bridge
    the gap between seasonal demand and existing committed supply.

    Formula
    -------
    .. code-block:: text

        A_target = demand_season * (1 + buffer) / (yield_mid * (1 - loss_pct))

        A_cap    = suitable_land[crop] where fit >= threshold (if parcels provided)
        A_capped = min(A_target, A_cap) if A_cap is not None else A_target

        A_rec    = max(0, A_capped - a_reported)
                   -- but only if a_reported < 1.1 * A_target
                   -- (if area already > 110% of target, oversupply stop rule applies: A_rec = 0)
    """

    @staticmethod
    def calculate_cap(
        suitable_parcels: List[Dict[str, Any]],
        fit_threshold: float = 60.0,
    ) -> float:
        """
        Calculate A_cap as the sum of parcel land areas (ha) where fit score >= threshold.
        Each parcel is a dict with 'land_ha' and 'fit_score'.
        """
        total_ha = sum(
            float(p.get("land_ha", 0.0))
            for p in suitable_parcels
            if float(p.get("fit_score", 0.0)) >= fit_threshold
        )
        return round(total_ha, 1)

    def compute(
        self,
        crop: str,
        season: str,
        demand_mt: float,
        yield_mid: float,
        loss_pct: float,
        buffer: float = 0.05,
        a_reported: float = 0.0,
        suitable_land_ha: Optional[Union[float, List[Dict[str, Any]]]] = None,
        fit_threshold: float = 60.0,
    ) -> TargetAreaResult:
        """
        Compute recommended planted area.

        Parameters
        ----------
        crop : str
            Crop identifier.
        season : str
            Season label (e.g. 'Maha 2025/2026').
        demand_mt : float
            Seasonal demand target in MT.
        yield_mid : float
            Expected yield in MT/ha.
        loss_pct : float
            Post-harvest loss fraction in [0, 1).
        buffer : float
            Safety buffer fraction (e.g. 0.05 for 5%).
        a_reported : float
            Already-reported / committed area (ha).
        suitable_land_ha : float | List[dict] | None
            Available suitable land in ha, or a list of parcels with 'land_ha' and 'fit_score'.
        fit_threshold : float
            Minimum suitability score required to count parcel towards A_cap (default 60.0).
        """
        if yield_mid <= 0:
            raise ValueError(f"yield_mid must be > 0, got {yield_mid}")
        if not (0.0 <= loss_pct < 1.0):
            raise ValueError(f"loss_pct must be in [0, 1), got {loss_pct}")
        if buffer < 0:
            raise ValueError(f"buffer must be >= 0, got {buffer}")

        # Core formula: A_target = demand_season * (1 + buffer) / (yield_mid * (1 - loss))
        effective_yield = yield_mid * (1.0 - loss_pct)
        a_target = demand_mt * (1.0 + buffer) / effective_yield

        # A_cap = suitable_land[crop] where fit >= threshold
        a_cap: Optional[float] = None
        if isinstance(suitable_land_ha, list):
            a_cap = self.calculate_cap(suitable_land_ha, fit_threshold=fit_threshold)
        elif suitable_land_ha is not None:
            a_cap = float(suitable_land_ha)

        a_capped = min(a_target, a_cap) if a_cap is not None else a_target

        # Oversupply stop rule: A_rec = 0 if reported > 110% of target
        if a_reported >= 1.10 * a_target:
            a_rec = 0.0
            rationale = (
                f"Oversupply stop rule triggered: Already-committed area ({a_reported:.1f} ha) exceeds "
                f"110% of A_target ({a_target:.1f} ha) — no additional planting recommended (A_rec = 0)."
            )
        else:
            # A_rec = max(0, min(A_target, A_cap) - A_reported[crop])
            a_rec = max(0.0, a_capped - a_reported)
            cap_note = (
                f"  Land cap applied at {a_cap:.1f} ha (suitable land with fit ≥ {fit_threshold})."
                if a_cap is not None else ""
            )
            rationale = (
                f"Seasonal demand: {demand_mt:.0f} MT (+{buffer*100:.0f}% buffer) "
                f"requires {a_target:.1f} ha at {yield_mid} MT/ha and {loss_pct*100:.0f}% loss.{cap_note}  "
                f"Existing committed: {a_reported:.1f} ha → additional {a_rec:.1f} ha recommended."
            )

        return TargetAreaResult(
            crop=crop,
            season=season,
            demand_season_mt=round(demand_mt, 1),
            yield_mid_mt_ha=yield_mid,
            loss_pct=loss_pct,
            buffer=buffer,
            a_target_ha=round(a_target, 1),
            a_cap_ha=round(a_cap, 1) if a_cap is not None else None,
            a_reported_ha=round(a_reported, 1),
            a_rec_ha=round(a_rec, 1),
            rationale=rationale,
        )


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    calc = TargetAreaCalculator()

    # Big Onion example: Maha season, 3 months demand ~4 months window
    # Seasonal demand = 4 × monthly demand; monthly ~6667 MT → 26,667 MT for 4 months
    print("=== Big Onion – Maha 2025/2026 ===")
    result = calc.compute(
        crop="big_onion",
        season="Maha 2025/2026",
        demand_mt=26_667,
        yield_mid=15.5,
        loss_pct=0.12,
        buffer=0.05,
        a_reported=500,
        suitable_land_ha=3000,
    )
    print(result)
    print(f"A_rec = {result.a_rec_ha} ha")
    print(f"Rationale: {result.rationale}")

    print("\n=== Chilli – Yala 2026 ===")
    result2 = calc.compute(
        crop="chilli_green",
        season="Yala 2026",
        demand_mt=8_900,
        yield_mid=5.2,
        loss_pct=0.15,
        buffer=0.05,
        a_reported=200,
    )
    print(result2)

    print("\n=== Over-committed scenario ===")
    result3 = calc.compute(
        crop="big_onion",
        season="Maha 2025/2026",
        demand_mt=10_000,
        yield_mid=15.5,
        loss_pct=0.12,
        a_reported=800,  # Well above 1.1 × A_target
    )
    print(f"A_rec = {result3.a_rec_ha} ha (expected 0)")
    print(f"Rationale: {result3.rationale}")
