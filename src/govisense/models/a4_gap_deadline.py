"""
AI 4 – Gap-Filling Recommendation Optimizer
Team DARKBITE · ModelX 2.0 Phase 1
Pilot: Anuradhapura (Big Onion, Chilli)

Formulation:
Linear Optimization using scipy.optimize.linprog (Free, open-source scientific engine).
Minimizes total gap cost across pilot crops by solving:
(a) Extra area to plant next season for deficit crops (Delta Area in ha)
(b) Buffer quantity to hold back/store during gluts (Storage in MT)
(c) Import volume to cover remaining structural deficit (Import in MT)

Subject to:
- Arable land constraint (Anuradhapura district arable cap)
- Minimum fair farmgate price support
- Zero imports during local bumper harvests
"""

import numpy as np
import scipy.optimize as opt
from typing import Dict, Any, List
from dataclasses import dataclass
from govisense.config import settings, CropConfig
from govisense.models.a3_supply_pressure import SPIResult


@dataclass
class RecommendationAction:
    crop: str
    season: str
    action_type: str  # "PLANT_EXPANSION", "HOLD_STORAGE_BUFFER", "TARGETED_IMPORT", "MAINTAIN_CURRENT_EXTENT"
    quantity: float
    unit: str
    target_timeline: str
    rationale: str
    fair_farmgate_floor_rs_kg: float


