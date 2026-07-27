"""
Data Quality & Completeness Auditing Engine.

Computes per-field completeness, missing value percentages, and flags
unreliable or untracked fields per board.
"""

import pandas as pd
from typing import Dict, Any, List

# Special 100% null fields in Board 2 specified as 'not tracked' in data dictionary
NOT_TRACKED_FIELDS = {
    "text_mm5n2tcb": "Expected Billing Month",
    "text_mm5nc1jf": "Actual Collection Month",
    "text_mm5n4hjg": "Collection status",
    "text_mm5nvdah": "Collection Date"
}

def get_board_completeness(df: pd.DataFrame, board_name: str) -> Dict[str, Any]:
    """Generate per-field completeness report and data health alerts."""
    total_rows = len(df)
    metrics: Dict[str, Any] = {}
    high_null_fields: List[str] = []
    untracked_fields: List[str] = []

    for col in df.columns:
        # Check null or empty string
        is_null_mask = df[col].isna() | (df[col].astype(str).str.strip() == "") | (df[col].astype(str).str.strip() == "None")
        null_count = int(is_null_mask.sum())
        non_null_count = total_rows - null_count
        completeness_pct = round((non_null_count / total_rows * 100), 2) if total_rows > 0 else 0.0

        metrics[col] = {
            "non_null_count": non_null_count,
            "null_count": null_count,
            "completeness_pct": completeness_pct,
            "null_pct": round(100.0 - completeness_pct, 2)
        }

        if col in NOT_TRACKED_FIELDS and completeness_pct == 0.0:
            untracked_fields.append(f"{col} ({NOT_TRACKED_FIELDS[col]}): 100% null (Not Tracked)")
        elif completeness_pct < 50.0:
            high_null_fields.append(f"{col}: {100.0 - completeness_pct:.1f}% null")

    return {
        "board_name": board_name,
        "total_rows": total_rows,
        "metrics": metrics,
        "high_null_fields_count": len(high_null_fields),
        "high_null_warnings": high_null_fields,
        "untracked_fields": untracked_fields
    }
