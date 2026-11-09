# Model Evaluation Scoreboard
**Data Version:** `7fd582fe` | **Source:** Real CBSL Prices & Verified NASA POWER Weather

| Crop | Model | Horizon | Metric | Model Value | Baseline Name | Baseline Value | Served Model | Coverage 80% | N | Verdict |
| :--- | :--- | :---: | :--- | :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| `chilli` | A2 Price Forecast | t+1 | WAPE | 0.1008 | SARIMAX | 0.1323 | `LightGBM` | 80.0% | 48 | **Usable** |
| `chilli` | A3 Supply Forecast | t+1 | WAPE | 0.1429 | seasonal_naive | 0.1947 | `LightGBM` | 75.0% | 48 | **Usable** |
| `big_onion` | A2 Price Forecast | t+1 | WAPE | 0.1474 | SARIMAX | 0.3334 | `LightGBM` | 80.0% | 48 | **Usable** |
| `big_onion` | A3 Supply Forecast | t+1 | WAPE | 0.5969 | seasonal_naive | 0.1723 | `seasonal_naive` | 68.8% | 48 | **Usable with limits** |
