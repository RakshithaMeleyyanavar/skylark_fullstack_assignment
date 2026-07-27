"""
Diagnostic script to inspect exact Deal Status ('color_mm5ncsbg') values in Board 1.
"""

import os
import pandas as pd
from dotenv import load_dotenv
from monday_client import MondayClient
from data_cleaning import clean_deal_funnel_data

load_dotenv()

DEAL_FUNNEL_BOARD_ID = os.getenv("DEAL_FUNNEL_BOARD_ID", "5030221175")

def debug_status_values():
    client = MondayClient()
    raw = client.fetch_board_data(DEAL_FUNNEL_BOARD_ID, use_cache=True)
    df_raw = pd.DataFrame(raw)
    df_clean, anomalies = clean_deal_funnel_data(df_raw)

    col = "color_mm5ncsbg"
    print("--- RAW BOARD 1 DEAL STATUS VALUES ---")
    print(df_raw[col].value_counts(dropna=False))

    print("\n--- CLEANED BOARD 1 DEAL STATUS VALUES ---")
    print(df_clean[col].value_counts(dropna=False))

    # Test exact string matching vs stripped/contains
    won_exact = (df_clean[col] == "Won").sum()
    won_lower = (df_clean[col].astype(str).str.strip().str.lower() == "won").sum()
    won_contains = (df_clean[col].astype(str).str.lower().str.contains("won")).sum()

    print(f"\nExact 'Won' count: {won_exact}")
    print(f"Stripped lower 'won' count: {won_lower}")
    print(f"Contains 'won' count: {won_contains}")

if __name__ == "__main__":
    debug_status_values()
