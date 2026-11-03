"""
Tests for Day 4 Item 3: Suitability Scorer (WP2)
"""

import pytest
from govisense.models.suitability_scorer import SuitabilityScorer, score_range


def test_score_range_trapezoid():
    # opt: 20-30, min: 10, max: 40
    # Exactly inside optimal range -> 100.0
    assert score_range(25, 20, 30, 10, 40) == 100.0
    assert score_range(20, 20, 30, 10, 40) == 100.0
    assert score_range(30, 20, 30, 10, 40) == 100.0

    # Below min or above max -> 0.0
    assert score_range(5, 20, 30, 10, 40) == 0.0
    assert score_range(10, 20, 30, 10, 40) == 0.0
    assert score_range(40, 20, 30, 10, 40) == 0.0
    assert score_range(45, 20, 30, 10, 40) == 0.0

    # Linear climb between min and opt_low
    # midpoint between 10 and 20 is 15 -> 50.0
    assert score_range(15, 20, 30, 10, 40) == pytest.approx(50.0)

    # Linear fall between opt_high and max
    # midpoint between 30 and 40 is 35 -> 50.0
    assert score_range(35, 20, 30, 10, 40) == pytest.approx(50.0)


def test_hard_filter_season_mismatch():
    scorer = SuitabilityScorer()
    conditions = {
        "current_month": 1,  # January (Big Onion plants 5-7)
        "is_rainfed": False,
        "annual_rainfall_mm": 1100,
        "avg_temp_c": 28,
        "soil_ph": 6.5,
        "zone": "dry",
    }
    res = scorer.score(conditions, "big_onion")
    assert res is not None
    assert res.hard_filtered is True
    assert res.score_0_100 == 0.0
    assert "Planting window mismatch" in res.reasons[0]


def test_hard_filter_rainfed_irrigation_needed():
    scorer = SuitabilityScorer()
    conditions = {
        "current_month": 6,  # June (Big Onion season)
        "is_rainfed": True,  # Rainfed, but Big Onion requires irrigation
        "annual_rainfall_mm": 1100,
        "avg_temp_c": 28,
        "soil_ph": 6.5,
        "zone": "dry",
    }
    res = scorer.score(conditions, "big_onion")
    assert res is not None
    assert res.hard_filtered is True
    assert "requires irrigation" in res.reasons[0]


def test_soft_score_and_weights():
    scorer = SuitabilityScorer()
    assert scorer.WEIGHTS == {
        "water": 0.35,
        "temp": 0.20,
        "soil": 0.25,
        "zone": 0.20,
    }

    # Perfect conditions for big onion in June
    conditions = {
        "current_month": 6,
        "is_rainfed": False,
        "annual_rainfall_mm": 600,
        "water_mm_available": 400,  # Big onion need=350, opt is 315-525
        "avg_temp_c": 22,           # Big onion opt is 18-25
        "soil_ph": 6.5,             # Big onion opt is 5.8-7.0
        "zone": "dry",              # Compatible
    }
    res = scorer.score(conditions, "big_onion")
    assert res is not None
    assert res.hard_filtered is False
    assert res.confidence == "high"
    assert res.score_0_100 >= 95.0


def test_confidence_drops_when_soil_missing():
    scorer = SuitabilityScorer()
    conditions = {
        "current_month": 6,
        "is_rainfed": False,
        "annual_rainfall_mm": 600,
        "water_mm_available": 400,
        "avg_temp_c": 22,
        "soil_ph": None,  # Missing soil pH!
        "zone": "dry",
    }
    res = scorer.score(conditions, "big_onion")
    assert res is not None
    assert res.hard_filtered is False
    assert res.confidence == "medium"
    assert any("Soil pH: unknown" in r for r in res.reasons)


def test_rank_crops_excludes_hard_filtered():
    scorer = SuitabilityScorer()
    conditions = {
        "current_month": 10,  # October
        "is_rainfed": False,
        "annual_rainfall_mm": 1100,
        "avg_temp_c": 28,
        "soil_ph": 6.5,
        "zone": "dry",
    }
    ranked = scorer.rank_crops(conditions)
    crop_ids = [r.crop_id for r in ranked]

    # October fits Tomato and Brinjal (9-11)
    assert "tomato" in crop_ids or "brinjal" in crop_ids
    # Big onion (5-7) must be filtered out
    assert "big_onion" not in crop_ids

    # Ranked results must be sorted descending by score
    scores = [r.score_0_100 for r in ranked]
    assert scores == sorted(scores, reverse=True)

