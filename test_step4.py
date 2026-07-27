"""
Step 4 Test Script: Verify live Monday.com GraphQL API connection and raw row counts.
"""

import os
import sys
from dotenv import load_dotenv
from monday_client import MondayClient

load_dotenv()

DEAL_FUNNEL_BOARD_ID = os.getenv("DEAL_FUNNEL_BOARD_ID", "5030221175")
WORK_ORDER_BOARD_ID = os.getenv("WORK_ORDER_BOARD_ID", "5030221237")

def test_live_connection():
    token = os.getenv("MONDAY_API_TOKEN")
    if not token or token == "your_monday_api_token_here":
        print("[ERROR] MONDAY_API_TOKEN is not set in .env file or environment.")
        sys.exit(1)

    print(f"Connecting to Monday.com API with token: {token[:6]}***...")
    client = MondayClient(api_token=token)

    # Fetch Board 1: Deal Funnel Data
    print(f"\n[1/2] Fetching live items for Board 1 (Deal Funnel, ID: {DEAL_FUNNEL_BOARD_ID})...")
    deal_items = client.fetch_board_items_raw(DEAL_FUNNEL_BOARD_ID, use_cache=False)
    print(f"-> Board 1 Raw Row Count: {len(deal_items)} rows (Expected ~346)")

    # Fetch Board 2: Work Order Tracker Data
    print(f"\n[2/2] Fetching live items for Board 2 (Work Order Tracker, ID: {WORK_ORDER_BOARD_ID})...")
    wo_items = client.fetch_board_items_raw(WORK_ORDER_BOARD_ID, use_cache=False)
    print(f"-> Board 2 Raw Row Count: {len(wo_items)} rows (Expected ~176)")

    print("\n[SUCCESS] Live connection to Monday.com GraphQL API verified!")
    print(f"Total raw items fetched: {len(deal_items) + len(wo_items)}")

if __name__ == "__main__":
    test_live_connection()
