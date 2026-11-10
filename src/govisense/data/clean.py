"""
GoviSense Data Cleaning & Feature Engineering Module
Transforms raw/processed data into model-ready features with lag structures,
seasonal indicators, and data provenance tracking.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Iterator, Optional, Tuple
from govisense.config import DEMO_DATA_DIR, PROCESSED_DATA_DIR, settings


def load_monthly_dataset(filepath: Optional[Path] = None, training_only: bool = False) -> pd.DataFrame:
    """
    Load the monthly master dataset.
    If training_only is True, filters strictly to empirical rows with source in ('real', 'anchor'),
    excluding interpolated freeze months and synthetic/demo data.
    """
    if filepath is None:
        filepath = PROCESSED_DATA_DIR / "monthly_master.csv"
        if not filepath.exists():
            filepath = DEMO_DATA_DIR / "seed_anuradhapura.csv"

    df = pd.read_csv(filepath)
    df["date"] = pd.to_datetime(df["date"])
    if training_only:
        if "source" in df.columns:
            df = df[df["source"].isin(["real", "anchor"])].copy()
        if "is_demo" in df.columns:
            df = df[~df["is_demo"]].copy()
    df = df.sort_values(by=["crop", "date"]).reset_index(drop=True)
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build lag features, rolling windows, and seasonal signals per crop.
    Adheres strictly to causal time ordering (no future leakage).
    """
    if df.empty:
        return df.copy()

    dfs = []
    for _crop_name, group in df.groupby("crop"):
        g = group.sort_values("date").copy()

        # Ensure date and month columns
        if "month" not in g.columns and "date" in g.columns:
            g["month"] = g["date"].dt.month

        # 1. Calendar / Cyclical Seasonality Features
        if "month" in g.columns:
            g["month_sin"] = np.sin(2 * np.pi * g["month"] / 12.0)
            g["month_cos"] = np.cos(2 * np.pi * g["month"] / 12.0)
            g["quarter"] = g["date"].dt.quarter if "date" in g.columns else ((g["month"] - 1) // 3 + 1)
            g["is_festival_season"] = g["month"].isin([4, 12]).astype(int)  # New Year & Christmas

        # 2. Planting-to-Harvest lag shift
        # For Big Onion & Chilli, planting happens ~3 months prior to harvest
        # 2. Planting-to-Harvest lag shift
        # For Big Onion & Chilli, planting happens ~3 months prior to harvest
        if "planted_extent_ha" in g.columns:
            g["planted_extent_lag3"] = g["planted_extent_ha"].shift(3)
            g["planted_extent_lag2"] = g["planted_extent_ha"].shift(2)
            g["planted_extent_lag1"] = g["planted_extent_ha"].shift(1)

        # 3. Weather Anomalies during growing season (rolling 3-month mean strictly shifted to forecast origin)
        if "rainfall_anomaly_mm" in g.columns:
            g["rainfall_anomaly_3m_mean"] = g["rainfall_anomaly_mm"].shift(1).rolling(window=3, min_periods=1).mean()
        if "temp_anomaly_celsius" in g.columns:
            g["temp_anomaly_3m_mean"] = g["temp_anomaly_celsius"].shift(1).rolling(window=3, min_periods=1).mean()
        # 4. Harvest Volume & Yield Lags
        if "harvest_volume_mt" in g.columns:
            g["harvest_volume_lag1"] = g["harvest_volume_mt"].shift(1)
            g["harvest_volume_lag12"] = g["harvest_volume_mt"].shift(12)  # Seasonal baseline
        if "yield_mt_per_ha" in g.columns:
            g["yield_rolling_6m"] = g["yield_mt_per_ha"].shift(1).rolling(window=6, min_periods=1).mean()

        # 5. Price Lags & Rolling Trends
        if "wholesale_price_rs_kg" in g.columns:
            g["wholesale_price_lag1"] = g["wholesale_price_rs_kg"].shift(1)
            g["wholesale_price_lag2"] = g["wholesale_price_rs_kg"].shift(2)
            g["wholesale_price_lag3"] = g["wholesale_price_rs_kg"].shift(3)
            g["wholesale_price_lag12"] = g["wholesale_price_rs_kg"].shift(12)
            g["wholesale_rolling_3m_mean"] = g["wholesale_price_rs_kg"].shift(1).rolling(window=3, min_periods=1).mean()

        if "retail_price_rs_kg" in g.columns:
            g["retail_price_lag1"] = g["retail_price_rs_kg"].shift(1)
            g["retail_price_lag2"] = g["retail_price_rs_kg"].shift(2)
            g["retail_rolling_3m_mean"] = g["retail_price_rs_kg"].shift(1).rolling(window=3, min_periods=1).mean()

        # 6. SPI Lags (AI 3 feedback into AI 2)
        if "actual_spi" in g.columns:
            g["actual_spi_lag1"] = g["actual_spi"].shift(1)
            g["actual_spi_lag2"] = g["actual_spi"].shift(2)

        # 7. Import volume lags
        # 7. Import volume lags
        if "import_volume_mt" in g.columns:
            g["import_volume_lag1"] = g["import_volume_mt"].shift(1)

        # 8. Local vs Import Price Gap (Wholesale Lag1 - Landed Import CIF & Tariff)
        if "wholesale_price_rs_kg" in g.columns:
            cif_per_kg = (
                settings.cif_colombo_rs_per_mt.get(_crop_name, 140000.0)
                + settings.import_tariff_rs_per_mt.get(_crop_name, 50000.0)
            ) / 1000.0
            g["local_vs_import_gap"] = g["wholesale_price_rs_kg"].shift(1) - cif_per_kg
        dfs.append(g)

    featured_df = pd.concat(dfs, axis=0).reset_index(drop=True)
    return featured_df


def get_walk_forward_splits(
    df: pd.DataFrame, min_train_months: int = 36, step_months: int = 6
) -> Iterator[Tuple[int, pd.Timestamp, pd.Timestamp, pd.DataFrame, pd.DataFrame]]:
    """
    Generator for Rolling-Origin (Walk-Forward) validation.
    Never shuffles time series; always trains on past and validates on future.
    """
    unique_dates = sorted(df["date"].unique())
    n_dates = len(unique_dates)

    for split_idx, split_point in enumerate(range(min_train_months, n_dates - step_months + 1, step_months)):
        train_cutoff = unique_dates[split_point - 1]
        val_cutoff = unique_dates[min(split_point + step_months - 1, n_dates - 1)]

        train_df = df[df["date"] <= train_cutoff].copy()
        val_df = df[(df["date"] > train_cutoff) & (df["date"] <= val_cutoff)].copy()

        yield split_idx, train_cutoff, val_cutoff, train_df, val_df
