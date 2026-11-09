"""
Pipeline & Catalogue Routes for GoviSense (Task 9)
Provides endpoints for Rashmika:
- GET /api/catalogue: Ingested data catalogue with licences and source URLs
- GET /api/catalogue/{dataset_id}: Single dataset detail
- GET /api/pipeline/run-info: Active pipeline execution metadata (run ID, model version, status)
- GET /api/simulation/adoption-summary (alias: /api/adoption/summary): Empirical adoption telemetry status
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query, status

from govisense.config import settings
from govisense.data.catalogue import DataCatalogue
from govisense.db.history import get_running_model_version

router = APIRouter(tags=["Pipeline & Data Catalogue"])

catalogue = DataCatalogue()
ACTIVE_RUN_ID = f"RUN-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


@router.get("/api/catalogue")
def get_catalogue(
    format: Optional[str] = Query(None, description="Filter by format: 'PDF', 'CSV', 'API'"),
    publisher: Optional[str] = Query(None, description="Filter by publisher (e.g. 'CBSL', 'HARTI')"),
):
    """
    Task 9 (P1): Returns data catalogue entries documenting data sources, licences, and variables.
    """
    entries = catalogue.list_datasets()
    if format:
        entries = [e for e in entries if e.get("format", "").upper() == format.upper()]
    if publisher:
        entries = [e for e in entries if publisher.lower() in e.get("publisher", "").lower()]

    return {
        "total_datasets": len(entries),
        "datasets": entries,
        "data_available": True,
        "is_demo": False,
        "source_type": "data_catalogue",
    }


@router.get("/api/catalogue/{dataset_id}")
def get_catalogue_dataset(dataset_id: str):
    """
    Task 9 (P1): Returns a single dataset catalogue record by ID (case-insensitive).
    """
    entry = (
        catalogue.get_dataset(dataset_id)
        or catalogue.get_dataset(dataset_id.upper())
        or catalogue.get_dataset(dataset_id.lower())
    )
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset '{dataset_id}' not found in data catalogue.",
        )
    from dataclasses import asdict
    return {
        "dataset": asdict(entry),
        "data_available": True,
        "is_demo": False,
        "source_type": "data_catalogue",
    }


@router.get("/api/pipeline/run-info")
@router.get("/api/run-info")
def get_pipeline_run_info():
    """
    Task 9 (P1): Returns active pipeline run information for Rashmika's dashboard and verification checks.
    Includes active run_id, active model versions, data catalogue version, and pipeline operational status.
    """
    from govisense.api import main as api_main
    models_ready = len(getattr(api_main, "a1_models", {})) == 2

    return {
        "run_id": ACTIVE_RUN_ID,
        "pipeline_version": "GoviSense v2.0",
        "model_version": get_running_model_version(),
        "data_version": "CBSL-HARTI-DOA-2024.12",
        "pilot_district": settings.pilot_district,
        "crops": ["big_onion", "chilli"],
        "status": "ready" if models_ready else "initializing",
        "models_loaded": models_ready,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data_available": True,
        "is_demo": False,
        "source_type": "pipeline_metadata",
    }
