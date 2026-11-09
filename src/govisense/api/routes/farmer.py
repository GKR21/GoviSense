"""
Farmer Routes Module for GoviSense (Task 11)
Provides endpoints for farmer crop recommendation (Top-3) and planting reports.
"""

from __future__ import annotations

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, Query

from govisense.config import settings
from govisense.api.auth import require_farmer
from govisense.api.schemas import PlantingReportPayload
from govisense.feedback.planting_reports import PlantingReport

router = APIRouter(prefix="/api/farmer", tags=["Farmer"])


@router.get("/top3", dependencies=[Depends(require_farmer)])
def farmer_top3(
    farmer_id: str = Query(..., description="Pseudonymous farmer identifier"),
    season: str = Query("Maha", description="Season: 'Maha' or 'Yala'"),
    land_ha: float = Query(3.0, description="Farmer's available land in hectares"),
    current_month: int = Query(10, description="Current calendar month (1-12)"),
    is_rainfed: bool = Query(False, description="Whether the farm area is rainfed (no irrigation)"),
    annual_rainfall_mm: float = Query(1100.0, description="Mean annual rainfall at site (mm)"),
    avg_temp_c: float = Query(28.0, description="Mean growing-season temperature (°C)"),
    soil_ph: Optional[float] = Query(None, description="Site soil pH (omit if unknown)"),
    zone: str = Query("dry", description="Agro-climatic zone: 'dry', 'intermediate', or 'wet'"),
):
    """
    Returns the top-3 recommended crops for a given farmer plus contextual
    metadata for each crop: fit_score, profit_range (P10–P90 price),
    risk_level, water_need, planting_window, harvest_period,
    spi_band_at_harvest, and confidence_badge.
    Protected: requires 'farmer' or 'admin' role.
    """
    from govisense.api import main as api_main
    return api_main.farmer_top3(
        farmer_id=farmer_id,
        season=season,
        land_ha=land_ha,
        current_month=current_month,
        is_rainfed=is_rainfed,
        annual_rainfall_mm=annual_rainfall_mm,
        avg_temp_c=avg_temp_c,
        soil_ph=soil_ph,
        zone=zone,
    )


@router.post("/report")
def submit_farmer_planting_report(payload: PlantingReportPayload):
    """
    Convenience endpoint for farmers to submit seasonal planting reports.
    Delegates to PlantingReportStore with explicit consent and pseudonymous ID.
    """
    from govisense.api import main as api_main
    return api_main.submit_planting_report(payload)

