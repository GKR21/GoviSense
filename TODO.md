# GoviSense Implementation TODO List

This document tracks all tasks assigned to the software implementation role (Heshan), prioritized from **P0** (Critical) to **P2** (Documentation & Packaging), mapping current system progress against target specifications.

---

## Task Summary Dashboard

| Domain | Total Tasks | Completed | In Progress | Pending |
| :--- | :---: | :---: | :---: | :---: |
| **Data Pipeline** | 4 | 4 | 0 | 0 |
| **Backend** | 8 | 2 | 3 | 3 |
| **Mobile App** | 5 | 0 | 1 | 4 |
| **Quality & Infra** | 3 | 0 | 1 | 2 |
| **Total** | **20** | **6** | **5** | **9** |

---

## 1. Data Pipeline

- [x] **Task 1 (P0)**: Fix the source label (`download_data.py:171`).
  - *Current Status*: Completed. Replaced single boolean interpolation check with 4-tier taxonomy (`real`, `anchor`, `interpolated`, `synthetic`) and explicit `is_demo` boolean flag. In `monthly_master.csv`, 140 rows are `real` (83.3%), 22 rows are audited `anchor` (13.1%), 6 rows are `interpolated` (3.6%), and `is_demo=False`. Demo seeding (`seed_anuradhapura.csv`) explicitly marks `source='synthetic'` and `is_demo=True`. Logged formal audit notification for Nayana.
  - *Files*: `scripts/download_data.py`, `scripts/seed_demo.py`, `src/govisense/data/clean.py`, `src/govisense/data/validate.py`.

- [x] **Task 2 (P1)**: Replace synthetic price, area, yield, and import series with real extractions.
  - *Current Status*: Completed. Replaced synthetic series with real empirical extractions from CBSL daily price bulletins, DOA CPP seasonal bulletins, HARTI market monitoring, WFP food price monitoring, and Customs trade statistics. Staged reproducible raw PDF fixtures in `data/raw/cbsl/` and `data/raw/cpp/`.
  - *Files*: `src/govisense/data/extract_cbsl.py`, `src/govisense/data/extract_cpp.py`, `scripts/download_data.py`, `data/raw/`.

- [x] **Task 3 (P1)**: Fix CPP column-offset alignment, add Sri Lanka national figures, and re-run 5% hand-check.
  - *Current Status*: Completed. Fixed table header and text-line parsing in `extract_cpp.py` to prevent column shifting when Target (ha) and Achieved (ha) both appear. Added Sri Lanka national aggregates (Big Onion 4,867 ha, 82,149 t; Chilli 15,899 ha, 142,116 t) with `validate_national_figures()`. Re-ran 5% hand-checked sample audit with an audited error rate of 4.55% across 22 ground-truth fields, passing the <= 10.0% honesty threshold.
  - *Files*: `src/govisense/data/extract_cpp.py`, `src/govisense/data/validate.py`, `docs/data-validation.md`, `tests/test_extract.py`.

- [x] **Task 4 (P1)**: Confirm `catalogue.csv` has the `licence` column.
  - *Current Status*: Confirmed. Column `licence` exists on line 1 of `data/catalogue.csv` and is validated in `test_catalogue_licence_and_provenance` in `tests/test_extract.py`.
  - *Files*: `data/catalogue.csv`, `src/govisense/data/catalogue.py`.

---

## 2. Backend

- [x] **Task 5 (P0)**: Replace hardcoded 64/24/12 adoption counts with explicit `data_available: false` response.
  - *Current Status*: Completed. Added `get_adoption_summary()` returning explicit `data_available: false`, null counts, and telemetry provenance notes. Implemented `GET /api/simulation/adoption-summary` and `GET /api/adoption/summary`, and updated `GET /api/simulation/adoption` with data availability flags.
  - *Files*: `src/govisense/api/main.py`, `src/govisense/simulation/agent_sim.py`, `tests/test_api.py`, `tests/test_day6_simulation_and_coverage.py`.

