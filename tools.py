"""
LLM Agent Tool Definitions & Data Retrieval Wrappers.

Provides tools for querying deals, work orders, cross-board safe views,
and data quality audit reports with explicit data health disclosures.
"""

import os
import pandas as pd
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

from monday_client import MondayClient
from data_cleaning import clean_deal_funnel_data, clean_work_order_data
from data_quality import get_board_completeness
from join_logic import safe_join_cross_board, best_effort_deal_match

load_dotenv()

DEAL_FUNNEL_BOARD_ID = os.getenv("DEAL_FUNNEL_BOARD_ID", "5030221175")
WORK_ORDER_BOARD_ID = os.getenv("WORK_ORDER_BOARD_ID", "5030221237")

_client = None

def _get_client() -> MondayClient:
    global _client
    if _client is None:
        token = os.getenv("MONDAY_API_TOKEN")
        _client = MondayClient(api_token=token)
    return _client


def get_deals(
    status: Optional[str] = None,
    owner: Optional[str] = None,
    sector: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieve live deal funnel items from Board 1 with filtering and data caveats.

    Args:
        status: Filter by Deal Status (e.g. 'Won', 'Open', 'Dead', 'On Hold')
        owner: Filter by Owner code (e.g. 'OWNER_001')
        sector: Filter by Sector/service

    Returns:
        Dict containing deal list, summary metrics, and data quality caveats.
    """
    client = _get_client()
    raw_items = client.fetch_board_data(DEAL_FUNNEL_BOARD_ID, use_cache=True)
    df_raw = pd.DataFrame(raw_items)
    df, anomalies = clean_deal_funnel_data(df_raw)

    # Apply filters if provided
    if status and "color_mm5ncsbg" in df.columns:
        df = df[df["color_mm5ncsbg"].astype(str).str.lower() == status.lower()]
    if owner and "color_mm5n9tt5" in df.columns:
        df = df[df["color_mm5n9tt5"].astype(str).str.lower() == owner.lower()]
    if sector and "color_mm5ndfr7" in df.columns:
        df = df[df["color_mm5ndfr7"].astype(str).str.lower() == sector.lower()]

    val_col = "numeric_mm5ndf61"
    total_deals = len(df)

    if val_col in df.columns:
        null_count = int(df[val_col].isna().sum())
        null_pct = round((null_count / total_deals * 100), 1) if total_deals > 0 else 0.0
        sum_masked_value = float(df[val_col].sum(skipna=True))
    else:
        null_count, null_pct, sum_masked_value = 0, 0.0, 0.0

    # Format deal records for LLM context
    records = []
    for _, row in df.head(50).iterrows():
        records.append({
            "deal_name": row.get("name", ""),
            "owner": row.get("color_mm5n9tt5", ""),
            "client_code": row.get("dropdown_mm5n1nq3", ""),
            "status": row.get("color_mm5ncsbg", ""),
            "stage": row.get("color_mm5nrbes", ""),
            "masked_deal_value": row.get("numeric_mm5ndf61") if pd.notnull(row.get("numeric_mm5ndf61")) else None,
            "tentative_close_date": str(row.get("date_mm5nkvyn")) if pd.notnull(row.get("date_mm5nkvyn")) else None,
            "sector": row.get("color_mm5ndfr7", "")
        })

    return {
        "board": "Deal Funnel Data (Board 1)",
        "total_deals_found": total_deals,
        "sum_masked_value": sum_masked_value,
        "sample_records_returned": len(records),
        "deals": records,
        "data_caveat": (
            f"Note: Masked deal values are missing/null for {null_count} out of {total_deals} deals ({null_pct}% null). "
            f"Sum of deal values (${sum_masked_value:,.2f}) reflects only non-null reported deals."
        ),
        "excluded_corrupt_rows": anomalies.get("corrupt_status_rows_excluded", 0)
    }


def get_work_orders(
    execution_status: Optional[str] = None,
    personnel: Optional[str] = None,
    sector: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieve live work order tracker items from Board 2 with filtering and financial metrics.

    Args:
        execution_status: Filter by Execution Status (e.g. 'Completed', 'Ongoing', 'Not Started')
        personnel: Filter by BD/KAM Personnel code (e.g. 'OWNER_001')
        sector: Filter by Sector

    Returns:
        Dict containing work order list, financial metrics, and untracked field disclosures.
    """
    client = _get_client()
    raw_items = client.fetch_board_data(WORK_ORDER_BOARD_ID, use_cache=True)
    df_raw = pd.DataFrame(raw_items)
    df, anomalies = clean_work_order_data(df_raw)

    if execution_status and "color_mm5ngrrp" in df.columns:
        df = df[df["color_mm5ngrrp"].astype(str).str.lower() == execution_status.lower()]
    if personnel and "color_mm5nf68v" in df.columns:
        df = df[df["color_mm5nf68v"].astype(str).str.lower() == personnel.lower()]
    if sector and "color_mm5nfp0j" in df.columns:
        df = df[df["color_mm5nfp0j"].astype(str).str.lower() == sector.lower()]

    total_wo = len(df)

    # Financial sums (preserving negative credit balances in Amount Receivable)
    billed_excl_gst = float(df["numeric_mm5nafen"].sum(skipna=True)) if "numeric_mm5nafen" in df.columns else 0.0
    collected_incl_gst = float(df["numeric_mm5nat1b"].sum(skipna=True)) if "numeric_mm5nat1b" in df.columns else 0.0
    amount_receivable = float(df["numeric_mm5npw9h"].sum(skipna=True)) if "numeric_mm5npw9h" in df.columns else 0.0

    records = []
    for _, row in df.head(50).iterrows():
        records.append({
            "deal_name_masked": row.get("name", ""),
            "customer_code": row.get("dropdown_mm5nm6ec", ""),
            "personnel": row.get("color_mm5nf68v", ""),
            "sector": row.get("color_mm5nfp0j", ""),
            "execution_status": row.get("color_mm5ngrrp", ""),
            "billed_value_excl_gst": row.get("numeric_mm5nafen") if pd.notnull(row.get("numeric_mm5nafen")) else None,
            "collected_incl_gst": row.get("numeric_mm5nat1b") if pd.notnull(row.get("numeric_mm5nat1b")) else None,
            "amount_receivable": row.get("numeric_mm5npw9h") if pd.notnull(row.get("numeric_mm5npw9h")) else None
        })

    return {
        "board": "Work Order Tracker (Board 2)",
        "total_work_orders_found": total_wo,
        "total_billed_excl_gst": billed_excl_gst,
        "total_collected_incl_gst": collected_incl_gst,
        "total_amount_receivable": amount_receivable,
        "sample_records_returned": len(records),
        "work_orders": records,
        "data_caveat": (
            "Disclosed: Expected Billing Month, Actual Collection Month, Collection Status, and Collection Date "
            "are 100% null (not tracked on this board). Amount Receivable includes valid negative credit balances."
        )
    }


def get_cross_board_view(
    sector: Optional[str] = None,
    owner: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get cross-board aggregate analysis safely joined on Owner/Personnel code or Sector.

    Args:
        sector: Optional sector filter
        owner: Optional owner/personnel filter

    Returns:
        Dict containing safe joined summary table and deal name match coverage metrics.
    """
    client = _get_client()
    df_deals_raw = pd.DataFrame(client.fetch_board_data(DEAL_FUNNEL_BOARD_ID, use_cache=True))
    df_wo_raw = pd.DataFrame(client.fetch_board_data(WORK_ORDER_BOARD_ID, use_cache=True))

    df_deals, _ = clean_deal_funnel_data(df_deals_raw)
    df_wo, _ = clean_work_order_data(df_wo_raw)

    join_key = "sector" if sector else "owner"
    merged_safe, meta_safe = safe_join_cross_board(df_deals, df_wo, join_key=join_key)

    _, meta_best_effort = best_effort_deal_match(df_deals, df_wo)

    return {
        "summary_table": merged_safe.to_dict(orient="records"),
        "safe_join_metadata": meta_safe,
        "best_effort_match_metadata": meta_best_effort,
        "join_rule_caveat": (
            "Cross-board aggregation is safely calculated on shared Owner code / Sector keys. "
            f"Best-effort deal name match achieves {meta_best_effort['coverage_confidence_pct']}% coverage. "
            "Deal-level financial reconciliation is limited to matched deal names only."
        )
    }


def get_data_quality_report(board_name: str = "all") -> Dict[str, Any]:
    """
    Get complete data health & completeness audit report for one or both boards.

    Args:
        board_name: 'deals', 'work_orders', or 'all'

    Returns:
        Dict containing per-field completeness %, null counts, and data health alerts.
    """
    client = _get_client()
    df_deals_raw = pd.DataFrame(client.fetch_board_data(DEAL_FUNNEL_BOARD_ID, use_cache=True))
    df_wo_raw = pd.DataFrame(client.fetch_board_data(WORK_ORDER_BOARD_ID, use_cache=True))

    df_deals, _ = clean_deal_funnel_data(df_deals_raw)
    df_wo, _ = clean_work_order_data(df_wo_raw)

    report = {}
    if board_name.lower() in ["deals", "all"]:
        report["deal_funnel_board"] = get_board_completeness(df_deals, "Deal Funnel Data")
    if board_name.lower() in ["work_orders", "all"]:
        report["work_order_board"] = get_board_completeness(df_wo, "Work Order Tracker")

    return report
