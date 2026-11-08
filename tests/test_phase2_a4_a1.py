"""
Acceptance Tests for Phase 2 Items 2.4, 2.5, 2.6:
  - 2.4: A4 Gap & Deadline reachability of all 4 policy options
  - 2.5: A4 Optimizer in real units (LKR) with robust scenario regret
  - 2.6: A1 Allocation Optimizer deterministic fairness (10,000 farmers test)
"""

import pytest
from datetime import date, timedelta
from govisense.models.a4_gap_deadline import (
    compute_gap_and_deadline,
    GapFillingOptimizer,
)
from govisense.models.a1_allocation import (
    FarmerAllocationOptimizer,
    DistrictCropTarget,
)
from govisense.models.a3_supply_pressure import SPIResult


def test_reachability_all_four_policy_options():
    today = date(2026, 5, 1)

    # 1. STORE (surplus supply)
    res_store = compute_gap_and_deadline(
        crop="big_onion",
        demand_mt=10000.0,
        supply_mt=15000.0,  # Surplus 5000 MT -> gap -5000 MT
        as_of_date=today,
    )
    assert res_store["policy_option"] == "STORE"
    assert res_store["gap_mt"] < 0

    # 2. IMPORT_NOW (severe shortage, shortage month starting in 8 weeks -> lead 7 weeks leaves 1 week <= 14 days)
    shortage_imminent = today + timedelta(weeks=8)
    res_import_now = compute_gap_and_deadline(
        crop="big_onion",
        demand_mt=10000.0,
        supply_mt=5000.0,  # Shortage 5000 MT
        shortage_month_first_day=shortage_imminent,
        as_of_date=today,
    )
    assert res_import_now["policy_option"] == "IMPORT_NOW"
    assert res_import_now["days_until_deadline"] <= 14

    # 3. IMPORT_LATER (shortage projected far in advance, e.g. 16 weeks ahead)
    shortage_distant = today + timedelta(weeks=16)
    res_import_later = compute_gap_and_deadline(
        crop="big_onion",
        demand_mt=10000.0,
        supply_mt=5000.0,  # Shortage 5000 MT
        shortage_month_first_day=shortage_distant,
        as_of_date=today,
    )
    assert res_import_later["policy_option"] == "IMPORT_LATER"
    assert res_import_later["days_until_deadline"] > 14

    # 4. DELAY (marginal gap within uncertainty band, e.g. demand 10000 vs supply 9950)
    res_delay = compute_gap_and_deadline(
        crop="big_onion",
        demand_mt=10000.0,
        supply_mt=9950.0,  # Gap 50 MT (< 200 MT)
        as_of_date=today,
    )
    assert res_delay["policy_option"] == "DELAY"


def test_optimizer_real_monetary_units_and_regret():
    optimizer = GapFillingOptimizer()
    spi_results = [
        SPIResult(
            crop="big_onion",
            target_date="2026-08",
            forecast_supply_mt=4000.0,
            projected_demand_mt=11000.0,
            gap_mt=-7000.0,
            spi_score=-0.63,
            spi_label="Shortage",
        ),
        SPIResult(
            crop="chilli",
            target_date="2026-08",
            forecast_supply_mt=6000.0,
            projected_demand_mt=2500.0,
            gap_mt=3500.0,
            spi_score=1.40,
            spi_label="Glut",
        ),
    ]
    res = optimizer.optimize_recommendations(spi_results, as_of_date=date(2026, 5, 1))
    assert res["solver_status"] in ["OPTIMAL", "FALLBACK"]
    # Objective cost in real LKR (must be > 100,000 LKR)
    assert res["total_objective_cost_lkr"] > 100_000.0

    # Robust regret is computed and non-negative
    for action in res["actions"]:
        assert action.robust_regret_lkr >= 0.0
        assert action.policy_option in ["IMPORT_NOW", "IMPORT_LATER", "DELAY", "STORE"]


def test_a1_allocation_10000_farmers_deterministic_fairness():
    optimizer = FarmerAllocationOptimizer()

    target_shares = {
        "big_onion": 0.60,
        "chilli": 0.40,
    }
    crops = ["big_onion", "chilli"]

    # 1. Test 10,000 simulated farmers aggregate accuracy within 1%
    n_farmers = 10_000
    total_onion_ha = 0.0
    total_chilli_ha = 0.0

    for i in range(n_farmers):
        fid = f"FARMER_{i:05d}"
        allocs = optimizer.allocate_deterministic_farmer(
            farmer_id=fid,
            season="Maha 2026",
            land_ha=1.0,
            target_shares=target_shares,
            crops=crops,
        )
        for a in allocs:
            if a.crop_id == "big_onion":
                total_onion_ha += a.allocated_ha
            elif a.crop_id == "chilli":
                total_chilli_ha += a.allocated_ha

    total_allocated = total_onion_ha + total_chilli_ha
    observed_onion_share = total_onion_ha / total_allocated
    observed_chilli_share = total_chilli_ha / total_allocated

    # Verify observed share matches target 0.60 / 0.40 within 1% (0.01)
    assert abs(observed_onion_share - 0.60) < 0.01
    assert abs(observed_chilli_share - 0.40) < 0.01

    # 2. Test identical reproducibility across repeated runs
    sample_fid = "FARMER_00042"
    run1 = optimizer.allocate_deterministic_farmer(
        farmer_id=sample_fid,
        season="Maha 2026",
        land_ha=2.5,
        target_shares=target_shares,
        crops=crops,
    )
    run2 = optimizer.allocate_deterministic_farmer(
        farmer_id=sample_fid,
        season="Maha 2026",
        land_ha=2.5,
        target_shares=target_shares,
        crops=crops,
    )

    assert len(run1) == len(run2)
    for a1, a2 in zip(run1, run2):
        assert a1.crop_id == a2.crop_id
        assert a1.allocated_ha == a2.allocated_ha
        # Max single crop fraction <= 60%
        assert a1.allocated_ha <= 2.5 * 0.60 + 1e-4

