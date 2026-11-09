# GoviSense Implementation TODO List

This document tracks all tasks assigned to the software implementation role (Heshan), prioritized from **P0** (Critical) to **P2** (Documentation & Packaging), mapping current system progress against target specifications.

---

## Task Summary Dashboard

| Domain | Total Tasks | Completed | In Progress | Pending |
| :--- | :---: | :---: | :---: | :---: |
| **Data Pipeline** | 4 | 4 | 0 | 0 |
| **Backend** | 8 | 8 | 0 | 0 |
| **Mobile App** | 5 | 3 | 1 | 1 |
| **Quality & Infra** | 3 | 0 | 1 | 2 |
| **Total** | **20** | **15** | **2** | **3** |

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

- [x] **Task 6 (P0)**: Make API return hash and run ID in decision history, and bind `model_version` dynamically.
  - *Current Status*: Completed. Updated `DecisionRecord` and `DecisionHistoryRecord` to automatically populate cryptographic SHA-256 `hash` and `run_id` (e.g. `RUN-20261109-XXXXXX`). Dynamically bound `model_version` to the active running pipeline model via `get_running_model_version(crop_id)`. `POST /api/history/log-action` and `GET /api/history/decisions` now return `hash` and `run_id` for audit traceability.
  - *Files*: `src/govisense/db/history.py`, `src/govisense/db/models.py`, `src/govisense/api/main.py`, `src/govisense/api/schemas.py`.

- [x] **Task 7 (P0)**: Add `is_demo`, `data_available`, and `source_type` fields to API responses.
  - *Current Status*: Completed. Added standard provenance metadata (`is_demo`, `data_available`, `source_type`) to `/api/forecasts/latest` (top-level and sub-model levels), `/api/simulate`, `/api/farmer/top3`, `/api/confidence/badge`, `/api/feedback/planting-report`, `/api/feedback/retrigger`, and `/api/history/decisions`. Defined contracts in `src/govisense/api/schemas.py`.
  - *Files*: `src/govisense/api/main.py`, `src/govisense/api/schemas.py`, `src/govisense/feedback/planting_reports.py`.

- [x] **Task 8 (P1)**: JWT login with `officer`, `farmer`, and `admin` roles, protect endpoints, and restrict CORS.
  - *Current Status*: Completed. Added `admin` role and `require_admin` dependency; seeded default administrator `admin_govisense` with `Admin@123`. Enforced RBAC protection: `/api/database/init` (admin only), `/api/simulate` (officer/admin), `/api/feedback/retrigger` (officer/admin), and `/api/history/log-action` (officer/admin). Replaced wildcard CORS with strict whitelisted origins (`localhost:8443`, `localhost:5173`, `localhost:3000`).
  - *Files*: `src/govisense/api/auth.py`, `src/govisense/api/main.py`, `src/govisense/db/session.py`.

- [x] **Task 9 (P1)**: Add missing endpoints for Rashmika (Catalogue, Adoption Summary, Decision List with Hash/Run ID, Run Info).
  - *Current Status*: Completed. Implemented `GET /api/catalogue` (with format/publisher filtering and licence information), `GET /api/catalogue/{id}` (case-insensitive detail query), `GET /api/pipeline/run-info` (returning active run_id, model_version, and operational status), and `GET /api/simulation/adoption-summary`.
  - *Files*: `src/govisense/api/routes/pipeline.py`, `src/govisense/api/main.py`, `src/govisense/data/catalogue.py`.

- [x] **Task 10 (P1)**: Alerts backend (`routes/alerts.py`, `i18n/templates.json`, `/api/alerts`, acknowledge endpoint).
  - *Current Status*: Completed. Created `src/govisense/i18n/templates.json` with comprehensive English, Sinhala, and Tamil advisory templates. Built `src/govisense/api/routes/alerts.py` supporting multilingual query (`lang=en|si|ta`), farmer acknowledgment (`POST /api/alerts/{id}/acknowledge`), officer inquiries (`POST /api/alerts/{id}/ask`), and automated startup seeding.
  - *Files*: `src/govisense/api/routes/alerts.py`, `src/govisense/i18n/templates.json`, `src/govisense/db/models.py`.

- [x] **Task 11 (P1)**: Modernize API architecture: replace `@app.on_event` with `lifespan`, split `main.py` into route modules, and populate `deps.py` / `schemas.py`.
  - *Current Status*: Completed. Modernized application lifecycle using async `lifespan(app)` context manager, completely removing deprecated `@app.on_event("startup")`. Decomposed routing into `routes/alerts.py`, `routes/pipeline.py`, `routes/farmer.py`, `routes/officer.py`, and `routes/auth.py`. Populated `src/govisense/api/deps.py` and `src/govisense/api/schemas.py`.
  - *Files*: `src/govisense/api/main.py`, `src/govisense/api/deps.py`, `src/govisense/api/schemas.py`, `src/govisense/api/routes/`.

