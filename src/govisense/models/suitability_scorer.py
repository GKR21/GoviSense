"""WP2 Suitability Scorer — hard filters then soft 0–100 score.

Team DARKBITE · ModelX 2.0 Phase 1
Pilot: Anuradhapura (Big Onion, Chilli)

Scoring approach
----------------
1. Hard filters (returns None / hard_filtered=True if failed):
   - planting_window_fits: current month inside crop planting window
   - rainfed_ok: if area is rainfed, crop must support rainfed cultivation

2. Soft score (0–100):
   Component weights (drop soil if no pH data → lower confidence):
     water : 0.35
     temp  : 0.20
     soil  : 0.25  (omitted if soil_ph missing → redistribute equally)
     zone  : 0.20

Each component uses score_range() which gives 100 inside the optimal band
and linearly decreases to 0 at the absolute min/max.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from govisense.data.crop_requirements import get_crop_requirements, CropRequirement


# ---------------------------------------------------------------------------
# Helper: trapezoidal score
# ---------------------------------------------------------------------------

def score_range(value: float, opt_low: float, opt_high: float, min_val: float, max_val: float) -> float:
    """
    Return a 0–100 score for *value* relative to an optimal range.

    Inside [opt_low, opt_high] → 100.
    Between [min_val, opt_low] → linearly 0 → 100.
    Between [opt_high, max_val] → linearly 100 → 0.
    Outside [min_val, max_val] → 0.

    Parameters
    ----------
    value : float
        The observed value to score.
    opt_low : float
        Lower bound of the optimal range (score = 100).
    opt_high : float
        Upper bound of the optimal range (score = 100).
    min_val : float
        Absolute minimum — score reaches 0 here.
    max_val : float
        Absolute maximum — score reaches 0 here.

    Returns
    -------
    float
        Score in [0.0, 100.0].
    """
    if value < min_val or value > max_val:
        return 0.0
    if opt_low <= value <= opt_high:
        return 100.0
    if value < opt_low:
        span = opt_low - min_val
        return (value - min_val) / span * 100.0 if span > 0 else 0.0
    # value > opt_high
    span = max_val - opt_high
    return (max_val - value) / span * 100.0 if span > 0 else 0.0


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class SuitabilityResult:
    """Suitability scoring output for one crop."""

    crop_id: str
    crop_name: str
    score_0_100: float
    reasons: List[str] = field(default_factory=list)
    confidence: str = "high"   # "high" | "medium" | "low"
    hard_filtered: bool = False


# ---------------------------------------------------------------------------
# Area conditions input specification
# ---------------------------------------------------------------------------
# Expected keys in the ``area_conditions`` dict passed to SuitabilityScorer:
#   current_month    : int          – calendar month (1-12) for planting window check
#   is_rainfed       : bool         – True if the area has no irrigation
#   annual_rainfall_mm : float      – mean annual rainfall at the site (mm)
#   avg_temp_c       : float        – mean temperature during growing season (°C)
#   soil_ph          : float | None – site soil pH; None = unknown
#   zone             : str          – "dry", "intermediate", or "wet" agro-climatic zone
# Optional:
#   water_mm_available : float      – available water in mm this season (if different from rainfall)


# Agro-zone compatibility per crop (hard-coded for pilot set; can be extended)
_ZONE_COMPAT: Dict[str, List[str]] = {
    "big_onion":    ["dry", "intermediate"],
    "chilli_green": ["dry", "intermediate", "wet"],
    "tomato":       ["dry", "intermediate", "wet"],
    "brinjal":      ["dry", "intermediate", "wet"],
    "bitter_gourd": ["dry", "intermediate", "wet"],
    "snake_gourd":  ["dry", "intermediate", "wet"],
    "long_bean":    ["dry", "intermediate", "wet"],
    "cowpea":       ["dry", "intermediate"],
    "sesame":       ["dry", "intermediate"],
    "mung_bean":    ["dry", "intermediate"],
}


class SuitabilityScorer:
    """
    Scores crop suitability for a given area based on hard filters
    and a weighted multi-criteria soft score.

    Usage::

        scorer = SuitabilityScorer()
        conditions = {
            "current_month": 10,
            "is_rainfed": False,
            "annual_rainfall_mm": 1200,
            "avg_temp_c": 28,
            "soil_ph": 6.5,
            "zone": "dry",
        }
        result = scorer.score(conditions, "big_onion")
        ranking = scorer.rank_crops(conditions)
    """

    WEIGHTS = {
        "water": 0.35,
        "temp":  0.20,
        "soil":  0.25,
        "zone":  0.20,
    }

    def __init__(self) -> None:
        self._crop_reqs = get_crop_requirements()

    def _hard_filter(
        self, conditions: Dict, crop: CropRequirement
    ) -> Optional[str]:
        """
        Apply hard filters.  Returns a failure reason string, or None if passes.
        """
        month = int(conditions.get("current_month", 1))
        is_rainfed = bool(conditions.get("is_rainfed", False))

        if not crop.season_fits(month):
            return (
                f"Planting window mismatch: crop plants {crop.plant_start_month}–"
                f"{crop.plant_end_month}, current month={month}"
            )
        if is_rainfed and not crop.rainfed_ok:
            return f"{crop.crop_name_en} requires irrigation; area is rainfed"

        return None

    def score(self, area_conditions: Dict, crop_id: str) -> Optional[SuitabilityResult]:
        """
        Score one crop for the given area conditions.

        Returns ``None`` if the crop fails a hard filter (hard_filtered=True
        entries are not returned to keep the API clean — callers that want
        hard-filtered entries should check ``hard_filtered`` on the result).

        Parameters
        ----------
        area_conditions : dict
            See module docstring for expected keys.
        crop_id : str
            Key from crop_requirements (e.g. ``"big_onion"``).

        Returns
        -------
        SuitabilityResult | None
            None only when the crop is hard-filtered *and* the caller should
            exclude it entirely.  The method itself returns a SuitabilityResult
            with ``hard_filtered=True``; rank_crops() then removes them.
        """
        crop = self._crop_reqs.get(crop_id)
        if crop is None:
            return None

        reasons: List[str] = []

        # Hard filter
        fail_reason = self._hard_filter(area_conditions, crop)
        if fail_reason:
            return SuitabilityResult(
                crop_id=crop_id,
                crop_name=crop.crop_name_en,
                score_0_100=0.0,
                reasons=[fail_reason],
                confidence="low",
                hard_filtered=True,
            )

        # ----------------------------------------------------------------
        # Soft scoring
        # ----------------------------------------------------------------
        zone = str(conditions.get("zone", "dry")) if (conditions := area_conditions) else "dry"
        soil_ph: Optional[float] = conditions.get("soil_ph")
        rainfall_mm: float = float(conditions.get("annual_rainfall_mm", 1200))
        avg_temp_c: float = float(conditions.get("avg_temp_c", 28))
        water_available: float = float(
            conditions.get("water_mm_available", rainfall_mm * 0.65)  # ~65% of annual in season
        )

        # Water score: compare available water against crop's seasonal water need
        # Optimal band: [water_need × 0.9, water_need × 1.5], min=need × 0.4, max=need × 2.5
        water_need = crop.water_mm_season
        water_score = score_range(
            water_available,
            opt_low=water_need * 0.9,
            opt_high=water_need * 1.5,
            min_val=water_need * 0.4,
            max_val=water_need * 2.5,
        )
        reasons.append(f"Water score: {water_score:.0f}/100 (available={water_available:.0f}mm, need={water_need}mm)")

        # Temp score
        temp_score = score_range(
            avg_temp_c,
            opt_low=crop.temp_opt_low_c,
            opt_high=crop.temp_opt_high_c,
            min_val=crop.temp_min_c,
            max_val=crop.temp_max_c,
        )
        reasons.append(f"Temp score: {temp_score:.0f}/100 (temp={avg_temp_c}°C, opt={crop.temp_opt_low_c}–{crop.temp_opt_high_c}°C)")

        # Soil score (skip if unknown)
        soil_score: Optional[float] = None
        if soil_ph is not None:
            soil_score = score_range(
                soil_ph,
                opt_low=crop.soil_ph_min,
                opt_high=crop.soil_ph_max,
                min_val=crop.soil_ph_min - 1.0,
                max_val=crop.soil_ph_max + 1.0,
            )
            reasons.append(f"Soil pH score: {soil_score:.0f}/100 (pH={soil_ph}, range={crop.soil_ph_min}–{crop.soil_ph_max})")
        else:
            reasons.append("Soil pH: unknown — soil term dropped, confidence lowered")

        # Zone score: 100 if compatible, 40 if not (partial—some crops tolerate outside zone)
        compat_zones = _ZONE_COMPAT.get(crop_id, ["dry", "intermediate", "wet"])
        zone_score = 100.0 if zone in compat_zones else 40.0
        reasons.append(f"Zone score: {zone_score:.0f}/100 (area={zone}, compatible={compat_zones})")

        # Weighted composite
        if soil_score is not None:
            weights = self.WEIGHTS.copy()
            final_score = (
                weights["water"] * water_score
                + weights["temp"] * temp_score
                + weights["soil"] * soil_score
                + weights["zone"] * zone_score
            )
            confidence = "high"
        else:
            # Redistribute the soil weight equally across remaining three
            w_water = self.WEIGHTS["water"] + self.WEIGHTS["soil"] / 3
            w_temp  = self.WEIGHTS["temp"]  + self.WEIGHTS["soil"] / 3
            w_zone  = self.WEIGHTS["zone"]  + self.WEIGHTS["soil"] / 3
            final_score = (
                w_water * water_score
                + w_temp  * temp_score
                + w_zone  * zone_score
            )
            confidence = "medium"

        final_score = round(min(100.0, max(0.0, final_score)), 1)

        return SuitabilityResult(
            crop_id=crop_id,
            crop_name=crop.crop_name_en,
            score_0_100=final_score,
            reasons=reasons,
            confidence=confidence,
            hard_filtered=False,
        )

    def rank_crops(self, area_conditions: Dict) -> List[SuitabilityResult]:
        """
        Score all crops in the requirements table for the given area conditions.
        Hard-filtered crops are removed.  Returns results sorted by score descending.

        Parameters
        ----------
        area_conditions : dict
            See module docstring.

        Returns
        -------
        List[SuitabilityResult]
            Ranked list, best crop first, hard-filtered crops excluded.
        """
        scored: List[SuitabilityResult] = []
        for crop_id in self._crop_reqs:
            result = self.score(area_conditions, crop_id)
            if result is not None and not result.hard_filtered:
                scored.append(result)
        scored.sort(key=lambda r: r.score_0_100, reverse=True)
        return scored


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    scorer = SuitabilityScorer()

    conditions = {
        "current_month": 10,
        "is_rainfed": False,
        "annual_rainfall_mm": 1100,
        "avg_temp_c": 28,
        "soil_ph": 6.8,
        "zone": "dry",
    }

    print("=== score_range sanity checks ===")
    assert score_range(25, 20, 28, 10, 35) == 100.0,  "Inside opt band"
    assert score_range(10, 20, 28, 10, 35) == 0.0,    "At min_val"
    assert score_range(35, 20, 28, 10, 35) == 0.0,    "At max_val"
    assert 0 < score_range(15, 20, 28, 10, 35) < 100, "Between min and opt_low"
    print("  Passed!")

    print("\n=== Full suitability ranking for October, dry zone ===")
    ranking = scorer.rank_crops(conditions)
    for i, r in enumerate(ranking, 1):
        print(f"  {i:2d}. {r.crop_name:20s}  {r.score_0_100:5.1f}/100  [{r.confidence}]")

    print("\n=== Big onion score detail ===")
    r = scorer.score(conditions, "big_onion")
    if r:
        for reason in r.reasons:
            print(f"  • {reason}")