- [ ] **Task 6 (P0)**: Make API return hash and run ID in decision history, and bind `model_version` dynamically.
  - *Current Status*: `DecisionRecord` dataclass in `db/history.py` drops `run_id` and content `hash`, and defaults `model_version` to fixed string `"GoviSense v2.0"`.
  - *Target*: Add `run_id` and cryptographic `hash` to `DecisionRecord` / `DecisionHistoryRecord`, and bind `model_version` to active model pipeline version.
  - *Files*: `src/govisense/db/history.py`, `src/govisense/db/models.py`, `src/govisense/api/main.py`.

- [ ] **Task 7 (P0)**: Add `is_demo`, `data_available`, and `source_type` fields to API responses.
  - *Current Status*: Forecast and simulation endpoints return metrics without standard provenance headers.
  - *Target*: Include `is_demo: bool`, `data_available: bool`, and `source_type: str` in forecast, price, and allocation responses so frontend and mobile accurately display telemetry authenticity.
  - *Files*: `src/govisense/api/main.py`, `src/govisense/api/schemas.py`.

- [ ] **Task 8 (P1)**: JWT login with `officer`, `farmer`, and `admin` roles, protect endpoints, and restrict CORS.
  - *Current Status*: `auth.py` implemented with `farmer` and `officer` roles, password hashing with bcrypt, and login/refresh endpoints. Wildcard CORS currently enabled (`allow_origins=["*"]`).
  - *Target*: Add `admin` role explicitly; protect `/api/database/init`, `/api/feedback/retrigger`, and `/api/simulate`; replace `allow_origins=["*"]` with explicit whitelist (`http://localhost:8443`, `http://localhost:5173`, `http://localhost:3000`).
  - *Files*: `src/govisense/api/auth.py`, `src/govisense/api/main.py`.

- [ ] **Task 9 (P1)**: Add missing endpoints for Rashmika (Catalogue, Adoption Summary, Decision List with Hash/Run ID, Run Info).
  - *Current Status*: Some endpoints exist in monolithic `main.py`; standalone catalogue query, run info, and enhanced decision history with hash/run ID are needed.
  - *Target*: Expose `GET /api/catalogue`, `GET /api/simulation/adoption-summary`, `GET /api/history/decisions` (with hash & run ID), and `GET /api/pipeline/run-info`.
  - *Files*: `src/govisense/api/main.py` or modular route files.

- [ ] **Task 10 (P1)**: Alerts backend (`routes/alerts.py`, `i18n/templates.json`, `/api/alerts`, acknowledge endpoint).
  - *Current Status*: DB models `Alert` and `AlertInteraction` exist; `routes/alerts.py` is currently empty (0 bytes).
  - *Target*: Create `src/govisense/i18n/templates.json` with English, Sinhala, and Tamil alert templates; implement `GET /api/alerts` and `POST /api/alerts/{id}/acknowledge`.
  - *Files*: `src/govisense/api/routes/alerts.py`, `src/govisense/i18n/templates.json`, `src/govisense/db/models.py`.

- [ ] **Task 11 (P1)**: Modernize API architecture: replace `@app.on_event` with `lifespan`, split `main.py` into route modules, and populate `deps.py` / `schemas.py`.
  - *Current Status*: `main.py` contains 600+ lines with deprecated `@app.on_event("startup")`; `deps.py`, `schemas.py`, and `routes/*` are mostly empty.
  - *Target*: Implement async `lifespan(app)` context manager; decompose into `routes/alerts.py`, `routes/auth.py`, `routes/farmer.py`, `routes/officer.py`; populate `schemas.py`.
  - *Files*: `src/govisense/api/main.py`, `src/govisense/api/deps.py`, `src/govisense/api/schemas.py`, `src/govisense/api/routes/`.

- [ ] **Task 12 (P1)**: Farmer ID checks: rate limit, duplicate-report handling, and registry verification note.
  - *Current Status*: `PlantingReportStore` accepts submissions without rate limiting or duplicate timestamp/area detection.
  - *Target*: Add rate limiting per `farmer_id`, reject duplicate reports within same season/crop window, and add documentation on future Agrarian Services Department registry integration.
  - *Files*: `src/govisense/feedback/planting_reports.py`, `src/govisense/api/main.py`.

---

## 3. Mobile App (Flutter / Dart)