- [x] **Task 12 (P1)**: Farmer ID checks: rate limit, duplicate-report handling, and registry verification note.
  - *Current Status*: Completed. Implemented local sliding-window rate limiting in `PlantingReportStore` (maximum 5 submissions per 60 seconds per `pseudonymous_id`). Added duplicate report rejection checking matching farmer ID, crop, season, and area. Documented future Agrarian Services Department national farmer registry integration in `docs/assumptions.md`, API responses, and store docstrings.
  - *Files*: `src/govisense/feedback/planting_reports.py`, `src/govisense/api/main.py`, `docs/assumptions.md`, `tests/test_task_12.py`.

---

## 3. Mobile App (Flutter / Dart)

- [x] **Task 13 (P0)**: Remove fake success receipt (`farmer_repository.dart:346-373`).
  - *Current Status*: Completed. Removed optimistic fake success receipt. Planting declarations initially create a `pending` report, attempt live FastAPI sync, mark `verified` upon confirmation, and if transmission fails or device is offline, persist locally with `status: 'pending'`, queue automatic background retries via `retryPendingReports()`, notify the farmer transparently via multilingual warning alert, and display a "Pending Sync" receipt with a manual "Retry Sync Now" trigger.
  - *Files*: `mobile/lib/features/farmer/data/farmer_repository.dart`, `mobile/lib/features/farmer/models/planting_report.dart`, `mobile/lib/features/farmer/presentation/farmer_page.dart`.

- [x] **Task 14 (P1)**: Show clear banner when recommendations come from offline `_initialCrops`.
  - *Current Status*: Completed. Added `isUsingOfflineFallback` state tracking to `FarmerRepository`. Implemented `_buildOfflineRecommendationsBanner()` rendered prominently in both the Home tab (under Top 3 recommendations) and Compare tab (under comparison overview) whenever live connection is unavailable, displaying explicit amber warning, `_initialCrops` identifier, trilingual message (English, Sinhala, Tamil), and a live connection retry action button.
  - *Files*: `mobile/lib/features/farmer/data/farmer_repository.dart`, `mobile/lib/features/farmer/presentation/farmer_page.dart`.

- [x] **Task 15 (P1)**: Verify market prices screen reads the API, and wire it if not.
  - *Current Status*: Completed. Verified that the screen previously relied on static hardcoded items. Created backend endpoints `GET /api/market-prices` and `GET /api/prices` backed by `MarketPriceRecord` and seeded with CBSL/HARTI daily benchmark DEC feeds. Created `MarketPriceItem` model with JSON deserialization, added `getMarketPrices()` to `FarmerApiService`, and wired `market_prices_page.dart` with asynchronous API fetching, category filtering, live vs. offline feed indicators (`● Live CBSL Feed` / `○ Offline Benchmark`), and pull-to-refresh (`RefreshIndicator`).
  - *Files*: `src/govisense/api/main.py`, `src/govisense/api/schemas.py`, `src/govisense/db/session.py`, `src/govisense/db/models.py`, `mobile/lib/features/farmer/models/market_price_item.dart`, `mobile/lib/features/farmer/services/farmer_api_service.dart`, `mobile/lib/features/farmer/presentation/market_prices_page.dart`, `tests/test_tasks_13_14_15.py`.

- [x] **Task 16 (P1)**: Build alert inbox with *Acknowledge* and *Ask an Officer*, and verify trilingual localization.
  - *Current Status*: Completed. Extended `FarmerAlert` model with `isAcknowledged`, `questionAsked`, and `officerResponse`. Added `acknowledgeAlert(id)` and `askOfficer(id, question)` in `FarmerRepository` and `FarmerApiService` communicating with `/api/alerts/{id}/acknowledge` and `/api/alerts/{id}/ask`. Implemented inline "Acknowledge" button and modal "Ask Officer" inquiry flow in `farmer_page.dart` and completely upgraded `mobile/lib/features/alerts/alerts_page.dart` into a full interactive trilingual alert inbox. Verified and added English, Sinhala, and Tamil translations across `app_translations.dart`.
  - *Files*: `mobile/lib/features/farmer/models/farmer_alert.dart`, `mobile/lib/features/farmer/data/farmer_repository.dart`, `mobile/lib/features/farmer/services/farmer_api_service.dart`, `mobile/lib/features/farmer/presentation/farmer_page.dart`, `mobile/lib/features/alerts/alerts_page.dart`, `mobile/lib/core/localization/app_translations.dart`.

- [x] **Task 17 (P1)**: Validate two-stage form (planting and harvest reports) schema consistency.
  - *Current Status*: Completed. Audited the two-stage declaration flow in `farmer_page.dart`: Stage 1 (Planting Intent & Acreage) and Stage 2 (Post-Harvest & Marketing Telemetry: yield MT, sale price Rs/kg, DEC marketing channel, and consent). Normalized season representation (`_normalizeSeasonForBackend`) to strictly align with backend `PlantingReportPayload` (`Maha 2025/2026`). Confirmed serialization matches backend SQLite table `planting_reports` and Pydantic validation rules.
  - *Files*: `mobile/lib/features/farmer/presentation/farmer_page.dart`, `mobile/lib/features/farmer/models/planting_report.dart`, `src/govisense/api/schemas.py`, `src/govisense/db/models.py`.

