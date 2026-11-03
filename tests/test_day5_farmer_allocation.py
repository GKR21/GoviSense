"""
Tests for Day 5 Item 5: Fair Farmer Allocation Optimizer (PuLP LP & Fallback)
"""

import pytest
from govisense.models.a4_gap_deadline import FarmerAllocationOptimizer, FarmerAllocationResult


def test_farmer_allocation_constraints():
    optimizer = FarmerAllocationOptimizer()

    farmers = [
        {"farmer_id": "F_01", "land_ha": 10.0},
        {"farmer_id": "F_02", "land_ha": 6.0},
    ]
    crops = ["big_onion", "chilli"]
    profit_scores = {
        "F_01": {"big_onion": 80, "chilli": 70},
        "F_02": {"big_onion": 60, "chilli": 90},
    }
    fit_scores = {
        "F_01": {"big_onion": 90, "chilli": 75},
        "F_02": {"big_onion": 70, "chilli": 85},
    }
    allowed = {"F_01": {"big_onion": True, "chilli": True}, "F_02": {"big_onion": True, "chilli": True}}
    # District caps
    a_rec = {"big_onion": 15.0, "chilli": 12.0}

    results = optimizer.allocate(farmers, crops, profit_scores, fit_scores, allowed, a_rec, season="Maha")

    assert len(results) == 2
    assert all(isinstance(r, FarmerAllocationResult) for r in results)

    # 1. Check max 60% of land in one crop
    for r in results:
        farmer_data = next(f for f in farmers if f["farmer_id"] == r.farmer_id)
        max_allowed_single_crop = farmer_data["land_ha"] * 0.60
        for alloc in r.top3:
            assert alloc.allocated_ha <= max_allowed_single_crop + 1e-4

        # Total allocated land cannot exceed farmer's total land
        total_farmer_ha = sum(alloc.allocated_ha for alloc in r.top3)
        assert total_farmer_ha <= farmer_data["land_ha"] + 1e-4

    # 2. Never exceed A_rec per crop
    total_onion = sum(
        alloc.allocated_ha for r in results for alloc in r.top3 if alloc.crop_id == "big_onion"
    )
    total_chilli = sum(
        alloc.allocated_ha for r in results for alloc in r.top3 if alloc.crop_id == "chilli"
    )
    assert total_onion <= a_rec["big_onion"] + 1e-4
    assert total_chilli <= a_rec["chilli"] + 1e-4


def test_farmer_allocation_seeded_hash_fairness():
    optimizer = FarmerAllocationOptimizer()
    farmers = [
        {"farmer_id": "F_Charlie", "land_ha": 4.0},
        {"farmer_id": "F_Alice", "land_ha": 5.0},
        {"farmer_id": "F_Bob", "land_ha": 6.0},
    ]
    crops = ["big_onion", "chilli"]
    profit_scores = {fid: {"big_onion": 70, "chilli": 70} for fid in ["F_Alice", "F_Bob", "F_Charlie"]}
    fit_scores = {fid: {"big_onion": 80, "chilli": 80} for fid in ["F_Alice", "F_Bob", "F_Charlie"]}
    allowed = {fid: {"big_onion": True, "chilli": True} for fid in ["F_Alice", "F_Bob", "F_Charlie"]}
    a_rec = {"big_onion": 10.0, "chilli": 10.0}

    # Run multiple times to verify deterministic, stable SHA-256 hash fairness ordering
    res1 = optimizer.allocate(farmers, crops, profit_scores, fit_scores, allowed, a_rec)
    res2 = optimizer.allocate(farmers, crops, profit_scores, fit_scores, allowed, a_rec)

    order1 = [r.farmer_id for r in res1]
    order2 = [r.farmer_id for r in res2]
    assert order1 == order2


def test_farmer_allocation_infeasibility_relaxation():
    optimizer = FarmerAllocationOptimizer()
    # A scenario with an impossibly tight change-from-last-season limit:
    # Farmer had 0 ha last season, max_change_pct = 0.0 (cannot change at all), but district wants crops
    farmers = [{"farmer_id": "F_01", "land_ha": 10.0}]
    crops = ["big_onion"]
    profit_scores = {"F_01": {"big_onion": 80}}
    fit_scores = {"F_01": {"big_onion": 80}}
    allowed = {"F_01": {"big_onion": True}}
    a_rec = {"big_onion": 5.0}

    last_season = {"F_01": {"big_onion": 0.0}}
    # max_change_pct = -0.1 (impossible bound) triggers relaxation
    results = optimizer.allocate(
        farmers, crops, profit_scores, fit_scores, allowed, a_rec,
        last_season_allocations=last_season,
        max_change_pct=-0.1,
    )
    # The solver relaxes the change-from-last-season constraint first!
    assert len(results) == 1
    assert results[0].relaxation_applied is not None
    assert "loosened" in results[0].relaxation_applied

