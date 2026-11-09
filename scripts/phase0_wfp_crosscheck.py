import pandas as pd
import numpy as np

wfp = pd.read_csv('data/raw/wfp/wfp_food_prices_lka.csv')
raw = pd.read_csv('data/raw/cbsl/cbsl_daily_prices_historical.csv', comment='#')
raw.columns = [c.strip() for c in raw.columns]
d_col = raw.columns[0]
raw[d_col] = pd.to_datetime(raw[d_col], errors='coerce')
raw = raw.dropna(subset=[d_col]).set_index(d_col)

# Inspect WFP commodities matching onion / chilli
for c in wfp['commodity'].unique():
    if any(k in c.lower() for k in ['onion', 'chilli', 'chili']):
        sub = wfp[wfp['commodity'] == c]
        markets = len(sub['market'].unique())
        rows = len(sub)
        d_min = sub['date'].min()
        d_max = sub['date'].max()
        print(f"WFP Commodity: {c:<30} | Markets: {markets:2d} | Rows: {rows:5d} | Dates: {d_min} to {d_max}")

# Cross check Colombo / Pettah
wfp['date'] = pd.to_datetime(wfp['date'])
for c in ['Onions (red)', 'Onions (big)', 'Chili (green)', 'Chili (red)'] + [x for x in wfp['commodity'].unique() if any(k in x.lower() for k in ['onion', 'chilli', 'chili'])]:
    sub = wfp[(wfp['commodity'] == c) & (wfp['market'].str.lower().str.contains('colombo|pettah'))]
    if len(sub) > 10:
        wfp_m = sub.set_index('date').resample('MS')['price'].mean()
        # candidate CBSL
        if 'big' in c.lower():
            cbsl_col = 'Big onion (imp) (wholesale, pettah) (Rs/kg)'
        elif 'green' in c.lower():
            cbsl_col = 'Green chilli (wholesale, pettah) (Rs/kg)'
        elif 'red' in c.lower() and 'chili' in c.lower():
            cbsl_col = 'Dried chilli (imp) (wholesale, pettah) (Rs/kg)'
        else:
            cbsl_col = 'Red onion (local) (wholesale, pettah) (Rs/kg)'
            
        cbsl_m = pd.to_numeric(raw[cbsl_col], errors='coerce').resample('MS').mean()
        cmp = pd.DataFrame({'cbsl': cbsl_m, 'wfp': wfp_m}).dropna()
        if len(cmp) > 5:
            r = np.corrcoef(cmp['cbsl'], cmp['wfp'])[0, 1]
            ratio = cmp['cbsl'] / cmp['wfp']
            pct_diff = np.abs(cmp['cbsl'] - cmp['wfp']) / cmp['wfp'] * 100.0
            gt_20 = (pct_diff > 20.0).sum()
            print(f"\nMatch: WFP '{c}' vs CBSL '{cbsl_col}' (N={len(cmp)} months):")
            print(f"  Pearson r = {r:.4f} | Ratio mean = {ratio.mean():.2f} (std={ratio.std():.2f}) | Diff > 20%: {gt_20}/{len(cmp)} ({gt_20/len(cmp)*100:.1f}%)")
