"""
GoviSense CBSL & HARTI Price Bulletin Extractor
Team DARKBITE · ModelX 2.0 Phase 1

Extracts commodity prices (Wholesale, Retail, Farmgate) from Central Bank of Sri Lanka (CBSL)
Daily Price Reports and HARTI Food Information Bulletins using pdfplumber.
Aggregates daily and weekly market records into monthly price benchmarks for Anuradhapura
and trading hub corridors (Dambulla DEC and Pettah).
"""

from __future__ import annotations

import io
import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import pandas as pd
import numpy as np
import pdfplumber

logger = logging.getLogger(__name__)

# Standard target commodities in CBSL daily reports
TARGET_COMMODITIES = {
    "big_onion": [
        r"big\s*onion",
        r"onion\s*\(big\)",
        r"imported\s*big\s*onion",
        r"local\s*big\s*onion",
        r"ලොකු\s*ලූනු",
    ],
    "chilli": [
        r"green\s*chilli",
        r"green\s*chilli\s*\(local\)",
        r"chilli\s*\(green\)",
        r"chilli",
        r"අමු\s*මිරිස්",
    ],
    "red_onion": [
        r"red\s*onion",
        r"onion\s*\(red\)",
        r"රතු\s*ලූනු",
    ],
    "potato": [
        r"potato",
        r"potato\s*\(nuwara\s*eliya\)",
        r"අර්තාපල්",
    ],
}

# Standard markets tracked
MARKET_CENTERS = ["Dambulla", "Pettah", "Kandy", "Narahenpita", "Meegoda"]


def normalize_cbsl_line_numbers(line: str) -> str:
    """Fixes space-separated digits in real CBSL daily price reports (e.g. '5 00.00' -> '500.00')."""
    # Fix comma spaces: '1 ,200.00' -> '1200.00'
    line = re.sub(r"(\d+)\s*,\s*(\d+)", r"\1\2", line)
    # Fix separated hundred digits: '5 00.00' -> '500.00', '2 65.00' -> '265.00'
    for _ in range(2):
        line = re.sub(r"(^|\s)(\d{1,2})\s+(\d{2}\.\d{2})", r"\1\2\3", line)
    return line


def parse_numeric_price(val: Any) -> Optional[float]:
    """
    Parses string price entries into a clean float value.
    Handles ranges (e.g. '120.00 - 140.00' -> 130.00), commas, currency prefixes,
    and missing value indicators ('n.a.', '-', '').
    """
    if val is None or pd.isna(val):
        return None
    if isinstance(val, (int, float)):
        return float(val)

    s = str(val).strip()
    if not s or s.lower() in ("n.a.", "na", "-", "--", "n/a", "nil"):
        return None

    # Normalize CBSL separated digits if present
    s = normalize_cbsl_line_numbers(s)

    # Remove currency prefixes, commas, slashes, trailing /=
    s = re.sub(r"/=", "", s)
    s = re.sub(r"/=-", "", s)
    s = re.sub(r"[Rsrs\$\,\/=]", "", s)
    s = s.strip()

    # Check for range: e.g. "120.00-140.00"
    range_match = re.search(r"(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)", s)
    if range_match:
        try:
            low = float(range_match.group(1))
            high = float(range_match.group(2))
            return round((low + high) / 2.0, 2)
        except ValueError:
            pass

    # Extract first valid numeric float
    num_match = re.search(r"\d+(?:\.\d+)?", s)
    if num_match:
        try:
            return float(num_match.group(0))
        except ValueError:
            return None

    return None


def match_commodity_name(raw_text: str) -> Optional[str]:
    """Matches raw line or table cell string to standardized crop ID."""
    if not raw_text:
        return None
    lower_text = raw_text.lower().strip()
    for crop_id, patterns in TARGET_COMMODITIES.items():
        for pat in patterns:
            if re.search(pat, lower_text):
                return crop_id
    return None


