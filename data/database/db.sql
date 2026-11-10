-- =====================================================================
-- GoviSense  -  Complete database  (PostgreSQL 14+)
-- =====================================================================
-- Normal form : Third Normal Form (3NF)
-- Contents    : 1. Reference (lookup) tables      5. Views
--               2. Core tables                    6. Indexes
--               3. Functions                      7. Seed data
--               4. Triggers
--
-- Usage       : createdb govisense && psql -d govisense -f db.sql
--               (run against an EMPTY database)
--
-- Derived from the live SQLite file data/database/govisense.db and the
-- ORM in src/govisense/db/models.py, then normalised.  Main 3NF changes:
--
--  * Repeated text codes (crop, district, season, role, irrigation,
--    sale channel, alert type, model name...) -> lookup tables + FKs.
--  * Translation columns (title_en/si/ta, crop_en/si/ta...) -> *_translations
--    tables (one row per language).
--  * Derived values removed and exposed through views / functions instead:
--      forecast_snapshots.spi_label / confidence_badge / season /
--      actual_price / actual_production, monthly_data.yield_mt_ha,
--      market_prices trend_pct / is_up / is_stable / *_display,
--      planting_reports.followed_recommendation / district / soil_ph,
--      harvest_reports.pseudonymous_id / crop_id / season,
--      decision_history.model_version / data_version / assumptions
--      (now reached through run_id -> runs),
--      alert_status.acknowledged (= acknowledged_at IS NOT NULL).
--  * Duplicated columns dropped: users.id / hashed_password,
--    alert_status.farmer_id, planting_reports.harvest_outcome_mt /
--    sale_price_rs_kg / sale_channel (they live in harvest_reports).
--  * JSON arrays (flags, problems) -> child tables (1NF).  JSONB is kept
--    only for free-form documents (assumptions, params, details).
-- =====================================================================

BEGIN;

-- Needed as a column default, so it is defined before the tables.
-- Run id format used by the API:  RUN-YYYYMMDD-XXXXXX
CREATE FUNCTION generate_run_id() RETURNS VARCHAR(36)
LANGUAGE sql VOLATILE AS $$
    SELECT 'RUN-' || to_char(now() AT TIME ZONE 'UTC', 'YYYYMMDD') || '-' ||
           upper(substr(md5(gen_random_uuid()::text), 1, 6));
$$;

-- =====================================================================
-- 1. REFERENCE / LOOKUP TABLES
-- =====================================================================

CREATE TABLE roles (
    role_code    VARCHAR(20) PRIMARY KEY,
    description  VARCHAR(200) NOT NULL
);

