"""
Data Cleaning and Normalization Pipeline.

Applies board-specific cleaning:
- Corrupt row detection (e.g. status header literal repetitions)
- Date parsing & numeric coercion (negative numbers preserved)
- Stage/Sector normalization & multi-value splitting
- Non-sector junk classification
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, List

# Non-sector labels identified in data dictionary
NON_SECTOR_JUNK = {"Tender", "DSP", "tender", "dsp"}

def clean_deal_funnel_data(df_raw: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Clean Board 1 (Deal Funnel) raw DataFrame.
    - Exclude 2 corrupt rows where Deal Status == 'Deal Status' literal
    - Coerce numeric and date fields
    - Normalize sector and owner codes
    """
    df = df_raw.copy()
    anomalies: Dict[str, Any] = {
        "initial_rows": len(df),
        "corrupt_status_rows_excluded": 0,
        "corrupt_stage_rows": 0,
        "non_sector_junk_count": 0
    }

    status_col = "color_mm5ncsbg"
    val_col = "numeric_mm5ndf61"

    # 1. Detect & Exclude corrupt rows (cell == header literal "Deal Status")
    if status_col in df.columns:
        corrupt_mask = df[status_col].astype(str).str.strip() == "Deal Status"
        anomalies["corrupt_status_rows_excluded"] = int(corrupt_mask.sum())
        df = df[~corrupt_mask].copy()

    # 2. Coerce numeric deal value (preserve NaNs, never convert NaN to 0)
    if val_col in df.columns:
        df[val_col] = pd.to_numeric(df[val_col], errors="coerce")

    # 3. Coerce Date columns
    date_cols = ["date_mm5nq7fv", "date_mm5nkvyn", "date_mm5n9m78"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # 4. Clean & normalize text fields
    owner_col = "color_mm5n9tt5"
    if owner_col in df.columns:
        df[owner_col] = df[owner_col].astype(str).str.strip()

    sector_col = "color_mm5ndfr7"
    if sector_col in df.columns:
        df[sector_col] = df[sector_col].astype(str).str.strip()
        junk_mask = df[sector_col].isin(NON_SECTOR_JUNK)
        anomalies["non_sector_junk_count"] = int(junk_mask.sum())

    # Multi-value product deal field split support helper
    product_col = "color_mm5ns41q"
    if product_col in df.columns:
        df["product_deal_list"] = df[product_col].fillna("").apply(
            lambda x: [p.strip() for p in str(x).split(",") if p.strip()]
        )

    anomalies["cleaned_rows"] = len(df)
    return df, anomalies


def clean_work_order_data(df_raw: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Clean Board 2 (Work Order Tracker) raw DataFrame.
    - Coerce financial fields to numeric (preserve negative credit balances)
    - Coerce date columns
    - Handle comma-separated multi-value 'Type of Work'
    """
    df = df_raw.copy()
    anomalies: Dict[str, Any] = {
        "initial_rows": len(df),
        "corrupt_rows_excluded": 0
    }

    # Numeric financial columns
    numeric_cols = [
        "numeric_mm5n90w", "numeric_mm5n8qdq", "numeric_mm5nafen",
        "numeric_mm5ng5ec", "numeric_mm5nat1b", "numeric_mm5nb1zd",
        "numeric_mm5nz3xc", "numeric_mm5npw9h", "numeric_mm5nzbhp",
        "numeric_mm5n4hs1", "numeric_mm5nfqkt"
    ]

    for col in numeric_cols:
        if col in df.columns:
            # pd.to_numeric cleanly retains negative values (e.g. credit balances in Amount Receivable)
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Date columns
    date_cols = [
        "date_mm5nzgn3", "date_mm5nmhz8", "date_mm5nteqq",
        "date_mm5ng5kv", "date_mm5njdr0", "date_mm5nvdah"
    ]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Split multi-value 'Type of Work'
    tow_col = "color_mm5ntavv"
    if tow_col in df.columns:
        df["type_of_work_list"] = df[tow_col].fillna("").apply(
            lambda x: [t.strip() for t in str(x).split(",") if t.strip()]
        )

    # Normalize Personnel and Sector codes for joining
    if "color_mm5nf68v" in df.columns:
        df["color_mm5nf68v"] = df["color_mm5nf68v"].astype(str).str.strip()
    if "color_mm5nfp0j" in df.columns:
        df["color_mm5nfp0j"] = df["color_mm5nfp0j"].astype(str).str.strip()

    anomalies["cleaned_rows"] = len(df)
    return df, anomalies
