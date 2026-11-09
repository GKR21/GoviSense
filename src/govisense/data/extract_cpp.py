"""
GoviSense CPP (Crop Production Programme) & DOA Extractor
Team DARKBITE · ModelX 2.0 Phase 1

Extracts seasonal agricultural statistics (Target extent, Planted extent, Yield, Production)
from Department of Agriculture (DOA) / DCS Seasonal Crop Prospects Bulletins using pdfplumber.
Maps seasonal Maha / Yala totals into monthly district-level agricultural time-series.
"""

from __future__ import annotations

import io
import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
import pandas as pd
import numpy as np
import pdfplumber

from govisense.data.extract_cbsl import parse_numeric_price, match_commodity_name

logger = logging.getLogger(__name__)


class CPPExtractor:
    """
    Extracts agricultural production data from Crop Production Programme (CPP) bulletins.
    Parses both district-level totals (e.g., Anuradhapura) and National totals (Sri Lanka).
    """

    def __init__(self, target_district: str = "Anuradhapura", include_national: bool = True):
        self.target_district = target_district.lower()
        self.include_national = include_national

    def extract_from_pdf(
        self,
        pdf_source: Union[str, Path, bytes, io.BytesIO],
        season: Optional[str] = None,
        year: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extracts seasonal district-level and national crop production records from a CPP PDF bulletin.
        Returns a list of dicts with district, crop, season, year, planted_extent_ha,
        yield_mt_per_ha, harvest_volume_mt.
        """
        records: List[Dict[str, Any]] = []

        if isinstance(pdf_source, (str, Path)):
            path = Path(pdf_source)
            if not path.exists():
                logger.warning(f"CPP PDF path not found: {path}")
                return []
            ctx = pdfplumber.open(str(path))
            filename = path.name
        elif isinstance(pdf_source, bytes):
            ctx = pdfplumber.open(io.BytesIO(pdf_source))
            filename = "buffer.pdf"
        else:
            ctx = pdfplumber.open(pdf_source)
            filename = getattr(pdf_source, "name", "stream.pdf")

        inferred_season = season
        inferred_year = year

        # Detect year from filename if present
        y_fn_match = re.search(r"202\d", str(filename))
        if y_fn_match and not inferred_year:
            inferred_year = int(y_fn_match.group(0))

        with ctx as pdf:
            pdf_wide_crop = match_commodity_name(filename) or "big_onion"
            for page in pdf.pages:
                text = page.extract_text() or ""
                lower_text = text.lower()

                # In official multi-page CPP bulletins (DOA / DCS), target crop tables have headers like:
                # "Other Field Crop Cultivation : Big Onion Production Targets"
                ofc_match = re.search(r"other field crop.*?:\s*([a-zA-Z\s]+?)\s*production targets", lower_text)
                if ofc_match:
                    detected = match_commodity_name(ofc_match.group(1))
                    if not detected:
                        continue
                    current_crop = detected
                elif len(pdf.pages) <= 2:
                    current_crop = match_commodity_name(text) or pdf_wide_crop
                else:
                    # Skip pages for unrelated crops (vegetables, paddy, fruits, seed requirements)
                    continue

                # Detect season & year from page text if not specified
                eff_season = inferred_season
                if not eff_season:
                    if "maha" in lower_text and "yala" not in lower_text:
                        eff_season = "Maha"
                    elif "yala" in lower_text and "maha" not in lower_text:
                        eff_season = "Yala"
                    else:
                        eff_season = "Yala"

                eff_year = inferred_year
                if not eff_year:
                    y_match = re.search(r"\b(201\d|202\d)\b", text)
                    eff_year = int(y_match.group(1)) if y_match else 2024

                # 1. Process structured tables
                tables = page.extract_tables()
                for table in tables:
                    if not table or len(table) < 2:
                        continue

                    header = [str(c or "").lower().strip() for c in table[0]]
                    dist_col = 0
                    crop_col = None
                    achieved_col = None
                    yield_col = None
                    prod_col = None

                    current_table_crop = match_commodity_name(text) or current_crop

                    target_col = None
                    for idx, c in enumerate(header):
                        if "district" in c or "දිස්ත්‍රික්" in c:
                            dist_col = idx
                        elif "crop" in c or "බෝග" in c:
                            crop_col = idx
                        elif "target" in c or "ඉලක්ක" in c:
                            target_col = idx
                        elif ("achieved" in c or "sown" in c or "planted" in c or "extent" in c or "වගා" in c) and "target" not in c and "ඉලක්ක" not in c:
                            achieved_col = idx
                        elif "yield" in c or "අස්වැන්න" in c:
                            yield_col = idx
                        elif "production" in c or "harvest" in c or "නිෂ්පාදනය" in c:
                            prod_col = idx

                    # Column offset alignment: if target_col is present, achieved_col is the column immediately after
                    if target_col is not None and achieved_col is None:
                        achieved_col = target_col + 1
                    if achieved_col is None and len(header) >= 3:
                        achieved_col = 3 if target_col is not None else 2
                    if prod_col is None and len(header) >= (achieved_col + 2 if achieved_col else 4):
                        prod_col = achieved_col + 1 if achieved_col is not None else 3
                    if yield_col is None and len(header) >= (prod_col + 2 if prod_col else 5):
                        yield_col = prod_col + 1 if prod_col is not None else 4

                    for row in table[1:]:
                        if not row or len(row) <= dist_col:
                            continue
                        row_dist = str(row[dist_col] or "").strip().lower()

                        is_target = self.target_district in row_dist or "total" in row_dist or "all" in row_dist
                        is_national = "sri lanka" in row_dist or "national" in row_dist

                        if not is_target and not (self.include_national and is_national):
                            continue

                        row_crop = current_table_crop
                        if crop_col is not None and len(row) > crop_col:
                            matched = match_commodity_name(str(row[crop_col]))
                            if matched:
                                row_crop = matched

                        planted_ha = (
                            parse_numeric_price(row[achieved_col])
                            if achieved_col is not None and len(row) > achieved_col
                            else None
                        )
                        prod_mt = (
                            parse_numeric_price(row[prod_col])
                            if prod_col is not None and len(row) > prod_col
                            else None
                        )
                        yield_val = (
                            parse_numeric_price(row[yield_col])
                            if yield_col is not None and len(row) > yield_col
                            else None
                        )

                        if planted_ha and prod_mt and (yield_val is None or yield_val <= 0):
                            yield_val = round(prod_mt / max(planted_ha, 1.0), 2)
                        elif planted_ha and yield_val and (prod_mt is None or prod_mt <= 0):
                            prod_mt = round(planted_ha * yield_val, 1)

                        if planted_ha or prod_mt:
                            dist_label = "Sri Lanka" if is_national else (
                                "Anuradhapura" if self.target_district in row_dist else row_dist.title()
                            )
                            records.append({
                                "district": dist_label,
                                "crop": row_crop,
                                "season": eff_season,
                                "year": eff_year,
                                "planted_extent_ha": planted_ha or 0.0,
                                "yield_mt_per_ha": yield_val or 0.0,
                                "harvest_volume_mt": prod_mt or 0.0,
                                "source": "DOA_CPP_Bulletin_National" if is_national else "DOA_CPP_Bulletin",
                            })

                # 2. Line parsing (real multi-column official CPP PDF layouts)
                in_target_district_section = False
                for line in text.split("\n"):
                    line_clean = line.strip()
                    lower_line = line_clean.lower()

                    if self.target_district in lower_line:
                        in_target_district_section = True
                    elif in_target_district_section and any(
                        d in lower_line for d in ["polonnaruwa", "badulla", "kurunegala", "sri lanka", "provincial:"]
                    ):
                        in_target_district_section = False

                    # Check for Sri Lanka National Row
                    if self.include_national and lower_line.startswith("sri lanka"):
                        line_crop = match_commodity_name(line_clean) or current_crop
                        matches = re.findall(r"\b\d+(?:,\d+)*(?:\.\d+)?\b", line_clean)
                        nums = [float(x.replace(",", "")) for x in matches if x]
                        if len(nums) >= 9:
                            # Standard layout: [maha_ha, maha_yield, maha_mt, yala_ha, yala_yield, yala_mt, year_ha, year_yield, year_mt]
                            records.append({
                                "district": "Sri Lanka",
                                "crop": line_crop,
                                "season": "Maha",
                                "year": eff_year,
                                "planted_extent_ha": nums[0],
                                "yield_mt_per_ha": nums[1],
                                "harvest_volume_mt": nums[2],
                                "source": "DOA_CPP_Bulletin_National",
                            })
                            records.append({
                                "district": "Sri Lanka",
                                "crop": line_crop,
                                "season": "Yala",
                                "year": eff_year,
                                "planted_extent_ha": nums[3],
                                "yield_mt_per_ha": nums[4],
                                "harvest_volume_mt": nums[5],
                                "source": "DOA_CPP_Bulletin_National",
                            })
                            records.append({
                                "district": "Sri Lanka",
                                "crop": line_crop,
                                "season": "Year",
                                "year": eff_year,
                                "planted_extent_ha": nums[6],
                                "yield_mt_per_ha": nums[7],
                                "harvest_volume_mt": nums[8],
                                "source": "DOA_CPP_Bulletin_National",
                            })
                        elif len(nums) >= 4:
                            # Column-offset fix: [target_ha, achieved_ha, prod_mt, yield_mt_ha]
                            records.append({
                                "district": "Sri Lanka",
                                "crop": line_crop,
                                "season": "Year",
                                "year": eff_year,
                                "planted_extent_ha": nums[1],
                                "yield_mt_per_ha": nums[3],
                                "harvest_volume_mt": nums[2],
                                "source": "DOA_CPP_Bulletin_National",
                            })
                        elif len(nums) == 3:
                            # [achieved_ha, prod_mt, yield_mt_ha]
                            records.append({
                                "district": "Sri Lanka",
                                "crop": line_crop,
                                "season": "Year",
                                "year": eff_year,
                                "planted_extent_ha": nums[0],
                                "yield_mt_per_ha": nums[2],
                                "harvest_volume_mt": nums[1],
                                "source": "DOA_CPP_Bulletin_National",
                            })
                        elif len(nums) >= 2:
                            records.append({
                                "district": "Sri Lanka",
                                "crop": line_crop,
                                "season": "Year",
                                "year": eff_year,
                                "planted_extent_ha": nums[0],
                                "yield_mt_per_ha": round(nums[1] / max(nums[0], 1.0), 2),
                                "harvest_volume_mt": nums[1],
                                "source": "DOA_CPP_Bulletin_National",
                            })

                    # Check for District Total Row in real CPP tables
                    elif in_target_district_section and lower_line.startswith("total"):
                        matches = re.findall(r"\b\d+(?:,\d+)*(?:\.\d+)?\b", line_clean)
                        nums = [float(x.replace(",", "")) for x in matches if x]
                        if len(nums) >= 6:
                            records.append({
                                "district": self.target_district.title(),
                                "crop": current_crop,
                                "season": "Year",
                                "year": eff_year,
                                "planted_extent_ha": nums[-3],
                                "yield_mt_per_ha": nums[-2],
                                "harvest_volume_mt": nums[-1],
                                "source": "DOA_CPP_Bulletin",
                            })

                    # Single line district match fallback
                    elif self.target_district in lower_line:
                        line_crop = match_commodity_name(line_clean) or current_crop
                        if any(r["district"] == self.target_district.title() and r["crop"] == line_crop for r in records):
                            continue
                        matches = re.findall(r"\b\d+(?:,\d+)*(?:\.\d+)?\b", line_clean)
                        nums = [float(x.replace(",", "")) for x in matches if x]
                        if len(nums) >= 4:
                            records.append({
                                "district": self.target_district.title(),
                                "crop": line_crop,
                                "season": eff_season,
                                "year": eff_year,
                                "planted_extent_ha": nums[1],
                                "yield_mt_per_ha": nums[3],
                                "harvest_volume_mt": nums[2],
                                "source": "DOA_CPP_Text",
                            })
                        elif len(nums) >= 2:
                            records.append({
                                "district": self.target_district.title(),
                                "crop": line_crop,
                                "season": eff_season,
                                "year": eff_year,
                                "planted_extent_ha": nums[0],
                                "yield_mt_per_ha": round(nums[1] / max(nums[0], 1.0), 2),
                                "harvest_volume_mt": nums[1],
                                "source": "DOA_CPP_Text",
                            })

        return records

    def validate_national_figures(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validates extracted national Sri Lanka totals against proposal reference benchmarks:
        Big Onion Year 2026: 4,867 ha, 82,149 t.
        """
        validated = {}
        for r in records:
            if r.get("district") == "Sri Lanka" and r.get("crop") == "big_onion":
                ha = r.get("planted_extent_ha", 0.0)
                mt = r.get("harvest_volume_mt", 0.0)
                ha_ok = abs(ha - 4867.0) <= 5.0
                mt_ok = abs(mt - 82149.0) <= 50.0
                if ha_ok and mt_ok:
                    validated["big_onion_national_2026"] = {
                        "planted_extent_ha": ha,
                        "harvest_volume_mt": mt,
                        "expected_ha": 4867.0,
                        "expected_mt": 82149.0,
                        "is_valid": True,
                    }
                    break
        return validated

    def disaggregate_season_to_months(
        self,
        season_record: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Disaggregates a seasonal crop aggregate into monthly timeline records
        based on Sri Lankan agronomic calendars:
          - Yala (Big Onion): Planting in May (35%), June (55%), July (10%);
            Harvest in August (40%), September (45%), October (15%).
          - Maha (Chilli): Planting in October (40%), November (50%), December (10%);
            Harvest in January (35%), February (45%), March (20%).
        """
        crop = season_record["crop"]
        season = season_record.get("season", "Yala")
        year = season_record.get("year", 2024)
        total_ha = season_record.get("planted_extent_ha", 0.0)
        total_mt = season_record.get("harvest_volume_mt", 0.0)
        yield_val = season_record.get("yield_mt_per_ha", 0.0)

        monthly_rows = []

        if crop == "big_onion" and season == "Yala":
            # Yala months: 5, 6, 7 (planting) and 8, 9, 10 (harvest)
            plant_weights = {5: 0.35, 6: 0.55, 7: 0.10}
            harvest_weights = {8: 0.40, 9: 0.45, 10: 0.15}

            for m in range(1, 13):
                p_ha = round(total_ha * plant_weights.get(m, 0.0), 1)
                h_mt = round(total_mt * harvest_weights.get(m, 0.0), 1)
                monthly_rows.append({
                    "year_month": f"{year:04d}-{m:02d}",
                    "crop": crop,
                    "district": season_record.get("district", "Anuradhapura"),
                    "month": m,
                    "year": year,
                    "planted_extent_ha": p_ha,
                    "yield_mt_per_ha": yield_val,
                    "harvest_volume_mt": h_mt,
                    "season": season,
                })

        elif crop == "chilli" and season == "Maha":
            # Maha months: 10, 11, 12 (planting) and 1, 2, 3 (harvest next year)
            plant_weights = {10: 0.40, 11: 0.50, 12: 0.10}
            harvest_weights = {1: 0.35, 2: 0.45, 3: 0.20}

            for m in range(1, 13):
                p_ha = round(total_ha * plant_weights.get(m, 0.0), 1)
                h_mt = round(total_mt * harvest_weights.get(m, 0.0), 1)
                monthly_rows.append({
                    "year_month": f"{year:04d}-{m:02d}",
                    "crop": crop,
                    "district": season_record.get("district", "Anuradhapura"),
                    "month": m,
                    "year": year,
                    "planted_extent_ha": p_ha,
                    "yield_mt_per_ha": yield_val,
                    "harvest_volume_mt": h_mt,
                    "season": season,
                })
        else:
            # Default spread
            for m in range(1, 13):
                monthly_rows.append({
                    "year_month": f"{year:04d}-{m:02d}",
                    "crop": crop,
                    "district": season_record.get("district", "Anuradhapura"),
                    "month": m,
                    "year": year,
                    "planted_extent_ha": round(total_ha / 12.0, 1),
                    "yield_mt_per_ha": yield_val,
                    "harvest_volume_mt": round(total_mt / 12.0, 1),
                    "season": season,
                })

        return monthly_rows


def create_sample_cpp_pdf_bytes(
    season: str = "Yala",
    year: int = 2024,
    onion_ha: float = 4250.0,
    onion_prod_mt: float = 65875.0,
    chilli_ha: float = 2100.0,
    chilli_prod_mt: float = 11340.0,
    include_national: bool = False,
    national_onion_ha: float = 4867.0,
    national_onion_prod_mt: float = 82149.0,
    national_chilli_ha: float = 15899.0,
    national_chilli_prod_mt: float = 142116.0,
) -> bytes:
    """
    Creates a valid PDF byte stream representing a Department of Agriculture
    Crop Production Programme (CPP) seasonal progress report.
    Includes both district (Anuradhapura) and National (Sri Lanka) totals when requested.
    """
    national_lines = ""
    if include_national:
        national_lines = (
            f"0 -20 Td (Sri Lanka        Big Onion   5000.0       {national_onion_ha:.1f}        {national_onion_prod_mt:.1f}         {national_onion_prod_mt/national_onion_ha:.2f}) Tj\n"
            f"0 -20 Td (Sri Lanka        Chilli      18000.0      {national_chilli_ha:.1f}        {national_chilli_prod_mt:.1f}         {national_chilli_prod_mt/national_chilli_ha:.2f}) Tj\n"
        )

    stream_text = (
        f"BT\n"
        f"/F1 12 Tf\n"
        f"50 720 Td (Department of Agriculture - Crop Production Programme: {season} {year}) Tj\n"
        f"0 -30 Td (District: Anuradhapura - Progress Report) Tj\n"
        f"0 -25 Td (District         Crop        Target (ha)  Achieved (ha)  Production (Mt)  Yield (Mt/ha)) Tj\n"
        f"0 -20 Td (Anuradhapura     Big Onion   4500.0       {onion_ha:.1f}        {onion_prod_mt:.1f}         {onion_prod_mt/onion_ha:.2f}) Tj\n"
        f"0 -20 Td (Anuradhapura     Chilli      2500.0       {chilli_ha:.1f}        {chilli_prod_mt:.1f}         {chilli_prod_mt/chilli_ha:.2f}) Tj\n"
        f"{national_lines}"
        f"ET\n"
    ).encode("latin1")

    stream_len = len(stream_text)

    pdf = bytearray()
    pdf.extend(b"%PDF-1.4\n")
    o1 = len(pdf)
    pdf.extend(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    o2 = len(pdf)
    pdf.extend(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
    o3 = len(pdf)
    pdf.extend(
        b"3 0 obj\n"
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\n"
        b"endobj\n"
    )
    o4 = len(pdf)
    pdf.extend(f"4 0 obj\n<< /Length {stream_len} >>\nstream\n".encode("latin1"))
    pdf.extend(stream_text)
    pdf.extend(b"\nendstream\nendobj\n")
    o5 = len(pdf)
    pdf.extend(b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")

    xref_pos = len(pdf)
    pdf.extend(b"xref\n0 6\n0000000000 65535 f \n")
    for offset in [o1, o2, o3, o4, o5]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("latin1"))

    pdf.extend(b"trailer\n<< /Size 6 /Root 1 0 R >>\n")
    pdf.extend(f"startxref\n{xref_pos}\n%%EOF\n".encode("latin1"))

    return bytes(pdf)
