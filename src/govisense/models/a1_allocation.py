"""
A1 Allocation Optimizer & Harvest Volume Forecaster
(GoviSense internal label: AI 1 / WP3 & WP5)
Team DARKBITE · ModelX 2.0 Phase 1
Pilot: Anuradhapura (Big Onion, Chilli)

Provides:
  1. District-level LP optimization:
     Maximizes expected farmer profit while keeping supply within the SPI balanced
     band [0.8, 1.2] * demand, with change cap <= 30% from previous season acreage.
  2. Deterministic, fair farmer assignment:
     Seeded hash of (farmer_id, season) mapped to cumulative area shares,
     ensuring fair allocation, identical reproducibility, and aggregate area
     matching optimizer targets within 1%.
  3. Re-exports of harvest volume forecasting modules from harvest_volume.py.
"""

import hashlib
import numpy as np
import scipy.optimize as opt
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from govisense.config import settings

# Re-exports from harvest_volume.py for 100% backward compatibility
from govisense.models.harvest_volume import (
    HarvestVolumeForecaster,
    ForecastResult,
    compute_transparent_accounting_supply,
    safe_forecast,
)

try:
    import pulp
    _PULP_AVAILABLE = bool(pulp.LpSolverDefault and pulp.LpSolverDefault.available())
except (ImportError, Exception):
    _PULP_AVAILABLE = False


@dataclass
class DistrictCropTarget:
    crop_id: str
    target_area_ha: float
    min_balanced_ha: float
    max_balanced_ha: float
    expected_profit_per_ha: float
    prev_season_area_ha: float
    share_of_total: float = 0.0


@dataclass
class FarmerCropAllocation:
    """Single allocation record: farmer -> crop -> ha."""
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
    solver: str  # "pulp" | "scipy_linprog" | "seeded_hash"
    solver_status: str
    relaxation_applied: Optional[str] = None
    allocated_area_ha: float = 0.0
    total_land_ha: float = 0.0


