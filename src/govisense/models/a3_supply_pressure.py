"""
A3 Supply Pressure Index (SPI) Engine
(GoviSense internal label: AI 3 / WP3)
Team DARKBITE · ModelX 2.0 Phase 1
Pilot: Anuradhapura (Big Onion, Chilli)

Calculates the headline balance score:
  SPI = (Effective Supply - Projected Demand) / Projected Demand

Labels:
  Glut     (> +0.15): Oversupply, price crash likely
  Balanced (-0.15 to +0.15): Stable market
  Shortage (< -0.15): Undersupply, price spike likely

Demand is provided by the DemandEstimator module (WP1) — not a hardcoded constant.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from govisense.config import settings
from govisense.models.demand_estimator import DemandEstimator


@dataclass
class SPIScenario:
    scenario: str           # "low", "mid", "high"
    supply_mt: float
    demand_mt: float
    gap_mt: float
    spi_ratio: float        # S / D (Bands 0.8 / 1.2)
    spi_score: float        # (S - D) / D (Bands ±0.15)
    spi_label: str          # "Glut", "Balanced", "Shortage"


@dataclass
class SPIResult:
    crop: str
    target_date: str
    forecast_supply_mt: float
    projected_demand_mt: float
    gap_mt: float
    spi_score: float        # Delta formula: (Supply - Demand) / Demand
    spi_ratio: float = 1.0  # Ratio formula: Supply / Demand (Bands 0.8 / 1.2)
    spi_label: str = "Balanced"  # "Glut", "Balanced", "Shortage"
    action_summary: str = ""
    demand_low_mt: float = 0.0
    demand_high_mt: float = 0.0
    confidence_badge: str = "medium"
    scenarios: Dict[str, SPIScenario] = field(default_factory=dict)


class SupplyPressureEngine:
    """
    Computes the Supply Pressure Index (SPI) from forecast supply
    and demand estimates provided by DemandEstimator.
    """

    def __init__(self):
        self.glut_threshold = settings.spi_glut_threshold
        self.shortage_threshold = settings.spi_shortage_threshold
        self.crops_cfg = settings.crops
        self._demand_estimator = DemandEstimator()

    def project_monthly_demand(self, crop: str, month: int, scenario: str = "mid") -> float:
        """
        Returns projected monthly demand (MT) for the pilot hub.
        Delegates to DemandEstimator (WP1) — no longer a hardcoded formula.
        """
        result = self._demand_estimator.estimate(crop, month, scenario=scenario)
        return result.demand_mt

    def compute_spi(
        self,
        crop: str,
        forecast_supply_mt: float,
        month: int,
        target_date: str = "Upcoming",
        import_volume_mt: float = 0.0,
        confidence_badge: str = "medium",
        supply_low_mt: Optional[float] = None,
        supply_high_mt: Optional[float] = None,
        loss_pct: float = 0.15,
    ) -> SPIResult:
        """
        Compute SPI score using forecast supply vs projected demand.
        Calculates both the ratio formula (SPI = Supply / Demand, bands 0.8 / 1.2)
        and deviation formula (SPI = (Supply - Demand) / Demand, bands ±0.15).
        Generates low, mid, and high uncertainty scenarios.
        """
        demand_est_mid = self._demand_estimator.estimate(crop, month, scenario="mid")
        demand_est_low = self._demand_estimator.estimate(crop, month, scenario="low")
        demand_est_high = self._demand_estimator.estimate(crop, month, scenario="high")

        projected_demand = demand_est_mid.demand_mt
        net_retention = 1.0 - loss_pct

        # Effective available supply
        effective_supply = (forecast_supply_mt * net_retention) + (import_volume_mt * 0.40)
        gap_mt = effective_supply - projected_demand

        # Delta formula: (S - D) / D
        if projected_demand <= 0:
            spi_score = 0.0
            spi_ratio = 1.0
        else:
            spi_score = gap_mt / projected_demand
            spi_ratio = effective_supply / projected_demand

        spi_score = round(float(np.clip(spi_score, -0.65, 0.75)), 3)
        spi_ratio = round(float(np.clip(spi_ratio, 0.35, 1.75)), 3)

        # Classification based on 0.8 / 1.2 ratio bands (equivalent to ±0.15/0.20 delta)
        if spi_ratio > 1.20 or spi_score > self.glut_threshold:
            label = "Glut"
            action = "Oversupply detected: Farm-gate crash risk. Activate storage buffers / defer imports."
        elif spi_ratio < 0.80 or spi_score < self.shortage_threshold:
            label = "Shortage"
            action = "Deficit detected: Consumer price spike risk. Nudge planting expansion or plan targeted imports."
        else:
            label = "Balanced"
            action = "Supply & demand in equilibrium. Stable market conditions expected."

        # Compute three scenarios (low, mid, high)
        s_low = supply_low_mt if supply_low_mt is not None else forecast_supply_mt * 0.85
        s_high = supply_high_mt if supply_high_mt is not None else forecast_supply_mt * 1.15

        eff_low = (s_low * net_retention) + (import_volume_mt * 0.40)
        eff_high = (s_high * net_retention) + (import_volume_mt * 0.40)

        # Low scenario (pessimistic: lowest supply vs highest demand)
        d_high = demand_est_high.demand_mt
        gap_low = eff_low - d_high
        ratio_low = eff_low / max(d_high, 1.0)
        score_low = gap_low / max(d_high, 1.0)
        label_low = "Glut" if ratio_low > 1.20 else ("Shortage" if ratio_low < 0.80 else "Balanced")

        # Mid scenario
        ratio_mid = spi_ratio
        score_mid = spi_score
        label_mid = label

        # High scenario (optimistic: highest supply vs lowest demand)
        d_low = demand_est_low.demand_mt
        gap_high = eff_high - d_low
        ratio_high = eff_high / max(d_low, 1.0)
        score_high = gap_high / max(d_low, 1.0)
        label_high = "Glut" if ratio_high > 1.20 else ("Shortage" if ratio_high < 0.80 else "Balanced")

        scenarios_dict = {
            "low": SPIScenario(
                scenario="low",
                supply_mt=round(s_low, 1),
                demand_mt=round(d_high, 1),
                gap_mt=round(gap_low, 1),
                spi_ratio=round(ratio_low, 3),
                spi_score=round(score_low, 3),
                spi_label=label_low,
            ),
            "mid": SPIScenario(
                scenario="mid",
                supply_mt=round(forecast_supply_mt, 1),
                demand_mt=round(projected_demand, 1),
                gap_mt=round(gap_mt, 1),
                spi_ratio=round(ratio_mid, 3),
                spi_score=round(score_mid, 3),
                spi_label=label_mid,
            ),
            "high": SPIScenario(
                scenario="high",
                supply_mt=round(s_high, 1),
                demand_mt=round(d_low, 1),
                gap_mt=round(gap_high, 1),
                spi_ratio=round(ratio_high, 3),
                spi_score=round(score_high, 3),
                spi_label=label_high,
            ),
        }

        return SPIResult(
            crop=crop,
            target_date=target_date,
            forecast_supply_mt=round(forecast_supply_mt, 1),
            projected_demand_mt=projected_demand,
            demand_low_mt=demand_est_low.demand_mt,
            demand_high_mt=demand_est_high.demand_mt,
            gap_mt=round(gap_mt, 1),
            spi_score=spi_score,
            spi_ratio=spi_ratio,
            spi_label=label,
            action_summary=action,
            confidence_badge=confidence_badge,
            scenarios=scenarios_dict,
        )

    def validate_historical_alignment(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validates the core thesis: high-SPI months correlate with subsequent
        wholesale price drops, and low-SPI months with subsequent price rises.

        Reports:
          - SPI vs forward price change correlation (1m, 2m)
          - Directional hit rate
          - Precision and recall for Glut and Shortage classes
          - Majority-class baseline hit rate
          - Confidence badge and thesis confirmation
        """
        results = {}
        for crop_name, group in df.groupby("crop"):
            g = group.sort_values("date").copy()
            g["price_pct_change_1m"] = g["wholesale_price_rs_kg"].pct_change(1).shift(-1)
            g["price_pct_change_2m"] = g["wholesale_price_rs_kg"].pct_change(2).shift(-2)

            clean_sub = g.dropna(subset=["actual_spi", "price_pct_change_1m"])

            # Correlation: SPI vs forward price change (expected negative)
            corr_1m = clean_sub["actual_spi"].corr(clean_sub["price_pct_change_1m"])
            corr_2m = clean_sub["actual_spi"].corr(clean_sub["price_pct_change_2m"])

            # Directional hit rate
            glut_correct = (
                clean_sub[clean_sub["actual_spi"] > self.glut_threshold]["price_pct_change_1m"] <= 0.05
            ).mean()
            short_correct = (
                clean_sub[clean_sub["actual_spi"] < self.shortage_threshold]["price_pct_change_1m"] >= -0.05
            ).mean()
            overall_hit_rate = np.nanmean([glut_correct, short_correct]) * 100

            # Majority-class baseline
            n = len(clean_sub)
            labels = clean_sub["spi_class"].values if "spi_class" in clean_sub.columns else []
            if len(labels) > 0:
                majority = max(set(labels), key=list(labels).count)
                majority_hit = list(labels).count(majority) / max(n, 1) * 100
            else:
                majority_hit = 0.0

            # Precision & recall for Glut and Shortage
            def _pr(df_sub, cls):
                if "spi_class" not in df_sub.columns:
                    return {"precision": None, "recall": None}
                # Predicted label from actual_spi column
                pred_labels = df_sub["actual_spi"].apply(
                    lambda s: "Glut" if s > self.glut_threshold
                    else ("Shortage" if s < self.shortage_threshold else "Balanced")
                )
                true_labels = df_sub["spi_class"]
                tp = ((true_labels == cls) & (pred_labels == cls)).sum()
                fp = ((true_labels != cls) & (pred_labels == cls)).sum()
                fn = ((true_labels == cls) & (pred_labels != cls)).sum()
                precision = tp / max(tp + fp, 1)
                recall = tp / max(tp + fn, 1)
                return {"precision": round(float(precision), 3), "recall": round(float(recall), 3)}

            glut_pr = _pr(clean_sub, "Glut")
            shortage_pr = _pr(clean_sub, "Shortage")

            thesis_confirmed = bool(corr_1m < -0.20 and overall_hit_rate > 65.0)

            # Confidence badge
            if not thesis_confirmed:
                badge = "low"
                badge_reason = "Price pressure did not follow SPI — low confidence for this crop."
            elif overall_hit_rate > 75:
                badge = "high"
                badge_reason = "SPI thesis confirmed with high directional hit rate."
            else:
                badge = "medium"
                badge_reason = "SPI thesis partially confirmed."

            results[crop_name] = {
                "spi_vs_next_month_price_change_corr": round(float(corr_1m), 3),
                "spi_vs_2month_price_change_corr": round(float(corr_2m), 3),
                "glut_prediction_hit_rate_pct": round(float(glut_correct) * 100, 1),
                "shortage_prediction_hit_rate_pct": round(float(short_correct) * 100, 1),
                "overall_direction_hit_rate_pct": round(float(overall_hit_rate), 1),
                "majority_class_baseline_pct": round(float(majority_hit), 1),
                "glut_precision": glut_pr["precision"],
                "glut_recall": glut_pr["recall"],
                "shortage_precision": shortage_pr["precision"],
                "shortage_recall": shortage_pr["recall"],
                "thesis_confirmed": thesis_confirmed,
                "confidence_badge": badge,
                "confidence_reason": badge_reason,
            }
        return results