- [ ] **Task 13 (P0)**: Remove fake success receipt (`farmer_repository.dart:346-373`).
  - *Current Status*: App optimistically inserts a "Planting Declaration Logged" confirmation alert into the inbox before the API confirms success.
  - *Target*: Remove optimistic fake receipt; on failure, mark report as `pending_sync`, display retry state, and notify the farmer.
  - *Files*: `mobile/lib/features/farmer/data/farmer_repository.dart`.

- [ ] **Task 14 (P1)**: Show clear banner when recommendations come from offline `_initialCrops`.
  - *Current Status*: Fallback to hardcoded `_initialCrops` happens silently when API is unreachable.
  - *Target*: Display persistent offline/cached warning banner in the farmer crop recommendation view.
  - *Files*: `mobile/lib/features/farmer/screens/` or provider/bloc layer.

- [ ] **Task 15 (P1)**: Verify market prices screen reads the API, and wire it if not.
  - *Current Status*: Uses mock or local data in `market_prices_screen.dart`.
  - *Target*: Connect screen to live backend prices endpoint (`/api/prices` or `/api/market-prices`) with graceful offline fallback.
  - *Files*: `mobile/lib/features/farmer/screens/market_prices_screen.dart`, `mobile/lib/features/farmer/services/farmer_api_service.dart`.

- [ ] **Task 16 (P1)**: Build alert inbox with *Acknowledge* and *Ask an Officer*, and verify trilingual localization.
  - *Current Status*: Basic alerts list exists in mobile state; lacks interactive acknowledge and officer query triggers.
  - *Target*: Add Acknowledge and Ask Officer action buttons; ensure English, Sinhala, and Tamil strings are fully translated.
  - *Files*: `mobile/lib/features/alerts/`, `mobile/lib/l10n/`.

- [ ] **Task 17 (P1)**: Validate two-stage form (planting and harvest reports) schema consistency.
  - *Current Status*: Form collects planting area; outcome fields (`harvest_outcome_mt`, `sale_price_rs_kg`, `sale_channel`) need verification against backend `PlantingReportRecord`.
  - *Target*: Ensure two-stage flow (Stage 1: Intent/Planting; Stage 2: Harvest & Sales) matches backend Pydantic/SQLAlchemy schema.
  - *Files*: `mobile/lib/features/farmer/screens/`, `src/govisense/db/models.py`.

---

## 4. Quality & Infrastructure

- [ ] **Task 18 (P1)**: TestClient tests for each endpoint, bad-input, concurrency (20 parallel reports), and data-validation.
  - *Current Status*: `test_api.py`, `test_extract.py`, `test_db_and_concurrency.py`, and `test_auth_and_rbac.py` pass.
  - *Target*: Expand test coverage with `TestClient` for all endpoints, invalid payload rejection (422/400), 20-thread concurrent report stress tests, and automated data-validation check on source labels.
  - *Files*: `tests/test_api.py`, `tests/test_concurrency_stress.py`, `src/govisense/data/validate.py`.

- [ ] **Task 19 (P2)**: Populate empty DevOps and documentation files.
  - *Current Status*: `.github/workflows/ci.yml` (0 bytes), `docker-compose.yml` (0 bytes), `Makefile` (0 bytes), `.env.example` (0 bytes), `docs/assumptions.md` (0 bytes), `docs/ai-usage-log.md` (0 bytes).
  - *Target*: Fill complete Docker Compose (FastAPI, Postgres/SQLite, React frontend), GitHub Actions CI matrix, development Makefile, `.env.example`, and comprehensive architecture/assumptions/AI audit documentation.
  - *Files*: `.github/workflows/ci.yml`, `docker-compose.yml`, `Makefile`, `.env.example`, `docs/assumptions.md`, `docs/ai-usage-log.md`.

- [ ] **Task 20 (P1)**: Run and verify all sanity checks: Auth, CORS, Alerts, and Mobile Prices screen.
  - *Current Status*: Auth and RBAC verified via 19 tests in `test_auth_and_rbac.py`. CORS and Alerts pending final modularization.
  - *Target*: End-to-end integration verification across backend and client interfaces.

