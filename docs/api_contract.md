# GoviSense REST API Specification & Data Contracts
**Team DARKBITE · ModelX 2.0 Phase 1**

This document specifies the exact API contract implemented across the GoviSense FastAPI backend (`src/govisense/api`), the React Officer Dashboard (`frontend/`), and the Farmer Apps (`mobile/` and PWA).

---

## 1. Regulatory Governance & Provenance Envelope (Rule 7)

Every API response carrying model output or decision recommendations strictly includes the cryptographic provenance envelope:

```json
{
  "run_id": "RUN-A1B2C3D4",
  "data_version": "a1b2c3d4",
  "model_version": "680c25e+8f9a2b1c",
  "data_quality": "real",
  "is_demo": false,
  "served_model": "LightGBM-v2.1",
  "assumptions_ref": "docs/assumptions.md"
}
```

* `run_id`: Execution identifier in database `runs` table.
* `data_version`: First 8 hex characters of SHA-256 over all processed training tables plus row counts.
* `model_version`: Git commit prefix (7 chars) + hash of fitted model parameter artifacts.
* `data_quality`: `real` | `partial` | `demo_estimate` | `no_data`.
* `is_demo`: `false` when running on genuine data, `true` when running demo/synthetic fallback.
* `served_model`: Explicit name of the winning model or `seasonal_naive_baseline` if baseline won.
* `assumptions_ref`: Reference to `docs/assumptions.md`.

---

## 2. API Endpoints Table

| Method | Endpoint | Description | Auth / Role |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | Service health, active database dialect, and code/data version hashes | Public |
| `POST` | `/api/auth/login` | JWT login for officers, farmers, and admins | Public |
| `GET` | `/api/forecasts/latest` | Latest forward multi-month harvest, demand, SPI, price & scenarios | Public / Officer |
| `POST` | `/api/simulate` | Interactive what-if simulation (area, yield, lead-time, thresholds) | Officer |
| `GET` | `/api/gap` | Gap timeline, best/worst deficit, deadlines, and policy options | Officer |
| `GET` | `/api/farmer/top3` | Personalized crop allocation, stop rule, profit range & agronomic score | Farmer / Public |
| `POST` | `/api/feedback/planting-report` | Farmer Stage 1 planting report submission with consent validation | Farmer |
| `POST` | `/api/feedback/harvest-report` | Farmer Stage 2 harvest, loss, storage and sale report submission | Farmer |
| `POST` | `/api/feedback/retrigger` | Force pipeline refit and forecast recalculation on new ground reports | Officer |
| `GET` | `/api/adoption/summary` | Recommended vs reported area, predicted vs actual, 0/30/60% sim | Officer |
| `GET` | `/api/history/decisions` | Immutable decision history ledger with SHA-256 record hashes | Officer |
| `POST` | `/api/history/log-action` | Log officer policy action with SHA-256 audit record hash | Officer |
| `GET` | `/api/runs/{id}` | Detailed execution parameters, assumptions, and forecast counts | Officer |
| `GET` | `/api/catalogue` | Provenance registry, dataset licences, URLs, and data freshness age | Public |
| `GET` | `/api/confidence/badge` | Detailed 5-rule confidence breakdown per crop | Public |
| `GET` | `/api/evaluation/scoreboard` | Walk-forward WAPE, coverage, baseline comparisons, and usability | Officer / Public |
| `GET` | `/api/alerts` | Active glut, shortage, and deadline alerts with multi-lingual text | Public |
| `POST` | `/api/alerts/{id}/ack` | Acknowledge active warning alert | Officer |
| `POST` | `/api/alerts/{id}/ask-officer` | Farmer inquiry on an active alert | Farmer |
| `GET` | `/api/prices/latest` | Current wholesale and retail market prices with freshness indicators | Public |

---

## 3. Detailed Request & Response Schemas

### 3.1 Health Check (`GET /api/health`)
Response Schema: `HealthResponse`
```json
{
  "status": "healthy",
  "active_database": "sqlite",
  "dialect": "sqlite",
  "is_fallback": true,
  "data_version": "47cb23aa",
  "model_version": "680c25e+93a10be4",
  "git_commit": "680c25e",
  "timestamp": "2026-11-09T02:20:00Z"
}
```

### 3.2 Simulation (`POST /api/simulate`)
Request Schema: `SimulateRequest`
```json
{
  "crop": "big_onion",
  "planted_area_ha": 3500.0,
  "expected_yield_mt_per_ha": 16.0,
  "lead_time_weeks": 7,
  "band_threshold_glut": 1.2,
  "band_threshold_shortage": 0.8,
  "loss_pct": 0.08
}
```
Response Schema: `SimulateResponse` (includes Provenance Envelope)

