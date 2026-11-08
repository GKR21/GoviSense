"""
GoviSense Pydantic API Schemas & Data Contracts
Team DARKBITE · ModelX 2.0 Proposal Specification

Covers all Phase 0-5 API contracts and satisfies Rule 7:
Every API response that carries model output includes:
- run_id (UUID or RUN-xxxx)
- data_version (8-char hex)
- model_version (git_commit+param_hash)
- data_quality ('real' | 'partial' | 'demo_estimate' | 'no_data')
- is_demo (bool)
- served_model (str)
- assumptions_ref (str or URL)
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


# ===========================================================================
# Base Provenance & Audit Envelope (Rule 7)
# ===========================================================================

class ModelOutputProvenance(BaseModel):
    run_id: str = Field(..., description="Execution identifier in database runs table")
    data_version: str = Field(..., description="Cryptographic SHA-256 (first 8 hex) of training tables + row counts")
    model_version: str = Field(..., description="Git commit prefix + hash of fitted model parameters")
    data_quality: Literal["real", "partial", "demo_estimate", "no_data"] = Field(
        "real", description="Data provenance classification"
    )
    is_demo: bool = Field(False, description="True if synthetic/demo data is served")
    served_model: Optional[str] = Field(None, description="Actual model served (model or baseline)")
    assumptions_ref: str = Field("docs/assumptions.md", description="Reference to assumptions documentation")


# ===========================================================================
# 1. Health & Status
# ===========================================================================

class HealthResponse(BaseModel):
    status: str
    active_database: str
    dialect: str
    is_fallback: bool
    data_version: str
    model_version: str
    git_commit: str
    timestamp: str


# ===========================================================================
# 2. Authentication (/api/auth/login)
# ===========================================================================

class LoginRequest(BaseModel):
    username: str
    password: str


class AuthUser(BaseModel):
    user_id: str
    username: str
    role: Literal["officer", "farmer", "admin"]
    full_name: str
    district: Optional[str] = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUser


# ===========================================================================
# 3. Forecasts & Simulation (/api/forecasts/latest, /api/simulate, /api/gap)
# ===========================================================================

class CropScenarioItem(BaseModel):
    scenario: Literal["low", "mid", "high"]
    supply_mt: float
    demand_mt: float
    spi: float
    spi_raw: float
    spi_label: str


class MonthlyForecastItem(BaseModel):
    crop: str
    month: int
    year_month: str
    projected_demand_mt: float
    expected_harvest_mt: float
    supply_low_mt: float
    supply_mid_mt: float
    supply_high_mt: float
    spi_score: float
    spi_raw: float
    spi_label: str
    risk_level: str
    expected_wholesale_price_rs_kg: float
    price_p10_rs_kg: float
    price_p50_rs_kg: float
    price_p90_rs_kg: float
    retail_price_rs_kg: float
    retail_method: str
    confidence_badge: str
    scenarios: Optional[List[CropScenarioItem]] = None


class LatestForecastsResponse(ModelOutputProvenance):
    as_of: str
    forecasts: List[MonthlyForecastItem]


class SimulateRequest(BaseModel):
    crop: str = "big_onion"
    planted_area_ha: Optional[float] = None
    expected_yield_mt_per_ha: Optional[float] = None
    lead_time_weeks: Optional[int] = 7
    band_threshold_glut: Optional[float] = 1.2
    band_threshold_shortage: Optional[float] = 0.8
    loss_pct: Optional[float] = None


class SimulateResponse(ModelOutputProvenance):
    crop: str
    simulated_area_ha: float
    simulated_yield_mt_per_ha: float
    lead_time_weeks: int
    scenarios: List[CropScenarioItem]
    adjusted_spi: float
    adjusted_spi_label: str
    adjusted_risk_level: str


class GapActionOption(BaseModel):
    action_type: Literal["IMPORT_NOW", "IMPORT_LATER", "DELAY", "STORE", "RESTRICT_EXPANSION", "ENCOURAGE_PLANTING"]
    quantity_mt: float
    unit: str = "MT"
    target_timeline: str
    rationale: str
    deadline_date: Optional[str] = None
    days_left: Optional[int] = None
    fair_farmgate_floor_rs_kg: Optional[float] = None


class GapTimelineItem(BaseModel):
    crop: str
    year_month: str
    projected_demand_mt: float
    expected_supply_mt: float
    best_gap_mt: float
    worst_gap_mt: float
    spi_label: str
    decision_deadline: str
    lead_weeks: int
    days_left: int
    recommended_option: str
    all_options: List[GapActionOption]


class GapTimelineResponse(ModelOutputProvenance):
    items: List[GapTimelineItem]


# ===========================================================================
# 4. Farmer Advisory & Top 3 (/api/farmer/top3)
# ===========================================================================

class CropComparisonCard(BaseModel):
    crop_id: str
    name_en: str
    name_si: str
    suitability_score: float
    allocated_ha: float
    remaining_target_ha: float
    stop_rule_active: bool
    expected_profit_min_rs_ha: float
    expected_profit_max_rs_ha: float
    risk_level: str
    water_need: str
    planting_window: str
    harvest_period: str
    market_pressure_at_harvest: str
    confidence_badge: str
    price_range_12m: Dict[str, float]


class FarmerTop3Response(ModelOutputProvenance):
    farmer_id: str
    district: str
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None
    as_of: str
    recommended_crops: List[CropComparisonCard]


# ===========================================================================
# 5. Feedback Loop & Reports (/api/feedback/...)
# ===========================================================================

class PlantingReportRequest(BaseModel):
    pseudonymous_id: str
    crop: str
    district: str
    season: str
    irrigation_type: str
    planned_area_ha: float
    planted_area_ha: float
    planting_date: str
    expected_harvest_date: str
    recommended_crop_shown: Optional[str] = None
    followed_recommendation: Literal["yes", "partly", "no"]
    reason_for_decision: Optional[str] = None
    expected_price_rs_kg: Optional[float] = None
    soil_ph: Optional[float] = None
    app_version: Optional[str] = "2.0.0"
    consent: bool


class PlantingReportResponse(BaseModel):
    status: str
    report_id: str
    retrigger_recommended: bool
    flags: List[str] = []


class HarvestReportRequest(BaseModel):
    pseudonymous_id: str
    crop: str
    district: str
    season: str
    harvest_date: str
    area_harvested_ha: float
    quantity_harvested_mt: float
    loss_quantity_mt: float
    quantity_sold_mt: float
    quantity_stored_mt: float
    farmgate_price_rs_kg: float
    sale_market_or_buyer: Optional[str] = None
    sale_month: Optional[int] = None
    production_problems: Optional[List[str]] = None
    notes: Optional[str] = None
    consent: bool


class HarvestReportResponse(BaseModel):
    status: str
    report_id: str
    yield_mt_per_ha: float
    flags: List[str] = []


class RetriggerRequest(BaseModel):
    reason: Optional[str] = "Farmer reports threshold reached"
    triggered_by: Optional[str] = "feedback_loop"


class RetriggerResponse(ModelOutputProvenance):
    status: str
    new_run_id: str
    crops_refitted: List[str]
    timestamp: str


# ===========================================================================
# 6. Adoption Summary (/api/adoption/summary)
# ===========================================================================

class AdoptionScenarioResult(BaseModel):
    adoption_rate_pct: int
    total_supply_mt: float
    projected_demand_mt: float
    spi_score: float
    spi_label: str
    farmgate_price_rs_kg: float
    total_farmer_revenue_mil_rs: float
    price_crash_risk_pct: float
    market_stability: str


class AdoptionSummaryResponse(ModelOutputProvenance):
    crop: str
    season: str
    total_recommended_ha: float
    total_reported_ha: float
    compliance_rate_pct: float
    simulation_results: List[AdoptionScenarioResult]
    actual_vs_predicted: Dict[str, Any]


# ===========================================================================
# 7. Decision History & Audit (/api/history/...)
# ===========================================================================

class LogActionRequest(BaseModel):
    run_id: Optional[str] = None
    crop: str
    season: str
    officer_id: str
    action_type: Literal["IMPORT_NOW", "IMPORT_LATER", "DELAY", "STORE", "RESTRICT_EXPANSION", "ENCOURAGE_PLANTING"]
    quantity_mt: float
    rationale: str
    model_recommended_action: Optional[str] = None
    officer_response: Literal["accepted", "modified", "rejected"] = "accepted"


class LogActionResponse(BaseModel):
    status: str
    decision_id: str
    record_hash: str
    timestamp: str


class DecisionRecordItem(BaseModel):
    decision_id: str
    run_id: Optional[str]
    record_hash: str
    crop: str
    season: str
    officer_id: str
    action_type: str
    quantity_mt: float
    rationale: str
    model_recommended_action: Optional[str]
    officer_response: str
    data_version: str
    model_version: str
    created_at: str


class DecisionHistoryResponse(BaseModel):
    decisions: List[DecisionRecordItem]


# ===========================================================================
# 8. Pipeline Runs (/api/runs/{id})
# ===========================================================================

class PipelineRunDetailResponse(BaseModel):
    run_id: str
    created_at: str
    trigger: str
    model_version: str
    data_version: str
    git_commit: Optional[str]
    assumptions: Dict[str, Any]
    forecast_count: int
    decision_count: int


# ===========================================================================
# 9. Data Catalogue & Prices (/api/catalogue, /api/prices/latest)
# ===========================================================================

class CatalogueItem(BaseModel):
    dataset_id: str
    title: str
    publisher: str
    source_url: str
    licence: str
    date_retrieved: str
    temporal_range: str
    source_type: str = "real"
    age_days: Optional[int] = None
    is_outdated: bool = False


class CatalogueResponse(BaseModel):
    sources: List[CatalogueItem]


class CommodityPriceItem(BaseModel):
    crop: str
    market: str
    date: str
    wholesale_price_rs_kg: float
    retail_price_rs_kg: float
    data_quality: str = "real"
    is_outdated: bool = False


class LatestPricesResponse(BaseModel):
    as_of: str
    prices: List[CommodityPriceItem]


# ===========================================================================
# 10. Evaluation Scoreboard (/api/evaluation/scoreboard)
# ===========================================================================

class ModelScoreboardItem(BaseModel):
    crop: str
    module: str
    model_wape: Optional[float]
    baseline_wape: Optional[float]
    served_model: str
    beat_baseline: bool
    interval_80_coverage_pct: Optional[float]
    eval_points: int
    verdict: Literal["Usable", "Usable with limits", "Not usable"]


class EvaluationScoreboardResponse(ModelOutputProvenance):
    scoreboard: List[ModelScoreboardItem]


# ===========================================================================
# 11. Alerts & Notifications (/api/alerts)
# ===========================================================================

class AlertItem(BaseModel):
    alert_id: str
    crop: str
    alert_type: str
    severity: str
    title_en: str
    title_si: str
    title_ta: str
    message_en: str
    message_si: str
    message_ta: str
    days_left: Optional[int]
    created_at: str
    is_acknowledged: bool = False
    officer_notes: Optional[str] = None


class AlertsResponse(BaseModel):
    alerts: List[AlertItem]


class AlertAckRequest(BaseModel):
    officer_id: Optional[str] = None
    officer_notes: Optional[str] = None


class AskOfficerRequest(BaseModel):
    farmer_id: str
    question: str

