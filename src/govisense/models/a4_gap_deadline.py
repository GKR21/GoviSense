"""
AI 4 – Gap-Filling Recommendation Optimizer & Decision Deadline
(GoviSense internal label: AI 4 / WP5)
Team DARKBITE · ModelX 2.0 Phase 1
Pilot: Anuradhapura (Big Onion, Chilli)

Provides:
  1. Gap and Deadline Calculator:
     - gap_mt = demand_mt - supply_mt (positive = shortage, negative = surplus)
     - Best-case and worst-case gap from low/high scenarios
     - Decision deadline: shortage_month_first_day - import_lead_time_weeks
     - Reachable policy options: IMPORT_NOW, IMPORT_LATER, DELAY, STORE
  2. Real-Unit Decision Optimizer (LP):
     - Storage cost (Rs/tonne-month) from HARTI study
     - Transport cost (Rs/tonne-km * distance to Dambulla)
     - Landed CIF + tariff (Rs/tonne)
     - Unmet demand penalty (Rs/tonne)
     - Robust scenario-based regret in LKR
  3. Re-exports FarmerAllocationOptimizer from a1_allocation.py.
"""

from datetime import datetime, date, timedelta
import numpy as np
import scipy.optimize as opt
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from govisense.config import settings, CropConfig
from govisense.models.a3_supply_pressure import SPIResult

# Re-export FarmerAllocationOptimizer from a1_allocation for 100% backward compatibility
from govisense.models.a1_allocation import (
    FarmerAllocationOptimizer,
    FarmerCropAllocation,
    FarmerAllocationResult,
)


@dataclass
class RecommendationAction:
    crop: str
    season: str
    action_type: str  # "IMPORT_NOW", "IMPORT_LATER", "DELAY", "STORE", "PLANT_EXPANSION", "HOLD_STORAGE_BUFFER"
    quantity: float
    unit: str
    target_timeline: str
    rationale: str
    fair_farmgate_floor_rs_kg: float
    best_case_gap_mt: float = 0.0
    mid_case_gap_mt: float = 0.0
    worst_case_gap_mt: float = 0.0
    decision_deadline: str = "T-45 days"
    days_until_deadline: int = 45
    import_lead_time_weeks: int = 7
    policy_option: str = "DELAY"  # "IMPORT_NOW" | "IMPORT_LATER" | "DELAY" | "STORE"
    objective_cost_lkr: float = 0.0
    robust_regret_lkr: float = 0.0


