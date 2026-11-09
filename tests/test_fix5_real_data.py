import pandas as pd
import numpy as np
from govisense.data.clean import load_monthly_dataset
from scripts.seed_demo import generate_counterfactual_simulation_dataset


def test_seed_demo_does_not_contaminate_monthly_master():
    master_df = load_monthly_dataset()
    demo_df = generate_counterfactual_simulation_dataset("diff_test")

    merged = pd.merge(master_df, demo_df, on=["year_month", "crop"], suffixes=("_master", "_demo"))
    assert len(merged) > 0

    # Ensure actual agricultural volumes and prices do NOT match synthetic generator
    diff_prices = ~np.isclose(merged["wholesale_price_rs_kg_master"], merged["wholesale_price_rs_kg_demo"])
    assert np.all(diff_prices), "Wholesale prices in master match synthetic generator!"

    diff_volumes = ~np.isclose(merged["harvest_volume_mt_master"], merged["harvest_volume_mt_demo"])
    assert np.all(diff_volumes), "Harvest volumes in master match synthetic generator!"


def test_master_provenance_labels():
    master_df = load_monthly_dataset()
    assert set(master_df["source_type"].unique()) == {"real", "anchor", "interpolated"}
    assert set(master_df["source"].unique()) == {"real", "anchor", "interpolated"}
    
    # 140 genuinely real empirical observations
    assert len(master_df[master_df["source_type"] == "real"]) == 140
    assert len(master_df[master_df["source_type"] == "anchor"]) == 22
    assert len(master_df[master_df["source_type"] == "interpolated"]) == 6
