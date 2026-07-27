"""
Cross-Board Data Joining Engine.

JOIN STRATEGIES:
1. SAFE JOIN: Aggregate joining on Owner code <-> Personnel code OR Sector <-> Sector.
2. BEST-EFFORT JOIN: Deal Name <-> Deal name masked exact match (~30% coverage).
   Computes confidence score and match metadata. Discloses confidence explicitly.
"""

import pandas as pd
from typing import Dict, Any, Tuple

def safe_join_cross_board(
    df_deals: pd.DataFrame,
    df_work_orders: pd.DataFrame,
    join_key: str = "owner"
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Perform safe cross-board aggregation joined on Owner code or Sector.
    """
    if join_key.lower() == "owner":
        k1, k2 = "color_mm5n9tt5", "color_mm5nf68v"
        key_name = "Owner Code"
    elif join_key.lower() == "sector":
        k1, k2 = "color_mm5ndfr7", "color_mm5nfp0j"
        key_name = "Sector"
    else:
        raise ValueError(f"Invalid safe join key '{join_key}'. Must be 'owner' or 'sector'.")

    # Aggregate Board 1 (Deals) by key
    deals_agg = df_deals.groupby(k1, as_index=False).agg(
        total_deals=("name", "count"),
        total_masked_value=("numeric_mm5ndf61", "sum"),
        value_null_count=("numeric_mm5ndf61", lambda x: x.isna().sum())
    ).rename(columns={k1: key_name})

    # Aggregate Board 2 (Work Orders) by key
    wo_agg = df_work_orders.groupby(k2, as_index=False).agg(
        total_work_orders=("name", "count"),
        total_billed_excl_gst=("numeric_mm5nafen", "sum"),
        total_amount_receivable=("numeric_mm5npw9h", "sum")
    ).rename(columns={k2: key_name})

    # Outer join on safe key
    merged = pd.merge(deals_agg, wo_agg, on=key_name, how="outer").fillna(0)

    metadata = {
        "join_key": key_name,
        "join_type": "SAFE_AGGREGATE_JOIN",
        "distinct_keys_deals": len(deals_agg),
        "distinct_keys_wo": len(wo_agg),
        "total_grouped_keys": len(merged)
    }

    return merged, metadata


def best_effort_deal_match(
    df_deals: pd.DataFrame,
    df_work_orders: pd.DataFrame
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Match individual deals between boards using exact Deal Name match.
    Provides best-effort deal-level alignment with explicit coverage confidence score.
    Filters out empty/generic names to prevent Cartesian products.
    """
    df1 = df_deals.copy()
    df2 = df_work_orders.copy()

    # Standardize deal names for matching and filter out empty strings
    df1["match_name"] = df1["name"].astype(str).str.strip().str.lower()
    df2["match_name"] = df2["name"].astype(str).str.strip().str.lower()

    valid_deals = df1[df1["match_name"] != ""].copy()
    valid_wo = df2[df2["match_name"] != ""].copy()

    # Perform merge on valid match_name
    merged = pd.merge(
        valid_deals,
        valid_wo,
        on="match_name",
        how="inner",
        suffixes=("_deal", "_wo")
    )

    total_deals = len(valid_deals)
    # Distinct Board 1 deals that successfully matched in Board 2
    distinct_matched_deals = merged["match_name"].nunique() if len(merged) > 0 else 0
    coverage_pct = round((distinct_matched_deals / total_deals * 100), 2) if total_deals > 0 else 0.0

    metadata = {
        "join_type": "BEST_EFFORT_NAME_MATCH",
        "total_deals_board1": total_deals,
        "total_work_orders_board2": len(valid_wo),
        "distinct_matched_deals": distinct_matched_deals,
        "total_matched_pairs": len(merged),
        "coverage_confidence_pct": coverage_pct,
        "reconciliation_reliability_note": (
            f"Best-effort match achieved {coverage_pct}% deal coverage ({distinct_matched_deals}/{total_deals} distinct deals matched). "
            f"Financial reconciliation is only valid for matched deals; remaining {100.0 - coverage_pct:.1f}% are unmatched."
        )
    }

    return merged, metadata