def compute_gap_and_deadline(
    crop: str,
    demand_mt: float,
    supply_mt: float,
    supply_low_mt: Optional[float] = None,
    supply_high_mt: Optional[float] = None,
    shortage_month_first_day: Optional[date] = None,
    as_of_date: Optional[date] = None,
    lead_weeks: Optional[int] = None,
    storage_capacity_mt: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Computes gap_mt = demand_mt - supply_mt (positive = shortage, negative = surplus).
    Calculates best-case and worst-case gap, decision deadline, and policy option.
    Policy options:
      - IMPORT_NOW (severe shortage, deadline within 2 weeks or already passed)
      - IMPORT_LATER (shortage projected, deadline > 2 weeks away)
      - DELAY (marginal gap within uncertainty band, or storage capacity exhausted)
      - STORE (surplus within storage buffer capacity)
    """
    # Gap definition: positive = shortage, negative = surplus
    mid_gap = demand_mt - supply_mt

    s_low = supply_low_mt if supply_low_mt is not None else supply_mt * 0.75
    s_high = supply_high_mt if supply_high_mt is not None else supply_mt * 1.25

    # Low supply gives worst-case shortage (maximum positive gap)
    worst_gap = demand_mt - s_low
    # High supply gives best-case gap (least shortage or deepest surplus)
    best_gap = demand_mt - s_high

    effective_lead_weeks = lead_weeks if lead_weeks is not None else settings.import_lead_time_weeks.get(crop, 7)
    today = as_of_date if as_of_date is not None else date.today()

    if shortage_month_first_day is None:
        shortage_month_first_day = today + timedelta(days=60)

    # Decision deadline formula: shortage_month_first_day - import_lead_time_weeks
    deadline_date = shortage_month_first_day - timedelta(weeks=effective_lead_weeks)
    days_until_deadline = (deadline_date - today).days

    cap = storage_capacity_mt if storage_capacity_mt is not None else getattr(settings, "onion_storage_capacity_mt", 15000.0)

    # Policy option classification
    if mid_gap < -150.0:
        # Clear surplus
        if abs(mid_gap) <= cap:
            policy_option = "STORE"
            action_summary = "Surplus projected: Activate storage buffers and price support."
        else:
            policy_option = "DELAY"
            action_summary = "Storage capacity exhausted: Defer imports and distribute surplus to regional hubs."
    elif mid_gap > 200.0:
        # Significant shortage
        if days_until_deadline <= 14:
            policy_option = "IMPORT_NOW"
            action_summary = "Urgent deficit: Decision deadline within 2 weeks, execute import tender immediately."
        else:
            policy_option = "IMPORT_LATER"
            action_summary = f"Shortage projected: Procurement planned for {days_until_deadline} days ahead."
    else:
        # Marginal gap within uncertainty band -> DELAY
        policy_option = "DELAY"
        action_summary = "Marginal gap within confidence band: Defer trade decision until next month's ground reports."

    return {
        "crop": crop,
        "gap_mt": round(mid_gap, 1),
        "mid_case_gap_mt": round(mid_gap, 1),
        "best_case_gap_mt": round(best_gap, 1),
        "worst_case_gap_mt": round(worst_gap, 1),
        "decision_deadline": deadline_date.isoformat(),
        "decision_deadline_date": deadline_date.isoformat(),
        "days_until_deadline": days_until_deadline,
        "is_deadline_passed": bool(days_until_deadline < 0),
        "import_lead_time_weeks": effective_lead_weeks,
        "policy_option": policy_option,
        "action_summary": action_summary,
    }


class GapFillingOptimizer:
    """
    Linear Programming Decision Optimizer in Real Units (LKR).
    Minimizes total system economic cost across pilot crops:
      - Storage cost (Rs/tonne-month)
      - Transport cost (Rs/tonne-km * distance to Dambulla)
      - Import landed CIF + tariff (Rs/tonne)
      - Unmet demand shortage penalty (Rs/tonne)
    Outputs: import_mt, store_mt, release_mt, objective value (LKR), and robust regret.
    """

    def __init__(self):
        self.settings = settings
        self.crops = settings.crops
        self.max_land_ha = settings.max_arable_land_ha

    def optimize_recommendations(
        self,
        spi_results: List[SPIResult],
        target_season: str = "Upcoming Maha 2025/2026",
        as_of_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """
        Solves LP for optimal multi-crop supply balancing in real monetary units (LKR).
        """
        crop_list = list(self.crops.keys())
        n_crops = len(crop_list)
        n_vars_per_crop = 4  # plant_ha, store_mt, import_mt, slack_shortage_mt
        total_vars = n_crops * n_vars_per_crop

        c = np.zeros(total_vars)
        bounds = []
        crop_gaps = {}
        today = as_of_date if as_of_date is not None else date.today()

        dist_dambulla_km = settings.distance_to_dambulla_km.get("Anuradhapura", 65.0)
        transport_rate = settings.transport_cost_rs_per_mt_km * dist_dambulla_km

        for i, crop_id in enumerate(crop_list):
            base_idx = i * n_vars_per_crop
            # Match SPI result
            matching_spi = next((r for r in spi_results if r.crop == crop_id), None)
            if matching_spi:
                # Conventional gap: demand - supply
                gap = matching_spi.projected_demand_mt - matching_spi.forecast_supply_mt
            else:
                gap = 0.0
            crop_gaps[crop_id] = gap

            # Real economic unit costs (LKR / MT or LKR / ha)
            # 1. Local cultivation nudge: cost per ha (approx seed/prep incentive)
            c[base_idx + 0] = 50000.0  # LKR/ha
            # 2. Storage buffer cost: storage cost + transport
            storage_cost = settings.storage_cost_rs_per_mt_month.get(crop_id, 4500.0)
            c[base_idx + 1] = storage_cost + transport_rate  # LKR/MT
            # 3. Import landed cost: CIF + Tariff
            cif = settings.cif_colombo_rs_per_mt.get(crop_id, 140000.0)
            tariff = settings.import_tariff_rs_per_mt.get(crop_id, 50000.0)
            c[base_idx + 2] = cif + tariff + transport_rate  # LKR/MT
            # 4. Shortage penalty: welfare cost of unmet staple demand
            c[base_idx + 3] = settings.unmet_demand_penalty_rs_per_mt.get(crop_id, 350000.0)  # LKR/MT

            # Variable bounds
            bounds.append((0.0, 3000.0))  # plant_ha
            bounds.append((0.0, 5000.0))  # store_mt
            # If local market has surplus (gap < 0), zero imports allowed
            if gap < -50.0:
                bounds.append((0.0, 0.0))
            else:
                bounds.append((0.0, 6000.0))
            bounds.append((0.0, None))    # slack

        # Arable land constraint: sum plant_ha <= max_extra_land
        A_ub = []
        b_ub = []
        land_row = np.zeros(total_vars)
        for i in range(n_crops):
            land_row[i * n_vars_per_crop + 0] = 1.0
        A_ub.append(land_row)
        b_ub.append(4000.0)

        # Balance constraints per crop
        for i, crop_id in enumerate(crop_list):
            cfg = self.crops[crop_id]
            base_idx = i * n_vars_per_crop
            gap = crop_gaps.get(crop_id, 0.0)
            yield_mt = cfg.base_yield_mt_per_ha * 0.85

            if gap > 0:
                # Shortage: (plant_ha * yield) + import_mt + slack >= gap
                cov_row = np.zeros(total_vars)
                cov_row[base_idx + 0] = -yield_mt
                cov_row[base_idx + 2] = -1.0
                cov_row[base_idx + 3] = -1.0
                A_ub.append(cov_row)
                b_ub.append(-gap)
            else:
                # Surplus: store_mt + slack >= |gap|
                cov_row = np.zeros(total_vars)
                cov_row[base_idx + 1] = -1.0
                cov_row[base_idx + 3] = -1.0
                A_ub.append(cov_row)
                b_ub.append(gap)

        res = opt.linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), bounds=bounds, method="highs")
        objective_lkr = float(res.fun) if res.success else 0.0

        actions: List[RecommendationAction] = []
        spi_map = {r.crop: r for r in spi_results}

        for i, crop_id in enumerate(crop_list):
            cfg = self.crops[crop_id]
            base_idx = i * n_vars_per_crop
            spi_res = spi_map.get(crop_id)

            if res.success:
                d_area = float(res.x[base_idx + 0])
                h_buf = float(res.x[base_idx + 1])
                i_q = float(res.x[base_idx + 2])
            else:
                d_area, h_buf, i_q = 0.0, 0.0, 0.0

            gap_val = crop_gaps.get(crop_id, 0.0)
            s_low_val = spi_res.scenarios["low"].supply_mt if (spi_res and spi_res.scenarios) else None
            s_high_val = spi_res.scenarios["high"].supply_mt if (spi_res and spi_res.scenarios) else None
            d_demand = spi_res.projected_demand_mt if spi_res else 5000.0
            d_supply = spi_res.forecast_supply_mt if spi_res else 5000.0

            # Compute gap & deadline metrics
            gap_info = compute_gap_and_deadline(
                crop=crop_id,
                demand_mt=d_demand,
                supply_mt=d_supply,
                supply_low_mt=s_low_val,
                supply_high_mt=s_high_val,
                as_of_date=today,
            )

            # Scenario Regret Calculation (LKR):
            # Regret = Cost(chosen_action, scenario) - Cost(optimal_action_for_scenario)
            # Under low scenario (deepest deficit), cost of unmet deficit:
            unmet_low_scenario = max(0.0, gap_info["worst_case_gap_mt"] - (i_q + d_area * cfg.base_yield_mt_per_ha))
            regret_lkr = unmet_low_scenario * (
                settings.unmet_demand_penalty_rs_per_mt.get(crop_id, 350000.0)
                - (settings.cif_colombo_rs_per_mt.get(crop_id, 140000.0) + settings.import_tariff_rs_per_mt.get(crop_id, 50000.0))
            )
            regret_lkr = max(0.0, round(float(regret_lkr), 2))

            if gap_info["policy_option"] == "STORE" or h_buf > 5.0:
                actions.append(
                    RecommendationAction(
                        crop=cfg.name_en,
                        season=target_season,
                        action_type="HOLD_STORAGE_BUFFER",
                        quantity=round(max(h_buf, abs(gap_val)), 1),
                        unit="MT",
                        target_timeline="Activate dedicated warehouse storage (Dambulla/Anuradhapura)",
                        rationale=f"Absorb {abs(gap_val):.1f} MT surplus into storage buffer to protect fair farmgate floor (Rs {cfg.min_fair_farmgate_price}/kg).",
                        fair_farmgate_floor_rs_kg=cfg.min_fair_farmgate_price,
                        best_case_gap_mt=gap_info["best_case_gap_mt"],
                        mid_case_gap_mt=gap_info["mid_case_gap_mt"],
                        worst_case_gap_mt=gap_info["worst_case_gap_mt"],
                        decision_deadline=gap_info["decision_deadline_date"],
                        days_until_deadline=gap_info["days_until_deadline"],
                        import_lead_time_weeks=gap_info["import_lead_time_weeks"],
                        policy_option="STORE",
                        objective_cost_lkr=round(objective_lkr, 2),
                        robust_regret_lkr=regret_lkr,
                    )
                )
            elif gap_info["policy_option"] in ["IMPORT_NOW", "IMPORT_LATER"] or i_q > 5.0 or d_area > 5.0:
                if d_area > 5.0:
                    actions.append(
                        RecommendationAction(
                            crop=cfg.name_en,
                            season=target_season,
                            action_type="PLANT_EXPANSION",
                            quantity=round(d_area, 1),
                            unit="hectares",
                            target_timeline="Nudge farmers within DoA planting window (next 30 days)",
                            rationale=f"Fills {round(d_area * cfg.base_yield_mt_per_ha, 1)} MT deficit via local cultivation.",
                            fair_farmgate_floor_rs_kg=cfg.min_fair_farmgate_price,
                            best_case_gap_mt=gap_info["best_case_gap_mt"],
                            mid_case_gap_mt=gap_info["mid_case_gap_mt"],
                            worst_case_gap_mt=gap_info["worst_case_gap_mt"],
                            decision_deadline=gap_info["decision_deadline_date"],
                            days_until_deadline=gap_info["days_until_deadline"],
                            import_lead_time_weeks=gap_info["import_lead_time_weeks"],
                            policy_option=gap_info["policy_option"],
                            objective_cost_lkr=round(objective_lkr, 2),
                            robust_regret_lkr=regret_lkr,
                        )
                    )
                if i_q > 5.0 or gap_info["policy_option"] in ["IMPORT_NOW", "IMPORT_LATER"]:
                    actions.append(
                        RecommendationAction(
                            crop=cfg.name_en,
                            season=target_season,
                            action_type="TARGETED_IMPORT",
                            quantity=round(max(i_q, gap_val), 1),
                            unit="MT",
                            target_timeline=f"Execute import procurement {gap_info['import_lead_time_weeks']} weeks ahead",
                            rationale=f"Targeted import to fill {gap_val:.1f} MT structural shortage.",
                            fair_farmgate_floor_rs_kg=cfg.min_fair_farmgate_price,
                            best_case_gap_mt=gap_info["best_case_gap_mt"],
                            mid_case_gap_mt=gap_info["mid_case_gap_mt"],
                            worst_case_gap_mt=gap_info["worst_case_gap_mt"],
                            decision_deadline=gap_info["decision_deadline_date"],
                            days_until_deadline=gap_info["days_until_deadline"],
                            import_lead_time_weeks=gap_info["import_lead_time_weeks"],
                            policy_option=gap_info["policy_option"],
                            objective_cost_lkr=round(objective_lkr, 2),
                            robust_regret_lkr=regret_lkr,
                        )
                    )
            else:
                actions.append(
                    RecommendationAction(
                        crop=cfg.name_en,
                        season=target_season,
                        action_type="MAINTAIN_CURRENT_EXTENT",
                        quantity=0.0,
                        unit="status_quo",
                        target_timeline="Current season",
                        rationale=f"Market balanced within uncertainty band (Gap: {gap_val:.1f} MT). Option: DELAY trade intervention.",
                        fair_farmgate_floor_rs_kg=cfg.min_fair_farmgate_price,
                        best_case_gap_mt=gap_info["best_case_gap_mt"],
                        mid_case_gap_mt=gap_info["mid_case_gap_mt"],
                        worst_case_gap_mt=gap_info["worst_case_gap_mt"],
                        decision_deadline=gap_info["decision_deadline_date"],
                        days_until_deadline=gap_info["days_until_deadline"],
                        import_lead_time_weeks=gap_info["import_lead_time_weeks"],
                        policy_option="DELAY",
                        objective_cost_lkr=round(objective_lkr, 2),
                        robust_regret_lkr=0.0,
                    )
                )

        return {
            "solver_status": "OPTIMAL" if res.success else "FALLBACK",
            "target_season": target_season,
            "pilot_district": self.settings.pilot_district,
            "total_objective_cost_lkr": round(objective_lkr, 2),
            "actions": actions,
        }
