import subprocess
import io
import pandas as pd
import numpy as np

print("=" * 80)
print("0.1: REGENERATE PRICES: seed_demo.py (seed 42) & download_data.py ANCHORS VS MASTER")
print("=" * 80)

# 1. Regenerate seed_demo.py (commit 2269aef) prices
seed_code = subprocess.check_output(['git', 'show', '2269aef:scripts/seed_demo.py'], text=True)
code_clean = seed_code.split("if __name__")[0]
scope = {'__file__': 'scripts/seed_demo.py'}
exec(code_clean, scope)
gen_df = scope['generate_anuradhapura_historical_data']()

# 2. Extract anchors in download_data.py
import re
with open('scripts/download_data.py', 'r', encoding='utf-8') as f:
    dl_text = f.read()

# Load master
master_df = pd.read_csv('data/processed/monthly_master.csv')

price_cols = ['wholesale_price_rs_kg', 'retail_price_rs_kg', 'farmgate_price_rs_kg']
for crop in ['big_onion', 'chilli']:
    print(f"\n--- Crop: {crop.upper()} ---")
    g_crop = gen_df[gen_df['crop'] == crop].reset_index(drop=True)
    m_crop = master_df[master_df['crop'] == crop].reset_index(drop=True)
    
    for col in price_cols:
        r = np.corrcoef(g_crop[col], m_crop[col])[0, 1]
        max_diff = np.max(np.abs(g_crop[col] - m_crop[col]))
        mean_diff = np.mean(np.abs(g_crop[col] - m_crop[col]))
        print(f"seed_demo.py vs Master | {col:<24} | Pearson r: {r:8.4f} | Max Diff: {max_diff:8.2f} | Mean Diff: {mean_diff:8.2f}")

# Check where master prices come from:
# Let's inspect scripts/download_data.py anchor dictionary
print("\nAnchor lookup in scripts/download_data.py:")
matches = re.findall(r'"(\d{4}-\d{2})":\s*\{\s*"big_onion":\s*\{"wholesale":\s*([\d\.]+)', dl_text)
print(f"Found {len(matches)} hardcoded monthly anchors in download_data.py:")
for ym, w in matches[:11]:
    m_val = master_df[(master_df['year_month'] == ym) & (master_df['crop'] == 'big_onion')]['wholesale_price_rs_kg'].values
    print(f"  {ym}: anchor wholesale = {w} | master wholesale = {m_val[0] if len(m_val) else 'N/A'}")

print("\n" + "=" * 80)
print("0.2: MASTER WHOLESALE VS EVERY CANDIDATE COLUMN IN RAW CBSL CSV")
print("=" * 80)

raw = pd.read_csv("data/raw/cbsl/cbsl_daily_prices_historical.csv", comment="#")
raw.columns = [c.strip() for c in raw.columns]
d_col = raw.columns[0]
raw[d_col] = pd.to_datetime(raw[d_col], errors="coerce")
raw = raw.dropna(subset=[d_col]).set_index(d_col)

# Filter candidate columns for onion and chilli
candidate_cols = [c for c in raw.columns if any(k in c.lower() for k in ['onion', 'chilli', 'chili'])]
print(f"Total candidate columns in raw CBSL: {len(candidate_cols)}")

for crop in ['big_onion', 'chilli']:
    print(f"\n--- Comparing Master {crop.upper()} Wholesale Price with Candidate Columns ---")
    m_crop = master_df[master_df.crop == crop].copy()
    m_crop['date'] = pd.to_datetime(m_crop['date'])
    m_series = m_crop.set_index('date')['wholesale_price_rs_kg']
    
    # Filter candidates by crop keywords
    kw = 'onion' if crop == 'big_onion' else 'chilli'
    crop_candidates = [c for c in candidate_cols if kw in c.lower()]
    
    results = []
    for col in crop_candidates:
        s_numeric = pd.to_numeric(raw[col], errors='coerce')
        if s_numeric.dropna().empty:
            continue
        m_raw = s_numeric.resample("MS").mean()
        cmp = pd.DataFrame({"raw": m_raw, "master": m_series}).dropna()
        if len(cmp) < 6:
            continue
        r = np.corrcoef(cmp["raw"], cmp["master"])[0, 1]
        ratio = cmp["master"] / cmp["raw"]
        pct_diff = np.abs(cmp["master"] - cmp["raw"]) / cmp["raw"] * 100.0
        months_within_1pct = (pct_diff <= 1.0).sum()
        results.append({
            "column": col,
            "N": len(cmp),
            "r": r,
            "ratio_mean": ratio.mean(),
            "ratio_min": ratio.min(),
            "ratio_max": ratio.max(),
            "ratio_std": ratio.std(),
            "within_1pct": months_within_1pct,
        })
    
    res_df = pd.DataFrame(results)
    if not res_df.empty:
        res_df = res_df.sort_values(by="r", ascending=False)
        for _, row in res_df.iterrows():
            print(f"Col: {row['column'][:45]:<45} | N={int(row['N']):2d} | r={row['r']:7.4f} | ratio={row['ratio_mean']:5.2f} [{row['ratio_min']:5.2f}, {row['ratio_max']:5.2f}] | <=1% diff: {int(row['within_1pct'])} mos")
    else:
        print("No matching candidate columns with sufficient data.")

print("\n" + "=" * 80)
print("0.3: CBSL DAILY MONTHLY MEANS VS WFP FOOD PRICES SRI LANKA")
print("=" * 80)