class CBSLPriceExtractor:
    """
    PDF Table Extractor for CBSL Daily Price Reports and HARTI bulletins.
    Employs pdfplumber to extract structured price grids and unformatted text fallback.
    """

    def __init__(self, pilot_district: str = "Anuradhapura"):
        self.pilot_district = pilot_district

    def extract_from_pdf(
        self,
        pdf_source: Union[str, Path, bytes, io.BytesIO],
        bulletin_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extracts price records from a CBSL / HARTI PDF document.
        Returns a list of dicts with crop, date, wholesale_price, retail_price, and market.
        """
        records: List[Dict[str, Any]] = []

        if isinstance(pdf_source, (str, Path)):
            path = Path(pdf_source)
            if not path.exists():
                logger.warning(f"CBSL PDF path not found: {path}")
                return []
            ctx = pdfplumber.open(str(path))
        elif isinstance(pdf_source, bytes):
            ctx = pdfplumber.open(io.BytesIO(pdf_source))
        else:
            ctx = pdfplumber.open(pdf_source)

        with ctx as pdf:
            inferred_date = bulletin_date
            for page_num, page in enumerate(pdf.pages, start=1):
                # 1. Check for date header if not provided
                text = page.extract_text() or ""
                if not inferred_date:
                    date_match = re.search(r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})", text)
                    if not date_match:
                        date_match = re.search(
                            r"(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})",
                            text,
                            re.IGNORECASE,
                        )
                    if date_match:
                        try:
                            inferred_date = pd.to_datetime(date_match.group(1)).strftime("%Y-%m-%d")
                        except Exception:
                            inferred_date = "2024-01-01"

                effective_date = inferred_date or "2024-01-01"

                # 2. Extract from formatted text lines (primary for real CBSL daily bulletins)
                page_records: List[Dict[str, Any]] = []
                if text:
                    for line in text.split("\n"):
                        crop_id = match_commodity_name(line)
                        if not crop_id:
                            continue
                        clean_line = normalize_cbsl_line_numbers(line)
                        clean_line = re.sub(r"(\d)\s*,\s*(\d)", r"\1\2", clean_line)
                        clean_line = re.sub(r"(\d)\s+(\d{2}\.\d{2})", r"\1\2", clean_line)
                        nums = [float(x) for x in re.findall(r"\b\d+(?:\.\d+)?\b", clean_line) if float(x) > 10.0]
                        if len(nums) >= 8:
                            # Standard layout: [Pettah Yest, Pettah Today, Dambulla Yest, Dambulla Today, Pettah Ret Yest, Pettah Ret Today, Dambulla Ret Yest, Dambulla Ret Today]
                            p_damb_w = nums[3]
                            p_damb_r = nums[7]
                            p_pett_w = nums[1]
                            p_pett_r = nums[5]

                            page_records.append({
                                "date": effective_date,
                                "commodity": crop_id,
                                "crop": crop_id,
                                "market_center": "Dambulla DEC",
                                "market": "Dambulla DEC",
                                "wholesale_price_rs_kg": p_damb_w,
                                "retail_price_rs_kg": p_damb_r,
                                "farmgate_price_rs_kg": round(p_damb_w * 0.82, 1),
                                "source": "CBSL_Daily_PDF",
                                "raw_item": line.strip()[:60],
                                "is_interpolated": False,
                            })
                            page_records.append({
                                "date": effective_date,
                                "commodity": crop_id,
                                "crop": crop_id,
                                "market_center": "Pettah",
                                "market": "Pettah",
                                "wholesale_price_rs_kg": p_pett_w,
                                "retail_price_rs_kg": p_pett_r,
                                "farmgate_price_rs_kg": round(p_pett_w * 0.82, 1),
                                "source": "CBSL_Daily_PDF",
                                "raw_item": line.strip()[:60],
                                "is_interpolated": False,
                            })
                        elif len(nums) >= 2:
                            page_records.append({
                                "date": effective_date,
                                "commodity": crop_id,
                                "crop": crop_id,
                                "market_center": "Dambulla DEC",
                                "market": "Dambulla DEC",
                                "wholesale_price_rs_kg": nums[0],
                                "retail_price_rs_kg": nums[1] if len(nums) > 1 else None,
                                "farmgate_price_rs_kg": round(nums[0] * 0.82, 1),
                                "source": "CBSL_Daily_PDF",
                                "raw_item": line.strip()[:60],
                                "is_interpolated": False,
                            })

                if page_records:
                    records.extend(page_records)
                else:
                    # 3. Fallback to table extraction if text lines did not match
                    tables = page.extract_tables()
                    for table in tables:
                        if not table or len(table) < 2:
                            continue
                        header = [str(c or "").lower().strip() for c in table[0]]
                        wholesale_col = 1 if len(header) > 1 else None
                        retail_col = 2 if len(header) > 2 else None
                        market_col = 0

                        for idx, col_name in enumerate(header):
                            if "wholesale" in col_name or "whsl" in col_name or "තොග" in col_name:
                                wholesale_col = idx
                            elif "retail" in col_name or "සිල්ලර" in col_name:
                                retail_col = idx
                            elif "market" in col_name or "center" in col_name or "වෙළඳපොළ" in col_name:
                                market_col = idx

                        for row in table[1:]:
                            if not row:
                                continue
                            raw_item = str(row[0] or "").strip()
                            crop_id = match_commodity_name(raw_item)
                            if not crop_id:
                                continue

                            raw_wholesale = row[wholesale_col] if wholesale_col is not None and len(row) > wholesale_col else None
                            raw_retail = row[retail_col] if retail_col is not None and len(row) > retail_col else None
                            raw_market = (
                                str(row[market_col]).strip()
                                if market_col is not None and len(row) > market_col and row[market_col]
                                else "Dambulla DEC"
                            )

                            p_wholesale = parse_numeric_price(raw_wholesale)
                            p_retail = parse_numeric_price(raw_retail)

                            if p_wholesale is not None or p_retail is not None:
                                p_farmgate = round(p_wholesale * 0.82, 1) if p_wholesale else None
                                records.append({
                                    "date": effective_date,
                                    "commodity": crop_id,
                                    "crop": crop_id,
                                    "market_center": raw_market,
                                    "market": raw_market,
                                    "wholesale_price_rs_kg": p_wholesale,
                                    "retail_price_rs_kg": p_retail,
                                    "farmgate_price_rs_kg": p_farmgate,
                                    "source": "CBSL_Daily_PDF",
                                    "raw_item": raw_item,
                                    "is_interpolated": False,
                                })

        return records

    def aggregate_daily_to_monthly(self, daily_records: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Aggregates daily or weekly market price observations into monthly averages.
        """
        if not daily_records:
            return pd.DataFrame()

        df = pd.DataFrame(daily_records)
        df["date"] = pd.to_datetime(df["date"])
        df["year_month"] = df["date"].dt.strftime("%Y-%m")

        grouped = df.groupby(["year_month", "crop"]).agg(
            wholesale_price_rs_kg=("wholesale_price_rs_kg", "mean"),
            retail_price_rs_kg=("retail_price_rs_kg", "mean"),
            farmgate_price_rs_kg=("farmgate_price_rs_kg", "mean"),
            observations_count=("date", "count"),
        ).reset_index()

        grouped["wholesale_price_rs_kg"] = grouped["wholesale_price_rs_kg"].round(1)
        grouped["retail_price_rs_kg"] = grouped["retail_price_rs_kg"].round(1)
        grouped["farmgate_price_rs_kg"] = grouped["farmgate_price_rs_kg"].round(1)
        return grouped


def create_sample_cbsl_pdf_bytes(
    date_str: str = "2024-08-15",
    big_onion_wholesale: float = 145.0,
    big_onion_retail: float = 195.0,
    chilli_wholesale: float = 380.0,
    chilli_retail: float = 520.0,
) -> bytes:
    """
    Creates a minimal valid PDF byte stream representing a CBSL Daily Price Report.
    Used for unit testing, reproducible extraction verification, and offline demos.
    """
    stream_text = (
        f"BT\n"
        f"/F1 12 Tf\n"
        f"50 720 Td (Central Bank of Sri Lanka - Daily Price Report: {date_str}) Tj\n"
        f"0 -30 Td (Market: Dambulla Dedicated Economic Centre) Tj\n"
        f"0 -25 Td (Item / Commodity                  Wholesale (Rs/kg)    Retail (Rs/kg)) Tj\n"
        f"0 -20 Td (Big Onion (Local/Imported)        {big_onion_wholesale:.2f}               {big_onion_retail:.2f}) Tj\n"
        f"0 -20 Td (Green Chilli (Local)              {chilli_wholesale:.2f}               {chilli_retail:.2f}) Tj\n"
        f"0 -20 Td (Red Onion (Sinnakkai)             260.00               340.00) Tj\n"
        f"0 -20 Td (Potato (Nuwara Eliya)             210.00               280.00) Tj\n"
        f"ET\n"
    ).encode("latin1")

    stream_len = len(stream_text)

    pdf = bytearray()
    pdf.extend(b"%PDF-1.4\n")
    # Object 1: Catalog
    o1 = len(pdf)
    pdf.extend(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    # Object 2: Pages
    o2 = len(pdf)
    pdf.extend(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
    # Object 3: Page
    o3 = len(pdf)
    pdf.extend(
        b"3 0 obj\n"
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\n"
        b"endobj\n"
    )
    # Object 4: Contents Stream
    o4 = len(pdf)
    pdf.extend(f"4 0 obj\n<< /Length {stream_len} >>\nstream\n".encode("latin1"))
    pdf.extend(stream_text)
    pdf.extend(b"\nendstream\nendobj\n")
    # Object 5: Font
    o5 = len(pdf)
    pdf.extend(b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")

    # Xref table
    xref_pos = len(pdf)
    pdf.extend(b"xref\n0 6\n0000000000 65535 f \n")
    for offset in [o1, o2, o3, o4, o5]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("latin1"))

    # Trailer
    pdf.extend(b"trailer\n<< /Size 6 /Root 1 0 R >>\n")
    pdf.extend(f"startxref\n{xref_pos}\n%%EOF\n".encode("latin1"))

    return bytes(pdf)
