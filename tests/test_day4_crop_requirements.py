"""
Tests for Day 4 Item 2: Crop Requirements Table
"""

import pytest
import pandas as pd
from govisense.data.crop_requirements import (
    load_crop_requirements,
    get_crop_requirements,
    CropRequirement,
    _validate_dataframe,
)


def test_crop_requirements_loaded():
    crops = get_crop_requirements()
    # 8-10 crops for Anuradhapura
    assert len(crops) >= 8
    expected_crops = {
        "big_onion", "chilli_green", "tomato", "brinjal",
        "bitter_gourd", "snake_gourd", "long_bean", "cowpea",
        "sesame", "mung_bean"
    }
    assert expected_crops.issubset(set(crops.keys()))


def test_crop_requirements_fields():
    crops = get_crop_requirements()
    bo = crops["big_onion"]
    assert bo.duration_months == 3
    assert bo.plant_start_month == 5
    assert bo.plant_end_month == 7
    assert bo.rainfed_ok is False
    assert 0.0 < bo.loss_pct < 1.0
    assert bo.loss_pct == pytest.approx(0.15)
    assert bo.yield_mid_mt_ha == pytest.approx(15.5)


def test_crop_requirements_season_fits():
    crops = get_crop_requirements()
    bo = crops["big_onion"]
    assert bo.season_fits(5) is True
    assert bo.season_fits(6) is True
    assert bo.season_fits(7) is True
    assert bo.season_fits(10) is False

    # Tomato plants in Sep-Nov (9-11)
    tom = crops["tomato"]
    assert tom.season_fits(10) is True
    assert tom.season_fits(5) is False


def test_crop_requirements_validation_catches_errors():
    bad_df = pd.DataFrame([{
        "crop_id": "test_crop",
        "crop_name_en": "Test",
        "crop_name_si": "ටෙස්ට්",
        "duration_months": 3,
        "plant_start_month": 15,  # Invalid month
        "plant_end_month": 5,
        "water_mm_season": 500,
        "temp_min_c": 30,
        "temp_opt_low_c": 20,    # min > opt_low error
        "temp_opt_high_c": 25,
        "temp_max_c": 35,
        "soil_ph_min": 7.0,
        "soil_ph_max": 6.0,      # min > max error
        "rainfed_ok": True,
        "yield_low_mt_ha": 10.0,
        "yield_mid_mt_ha": 5.0,  # low > mid error
        "yield_high_mt_ha": 15.0,
        "loss_pct": 1.5,         # loss > 1.0 error
        "cost_per_ha_rs": 50000,
        "source_note": "Test",
    }])
    errors = _validate_dataframe(bad_df)
    assert len(errors) >= 4

