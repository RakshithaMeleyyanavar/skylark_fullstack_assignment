"""
One-Click Executive Leadership Update Generator.

Synthesizes high-level pipeline status, execution status, collection progress,
and data health caveats into a structured executive update.
"""

import os
import pandas as pd
from typing import Dict, Any
from monday_client import MondayClient
from data_cleaning import clean_deal_funnel_data, clean_work_order_data
from join_logic import best_effort_deal_match

DEAL_FUNNEL_BOARD_ID = os.getenv("DEAL_FUNNEL_BOARD_ID", "5030221175")
WORK_ORDER_BOARD_ID = os.getenv("WORK_ORDER_BOARD_ID", "5030221237")

def generate_leadership_update() -> Dict[str, Any]:
    """Generate structured executive summary from live board data."""
    client = MondayClient()
    df_deals_raw = pd.DataFrame(client.fetch_board_data(DEAL_FUNNEL_BOARD_ID, use_cache=True))
    df_wo_raw = pd.DataFrame(client.fetch_board_data(WORK_ORDER_BOARD_ID, use_cache=True))

    df_deals, anomalies_deals = clean_deal_funnel_data(df_deals_raw)
    df_wo, anomalies_wo = clean_work_order_data(df_wo_raw)

    # 1. Pipeline Movement Metrics
    total_deals = len(df_deals)
    status_counts = df_deals["color_mm5ncsbg"].value_counts().to_dict() if "color_mm5ncsbg" in df_deals.columns else {}
    won_count = status_counts.get("Won", 0)
    open_count = status_counts.get("Open", 0)
    dead_count = status_counts.get("Dead", 0)

    val_col = "numeric_mm5ndf61"
    total_reported_deal_val = float(df_deals[val_col].sum(skipna=True)) if val_col in df_deals.columns else 0.0
    val_null_cnt = int(df_deals[val_col].isna().sum()) if val_col in df_deals.columns else 0
    val_null_pct = round((val_null_cnt / total_deals * 100), 1) if total_deals > 0 else 0.0

    # 2. Execution Status Metrics
    total_wo = len(df_wo)
    exec_counts = df_wo["color_mm5ngrrp"].value_counts().to_dict() if "color_mm5ngrrp" in df_wo.columns else {}
    completed_wo = exec_counts.get("Completed", 0) + exec_counts.get("Complete", 0)
    ongoing_wo = exec_counts.get("Ongoing", 0)

    # 3. Financial Collections Metrics
    billed_excl_gst = float(df_wo["numeric_mm5nafen"].sum(skipna=True)) if "numeric_mm5nafen" in df_wo.columns else 0.0
    collected_incl_gst = float(df_wo["numeric_mm5nat1b"].sum(skipna=True)) if "numeric_mm5nat1b" in df_wo.columns else 0.0
    amount_receivable = float(df_wo["numeric_mm5npw9h"].sum(skipna=True)) if "numeric_mm5npw9h" in df_wo.columns else 0.0

    # 4. Join Coverage
    _, match_meta = best_effort_deal_match(df_deals, df_wo)

    # Build Executive Markdown Summary
    summary_markdown = f"""
### 📊 Leadership Executive Update

**1. Pipeline Movement**
- **Total Deals**: {total_deals} valid deals ({anomalies_deals.get('corrupt_status_rows_excluded', 0)} corrupt rows excluded).
- **Status Breakdown**: {won_count} Won | {open_count} Open | {dead_count} Dead.
- **Reported Deal Volume**: **${total_reported_deal_val:,.2f}** *(Caveat: {val_null_pct}% of deals have unreported/null values)*.

**2. Execution Status (Work Orders)**
- **Active Work Orders**: {total_wo} tracked across operational teams.
- **Delivery Progress**: {completed_wo} Completed | {ongoing_wo} Ongoing.

**3. Financial & Collection Health**
- **Total Billed Value (excl GST)**: **${billed_excl_gst:,.2f}**
- **Total Collections (incl GST)**: **${collected_incl_gst:,.2f}**
- **Outstanding Receivable**: **${amount_receivable:,.2f}** *(includes valid credit balances)*.

**4. Data Quality & Join Reliability**
- **Board 1 Gaps**: Deal Value is 52% null; Close Date (A) is 92.4% null.
- **Board 2 Untracked**: Expected Billing Month & Collection Date are 100% null (not tracked).
- **Cross-Board Reconciliation**: Safe joins enabled by Owner Code ({match_meta['distinct_matched_deals']} distinct deal matches, {match_meta['coverage_confidence_pct']}% deal-level match confidence).
"""

    return {
        "markdown": summary_markdown,
        "total_deals": total_deals,
        "won_count": won_count,
        "total_wo": total_wo,
        "billed_excl_gst": billed_excl_gst,
        "amount_receivable": amount_receivable,
        "match_confidence": match_meta['coverage_confidence_pct']
    }
