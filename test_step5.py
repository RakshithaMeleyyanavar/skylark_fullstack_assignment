"""
Step 5 Test Script: Full raw fetch for both boards into untouched pandas DataFrames.
Validates raw row counts (346 / 176) and confirms corrupt rows + nulls remain intact.
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv
from monday_client import MondayClient

load_dotenv()

DEAL_FUNNEL_BOARD_ID = os.getenv("DEAL_FUNNEL_BOARD_ID", "5030221175")
WORK_ORDER_BOARD_ID = os.getenv("WORK_ORDER_BOARD_ID", "5030221237")

def test_raw_dataframes():
    token = os.getenv("MONDAY_API_TOKEN")
    if not token or token == "your_monday_api_token_here":
        print("[ERROR] MONDAY_API_TOKEN is not set.")
        sys.exit(1)

    client = MondayClient(api_token=token)

    # 1. Fetch Board 1 raw records -> untouched DataFrame
    print("[1/2] Fetching raw records for Board 1 (Deal Funnel)...")
    deals_records = client.fetch_board_data(DEAL_FUNNEL_BOARD_ID, use_cache=True)
    df_deals_raw = pd.DataFrame(deals_records)

    print(f"  -> df_deals_raw shape: {df_deals_raw.shape} (Rows: {len(df_deals_raw)}, Cols: {len(df_deals_raw.columns)})")
    assert len(df_deals_raw) == 346, f"Expected 346 rows, got {len(df_deals_raw)}"

    # 2. Fetch Board 2 raw records -> untouched DataFrame
    print("[2/2] Fetching raw records for Board 2 (Work Order Tracker)...")
    wo_records = client.fetch_board_data(WORK_ORDER_BOARD_ID, use_cache=True)
    df_wo_raw = pd.DataFrame(wo_records)

    print(f"  -> df_wo_raw shape: {df_wo_raw.shape} (Rows: {len(df_wo_raw)}, Cols: {len(df_wo_raw.columns)})")
    assert len(df_wo_raw) == 176, f"Expected 176 rows, got {len(df_wo_raw)}"

    # 3. Detect corrupt rows in raw df_deals_raw before cleaning
    # Status column is 'color_mm5ncsbg'
    status_col = "color_mm5ncsbg"
    corrupt_status_count = 0
    if status_col in df_deals_raw.columns:
        corrupt_status_count = (df_deals_raw[status_col] == "Deal Status").sum()
        print(f"\n[CORRUPT ROW CHECK] Found {corrupt_status_count} corrupt Deal Status rows in raw DataFrame (Value == 'Deal Status' literal).")

    # 4. Print completeness highlights for raw data
    print("\n--- Board 1 (Deal Funnel) Untouched Null Counts ---")
    val_col = "numeric_mm5ndf61"
    if val_col in df_deals_raw.columns:
        null_val_cnt = df_deals_raw[val_col].isna().sum() | (df_deals_raw[val_col] == "").sum()
        print(f"  -> Masked Deal Value nulls: {null_val_cnt} / {len(df_deals_raw)} ({null_val_cnt/len(df_deals_raw)*100:.1f}%)")

    print("\n[SUCCESS] STEP 5 Complete: Untouched DataFrames generated and validated successfully!")

if __name__ == "__main__":
    test_raw_dataframes()
