# Farmer mobile AI audit — 2026-11-10

Status: implementation has not passed the release checks. This records observed
behavior on `develop` at `2782987`, before production code changes.

## Git gate

All three required commits are ancestors of HEAD: `5b78e84`, `eb1d013`,
`6cad076`. The combined `git branch --contains` command treats later arguments
as branch patterns, so each commit was checked separately as well.

## Local runtime

TestClient exercised the real application lifespan, existing PostgreSQL schema,
model loading and login in a separate temporary audit database. No configured
application database was used. Existing initialization seeded benchmark prices,
template alerts and migrated JSON reports; these are not independent live data.

| Request | HTTP | Observed result |
| --- | --- | --- |
| GET /api/farmer/top3 | 200 | Brinjal and tomato; missing price, profit and SPI; nevertheless marked data_available=true and high confidence |
| GET /api/prices/latest | 200 | Two December 2024 monthly prices, both is_outdated=false |
| GET /api/alerts | 200 | Five seeded template alerts, marked is_demo=false |

The prices route exists in `api/routes/data.py`; checking only main.py would
incorrectly conclude it is absent. The endpoint currently manufactures retail
prices when missing and floor prices when history is absent.

## Season filter, all months

These are CSV window checks, before soil/water suitability ranking:

| Month | Passing crop IDs |
| --- | --- |
| 1, 2, 3, 12 | none |
| 4 | chilli_green, bitter_gourd, snake_gourd, long_bean, cowpea, mung_bean |
| 5, 6 | big_onion, chilli_green, bitter_gourd, snake_gourd, long_bean, cowpea, sesame, mung_bean |
| 7 | big_onion, snake_gourd, cowpea, sesame, mung_bean |
| 8 | cowpea, mung_bean |
| 9, 10, 11 | tomato, brinjal |

The current default query hardcodes month 10 and an old season; `as_of` is
ignored. November also permits only tomato/brinjal. Available A1/A2 models
cover big_onion/chilli, so the default candidate crops lack these forecasts.

## API calls and consumers

| Method/path | Consumer | Model |
| --- | --- | --- |
| POST /api/auth/login | AuthPage, AuthRepository | token map |
| GET /api/auth/me | splash/login validation | user map; separate AuthUser is not used here |
| GET /api/health | farmer connection check | status map |
| GET /api/farmer/top3 | farmer home, comparison, crop detail | CropItem via service mapper |
| GET /api/market-prices | market prices screen | MarketPriceItem |
| POST /api/feedback/planting-report | report wizard, retry | PlantingReport, PlantingReceipt |
| POST /api/alerts/{id}/acknowledge | farmer inbox | boolean |
| POST /api/alerts/{id}/ask | farmer inbox | boolean |
| GET /api/forecasts/latest | officer page | MonthlySupplyPoint, forecast models |
| POST /api/simulate | officer page | scenario models |
| POST /api/history/log-action | officer page | OfficerDecision |
| GET /api/auth/me | officer identity | user map |

The receipt QR encodes the server verification URL; it is not a fetch performed
by the app. The farmer inbox currently never fetches GET /api/alerts.

## Sources and parsing mismatches

| Screen | Current source and problem |
| --- | --- |
| Farmer home/comparison/detail | Static repository crops until a nonempty API result replaces them; no durable recommendation cache |
| Market prices | Bundled _allPrices until a nonempty legacy market-prices response; no durable cache |
| Farmer inbox | Static weather/market alerts plus local submission events; backend alerts are not loaded |
| Farmer profile/card | Fixed initial farmer ID, name and parcel; not verified server profile |
| Report history/receipt | Actual acceptance receipts, but pending reports survive only this process |
| Officer page | API forecasts/simulation/actions; retained navigation is outside the intended farmer APK |
| Old dashboard/forecasts/alerts/profile pages | Additional placeholder/dead screens; reachability must be removed or verified |

- Backend sends real crop IDs such as brinjal/tomato; Dart maps every unknown
  crop to Green Gram and adds fabricated metadata.