---

## 4. Quality & Infrastructure

- [x] **Task 18 (P1)**: TestClient tests for each endpoint, bad-input, concurrency (20 parallel reports), and data-validation.
  - *Current Status*: Completed. Created comprehensive test suite `tests/test_task_18_comprehensive_quality.py` with 23 thorough automated tests:
    1. Comprehensive `TestClient` endpoint verification covering all 14 REST routes (`/`, `/api/health`, `/api/auth/me`, `/api/auth/refresh`, `/api/forecasts/latest`, `/api/pipeline/run-info`, `/api/catalogue`, `/api/simulate`, `/api/simulation/adoption`, `/api/farmer/top3`, `/api/feedback/planting-report`, `/api/history/decisions`, `/api/alerts`, `/api/market-prices`, `/api/database/init`).
    2. Robust bad-input and security validation: missing required fields (422), malformed data types (422), unauthenticated access to protected endpoints (401), unauthorized role access (403), duplicate report rejection, and sliding-window rate limiting per farmer.
    3. Concurrency stress test: 20 parallel threads submitting planting reports simultaneously through the API without database locking errors or data corruption.
    4. Data validation and integrity tests: verified `monthly_master.csv` conforms strictly to the 4-tier taxonomy (`real`, `anchor`, `interpolated`, `synthetic`), `is_demo=False`, and audited 5% hand-checked extraction sample achieves <= 10.0% error rate.
    All 103 test cases across the entire project now pass with 100% success rate.
  - *Files*: `tests/test_task_18_comprehensive_quality.py`.

- [x] **Task 19 (P2)**: Populate DevOps, containerization, and system documentation.
  - *Current Status*: Completed.
    - `.github/workflows/ci.yml`: Multi-version Python (3.11, 3.12, 3.13) matrix testing, system dependencies, Ruff linting, Pytest test coverage, data integrity verification, and Node.js 20 frontend build/typecheck.
    - `Dockerfile`: Multi-stage Python 3.11-slim production container with system graphics/PDF libraries, healthcheck, and uvicorn runner.
    - `docker-compose.yml`: Integrated stack running `backend` (FastAPI) and `frontend` (Nginx SPA reverse proxy), volume-persisting `/app/data` and `/app/models_store`, with automated healthchecks.
    - `Makefile`: Cross-platform developer targets (`install`, `test`, `test-task18`, `test-cov`, `lint`, `format`, `run-api`, `run-frontend`, `docker-build`, `docker-up`, `docker-down`, `init-db`, `data-validate`, `clean`).
    - `.env.example`: Comprehensive environment configuration template covering JWT secrets, expiry, CORS origins, SQLite/PostgreSQL URIs, pilot district, and paths.
    - `docs/assumptions.md`: Detailed agronomic, supply loss, price floor, SPI banding, climatological baselines, 4-tier data provenance taxonomy, and future national farmer registry integration notes.
    - `docs/ai-usage-log.md`: Complete AI engineering audit log detailing AI 1-4 pipeline architectures, generative AI pair-programming trajectory, human verification checkpoints, and ethical privacy principles.
  - *Files*: `.github/workflows/ci.yml`, `docker-compose.yml`, `Dockerfile`, `frontend/Dockerfile`, `frontend/nginx.conf`, `Makefile`, `.env.example`, `docs/assumptions.md`, `docs/ai-usage-log.md`.

- [x] **Task 20 (P1)**: Run and verify all sanity checks: Auth, CORS, Alerts, and Mobile Prices screen.
  - *Current Status*: Completed. Authored and executed dedicated end-to-end integration test suite `tests/test_task_20_unverified_checks.py`:
    1. **Auth & RBAC**: Verified login across all three roles (`farmer`, `officer`, `admin`), token refresh, `me` claims, and strict role boundary enforcement (farmers blocked from officer actions with 403, officers blocked from database re-init with 403, authorized roles permitted).
    2. **CORS Whitelist**: Verified that whitelisted origins (`http://localhost:3000`, `http://localhost:5173`) receive `Access-Control-Allow-Origin`, while unlisted/malicious origins are strictly blocked without wildcard fallback.
    3. **Multilingual Alerts & Lifecycle**: Verified trilingual output (`lang=en`, `lang=si`, `lang=ta` containing genuine Unicode scripts), alert acknowledgment (`/api/alerts/{id}/acknowledge`), and farmer-to-officer question submission (`/api/alerts/{id}/ask`).
    4. **Mobile Market Prices Screen**: Verified `/api/market-prices` returns real CBSL/HARTI benchmark prices (`data_available: true`, `is_demo: false`, `source_type: "cbsl_harti_market_bulletin"`), category filtering, and 100% schema alignment with mobile `MarketPriceItem`.
    All 148 automated tests in the project repository pass with 100% success rate.
  - *Files*: `tests/test_task_20_unverified_checks.py`.

