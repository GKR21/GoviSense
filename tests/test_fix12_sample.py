import pandas as pd
from pathlib import Path


def test_hand_check_sample_real_structure():
    root = Path(__file__).resolve().parent.parent
    sample_file = root / "data" / "interim" / "hand_check_REAL.csv"
    assert sample_file.exists(), "hand_check_REAL.csv does not exist"

    df = pd.read_csv(sample_file)

    # 1. Minimum 8 rows (representing at least 5% sample of real data records)
    assert len(df) >= 8, f"Sample size {len(df)} is less than 8 rows"

    # 2. Required columns present
    expected_cols = [
        "sample_id",
        "source_bulletin_pdf",
        "page_number",
        "crop",
        "district",
        "field_name",
        "extracted_value",
        "reviewer_verified_value",
        "is_match",
        "reviewer_notes",
    ]
    for col in expected_cols:
        assert col in df.columns, f"Missing column {col} in hand_check_REAL.csv"

    # 3. Reviewer verification columns must be strictly empty (no fabricated audit claims)
    for idx, row in df.iterrows():
        assert pd.isna(row["reviewer_verified_value"]) or str(row["reviewer_verified_value"]).strip() == "", (
            f"Row {idx} has pre-populated reviewer_verified_value: {row['reviewer_verified_value']}"
        )
        assert pd.isna(row["is_match"]) or str(row["is_match"]).strip() == "", (
            f"Row {idx} has pre-populated is_match: {row['is_match']}"
        )
        assert pd.isna(row["reviewer_notes"]) or str(row["reviewer_notes"]).strip() == "", (
            f"Row {idx} has pre-populated reviewer_notes: {row['reviewer_notes']}"
        )

    # 4. Source bulletins referenced exist on disk
    for src_pdf in df["source_bulletin_pdf"].unique():
        pdf_path = root / src_pdf
        assert pdf_path.exists(), f"Source bulletin PDF {src_pdf} does not exist on disk"
