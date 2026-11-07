"""
GoviSense Data Catalogue Module
Team DARKBITE · ModelX 2.0 Phase 1

Provides program access, validation, and audit provenance for all empirical datasets
used in GoviSense (CBSL, HARTI, DOA/CPP, WFP, Open-Meteo, DCS HIES).
Ensures all columns in the monthly master grid map to registered, authenticated data sources.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
from dataclasses import dataclass, asdict

from govisense.config import DATA_DIR

logger = logging.getLogger(__name__)

DEFAULT_CATALOGUE_PATH = DATA_DIR / "catalogue.csv"


@dataclass
class DatasetEntry:
    dataset_id: str
    title: str
    publisher: str
    format: str
    frequency: str
    temporal_range: str
    spatial_coverage: str
    extracted_variables: List[str]
    source_url: str
    citation: str
    missing_data_treatment: str
    licence: str = "public government publication, terms not stated"
    date_retrieved: str = "2026-11-07"
    url_snapshot: str = ""
    is_primary: bool = True


class DataCatalogue:
    """
    Catalogue registry managing data provenance, source URLs, and variable mappings.
    """

    def __init__(self, catalogue_path: Optional[Path] = None):
        self.catalogue_path = catalogue_path or DEFAULT_CATALOGUE_PATH
        self.entries: Dict[str, DatasetEntry] = {}
        self.load()

    def load(self) -> None:
        """Loads and parses the catalogue CSV."""
        if not self.catalogue_path.exists():
            logger.warning(f"Data catalogue not found at {self.catalogue_path}")
            return

        df = pd.read_csv(self.catalogue_path)
        for _, row in df.iterrows():
            vars_list = [v.strip() for v in str(row["extracted_variables"]).split(";") if v.strip()]
            entry = DatasetEntry(
                dataset_id=str(row["dataset_id"]),
                title=str(row["title"]),
                publisher=str(row["publisher"]),
                format=str(row["format"]),
                frequency=str(row["frequency"]),
                temporal_range=str(row["temporal_range"]),
                spatial_coverage=str(row["spatial_coverage"]),
                extracted_variables=vars_list,
                source_url=str(row["source_url"]),
                citation=str(row["citation"]),
                missing_data_treatment=str(row["missing_data_treatment"]),
                licence=str(row.get("licence", "public government publication, terms not stated")),
                date_retrieved=str(row.get("date_retrieved", "2026-11-07")),
                url_snapshot=str(row.get("url_snapshot", "")),
                is_primary=bool(row.get("is_primary", True)),
            )
            self.entries[entry.dataset_id] = entry

    def list_datasets(self) -> List[Dict[str, Any]]:
        """Returns all catalogue entries as dicts."""
        return [asdict(e) for e in self.entries.values()]

    def get_dataset(self, dataset_id: str) -> Optional[DatasetEntry]:
        """Retrieves a specific dataset entry by ID."""
        return self.entries.get(dataset_id)

    def find_datasets_for_variable(self, variable_name: str) -> List[DatasetEntry]:
        """Returns datasets that provide a given variable."""
        matches = []
        for entry in self.entries.values():
            if variable_name in entry.extracted_variables:
                matches.append(entry)
        return matches

    def validate_dataset_coverage(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validates that every operational feature in a dataset maps to at least
        one documented data source in the catalogue.
        """
        all_catalogued_vars = set()
        for entry in self.entries.values():
            all_catalogued_vars.update(entry.extracted_variables)

        # Standard derived/metadata columns that do not require external ingestion
        system_cols = {
            "year_month", "date", "year", "month", "district", "crop",
            "actual_spi", "spi_class", "is_interpolated", "data_source",
            "is_simulation", "source"
        }

        unmapped = []
        for col in df.columns:
            if col not in system_cols and col not in all_catalogued_vars:
                unmapped.append(col)

        is_valid = len(unmapped) == 0
        return {
            "is_valid": is_valid,
            "total_columns": len(df.columns),
            "catalogued_variables_count": len(all_catalogued_vars),
            "unmapped_columns": unmapped,
            "provenance_compliance_score": round((len(df.columns) - len(unmapped)) / len(df.columns) * 100.0, 1)
        }


def get_default_catalogue() -> DataCatalogue:
    """Convenience singleton loader."""
    return DataCatalogue()