CREATE TABLE languages (
    lang_code    VARCHAR(10) PRIMARY KEY,           -- en | si | ta
    name         VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE districts (
    district_id  SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name         VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE ds_divisions (                         -- Divisional Secretariats
    division_id  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    district_id  SMALLINT NOT NULL REFERENCES districts(district_id),
    name         VARCHAR(100) NOT NULL,
    UNIQUE (district_id, name),
    UNIQUE (division_id, district_id)               -- target of composite FKs
);

CREATE TABLE crop_categories (
    category_code VARCHAR(30) PRIMARY KEY,
    name          VARCHAR(60) NOT NULL
);

CREATE TABLE crops (
    crop_id         VARCHAR(50) PRIMARY KEY,         -- e.g. big_onion
    scientific_name VARCHAR(100),
    category_code   VARCHAR(30) NOT NULL REFERENCES crop_categories(category_code)
);

CREATE TABLE crop_translations (
    crop_id      VARCHAR(50) NOT NULL REFERENCES crops(crop_id) ON DELETE CASCADE,
    lang_code    VARCHAR(10) NOT NULL REFERENCES languages(lang_code),
    name         VARCHAR(128) NOT NULL,
    PRIMARY KEY (crop_id, lang_code)
);

CREATE TABLE seasons (
    season_id    SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    label        VARCHAR(50) NOT NULL UNIQUE,        -- 'Maha 2025/2026'
    season_type  VARCHAR(10) NOT NULL CHECK (season_type IN ('Maha','Yala')),
    start_date   DATE NOT NULL,
    end_date     DATE NOT NULL,
    CHECK (end_date > start_date),
    EXCLUDE USING gist (daterange(start_date, end_date, '[]') WITH &&)  -- no overlaps
);

CREATE TABLE irrigation_types (
    irrigation_code VARCHAR(30) PRIMARY KEY,
    name            VARCHAR(60) NOT NULL,
    water_class     VARCHAR(10) NOT NULL CHECK (water_class IN ('rainfed','irrigated'))
);

CREATE TABLE soil_types (
    soil_code    VARCHAR(30) PRIMARY KEY,
    name         VARCHAR(60) NOT NULL
);

CREATE TABLE sale_channels (
    channel_code VARCHAR(30) PRIMARY KEY,
    name         VARCHAR(80) NOT NULL
);

CREATE TABLE data_source_types (                    -- 4-tier provenance taxonomy
    source_type  VARCHAR(20) PRIMARY KEY,
    description  VARCHAR(200) NOT NULL,
    is_demo      BOOLEAN NOT NULL
);

CREATE TABLE data_quality_levels (
    quality_code VARCHAR(30) PRIMARY KEY,
    description  VARCHAR(200) NOT NULL
);

CREATE TABLE alert_types (
    type_code    VARCHAR(30) PRIMARY KEY,
    description  VARCHAR(200) NOT NULL
);

CREATE TABLE severity_levels (
    severity_code VARCHAR(20) PRIMARY KEY,
    rank          SMALLINT NOT NULL UNIQUE
);

CREATE TABLE spi_bands (                            -- Supply Pressure Index bands
    band_code    VARCHAR(20) PRIMARY KEY,           -- label shown to users
    min_ratio    NUMERIC(6,3),                      -- inclusive, NULL = -infinity
    max_ratio    NUMERIC(6,3)                       -- exclusive, NULL = +infinity
);

CREATE TABLE confidence_levels (
    level_code   VARCHAR(10) PRIMARY KEY,           -- high | medium | low
    min_score    NUMERIC(5,1) NOT NULL UNIQUE       -- inclusive lower bound (0-100)
);

CREATE TABLE decision_actions (
    action_code  VARCHAR(50) PRIMARY KEY,
    description  VARCHAR(200) NOT NULL
);

CREATE TABLE forecast_models (
    model_name   VARCHAR(60) PRIMARY KEY,
    model_kind   VARCHAR(12) NOT NULL CHECK (model_kind IN ('price','supply','baseline','component')),
    is_baseline  BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE market_centers (                       -- Dedicated Economic Centres
    center_id    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name         VARCHAR(128) NOT NULL UNIQUE,
    district_id  SMALLINT REFERENCES districts(district_id)
);

CREATE TABLE market_center_translations (
    center_id    INTEGER NOT NULL REFERENCES market_centers(center_id) ON DELETE CASCADE,
    lang_code    VARCHAR(10) NOT NULL REFERENCES languages(lang_code),
    name         VARCHAR(128) NOT NULL,
    PRIMARY KEY (center_id, lang_code)
);

CREATE TABLE officer_designations (
    designation_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name           VARCHAR(80) NOT NULL UNIQUE
);

-- =====================================================================
-- 2. CORE TABLES
-- =====================================================================

-- ---- Identity / people ----------------------------------------------

CREATE TABLE officers (
    officer_id     VARCHAR(50) PRIMARY KEY,
    name           VARCHAR(100) NOT NULL,
    district_id    SMALLINT NOT NULL REFERENCES districts(district_id),
    division_id    INTEGER,
    designation_id SMALLINT NOT NULL REFERENCES officer_designations(designation_id),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    FOREIGN KEY (division_id, district_id) REFERENCES ds_divisions(division_id, district_id)
);

CREATE TABLE farmer_profiles (
    pseudonymous_id VARCHAR(50) PRIMARY KEY,         -- no real identity stored
    district_id     SMALLINT NOT NULL REFERENCES districts(district_id),
    division_id     INTEGER,
    total_land_ha   NUMERIC(8,2) NOT NULL CHECK (total_land_ha > 0),
    irrigation_code VARCHAR(30) NOT NULL REFERENCES irrigation_types(irrigation_code),
    soil_code       VARCHAR(30) REFERENCES soil_types(soil_code),
    soil_ph         NUMERIC(3,1) CHECK (soil_ph BETWEEN 0 AND 14),
    consent_given   BOOLEAN NOT NULL,
    consent_at      TIMESTAMPTZ NOT NULL,
    lang_code       VARCHAR(10) NOT NULL REFERENCES languages(lang_code),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    FOREIGN KEY (division_id, district_id) REFERENCES ds_divisions(division_id, district_id)
);

CREATE TABLE users (
    user_id         VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    username        VARCHAR(50) NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    role_code       VARCHAR(20) NOT NULL REFERENCES roles(role_code),
    pseudonymous_id VARCHAR(50) UNIQUE REFERENCES farmer_profiles(pseudonymous_id),
    officer_id      VARCHAR(50) UNIQUE REFERENCES officers(officer_id),
    full_name       VARCHAR(128),
    phone_number    VARCHAR(32),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_login      TIMESTAMPTZ,
    CONSTRAINT chk_user_role_link CHECK (
        (role_code = 'farmer'  AND pseudonymous_id IS NOT NULL AND officer_id IS NULL) OR
        (role_code = 'officer' AND officer_id IS NOT NULL AND pseudonymous_id IS NULL) OR
        (role_code = 'admin'   AND pseudonymous_id IS NULL)
    )
);

-- ---- Data provenance & pipeline runs --------------------------------

CREATE TABLE data_catalogue (
    dataset_id     VARCHAR(50) PRIMARY KEY,
    title          VARCHAR(150) NOT NULL,
    publisher      VARCHAR(100) NOT NULL,
    source_url     VARCHAR(255),
    licence        VARCHAR(100) NOT NULL,
    date_retrieved DATE,
    temporal_range VARCHAR(50),
    is_primary     BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE runs (                                 -- one row per model/pipeline run
    run_id        VARCHAR(36) PRIMARY KEY DEFAULT generate_run_id(),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    trigger_type  VARCHAR(30) NOT NULL
                  CHECK (trigger_type IN ('scheduled','manual','retrigger_feedback','test_audit','api')),
    model_version VARCHAR(100) NOT NULL,
    data_version  VARCHAR(100) NOT NULL,
    assumptions   JSONB NOT NULL DEFAULT '{}'::jsonb,
    git_commit    VARCHAR(40)
);

CREATE TABLE monthly_data (
    id                       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    crop_id                  VARCHAR(50) NOT NULL REFERENCES crops(crop_id),
    district_id              SMALLINT NOT NULL REFERENCES districts(district_id),
    month                    DATE NOT NULL CHECK (EXTRACT(DAY FROM month) = 1),
    planted_area_ha          DOUBLE PRECISION CHECK (planted_area_ha   >= 0),
    harvested_area_ha        DOUBLE PRECISION CHECK (harvested_area_ha >= 0),
    production_mt            DOUBLE PRECISION CHECK (production_mt     >= 0),
    wholesale_price_rs_kg    DOUBLE PRECISION CHECK (wholesale_price_rs_kg >= 0),
    retail_price_rs_kg       DOUBLE PRECISION CHECK (retail_price_rs_kg    >= 0),
    farmgate_price_rs_kg     DOUBLE PRECISION CHECK (farmgate_price_rs_kg  >= 0),
    imports_mt               DOUBLE PRECISION CHECK (imports_mt >= 0),
    weather_rainfall_anomaly DOUBLE PRECISION,
    source_type              VARCHAR(20) NOT NULL REFERENCES data_source_types(source_type),
    dataset_id               VARCHAR(50) REFERENCES data_catalogue(dataset_id),
    CONSTRAINT uq_crop_district_month UNIQUE (crop_id, district_id, month)
);

CREATE TABLE market_prices (                        -- daily DEC price bulletins
    price_id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    crop_id         VARCHAR(50) NOT NULL REFERENCES crops(crop_id),
    center_id       INTEGER NOT NULL REFERENCES market_centers(center_id),
    price_date      DATE NOT NULL,
    wholesale_price NUMERIC(10,2) CHECK (wholesale_price >= 0),
    retail_price    NUMERIC(10,2) CHECK (retail_price    >= 0),
    dataset_id      VARCHAR(50) REFERENCES data_catalogue(dataset_id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_price_crop_center_date UNIQUE (crop_id, center_id, price_date),
    CONSTRAINT chk_price_present CHECK (wholesale_price IS NOT NULL OR retail_price IS NOT NULL)
);

-- ---- Forecasting & evaluation ---------------------------------------

CREATE TABLE forecast_snapshots (
    forecast_id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id              VARCHAR(36) NOT NULL REFERENCES runs(run_id),
    crop_id             VARCHAR(50) NOT NULL REFERENCES crops(crop_id),
    district_id         SMALLINT NOT NULL REFERENCES districts(district_id),
    forecast_for_month  DATE NOT NULL CHECK (EXTRACT(DAY FROM forecast_for_month) = 1),
    horizon_months      SMALLINT NOT NULL CHECK (horizon_months >= 0),
    price_p10           DOUBLE PRECISION,
    price_p50           DOUBLE PRECISION NOT NULL,
    price_p90           DOUBLE PRECISION,
    retail_price_rs_kg  DOUBLE PRECISION,
    retail_price_method VARCHAR(50) NOT NULL,
    retail_price_p10    DOUBLE PRECISION,
    retail_price_p90    DOUBLE PRECISION,
    supply_low_mt       DOUBLE PRECISION,
    supply_mid_mt       DOUBLE PRECISION NOT NULL,
    supply_high_mt      DOUBLE PRECISION,
    demand_mt           DOUBLE PRECISION NOT NULL CHECK (demand_mt >= 0),
    spi_ratio_low       DOUBLE PRECISION,           -- model outputs (clipped), not
    spi_ratio_mid       DOUBLE PRECISION NOT NULL,  -- recomputable from supply/demand
    spi_ratio_high      DOUBLE PRECISION,
    spi_raw             DOUBLE PRECISION,
    spi_delta_mid       DOUBLE PRECISION,
    gap_best_mt         DOUBLE PRECISION,
    gap_worst_mt        DOUBLE PRECISION,
    decision_deadline   DATE,
    import_lead_weeks   SMALLINT NOT NULL DEFAULT 0 CHECK (import_lead_weeks >= 0),
    recommended_action  VARCHAR(50) REFERENCES decision_actions(action_code),
    price_model_used    VARCHAR(60) NOT NULL REFERENCES forecast_models(model_name),
    supply_model_used   VARCHAR(60) NOT NULL REFERENCES forecast_models(model_name),
    confidence_score    NUMERIC(5,1) NOT NULL CHECK (confidence_score BETWEEN 0 AND 100),
    data_quality        VARCHAR(30) NOT NULL REFERENCES data_quality_levels(quality_code),
    is_demo             BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_price_quantiles  CHECK (
        (price_p10 IS NULL OR price_p10 <= price_p50) AND
        (price_p90 IS NULL OR price_p50 <= price_p90)),
    CONSTRAINT chk_supply_quantiles CHECK (
        (supply_low_mt  IS NULL OR supply_low_mt  <= supply_mid_mt) AND
        (supply_high_mt IS NULL OR supply_mid_mt  <= supply_high_mt)),
    CONSTRAINT uq_forecast_run_crop_month UNIQUE (run_id, crop_id, district_id, forecast_for_month)
);

CREATE TABLE evaluation_results (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id           VARCHAR(36) NOT NULL REFERENCES runs(run_id),
    crop_id          VARCHAR(50) NOT NULL REFERENCES crops(crop_id),
    model_name       VARCHAR(60) NOT NULL REFERENCES forecast_models(model_name),
    metric_name      VARCHAR(50) NOT NULL,
    metric_value     DOUBLE PRECISION NOT NULL,
    baseline_name    VARCHAR(60) REFERENCES forecast_models(model_name),
    baseline_value   DOUBLE PRECISION,
    beat_baseline    BOOLEAN NOT NULL,
    evaluation_period VARCHAR(50),
    details          JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_baseline_pair CHECK ((baseline_name IS NULL) = (baseline_value IS NULL))
);

-- ---- Farmer feedback loop -------------------------------------------

CREATE TABLE planting_reports (
    report_id               VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    pseudonymous_id         VARCHAR(50) NOT NULL REFERENCES farmer_profiles(pseudonymous_id),
    crop_id                 VARCHAR(50) NOT NULL REFERENCES crops(crop_id),
    season_id               SMALLINT NOT NULL REFERENCES seasons(season_id),
    planned_area_ha         NUMERIC(8,2) NOT NULL CHECK (planned_area_ha > 0),
    actual_area_ha          NUMERIC(8,2) CHECK (actual_area_ha > 0),
    irrigation_code         VARCHAR(30) NOT NULL REFERENCES irrigation_types(irrigation_code),
    planting_date           DATE,
    expected_harvest_date   DATE,
    recommended_crop_shown  VARCHAR(50) REFERENCES crops(crop_id),
    reason                  TEXT,
    expected_price_rs_kg    NUMERIC(10,2) CHECK (expected_price_rs_kg >= 0),
    consent_given           BOOLEAN NOT NULL,
    app_version             VARCHAR(20) NOT NULL,
    lang_code               VARCHAR(10) NOT NULL REFERENCES languages(lang_code),
    source                  VARCHAR(30) NOT NULL DEFAULT 'farmer_report',
    notes                   TEXT,
    submitted_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_farmer_crop_season UNIQUE (pseudonymous_id, crop_id, season_id),
    CONSTRAINT chk_harvest_after_planting CHECK (
        planting_date IS NULL OR expected_harvest_date IS NULL OR expected_harvest_date > planting_date)
);

CREATE TABLE planting_report_flags (
    report_id    VARCHAR(36) NOT NULL REFERENCES planting_reports(report_id) ON DELETE CASCADE,
    flag_code    VARCHAR(50) NOT NULL,              -- e.g. FLAG_LARGE_HOLDING
    PRIMARY KEY (report_id, flag_code)
);

CREATE TABLE harvest_reports (
    harvest_id           VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    planting_report_id   VARCHAR(36) NOT NULL REFERENCES planting_reports(report_id),
    area_harvested_ha    NUMERIC(8,2) NOT NULL CHECK (area_harvested_ha > 0),
    harvest_date         DATE,
    harvest_quantity_kg  DOUBLE PRECISION NOT NULL CHECK (harvest_quantity_kg >= 0),
    loss_kg              DOUBLE PRECISION NOT NULL DEFAULT 0 CHECK (loss_kg >= 0),
    quantity_sold_kg     DOUBLE PRECISION NOT NULL DEFAULT 0 CHECK (quantity_sold_kg >= 0),
    quantity_stored_kg   DOUBLE PRECISION NOT NULL DEFAULT 0 CHECK (quantity_stored_kg >= 0),
    sale_price_rs_kg     NUMERIC(10,2) CHECK (sale_price_rs_kg >= 0),
    channel_code         VARCHAR(30) REFERENCES sale_channels(channel_code),
    sale_month           SMALLINT CHECK (sale_month BETWEEN 1 AND 12),
    notes                TEXT,
    submitted_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_disposition_le_harvest CHECK
        (quantity_sold_kg + loss_kg + quantity_stored_kg <= harvest_quantity_kg + 0.01)
);

CREATE TABLE harvest_report_flags (
    harvest_id   VARCHAR(36) NOT NULL REFERENCES harvest_reports(harvest_id) ON DELETE CASCADE,
    flag_code    VARCHAR(50) NOT NULL,
    PRIMARY KEY (harvest_id, flag_code)
);

CREATE TABLE harvest_report_problems (
    harvest_id   VARCHAR(36) NOT NULL REFERENCES harvest_reports(harvest_id) ON DELETE CASCADE,
    problem_code VARCHAR(50) NOT NULL,
    PRIMARY KEY (harvest_id, problem_code)
);

-- ---- Officer decisions (append-only audit trail) --------------------

CREATE TABLE decision_history (
    decision_id              VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    run_id                   VARCHAR(36) NOT NULL REFERENCES runs(run_id),
    record_hash              CHAR(64) NOT NULL UNIQUE,     -- SHA-256, set by trigger if absent
    crop_id                  VARCHAR(50) NOT NULL REFERENCES crops(crop_id),
    season_id                SMALLINT NOT NULL REFERENCES seasons(season_id),
    officer_id               VARCHAR(50) NOT NULL REFERENCES officers(officer_id),
    model_recommended_action VARCHAR(50) REFERENCES decision_actions(action_code),
    officer_response         VARCHAR(20) NOT NULL
                             CHECK (officer_response IN ('accepted','modified','rejected')),
    action_type              VARCHAR(50) NOT NULL REFERENCES decision_actions(action_code),
    quantity                 DOUBLE PRECISION NOT NULL CHECK (quantity >= 0),
    unit                     VARCHAR(20) NOT NULL,
    rationale                TEXT NOT NULL,
    is_demo                  BOOLEAN NOT NULL DEFAULT FALSE,
    data_available           BOOLEAN NOT NULL DEFAULT TRUE,
    source_type              VARCHAR(64) NOT NULL DEFAULT 'officer_audit_log',
    decided_at               TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---- Alerts ----------------------------------------------------------

CREATE TABLE alerts (
    alert_id     VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    crop_id      VARCHAR(50) NOT NULL REFERENCES crops(crop_id),
    district_id  SMALLINT NOT NULL REFERENCES districts(district_id),
    season_id    SMALLINT REFERENCES seasons(season_id),
    month        DATE CHECK (month IS NULL OR EXTRACT(DAY FROM month) = 1),
    type_code    VARCHAR(30) NOT NULL REFERENCES alert_types(type_code),
    severity     VARCHAR(20) NOT NULL REFERENCES severity_levels(severity_code),
    message_key  VARCHAR(100) NOT NULL,             -- key into i18n/templates.json
    params       JSONB NOT NULL DEFAULT '{}'::jsonb,
    run_id       VARCHAR(36) REFERENCES runs(run_id),
    target_role  VARCHAR(20) REFERENCES roles(role_code),   -- NULL = everyone
    status       VARCHAR(20) NOT NULL DEFAULT 'active'
                 CHECK (status IN ('active','resolved','expired')),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE alert_translations (
    alert_id     VARCHAR(36) NOT NULL REFERENCES alerts(alert_id) ON DELETE CASCADE,
    lang_code    VARCHAR(10) NOT NULL REFERENCES languages(lang_code),
    title        VARCHAR(255) NOT NULL,
    message      TEXT NOT NULL,
    PRIMARY KEY (alert_id, lang_code)
);

CREATE TABLE alert_status (                         -- per-user read / acknowledge state
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    alert_id         VARCHAR(36) NOT NULL REFERENCES alerts(alert_id) ON DELETE CASCADE,
    user_id          VARCHAR(36) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    read_at          TIMESTAMPTZ,
    acknowledged_at  TIMESTAMPTZ,
    CONSTRAINT uq_alert_user UNIQUE (alert_id, user_id),
    CONSTRAINT chk_ack_after_read CHECK (
        acknowledged_at IS NULL OR read_at IS NULL OR acknowledged_at >= read_at)
);

CREATE TABLE alert_questions (                      -- "Ask an Officer"
    question_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    alert_id          VARCHAR(36) NOT NULL REFERENCES alerts(alert_id) ON DELETE CASCADE,
    user_id           VARCHAR(36) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    question          TEXT NOT NULL,
    asked_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    answered_by       VARCHAR(50) REFERENCES officers(officer_id),
    officer_response  TEXT,
    responded_at      TIMESTAMPTZ,
    CONSTRAINT chk_response_pair CHECK (
        (officer_response IS NULL AND responded_at IS NULL AND answered_by IS NULL) OR
        (officer_response IS NOT NULL AND answered_by IS NOT NULL))
);

-- ---- Generic audit log ----------------------------------------------

CREATE TABLE audit_log (
    audit_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    table_name  VARCHAR(63) NOT NULL,
    record_pk   TEXT NOT NULL,
    action      VARCHAR(6) NOT NULL CHECK (action IN ('INSERT','UPDATE','DELETE')),
    changed_by  TEXT NOT NULL,
    old_data    JSONB,
    new_data    JSONB,
    changed_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =====================================================================
-- 3. FUNCTIONS
-- =====================================================================
-- (generate_run_id() is defined at the top of the file.)

-- Season that contains a calendar date (NULL if none is configured)
CREATE FUNCTION fn_season_for_date(p_date DATE) RETURNS SMALLINT
LANGUAGE sql STABLE AS $$
    SELECT season_id FROM seasons WHERE p_date BETWEEN start_date AND end_date LIMIT 1;
$$;

-- SPI ratio -> band label (Shortage / Balanced / Glut), driven by spi_bands
CREATE FUNCTION fn_spi_label(p_ratio DOUBLE PRECISION) RETURNS VARCHAR(20)
LANGUAGE sql STABLE AS $$
    SELECT band_code FROM spi_bands
    WHERE (min_ratio IS NULL OR p_ratio >= min_ratio)
      AND (max_ratio IS NULL OR p_ratio <  max_ratio)
    ORDER BY min_ratio NULLS FIRST
    LIMIT 1;
$$;

-- Confidence score (0-100) -> high / medium / low, driven by confidence_levels
CREATE FUNCTION fn_confidence_level(p_score NUMERIC) RETURNS VARCHAR(10)
LANGUAGE sql STABLE AS $$
    SELECT level_code FROM confidence_levels
    WHERE p_score >= min_score
    ORDER BY min_score DESC
    LIMIT 1;
$$;

-- Tamper-evident SHA-256 over the business content of a decision
CREATE FUNCTION compute_decision_hash(
    p_decision_id TEXT, p_run_id TEXT, p_crop_id TEXT, p_season_label TEXT,
    p_officer_id TEXT, p_response TEXT, p_action TEXT, p_quantity DOUBLE PRECISION,
    p_unit TEXT, p_rationale TEXT, p_decided_at TIMESTAMPTZ
) RETURNS CHAR(64)
LANGUAGE sql IMMUTABLE AS $$
    SELECT encode(sha256(convert_to(concat_ws('|',
        p_decision_id, p_run_id, p_crop_id, p_season_label, p_officer_id,
        p_response, p_action, p_quantity::text, p_unit, p_rationale,
        to_char(p_decided_at AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.US')
    ), 'UTF8')), 'hex')::char(64);
$$;

-- Area (ha) a farmer has already declared for a season
CREATE FUNCTION fn_farmer_season_area(p_pseudonymous_id TEXT, p_season_id SMALLINT)
RETURNS NUMERIC
LANGUAGE sql STABLE AS $$
    SELECT COALESCE(SUM(COALESCE(actual_area_ha, planned_area_ha)), 0)
    FROM planting_reports
    WHERE pseudonymous_id = p_pseudonymous_id AND season_id = p_season_id;
$$;

-- Alert text in the requested language, falling back to English
CREATE FUNCTION fn_alert_localized(p_alert_id TEXT, p_lang TEXT)
RETURNS TABLE (alert_id VARCHAR, lang_code VARCHAR, title VARCHAR, message TEXT)
LANGUAGE sql STABLE AS $$
    SELECT t.alert_id, t.lang_code, t.title, t.message
    FROM alert_translations t
    WHERE t.alert_id = p_alert_id AND t.lang_code IN (p_lang, 'en')
    ORDER BY (t.lang_code = p_lang) DESC
    LIMIT 1;
$$;

-- Adoption summary.  Honest by design: when no report carries a shown
-- recommendation, data_available = FALSE and the counts are NULL
-- (no hard-coded 64/24/12 figures).
CREATE FUNCTION fn_adoption_summary(p_season_label TEXT DEFAULT NULL, p_crop_id TEXT DEFAULT NULL)
RETURNS TABLE (
    data_available BOOLEAN, total_reports BIGINT, followed BIGINT,
    not_followed BIGINT, followed_pct NUMERIC, note TEXT)
LANGUAGE sql STABLE AS $$
    WITH r AS (
        SELECT pr.crop_id, pr.recommended_crop_shown
        FROM planting_reports pr
        JOIN seasons s ON s.season_id = pr.season_id
        WHERE pr.recommended_crop_shown IS NOT NULL
          AND (p_season_label IS NULL OR s.label = p_season_label)
          AND (p_crop_id      IS NULL OR pr.crop_id = p_crop_id)
    ), c AS (
        SELECT count(*) AS total,
               count(*) FILTER (WHERE crop_id =  recommended_crop_shown) AS yes,
               count(*) FILTER (WHERE crop_id <> recommended_crop_shown) AS no
        FROM r
    )
    SELECT c.total > 0,
           CASE WHEN c.total > 0 THEN c.total END,
           CASE WHEN c.total > 0 THEN c.yes   END,
           CASE WHEN c.total > 0 THEN c.no    END,
           CASE WHEN c.total > 0 THEN round(100.0 * c.yes / c.total, 1) END,
           CASE WHEN c.total > 0 THEN 'Computed from farmer planting reports'
                ELSE 'No planting reports with a shown recommendation yet' END
    FROM c;
$$;

-- Latest market-price feed in a language, with day-over-day trend
CREATE FUNCTION fn_market_prices_feed(p_lang TEXT DEFAULT 'en', p_category TEXT DEFAULT NULL)
RETURNS TABLE (
    crop_id VARCHAR, crop_name VARCHAR, category_code VARCHAR, market_center VARCHAR,
    wholesale_price NUMERIC, retail_price NUMERIC, price_date DATE,
    trend_pct NUMERIC, is_up BOOLEAN, is_stable BOOLEAN)
LANGUAGE sql STABLE AS $$
    WITH ranked AS (
        SELECT mp.*,
               LAG(mp.wholesale_price) OVER w AS prev_wholesale,
               ROW_NUMBER()            OVER (PARTITION BY mp.crop_id, mp.center_id
                                             ORDER BY mp.price_date DESC) AS rn
        FROM market_prices mp
        WINDOW w AS (PARTITION BY mp.crop_id, mp.center_id ORDER BY mp.price_date)
    ), latest AS (
        -- LAG must run over the full series, so filter to newest row afterwards
        SELECT * FROM ranked WHERE rn = 1
    )
    SELECT l.crop_id,
           COALESCE(ct.name, ce.name, l.crop_id)::varchar,
           c.category_code,
           COALESCE(mt.name, mc.name)::varchar,
           l.wholesale_price, l.retail_price, l.price_date,
           tp.pct,
           COALESCE(tp.pct >  0.5, FALSE),
           COALESCE(abs(tp.pct) <= 0.5, TRUE)
    FROM latest l
    JOIN crops c           ON c.crop_id   = l.crop_id
    JOIN market_centers mc ON mc.center_id = l.center_id
    LEFT JOIN crop_translations ct ON ct.crop_id = l.crop_id AND ct.lang_code = p_lang
    LEFT JOIN crop_translations ce ON ce.crop_id = l.crop_id AND ce.lang_code = 'en'
    LEFT JOIN market_center_translations mt
           ON mt.center_id = l.center_id AND mt.lang_code = p_lang
    CROSS JOIN LATERAL (
        SELECT CASE WHEN l.prev_wholesale > 0
                    THEN round((l.wholesale_price - l.prev_wholesale) / l.prev_wholesale * 100, 1)
               END AS pct) tp
    WHERE p_category IS NULL OR c.category_code = p_category
    ORDER BY c.category_code, 2, 4;
$$;

-- ---- trigger functions ----------------------------------------------

CREATE FUNCTION trg_set_updated_at() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at := now();
    RETURN NEW;
END $$;

CREATE FUNCTION trg_block_modification() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION '% on % is not allowed: table is append-only (audit/provenance)',
        TG_OP, TG_TABLE_NAME USING ERRCODE = 'GV403';
END $$;

CREATE FUNCTION trg_decision_hash() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE v_season TEXT;
BEGIN
    IF NEW.record_hash IS NULL OR NEW.record_hash = '' THEN
        SELECT label INTO v_season FROM seasons WHERE season_id = NEW.season_id;
        NEW.record_hash := compute_decision_hash(
            NEW.decision_id, NEW.run_id, NEW.crop_id, v_season, NEW.officer_id,
            NEW.officer_response, NEW.action_type, NEW.quantity, NEW.unit,
            NEW.rationale, NEW.decided_at);
    END IF;
    RETURN NEW;
END $$;

-- Task 12: max 5 submissions / 60 s per farmer
CREATE FUNCTION trg_planting_rate_limit() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE v_recent INTEGER;
BEGIN
    SELECT count(*) INTO v_recent FROM planting_reports
    WHERE pseudonymous_id = NEW.pseudonymous_id
      AND submitted_at > now() - interval '60 seconds';
    IF v_recent >= 5 THEN
        RAISE EXCEPTION 'Rate limit exceeded: max 5 planting reports per 60 seconds per farmer'
            USING ERRCODE = 'GV429';
    END IF;
    RETURN NEW;
END $$;

CREATE FUNCTION trg_planting_validate() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
    v_consent BOOLEAN;
    v_land    NUMERIC;
    v_other   NUMERIC;
BEGIN
    SELECT consent_given, total_land_ha INTO v_consent, v_land
    FROM farmer_profiles WHERE pseudonymous_id = NEW.pseudonymous_id;

    IF NOT COALESCE(v_consent, FALSE) OR NOT NEW.consent_given THEN
        RAISE EXCEPTION 'Planting report rejected: farmer consent not given'
            USING ERRCODE = 'GV451';
    END IF;

    SELECT COALESCE(SUM(COALESCE(actual_area_ha, planned_area_ha)), 0) INTO v_other
    FROM planting_reports
    WHERE pseudonymous_id = NEW.pseudonymous_id
      AND season_id = NEW.season_id
      AND report_id <> NEW.report_id;

    IF v_other + COALESCE(NEW.actual_area_ha, NEW.planned_area_ha) > v_land THEN
        RAISE EXCEPTION 'Declared area (% ha) exceeds registered land holding (% ha)',
            v_other + COALESCE(NEW.actual_area_ha, NEW.planned_area_ha), v_land
            USING ERRCODE = 'GV422';
    END IF;
    RETURN NEW;
END $$;

CREATE FUNCTION trg_harvest_validate() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE pr planting_reports%ROWTYPE;
BEGIN
    SELECT * INTO pr FROM planting_reports WHERE report_id = NEW.planting_report_id;
    IF NEW.harvest_date IS NOT NULL AND pr.planting_date IS NOT NULL
       AND NEW.harvest_date < pr.planting_date THEN
        RAISE EXCEPTION 'Harvest date % precedes planting date %', NEW.harvest_date, pr.planting_date
            USING ERRCODE = 'GV422';
    END IF;
    IF NEW.area_harvested_ha > COALESCE(pr.actual_area_ha, pr.planned_area_ha) * 1.10 THEN
        RAISE EXCEPTION 'Harvested area (% ha) exceeds planted area (% ha) by more than 10%%',
            NEW.area_harvested_ha, COALESCE(pr.actual_area_ha, pr.planned_area_ha)
            USING ERRCODE = 'GV422';
    END IF;
    RETURN NEW;
END $$;

-- Acknowledging an unread alert also marks it read
CREATE FUNCTION trg_alert_status_ack() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.acknowledged_at IS NOT NULL AND NEW.read_at IS NULL THEN
        NEW.read_at := NEW.acknowledged_at;
    END IF;
    RETURN NEW;
END $$;

-- Officer answers a question: stamp the time automatically
CREATE FUNCTION trg_alert_question_response() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.officer_response IS NOT NULL AND NEW.responded_at IS NULL THEN
        NEW.responded_at := now();
    END IF;
    RETURN NEW;
END $$;

-- Generic row audit.  TG_ARGV[0] = name of the primary-key column.
-- Set the actor with:  SET LOCAL govisense.current_user = '<username>';
CREATE FUNCTION trg_audit_row() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE v_row JSONB;
BEGIN
    v_row := CASE WHEN TG_OP = 'DELETE' THEN to_jsonb(OLD) ELSE to_jsonb(NEW) END;
    INSERT INTO audit_log (table_name, record_pk, action, changed_by, old_data, new_data)
    VALUES (TG_TABLE_NAME,
            v_row ->> TG_ARGV[0],
            TG_OP,
            COALESCE(NULLIF(current_setting('govisense.current_user', TRUE), ''), session_user),
            CASE WHEN TG_OP IN ('UPDATE','DELETE') THEN to_jsonb(OLD) - 'password_hash' END,
            CASE WHEN TG_OP IN ('INSERT','UPDATE') THEN to_jsonb(NEW) - 'password_hash' END);
    RETURN NULL;
END $$;

-- =====================================================================
-- 4. TRIGGERS
-- =====================================================================

-- updated_at maintenance
CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users            FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at();
CREATE TRIGGER trg_farmer_profiles_updated_at
    BEFORE UPDATE ON farmer_profiles  FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at();

-- Append-only audit/provenance tables
CREATE TRIGGER trg_decision_history_immutable
    BEFORE UPDATE OR DELETE ON decision_history
    FOR EACH ROW EXECUTE FUNCTION trg_block_modification();
CREATE TRIGGER trg_decision_history_no_truncate
    BEFORE TRUNCATE ON decision_history
    FOR EACH STATEMENT EXECUTE FUNCTION trg_block_modification();
CREATE TRIGGER trg_runs_immutable
    BEFORE UPDATE OR DELETE ON runs
    FOR EACH ROW EXECUTE FUNCTION trg_block_modification();
CREATE TRIGGER trg_audit_log_immutable
    BEFORE UPDATE OR DELETE ON audit_log
    FOR EACH ROW EXECUTE FUNCTION trg_block_modification();

-- Decision hash (only fills it when the application did not supply one)
CREATE TRIGGER trg_decision_history_hash
    BEFORE INSERT ON decision_history
    FOR EACH ROW EXECUTE FUNCTION trg_decision_hash();

-- Planting / harvest business rules
CREATE TRIGGER trg_planting_rate_limit
    BEFORE INSERT ON planting_reports
    FOR EACH ROW EXECUTE FUNCTION trg_planting_rate_limit();
CREATE TRIGGER trg_planting_validate
    BEFORE INSERT OR UPDATE ON planting_reports
    FOR EACH ROW EXECUTE FUNCTION trg_planting_validate();
CREATE TRIGGER trg_harvest_validate
    BEFORE INSERT OR UPDATE ON harvest_reports
    FOR EACH ROW EXECUTE FUNCTION trg_harvest_validate();

-- Alert workflow
CREATE TRIGGER trg_alert_status_ack
    BEFORE INSERT OR UPDATE ON alert_status
    FOR EACH ROW EXECUTE FUNCTION trg_alert_status_ack();
CREATE TRIGGER trg_alert_question_response
    BEFORE INSERT OR UPDATE ON alert_questions
    FOR EACH ROW EXECUTE FUNCTION trg_alert_question_response();

-- Row-level audit of sensitive tables
CREATE TRIGGER trg_audit_users
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION trg_audit_row('user_id');
CREATE TRIGGER trg_audit_farmer_profiles
    AFTER INSERT OR UPDATE OR DELETE ON farmer_profiles
    FOR EACH ROW EXECUTE FUNCTION trg_audit_row('pseudonymous_id');
CREATE TRIGGER trg_audit_planting_reports
    AFTER INSERT OR UPDATE OR DELETE ON planting_reports
    FOR EACH ROW EXECUTE FUNCTION trg_audit_row('report_id');
CREATE TRIGGER trg_audit_harvest_reports
    AFTER INSERT OR UPDATE OR DELETE ON harvest_reports
    FOR EACH ROW EXECUTE FUNCTION trg_audit_row('harvest_id');
CREATE TRIGGER trg_audit_alert_questions
    AFTER INSERT OR UPDATE OR DELETE ON alert_questions
    FOR EACH ROW EXECUTE FUNCTION trg_audit_row('question_id');

-- =====================================================================
-- 5. VIEWS
-- =====================================================================

-- Monthly data with derived yield
CREATE VIEW v_monthly_data AS
SELECT m.*, d.name AS district,
       CASE WHEN m.harvested_area_ha > 0
            THEN m.production_mt / m.harvested_area_ha END AS yield_mt_ha
FROM monthly_data m
JOIN districts d USING (district_id);

-- Newest forecast per crop / district / month with all derived fields
CREATE VIEW v_forecast_latest AS
SELECT DISTINCT ON (f.crop_id, f.district_id, f.forecast_for_month)
       f.*,
       d.name                              AS district,
       fn_season_for_date(f.forecast_for_month) AS season_id,
       fn_spi_label(f.spi_ratio_mid)       AS spi_label,
       fn_confidence_level(f.confidence_score) AS confidence_badge,
       md.wholesale_price_rs_kg            AS actual_price_rs_kg,
       md.production_mt                    AS actual_production_mt,
       r.model_version, r.data_version
FROM forecast_snapshots f
JOIN districts d USING (district_id)
JOIN runs r      USING (run_id)
LEFT JOIN monthly_data md
       ON md.crop_id = f.crop_id AND md.district_id = f.district_id
      AND md.month   = f.forecast_for_month
ORDER BY f.crop_id, f.district_id, f.forecast_for_month, f.created_at DESC;

-- Decision history exactly as the API returns it (hash + run id + versions)
CREATE VIEW v_decision_history AS
SELECT dh.decision_id, dh.record_hash AS hash, dh.run_id,
       r.model_version, r.data_version, r.assumptions,
       dh.crop_id, s.label AS season, dh.officer_id,
       dh.model_recommended_action, dh.officer_response, dh.action_type,
       dh.quantity, dh.unit, dh.rationale,
       dh.is_demo, dh.data_available, dh.source_type, dh.decided_at AS timestamp
FROM decision_history dh
JOIN runs r    USING (run_id)
JOIN seasons s USING (season_id);

-- Alerts in every language (English fallback)
CREATE VIEW v_alerts_localized AS
SELECT a.alert_id, a.crop_id, d.name AS district, a.type_code, a.severity,
       a.message_key, a.params, a.status, a.target_role, a.created_at,
       l.lang_code AS requested_lang, t.lang_code AS shown_lang, t.title, t.message
FROM alerts a
JOIN districts d USING (district_id)
CROSS JOIN languages l
CROSS JOIN LATERAL fn_alert_localized(a.alert_id, l.lang_code) t;

-- Per-user alert inbox state
CREATE VIEW v_alert_inbox AS
SELECT s.user_id, s.alert_id, s.read_at, s.acknowledged_at,
       (s.acknowledged_at IS NOT NULL) AS acknowledged,
       q.question, q.officer_response, q.responded_at
FROM alert_status s
LEFT JOIN LATERAL (
    SELECT question, officer_response, responded_at
    FROM alert_questions aq
    WHERE aq.alert_id = s.alert_id AND aq.user_id = s.user_id
    ORDER BY aq.asked_at DESC LIMIT 1) q ON TRUE;

-- Planting declaration + its harvest outcome (two-stage form), with context
CREATE VIEW v_planting_harvest AS
SELECT pr.report_id, pr.pseudonymous_id, fp.district_id, d.name AS district,
       pr.crop_id, s.label AS season, pr.planned_area_ha, pr.actual_area_ha,
       pr.irrigation_code, fp.soil_ph,
       pr.recommended_crop_shown,
       CASE WHEN pr.recommended_crop_shown IS NULL THEN NULL
            ELSE pr.crop_id = pr.recommended_crop_shown END AS followed_recommendation,
       hr.harvest_id, hr.harvest_quantity_kg, hr.harvest_quantity_kg / 1000.0 AS harvest_outcome_mt,
       hr.sale_price_rs_kg, hr.channel_code AS sale_channel, pr.submitted_at
FROM planting_reports pr
JOIN farmer_profiles fp USING (pseudonymous_id)
JOIN districts d        ON d.district_id = fp.district_id
JOIN seasons s          USING (season_id)
LEFT JOIN harvest_reports hr ON hr.planting_report_id = pr.report_id;

-- Latest price feed, English (use fn_market_prices_feed for si / ta)
CREATE VIEW v_market_prices_latest AS
SELECT * FROM fn_market_prices_feed('en');

-- =====================================================================
-- 6. INDEXES   (PK / UNIQUE constraints already create their own)
-- =====================================================================

-- Foreign keys & hot filters
CREATE INDEX ix_ds_divisions_district        ON ds_divisions (district_id);
CREATE INDEX ix_crops_category               ON crops (category_code);
CREATE INDEX ix_officers_district            ON officers (district_id);
CREATE INDEX ix_officers_division            ON officers (division_id);
CREATE INDEX ix_farmer_profiles_district     ON farmer_profiles (district_id);
CREATE INDEX ix_farmer_profiles_division     ON farmer_profiles (division_id);
CREATE UNIQUE INDEX ux_users_username_ci     ON users (lower(username));
CREATE INDEX ix_users_role                   ON users (role_code) WHERE is_active;

CREATE INDEX ix_runs_created_at              ON runs (created_at DESC);
CREATE INDEX ix_monthly_district_month       ON monthly_data (district_id, month);
CREATE INDEX ix_monthly_source               ON monthly_data (source_type);
CREATE INDEX ix_monthly_dataset              ON monthly_data (dataset_id);

CREATE INDEX ix_prices_crop_date             ON market_prices (crop_id, price_date DESC);
CREATE INDEX ix_prices_center_date           ON market_prices (center_id, price_date DESC);
CREATE INDEX ix_prices_date_brin             ON market_prices USING brin (price_date);

CREATE INDEX ix_forecast_crop_month          ON forecast_snapshots (crop_id, forecast_for_month);
CREATE INDEX ix_forecast_latest              ON forecast_snapshots (crop_id, district_id, forecast_for_month, created_at DESC);
CREATE INDEX ix_forecast_run                 ON forecast_snapshots (run_id);
CREATE INDEX ix_forecast_action              ON forecast_snapshots (recommended_action) WHERE recommended_action IS NOT NULL;
CREATE INDEX ix_forecast_demo                ON forecast_snapshots (is_demo) WHERE is_demo;

CREATE INDEX ix_eval_run                     ON evaluation_results (run_id);
CREATE INDEX ix_eval_crop_model              ON evaluation_results (crop_id, model_name);
CREATE INDEX ix_eval_created                 ON evaluation_results (created_at DESC);

CREATE INDEX ix_planting_farmer_time         ON planting_reports (pseudonymous_id, submitted_at DESC);  -- rate limit
CREATE INDEX ix_planting_crop_season         ON planting_reports (crop_id, season_id);
CREATE INDEX ix_planting_recommended         ON planting_reports (recommended_crop_shown) WHERE recommended_crop_shown IS NOT NULL;
CREATE INDEX ix_planting_submitted_brin      ON planting_reports USING brin (submitted_at);
CREATE INDEX ix_harvest_planting             ON harvest_reports (planting_report_id);
CREATE INDEX ix_harvest_channel              ON harvest_reports (channel_code);
CREATE INDEX ix_harvest_submitted_brin       ON harvest_reports USING brin (submitted_at);
CREATE INDEX ix_planting_flags_code          ON planting_report_flags (flag_code);
CREATE INDEX ix_harvest_flags_code           ON harvest_report_flags (flag_code);
CREATE INDEX ix_harvest_problems_code        ON harvest_report_problems (problem_code);

CREATE INDEX ix_decision_run                 ON decision_history (run_id);
CREATE INDEX ix_decision_officer_time        ON decision_history (officer_id, decided_at DESC);
CREATE INDEX ix_decision_crop_season         ON decision_history (crop_id, season_id);
CREATE INDEX ix_decision_action              ON decision_history (action_type);

CREATE INDEX ix_alerts_active_recent         ON alerts (created_at DESC) WHERE status = 'active';
CREATE INDEX ix_alerts_crop_district         ON alerts (crop_id, district_id);
CREATE INDEX ix_alerts_run                   ON alerts (run_id);
CREATE INDEX ix_alerts_params_gin            ON alerts USING gin (params);
CREATE INDEX ix_alert_status_user            ON alert_status (user_id);
CREATE INDEX ix_alert_status_unread          ON alert_status (user_id) WHERE read_at IS NULL;
CREATE INDEX ix_alert_questions_alert        ON alert_questions (alert_id);
CREATE INDEX ix_alert_questions_user         ON alert_questions (user_id);
CREATE INDEX ix_alert_questions_open         ON alert_questions (asked_at) WHERE officer_response IS NULL;

CREATE INDEX ix_audit_table_pk               ON audit_log (table_name, record_pk);
CREATE INDEX ix_audit_changed_brin           ON audit_log USING brin (changed_at);

-- =====================================================================
-- 7. SEED DATA  (reference data only - no users, no passwords)
-- =====================================================================

INSERT INTO roles VALUES
    ('farmer',  'Farmer using the mobile app'),
    ('officer', 'Agrarian / extension officer using the dashboard'),
    ('admin',   'System administrator');

INSERT INTO languages VALUES ('en','English'), ('si','Sinhala'), ('ta','Tamil');

INSERT INTO districts (name) VALUES
    ('Ampara'),('Anuradhapura'),('Badulla'),('Batticaloa'),('Colombo'),('Galle'),
    ('Gampaha'),('Hambantota'),('Jaffna'),('Kalutara'),('Kandy'),('Kegalle'),
    ('Kilinochchi'),('Kurunegala'),('Mannar'),('Matale'),('Matara'),('Monaragala'),
    ('Mullaitivu'),('Nuwara Eliya'),('Polonnaruwa'),('Puttalam'),('Ratnapura'),
    ('Trincomalee'),('Vavuniya');

INSERT INTO crop_categories VALUES
    ('vegetable','Vegetable'), ('spice','Spice / Condiment'),
    ('pulse','Pulse / Legume'), ('cereal','Cereal'), ('fruit','Fruit');

INSERT INTO crops VALUES
    ('big_onion', 'Allium cepa',          'vegetable'),
    ('chilli',    'Capsicum annuum',      'spice'),
    ('green_gram','Vigna radiata',        'pulse');

INSERT INTO crop_translations VALUES
    ('big_onion','en','Big Onion'),  ('big_onion','si','ලොකු ළූණු'), ('big_onion','ta','பெரிய வெங்காயம்'),
    ('chilli','en','Chilli'),        ('chilli','si','මිරිස්'),        ('chilli','ta','மிளகாய்'),
    ('green_gram','en','Green Gram'),('green_gram','si','මුං ඇට'),    ('green_gram','ta','பாசிப்பயறு');

INSERT INTO seasons (label, season_type, start_date, end_date) VALUES
    ('Maha 2024/2025','Maha','2024-10-01','2025-03-31'),
    ('Yala 2025',     'Yala','2025-04-01','2025-09-30'),
    ('Maha 2025/2026','Maha','2025-10-01','2026-03-31'),
    ('Yala 2026',     'Yala','2026-04-01','2026-09-30'),
    ('Maha 2026/2027','Maha','2026-10-01','2027-03-31');

INSERT INTO irrigation_types VALUES
    ('rainfed',          'Rainfed',          'rainfed'),
    ('minor_tank',       'Minor Tank',       'irrigated'),
    ('major_irrigation', 'Major Irrigation', 'irrigated'),
    ('agro_well',        'Agro-well',        'irrigated'),
    ('irrigated',        'Irrigated (unspecified)', 'irrigated');

INSERT INTO soil_types VALUES
    ('reddish_brown_earth','Reddish Brown Earth'),
    ('low_humic_gley','Low Humic Gley'),
    ('alluvial','Alluvial'),
    ('regosol','Regosol');

INSERT INTO sale_channels VALUES
    ('DEC_WHOLESALE','Dedicated Economic Centre (wholesale)'),
    ('DAMBULLA_DEC','Dambulla DEC'),
    ('KEPPETIPOLA_DEC','Keppetipola DEC'),
    ('ASC_BUYBACK','ASC Buy-Back'),
    ('LOCAL_COLLECTOR','Local Collector');

INSERT INTO data_source_types VALUES
    ('real',         'Directly extracted from an official publication', FALSE),
    ('anchor',       'Audited anchor value from an official source',    FALSE),
    ('interpolated', 'Interpolated between real observations',          FALSE),
    ('synthetic',    'Generated for demo / testing',                    TRUE);

INSERT INTO data_quality_levels VALUES
    ('verified',    'Checked against the source publication'),
    ('provisional', 'Not yet cross-checked'),
    ('stale',       'Older than the freshness threshold'),
    ('demo',        'Synthetic demo data');

INSERT INTO alert_types VALUES
    ('GLUT_WARNING',     'Forecast supply exceeds demand: price-crash risk'),
    ('SHORTAGE_WARNING', 'Forecast supply below demand: price-spike risk'),
    ('WEATHER',          'Weather / drainage advisory'),
    ('MARKET',           'Market price movement'),
    ('SYSTEM',           'System notice');

INSERT INTO severity_levels VALUES ('info',1), ('warning',2), ('critical',3);

-- SPI thresholds mirror the +/-15% band used in the simulation
INSERT INTO spi_bands VALUES
    ('Shortage', NULL, 0.850),
    ('Balanced', 0.850, 1.150),
    ('Glut',     1.150, NULL);

-- score = passed_rules / 5 * 100  ->  >=80 high (4+ rules), >=40 medium (2+)
INSERT INTO confidence_levels VALUES ('low',0), ('medium',40), ('high',80);

INSERT INTO decision_actions VALUES
    ('HOLD_STORAGE',       'Hold stock in storage'),
    ('PLANT_EXPANSION',    'Encourage additional planting'),
    ('RESTRICT_EXPANSION', 'Discourage additional planting'),
    ('IMPORT_LATER',       'Defer / delay imports'),
    ('IMPORT_NOW',         'Trigger imports now'),
    ('NO_ACTION',          'No intervention');

INSERT INTO forecast_models VALUES
    ('seasonal_naive',            'baseline',  TRUE),
    ('SARIMAX',                   'baseline',  TRUE),
    ('SARIMAX-LightGBM-ensemble', 'price',     FALSE),
    ('A1-HarvestVolume',          'supply',    FALSE),
    ('A1-Baseline-Lagged-SMA',    'baseline',  TRUE),
    ('A2 Price Forecast',         'component', FALSE),
    ('A3 Supply Forecast',        'component', FALSE);

INSERT INTO market_centers (name, district_id) VALUES
    ('Dambulla DEC',    (SELECT district_id FROM districts WHERE name = 'Matale')),
    ('Keppetipola DEC', (SELECT district_id FROM districts WHERE name = 'Badulla')),
    ('Meegoda DEC',     (SELECT district_id FROM districts WHERE name = 'Colombo')),
    ('Anuradhapura DEC',(SELECT district_id FROM districts WHERE name = 'Anuradhapura'));

INSERT INTO market_center_translations (center_id, lang_code, name)
SELECT c.center_id, v.lang, v.name
FROM market_centers c
JOIN (VALUES
    ('Dambulla DEC','en','Dambulla DEC'),       ('Dambulla DEC','si','දඹුල්ල ආර්ථික මධ්‍යස්ථානය'),   ('Dambulla DEC','ta','தம்புள்ளை பொருளாதார மையம்'),
    ('Keppetipola DEC','en','Keppetipola DEC'), ('Keppetipola DEC','si','කැප්පෙටිපොල ආර්ථික මධ්‍යස්ථානය'), ('Keppetipola DEC','ta','கெப்பெட்டிபொல பொருளாதார மையம்'),
    ('Meegoda DEC','en','Meegoda DEC'),         ('Meegoda DEC','si','මීගොඩ ආර්ථික මධ්‍යස්ථානය'),     ('Meegoda DEC','ta','மீகொட பொருளாதார மையம்'),
    ('Anuradhapura DEC','en','Anuradhapura DEC'),('Anuradhapura DEC','si','අනුරාධපුර ආර්ථික මධ්‍යස්ථානය'),('Anuradhapura DEC','ta','அனுராதபுரம் பொருளாதார மையம்')
) AS v(center, lang, name) ON v.center = c.name;

INSERT INTO officer_designations (name) VALUES
    ('Crop Forecaster'), ('Agricultural Extension Officer'), ('Agrarian Services Officer');

COMMIT;