- Backend sends nullable price/profit/SPI; Dart substitutes fit 80, prices
  200/350, water 500, balanced risk and price-based profit multipliers.
- Backend has expected_net_profit_per_acre; Dart does not consume it and instead
  derives its own profits. Supply/price quality, provenance, stop-rule numbers
  and 12-month intervals are also not represented by CropItem.
- CropItem requires localized names, formatted profit strings, scientific name,
  photo attribution, tips, cost and yield strings not supplied by the response.
- MarketPriceItem expects crop_en/si/ta, formatted wholesale/retail strings,
  economic_center_en/si/ta and trend flags. Prices/latest instead sends crop,
  market, date and numeric wholesale_price_rs_kg/retail_price_rs_kg.
- Missing market values become zero and a missing trend becomes stable. These
  are claims rather than missing-data states.
- Alerts return translations, message_key and params but FarmerAlert has no
  server parser. Authentication's /me response does not provide the required
  farmer pseudonymous ID to the current mobile profile.
- Current responses lack the common api_version/generated_at/as_of envelope;
  available keys differ between successful and empty recommendations.

## Backend correctness

Ranking is truncated with ranking[:3] before the stop check. A stopped crop stays
in the results with zero area, so the next eligible crop is not promoted.
Reported area goes through a store with JSON/in-memory fallback. Allocation is
min(land * 0.60, remaining), not the district optimizer. Run IDs are commit-derived,
not distinct persisted executions. Optimizer infeasibility silently uses bound
midpoints and relaxes change constraints. Supply/SPI provenance is not computed
from the columns used; synthetic area/import inputs can be labelled real.

## Baseline checks

Full command: `.venv/Scripts/python.exe -m pytest -q --tb=short` with isolated
PostgreSQL DATABASE_URL and TEST_DATABASE_URL. Collected **275**, with **261
passed, 12 failed, 2 skipped**, in 212.29 seconds. No deselection or test edits.

Failing tests: test_fix12_sample; test_fix2_auth seed login;
test_fix6_monthly_data populated master; test_fix9_cbsl; test_fix_f4_outdated_data;
three test_phase1_data cases (sources, PDF, sample); test_phase5_farmer_experience
inquiry flow; test_provenance persisted run; two test_real_price_validation cases.
Connection-pool exhaustion also appears in this full baseline run. Existing
auth/security failures are handed off rather than changed in this scope.

## Blockers

- BLOCKED: no hosted backend URL. User confirmed it is not hosted yet. The
  proposed api.govisense.lk default is not evidence of a deployed service.
- BLOCKED: raw CBSL/WFP/PDF/source files are absent under data/raw. Processed
  tables exist but cannot establish exact latest daily raw-row equality.
- BLOCKED: a clean full-suite result includes existing failures, with some
  fixes outside the permitted scope. Do not claim the release checks passed.
- Pending: Step 1 contract freeze, A5/A6/A1/A3/A9, B1/B2/B3/B4. An audit is not
  implementation completion and no APK was built.

## A3 date validation follow-up

The endpoint now validates ISO dates and months, defaults to today's UTC month,
echoes as_of/generated_at/planting_month on both populated and empty responses,
and rejects conflicting date/month aliases with AS_OF_MONTH_CONFLICT. Existing
explicit month queries remain supported when no as_of is provided.

Runtime on 2026-11-10 returned brinjal/tomato. On 2026-06-15 it returned
chilli_green/bitter_gourd/snake_gourd; big onion passes the June window but did
not rank in the first three for the default parcel. November crops had null
supply_forecast_mt, profit_range_rs_kg, price_forecast,
expected_net_profit_per_acre, monthly_price_ranges_12m and spi_ratio_at_harvest.
The June chilli had these model values; the other June crops lacked them.
Model freshness/cutoff correctness is not established by this seasonal fix.

All 12 added TestClient cases passed. The full suite collected 287: **275
passed, 10 failed, 2 skipped**, in 172.34 seconds. The ten failing cases are a
subset of the baseline failures; the two pool-timeout cases did not recur.
This is not a clean regression gate. No existing tests were edited or excluded.