wfp = pd.read_csv("data/raw/wfp/wfp_food_prices_lka.csv")
print("WFP dataset shape:", wfp.shape)
print("WFP columns:", wfp.columns.tolist())
print("WFP commodity value counts:")
print(wfp['commodity'].value_counts().head(10))

# Filter WFP for Onions and Chillies
wfp_onion = wfp[wfp['commodity'].str.lower().str.contains('onion')].copy()
wfp_chilli = wfp[wfp['commodity'].str.lower().str.contains('chilli|chili')].copy()

print(f"\nWFP Onion commodities: {wfp_onion['commodity'].unique().tolist()}")
print(f"WFP Chilli commodities: {wfp_chilli['commodity'].unique().tolist()}")
print(f"WFP Markets: {wfp['market'].unique()[:5].tolist()}")
print(f"WFP Price units: {wfp['unit'].unique().tolist()} | Price types: {wfp['priceflag'].unique().tolist() if 'priceflag' in wfp.columns else 'N/A'}")

# Cross check CBSL Pettah imported big onion against WFP Pettah big onion
wfp_bo = wfp_onion[wfp_onion['market'].str.lower().str.contains('pettah|colombo')].copy()
if not wfp_bo.empty:
    wfp_bo['date'] = pd.to_datetime(wfp_bo['date'])
    wfp_bo = wfp_bo.set_index('date').resample('MS')['price'].mean()
    cbsl_bo = raw['Big onion (imp) (wholesale, pettah) (Rs/kg)'].astype(float).resample('MS').mean()
    comp_wfp = pd.DataFrame({'cbsl': cbsl_bo, 'wfp': wfp_bo}).dropna()
    comp_wfp['ratio'] = comp_wfp['cbsl'] / comp_wfp['wfp']
    comp_wfp['pct_diff'] = np.abs(comp_wfp['cbsl'] - comp_wfp['wfp']) / comp_wfp['wfp'] * 100.0
    r_wfp = np.corrcoef(comp_wfp['cbsl'], comp_wfp['wfp'])[0, 1]
    diff_gt_20 = (comp_wfp['pct_diff'] > 20.0).sum()
    print(f"\nCBSL Pettah vs WFP Pettah Big Onion (N={len(comp_wfp)}):")
    print(f"  Pearson r: {r_wfp:.4f} | Mean Ratio (CBSL/WFP): {comp_wfp['ratio'].mean():.2f} (std={comp_wfp['ratio'].std():.2f})")
    print(f"  Months differing over 20%: {diff_gt_20} of {len(comp_wfp)} ({diff_gt_20/len(comp_wfp)*100:.1f}%)")

print("\n" + "=" * 80)
print("0.4: REPRODUCTION OF PROPOSAL BENCHMARK VALUES FROM RAW CBSL FILE")
print("=" * 80)
benchmarks = [
    ("2025-02-17", "Big onion imp ~Rs 130", 130.0),
    ("2026-09-16", "Big onion imp ~Rs 260", 260.0),
    ("2025-02-17", "Dried chilli imp ~Rs 650", 650.0),
    ("2026-09-16", "Dried chilli imp ~Rs 1120", 1120.0),
    ("2026-09-16", "Green chilli ~Rs 500", 500.0),
    ("2026-09-21", "Green chilli ~Rs 300", 300.0),
]

target_dates = ["2025-02-17", "2026-09-16", "2026-09-21"]
print(f"Available dates in raw CBSL around target dates:")
for td in target_dates:
    dt = pd.to_datetime(td)
    nearby = raw.loc[dt - pd.Timedelta(days=2): dt + pd.Timedelta(days=2)]
    print(f"Date {td} in raw CBSL index? {dt in raw.index} (Nearby found: {len(nearby)} rows)")

print("\nInspecting exact raw values on target dates for all candidate columns:")
for td in target_dates:
    dt = pd.to_datetime(td)
    if dt in raw.index:
        row = raw.loc[dt]
        print(f"\n--- Date: {td} ---")
        for col in candidate_cols:
            val = row[col]
            if pd.notna(val) and str(val).strip() != "":
                print(f"  {col:<55}: {val}")
    else:
        print(f"\n--- Date: {td} NOT directly in index ---")

print("\n" + "=" * 80)
print("0.5: RAW CBSL COLUMN LIST, SPAN, NULL SHARES OVER TIME")
print("=" * 80)
print(f"Total columns: {len(raw.columns)}")
print(f"Raw Date Range: {raw.index.min()} to {raw.index.max()}")

null_summary = []
for col in candidate_cols:
    s = raw[col]
    s_valid = s.dropna()
    s_valid = s_valid[s_valid.astype(str).str.strip() != ""]
    if not s_valid.empty:
        first_d = s_valid.index.min().strftime('%Y-%m-%d')
        last_d = s_valid.index.max().strftime('%Y-%m-%d')
        total_valid = len(s_valid)
        null_share = (len(raw) - total_valid) / len(raw) * 100.0
        null_summary.append({
            "col": col,
            "first_date": first_d,
            "last_date": last_d,
            "valid_days": total_valid,
            "null_pct": null_share
        })

ns_df = pd.DataFrame(null_summary).sort_values(by="valid_days", ascending=False)
for _, r in ns_df.iterrows():
    print(f"{r['col']:<55} | {r['first_date']} to {r['last_date']} | Valid: {int(r['valid_days']):4d} | Null: {r['null_pct']:5.1f}%")