### 3.3 Farmer Top 3 Recommendation (`GET /api/farmer/top3`)
Query Parameters:
- `farmer_id`: Pseudonymous ID string (e.g., `LK-AP-001`)
- `district`: string (default: `"Anuradhapura"`)
- `soil_type`: optional string
- `irrigation_type`: `"irrigated"` | `"rainfed"`
- `as_of`: optional ISO date string

Response Schema: `FarmerTop3Response`
```json
{
  "run_id": "RUN-01",
  "data_version": "47cb23aa",
  "model_version": "680c25e+93a10be4",
  "data_quality": "real",
  "is_demo": false,
  "farmer_id": "LK-AP-001",
  "district": "Anuradhapura",
  "as_of": "2026-11-09",
  "recommended_crops": [
    {
      "crop_id": "big_onion",
      "name_en": "Big Onion",
      "name_si": "ලොකු ලූණු",
      "suitability_score": 86.4,
      "allocated_ha": 1.2,
      "remaining_target_ha": 450.0,
      "stop_rule_active": false,
      "expected_profit_min_rs_ha": 350000.0,
      "expected_profit_max_rs_ha": 680000.0,
      "risk_level": "Medium",
      "water_need": "Moderate",
      "planting_window": "May - June",
      "harvest_period": "August - September",
      "market_pressure_at_harvest": "Balanced",
      "confidence_badge": "high",
      "price_range_12m": { "min": 110.0, "p50": 165.0, "max": 240.0 }
    }
  ]
}
```

### 3.4 Feedback Loop: Stage 1 Planting Report (`POST /api/feedback/planting-report`)
Request Schema: `PlantingReportRequest`
```json
{
  "pseudonymous_id": "LK-AP-001",
  "crop": "big_onion",
  "district": "Anuradhapura",
  "season": "2026 Yala",
  "irrigation_type": "major_irrigation",
  "planned_area_ha": 1.2,
  "planted_area_ha": 1.2,
  "planting_date": "2026-05-15",
  "expected_harvest_date": "2026-08-20",
  "recommended_crop_shown": "big_onion",
  "followed_recommendation": "yes",
  "reason_for_decision": "High expected farmgate return",
  "expected_price_rs_kg": 150.0,
  "soil_ph": 6.8,
  "app_version": "2.0.0",
  "consent": true
}
```

### 3.5 Feedback Loop: Stage 2 Harvest Report (`POST /api/feedback/harvest-report`)
Request Schema: `HarvestReportRequest`
```json
{
  "pseudonymous_id": "LK-AP-001",
  "crop": "big_onion",
  "district": "Anuradhapura",
  "season": "2026 Yala",
  "harvest_date": "2026-08-22",
  "area_harvested_ha": 1.2,
  "quantity_harvested_mt": 18.5,
  "loss_quantity_mt": 1.2,
  "quantity_sold_mt": 14.0,
  "quantity_stored_mt": 3.3,
  "farmgate_price_rs_kg": 155.0,
  "sale_market_or_buyer": "Dambulla Dedicated Economic Centre",
  "sale_month": 8,
  "production_problems": ["thrips"],
  "notes": "Good yield despite minor dry spell",
  "consent": true
}
```

### 3.6 Decision Audit Ledger (`POST /api/history/log-action`)
Request Schema: `LogActionRequest`
```json
{
  "run_id": "RUN-01",
  "crop": "big_onion",
  "season": "2026 Yala",
  "officer_id": "OFFICER-001",
  "action_type": "STORE",
  "quantity_mt": 1500.0,
  "rationale": "High projected harvest in August; absorb glut into cold storage",
  "model_recommended_action": "STORE",
  "officer_response": "accepted"
}
```
Response:
```json
{
  "status": "success",
  "decision_id": "DEC-982FA1",
  "record_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "timestamp": "2026-11-09T02:22:00Z"
}
```

---

## 4. Contract Test Suites

The contract tests in `tests/test_api_contract.py` assert that:
1. All endpoints defined in this specification exist and respond with HTTP 200/201.
2. Response payloads validate against Pydantic models in `src/govisense/api/schemas.py`.
3. Model-bearing outputs include required provenance fields: `run_id`, `data_version`, `model_version`, `data_quality`, `is_demo`, `assumptions_ref`.
