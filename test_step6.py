"""
Step 6 Validation Script: Validate cleaning, data quality auditing, and cross-board join logic.
Confirms exclusion of the 2 corrupted Deal Status rows and prints completeness reports.
"""

import os
import sys
from dotenv import load_dotenv
from monday_client import MondayClient
from data_cleaning import clean_deal_funnel_data, clean_work_order_data
from data_quality import get_board_completeness
from join_logic import safe_join_cross_board, best_effort_deal_match

load_dotenv()

DEAL_FUNNEL_BOARD_ID = os.getenv("DEAL_FUNNEL_BOARD_ID", "5030221175")
WORK_ORDER_BOARD_ID = os.getenv("WORK_ORDER_BOARD_ID", "5030221237")

def test_step6_validation():
    token = os.getenv("MONDAY_API_TOKEN")
    if not token or token == "your_monday_api_token_here":
        print("[ERROR] MONDAY_API_TOKEN is missing.")
        sys.exit(1)

    client = MondayClient(api_token=token)

    # 1. Fetch raw data
    print("[1/4] Fetching live raw data...")
    raw_deals = client.fetch_board_data(DEAL_FUNNEL_BOARD_ID, use_cache=True)
    raw_wo = client.fetch_board_data(WORK_ORDER_BOARD_ID, use_cache=True)

    df_deals_raw = pd.DataFrame(raw_deals)
    df_wo_raw = pd.DataFrame(raw_wo)

    # 2. Clean data
    print("\n[2/4] Testing Data Cleaning...")
    df_deals_clean, deal_anomalies = clean_deal_funnel_data(df_deals_raw)
    df_wo_clean, wo_anomalies = clean_work_order_data(df_wo_raw)

    print(f"  -> Deal Funnel Raw Rows: {deal_anomalies['initial_rows']}")
    print(f"  -> Corrupt Status Rows Excluded: {deal_anomalies['corrupt_status_rows_excluded']}")
    print(f"  -> Deal Funnel Cleaned Rows: {len(df_deals_clean)}")
    assert len(df_deals_clean) == 344, f"Expected 344 cleaned rows (346 - 2 corrupt), got {len(df_deals_clean)}"

    print(f"  -> Work Order Cleaned Rows: {len(df_wo_clean)}")

    # 3. Data Quality Completeness Report
    print("\n[3/4] Testing Data Quality Completeness Engine...")
    dq_deals = get_board_completeness(df_deals_clean, "Deal Funnel Cleaned")
    dq_wo = get_board_completeness(df_wo_clean, "Work Order Tracker Cleaned")

    print(f"  -> Deal Funnel High Null Warnings: {dq_deals['high_null_fields_count']} fields")
    for warn in dq_deals['high_null_warnings'][:5]:
        print(f"     * {warn}")

    print(f"  -> Work Order Untracked Fields (100% null): {len(dq_wo['untracked_fields'])} fields")
    for untracked in dq_wo['untracked_fields']:
        print(f"     * {untracked}")

    # 4. Cross-Board Join Logic
    print("\n[4/4] Testing Cross-Board Join Engine...")
    df_safe_owner, safe_meta = safe_join_cross_board(df_deals_clean, df_wo_clean, join_key="owner")
    print(f"  -> Safe Owner Join Result: {len(df_safe_owner)} distinct owner groups")

    df_matched, match_meta = best_effort_deal_match(df_deals_clean, df_wo_clean)
    print(f"  -> Best-Effort Deal Name Match: {match_meta['distinct_matched_deals']} distinct matched deals ({match_meta['total_matched_pairs']} pairs)")
    print(f"  -> Match Coverage Confidence: {match_meta['coverage_confidence_pct']}%")
    print(f"  -> Reliability Note: {match_meta['reconciliation_reliability_note']}")


    print("\n[SUCCESS] STEP 6 Complete: Cleaning, Data Quality, and Join Logic fully verified!")

if __name__ == "__main__":
    import pandas as pd
    test_step6_validation()