class GapFillingOptimizer:
    def __init__(self):
        self.settings = settings
        self.crops = settings.crops
        self.max_land_ha = settings.max_arable_land_ha

    def optimize_recommendations(
        self,
        spi_results: List[SPIResult],
        target_season: str = "Upcoming Maha 2025/2026",
    ) -> Dict[str, Any]:
        """
        Solves Linear Programming problem for optimal multi-crop supply balancing.
        Variables per crop i:
          x[3*i + 0] = delta_area (ha)
          x[3*i + 1] = hold_buffer (MT)
          x[3*i + 2] = import_quota (MT)
          x[3*i + 3] = residual_slack
        """
        crop_list = list(self.crops.keys())
        n_crops = len(crop_list)
        n_vars_per_crop = 4  # plant_ha, hold_mt, import_mt, slack
        total_vars = n_crops * n_vars_per_crop

        c = np.zeros(total_vars)
        bounds = []

        crop_gaps = {res.crop: res.gap_mt for res in spi_results}

        for i, crop_id in enumerate(crop_list):
            cfg = self.crops[crop_id]
            base_idx = i * n_vars_per_crop
            gap = crop_gaps.get(crop_id, 0.0)

            # Cost weights
            # plant_ha cost: low friction to promote local agriculture
            c[base_idx + 0] = 0.5
            # hold_buffer cost: warehouse refrigeration cost
            c[base_idx + 1] = 2.0
            # import quota: FX drainage penalty
            c[base_idx + 2] = 6.0
            # slack penalty: very high to ensure gaps are filled
            c[base_idx + 3] = 25.0

            # Bounds
            # 1. Delta plant area (0 to 3,000 ha)
            bounds.append((0.0, 3000.0))
            # 2. Hold buffer (0 to 5,000 MT)
            bounds.append((0.0, 5000.0))
            # 3. Import quota: Zero if local market has a glut!
            if gap > 0:
                bounds.append((0.0, 0.0))  # No imports allowed during local glut
            else:
                bounds.append((0.0, 6000.0))
            # 4. Slack
            bounds.append((0.0, None))

        # Constraints: A_ub * x <= b_ub
        A_ub = []
        b_ub = []

        # 1. Total arable land constraint across all crops
        land_row = np.zeros(total_vars)
        for i in range(n_crops):
            land_row[i * n_vars_per_crop + 0] = 1.0  # plant_ha
        A_ub.append(land_row)
        b_ub.append(4000.0)  # Max extra seasonal land

        # 2. Coverage constraints per crop
        for i, crop_id in enumerate(crop_list):
            cfg = self.crops[crop_id]
            base_idx = i * n_vars_per_crop
            gap = crop_gaps.get(crop_id, 0.0)
            yield_mt = cfg.base_yield_mt_per_ha

            if gap < 0:
                # Shortage: deficit = abs(gap)
                # (plant_ha * yield) + import_quota + slack >= abs(gap)
                # -> -plant_ha * yield - import_quota - slack <= -abs(gap)
                deficit = abs(gap)
                cov_row = np.zeros(total_vars)
                cov_row[base_idx + 0] = -yield_mt
                cov_row[base_idx + 2] = -1.0
                cov_row[base_idx + 3] = -1.0
                A_ub.append(cov_row)
                b_ub.append(-deficit)
            else:
                # Glut: surplus = gap
                # hold_buffer + slack >= gap
                # -> -hold_buffer - slack <= -gap
                cov_row = np.zeros(total_vars)
                cov_row[base_idx + 1] = -1.0
                cov_row[base_idx + 3] = -1.0
                A_ub.append(cov_row)
                b_ub.append(-gap)

        res = opt.linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), bounds=bounds, method="highs")

        actions: List[RecommendationAction] = []
        spi_map = {r.crop: r for r in spi_results}

        for i, crop_id in enumerate(crop_list):
            cfg = self.crops[crop_id]
            base_idx = i * n_vars_per_crop
            spi_res = spi_map.get(crop_id)

            if res.success:
                d_area = res.x[base_idx + 0]
                h_buf = res.x[base_idx + 1]
                i_q = res.x[base_idx + 2]
            else:
                d_area, h_buf, i_q = 0.0, 0.0, 0.0

            if spi_res and spi_res.spi_label == "Shortage":
                if d_area > 5.0:
                    actions.append(RecommendationAction(
                        crop=cfg.name_en,
                        season=target_season,
                        action_type="PLANT_EXPANSION",
                        quantity=round(float(d_area), 1),
                        unit="hectares",
                        target_timeline="Nudge farmers within DoA planting window (next 30 days)",
                        rationale=f"Fills {round(d_area * cfg.base_yield_mt_per_ha, 1)} MT deficit via local cultivation. Protects farm-gate price above fair floor (Rs {cfg.min_fair_farmgate_price}/kg).",
                        fair_farmgate_floor_rs_kg=cfg.min_fair_farmgate_price
                    ))
                if i_q > 5.0:
                    actions.append(RecommendationAction(
                        crop=cfg.name_en,
                        season=target_season,
                        action_type="TARGETED_IMPORT",
                        quantity=round(float(i_q), 1),
                        unit="MT",
                        target_timeline="Staggered customs clearance over 45 days",
                        rationale=f"Emergency buffer import to cap retail spike without depressing farmer harvest incentives.",
                        fair_farmgate_floor_rs_kg=cfg.min_fair_farmgate_price
                    ))
            elif spi_res and spi_res.spi_label == "Glut":
                if h_buf > 5.0:
                    actions.append(RecommendationAction(
                        crop=cfg.name_en,
                        season=target_season,
                        action_type="HOLD_STORAGE_BUFFER",
                        quantity=round(float(h_buf), 1),
                        unit="MT",
                        target_timeline="Activate Dambulla/Anuradhapura dedicated warehouse storage",
                        rationale=f"Hold back bumper surplus off spot market to safeguard minimum fair farmgate floor (Rs {cfg.min_fair_farmgate_price}/kg).",
                        fair_farmgate_floor_rs_kg=cfg.min_fair_farmgate_price
                    ))
            else:
                actions.append(RecommendationAction(
                    crop=cfg.name_en,
                    season=target_season,
                    action_type="MAINTAIN_CURRENT_EXTENT",
                    quantity=0.0,
                    unit="status_quo",
                    target_timeline="Current season",
                    rationale="Market balanced within +-15% target band. No intervention required.",
                    fair_farmgate_floor_rs_kg=cfg.min_fair_farmgate_price
                ))

        return {
            "solver_status": "OPTIMAL" if res.success else "FALLBACK",
            "target_season": target_season,
            "pilot_district": self.settings.pilot_district,
            "actions": actions
        }