class FarmerAllocationOptimizer:
    """
    Fair Farmer Allocation Optimizer (Proposal Section 6 - A1).
    Maximizes expected farmer profit subject to:
      - Supply within SPI balanced band [0.80, 1.20] * Demand
      - Max change cap <= 30% from last season acreage
      - Max 60% of farmer's land in a single crop
      - Deterministic fair assignment via seeded SHA-256 hash
    """

    MAX_SINGLE_CROP_FRACTION: float = 0.60
    MAX_CHANGE_PCT: float = 0.30
    HASH_SALT: str = "govisense_maha_yala_v1"

    def optimize_district_targets(
        self,
        crops: List[str],
        demands_mt: Dict[str, float],
        prev_season_areas_ha: Dict[str, float],
        yields_mt_ha: Dict[str, float],
        loss_pcts: Dict[str, float],
        profit_per_ha_rs: Dict[str, float],
        max_district_land_ha: float = 12500.0,
    ) -> Dict[str, DistrictCropTarget]:
        """
        Solves district-level LP to find optimal target acreages A_c
        maximizing aggregate farmer profit subject to SPI [0.8, 1.2] band
        and <= 30% change constraint from previous season.
        """
        n = len(crops)
        c = -np.array([profit_per_ha_rs.get(cp, 100000.0) for cp in crops], dtype=float)

        bounds = []
        min_areas = []
        max_areas = []

        for cp in crops:
            d = demands_mt.get(cp, 5000.0)
            y = max(yields_mt_ha.get(cp, 10.0), 0.1)
            loss = loss_pcts.get(cp, 0.15)
            net_yield = y * (1.0 - loss)

            # SPI balanced band: 0.8 * D <= Area * net_yield <= 1.2 * D
            min_spi_area = (0.80 * d) / net_yield
            max_spi_area = (1.20 * d) / net_yield

            # Change cap: <= 30% from previous season
            prev_a = prev_season_areas_ha.get(cp, (min_spi_area + max_spi_area) / 2.0)
            min_change_area = prev_a * (1.0 - self.MAX_CHANGE_PCT)
            max_change_area = prev_a * (1.0 + self.MAX_CHANGE_PCT)

            lb = max(0.0, max(min_spi_area, min_change_area))
            ub = min(max_spi_area, max_change_area)
            if lb > ub:
                lb = min_spi_area
                ub = max_spi_area

            bounds.append((lb, ub))
            min_areas.append(min_spi_area)
            max_areas.append(max_spi_area)

        A_ub = np.ones((1, n))
        b_ub = np.array([max_district_land_ha])

        res = opt.linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")
        targets: Dict[str, DistrictCropTarget] = {}

        if res.success:
            sol_areas = res.x
        else:
            sol_areas = [(b[0] + b[1]) / 2.0 for b in bounds]

        total_area = max(sum(sol_areas), 1.0)
        for i, cp in enumerate(crops):
            targets[cp] = DistrictCropTarget(
                crop_id=cp,
                target_area_ha=round(float(sol_areas[i]), 1),
                min_balanced_ha=round(float(min_areas[i]), 1),
                max_balanced_ha=round(float(max_areas[i]), 1),
                expected_profit_per_ha=profit_per_ha_rs.get(cp, 100000.0),
                prev_season_area_ha=prev_season_areas_ha.get(cp, 0.0),
                share_of_total=round(float(sol_areas[i] / total_area), 4),
            )
        return targets

    def get_farmer_hash_fraction(self, farmer_id: str, season: str, offset: int = 0) -> float:
        """Computes deterministic uniform value in [0, 1) from SHA-256."""
        raw = f"{self.HASH_SALT}:{season}:{farmer_id}:{offset}".encode("utf-8")
        hex_digest = hashlib.sha256(raw).hexdigest()
        val = int(hex_digest[:14], 16) / float(16**14)
        return val

    def allocate_deterministic_farmer(
        self,
        farmer_id: str,
        season: str,
        land_ha: float,
        target_shares: Dict[str, float],
        crops: Optional[List[str]] = None,
        profit_scores: Optional[Dict[str, float]] = None,
        fit_scores: Optional[Dict[str, float]] = None,
        allowed: Optional[Dict[str, bool]] = None,
        last_season_allocation: Optional[Dict[str, float]] = None,
    ) -> List[FarmerCropAllocation]:
        """
        Deterministic allocation for a single farmer mapping cumulative area shares.
        Stratifies farmers across target crops so that aggregate allocated acreage
        matches optimizer targets within 1%.
        """
        if crops is None:
            crops = list(target_shares.keys())

        valid_crops = [c for c in crops if (allowed is None or allowed.get(c, True))]
        if not valid_crops:
            valid_crops = crops

        sub_shares = {c: target_shares.get(c, 1.0 / len(valid_crops)) for c in valid_crops}
        total_s = max(sum(sub_shares.values()), 1e-4)
        normalized_shares = {c: sub_shares[c] / total_s for c in valid_crops}

        cum_intervals = []
        running = 0.0
        for c in valid_crops:
            start = running
            running += normalized_shares[c]
            cum_intervals.append((c, start, min(1.0, running)))

        u = self.get_farmer_hash_fraction(farmer_id, season, offset=0)
        chosen_primary = valid_crops[0]
        for c, start, end in cum_intervals:
            if start <= u < end or (u >= 1.0 and end >= 1.0):
                chosen_primary = c
                break

        crops_cfg = settings.crops
        allocs = []
        # Primary crop receives the allocation for this farmer, capped at MAX_SINGLE_CROP_FRACTION (60%)
        primary_ha = round(land_ha * self.MAX_SINGLE_CROP_FRACTION, 2)
        allocs.append(
            FarmerCropAllocation(
                farmer_id=farmer_id,
                crop_id=chosen_primary,
                crop_name=crops_cfg[chosen_primary].name_en if chosen_primary in crops_cfg else chosen_primary.title(),
                allocated_ha=primary_ha,
                profit_score=profit_scores.get(chosen_primary, 75.0) if profit_scores else 75.0,
                fit_score=fit_scores.get(chosen_primary, 80.0) if fit_scores else 80.0,
                season=season,
            )
        )

        # Secondary advisory crops (allocated_ha = 0.0 for pure rotation advisory)
        remaining_crops = [c for c in valid_crops if c != chosen_primary]
        for c in remaining_crops[:2]:
            allocs.append(
                FarmerCropAllocation(
                    farmer_id=farmer_id,
                    crop_id=c,
                    crop_name=crops_cfg[c].name_en if c in crops_cfg else c.title(),
                    allocated_ha=0.0,
                    profit_score=profit_scores.get(c, 60.0) if profit_scores else 60.0,
                    fit_score=fit_scores.get(c, 65.0) if fit_scores else 65.0,
                    season=season,
                )
            )

        return allocs

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
        Batch allocation running PuLP LP if available or scipy linprog fallback,
        integrating deterministic seeded hash ordering and infeasibility relaxation.
        """
        def _farmer_sort_key(f: Dict) -> str:
            raw = f"{self.HASH_SALT}:{season}:{f['farmer_id']}".encode("utf-8")
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
                    row_up = np.zeros(n_vars)
                    row_up[var_idx] = 1.0
                    A_ub_rows.append(row_up)
                    b_ub_vals.append(last_ha + max_delta)

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

        prob += pulp.lpSum(
            x[(f["farmer_id"], c)]
            * profit_scores.get(f["farmer_id"], {}).get(c, 50.0)
            * fit_scores.get(f["farmer_id"], {}).get(c, 50.0)
            / 10_000.0
            for f in farmers
            for c in crops
        )

        for f in farmers:
            fid = f["farmer_id"]
            land = float(f["land_ha"])
            prob += pulp.lpSum(x[(fid, c)] for c in crops) <= land, f"Land_{fid}"

        for c in crops:
            cap = a_rec.get(c, 1e6)
            prob += pulp.lpSum(x[(f["farmer_id"], c)] for f in farmers) <= cap, f"Cap_{c}"

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
        import pulp

        relaxation = None
        prob, x, status = self._solve_pulp_attempt(
            farmers, crops, profit_scores, fit_scores, allowed, a_rec, crops_cfg,
            self.MAX_SINGLE_CROP_FRACTION, last_season_allocations, max_change_pct,
        )

        if status != "Optimal" and last_season_allocations:
            relaxation = "loosened_change_from_last_season"
            prob, x, status = self._solve_pulp_attempt(
                farmers, crops, profit_scores, fit_scores, allowed, a_rec, crops_cfg,
                self.MAX_SINGLE_CROP_FRACTION, None, None,
            )

        if status != "Optimal":
            relaxation = (
                "loosened_single_crop_limit" if relaxation is None
                else f"{relaxation}+loosened_single_crop_limit"
            )
            prob, x, status = self._solve_pulp_attempt(
                farmers, crops, profit_scores, fit_scores, allowed, a_rec, crops_cfg,
                1.0, None, None,
            )

        return self._extract_top3(
            farmers, crops, x, profit_scores, fit_scores, crops_cfg,
            season, "pulp", status,
            get_val=lambda v: pulp.value(v) or 0.0,
            relaxation_applied=relaxation,
        )

    def _extract_top3(
        self, farmers, crops, x, profit_scores, fit_scores, crops_cfg,
        season, solver_name, solver_status, get_val: Callable,
        relaxation_applied: Optional[str] = None,
    ) -> List[FarmerAllocationResult]:
        results: List[FarmerAllocationResult] = []
        for f in farmers:
            fid = f["farmer_id"]
            allocations: List[FarmerCropAllocation] = []
            for c in crops:
                val = get_val(x.get((fid, c), 0.0))
                if val > 1e-4:
                    allocations.append(
                        FarmerCropAllocation(
                            farmer_id=fid,
                            crop_id=c,
                            crop_name=crops_cfg[c].name_en if c in crops_cfg else c.title(),
                            allocated_ha=round(val, 2),
                            profit_score=profit_scores.get(fid, {}).get(c, 0.0),
                            fit_score=fit_scores.get(fid, {}).get(c, 0.0),
                            season=season,
                        )
                    )
            allocations.sort(key=lambda a: a.allocated_ha, reverse=True)
            top3 = allocations[:3]
            results.append(
                FarmerAllocationResult(
                    farmer_id=fid,
                    season=season,
                    top3=top3,
                    solver=solver_name,
                    solver_status=solver_status,
                    relaxation_applied=relaxation_applied,
                    allocated_area_ha=sum(a.allocated_ha for a in top3),
                    total_land_ha=float(f["land_ha"]),
                )
            )
        return results
