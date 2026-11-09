import pandas as pd
import numpy as np
from pathlib import Path

def build_monthly_cbsl_table():
    raw_path = Path("data/raw/cbsl/cbsl_daily_prices_historical.csv")
    out_path = Path("data/processed/monthly_prices_cbsl.csv")
    
    # Read raw file with comment="#"
    df_raw = pd.read_csv(raw_path, comment="#")
    df_raw.columns = [c.strip() for c in df_raw.columns]
    date_col = df_raw.columns[0]
    
    df_raw[date_col] = pd.to_datetime(df_raw[date_col], errors="coerce")
    df_raw = df_raw.dropna(subset=[date_col]).sort_values(by=date_col).set_index(date_col)
    
    # Mapping of canonical clean column names to raw CBSL column names
    price_col_map = {
        # Big Onion (Imported)
        "big_onion_imp_wholesale_pettah": "Big onion (imp) (wholesale, pettah) (Rs/kg)",
        "big_onion_imp_wholesale_dambulla": "Big onion (imp) (wholesale, dambulla) (Rs/kg)",
        "big_onion_imp_retail_pettah": "Big onion (imp) (retail, pettah) (Rs/kg)",
        "big_onion_imp_retail_dambulla": "Big onion (imp) (retail, dambulla) (Rs/kg)",
        # Big Onion (Local)
        "big_onion_loc_wholesale_pettah": "Big onion (local) (wholesale, pettah) (Rs/kg)",
        "big_onion_loc_wholesale_dambulla": "Big onion (local) (wholesale, dambulla) (Rs/kg)",
        "big_onion_loc_retail_pettah": "Big onion (local) (retail, pettah) (Rs/kg)",
        "big_onion_loc_retail_dambulla": "Big onion (local) (retail, dambulla) (Rs/kg)",
        # Green Chilli
        "green_chilli_wholesale_pettah": "Green chilli (wholesale, pettah) (Rs/kg)",
        "green_chilli_wholesale_dambulla": "Green chilli (wholesale, dambulla) (Rs/kg)",
        "green_chilli_retail_pettah": "Green chilli (retail, pettah) (Rs/kg)",
        "green_chilli_retail_dambulla": "Green chilli (retail, dambulla) (Rs/kg)",
        # Dried Chilli (Imported)
        "dried_chilli_imp_wholesale_pettah": "Dried chilli (imp) (wholesale, pettah) (Rs/kg)",
        "dried_chilli_imp_wholesale_dambulla": "Dried chilli (imp) (wholesale, dambulla) (Rs/kg)",
        "dried_chilli_imp_retail_pettah": "Dried chilli (imp) (retail, pettah) (Rs/kg)",
        "dried_chilli_imp_retail_dambulla": "Dried chilli (imp) (retail, dambulla) (Rs/kg)",
        # Red Onion (Local)
        "red_onion_loc_wholesale_pettah": "Red onion (local) (wholesale, pettah) (Rs/kg)",
        "red_onion_loc_wholesale_dambulla": "Red onion (local) (wholesale, dambulla) (Rs/kg)",
        "red_onion_loc_retail_pettah": "Red onion (local) (retail, pettah) (Rs/kg)",
        "red_onion_loc_retail_dambulla": "Red onion (local) (retail, dambulla) (Rs/kg)",
        # Red Onion (Imported)
        "red_onion_imp_wholesale_pettah": "Red onion (imp) (wholesale, pettah) (Rs/kg)",
        "red_onion_imp_retail_pettah": "Red onion (imp) (retail, pettah) (Rs/kg)",
        # Potato (Local & Imported)
        "potato_loc_wholesale_pettah": "Potato (local) (wholesale, pettah) (Rs/kg)" if "Potato (local) (wholesale, pettah) (Rs/kg)" in df_raw.columns else None,
        "potato_loc_wholesale_dambulla": "Potato (local) (wholesale, dambulla) (Rs/kg)" if "Potato (local) (wholesale, dambulla) (Rs/kg)" in df_raw.columns else None,
        "potato_imp_wholesale_pettah": "Potato (imp) (wholesale, pettah) (Rs/kg)" if "Potato (imp) (wholesale, pettah) (Rs/kg)" in df_raw.columns else None,
    }
    
    # Clean available mappings
    valid_map = {clean_name: raw_name for clean_name, raw_name in price_col_map.items() if raw_name and raw_name in df_raw.columns}
    
    # 1. Outlier detection on daily values (> 5 MAD from 30-day rolling median)
    outlier_records = []
    daily_numeric = pd.DataFrame(index=df_raw.index)
    
    for clean_name, raw_name in valid_map.items():
        s = pd.to_numeric(df_raw[raw_name], errors="coerce")
        daily_numeric[clean_name] = s
        
        # Outlier calculation
        rolling_med = s.rolling(30, min_periods=5).median()
        rolling_mad = (s - rolling_med).abs().rolling(30, min_periods=5).median()
        outliers = s[(s - rolling_med).abs() > 5.0 * rolling_mad.replace(0, np.nan)]
        for dt, val in outliers.items():
            outlier_records.append({
                "date": dt.strftime('%Y-%m-%d'),
                "series": clean_name,
                "raw_col": raw_name,
                "value": val,
                "rolling_median": rolling_med.loc[dt],
                "deviation_mad": abs(val - rolling_med.loc[dt]) / (rolling_mad.loc[dt] if rolling_mad.loc[dt] > 0 else 1.0)
            })
            
    print(f"Detected {len(outlier_records)} daily price outlier candidates (> 5 MAD). Logged for human review.")
    if outlier_records:
        pd.DataFrame(outlier_records).to_csv("data/interim/cbsl_daily_price_outliers.csv", index=False)
    
    # 2. Resample Monthly (MS)
    # Monthly mean, count of trading days
    monthly_mean = daily_numeric.resample("MS").mean()
    monthly_count = daily_numeric.resample("MS").count()
    
    # Full calendar month range from 2016-08-01 to 2026-10-01
    full_idx = pd.date_range("2016-08-01", "2026-10-01", freq="MS")
    monthly_mean = monthly_mean.reindex(full_idx)
    monthly_count = monthly_count.reindex(full_idx).fillna(0)
    
    MIN_TRADING_DAYS = 5  # Flag partial months if fewer than 5 days
    
    records = []
    for dt in full_idx:
        ym = dt.strftime("%Y-%m")
        d_str = dt.strftime("%Y-%m-%d")
        
        row_dict = {
            "year_month": ym,
            "date": d_str,
            "year": dt.year,
            "month": dt.month,
        }
        
        for clean_name in valid_map.keys():
            val = monthly_mean.loc[dt, clean_name]
            cnt = int(monthly_count.loc[dt, clean_name])
            row_dict[clean_name] = round(val, 2) if pd.notna(val) else np.nan
            row_dict[f"{clean_name}_days"] = cnt
            row_dict[f"{clean_name}_partial"] = bool(cnt > 0 and cnt < MIN_TRADING_DAYS)
            
        records.append(row_dict)
        
    monthly_df = pd.DataFrame(records)
    
    # 3. Interpolation for gaps of at most 2 months, longer gaps remain null
    for clean_name in valid_map.keys():
        s = monthly_df[clean_name].copy()
        # mask identifying original non-nulls
        valid_mask = s.notna()
        # linear interpolate with limit=2
        s_interp = s.interpolate(method="linear", limit=2, limit_area="inside")
        is_interp = s.isna() & s_interp.notna()
        
        monthly_df[clean_name] = s_interp.round(2)
        monthly_df[f"{clean_name}_is_interpolated"] = is_interp
        monthly_df[f"{clean_name}_provenance"] = np.where(
            valid_mask, "CBSL_Daily_Mean_Real",
            np.where(is_interp, "Linear_Interpolated_Max2Mo", "No_Data")
        )
        
    out_path.parent.mkdir(parents=True, exist_ok=True)
    monthly_df.to_csv(out_path, index=False)
    print(f"✅ Successfully built {out_path} with {len(monthly_df)} months ({monthly_df['year_month'].min()} to {monthly_df['year_month'].max()}).")
    return monthly_df

if __name__ == "__main__":
    build_monthly_cbsl_table()
