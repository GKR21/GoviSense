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

Also provides FarmerAllocationOptimizer (Item 5):
Allocates crops to individual farmers using PuLP LP (or scipy linprog fallback).
"""

import hashlib
import numpy as np
import scipy.optimize as opt
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from govisense.config import settings, CropConfig
from govisense.models.a3_supply_pressure import SPIResult

try:
    import pulp
    _PULP_AVAILABLE = bool(pulp.LpSolverDefault and pulp.LpSolverDefault.available())
except (ImportError, Exception):
    _PULP_AVAILABLE = False


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

            # Scenario gap calculation (best case, mid case, worst case)
            mid_gap = gap
            if spi_res and hasattr(spi_res, "scenarios") and spi_res.scenarios:
                worst_gap = spi_res.scenarios["low"].gap_mt
                best_gap = spi_res.scenarios["high"].gap_mt
            else:
                worst_gap = mid_gap - 1200.0 if mid_gap < 0 else mid_gap - 800.0
                best_gap = mid_gap + 1500.0 if mid_gap > 0 else mid_gap + 1000.0

            # Import lead time: 6 to 8 weeks (45 to 56 days)
            import_lead_weeks = 7
            lead_days = import_lead_weeks * 7  # 49 days
            decision_deadline_desc = f"{lead_days} days before projected shortage (T-{lead_days}d)"
            days_remaining = max(14, lead_days - 20)

            # Determine policy option: IMPORT_NOW, IMPORT_LATER, DELAY, STORE
            if spi_res and spi_res.spi_label == "Glut":
                policy_opt = "STORE"
            elif spi_res and spi_res.spi_label == "Shortage":
                policy_opt = "IMPORT_NOW" if days_remaining <= 30 else "IMPORT_LATER"
            else:
                policy_opt = "DELAY"

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
                        fair_farmgate_floor_rs_kg=cfg.min_fair_farmgate_price,
                        best_case_gap_mt=round(float(best_gap), 1),
                        mid_case_gap_mt=round(float(mid_gap), 1),
                        worst_case_gap_mt=round(float(worst_gap), 1),
                        decision_deadline=decision_deadline_desc,
                        days_until_deadline=days_remaining,
                        import_lead_time_weeks=import_lead_weeks,
                        policy_option=policy_opt,
                    ))
                if i_q > 5.0:
                    actions.append(RecommendationAction(
                        crop=cfg.name_en,
                        season=target_season,
                        action_type="TARGETED_IMPORT",
                        quantity=round(float(i_q), 1),
                        unit="MT",
                        target_timeline=f"Execute import procurement {import_lead_weeks} weeks ahead of deficit",
                        rationale=f"Emergency buffer import to cap retail spike without depressing farmer harvest incentives. Best-case gap: {best_gap:.1f} MT, Worst-case gap: {worst_gap:.1f} MT.",
                        fair_farmgate_floor_rs_kg=cfg.min_fair_farmgate_price,
                        best_case_gap_mt=round(float(best_gap), 1),
                        mid_case_gap_mt=round(float(mid_gap), 1),
                        worst_case_gap_mt=round(float(worst_gap), 1),
                        decision_deadline=decision_deadline_desc,
                        days_until_deadline=days_remaining,
                        import_lead_time_weeks=import_lead_weeks,
                        policy_option=policy_opt,
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
                        rationale=f"Hold back bumper surplus off spot market to safeguard minimum fair farmgate floor (Rs {cfg.min_fair_farmgate_price}/kg). Best-case surplus: {best_gap:.1f} MT, Worst-case surplus: {worst_gap:.1f} MT.",
                        fair_farmgate_floor_rs_kg=cfg.min_fair_farmgate_price,
                        best_case_gap_mt=round(float(best_gap), 1),
                        mid_case_gap_mt=round(float(mid_gap), 1),
                        worst_case_gap_mt=round(float(worst_gap), 1),
                        decision_deadline="Immediate - within peak harvest window",
                        days_until_deadline=7,
                        import_lead_time_weeks=import_lead_weeks,
                        policy_option="STORE",
                    ))
            else:
                actions.append(RecommendationAction(
                    crop=cfg.name_en,
                    season=target_season,
                    action_type="MAINTAIN_CURRENT_EXTENT",
                    quantity=0.0,
                    unit="status_quo",
                    target_timeline="Current season",
                    rationale=f"Market balanced within target band (Gap: {mid_gap:.1f} MT). Option: DELAY trade intervention.",
                    fair_farmgate_floor_rs_kg=cfg.min_fair_farmgate_price,
                    best_case_gap_mt=round(float(best_gap), 1),
                    mid_case_gap_mt=round(float(mid_gap), 1),
                    worst_case_gap_mt=round(float(worst_gap), 1),
                    decision_deadline="Continuous monitoring",
                    days_until_deadline=60,
                    import_lead_time_weeks=import_lead_weeks,
                    policy_option="DELAY",
                ))

        return {
            "solver_status": "OPTIMAL" if res.success else "FALLBACK",
            "target_season": target_season,
            "pilot_district": self.settings.pilot_district,
            "actions": actions
        }


# ---------------------------------------------------------------------------
# Item 5 – Fair Farmer Allocation Optimizer (PuLP / scipy fallback)
# ---------------------------------------------------------------------------


@dataclass
class FarmerCropAllocation:
    """Single allocation record: farmer → crop → ha."""

    farmer_id: str
    crop_id: str
    crop_name: str
    allocated_ha: float
    profit_score: float
    fit_score: float
    season: str


@dataclass
class FarmerAllocationResult:
    """Output of FarmerAllocationOptimizer.allocate()."""

    farmer_id: str
    season: str
    top3: List[FarmerCropAllocation]
    solver: str  # "pulp" | "scipy_linprog"
    solver_status: str
    relaxation_applied: Optional[str] = None


class FarmerAllocationOptimizer:
    """
    Allocates crops to individual farmers using fair LP optimization.

    Uses PuLP if available, otherwise falls back to scipy.optimize.linprog.

    Variables
    ---------
    x[f][c] = hectares allocated to farmer *f* for crop *c*.

    Objective (maximise)
    --------------------
    sum_{f,c}  x[f][c] * profit_score[f][c] * fit[f][c]

    Constraints
    -----------
    1. sum_c  x[f][c]  <= land[f]               (per-farmer land budget)
    2. x[f][c]         <= 0.60 * land[f]         (max 60 % in one crop)
    3. x[f][c]         = 0  if allowed[f][c]=False (hard filter from suitability)
    4. sum_f  x[f][c]  <= A_rec[c]               (never exceed district target area)
    5. Optional: |x[f][c] - last_season[f][c]| <= max_change_pct * land[f]

    Infeasibility Relaxation
    ------------------------
    If the formulation is infeasible, the solver relaxes constraints in order:
    1. Loosen change-from-last-season limit first.
    2. If still infeasible, loosen single-crop limit (from 60% up to 100%).

    Farmer ordering
    ---------------
    Deterministic pseudonymous order: seeded hash of farmer ID so the ranking
    is stable and fair without leaking personal identifiers.

    Returns top-3 crops per farmer.
    """

    MAX_SINGLE_CROP_FRACTION: float = 0.60

    def allocate(
        self,
        farmers: List[Dict[str, Any]],
        crops: List[str],
        profit_scores: Dict[str, Dict[str, float]],
        fit_scores: Dict[str, Dict[str, float]],
        allowed: Dict[str, Dict[str, bool]],
        a_rec: Dict[str, float],
        season: str = "Upcoming",
        last_season_allocations: Optional[Dict[str, Dict[str, float]]] = None,
        max_change_pct: Optional[float] = None,
    ) -> List[FarmerAllocationResult]:
        """
        Run LP allocation and return top-3 per farmer.
        """
        # Deterministic pseudonymous ordering via SHA-256
        def _farmer_sort_key(f: Dict) -> str:
            raw = str(f["farmer_id"]).encode()
            return hashlib.sha256(raw).hexdigest()

        sorted_farmers = sorted(farmers, key=_farmer_sort_key)
        crops_cfg = settings.crops

        if _PULP_AVAILABLE:
            return self._allocate_pulp(
                sorted_farmers, crops, profit_scores, fit_scores, allowed,
                a_rec, season, crops_cfg,
                last_season_allocations=last_season_allocations,
                max_change_pct=max_change_pct,
            )
        else:
            return self._allocate_scipy(
                sorted_farmers, crops, profit_scores, fit_scores, allowed,
                a_rec, season, crops_cfg,
                last_season_allocations=last_season_allocations,
                max_change_pct=max_change_pct,
            )

    # ------------------------------------------------------------------
    # PuLP implementation
    # ------------------------------------------------------------------

    def _solve_pulp_attempt(
        self,
        farmers, crops, profit_scores, fit_scores, allowed, a_rec, crops_cfg,
        single_crop_fraction: float,
        last_season_allocations: Optional[Dict[str, Dict[str, float]]],
        max_change_pct: Optional[float],
    ):
        import pulp

        prob = pulp.LpProblem("FarmerCropAllocation", pulp.LpMaximize)

        x: Dict[Tuple, pulp.LpVariable] = {}
        for f in farmers:
            fid = f["farmer_id"]
            land = float(f["land_ha"])
            for c in crops:
                is_allowed = allowed.get(fid, {}).get(c, True)
                ub = min(land * single_crop_fraction, a_rec.get(c, land)) if is_allowed else 0.0
                x[(fid, c)] = pulp.LpVariable(
                    f"x_{fid}_{c}",
                    lowBound=0.0,
                    upBound=ub,
                    cat="Continuous",
                )

        # Objective: maximise weighted profit × fit
        prob += pulp.lpSum(
            x[(f["farmer_id"], c)]
            * profit_scores.get(f["farmer_id"], {}).get(c, 50.0)
            * fit_scores.get(f["farmer_id"], {}).get(c, 50.0)
            / 10_000.0
            for f in farmers
            for c in crops
        )

        # Constraint 1: per-farmer land budget
        for f in farmers:
            fid = f["farmer_id"]
            land = float(f["land_ha"])
            prob += pulp.lpSum(x[(fid, c)] for c in crops) <= land, f"Land_{fid}"

        # Constraint 2: district target area cap per crop (never exceed A_rec)
        for c in crops:
            cap = a_rec.get(c, 1e6)
            prob += pulp.lpSum(x[(f["farmer_id"], c)] for f in farmers) <= cap, f"Cap_{c}"

        # Constraint 3 (optional): change from last season limit
        if last_season_allocations and max_change_pct is not None:
            for f in farmers:
                fid = f["farmer_id"]
                land = float(f["land_ha"])
                max_delta = max_change_pct * land
                for c in crops:
                    last_ha = last_season_allocations.get(fid, {}).get(c, 0.0)
                    prob += x[(fid, c)] - last_ha <= max_delta, f"DeltaUp_{fid}_{c}"
                    prob += last_ha - x[(fid, c)] <= max_delta, f"DeltaDn_{fid}_{c}"

        prob.solve(pulp.PULP_CBC_CMD(msg=0))
        status_str = pulp.LpStatus[prob.status]
        return prob, x, status_str

    def _allocate_pulp(
        self,
        farmers, crops, profit_scores, fit_scores, allowed, a_rec, season, crops_cfg,
        last_season_allocations: Optional[Dict[str, Dict[str, float]]] = None,
        max_change_pct: Optional[float] = None,
    ) -> List[FarmerAllocationResult]:
        """PuLP LP solver implementation with automatic relaxation for infeasibility."""
        relaxation = None

        # Attempt 1: Full model
        prob, x, status = self._solve_pulp_attempt(
            farmers, crops, profit_scores, fit_scores, allowed, a_rec, crops_cfg,
            single_crop_fraction=self.MAX_SINGLE_CROP_FRACTION,
            last_season_allocations=last_season_allocations,
            max_change_pct=max_change_pct,
        )

        # Infeasibility relaxation 1: loosen / drop change-from-last-season limit first
        if status != "Optimal" and last_season_allocations is not None:
            relaxation = "loosened_change_from_last_season"
            prob, x, status = self._solve_pulp_attempt(
                farmers, crops, profit_scores, fit_scores, allowed, a_rec, crops_cfg,
                single_crop_fraction=self.MAX_SINGLE_CROP_FRACTION,
                last_season_allocations=None,
                max_change_pct=None,
            )

        # Infeasibility relaxation 2: loosen single-crop fraction up to 1.0
        if status != "Optimal":
            relaxation = (
                "loosened_single_crop_limit" if relaxation is None
                else f"{relaxation}+loosened_single_crop_limit"
            )
            prob, x, status = self._solve_pulp_attempt(
                farmers, crops, profit_scores, fit_scores, allowed, a_rec, crops_cfg,
                single_crop_fraction=1.0,
                last_season_allocations=None,
                max_change_pct=None,
            )

        import pulp
        return self._extract_top3(
            farmers, crops, x, profit_scores, fit_scores, crops_cfg,
            season, "pulp", status,
            get_val=lambda v: pulp.value(v) or 0.0,
            relaxation_applied=relaxation,
        )

    # ------------------------------------------------------------------
    # scipy linprog fallback implementation
    # ------------------------------------------------------------------

    def _solve_scipy_attempt(
        self,
        farmers, crops, profit_scores, fit_scores, allowed, a_rec,
        single_crop_fraction: float,
        last_season_allocations: Optional[Dict[str, Dict[str, float]]],
        max_change_pct: Optional[float],
    ):
        n_farmers = len(farmers)
        n_crops = len(crops)
        n_vars = n_farmers * n_crops

        farmer_ids = [f["farmer_id"] for f in farmers]
        idx = {(fid, c): i * n_crops + j for i, fid in enumerate(farmer_ids) for j, c in enumerate(crops)}

        # Objective (minimise -profit*fit)
        c_vec = np.zeros(n_vars)
        for i, f in enumerate(farmers):
            fid = f["farmer_id"]
            for j, c in enumerate(crops):
                p = profit_scores.get(fid, {}).get(c, 50.0)
                s = fit_scores.get(fid, {}).get(c, 50.0)
                c_vec[idx[(fid, c)]] = -(p * s) / 10_000.0

        # Bounds: 0 <= x[f][c] <= min(land * single_crop_fraction, a_rec)
        bounds = []
        for i, f in enumerate(farmers):
            fid = f["farmer_id"]
            land = float(f["land_ha"])
            for j, c in enumerate(crops):
                is_allowed = allowed.get(fid, {}).get(c, True)
                ub = min(land * single_crop_fraction, a_rec.get(c, land)) if is_allowed else 0.0
                bounds.append((0.0, ub))

        # Inequality constraints (A_ub x <= b_ub)
        A_ub_rows, b_ub_vals = [], []

        # Constraint 1: Per-farmer land budget
        for i, f in enumerate(farmers):
            fid = f["farmer_id"]
            land = float(f["land_ha"])
            row = np.zeros(n_vars)
            for j, c in enumerate(crops):
                row[idx[(fid, c)]] = 1.0
            A_ub_rows.append(row)
            b_ub_vals.append(land)

        # Constraint 2: District cap per crop (never exceed A_rec)
        for j, c in enumerate(crops):
            cap = a_rec.get(c, 1e6)
            row = np.zeros(n_vars)
            for i, f in enumerate(farmers):
                row[idx[(f["farmer_id"], c)]] = 1.0
            A_ub_rows.append(row)
            b_ub_vals.append(cap)

        # Constraint 3: Change from last season limit
        if last_season_allocations and max_change_pct is not None:
            for i, f in enumerate(farmers):
                fid = f["farmer_id"]
                land = float(f["land_ha"])
                max_delta = max_change_pct * land
                for j, c in enumerate(crops):
                    last_ha = last_season_allocations.get(fid, {}).get(c, 0.0)
                    var_idx = idx[(fid, c)]
                    # x - last_ha <= max_delta  =>  x <= last_ha + max_delta
                    row_up = np.zeros(n_vars)
                    row_up[var_idx] = 1.0
                    A_ub_rows.append(row_up)
                    b_ub_vals.append(last_ha + max_delta)

                    # last_ha - x <= max_delta  =>  -x <= -last_ha + max_delta
                    row_dn = np.zeros(n_vars)
                    row_dn[var_idx] = -1.0
                    A_ub_rows.append(row_dn)
                    b_ub_vals.append(max_delta - last_ha)

        res = opt.linprog(
            c_vec,
            A_ub=np.array(A_ub_rows) if A_ub_rows else None,
            b_ub=np.array(b_ub_vals) if b_ub_vals else None,
            bounds=bounds,
            method="highs",
        )
        return res, idx

    def _allocate_scipy(
        self,
        farmers, crops, profit_scores, fit_scores, allowed, a_rec, season, crops_cfg,
        last_season_allocations: Optional[Dict[str, Dict[str, float]]] = None,
        max_change_pct: Optional[float] = None,
    ) -> List[FarmerAllocationResult]:
        """scipy.optimize.linprog implementation with automatic relaxation for infeasibility."""
        relaxation = None

        # Attempt 1: Full model
        res, idx = self._solve_scipy_attempt(
            farmers, crops, profit_scores, fit_scores, allowed, a_rec,
            single_crop_fraction=self.MAX_SINGLE_CROP_FRACTION,
            last_season_allocations=last_season_allocations,
            max_change_pct=max_change_pct,
        )

        # Infeasibility relaxation 1: loosen / drop change-from-last-season limit first
        if not res.success and last_season_allocations is not None:
            relaxation = "loosened_change_from_last_season"
            res, idx = self._solve_scipy_attempt(
                farmers, crops, profit_scores, fit_scores, allowed, a_rec,
                single_crop_fraction=self.MAX_SINGLE_CROP_FRACTION,
                last_season_allocations=None,
                max_change_pct=None,
            )

        # Infeasibility relaxation 2: loosen single-crop fraction up to 1.0
        if not res.success:
            relaxation = (
                "loosened_single_crop_limit" if relaxation is None
                else f"{relaxation}+loosened_single_crop_limit"
            )
            res, idx = self._solve_scipy_attempt(
                farmers, crops, profit_scores, fit_scores, allowed, a_rec,
                single_crop_fraction=1.0,
                last_season_allocations=None,
                max_change_pct=None,
            )

        # Map solution back to named variables
        x_dict = {}
        for key, i in idx.items():
            x_dict[key] = res.x[i] if res.success else 0.0

        solver_status = "OPTIMAL" if res.success else "FALLBACK"

        return self._extract_top3(
            farmers, crops, x_dict, profit_scores, fit_scores, crops_cfg,
            season, "scipy_linprog", solver_status,
            get_val=lambda v: float(v),
            relaxation_applied=relaxation,
        )

    # ------------------------------------------------------------------
    # Shared top-3 extractor
    # ------------------------------------------------------------------

    def _extract_top3(
        self, farmers, crops, x, profit_scores, fit_scores, crops_cfg,
        season, solver_name, solver_status, get_val,
        relaxation_applied: Optional[str] = None,
    ) -> List[FarmerAllocationResult]:
        """Extract and return top-3 allocations per farmer."""
        results: List[FarmerAllocationResult] = []
        for f in farmers:
            fid = f["farmer_id"]
            allocations: List[FarmerCropAllocation] = []
            for c in crops:
                ha = get_val(x[(fid, c)])
                if ha > 0.01:
                    cfg = crops_cfg.get(c)
                    crop_name = cfg.name_en if cfg else c
                    allocations.append(FarmerCropAllocation(
                        farmer_id=fid,
                        crop_id=c,
                        crop_name=crop_name,
                        allocated_ha=round(ha, 2),
                        profit_score=profit_scores.get(fid, {}).get(c, 50.0),
                        fit_score=fit_scores.get(fid, {}).get(c, 50.0),
                        season=season,
                    ))
            # Sort by (profit_score × fit_score) descending and take top 3
            allocations.sort(key=lambda a: a.profit_score * a.fit_score, reverse=True)
            results.append(FarmerAllocationResult(
                farmer_id=fid,
                season=season,
                top3=allocations[:3],
                solver=solver_name,
                solver_status=solver_status,
                relaxation_applied=relaxation_applied,
            ))
        return results


# ---------------------------------------------------------------------------
# Smoke test for FarmerAllocationOptimizer
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    optimizer = FarmerAllocationOptimizer()

    test_farmers = [
        {"farmer_id": "F001", "land_ha": 5.0},
        {"farmer_id": "F002", "land_ha": 3.0},
        {"farmer_id": "F003", "land_ha": 8.0},
    ]
    test_crops = ["big_onion", "chilli"]
    profit_scores = {
        "F001": {"big_onion": 70, "chilli": 60},
        "F002": {"big_onion": 50, "chilli": 80},
        "F003": {"big_onion": 65, "chilli": 55},
    }
    fit_scores = {
        "F001": {"big_onion": 85, "chilli": 75},
        "F002": {"big_onion": 60, "chilli": 90},
        "F003": {"big_onion": 80, "chilli": 70},
    }
    allowed = {fid: {c: True for c in test_crops} for fid in ["F001", "F002", "F003"]}
    a_rec_vals = {"big_onion": 10.0, "chilli": 8.0}

    results = optimizer.allocate(
        test_farmers, test_crops, profit_scores, fit_scores, allowed, a_rec_vals, season="Maha 2025/2026"
    )
    print(f"Solver used: {results[0].solver} | Status: {results[0].solver_status}")
    for r in results:
        print(f"\nFarmer {r.farmer_id} top-3:")
        for alloc in r.top3:
            print(f"  {alloc.crop_name}: {alloc.allocated_ha} ha (profit={alloc.profit_score}, fit={alloc.fit_score})")
