"""
GoviSense Pydantic Schemas & DTO Contracts
Provides request and response validation models with explicit data provenance:
- is_demo: bool (distinguishes live ground data from demo/mock pipelines)
- data_available: bool (explicit transparency when telemetry is unavailable)
- source_type: str (e.g. 'empirical_pipeline', 'officer_audit_log', 'agent_simulation')
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional


# ---------------------------------------------------------------------------
# Base Provenance Mixin
# ---------------------------------------------------------------------------

class ProvenanceMeta(BaseModel):
    """Standardized provenance metadata attached to all public API payloads."""
    is_demo: bool = Field(False, description="Whether the payload uses demo or mock synthetic data")
    data_available: bool = Field(True, description="Whether empirical ground data is available")
    source_type: str = Field("empirical_pipeline", description="Taxonomy source category")


# ---------------------------------------------------------------------------
# Decision History & Audit Schemas (Task 6)
# ---------------------------------------------------------------------------

class DecisionLogPayload(BaseModel):
    crop_id: str = Field(..., description="Crop identifier (e.g. 'big_onion', 'chilli')")
    season: str = Field("Maha 2025/2026", description="Agricultural season")
    officer_id: str = Field(..., description="Identifier of the recording officer")
    action_type: str = Field(..., description="Action type: PLANT_EXPANSION, HOLD_STORAGE, DEFER_IMPORT, MAINTAIN")
    quantity: float = Field(..., description="Intervention quantity in MT")
    unit: str = Field("MT", description="Measurement unit")
    rationale: str = Field(..., description="Agronomic or policy justification")
    model_version: Optional[str] = Field(None, description="Model version string (binds to active running model if omitted)")
    data_version: Optional[str] = Field("CBSL-HARTI-DOA-2024.12", description="Data pipeline release version")
    assumptions: Optional[Dict[str, Any]] = Field(None, description="Snapshot of planning parameters and loss ratios")
    notes: Optional[str] = Field(None, description="Optional officer notes")
    run_id: Optional[str] = Field(None, description="Pipeline run ID (auto-generated if omitted)")
    hash: Optional[str] = Field(None, description="SHA256 cryptographic verification hash (auto-computed if omitted)")


class DecisionRecordResponse(ProvenanceMeta):
    decision_id: str
    run_id: str
    hash: str
    crop_id: str
    season: str
    officer_id: str
    action_type: str
    quantity: float
    unit: str
    rationale: str
    model_version: str
    data_version: str
    assumptions: Dict[str, Any]
    timestamp: str


# ---------------------------------------------------------------------------
# What-If Simulation Schemas (Task 7 & 8)
# ---------------------------------------------------------------------------

class SimulationRequest(BaseModel):
    crop: str = Field(..., description="Crop identifier: 'big_onion' or 'chilli'")
    custom_planted_extent_ha: Optional[float] = Field(None, description="Custom planted extent in ha")
    custom_yield_mt_ha: Optional[float] = Field(None, description="Custom yield in MT/ha")
    custom_import_volume_mt: Optional[float] = Field(None, description="Custom import volume in MT")
    custom_loss_pct: Optional[float] = Field(None, description="Custom post-harvest loss fraction (e.g. 0.15)")


class SimulationScenarioItem(BaseModel):
    scenario: str
    supply_mt: float
    demand_mt: float
    gap_mt: float
    spi_ratio: float
    spi_score: float
    spi_label: str


class SimulationResponse(ProvenanceMeta):
    crop: str
    simulated_supply_mt: float
    simulated_spi: float
    simulated_spi_ratio: float
    simulated_label: str
    simulated_gap_mt: float
    area_ha: float
    yield_mt_ha: float
    loss_pct: float
    action_summary: str
    scenarios: Dict[str, SimulationScenarioItem]


# ---------------------------------------------------------------------------
# Farmer & Feedback Schemas
# ---------------------------------------------------------------------------

class PlantingReportPayload(BaseModel):
    crop_id: str
    season: str = "Maha 2025/2026"
    planned_area_ha: float
    actual_area_ha: float
    consent_given: bool
    pseudonymous_id: str
    harvest_outcome_mt: Optional[float] = None
    sale_price_rs_kg: Optional[float] = None
    sale_channel: Optional[str] = None
    notes: Optional[str] = None


class ReTriggerPayload(BaseModel):
    crop_id: str
    season: str = "Maha 2025/2026"
    target_month: int = 4
    suitable_land_ha: Optional[float] = None


class AdoptionSummaryResponse(ProvenanceMeta):
    data_available: bool = False
    is_demo: bool = True
    source_type: str = "telemetry_summary"
    district: str
    crop: str
    season: str
    counts: Dict[str, Optional[int]]
    message: str
    provenance_note: str


# ---------------------------------------------------------------------------
# Market Prices Schemas (Task 15)
# ---------------------------------------------------------------------------

class MarketPriceItemResponse(BaseModel):
    id: int
    crop_id: str
    crop_name: str
    crop_en: str
    crop_si: str
    crop_ta: str
    category: str
    market_center: str
    economic_center_en: str
    economic_center_si: str
    economic_center_ta: str
    wholesale_price: str
    retail_price: str
    wholesale_val: Optional[float] = None
    retail_val: Optional[float] = None
    trend_pct: str
    is_up: bool
    is_stable: bool
    price_date: str
    source: str = "CBSL/HARTI"


class MarketPricesResponse(ProvenanceMeta):
    data_available: bool = True
    is_demo: bool = False
    source_type: str = "cbsl_harti_market_bulletin"
    total: int
    prices: List[MarketPriceItemResponse]

